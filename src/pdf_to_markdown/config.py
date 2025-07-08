"""
Configuration 관리 모듈

설정 파일 로드/저장 및 CLI 옵션과의 병합을 담당합니다.
"""

import logging
import yaml
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any, Union
from .markdown_config import MarkdownConfig, ConfigPresets
from .exceptions import ConfigurationError


@dataclass
class ConversionConfig:
    """변환 관련 설정"""
    title_font_threshold: float = 1.2
    extract_images: bool = True
    preserve_formatting: bool = True
    merge_paragraphs: bool = False
    table_detection: bool = True
    min_confidence: float = 0.5
    skip_empty_pages: bool = True


@dataclass
class OutputConfig:
    """출력 관련 설정"""
    encoding: str = 'utf-8'
    line_ending: str = '\n'
    indent_size: int = 2
    image_format: str = 'png'
    create_output_dir: bool = True
    backup_existing: bool = False


@dataclass
class LoggingConfig:
    """로깅 설정"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    console_output: bool = True


@dataclass
class AppConfig:
    """전체 애플리케이션 설정"""
    conversion: ConversionConfig
    output: OutputConfig
    logging: LoggingConfig
    markdown: MarkdownConfig
    
    def __post_init__(self):
        """설정 초기화 후 검증"""
        self.validate()
    
    def validate(self) -> None:
        """설정 유효성 검사"""
        # 변환 설정 검증
        if self.conversion.title_font_threshold <= 0:
            raise ConfigurationError("title_font_threshold는 0보다 커야 합니다")
        
        if not 0 <= self.conversion.min_confidence <= 1:
            raise ConfigurationError("min_confidence는 0과 1 사이여야 합니다")
        
        # 출력 설정 검증
        if self.output.encoding not in ['utf-8', 'utf-16', 'ascii']:
            raise ConfigurationError(f"지원되지 않는 인코딩: {self.output.encoding}")
        
        if self.output.line_ending not in ['\n', '\r\n', '\r']:
            raise ConfigurationError(f"지원되지 않는 줄바꿈: {repr(self.output.line_ending)}")
        
        # 로깅 설정 검증
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.level.upper() not in valid_levels:
            raise ConfigurationError(f"지원되지 않는 로그 레벨: {self.logging.level}")
        
        # Markdown 설정 검증
        markdown_warnings = self.markdown.validate()
        if markdown_warnings:
            logger = logging.getLogger(__name__)
            for warning in markdown_warnings:
                logger.warning(f"Markdown 설정 경고: {warning}")


class ConfigManager:
    """설정 파일 관리자"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_config(self, config_path: Optional[Path] = None) -> AppConfig:
        """
        설정 파일을 로드합니다
        
        Args:
            config_path: 설정 파일 경로 (None이면 기본 설정 사용)
            
        Returns:
            AppConfig: 로드된 설정
            
        Raises:
            ConfigurationError: 설정 파일 로드 실패 시
        """
        try:
            if config_path is None or not config_path.exists():
                self.logger.info("기본 설정을 사용합니다")
                return self.get_default_config()
            
            self.logger.info(f"설정 파일 로드: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as file:
                config_dict = yaml.safe_load(file)
            
            if not config_dict:
                self.logger.warning("빈 설정 파일입니다. 기본 설정을 사용합니다")
                return self.get_default_config()
            
            return self._dict_to_config(config_dict)
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"YAML 파싱 오류: {e}")
        except Exception as e:
            raise ConfigurationError(f"설정 파일 로드 실패: {e}")
    
    def save_config(self, config: AppConfig, config_path: Path) -> None:
        """
        설정을 파일에 저장합니다
        
        Args:
            config: 저장할 설정
            config_path: 저장할 파일 경로
            
        Raises:
            ConfigurationError: 설정 파일 저장 실패 시
        """
        try:
            # 디렉토리 생성
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config_dict = self._config_to_dict(config)
            
            with open(config_path, 'w', encoding='utf-8') as file:
                yaml.dump(config_dict, file, 
                         default_flow_style=False, 
                         allow_unicode=True,
                         indent=2,
                         sort_keys=False)
            
            self.logger.info(f"설정 파일 저장 완료: {config_path}")
            
        except Exception as e:
            raise ConfigurationError(f"설정 파일 저장 실패: {e}")
    
    def get_default_config(self) -> AppConfig:
        """기본 설정을 반환합니다"""
        return AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=MarkdownConfig()
        )
    
    def get_preset_config(self, preset_name: str) -> AppConfig:
        """
        사전 정의된 설정 프리셋을 반환합니다
        
        Args:
            preset_name: 프리셋 이름 (github, minimal, documentation, publishing)
            
        Returns:
            AppConfig: 프리셋 설정
        """
        preset_mapping = {
            'github': ConfigPresets.github_flavored,
            'minimal': ConfigPresets.minimal,
            'documentation': ConfigPresets.documentation,
            'publishing': ConfigPresets.publishing,
        }
        
        if preset_name not in preset_mapping:
            available = ', '.join(preset_mapping.keys())
            raise ConfigurationError(f"알 수 없는 프리셋: {preset_name}. 사용 가능: {available}")
        
        markdown_config = preset_mapping[preset_name]()
        
        return AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=markdown_config
        )
    
    def merge_cli_options(self, config: AppConfig, cli_options: Dict[str, Any]) -> AppConfig:
        """
        CLI 옵션을 설정에 병합합니다
        
        Args:
            config: 기본 설정
            cli_options: CLI에서 전달된 옵션들
            
        Returns:
            AppConfig: 병합된 설정
        """
        # 깊은 복사를 위해 dict로 변환 후 다시 객체 생성
        config_dict = self._config_to_dict(config)
        
        # CLI 옵션 매핑
        cli_mapping = {
            'extract_images': ('conversion', 'extract_images'),
            'preserve_formatting': ('conversion', 'preserve_formatting'),
            'merge_paragraphs': ('conversion', 'merge_paragraphs'),
            'table_detection': ('conversion', 'table_detection'),
            'encoding': ('output', 'encoding'),
            'image_format': ('output', 'image_format'),
            'verbose': ('logging', 'level'),
            'quiet': ('logging', 'console_output'),
        }
        
        for cli_key, value in cli_options.items():
            if value is None:
                continue
                
            if cli_key in cli_mapping:
                section, setting_key = cli_mapping[cli_key]
                
                # 특별 처리
                if cli_key == 'verbose' and isinstance(value, int):
                    # verbose 카운트를 로그 레벨로 변환
                    levels = ['ERROR', 'WARNING', 'INFO', 'DEBUG']
                    level_index = min(value + 1, len(levels) - 1)
                    config_dict[section][setting_key] = levels[level_index]
                elif cli_key == 'quiet' and value:
                    config_dict[section][setting_key] = False
                else:
                    config_dict[section][setting_key] = value
        
        return self._dict_to_config(config_dict)
    
    def create_sample_config(self, output_path: Path) -> None:
        """샘플 설정 파일을 생성합니다"""
        sample_config = self.get_default_config()
        
        # 설명이 포함된 설정 파일 생성
        sample_dict = self._config_to_dict(sample_config)
        
        # 주석 추가를 위한 커스텀 YAML 생성
        yaml_content = self._generate_commented_yaml(sample_dict)
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(yaml_content)
        
        self.logger.info(f"샘플 설정 파일 생성: {output_path}")
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> AppConfig:
        """딕셔너리를 AppConfig 객체로 변환"""
        try:
            # 각 섹션별로 객체 생성
            conversion = ConversionConfig(**config_dict.get('conversion', {}))
            output = OutputConfig(**config_dict.get('output', {}))
            logging_config = LoggingConfig(**config_dict.get('logging', {}))
            
            # Markdown 설정은 별도 처리
            markdown_dict = config_dict.get('markdown', {})
            if markdown_dict:
                markdown = MarkdownConfig.from_dict(markdown_dict)
            else:
                markdown = MarkdownConfig()
            
            return AppConfig(
                conversion=conversion,
                output=output,
                logging=logging_config,
                markdown=markdown
            )
            
        except TypeError as e:
            raise ConfigurationError(f"잘못된 설정 형식: {e}")
    
    def _config_to_dict(self, config: AppConfig) -> Dict[str, Any]:
        """AppConfig 객체를 딕셔너리로 변환"""
        return {
            'conversion': asdict(config.conversion),
            'output': asdict(config.output),
            'logging': asdict(config.logging),
            'markdown': config.markdown.to_dict()
        }
    
    def _generate_commented_yaml(self, config_dict: Dict[str, Any]) -> str:
        """주석이 포함된 YAML 문자열 생성"""
        yaml_lines = [
            "# PDF to Markdown 변환기 설정 파일",
            "# 각 섹션별로 변환 옵션을 설정할 수 있습니다",
            "",
            "# 변환 관련 설정",
            "conversion:",
            "  title_font_threshold: 1.2  # 제목 인식을 위한 폰트 크기 임계값",
            "  extract_images: true       # 이미지 추출 여부",
            "  preserve_formatting: true  # 원본 형식 보존",
            "  merge_paragraphs: false    # 단락 병합 여부",
            "  table_detection: true      # 테이블 감지 여부",
            "  min_confidence: 0.5        # 최소 신뢰도",
            "  skip_empty_pages: true     # 빈 페이지 건너뛰기",
            "",
            "# 출력 관련 설정",
            "output:",
            "  encoding: utf-8            # 파일 인코딩",
            "  line_ending: '\\n'          # 줄바꿈 문자",
            "  indent_size: 2             # 들여쓰기 크기",
            "  image_format: png          # 이미지 형식",
            "  create_output_dir: true    # 출력 디렉토리 생성",
            "  backup_existing: false     # 기존 파일 백업",
            "",
            "# 로깅 설정",
            "logging:",
            "  level: INFO                # 로그 레벨 (DEBUG, INFO, WARNING, ERROR)",
            "  console_output: true       # 콘솔 출력 여부",
            "  file_path: null            # 로그 파일 경로 (null이면 파일 저장 안함)",
            "",
            "# Markdown 생성 세부 설정",
            "markdown:",
            "  heading:",
            "    max_level: 6",
            "    add_toc: false",
            "  paragraph:",
            "    max_line_length: 80",
            "    preserve_line_breaks: false",
            "  list:",
            "    bullet_marker: '-'",
            "    indent_size: 2",
            "  table:",
            "    format_type: standard",
            "    align_columns: true",
            "  image:",
            "    extract_images: true",
            "    image_directory: images",
            "  output:",
            "    encoding: utf-8",
            "    add_final_newline: true"
        ]
        
        return '\n'.join(yaml_lines) 