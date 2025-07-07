"""
PDF Reader 모듈 테스트

PDFReader 클래스의 주요 기능들을 테스트합니다.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pymupdf as fitz

# 프로젝트 모듈 import
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf_to_markdown.pdf_reader import PDFReader
from pdf_to_markdown.data_models import FontStyle, DocumentMetadata
from pdf_to_markdown.exceptions import (
    FileNotFoundError, FileAccessError, CorruptedFileError,
    EncryptedFileError, PageExtractionError, TextExtractionError
)


class TestPDFReader:
    """PDFReader 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        # 테스트용 PDF 파일 경로
        self.test_pdf_path = Path("test_files/sample.pdf")
        self.table_pdf_path = Path("test_files/table_sample.pdf")
        
        # 존재하지 않는 파일 경로
        self.nonexistent_path = Path("nonexistent_file.pdf")
        
        # 임시 빈 파일
        self.temp_dir = tempfile.mkdtemp()
        self.empty_file_path = Path(self.temp_dir) / "empty.pdf"
        self.empty_file_path.touch()
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        # 임시 파일 정리
        if self.empty_file_path.exists():
            self.empty_file_path.unlink()
        if Path(self.temp_dir).exists():
            os.rmdir(self.temp_dir)
    
    def test_init_success(self):
        """정상적인 PDF 파일로 초기화 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다. create_test_pdf.py를 먼저 실행하세요.")
        
        reader = PDFReader(self.test_pdf_path)
        
        assert reader.pdf_path == self.test_pdf_path
        assert reader.extract_images is True
        assert reader.stats.total_pages == 0  # 아직 문서를 열지 않음
        assert len(reader.stats.errors) == 0
    
    def test_init_with_nonexistent_file(self):
        """존재하지 않는 파일로 초기화 시 예외 발생 테스트"""
        with pytest.raises(FileNotFoundError):
            PDFReader(self.nonexistent_path)
    
    def test_init_with_empty_file(self):
        """빈 파일로 초기화 시 예외 발생 테스트"""
        with pytest.raises(CorruptedFileError):
            PDFReader(self.empty_file_path)
    
    def test_open_document_success(self):
        """정상적인 PDF 문서 열기 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        reader = PDFReader(self.test_pdf_path)
        
        try:
            doc = reader.open_document()
            
            assert doc is not None
            assert reader._is_open is True
            assert reader.stats.total_pages > 0
        finally:
            reader.close_document()
    
    def test_close_document(self):
        """PDF 문서 닫기 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        reader = PDFReader(self.test_pdf_path)
        
        # 문서 열기
        reader.open_document()
        assert reader._is_open is True
        
        # 문서 닫기
        reader.close_document()
        assert reader._is_open is False
        assert reader._document is None
    
    def test_context_manager(self):
        """컨텍스트 매니저 기능 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        with PDFReader(self.test_pdf_path) as reader:
            assert reader._is_open is True
            assert reader._document is not None
        
        # 컨텍스트 종료 후 자동으로 닫혀야 함
        assert reader._is_open is False
    
    def test_get_document_info(self):
        """문서 메타데이터 추출 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        reader = PDFReader(self.test_pdf_path)
        metadata = reader.get_document_info()
        
        assert isinstance(metadata, DocumentMetadata)
        assert metadata.page_count > 0
        assert metadata.file_size > 0
        assert metadata.is_encrypted is False
    
    def test_extract_page_text_success(self):
        """페이지 텍스트 추출 성공 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        with PDFReader(self.test_pdf_path) as reader:
            text_blocks = reader.extract_page_text(0)  # 첫 번째 페이지
            
            assert len(text_blocks) > 0
            assert all(block.text.strip() for block in text_blocks)
            assert all(block.page_num == 0 for block in text_blocks)
            assert all(block.font_info is not None for block in text_blocks)
    
    def test_extract_page_text_invalid_page(self):
        """잘못된 페이지 번호로 텍스트 추출 시 예외 발생 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        with PDFReader(self.test_pdf_path) as reader:
            # 음수 페이지 번호
            with pytest.raises(PageExtractionError):
                reader.extract_page_text(-1)
            
            # 존재하지 않는 페이지 번호
            with pytest.raises(PageExtractionError):
                reader.extract_page_text(999)
    
    def test_extract_page_text_without_opening(self):
        """문서를 열지 않고 텍스트 추출 시 예외 발생 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        reader = PDFReader(self.test_pdf_path)
        
        with pytest.raises(TextExtractionError):
            reader.extract_page_text(0)
    
    def test_extract_images_success(self):
        """이미지 추출 성공 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        with PDFReader(self.test_pdf_path, extract_images=True) as reader:
            images = reader.extract_images(0)
            
            # 테스트 PDF에 이미지가 있다면 추출되어야 함
            # 없다면 빈 리스트여야 함
            assert isinstance(images, list)
            
            for image in images:
                assert image.data is not None
                assert image.width > 0
                assert image.height > 0
                assert image.page_num == 0
    
    def test_extract_images_disabled(self):
        """이미지 추출 비활성화 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        with PDFReader(self.test_pdf_path, extract_images=False) as reader:
            images = reader.extract_images(0)
            
            # 이미지 추출이 비활성화되어 있으면 빈 리스트 반환
            assert images == []
    
    def test_extract_page_content(self):
        """페이지 전체 콘텐츠 추출 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        reader = PDFReader(self.test_pdf_path)
        page_info = reader.extract_page_content(0)
        
        assert page_info.page_num == 0
        assert page_info.width > 0
        assert page_info.height > 0
        assert len(page_info.text_blocks) > 0
        assert isinstance(page_info.images, list)
    
    def test_extract_all_pages(self):
        """모든 페이지 추출 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        reader = PDFReader(self.test_pdf_path)
        
        # 제너레이터로 모든 페이지 추출
        pages = list(reader.extract_all_pages())
        
        assert len(pages) > 0
        assert reader.stats.processed_pages == len(pages)
        assert reader.stats.processing_time > 0
        
        # 페이지 번호가 순차적인지 확인
        for i, page in enumerate(pages):
            assert page.page_num == i
    
    def test_extract_document(self):
        """전체 문서 추출 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        reader = PDFReader(self.test_pdf_path)
        document = reader.extract_document()
        
        assert document.metadata is not None
        assert len(document.pages) > 0
        assert document.total_text_blocks > 0
        assert document.metadata.page_count == len(document.pages)
    
    def test_font_info_extraction(self):
        """폰트 정보 추출 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        with PDFReader(self.test_pdf_path) as reader:
            text_blocks = reader.extract_page_text(0)
            
            for block in text_blocks:
                font_info = block.font_info
                
                assert font_info.name is not None
                assert font_info.size > 0
                assert isinstance(font_info.style, FontStyle)
                assert len(font_info.color) == 3  # RGB 튜플
                assert all(0 <= c <= 1 for c in font_info.color)  # 0-1 범위
    
    def test_processing_stats(self):
        """처리 통계 테스트"""
        if not self.test_pdf_path.exists():
            pytest.skip("테스트 PDF 파일이 없습니다.")
        
        reader = PDFReader(self.test_pdf_path)
        
        # 초기 상태
        stats = reader.get_processing_stats()
        assert stats.processed_pages == 0
        assert stats.text_blocks_extracted == 0
        assert stats.images_extracted == 0
        
        # 문서 처리 후
        reader.extract_document()
        stats = reader.get_processing_stats()
        
        assert stats.processed_pages > 0
        assert stats.text_blocks_extracted > 0
        assert stats.processing_time > 0
    
    def test_table_pdf_processing(self):
        """테이블 포함 PDF 처리 테스트"""
        if not self.table_pdf_path.exists():
            pytest.skip("테이블 테스트 PDF 파일이 없습니다.")
        
        with PDFReader(self.table_pdf_path) as reader:
            text_blocks = reader.extract_page_text(0)
            
            # 테이블 텍스트가 추출되는지 확인
            assert len(text_blocks) > 0
            
            # 테이블 관련 텍스트가 포함되어 있는지 확인
            all_text = " ".join(block.text for block in text_blocks)
            assert len(all_text.strip()) > 0


class TestPDFReaderErrorHandling:
    """PDFReader 오류 처리 테스트"""
    
    def test_mock_corrupted_file(self):
        """손상된 파일 처리 테스트 (모킹)"""
        with patch('pymupdf.open') as mock_open:
            mock_open.side_effect = fitz.FileDataError("Corrupted file")
            
            # 임시 파일 생성
            temp_file = Path(tempfile.mktemp(suffix=".pdf"))
            temp_file.write_bytes(b"fake pdf content")
            
            try:
                reader = PDFReader(temp_file)
                with pytest.raises(CorruptedFileError):
                    reader.open_document()
            finally:
                if temp_file.exists():
                    temp_file.unlink()
    
    def test_mock_encrypted_file(self):
        """암호화된 파일 처리 테스트 (모킹)"""
        with patch('pymupdf.open') as mock_open:
            mock_doc = Mock()
            mock_doc.needs_pass = True
            mock_open.return_value = mock_doc
            
            # 임시 파일 생성
            temp_file = Path(tempfile.mktemp(suffix=".pdf"))
            temp_file.write_bytes(b"fake pdf content")
            
            try:
                reader = PDFReader(temp_file)
                with pytest.raises(EncryptedFileError):
                    reader.open_document()
            finally:
                if temp_file.exists():
                    temp_file.unlink()


# 테스트 실행 유틸리티 함수
def run_basic_tests():
    """기본 테스트들을 실행합니다"""
    test_instance = TestPDFReader()
    test_instance.setup_method()
    
    try:
        print("PDF Reader 기본 테스트 실행 중...")
        
        # 기본 초기화 테스트
        test_instance.test_init_success()
        print("✅ 초기화 테스트 통과")
        
        # 문서 열기/닫기 테스트
        test_instance.test_open_document_success()
        print("✅ 문서 열기/닫기 테스트 통과")
        
        # 메타데이터 추출 테스트
        test_instance.test_get_document_info()
        print("✅ 메타데이터 추출 테스트 통과")
        
        # 텍스트 추출 테스트
        test_instance.test_extract_page_text_success()
        print("✅ 텍스트 추출 테스트 통과")
        
        # 전체 문서 추출 테스트
        test_instance.test_extract_document()
        print("✅ 전체 문서 추출 테스트 통과")
        
        print("🎉 모든 기본 테스트 통과!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False
    finally:
        test_instance.teardown_method()


if __name__ == "__main__":
    # 직접 실행 시 기본 테스트 수행
    run_basic_tests() 