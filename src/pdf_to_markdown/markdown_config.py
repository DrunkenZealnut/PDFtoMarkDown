"""
Markdown 생성 설정 모듈

Markdown 변환 과정에서 사용되는 다양한 옵션들을 관리합니다.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path


class LineEndingType(Enum):
    """줄바꿈 타입"""
    LF = "\n"      # Unix/Linux/macOS
    CRLF = "\r\n"  # Windows
    CR = "\r"      # Classic Mac


class ImageFormatType(Enum):
    """이미지 형식"""
    ORIGINAL = "original"  # 원본 형식 유지
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"


class TableFormatType(Enum):
    """테이블 형식"""
    STANDARD = "standard"     # 표준 Markdown 테이블
    GRID = "grid"            # Grid 스타일 테이블 (확장)
    SIMPLE = "simple"        # 간단한 형식


@dataclass
class HeadingConfig:
    """제목 변환 설정"""
    max_level: int = 6                    # 최대 제목 레벨 (1-6)
    min_level: int = 1                    # 최소 제목 레벨
    add_toc: bool = False                 # 목차(TOC) 생성 여부
    toc_max_level: int = 3                # 목차에 포함할 최대 레벨
    heading_ids: bool = False             # 제목에 ID 추가 여부
    setext_style: bool = False            # Setext 스타일 제목 사용 (= 및 - 언더라인)


@dataclass
class ParagraphConfig:
    """단락 변환 설정"""
    preserve_line_breaks: bool = False    # 원본 줄바꿈 유지
    max_line_length: int = 80            # 최대 줄 길이 (0이면 제한 없음)
    paragraph_spacing: int = 1           # 단락 간 빈 줄 수
    indent_nested: bool = False          # 중첩된 단락 들여쓰기
    trim_whitespace: bool = True         # 앞뒤 공백 제거


@dataclass
class ListConfig:
    """리스트 변환 설정"""
    bullet_marker: str = "-"             # 불릿 리스트 마커 (-, *, +)
    ordered_style: str = "1."            # 번호 리스트 스타일 (1., 1), a., i.)
    indent_size: int = 2                 # 들여쓰기 크기 (공백 수)
    preserve_numbering: bool = True      # 원본 번호 유지
    compact_lists: bool = False          # 압축된 리스트 (빈 줄 없음)
    max_depth: int = 6                   # 최대 중첩 깊이


@dataclass
class TableConfig:
    """테이블 변환 설정"""
    format_type: TableFormatType = TableFormatType.STANDARD
    include_header: bool = True          # 헤더 행 포함
    align_columns: bool = True           # 열 정렬
    min_column_width: int = 3           # 최소 열 너비
    max_column_width: int = 50          # 최대 열 너비
    cell_padding: int = 1               # 셀 패딩 (공백 수)
    escape_pipes: bool = True           # 파이프 문자 이스케이프


@dataclass
class ImageConfig:
    """이미지 변환 설정"""
    extract_images: bool = True          # 이미지 추출 여부
    image_directory: str = "images"      # 이미지 저장 디렉토리
    format_type: ImageFormatType = ImageFormatType.ORIGINAL
    max_width: Optional[int] = None      # 최대 너비 (픽셀)
    max_height: Optional[int] = None     # 최대 높이 (픽셀)
    quality: int = 85                    # JPEG 품질 (1-100)
    inline_small_images: bool = False    # 작은 이미지를 인라인으로 포함
    inline_size_threshold: int = 1024    # 인라인 포함 임계값 (바이트)
    alt_text_template: str = "Image {index}"  # 대체 텍스트 템플릿


@dataclass
class MetadataConfig:
    """메타데이터 변환 설정"""
    include_yaml_frontmatter: bool = True    # YAML Front Matter 포함
    include_title: bool = True               # 제목 포함
    include_author: bool = True              # 작성자 포함
    include_creation_date: bool = True       # 생성 날짜 포함
    include_page_count: bool = True          # 페이지 수 포함
    include_processing_info: bool = False    # 처리 정보 포함
    custom_fields: Dict[str, str] = field(default_factory=dict)  # 사용자 정의 필드


@dataclass
class OutputConfig:
    """출력 설정"""
    encoding: str = "utf-8"                  # 파일 인코딩
    line_ending: LineEndingType = LineEndingType.LF
    add_final_newline: bool = True           # 파일 끝에 빈 줄 추가
    backup_original: bool = False            # 원본 파일 백업
    overwrite_existing: bool = False         # 기존 파일 덮어쓰기
    output_directory: Optional[str] = None   # 출력 디렉토리
    filename_template: str = "{name}.md"     # 파일명 템플릿


@dataclass
class ProcessingConfig:
    """처리 설정"""
    skip_empty_paragraphs: bool = True       # 빈 단락 건너뛰기
    merge_consecutive_lists: bool = True     # 연속된 리스트 병합
    clean_text: bool = True                  # 텍스트 정리 (특수문자, 공백 등)
    normalize_unicode: bool = True           # 유니코드 정규화
    handle_page_breaks: bool = True          # 페이지 나누기 처리
    max_consecutive_newlines: int = 2        # 최대 연속 빈 줄 수


@dataclass
class MarkdownConfig:
    """Markdown 생성 종합 설정"""
    heading: HeadingConfig = field(default_factory=HeadingConfig)
    paragraph: ParagraphConfig = field(default_factory=ParagraphConfig)
    list: ListConfig = field(default_factory=ListConfig)
    table: TableConfig = field(default_factory=TableConfig)
    image: ImageConfig = field(default_factory=ImageConfig)
    metadata: MetadataConfig = field(default_factory=MetadataConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'MarkdownConfig':
        """딕셔너리에서 설정 생성"""
        config = cls()
        
        for section_name, section_config in config_dict.items():
            if hasattr(config, section_name):
                section_obj = getattr(config, section_name)
                for key, value in section_config.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
        
        return config
    
    def to_dict(self) -> Dict:
        """설정을 딕셔너리로 변환"""
        result = {}
        
        for field_name in ['heading', 'paragraph', 'list', 'table', 
                          'image', 'metadata', 'output', 'processing']:
            section_obj = getattr(self, field_name)
            section_dict = {}
            
            for attr_name in dir(section_obj):
                if not attr_name.startswith('_'):
                    attr_value = getattr(section_obj, attr_name)
                    if not callable(attr_value):
                        if isinstance(attr_value, Enum):
                            section_dict[attr_name] = attr_value.value
                        else:
                            section_dict[attr_name] = attr_value
            
            result[field_name] = section_dict
        
        return result
    
    def validate(self) -> List[str]:
        """설정 유효성 검사"""
        warnings = []
        
        # 제목 설정 검사
        if self.heading.max_level < self.heading.min_level:
            warnings.append("제목 최대 레벨이 최소 레벨보다 작습니다")
        
        if self.heading.toc_max_level > self.heading.max_level:
            warnings.append("목차 최대 레벨이 제목 최대 레벨보다 큽니다")
        
        # 단락 설정 검사
        if self.paragraph.max_line_length > 0 and self.paragraph.max_line_length < 20:
            warnings.append("최대 줄 길이가 너무 짧습니다 (최소 20자 권장)")
        
        # 리스트 설정 검사
        if self.list.bullet_marker not in ["-", "*", "+"]:
            warnings.append(f"지원되지 않는 불릿 마커: {self.list.bullet_marker}")
        
        if self.list.indent_size < 1:
            warnings.append("들여쓰기 크기는 1 이상이어야 합니다")
        
        # 이미지 설정 검사
        if self.image.quality < 1 or self.image.quality > 100:
            warnings.append("이미지 품질은 1-100 범위여야 합니다")
        
        # 처리 설정 검사
        if self.processing.max_consecutive_newlines < 1:
            warnings.append("최대 연속 빈 줄 수는 1 이상이어야 합니다")
        
        return warnings


# 사전 정의된 설정 프리셋
class ConfigPresets:
    """설정 프리셋 모음"""
    
    @staticmethod
    def github_flavored() -> MarkdownConfig:
        """GitHub Flavored Markdown 설정"""
        config = MarkdownConfig()
        config.heading.add_toc = True
        config.heading.heading_ids = True
        config.table.format_type = TableFormatType.STANDARD
        config.list.bullet_marker = "-"
        config.output.line_ending = LineEndingType.LF
        return config
    
    @staticmethod
    def minimal() -> MarkdownConfig:
        """최소한의 설정"""
        config = MarkdownConfig()
        config.metadata.include_yaml_frontmatter = False
        config.image.extract_images = False
        config.processing.clean_text = False
        config.heading.add_toc = False
        return config
    
    @staticmethod
    def documentation() -> MarkdownConfig:
        """문서 작성용 설정"""
        config = MarkdownConfig()
        config.heading.add_toc = True
        config.heading.toc_max_level = 4
        config.paragraph.max_line_length = 100
        config.list.compact_lists = False
        config.metadata.include_processing_info = True
        return config
    
    @staticmethod
    def publishing() -> MarkdownConfig:
        """출판용 설정"""
        config = MarkdownConfig()
        config.paragraph.max_line_length = 80
        config.paragraph.preserve_line_breaks = False
        config.processing.clean_text = True
        config.processing.normalize_unicode = True
        config.image.max_width = 800
        config.image.quality = 90
        return config 