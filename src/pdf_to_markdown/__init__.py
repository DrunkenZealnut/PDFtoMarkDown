"""
PDF to Markdown 변환기

PDF 문서를 Markdown 형식으로 변환하는 Python 라이브러리
"""

__version__ = "0.2.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "Convert PDF files to Markdown format"

# 주요 클래스들을 패키지 레벨에서 직접 import 가능하도록 설정
from .pdf_reader import PDFReader
from .text_parser import TextParser
from .markdown_generator import MarkdownGenerator
from .markdown_config import MarkdownConfig, ConfigPresets
from .config import ConfigManager, AppConfig, ConversionConfig, OutputConfig, LoggingConfig
from .converter import PDFToMarkdownConverter, ConversionManager, ConversionResult
from .ui_utils import ProgressReporter, StatusReporter, ConversionStats, BatchProgressReporter
from .data_models import (
    DocumentContent, DocumentMetadata, PageInfo, TextBlock, ImageInfo, 
    FontInfo, FontStyle, ProcessingStats
)
from .text_structures import (
    DocumentStructure, DocumentElement, ElementType,
    Heading, Paragraph, ListItem, Table, TableRow, TableCell,
    ListType, FontStatistics
)
from .exceptions import (
    PDFProcessingError, ConfigurationError, FileNotFoundError, FileAccessError,
    CorruptedFileError, EncryptedFileError, UnsupportedFormatError,
    PageExtractionError, TextExtractionError, ImageExtractionError,
    MemoryError, TimeoutError
)

# 편의 기능 함수들
def convert_pdf(pdf_path, output_path=None, config=None, quiet=False):
    """
    PDF 파일을 Markdown으로 변환하는 편의 함수
    
    Args:
        pdf_path (str | Path): PDF 파일 경로
        output_path (str | Path, optional): 출력 파일 경로
        config (AppConfig, optional): 설정 객체
        quiet (bool): 조용한 모드
        
    Returns:
        ConversionResult: 변환 결과
        
    Example:
        >>> from pdf_to_markdown import convert_pdf
        >>> result = convert_pdf("document.pdf", "output.md")
        >>> print(f"성공: {result.success}")
    """
    from pathlib import Path
    
    pdf_path = Path(pdf_path)
    output_path = Path(output_path) if output_path else None
    
    return ConversionManager.convert_single_file(
        pdf_path=pdf_path,
        output_path=output_path,
        config=config,
        quiet=quiet
    )


def convert_directory(input_dir, output_dir=None, config=None, pattern="*.pdf", quiet=False):
    """
    디렉토리 내 모든 PDF 파일을 변환하는 편의 함수
    
    Args:
        input_dir (str | Path): 입력 디렉토리
        output_dir (str | Path, optional): 출력 디렉토리
        config (AppConfig, optional): 설정 객체
        pattern (str): 파일 패턴
        quiet (bool): 조용한 모드
        
    Returns:
        List[ConversionResult]: 변환 결과 목록
        
    Example:
        >>> from pdf_to_markdown import convert_directory
        >>> results = convert_directory("./pdfs", "./markdown")
        >>> success_count = sum(1 for r in results if r.success)
        >>> print(f"성공: {success_count}/{len(results)}")
    """
    from pathlib import Path
    
    input_dir = Path(input_dir)
    output_dir = Path(output_dir) if output_dir else None
    
    return ConversionManager.convert_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        config=config,
        pattern=pattern,
        quiet=quiet
    )


def create_config(preset_name=None, **kwargs):
    """
    설정 객체를 생성하는 편의 함수
    
    Args:
        preset_name (str, optional): 프리셋 이름 (github, minimal, documentation, publishing)
        **kwargs: 추가 설정 옵션
        
    Returns:
        AppConfig: 설정 객체
        
    Example:
        >>> from pdf_to_markdown import create_config
        >>> config = create_config("github", extract_images=True)
    """
    config_manager = ConfigManager()
    
    if preset_name:
        config = config_manager.get_preset_config(preset_name)
    else:
        config = config_manager.get_default_config()
    
    # kwargs를 통한 추가 설정 적용
    if kwargs:
        config = config_manager.merge_cli_options(config, kwargs)
    
    return config


# 패키지에서 공개할 심볼들
__all__ = [
    # 버전 정보
    "__version__",
    "__author__", 
    "__email__",
    "__description__",
    
    # 핵심 클래스들
    "PDFReader",
    "TextParser", 
    "MarkdownGenerator",
    "PDFToMarkdownConverter",
    "ConversionManager",
    
    # 설정 관련
    "MarkdownConfig",
    "ConfigPresets",
    "ConfigManager",
    "AppConfig",
    "ConversionConfig",
    "OutputConfig",
    "LoggingConfig",
    
    # UI 및 유틸리티
    "ProgressReporter",
    "StatusReporter",
    "ConversionStats",
    "BatchProgressReporter",
    
    # 데이터 모델
    "DocumentContent",
    "DocumentMetadata",
    "PageInfo",
    "TextBlock",
    "ImageInfo",
    "FontInfo",
    "FontStyle",
    "ProcessingStats",
    "ConversionResult",
    
    # 텍스트 구조
    "DocumentStructure",
    "DocumentElement",
    "ElementType",
    "Heading",
    "Paragraph",
    "ListItem",
    "Table",
    "TableRow",
    "TableCell",
    "ListType",
    "FontStatistics",
    
    # 예외 클래스들
    "PDFProcessingError",
    "ConfigurationError",
    "FileNotFoundError",
    "FileAccessError",
    "CorruptedFileError",
    "EncryptedFileError",
    "UnsupportedFormatError",
    "PageExtractionError",
    "TextExtractionError",
    "ImageExtractionError",
    "MemoryError",
    "TimeoutError",
    
    # 편의 함수들
    "convert_pdf",
    "convert_directory",
    "create_config",
] 