"""
Text Parser 모듈 테스트

TextParser 클래스의 각 기능을 개별적으로 테스트합니다.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from src.pdf_to_markdown.text_parser import TextParser
from src.pdf_to_markdown.data_models import (
    TextBlock, FontInfo, FontStyle, DocumentContent, PageInfo, ImageInfo
)
from src.pdf_to_markdown.text_structures import (
    ElementType, ListType, Heading, Paragraph, ListItem, Table
)


class TestTextParser:
    """TextParser 클래스 테스트"""
    
    @pytest.fixture
    def parser(self):
        """기본 TextParser 인스턴스"""
        return TextParser(
            title_font_threshold=1.2,
            merge_paragraphs=False,
            table_detection=True
        )
    
    @pytest.fixture
    def sample_font_info(self):
        """샘플 폰트 정보"""
        return FontInfo(
            name="Arial",
            size=12.0,
            style=FontStyle.NORMAL,
            color=(0, 0, 0)
        )
    
    @pytest.fixture
    def sample_text_blocks(self, sample_font_info):
        """테스트용 텍스트 블록들"""
        blocks = []
        
        # 제목 (큰 폰트, 볼드)
        title_font = FontInfo("Arial", 18.0, FontStyle.BOLD, (0, 0, 0))
        title_block = TextBlock(
            text="주요 제목",
            bbox=(50, 700, 200, 720),
            font_info=title_font,
            page_num=1
        )
        blocks.append(title_block)
        
        # 부제목 (중간 폰트, 볼드)
        subtitle_font = FontInfo("Arial", 14.0, FontStyle.BOLD, (0, 0, 0))
        subtitle_block = TextBlock(
            text="부제목 예시",
            bbox=(50, 650, 150, 665),
            font_info=subtitle_font,
            page_num=1
        )
        blocks.append(subtitle_block)
        
        # 본문 텍스트
        body_blocks = [
            TextBlock(
                text="이것은 본문 텍스트입니다.",
                bbox=(50, 600, 300, 615),
                font_info=sample_font_info,
                page_num=1
            ),
            TextBlock(
                text="여러 줄로 구성된 단락의 예시입니다.",
                bbox=(50, 580, 320, 595),
                font_info=sample_font_info,
                page_num=1
            )
        ]
        blocks.extend(body_blocks)
        
        # 리스트 항목들
        list_blocks = [
            TextBlock(
                text="• 첫 번째 리스트 항목",
                bbox=(70, 550, 250, 565),
                font_info=sample_font_info,
                page_num=1
            ),
            TextBlock(
                text="• 두 번째 리스트 항목",
                bbox=(70, 530, 250, 545),
                font_info=sample_font_info,
                page_num=1
            ),
            TextBlock(
                text="1. 번호 있는 리스트",
                bbox=(70, 500, 200, 515),
                font_info=sample_font_info,
                page_num=1
            )
        ]
        blocks.extend(list_blocks)
        
        return blocks
    
    @pytest.fixture
    def sample_document(self, sample_text_blocks):
        """테스트용 문서 내용"""
        page_info = PageInfo(
            page_num=1,
            text_blocks=sample_text_blocks,
            images=[],
            page_size=(612, 792)
        )
        
        return DocumentContent(
            pages=[page_info],
            metadata=Mock(),
            total_pages=1
        )
    
    def test_parser_initialization(self):
        """TextParser 초기화 테스트"""
        parser = TextParser(
            title_font_threshold=1.5,
            merge_paragraphs=True,
            table_detection=False
        )
        
        assert parser.title_font_threshold == 1.5
        assert parser.merge_paragraphs is True
        assert parser.table_detection is False
        assert parser._font_stats is None
        assert parser._main_font is None
    
    def test_analyze_font_statistics(self, parser, sample_text_blocks):
        """폰트 통계 분석 테스트"""
        parser._analyze_font_statistics(sample_text_blocks)
        
        # 폰트 통계가 생성되었는지 확인
        assert parser._font_stats is not None
        assert len(parser._font_stats) > 0
        
        # 본문 폰트가 설정되었는지 확인
        assert parser._main_font is not None
        assert parser._main_font.font_name == "Arial"
        assert parser._main_font.font_size == 12.0
    
    def test_identify_headings(self, parser, sample_text_blocks):
        """제목 식별 테스트"""
        # 먼저 폰트 통계 분석
        parser._analyze_font_statistics(sample_text_blocks)
        
        headings = parser.identify_headings(sample_text_blocks)
        
        # 제목이 식별되었는지 확인
        assert len(headings) >= 2  # 주요 제목, 부제목
        
        # 첫 번째 제목 확인
        main_heading = headings[0]
        assert main_heading.text == "주요 제목"
        assert main_heading.level == 1  # 가장 큰 폰트이므로 H1
        assert main_heading.font_size == 18.0
        assert main_heading.confidence > 0.5
        
        # 두 번째 제목 확인 (부제목)
        sub_heading = next((h for h in headings if h.text == "부제목 예시"), None)
        assert sub_heading is not None
        assert sub_heading.level > main_heading.level  # 더 낮은 레벨
    
    def test_identify_paragraphs(self, parser, sample_text_blocks):
        """단락 식별 테스트"""
        # 먼저 제목을 식별
        parser._analyze_font_statistics(sample_text_blocks)
        headings = parser.identify_headings(sample_text_blocks)
        
        paragraphs = parser.identify_paragraphs(sample_text_blocks, headings)
        
        # 단락이 식별되었는지 확인
        assert len(paragraphs) > 0
        
        # 제목이 아닌 텍스트만 단락으로 분류되었는지 확인
        heading_texts = {h.text for h in headings}
        for paragraph in paragraphs:
            assert paragraph.text not in heading_texts
    
    def test_identify_lists(self, parser, sample_text_blocks):
        """리스트 식별 테스트"""
        lists = parser.identify_lists(sample_text_blocks)
        
        # 리스트 항목이 식별되었는지 확인
        assert len(lists) >= 3  # 불릿 2개, 번호 1개
        
        # 불릿 리스트 확인
        bullet_items = [item for item in lists if item.list_type == ListType.BULLET]
        assert len(bullet_items) >= 2
        assert bullet_items[0].marker == "•"
        assert "첫 번째" in bullet_items[0].text
        
        # 번호 리스트 확인
        numbered_items = [item for item in lists if item.list_type == ListType.NUMBERED]
        assert len(numbered_items) >= 1
        assert numbered_items[0].marker == "1."
        assert "번호 있는" in numbered_items[0].text
    
    def test_list_pattern_matching(self, parser):
        """리스트 패턴 매칭 테스트"""
        test_cases = [
            ("• 불릿 포인트", ListType.BULLET, "•"),
            ("- 대시 리스트", ListType.BULLET, "-"),
            ("* 별표 리스트", ListType.BULLET, "*"),
            ("1. 번호 리스트", ListType.NUMBERED, "1."),
            ("2) 괄호 번호", ListType.NUMBERED, "2)"),
            ("(3) 양괄호 번호", ListType.NUMBERED, "(3)"),
            ("a. 소문자 알파벳", ListType.LETTERED, "a."),
            ("A. 대문자 알파벳", ListType.LETTERED, "A."),
            ("i. 로마 숫자 소문자", ListType.ROMAN, "i."),
            ("II. 로마 숫자 대문자", ListType.ROMAN, "II."),
        ]
        
        for text, expected_type, expected_marker in test_cases:
            # 각 패턴에 대해 매칭 테스트
            found_match = False
            for list_type, patterns in parser.list_patterns.items():
                for pattern in patterns:
                    import re
                    match = re.match(pattern, text)
                    if match:
                        assert list_type == expected_type, f"패턴 매칭 실패: {text}"
                        assert match.group(0).strip() == expected_marker, f"마커 추출 실패: {text}"
                        found_match = True
                        break
                if found_match:
                    break
            
            assert found_match, f"패턴 매칭되지 않음: {text}"
    
    def test_table_detection(self, parser, sample_document):
        """테이블 감지 테스트"""
        # 테이블 감지 활성화
        parser.table_detection = True
        tables = parser.identify_tables(sample_document)
        
        # 현재 샘플 데이터에는 테이블이 없으므로 빈 리스트 예상
        assert isinstance(tables, list)
        
        # 테이블 감지 비활성화
        parser.table_detection = False
        tables = parser.identify_tables(sample_document)
        assert len(tables) == 0
    
    def test_document_structure_analysis(self, parser, sample_document):
        """전체 문서 구조 분석 테스트"""
        structure = parser.analyze_document_structure(sample_document)
        
        # 구조 분석 결과 확인
        assert structure.total_elements > 0
        assert structure.heading_count >= 2
        assert structure.paragraph_count >= 2
        assert structure.list_count >= 3
        
        # 신뢰도 점수 확인
        assert 0.0 <= structure.confidence_score <= 1.0
        
        # 요소들이 올바른 순서로 정렬되었는지 확인
        prev_y = float('inf')
        for element in structure.elements:
            current_y = element.bbox[1]
            assert current_y <= prev_y, "요소들이 올바른 순서로 정렬되지 않음"
            prev_y = current_y
    
    def test_indentation_level_calculation(self, parser):
        """들여쓰기 레벨 계산 테스트"""
        # 기본 여백 (50)에서 시작
        assert parser._calculate_indentation_level(40) == 0
        assert parser._calculate_indentation_level(50) == 0
        
        # 첫 번째 들여쓰기 (20씩 증가)
        assert parser._calculate_indentation_level(70) == 1
        assert parser._calculate_indentation_level(90) == 2
        assert parser._calculate_indentation_level(110) == 3
        
        # 최대 레벨 제한 (5)
        assert parser._calculate_indentation_level(200) == 5
    
    def test_title_case_detection(self, parser):
        """제목 형식 감지 테스트"""
        # 제목 형식
        assert parser._is_title_case("주요 제목") is True
        assert parser._is_title_case("Chapter 1: Introduction") is True
        assert parser._is_title_case("A Short Title") is True
        
        # 제목이 아닌 형식
        assert parser._is_title_case("") is False
        assert parser._is_title_case("ALL UPPERCASE TEXT") is False
        assert parser._is_title_case("lowercase text") is False
        assert parser._is_title_case("이것은 매우 긴 텍스트로서 제목이라기보다는 본문에 가까운 내용입니다. 제목은 보통 짧기 때문입니다.") is False
    
    def test_paragraph_merging(self):
        """단락 병합 기능 테스트"""
        parser = TextParser(merge_paragraphs=True)
        
        # 테스트용 텍스트 블록들 생성
        font_info = FontInfo("Arial", 12.0, FontStyle.NORMAL, (0, 0, 0))
        
        blocks = [
            TextBlock("첫 번째 문장입니다.", (50, 100, 200, 115), font_info, 1),
            TextBlock("두 번째 문장입니다.", (50, 80, 200, 95), font_info, 1),
            TextBlock("마지막 문장입니다.", (50, 60, 200, 75), font_info, 1),
        ]
        
        # 문서 생성
        page_info = PageInfo(
            page_num=1,
            text_blocks=blocks,
            images=[],
            page_size=(612, 792)
        )
        document = DocumentContent(pages=[page_info], metadata=Mock(), total_pages=1)
        
        # 구조 분석
        structure = parser.analyze_document_structure(document)
        
        # 병합된 단락이 있는지 확인
        merged_paragraphs = [p for p in structure.paragraphs if p.is_merged]
        if merged_paragraphs:
            assert len(merged_paragraphs[0].text_blocks) > 1
    
    def test_confidence_score_calculation(self, parser):
        """확신도 점수 계산 테스트"""
        from src.pdf_to_markdown.text_structures import DocumentElement
        
        # 높은 확신도 제목 생성
        high_conf_heading = Heading(
            text="High Confidence Title",
            level=1,
            font_size=18.0,
            font_name="Arial",
            bbox=(0, 0, 100, 20),
            page_num=1,
            confidence=0.9
        )
        
        # 낮은 확신도 제목 생성
        low_conf_heading = Heading(
            text="Low Confidence Title",
            level=2,
            font_size=14.0,
            font_name="Arial",
            bbox=(0, 30, 100, 50),
            page_num=1,
            confidence=0.3
        )
        
        elements = [
            DocumentElement(
                element_type=ElementType.HEADING,
                content=high_conf_heading,
                bbox=high_conf_heading.bbox,
                page_num=1,
                order=0
            ),
            DocumentElement(
                element_type=ElementType.HEADING,
                content=low_conf_heading,
                bbox=low_conf_heading.bbox,
                page_num=1,
                order=1
            )
        ]
        
        confidence = parser._calculate_confidence_score(elements)
        
        # 가중평균이므로 0.3과 0.9 사이의 값
        assert 0.3 < confidence < 0.9
    
    def test_analysis_warnings(self, parser):
        """분석 경고 생성 테스트"""
        from src.pdf_to_markdown.text_structures import DocumentElement
        
        # H1 다음에 바로 H3 (H2 건너뛰기)
        heading1 = Heading("Title 1", 1, 18.0, "Arial", (0, 0, 100, 20), 1, 0.9)
        heading3 = Heading("Title 3", 3, 14.0, "Arial", (0, 30, 100, 50), 1, 0.8)
        
        elements = [
            DocumentElement(ElementType.HEADING, heading1, heading1.bbox, 1, 0),
            DocumentElement(ElementType.HEADING, heading3, heading3.bbox, 1, 1)
        ]
        
        warnings = parser._generate_analysis_warnings(elements)
        
        # 제목 레벨 건너뛰기 경고 확인
        level_skip_warnings = [w for w in warnings if "건너뛰어짐" in w]
        assert len(level_skip_warnings) > 0


@pytest.mark.integration
class TestTextParserIntegration:
    """TextParser 통합 테스트"""
    
    def test_with_real_pdf_sample(self):
        """실제 PDF 샘플과의 통합 테스트"""
        # 실제 sample.pdf가 있다면 테스트
        sample_path = Path("test_files/sample.pdf")
        if not sample_path.exists():
            pytest.skip("test_files/sample.pdf 파일이 없습니다")
        
        from src.pdf_to_markdown.pdf_reader import PDFReader
        
        # PDF 읽기
        with PDFReader(str(sample_path)) as reader:
            document = reader.extract_document()
        
        # 텍스트 파싱
        parser = TextParser()
        structure = parser.analyze_document_structure(document)
        
        # 기본 검증
        assert structure.total_elements > 0
        assert structure.confidence_score > 0.0
        assert len(structure.analysis_warnings) >= 0
        
        print(f"분석 결과: {structure.heading_count}개 제목, {structure.paragraph_count}개 단락")


if __name__ == "__main__":
    # 간단한 실행 테스트
    pytest.main([__file__, "-v"]) 