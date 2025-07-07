"""
Markdown Generator 모듈

분석된 문서 구조를 Markdown 형식으로 변환합니다.
"""

import re
import logging
import unicodedata
from typing import List, Dict, Any, Optional, Tuple, Set
from pathlib import Path
from datetime import datetime
from io import BytesIO
import base64

from .text_structures import (
    DocumentStructure, DocumentElement, ElementType,
    Heading, Paragraph, ListItem, Table, ListType
)
from .data_models import DocumentContent, ImageInfo
from .markdown_config import MarkdownConfig, LineEndingType, ImageFormatType, TableFormatType


class MarkdownGenerator:
    """
    문서 구조를 Markdown으로 변환하는 클래스
    
    주요 기능:
    - 제목 → Markdown 헤더 변환
    - 단락 → 일반 텍스트 변환
    - 리스트 → Markdown 리스트 변환
    - 테이블 → Markdown 테이블 변환
    - 이미지 → 이미지 링크 처리
    - 메타데이터 → YAML Front Matter
    - 목차(TOC) 생성
    """
    
    def __init__(self, config: Optional[MarkdownConfig] = None):
        """
        Markdown Generator 초기화
        
        Args:
            config: Markdown 생성 설정
        """
        self.config = config or MarkdownConfig()
        self.logger = logging.getLogger(__name__)
        
        # 변환 상태 관리
        self._current_list_level = 0
        self._current_list_type = None
        self._image_counter = 0
        self._heading_counter = {}  # 레벨별 제목 번호
        self._generated_ids = set()  # 중복 ID 방지
        
        # 설정 검증
        warnings = self.config.validate()
        if warnings:
            for warning in warnings:
                self.logger.warning(f"설정 경고: {warning}")
    
    def generate_markdown(self, 
                         structure: DocumentStructure, 
                         document: DocumentContent,
                         output_path: Optional[Path] = None) -> str:
        """
        문서 구조를 Markdown으로 변환합니다
        
        Args:
            structure: 분석된 문서 구조
            document: 원본 문서 내용
            output_path: 출력 파일 경로 (이미지 경로 계산용)
            
        Returns:
            str: 생성된 Markdown 텍스트
        """
        self.logger.info(f"Markdown 생성 시작: {structure.total_elements}개 요소")
        
        # 상태 초기화
        self._reset_generation_state()
        
        # Markdown 구성 요소들
        markdown_parts = []
        
        # 1. YAML Front Matter (메타데이터)
        if self.config.metadata.include_yaml_frontmatter:
            frontmatter = self._generate_frontmatter(document.metadata, structure)
            if frontmatter:
                markdown_parts.append(frontmatter)
        
        # 2. 목차 (TOC)
        if self.config.heading.add_toc and structure.headings:
            toc = self._generate_toc(structure.headings)
            if toc:
                markdown_parts.append(toc)
        
        # 3. 문서 내용
        content = self._generate_content(structure, document, output_path)
        if content:
            markdown_parts.append(content)
        
        # 4. 후처리
        markdown_text = self._join_parts(markdown_parts)
        markdown_text = self._post_process_text(markdown_text)
        
        self.logger.info("Markdown 생성 완료")
        return markdown_text
    
    def _reset_generation_state(self):
        """생성 상태 초기화"""
        self._current_list_level = 0
        self._current_list_type = None
        self._image_counter = 0
        self._heading_counter = {}
        self._generated_ids.clear()
    
    def _generate_frontmatter(self, metadata, structure: DocumentStructure) -> str:
        """YAML Front Matter 생성"""
        if not self.config.metadata.include_yaml_frontmatter:
            return ""
        
        frontmatter_lines = ["---"]
        
        # 제목
        if self.config.metadata.include_title and metadata.title:
            frontmatter_lines.append(f'title: "{self._escape_yaml_string(metadata.title)}"')
        
        # 작성자
        if self.config.metadata.include_author and metadata.author:
            frontmatter_lines.append(f'author: "{self._escape_yaml_string(metadata.author)}"')
        
        # 생성 날짜
        if self.config.metadata.include_creation_date:
            if metadata.creation_date:
                frontmatter_lines.append(f"date: {metadata.creation_date}")
            else:
                frontmatter_lines.append(f"date: {datetime.now().isoformat()}")
        
        # 페이지 수
        if self.config.metadata.include_page_count:
            frontmatter_lines.append(f"pages: {metadata.page_count}")
        
        # 처리 정보
        if self.config.metadata.include_processing_info:
            frontmatter_lines.append(f"elements: {structure.total_elements}")
            frontmatter_lines.append(f"headings: {structure.heading_count}")
            frontmatter_lines.append(f"paragraphs: {structure.paragraph_count}")
            frontmatter_lines.append(f"lists: {structure.list_count}")
            frontmatter_lines.append(f"tables: {structure.table_count}")
            frontmatter_lines.append(f"confidence: {structure.confidence_score:.2f}")
        
        # 사용자 정의 필드
        for key, value in self.config.metadata.custom_fields.items():
            frontmatter_lines.append(f'{key}: "{self._escape_yaml_string(str(value))}"')
        
        frontmatter_lines.append("---")
        return "\n".join(frontmatter_lines)
    
    def _generate_toc(self, headings: List[Heading]) -> str:
        """목차(TOC) 생성"""
        if not headings:
            return ""
        
        toc_lines = ["## 목차", ""]
        
        for heading in headings:
            if heading.level <= self.config.heading.toc_max_level:
                indent = "  " * (heading.level - 1)
                
                # 제목 ID 생성
                heading_id = self._generate_heading_id(heading.text)
                
                # TOC 항목 생성
                toc_item = f"{indent}- [{heading.text}](#{heading_id})"
                toc_lines.append(toc_item)
        
        toc_lines.append("")  # TOC 후 빈 줄
        return "\n".join(toc_lines)
    
    def _generate_content(self, 
                         structure: DocumentStructure, 
                         document: DocumentContent,
                         output_path: Optional[Path]) -> str:
        """문서 내용 생성"""
        content_lines = []
        
        # 요소별 변환
        for element in structure.elements:
            element_content = self._convert_element(element, document, output_path)
            if element_content:
                content_lines.append(element_content)
        
        return "\n".join(content_lines)
    
    def _convert_element(self, 
                        element: DocumentElement, 
                        document: DocumentContent,
                        output_path: Optional[Path]) -> str:
        """개별 문서 요소 변환"""
        try:
            if element.element_type == ElementType.HEADING:
                return self._convert_heading(element.content)
            elif element.element_type == ElementType.PARAGRAPH:
                return self._convert_paragraph(element.content)
            elif element.element_type == ElementType.LIST_ITEM:
                return self._convert_list_item(element.content)
            elif element.element_type == ElementType.TABLE:
                return self._convert_table(element.content)
            elif element.element_type == ElementType.IMAGE:
                return self._convert_image(element.content, output_path)
            else:
                self.logger.warning(f"지원되지 않는 요소 타입: {element.element_type}")
                return ""
                
        except Exception as e:
            self.logger.error(f"요소 변환 실패 ({element.element_type}): {e}")
            return ""
    
    def _convert_heading(self, heading: Heading) -> str:
        """제목 변환"""
        # 레벨 조정
        level = max(self.config.heading.min_level, 
                   min(heading.level, self.config.heading.max_level))
        
        # 제목 텍스트 정리
        text = self._clean_text(heading.text)
        
        if self.config.heading.setext_style and level <= 2:
            # Setext 스타일 (= 및 - 언더라인)
            underline_char = "=" if level == 1 else "-"
            underline = underline_char * len(text)
            result = f"{text}\n{underline}"
        else:
            # ATX 스타일 (# ## ###)
            prefix = "#" * level
            result = f"{prefix} {text}"
        
        # 제목 ID 추가
        if self.config.heading.heading_ids:
            heading_id = self._generate_heading_id(text)
            if not self.config.heading.setext_style:
                result += f" {{#{heading_id}}}"
            else:
                result += f"\n{{#{heading_id}}}"
        
        # 제목 후 빈 줄 추가
        return result + "\n"
    
    def _convert_paragraph(self, paragraph: Paragraph) -> str:
        """단락 변환"""
        if not paragraph.text.strip():
            if self.config.processing.skip_empty_paragraphs:
                return ""
        
        # 텍스트 정리
        text = self._clean_text(paragraph.text)
        
        # 줄바꿈 처리
        if not self.config.paragraph.preserve_line_breaks:
            # 줄바꿈을 공백으로 변환 (단, 의도적인 줄바꿈은 유지)
            text = re.sub(r'\n(?!\n)', ' ', text)
            text = re.sub(r'\s+', ' ', text)  # 연속 공백 제거
        
        # 줄 길이 제한
        if self.config.paragraph.max_line_length > 0:
            text = self._wrap_text(text, self.config.paragraph.max_line_length)
        
        # 앞뒤 공백 제거
        if self.config.paragraph.trim_whitespace:
            text = text.strip()
        
        # 단락 간격 추가
        spacing = "\n" * self.config.paragraph.paragraph_spacing
        return text + spacing
    
    def _convert_list_item(self, list_item: ListItem) -> str:
        """리스트 항목 변환"""
        # 들여쓰기 계산
        indent = " " * (list_item.level * self.config.list.indent_size)
        
        # 리스트 마커 결정
        if list_item.list_type == ListType.BULLET:
            marker = self.config.list.bullet_marker
        else:
            # 번호 리스트
            if self.config.list.preserve_numbering and list_item.marker:
                marker = list_item.marker
            else:
                marker = self.config.list.ordered_style
        
        # 텍스트 정리
        text = self._clean_text(list_item.text)
        
        # 리스트 항목 생성
        result = f"{indent}{marker} {text}"
        
        # 압축 리스트가 아니면 빈 줄 추가
        if not self.config.list.compact_lists:
            result += "\n"
        
        return result
    
    def _convert_table(self, table: Table) -> str:
        """테이블 변환"""
        if not table.rows:
            return ""
        
        if self.config.table.format_type == TableFormatType.STANDARD:
            return self._convert_table_standard(table)
        elif self.config.table.format_type == TableFormatType.GRID:
            return self._convert_table_grid(table)
        else:  # SIMPLE
            return self._convert_table_simple(table)
    
    def _convert_table_standard(self, table: Table) -> str:
        """표준 Markdown 테이블 변환"""
        if not table.rows:
            return ""
        
        lines = []
        
        # 열 너비 계산
        max_cols = max(len(row.cells) for row in table.rows)
        col_widths = [self.config.table.min_column_width] * max_cols
        
        # 각 열의 최대 너비 계산
        for row in table.rows:
            for i, cell in enumerate(row.cells):
                if i < len(col_widths):
                    text_len = len(self._clean_text(cell.text))
                    col_widths[i] = max(col_widths[i], min(text_len + 2, self.config.table.max_column_width))
        
        # 테이블 행 생성
        for row_idx, row in enumerate(table.rows):
            cells = []
            for col_idx in range(max_cols):
                if col_idx < len(row.cells):
                    cell_text = self._clean_text(row.cells[col_idx].text)
                    if self.config.table.escape_pipes:
                        cell_text = cell_text.replace("|", "\\|")
                else:
                    cell_text = ""
                
                # 셀 패딩 적용
                padding = " " * self.config.table.cell_padding
                if self.config.table.align_columns:
                    cell_text = cell_text.ljust(col_widths[col_idx] - 2 * self.config.table.cell_padding)
                
                cells.append(f"{padding}{cell_text}{padding}")
            
            line = "|" + "|".join(cells) + "|"
            lines.append(line)
            
            # 헤더 구분선 (첫 번째 행 후)
            if row_idx == 0 and table.has_header:
                separator_cells = []
                for col_idx in range(max_cols):
                    sep = "-" * col_widths[col_idx]
                    separator_cells.append(sep)
                separator_line = "|" + "|".join(separator_cells) + "|"
                lines.append(separator_line)
        
        return "\n".join(lines) + "\n\n"
    
    def _convert_table_grid(self, table: Table) -> str:
        """Grid 스타일 테이블 변환 (확장 형식)"""
        # 간단한 구현 - 실제로는 더 복잡한 그리드 형식
        return self._convert_table_standard(table)
    
    def _convert_table_simple(self, table: Table) -> str:
        """간단한 테이블 변환"""
        if not table.rows:
            return ""
        
        lines = []
        for row in table.rows:
            cell_texts = [self._clean_text(cell.text) for cell in row.cells]
            line = " | ".join(cell_texts)
            lines.append(line)
        
        return "\n".join(lines) + "\n\n"
    
    def _convert_image(self, image: ImageInfo, output_path: Optional[Path]) -> str:
        """이미지 변환"""
        if not self.config.image.extract_images:
            return ""
        
        self._image_counter += 1
        
        # 이미지 파일명 생성
        image_filename = f"image_{self._image_counter:03d}.{image.format.lower()}"
        
        # 상대 경로 계산
        if output_path:
            image_dir = output_path.parent / self.config.image.image_directory
            image_path = image_dir / image_filename
            relative_path = f"{self.config.image.image_directory}/{image_filename}"
        else:
            relative_path = image_filename
        
        # Alt 텍스트 생성
        alt_text = self.config.image.alt_text_template.format(index=self._image_counter)
        
        # 작은 이미지 인라인 처리
        if (self.config.image.inline_small_images and 
            len(image.data) <= self.config.image.inline_size_threshold):
            
            # Base64 인코딩
            encoded_data = base64.b64encode(image.data).decode('utf-8')
            mime_type = f"image/{image.format.lower()}"
            return f"![{alt_text}](data:{mime_type};base64,{encoded_data})\n\n"
        
        # 일반 이미지 링크
        return f"![{alt_text}]({relative_path})\n\n"
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        if not self.config.processing.clean_text:
            return text
        
        # 유니코드 정규화
        if self.config.processing.normalize_unicode:
            text = unicodedata.normalize('NFC', text)
        
        # 특수 문자 처리
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Markdown 특수 문자 이스케이프
        markdown_chars = r'\\`*_{}[]()#+-.!|'
        for char in markdown_chars:
            if char in text and char not in ['*', '_']:  # 강조는 유지
                text = text.replace(char, f'\\{char}')
        
        # 연속 공백 정리
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()
    
    def _wrap_text(self, text: str, max_length: int) -> str:
        """텍스트 줄바꿈"""
        if max_length <= 0:
            return text
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            
            # 현재 줄에 추가할 수 있는지 확인
            if current_length + word_length + len(current_line) <= max_length:
                current_line.append(word)
                current_length += word_length
            else:
                # 현재 줄 완성
                if current_line:
                    lines.append(' '.join(current_line))
                
                # 새 줄 시작
                current_line = [word]
                current_length = word_length
        
        # 마지막 줄 추가
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def _generate_heading_id(self, text: str) -> str:
        """제목 ID 생성"""
        # 특수 문자 제거 및 소문자 변환
        id_text = re.sub(r'[^\w\s-]', '', text.lower())
        id_text = re.sub(r'[-\s]+', '-', id_text)
        id_text = id_text.strip('-')
        
        # 중복 방지
        original_id = id_text
        counter = 1
        while id_text in self._generated_ids:
            id_text = f"{original_id}-{counter}"
            counter += 1
        
        self._generated_ids.add(id_text)
        return id_text
    
    def _escape_yaml_string(self, text: str) -> str:
        """YAML 문자열 이스케이프"""
        return text.replace('"', '\\"').replace('\n', '\\n')
    
    def _join_parts(self, parts: List[str]) -> str:
        """Markdown 파트들 결합"""
        # 빈 파트 제거
        non_empty_parts = [part for part in parts if part.strip()]
        
        # 파트 간 구분을 위한 빈 줄 추가
        result = "\n\n".join(non_empty_parts)
        
        return result
    
    def _post_process_text(self, text: str) -> str:
        """최종 후처리"""
        # 연속된 빈 줄 제한
        max_newlines = self.config.processing.max_consecutive_newlines
        pattern = f'\n{{{max_newlines + 1},}}'
        replacement = '\n' * max_newlines
        text = re.sub(pattern, replacement, text)
        
        # 줄바꿈 타입 적용
        if self.config.output.line_ending != LineEndingType.LF:
            text = text.replace('\n', self.config.output.line_ending.value)
        
        # 파일 끝 빈 줄
        if self.config.output.add_final_newline and not text.endswith('\n'):
            text += self.config.output.line_ending.value
        
        return text
    
    def save_markdown(self, 
                     markdown_text: str, 
                     output_path: Path,
                     images: Optional[List[ImageInfo]] = None) -> None:
        """Markdown과 이미지를 파일로 저장"""
        try:
            # 출력 디렉토리 생성
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 백업 생성
            if self.config.output.backup_original and output_path.exists():
                backup_path = output_path.with_suffix(f"{output_path.suffix}.backup")
                output_path.rename(backup_path)
                self.logger.info(f"백업 생성: {backup_path}")
            
            # Markdown 파일 저장
            with open(output_path, 'w', encoding=self.config.output.encoding) as f:
                f.write(markdown_text)
            
            self.logger.info(f"Markdown 저장 완료: {output_path}")
            
            # 이미지 저장
            if images and self.config.image.extract_images:
                self._save_images(images, output_path.parent)
                
        except Exception as e:
            self.logger.error(f"파일 저장 실패: {e}")
            raise
    
    def _save_images(self, images: List[ImageInfo], base_dir: Path) -> None:
        """이미지 파일들 저장"""
        if not images:
            return
        
        # 이미지 디렉토리 생성
        image_dir = base_dir / self.config.image.image_directory
        image_dir.mkdir(parents=True, exist_ok=True)
        
        for i, image in enumerate(images, 1):
            try:
                # 파일명 생성
                filename = f"image_{i:03d}.{image.format.lower()}"
                image_path = image_dir / filename
                
                # 이미지 저장
                with open(image_path, 'wb') as f:
                    f.write(image.data)
                
                self.logger.debug(f"이미지 저장: {image_path}")
                
            except Exception as e:
                self.logger.error(f"이미지 저장 실패 ({filename}): {e}")
        
        self.logger.info(f"{len(images)}개 이미지 저장 완료: {image_dir}") 