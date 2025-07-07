"""
PDF Reader 모듈

PDF 파일을 읽고 텍스트, 이미지, 메타데이터를 추출하는 기능을 제공합니다.
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Iterator
from contextlib import contextmanager

import pymupdf as fitz
from PIL import Image
import io

from .data_models import (
    TextBlock, FontInfo, FontStyle, ImageInfo, DocumentMetadata,
    PageInfo, DocumentContent, ProcessingStats
)
from .exceptions import (
    FileNotFoundError, FileAccessError, CorruptedFileError,
    EncryptedFileError, UnsupportedFormatError, PageExtractionError,
    TextExtractionError, ImageExtractionError, MemoryError
)


class PDFReader:
    """
    PDF 파일을 읽고 구조화된 데이터로 변환하는 클래스
    
    주요 기능:
    - PDF 파일 안전한 열기/닫기
    - 페이지별 텍스트 블록 추출
    - 폰트 정보 분석
    - 이미지 추출 및 저장
    - 문서 메타데이터 추출
    """
    
    def __init__(self, pdf_path: Path, extract_images: bool = True):
        """
        PDF Reader 초기화
        
        Args:
            pdf_path: PDF 파일 경로
            extract_images: 이미지 추출 여부
        """
        self.pdf_path = Path(pdf_path)
        self.should_extract_images = extract_images
        self.logger = logging.getLogger(__name__)
        
        # 문서 관련 속성
        self._document: Optional[fitz.Document] = None
        self._is_open = False
        
        # 통계 정보
        self.stats = ProcessingStats(
            total_pages=0,
            processed_pages=0,
            text_blocks_extracted=0,
            images_extracted=0,
            processing_time=0.0,
            errors=[],
            warnings=[]
        )
        
        # 초기 검증
        self._validate_file()
    
    def _validate_file(self) -> None:
        """PDF 파일 유효성 검사"""
        # 파일 존재 확인
        if not self.pdf_path.exists():
            raise FileNotFoundError(str(self.pdf_path))
        
        # 파일 접근 권한 확인
        if not os.access(self.pdf_path, os.R_OK):
            raise FileAccessError(str(self.pdf_path), "읽기 권한 없음")
        
        # 파일 크기 확인 (0바이트 파일 체크)
        if self.pdf_path.stat().st_size == 0:
            raise CorruptedFileError(str(self.pdf_path), "빈 파일")
    
    @contextmanager
    def _document_context(self):
        """문서 열기/닫기를 안전하게 관리하는 컨텍스트 매니저"""
        try:
            self.open_document()
            yield self._document
        finally:
            self.close_document()
    
    def open_document(self) -> fitz.Document:
        """
        PDF 문서를 안전하게 엽니다
        
        Returns:
            fitz.Document: 열린 PDF 문서
            
        Raises:
            CorruptedFileError: 손상된 PDF 파일
            EncryptedFileError: 암호화된 PDF 파일
            UnsupportedFormatError: 지원하지 않는 형식
        """
        if self._is_open and self._document:
            return self._document
        
        try:
            self._document = fitz.open(str(self.pdf_path))
            
            # 암호화 확인
            if self._document.needs_pass:
                self._document.close()
                raise EncryptedFileError(str(self.pdf_path))
            
            # 페이지 수 확인
            if self._document.page_count == 0:
                self._document.close()
                raise CorruptedFileError(str(self.pdf_path), "페이지가 없음")
            
            self._is_open = True
            self.stats.total_pages = self._document.page_count
            
            self.logger.info(f"PDF 문서 열기 성공: {self.pdf_path} ({self._document.page_count}페이지)")
            return self._document
            
        except fitz.FileDataError as e:
            raise CorruptedFileError(str(self.pdf_path), str(e))
        except fitz.EmptyFileError:
            raise CorruptedFileError(str(self.pdf_path), "빈 파일")
        except Exception as e:
            raise UnsupportedFormatError(str(self.pdf_path), str(e))
    
    def close_document(self) -> None:
        """PDF 문서를 안전하게 닫습니다"""
        if self._document and self._is_open:
            try:
                self._document.close()
                self.logger.debug(f"PDF 문서 닫기 완료: {self.pdf_path}")
            except Exception as e:
                self.logger.warning(f"PDF 문서 닫기 중 오류: {e}")
            finally:
                self._document = None
                self._is_open = False
    
    def get_document_info(self) -> DocumentMetadata:
        """
        문서 메타데이터를 반환합니다
        
        Returns:
            DocumentMetadata: 문서 메타데이터
        """
        with self._document_context() as doc:
            metadata = doc.metadata
            
            return DocumentMetadata(
                title=metadata.get('title', ''),
                author=metadata.get('author', ''),
                subject=metadata.get('subject', ''),
                creator=metadata.get('creator', ''),
                producer=metadata.get('producer', ''),
                creation_date=metadata.get('creationDate', ''),
                modification_date=metadata.get('modDate', ''),
                page_count=doc.page_count,
                file_size=self.pdf_path.stat().st_size,
                is_encrypted=doc.needs_pass
            )
    
    def extract_page_text(self, page_num: int) -> List[TextBlock]:
        """
        페이지에서 텍스트 블록을 추출합니다
        
        Args:
            page_num: 페이지 번호 (0부터 시작)
            
        Returns:
            List[TextBlock]: 추출된 텍스트 블록들
            
        Raises:
            PageExtractionError: 페이지 추출 오류
            TextExtractionError: 텍스트 추출 오류
        """
        if not self._document or not self._is_open:
            raise TextExtractionError(str(self.pdf_path), page_num, "문서가 열리지 않음")
        
        if page_num < 0 or page_num >= self._document.page_count:
            raise PageExtractionError(str(self.pdf_path), page_num, "잘못된 페이지 번호")
        
        try:
            page = self._document[page_num]
            text_blocks = []
            
            # 텍스트 딕셔너리 추출 (폰트 정보 포함)
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:  # 텍스트 블록인 경우
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if text:  # 빈 텍스트 제외
                                # 폰트 정보 추출
                                font_info = self._extract_font_info(span)
                                
                                # 텍스트 블록 생성
                                text_block = TextBlock(
                                    text=text,
                                    bbox=span.get("bbox", (0, 0, 0, 0)),
                                    font_info=font_info,
                                    page_num=page_num,
                                    block_type="text"
                                )
                                text_blocks.append(text_block)
            
            self.stats.text_blocks_extracted += len(text_blocks)
            self.logger.debug(f"페이지 {page_num + 1}에서 {len(text_blocks)}개 텍스트 블록 추출")
            
            return text_blocks
            
        except Exception as e:
            error_msg = f"텍스트 추출 중 오류: {str(e)}"
            self.stats.errors.append(error_msg)
            raise TextExtractionError(str(self.pdf_path), page_num, str(e))
    
    def _extract_font_info(self, span: Dict[str, Any]) -> FontInfo:
        """
        스팬에서 폰트 정보를 추출합니다
        
        Args:
            span: PyMuPDF 스팬 딕셔너리
            
        Returns:
            FontInfo: 폰트 정보
        """
        font_name = span.get("font", "Unknown")
        font_size = span.get("size", 12.0)
        font_flags = span.get("flags", 0)
        color = span.get("color", 0)
        
        # 폰트 스타일 결정
        is_bold = bool(font_flags & 2**4)  # Bold flag
        is_italic = bool(font_flags & 2**1)  # Italic flag
        
        if is_bold and is_italic:
            style = FontStyle.BOLD_ITALIC
        elif is_bold:
            style = FontStyle.BOLD
        elif is_italic:
            style = FontStyle.ITALIC
        else:
            style = FontStyle.NORMAL
        
        # 색상을 RGB로 변환 (0-1 범위)
        if isinstance(color, int):
            # 정수 색상값을 RGB로 변환
            r = ((color >> 16) & 0xFF) / 255.0
            g = ((color >> 8) & 0xFF) / 255.0
            b = (color & 0xFF) / 255.0
            rgb_color = (r, g, b)
        else:
            rgb_color = (0.0, 0.0, 0.0)  # 기본값: 검정색
        
        return FontInfo(
            name=font_name,
            size=font_size,
            style=style,
            color=rgb_color
        )
    
    def extract_images(self, page_num: int) -> List[ImageInfo]:
        """
        페이지에서 이미지를 추출합니다
        
        Args:
            page_num: 페이지 번호 (0부터 시작)
            
        Returns:
            List[ImageInfo]: 추출된 이미지 정보들
            
        Raises:
            PageExtractionError: 페이지 추출 오류
            ImageExtractionError: 이미지 추출 오류
        """
        if not self.should_extract_images:
            return []
        
        if not self._document or not self._is_open:
            raise ImageExtractionError(str(self.pdf_path), page_num, None, "문서가 열리지 않음")
        
        if page_num < 0 or page_num >= self._document.page_count:
            raise PageExtractionError(str(self.pdf_path), page_num, "잘못된 페이지 번호")
        
        try:
            page = self._document[page_num]
            images = []
            
            # 페이지의 이미지 목록 가져오기
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # 이미지 데이터 추출
                    xref = img[0]
                    pix = fitz.Pixmap(self._document, xref)
                    
                    # CMYK 색상 공간을 RGB로 변환
                    if pix.n - pix.alpha < 4:  # GRAY 또는 RGB
                        img_data = pix.tobytes("png")
                    else:  # CMYK
                        pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
                        img_data = pix_rgb.tobytes("png")
                        pix_rgb = None
                    
                    # 이미지 정보 생성
                    image_info = ImageInfo(
                        data=img_data,
                        width=pix.width,
                        height=pix.height,
                        format="png",
                        bbox=page.get_image_bbox(img),
                        page_num=page_num,
                        image_index=img_index
                    )
                    
                    images.append(image_info)
                    pix = None  # 메모리 정리
                    
                except Exception as e:
                    warning_msg = f"페이지 {page_num + 1}의 이미지 {img_index + 1} 추출 실패: {str(e)}"
                    self.stats.warnings.append(warning_msg)
                    self.logger.warning(warning_msg)
            
            self.stats.images_extracted += len(images)
            self.logger.debug(f"페이지 {page_num + 1}에서 {len(images)}개 이미지 추출")
            
            return images
            
        except Exception as e:
            error_msg = f"이미지 추출 중 오류: {str(e)}"
            self.stats.errors.append(error_msg)
            raise ImageExtractionError(str(self.pdf_path), page_num, None, str(e))
    
    def extract_page_content(self, page_num: int) -> PageInfo:
        """
        페이지의 모든 콘텐츠를 추출합니다
        
        Args:
            page_num: 페이지 번호 (0부터 시작)
            
        Returns:
            PageInfo: 페이지 정보
        """
        with self._document_context() as doc:
            page = doc[page_num]
            
            # 페이지 기본 정보
            rect = page.rect
            rotation = page.rotation
            
            # 텍스트 및 이미지 추출
            text_blocks = self.extract_page_text(page_num)
            images = self.extract_images(page_num)
            
            return PageInfo(
                page_num=page_num,
                width=rect.width,
                height=rect.height,
                rotation=rotation,
                text_blocks=text_blocks,
                images=images
            )
    
    def extract_all_pages(self) -> Iterator[PageInfo]:
        """
        모든 페이지의 콘텐츠를 순차적으로 추출합니다 (제너레이터)
        
        Yields:
            PageInfo: 각 페이지 정보
        """
        start_time = time.time()
        
        with self._document_context() as doc:
            for page_num in range(doc.page_count):
                try:
                    page_info = self.extract_page_content(page_num)
                    self.stats.processed_pages += 1
                    yield page_info
                    
                except Exception as e:
                    error_msg = f"페이지 {page_num + 1} 처리 실패: {str(e)}"
                    self.stats.errors.append(error_msg)
                    self.logger.error(error_msg)
        
        self.stats.processing_time = time.time() - start_time
    
    def extract_document(self) -> DocumentContent:
        """
        전체 문서의 콘텐츠를 추출합니다
        
        Returns:
            DocumentContent: 문서 내용
        """
        # 메타데이터 추출
        metadata = self.get_document_info()
        
        # 모든 페이지 추출
        pages = list(self.extract_all_pages())
        
        # 통계 업데이트
        total_text_blocks = sum(len(page.text_blocks) for page in pages)
        total_images = sum(len(page.images) for page in pages)
        
        return DocumentContent(
            metadata=metadata,
            pages=pages,
            total_text_blocks=total_text_blocks,
            total_images=total_images
        )
    
    def get_processing_stats(self) -> ProcessingStats:
        """
        처리 통계를 반환합니다
        
        Returns:
            ProcessingStats: 처리 통계
        """
        return self.stats
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.open_document()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close_document()
    
    def __del__(self):
        """소멸자 - 문서가 열려있다면 닫기"""
        self.close_document() 