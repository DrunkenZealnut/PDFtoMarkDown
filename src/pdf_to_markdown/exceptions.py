"""
PDF to Markdown 변환기 예외 클래스

PDF 처리 과정에서 발생할 수 있는 다양한 예외상황을 정의합니다.
"""

from typing import Optional


class PDFProcessingError(Exception):
    """PDF 처리 관련 기본 예외 클래스"""
    
    def __init__(self, message: str, pdf_path: str = ""):
        self.message = message
        self.pdf_path = pdf_path
        super().__init__(self.message)
    
    def __str__(self):
        if self.pdf_path:
            return f"PDF 처리 오류 ({self.pdf_path}): {self.message}"
        return f"PDF 처리 오류: {self.message}"


class FileNotFoundError(PDFProcessingError):
    """PDF 파일을 찾을 수 없는 경우"""
    
    def __init__(self, pdf_path: str):
        message = f"PDF 파일을 찾을 수 없습니다: {pdf_path}"
        super().__init__(message, pdf_path)


class FileAccessError(PDFProcessingError):
    """PDF 파일에 접근할 수 없는 경우"""
    
    def __init__(self, pdf_path: str, reason: str = "권한 없음"):
        message = f"PDF 파일에 접근할 수 없습니다 ({reason})"
        super().__init__(message, pdf_path)


class CorruptedFileError(PDFProcessingError):
    """손상된 PDF 파일인 경우"""
    
    def __init__(self, pdf_path: str, details: str = ""):
        message = f"PDF 파일이 손상되었습니다"
        if details:
            message += f": {details}"
        super().__init__(message, pdf_path)


class EncryptedFileError(PDFProcessingError):
    """암호화된 PDF 파일인 경우"""
    
    def __init__(self, pdf_path: str):
        message = "암호화된 PDF 파일입니다. 현재 버전에서는 지원하지 않습니다."
        super().__init__(message, pdf_path)


class UnsupportedFormatError(PDFProcessingError):
    """지원하지 않는 PDF 형식인 경우"""
    
    def __init__(self, pdf_path: str, format_info: str = ""):
        message = f"지원하지 않는 PDF 형식입니다"
        if format_info:
            message += f": {format_info}"
        super().__init__(message, pdf_path)


class PageExtractionError(PDFProcessingError):
    """페이지 추출 중 오류가 발생한 경우"""
    
    def __init__(self, pdf_path: str, page_num: int, details: str = ""):
        message = f"페이지 {page_num + 1} 추출 중 오류 발생"
        if details:
            message += f": {details}"
        super().__init__(message, pdf_path)


class TextExtractionError(PDFProcessingError):
    """텍스트 추출 중 오류가 발생한 경우"""
    
    def __init__(self, pdf_path: str, page_num: Optional[int] = None, details: str = ""):
        if page_num is not None:
            message = f"페이지 {page_num + 1}에서 텍스트 추출 중 오류 발생"
        else:
            message = "텍스트 추출 중 오류 발생"
        
        if details:
            message += f": {details}"
        super().__init__(message, pdf_path)


class ImageExtractionError(PDFProcessingError):
    """이미지 추출 중 오류가 발생한 경우"""
    
    def __init__(self, pdf_path: str, page_num: Optional[int] = None, image_index: Optional[int] = None, details: str = ""):
        message = "이미지 추출 중 오류 발생"
        
        if page_num is not None:
            message += f" (페이지 {page_num + 1}"
            if image_index is not None:
                message += f", 이미지 {image_index + 1}"
            message += ")"
        
        if details:
            message += f": {details}"
        super().__init__(message, pdf_path)


class MemoryError(PDFProcessingError):
    """메모리 부족 오류"""
    
    def __init__(self, pdf_path: str, operation: str = ""):
        message = "메모리가 부족합니다"
        if operation:
            message += f" ({operation} 중)"
        super().__init__(message, pdf_path)


class TimeoutError(PDFProcessingError):
    """처리 시간 초과 오류"""
    
    def __init__(self, pdf_path: str, timeout_seconds: int):
        message = f"처리 시간이 초과되었습니다 ({timeout_seconds}초)"
        super().__init__(message, pdf_path) 