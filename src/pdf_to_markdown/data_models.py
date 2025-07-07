"""
PDF to Markdown 변환기 데이터 모델

PDF 처리 과정에서 사용되는 데이터 구조들을 정의합니다.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from enum import Enum


class FontStyle(Enum):
    """폰트 스타일 열거형"""
    NORMAL = "normal"
    BOLD = "bold"
    ITALIC = "italic"
    BOLD_ITALIC = "bold_italic"


@dataclass
class FontInfo:
    """폰트 정보"""
    name: str
    size: float
    style: FontStyle
    color: Tuple[float, float, float]  # RGB 값 (0-1 범위)


@dataclass
class TextBlock:
    """텍스트 블록 정보"""
    text: str
    bbox: Tuple[float, float, float, float]  # (x0, y0, x1, y1)
    font_info: FontInfo
    page_num: int
    block_type: str = "text"  # text, image, table 등


@dataclass
class ImageInfo:
    """이미지 정보"""
    data: bytes
    width: int
    height: int
    format: str
    bbox: Tuple[float, float, float, float]
    page_num: int
    image_index: int


@dataclass
class DocumentMetadata:
    """문서 메타데이터"""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    page_count: int = 0
    file_size: int = 0
    is_encrypted: bool = False


@dataclass
class PageInfo:
    """페이지 정보"""
    page_num: int
    width: float
    height: float
    rotation: int
    text_blocks: List[TextBlock]
    images: List[ImageInfo]


@dataclass
class DocumentContent:
    """전체 문서 내용"""
    metadata: DocumentMetadata
    pages: List[PageInfo]
    total_text_blocks: int = 0
    total_images: int = 0


@dataclass
class ProcessingStats:
    """처리 통계"""
    total_pages: int
    processed_pages: int
    text_blocks_extracted: int
    images_extracted: int
    processing_time: float
    errors: List[str]
    warnings: List[str] 