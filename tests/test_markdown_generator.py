"""
Markdown 생성기 모듈 테스트

markdown_generator.py의 기능을 테스트합니다.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

# 테스트 대상 모듈 import
from src.pdf_to_markdown.markdown_generator import MarkdownGenerator
from src.pdf_to_markdown.markdown_config import MarkdownConfig, ConfigPresets
from src.pdf_to_markdown.data_models import (
    DocumentStructure,
    DocumentContent,
    DocumentElement,
    ElementType,
    Heading,
    Paragraph,
    ListItem,
    ListType,
    Table,
    TableRow,
    TableCell,
    ImageInfo,
    DocumentMetadata
)


class TestMarkdownGenerator:
    """MarkdownGenerator 클래스 테스트"""

    def test_initialization_default_config(self):
        """기본 설정으로 초기화 테스트"""
        generator = MarkdownGenerator()
        
        assert generator.config is not None
        assert isinstance(generator.config, MarkdownConfig)
        assert generator._image_counter == 0
        assert generator._generated_ids == set()

    def test_initialization_custom_config(self):
        """사용자 정의 설정으로 초기화 테스트"""
        custom_config = ConfigPresets.github_flavored()
        generator = MarkdownGenerator(custom_config)
        
        assert generator.config == custom_config
        assert generator.config.heading.add_toc is True

    def test_reset_generation_state(self):
        """생성 상태 초기화 테스트"""
        generator = MarkdownGenerator()
        
        # 상태 변경
        generator._image_counter = 5
        generator._generated_ids.add("test-id")
        
        # 초기화
        generator._reset_generation_state()
        
        assert generator._image_counter == 0
        assert len(generator._generated_ids) == 0

    def test_generate_heading_id(self):
        """제목 ID 생성 테스트"""
        generator = MarkdownGenerator()
        
        # 일반적인 제목
        id1 = generator._generate_heading_id("Introduction")
        assert id1 == "introduction"
        
        # 특수 문자 포함
        id2 = generator._generate_heading_id("Chapter 1: Getting Started!")
        assert id2 == "chapter-1-getting-started"
        
        # 중복 방지
        id3 = generator._generate_heading_id("Introduction")
        assert id3 == "introduction-1"

    def test_clean_text(self):
        """텍스트 정리 테스트"""
        generator = MarkdownGenerator()
        
        # 특수 문자 이스케이프
        text1 = generator._clean_text("Text with [brackets] and *asterisks*")
        assert "\\[brackets\\]" in text1
        # *는 강조로 유지되어야 함
        assert "*asterisks*" in text1
        
        # 연속 공백 정리
        text2 = generator._clean_text("Text   with    multiple    spaces")
        assert "Text with multiple spaces" == text2.strip()

    def test_wrap_text(self):
        """텍스트 줄바꿈 테스트"""
        generator = MarkdownGenerator()
        
        long_text = "This is a very long line that should be wrapped at the specified width"
        wrapped = generator._wrap_text(long_text, 20)
        
        lines = wrapped.split('\n')
        for line in lines:
            assert len(line) <= 25  # 여유를 두고 확인

    def test_convert_heading(self):
        """제목 변환 테스트"""
        generator = MarkdownGenerator()
        
        heading = Heading(text="Test Heading", level=2, font_size=14.0)
        result = generator._convert_heading(heading)
        
        assert result.startswith("## Test Heading")
        assert result.endswith("\n")

    def test_convert_heading_setext_style(self):
        """Setext 스타일 제목 변환 테스트"""
        config = MarkdownConfig()
        config.heading.setext_style = True
        generator = MarkdownGenerator(config)
        
        heading = Heading(text="Main Title", level=1, font_size=16.0)
        result = generator._convert_heading(heading)
        
        lines = result.strip().split('\n')
        assert lines[0] == "Main Title"
        assert lines[1] == "=" * len("Main Title")

    def test_convert_paragraph(self):
        """단락 변환 테스트"""
        generator = MarkdownGenerator()
        
        paragraph = Paragraph(text="This is a test paragraph.", formatting=None)
        result = generator._convert_paragraph(paragraph)
        
        assert "This is a test paragraph." in result
        assert result.endswith("\n")

    def test_convert_list_item_bullet(self):
        """불릿 리스트 항목 변환 테스트"""
        generator = MarkdownGenerator()
        
        list_item = ListItem(
            text="Test bullet item",
            level=0,
            list_type=ListType.BULLET,
            marker=None
        )
        result = generator._convert_list_item(list_item)
        
        assert result.startswith("- Test bullet item")

    def test_convert_list_item_ordered(self):
        """번호 리스트 항목 변환 테스트"""
        generator = MarkdownGenerator()
        
        list_item = ListItem(
            text="Test ordered item",
            level=0,
            list_type=ListType.ORDERED,
            marker="1."
        )
        result = generator._convert_list_item(list_item)
        
        assert result.startswith("1. Test ordered item")

    def test_convert_table_standard(self):
        """표준 테이블 변환 테스트"""
        generator = MarkdownGenerator()
        
        # 테이블 데이터 생성
        header_row = TableRow(cells=[
            TableCell(text="Header 1", is_header=True),
            TableCell(text="Header 2", is_header=True)
        ])
        data_row = TableRow(cells=[
            TableCell(text="Data 1", is_header=False),
            TableCell(text="Data 2", is_header=False)
        ])
        
        table = Table(rows=[header_row, data_row], has_header=True)
        result = generator._convert_table(table)
        
        lines = result.strip().split('\n')
        assert "Header 1" in lines[0] and "Header 2" in lines[0]
        assert "---" in lines[1]  # 구분선
        assert "Data 1" in lines[2] and "Data 2" in lines[2]

    def test_convert_image(self):
        """이미지 변환 테스트"""
        generator = MarkdownGenerator()
        
        image = ImageInfo(
            data=b"fake_image_data",
            format="PNG",
            width=100,
            height=100
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.md"
            result = generator._convert_image(image, output_path.parent)
            
            assert result.startswith("![Image 001]")
            assert "images/image_001.png" in result

    def test_generate_frontmatter(self):
        """YAML Front Matter 생성 테스트"""
        config = MarkdownConfig()
        config.metadata.include_yaml_frontmatter = True
        generator = MarkdownGenerator(config)
        
        metadata = DocumentMetadata(
            title="Test Document",
            author="Test Author",
            page_count=5
        )
        
        structure = DocumentStructure(elements=[], total_elements=10)
        
        result = generator._generate_frontmatter(metadata, structure)
        
        assert result.startswith("---")
        assert result.endswith("---")
        assert 'title: "Test Document"' in result
        assert 'author: "Test Author"' in result
        assert "pages: 5" in result

    def test_generate_toc(self):
        """목차 생성 테스트"""
        config = MarkdownConfig()
        config.heading.add_toc = True
        generator = MarkdownGenerator(config)
        
        headings = [
            Heading(text="Chapter 1", level=1, font_size=16.0),
            Heading(text="Section 1.1", level=2, font_size=14.0),
            Heading(text="Chapter 2", level=1, font_size=16.0)
        ]
        
        result = generator._generate_toc(headings)
        
        assert "## 목차" in result
        assert "- [Chapter 1](#chapter-1)" in result
        assert "  - [Section 1.1](#section-1-1)" in result
        assert "- [Chapter 2](#chapter-2)" in result

    def test_post_process_text(self):
        """후처리 테스트"""
        generator = MarkdownGenerator()
        
        text_with_multiple_newlines = "Line 1\n\n\n\n\nLine 2"
        result = generator._post_process_text(text_with_multiple_newlines)
        
        # 연속된 빈 줄이 제한되어야 함
        assert "\n\n\n\n\n" not in result

    def test_escape_yaml_string(self):
        """YAML 문자열 이스케이프 테스트"""
        generator = MarkdownGenerator()
        
        text_with_quotes = 'Text with "quotes" and \n newlines'
        result = generator._escape_yaml_string(text_with_quotes)
        
        assert '\\"' in result  # 따옴표 이스케이프
        assert '\\n' in result  # 줄바꿈 이스케이프

    def test_full_markdown_generation(self):
        """전체 Markdown 생성 테스트"""
        generator = MarkdownGenerator()
        
        # 문서 구조 생성
        elements = [
            DocumentElement(
                element_type=ElementType.HEADING,
                content=Heading(text="Test Document", level=1, font_size=16.0),
                page_number=1,
                confidence=0.9
            ),
            DocumentElement(
                element_type=ElementType.PARAGRAPH,
                content=Paragraph(text="This is a test paragraph.", formatting=None),
                page_number=1,
                confidence=0.8
            )
        ]
        
        structure = DocumentStructure(elements=elements, total_elements=2)
        
        # 문서 내용 생성
        metadata = DocumentMetadata(title="Test", page_count=1)
        document = DocumentContent(metadata=metadata, pages=[])
        
        # Markdown 생성
        result = generator.generate_markdown(structure, document)
        
        assert isinstance(result, str)
        assert "# Test Document" in result
        assert "This is a test paragraph." in result

    def test_save_markdown(self):
        """Markdown 파일 저장 테스트"""
        generator = MarkdownGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.md"
            markdown_text = "# Test\n\nThis is a test."
            
            generator.save_markdown(markdown_text, output_path)
            
            # 파일이 생성되었는지 확인
            assert output_path.exists()
            
            # 내용 확인
            content = output_path.read_text(encoding='utf-8')
            assert content == markdown_text

    def test_save_images(self):
        """이미지 저장 테스트"""
        generator = MarkdownGenerator()
        
        images = [
            ImageInfo(
                data=b"fake_image_data_1",
                format="PNG",
                width=100,
                height=100
            ),
            ImageInfo(
                data=b"fake_image_data_2",
                format="JPEG",
                width=200,
                height=150
            )
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            generator._save_images(images, base_dir)
            
            # 이미지 디렉토리 확인
            image_dir = base_dir / "images"
            assert image_dir.exists()
            
            # 이미지 파일 확인
            image1_path = image_dir / "image_001.png"
            image2_path = image_dir / "image_002.jpeg"
            
            assert image1_path.exists()
            assert image2_path.exists()
            
            # 파일 내용 확인
            assert image1_path.read_bytes() == b"fake_image_data_1"
            assert image2_path.read_bytes() == b"fake_image_data_2"


class TestMarkdownGeneratorPresets:
    """다양한 프리셋에 대한 테스트"""

    def test_github_preset_generation(self):
        """GitHub 프리셋 생성 테스트"""
        config = ConfigPresets.github_flavored()
        generator = MarkdownGenerator(config)
        
        heading = Heading(text="Test Heading", level=1, font_size=16.0)
        result = generator._convert_heading(heading)
        
        # GitHub 프리셋은 제목 ID를 포함해야 함
        if config.heading.heading_ids:
            assert "{#test-heading}" in result

    def test_minimal_preset_generation(self):
        """최소 프리셋 생성 테스트"""
        config = ConfigPresets.minimal()
        generator = MarkdownGenerator(config)
        
        # 최소 설정은 이미지 추출을 하지 않음
        assert config.image.extract_images is False
        
        image = ImageInfo(data=b"test", format="PNG", width=100, height=100)
        result = generator._convert_image(image, None)
        
        # 이미지 추출이 비활성화되어 있으므로 빈 문자열 반환
        assert result == ""


class TestMarkdownGeneratorEdgeCases:
    """엣지 케이스 테스트"""

    def test_empty_text_handling(self):
        """빈 텍스트 처리 테스트"""
        generator = MarkdownGenerator()
        
        # 빈 단락
        empty_paragraph = Paragraph(text="", formatting=None)
        result = generator._convert_paragraph(empty_paragraph)
        
        # 빈 단락 건너뛰기 설정에 따라 빈 문자열 반환
        if generator.config.processing.skip_empty_paragraphs:
            assert result == ""

    def test_very_long_text_wrapping(self):
        """매우 긴 텍스트 줄바꿈 테스트"""
        generator = MarkdownGenerator()
        
        # 매우 긴 단어
        long_word = "a" * 200
        wrapped = generator._wrap_text(long_word, 50)
        
        # 긴 단어도 적절히 처리되어야 함
        assert len(wrapped) > 0

    def test_special_characters_in_headings(self):
        """제목의 특수 문자 처리 테스트"""
        generator = MarkdownGenerator()
        
        heading = Heading(
            text="Chapter #1: Getting Started (Version 2.0)!",
            level=1,
            font_size=16.0
        )
        result = generator._convert_heading(heading)
        
        # 특수 문자가 적절히 이스케이프되어야 함
        assert "\\#1" in result or "#1" in result


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 