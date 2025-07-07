"""
텍스트 구조 분석 결과 데이터 모델

PDF에서 추출한 텍스트를 구조화하여 표현하는 데이터 클래스들을 정의합니다.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from .data_models import TextBlock


class ElementType(Enum):
    """문서 요소 타입"""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    IMAGE = "image"
    UNKNOWN = "unknown"


class ListType(Enum):
    """리스트 타입"""
    BULLET = "bullet"          # • - * 등
    NUMBERED = "numbered"      # 1. 2. 3. 등
    LETTERED = "lettered"      # a. b. c. 등
    ROMAN = "roman"           # i. ii. iii. 등


@dataclass
class Heading:
    """제목 정보"""
    text: str
    level: int  # 1-6 (H1-H6)
    font_size: float
    font_name: str
    bbox: Tuple[float, float, float, float]
    page_num: int
    confidence: float  # 제목일 확신도 (0-1)


@dataclass
class Paragraph:
    """단락 정보"""
    text: str
    text_blocks: List[TextBlock]
    bbox: Tuple[float, float, float, float]
    page_num: int
    is_merged: bool = False  # 여러 블록이 병합되었는지 여부


@dataclass
class ListItem:
    """리스트 항목"""
    text: str
    list_type: ListType
    marker: str  # 실제 마커 텍스트 (•, 1., a. 등)
    level: int  # 들여쓰기 레벨 (0부터 시작)
    bbox: Tuple[float, float, float, float]
    page_num: int


@dataclass
class TableCell:
    """테이블 셀"""
    text: str
    row: int
    col: int
    rowspan: int = 1
    colspan: int = 1
    bbox: Tuple[float, float, float, float] = (0, 0, 0, 0)


@dataclass
class TableRow:
    """테이블 행"""
    cells: List[TableCell]
    row_index: int
    bbox: Tuple[float, float, float, float]


@dataclass
class Table:
    """테이블 정보"""
    rows: List[TableRow]
    bbox: Tuple[float, float, float, float]
    page_num: int
    has_header: bool = False
    confidence: float = 0.0  # 테이블일 확신도


@dataclass
class DocumentElement:
    """문서 요소 (범용)"""
    element_type: ElementType
    content: Any  # Heading, Paragraph, ListItem, Table 등
    bbox: Tuple[float, float, float, float]
    page_num: int
    order: int  # 문서 내 순서


@dataclass
class DocumentStructure:
    """분석된 문서 구조"""
    elements: List[DocumentElement]
    headings: List[Heading]
    paragraphs: List[Paragraph]
    lists: List[ListItem]
    tables: List[Table]
    
    # 구조 분석 통계
    total_elements: int = 0
    heading_count: int = 0
    paragraph_count: int = 0
    list_count: int = 0
    table_count: int = 0
    
    # 분석 품질 지표
    confidence_score: float = 0.0  # 전체 분석 확신도
    analysis_warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """초기화 후 통계 계산"""
        self.total_elements = len(self.elements)
        self.heading_count = len(self.headings)
        self.paragraph_count = len(self.paragraphs)
        self.list_count = len(self.lists)
        self.table_count = len(self.tables)


@dataclass
class FontStatistics:
    """폰트 사용 통계"""
    font_name: str
    font_size: float
    occurrence_count: int
    total_text_length: int
    is_bold: bool
    is_italic: bool
    
    # 계산된 속성
    @property
    def frequency_ratio(self) -> float:
        """전체 텍스트 대비 이 폰트가 사용된 비율"""
        return self.occurrence_count
    
    @property
    def avg_text_length(self) -> float:
        """평균 텍스트 길이"""
        return self.total_text_length / self.occurrence_count if self.occurrence_count > 0 else 0


@dataclass
class DocumentAnalytics:
    """문서 분석 결과"""
    font_statistics: List[FontStatistics]
    main_font: FontStatistics  # 본문 폰트
    heading_fonts: List[FontStatistics]  # 제목용 폰트들
    
    # 레이아웃 분석
    avg_line_spacing: float
    avg_paragraph_spacing: float
    page_margins: Tuple[float, float, float, float]  # top, right, bottom, left
    
    # 콘텐츠 분석
    total_words: int
    total_characters: int
    avg_words_per_paragraph: float
    reading_difficulty: str  # "easy", "medium", "hard" 