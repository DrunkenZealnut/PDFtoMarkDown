"""
Text Parser 모듈

PDF에서 추출된 텍스트 블록들을 분석하여 문서 구조(제목, 단락, 리스트, 테이블)를 파악합니다.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
from pathlib import Path

import pdfplumber

from .data_models import TextBlock, FontInfo, FontStyle, DocumentContent, PageInfo
from .text_structures import (
    DocumentStructure, DocumentElement, ElementType,
    Heading, Paragraph, ListItem, ListType, Table, TableRow, TableCell,
    FontStatistics, DocumentAnalytics
)


class TextParser:
    """
    추출된 텍스트를 분석하여 문서 구조를 파악하는 클래스
    
    주요 기능:
    - 폰트 분석을 통한 제목 식별
    - 리스트 패턴 인식
    - 단락 병합 및 정리
    - 테이블 구조 분석
    - 문서 요소 순서 결정
    """
    
    def __init__(self, 
                 title_font_threshold: float = 1.2,
                 merge_paragraphs: bool = False,
                 table_detection: bool = True):
        """
        Text Parser 초기화
        
        Args:
            title_font_threshold: 제목 인식을 위한 폰트 크기 임계값 (본문 대비 배수)
            merge_paragraphs: 단락 병합 여부
            table_detection: 테이블 자동 인식 여부
        """
        self.title_font_threshold = title_font_threshold
        self.merge_paragraphs = merge_paragraphs
        self.table_detection = table_detection
        
        self.logger = logging.getLogger(__name__)
        
        # 분석 결과 캐시
        self._font_stats: Optional[List[FontStatistics]] = None
        self._main_font: Optional[FontStatistics] = None
        
        # 리스트 패턴 정의
        self.list_patterns = {
            ListType.BULLET: [
                r'^[•\-\*\+]\s+',  # •, -, *, + 
                r'^[○◦▪▫]\s+',     # 다양한 불릿 기호
            ],
            ListType.NUMBERED: [
                r'^\d+\.\s+',      # 1. 2. 3.
                r'^\d+\)\s+',      # 1) 2) 3)
                r'^\(\d+\)\s+',    # (1) (2) (3)
            ],
            ListType.LETTERED: [
                r'^[a-z]\.\s+',    # a. b. c.
                r'^[A-Z]\.\s+',    # A. B. C.
                r'^[a-z]\)\s+',    # a) b) c)
                r'^[A-Z]\)\s+',    # A) B) C)
            ],
            ListType.ROMAN: [
                r'^[ivxlcdm]+\.\s+',  # i. ii. iii.
                r'^[IVXLCDM]+\.\s+',  # I. II. III.
            ]
        }
    
    def analyze_document_structure(self, document: DocumentContent) -> DocumentStructure:
        """
        문서 구조를 종합적으로 분석합니다
        
        Args:
            document: PDFReader로 추출한 문서 내용
            
        Returns:
            DocumentStructure: 분석된 문서 구조
        """
        self.logger.info(f"문서 구조 분석 시작: {len(document.pages)}페이지")
        
        # 모든 텍스트 블록 수집
        all_text_blocks = []
        for page in document.pages:
            all_text_blocks.extend(page.text_blocks)
        
        self.logger.debug(f"총 {len(all_text_blocks)}개 텍스트 블록 분석")
        
        # 1. 폰트 통계 분석
        self._analyze_font_statistics(all_text_blocks)
        
        # 2. 개별 요소 식별
        headings = self.identify_headings(all_text_blocks)
        paragraphs = self.identify_paragraphs(all_text_blocks, headings)
        lists = self.identify_lists(all_text_blocks)
        tables = self.identify_tables(document) if self.table_detection else []
        
        # 3. 문서 요소 통합 및 순서 정렬
        elements = self._create_document_elements(headings, paragraphs, lists, tables)
        elements = self._sort_elements_by_position(elements)
        
        # 4. 분석 품질 평가
        confidence_score = self._calculate_confidence_score(elements)
        warnings = self._generate_analysis_warnings(elements)
        
        structure = DocumentStructure(
            elements=elements,
            headings=headings,
            paragraphs=paragraphs,
            lists=lists,
            tables=tables,
            confidence_score=confidence_score,
            analysis_warnings=warnings
        )
        
        self.logger.info(
            f"구조 분석 완료: "
            f"{len(headings)}개 제목, "
            f"{len(paragraphs)}개 단락, "
            f"{len(lists)}개 리스트, "
            f"{len(tables)}개 테이블"
        )
        
        return structure
    
    def _analyze_font_statistics(self, text_blocks: List[TextBlock]) -> None:
        """폰트 사용 통계를 분석합니다"""
        font_counts = defaultdict(lambda: {
            'count': 0,
            'total_length': 0,
            'sizes': [],
            'is_bold': False,
            'is_italic': False
        })
        
        for block in text_blocks:
            font_info = block.font_info
            font_key = f"{font_info.name}_{font_info.size}_{font_info.style.value}"
            
            font_counts[font_key]['count'] += 1
            font_counts[font_key]['total_length'] += len(block.text)
            font_counts[font_key]['sizes'].append(font_info.size)
            font_counts[font_key]['is_bold'] = font_info.style in [FontStyle.BOLD, FontStyle.BOLD_ITALIC]
            font_counts[font_key]['is_italic'] = font_info.style in [FontStyle.ITALIC, FontStyle.BOLD_ITALIC]
        
        # FontStatistics 객체 생성
        self._font_stats = []
        for font_key, stats in font_counts.items():
            parts = font_key.rsplit('_', 2)
            font_name = parts[0]
            font_size = float(parts[1])
            
            font_stat = FontStatistics(
                font_name=font_name,
                font_size=font_size,
                occurrence_count=stats['count'],
                total_text_length=stats['total_length'],
                is_bold=stats['is_bold'],
                is_italic=stats['is_italic']
            )
            self._font_stats.append(font_stat)
        
        # 가장 많이 사용된 폰트를 본문 폰트로 설정
        if self._font_stats:
            self._main_font = max(self._font_stats, key=lambda x: x.occurrence_count)
            self.logger.debug(f"본문 폰트: {self._main_font.font_name} {self._main_font.font_size}pt")
    
    def identify_headings(self, text_blocks: List[TextBlock]) -> List[Heading]:
        """
        폰트 크기와 스타일을 기반으로 제목을 식별합니다
        
        Args:
            text_blocks: 분석할 텍스트 블록들
            
        Returns:
            List[Heading]: 식별된 제목들
        """
        if not self._main_font:
            return []
        
        headings = []
        main_font_size = self._main_font.font_size
        
        for block in text_blocks:
            font_info = block.font_info
            
            # 제목 후보 조건들
            is_larger_font = font_info.size >= main_font_size * self.title_font_threshold
            is_bold = font_info.style in [FontStyle.BOLD, FontStyle.BOLD_ITALIC]
            is_short_text = len(block.text.strip()) < 100  # 제목은 보통 짧음
            is_sentence_case = self._is_title_case(block.text)
            
            # 제목 확신도 계산
            confidence = 0.0
            if is_larger_font:
                confidence += 0.4
            if is_bold:
                confidence += 0.3
            if is_short_text:
                confidence += 0.2
            if is_sentence_case:
                confidence += 0.1
            
            # 임계값 이상이면 제목으로 분류
            if confidence >= 0.5:
                # 제목 레벨 결정 (폰트 크기 기반)
                size_ratio = font_info.size / main_font_size
                if size_ratio >= 2.0:
                    level = 1
                elif size_ratio >= 1.8:
                    level = 2
                elif size_ratio >= 1.6:
                    level = 3
                elif size_ratio >= 1.4:
                    level = 4
                elif size_ratio >= 1.2:
                    level = 5
                else:
                    level = 6
                
                heading = Heading(
                    text=block.text.strip(),
                    level=level,
                    font_size=font_info.size,
                    font_name=font_info.name,
                    bbox=block.bbox,
                    page_num=block.page_num,
                    confidence=confidence
                )
                headings.append(heading)
        
        self.logger.debug(f"{len(headings)}개 제목 식별됨")
        return headings
    
    def identify_paragraphs(self, text_blocks: List[TextBlock], headings: List[Heading]) -> List[Paragraph]:
        """
        제목이 아닌 텍스트들을 단락으로 그룹화합니다
        
        Args:
            text_blocks: 분석할 텍스트 블록들
            headings: 이미 식별된 제목들
            
        Returns:
            List[Paragraph]: 식별된 단락들
        """
        # 제목 텍스트 세트 생성 (빠른 검색용)
        heading_texts = {h.text for h in headings}
        
        # 제목이 아닌 블록들 수집
        paragraph_blocks = [
            block for block in text_blocks 
            if block.text.strip() not in heading_texts
        ]
        
        paragraphs = []
        
        if self.merge_paragraphs:
            # 단락 병합 로직
            paragraphs = self._merge_text_blocks_into_paragraphs(paragraph_blocks)
        else:
            # 각 블록을 별도 단락으로 처리
            for block in paragraph_blocks:
                if block.text.strip():  # 빈 텍스트 제외
                    paragraph = Paragraph(
                        text=block.text.strip(),
                        text_blocks=[block],
                        bbox=block.bbox,
                        page_num=block.page_num,
                        is_merged=False
                    )
                    paragraphs.append(paragraph)
        
        self.logger.debug(f"{len(paragraphs)}개 단락 식별됨")
        return paragraphs
    
    def identify_lists(self, text_blocks: List[TextBlock]) -> List[ListItem]:
        """
        리스트 패턴을 식별합니다
        
        Args:
            text_blocks: 분석할 텍스트 블록들
            
        Returns:
            List[ListItem]: 식별된 리스트 항목들
        """
        list_items = []
        
        for block in text_blocks:
            text = block.text.strip()
            if not text:
                continue
            
            # 각 리스트 타입별 패턴 매칭
            for list_type, patterns in self.list_patterns.items():
                for pattern in patterns:
                    match = re.match(pattern, text)
                    if match:
                        marker = match.group(0).strip()
                        item_text = text[len(match.group(0)):].strip()
                        
                        # 들여쓰기 레벨 계산 (bbox의 x 좌표 기반)
                        level = self._calculate_indentation_level(block.bbox[0])
                        
                        list_item = ListItem(
                            text=item_text,
                            list_type=list_type,
                            marker=marker,
                            level=level,
                            bbox=block.bbox,
                            page_num=block.page_num
                        )
                        list_items.append(list_item)
                        break
                if list_items and list_items[-1].text == item_text:
                    break  # 이미 매칭된 경우 다른 패턴 시도 안함
        
        self.logger.debug(f"{len(list_items)}개 리스트 항목 식별됨")
        return list_items
    
    def identify_tables(self, document: DocumentContent) -> List[Table]:
        """
        pdfplumber를 사용하여 테이블을 식별합니다
        
        Args:
            document: 문서 내용
            
        Returns:
            List[Table]: 식별된 테이블들
        """
        if not self.table_detection:
            return []
        
        tables = []
        
        # 각 페이지에서 테이블 추출 시도
        for page_info in document.pages:
            try:
                # 임시로 간단한 테이블 감지 로직 구현
                # 실제로는 pdfplumber.open()을 사용해야 하지만
                # 여기서는 텍스트 블록 기반으로 테이블 패턴 감지
                page_tables = self._detect_table_patterns(page_info)
                tables.extend(page_tables)
                
            except Exception as e:
                self.logger.warning(f"페이지 {page_info.page_num}에서 테이블 추출 실패: {e}")
        
        self.logger.debug(f"{len(tables)}개 테이블 식별됨")
        return tables
    
    def _detect_table_patterns(self, page_info: PageInfo) -> List[Table]:
        """텍스트 블록 패턴을 기반으로 테이블을 감지합니다"""
        tables = []
        
        # 단순한 테이블 패턴 감지 로직
        # 비슷한 y 좌표에 여러 텍스트가 정렬되어 있으면 테이블로 간주
        y_groups = defaultdict(list)
        
        for block in page_info.text_blocks:
            y_coord = round(block.bbox[1])  # y 좌표 반올림
            y_groups[y_coord].append(block)
        
        # 3개 이상의 블록이 같은 y 좌표에 있으면 테이블 행으로 간주
        table_rows = []
        for y_coord, blocks in y_groups.items():
            if len(blocks) >= 2:  # 최소 2개 열
                # x 좌표로 정렬
                blocks.sort(key=lambda b: b.bbox[0])
                
                # TableCell 생성
                cells = []
                for col_idx, block in enumerate(blocks):
                    cell = TableCell(
                        text=block.text.strip(),
                        row=len(table_rows),
                        col=col_idx,
                        bbox=block.bbox
                    )
                    cells.append(cell)
                
                # TableRow 생성
                row_bbox = (
                    min(b.bbox[0] for b in blocks),
                    min(b.bbox[1] for b in blocks),
                    max(b.bbox[2] for b in blocks),
                    max(b.bbox[3] for b in blocks)
                )
                
                row = TableRow(
                    cells=cells,
                    row_index=len(table_rows),
                    bbox=row_bbox
                )
                table_rows.append(row)
        
        # 연속된 행들을 하나의 테이블로 그룹화
        if len(table_rows) >= 2:  # 최소 2행
            table_bbox = (
                min(row.bbox[0] for row in table_rows),
                min(row.bbox[1] for row in table_rows),
                max(row.bbox[2] for row in table_rows),
                max(row.bbox[3] for row in table_rows)
            )
            
            table = Table(
                rows=table_rows,
                bbox=table_bbox,
                page_num=page_info.page_num,
                has_header=True,  # 첫 번째 행을 헤더로 가정
                confidence=0.7  # 간단한 패턴 매칭이므로 중간 확신도
            )
            tables.append(table)
        
        return tables
    
    def _merge_text_blocks_into_paragraphs(self, blocks: List[TextBlock]) -> List[Paragraph]:
        """텍스트 블록들을 단락으로 병합합니다"""
        if not blocks:
            return []
        
        paragraphs = []
        current_blocks = []
        current_text = ""
        
        # 페이지별로 그룹화
        blocks_by_page = defaultdict(list)
        for block in blocks:
            blocks_by_page[block.page_num].append(block)
        
        for page_num in sorted(blocks_by_page.keys()):
            page_blocks = blocks_by_page[page_num]
            
            # y 좌표로 정렬 (위에서 아래로)
            page_blocks.sort(key=lambda b: -b.bbox[1])  # y 좌표 내림차순
            
            for block in page_blocks:
                # 단락 분리 조건 확인
                should_break = (
                    len(current_text) > 0 and (
                        block.text.strip().endswith('.') or
                        block.text.strip().endswith('!') or
                        block.text.strip().endswith('?') or
                        len(current_text) > 500  # 너무 긴 단락 분리
                    )
                )
                
                if should_break and current_blocks:
                    # 현재 단락 생성
                    paragraph = self._create_paragraph_from_blocks(current_blocks, current_text)
                    paragraphs.append(paragraph)
                    
                    # 새 단락 시작
                    current_blocks = [block]
                    current_text = block.text.strip()
                else:
                    # 현재 단락에 추가
                    current_blocks.append(block)
                    if current_text:
                        current_text += " " + block.text.strip()
                    else:
                        current_text = block.text.strip()
            
            # 페이지 끝에서 남은 블록들 처리
            if current_blocks:
                paragraph = self._create_paragraph_from_blocks(current_blocks, current_text)
                paragraphs.append(paragraph)
                current_blocks = []
                current_text = ""
        
        return paragraphs
    
    def _create_paragraph_from_blocks(self, blocks: List[TextBlock], text: str) -> Paragraph:
        """텍스트 블록들로부터 단락 객체를 생성합니다"""
        # 전체 bbox 계산
        min_x = min(b.bbox[0] for b in blocks)
        min_y = min(b.bbox[1] for b in blocks)
        max_x = max(b.bbox[2] for b in blocks)
        max_y = max(b.bbox[3] for b in blocks)
        
        bbox = (min_x, min_y, max_x, max_y)
        page_num = blocks[0].page_num  # 첫 번째 블록의 페이지 번호 사용
        
        return Paragraph(
            text=text,
            text_blocks=blocks,
            bbox=bbox,
            page_num=page_num,
            is_merged=len(blocks) > 1
        )
    
    def _calculate_indentation_level(self, x_coordinate: float) -> int:
        """x 좌표를 기반으로 들여쓰기 레벨을 계산합니다"""
        # 단순한 들여쓰기 계산 로직
        # 실제로는 페이지 여백과 표준 들여쓰기를 고려해야 함
        base_margin = 50  # 기본 여백
        indent_size = 20  # 들여쓰기 크기
        
        if x_coordinate <= base_margin:
            return 0
        
        level = int((x_coordinate - base_margin) / indent_size)
        return min(level, 5)  # 최대 5레벨까지
    
    def _is_title_case(self, text: str) -> bool:
        """텍스트가 제목 형식인지 확인합니다"""
        text = text.strip()
        if not text:
            return False
        
        # 모든 단어가 대문자로 시작하는지 확인
        words = text.split()
        if len(words) == 0:
            return False
        
        # 첫 글자가 대문자이고, 전체가 대문자가 아닌 경우
        return (text[0].isupper() and 
                not text.isupper() and 
                len(text) < 100)
    
    def _create_document_elements(self, headings: List[Heading], 
                                paragraphs: List[Paragraph],
                                lists: List[ListItem], 
                                tables: List[Table]) -> List[DocumentElement]:
        """개별 요소들을 DocumentElement로 통합합니다"""
        elements = []
        order = 0
        
        # 제목 요소 추가
        for heading in headings:
            element = DocumentElement(
                element_type=ElementType.HEADING,
                content=heading,
                bbox=heading.bbox,
                page_num=heading.page_num,
                order=order
            )
            elements.append(element)
            order += 1
        
        # 단락 요소 추가
        for paragraph in paragraphs:
            element = DocumentElement(
                element_type=ElementType.PARAGRAPH,
                content=paragraph,
                bbox=paragraph.bbox,
                page_num=paragraph.page_num,
                order=order
            )
            elements.append(element)
            order += 1
        
        # 리스트 요소 추가
        for list_item in lists:
            element = DocumentElement(
                element_type=ElementType.LIST_ITEM,
                content=list_item,
                bbox=list_item.bbox,
                page_num=list_item.page_num,
                order=order
            )
            elements.append(element)
            order += 1
        
        # 테이블 요소 추가
        for table in tables:
            element = DocumentElement(
                element_type=ElementType.TABLE,
                content=table,
                bbox=table.bbox,
                page_num=table.page_num,
                order=order
            )
            elements.append(element)
            order += 1
        
        return elements
    
    def _sort_elements_by_position(self, elements: List[DocumentElement]) -> List[DocumentElement]:
        """요소들을 페이지와 위치 순서대로 정렬합니다"""
        return sorted(elements, key=lambda e: (e.page_num, -e.bbox[1], e.bbox[0]))
    
    def _calculate_confidence_score(self, elements: List[DocumentElement]) -> float:
        """분석 결과의 전체 확신도를 계산합니다"""
        if not elements:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for element in elements:
            weight = 1.0
            
            if element.element_type == ElementType.HEADING:
                score = element.content.confidence
                weight = 2.0  # 제목은 더 중요
            elif element.element_type == ElementType.TABLE:
                score = element.content.confidence
                weight = 1.5  # 테이블도 중요
            else:
                score = 0.8  # 단락과 리스트는 기본 점수
            
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _generate_analysis_warnings(self, elements: List[DocumentElement]) -> List[str]:
        """분석 과정에서 발견된 문제점들을 경고로 생성합니다"""
        warnings = []
        
        # 제목 레벨 건너뛰기 확인
        headings = [e for e in elements if e.element_type == ElementType.HEADING]
        if headings:
            levels = [h.content.level for h in headings]
            for i in range(1, len(levels)):
                if levels[i] > levels[i-1] + 1:
                    warnings.append(f"제목 레벨이 건너뛰어짐: H{levels[i-1]} 다음에 H{levels[i]}")
        
        # 리스트 구조 확인
        lists = [e for e in elements if e.element_type == ElementType.LIST_ITEM]
        if lists:
            list_types = [l.content.list_type for l in lists]
            # 연속된 리스트 타입 변경 확인
            type_changes = 0
            for i in range(1, len(list_types)):
                if list_types[i] != list_types[i-1]:
                    type_changes += 1
            
            if type_changes > len(lists) * 0.3:  # 30% 이상 타입 변경
                warnings.append("리스트 타입이 자주 변경됨 - 일관성 확인 필요")
        
        # 테이블 품질 확인
        tables = [e for e in elements if e.element_type == ElementType.TABLE]
        for table_elem in tables:
            table = table_elem.content
            if table.confidence < 0.5:
                warnings.append(f"페이지 {table.page_num}의 테이블 인식 확신도 낮음")
        
        return warnings
    
    def get_font_statistics(self) -> List[FontStatistics]:
        """폰트 통계를 반환합니다"""
        return self._font_stats or []
    
    def get_main_font(self) -> Optional[FontStatistics]:
        """본문 폰트 정보를 반환합니다"""
        return self._main_font 