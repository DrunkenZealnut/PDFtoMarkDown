"""
설정 관리 모듈 테스트

config.py와 markdown_config.py의 기능을 테스트합니다.
"""

import os
import tempfile
import pytest
from pathlib import Path
from typing import Dict, Any

# 테스트 대상 모듈 import
from src.pdf_to_markdown.config import (
    AppConfig,
    ConversionConfig,
    OutputConfig,
    LoggingConfig,
    ConfigManager,
)
from src.pdf_to_markdown.markdown_config import (
    MarkdownConfig,
    HeadingConfig,
    ParagraphConfig,
    ListConfig,
    TableConfig,
    ImageConfig,
    MetadataConfig,
    ConfigPresets,
)
from src.pdf_to_markdown.exceptions import ConfigurationError


class TestAppConfig:
    """AppConfig 클래스 테스트"""

    def test_default_config_creation(self):
        """기본 설정 생성 테스트"""
        conversion = ConversionConfig()
        output = OutputConfig()
        logging = LoggingConfig()
        markdown = MarkdownConfig()
        
        config = AppConfig(
            conversion=conversion,
            output=output,
            logging=logging,
            markdown=markdown
        )
        
        assert config.conversion.title_font_threshold == 1.2
        assert config.output.encoding == 'utf-8'
        assert config.logging.level == "INFO"
        assert config.markdown.heading.max_level == 6

    def test_config_validation_success(self):
        """정상적인 설정 검증 테스트"""
        config = AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=MarkdownConfig()
        )
        # 예외가 발생하지 않아야 함
        config.validate()

    def test_config_validation_invalid_threshold(self):
        """잘못된 임계값 검증 테스트"""
        conversion = ConversionConfig(title_font_threshold=0)
        
        with pytest.raises(ConfigurationError):
            AppConfig(
                conversion=conversion,
                output=OutputConfig(),
                logging=LoggingConfig(),
                markdown=MarkdownConfig()
            )

    def test_config_validation_invalid_confidence(self):
        """잘못된 신뢰도 검증 테스트"""
        conversion = ConversionConfig(min_confidence=1.5)
        
        with pytest.raises(ConfigurationError):
            AppConfig(
                conversion=conversion,
                output=OutputConfig(),
                logging=LoggingConfig(),
                markdown=MarkdownConfig()
            )

    def test_config_validation_invalid_encoding(self):
        """잘못된 인코딩 검증 테스트"""
        output = OutputConfig(encoding='invalid-encoding')
        
        with pytest.raises(ConfigurationError):
            AppConfig(
                conversion=ConversionConfig(),
                output=output,
                logging=LoggingConfig(),
                markdown=MarkdownConfig()
            )


class TestMarkdownConfig:
    """MarkdownConfig 클래스 테스트"""

    def test_default_markdown_config(self):
        """기본 마크다운 설정 테스트"""
        config = MarkdownConfig()
        
        assert config.heading.max_level == 6
        assert config.paragraph.max_line_length == 80
        assert config.list.bullet_marker == "-"
        assert config.table.include_header is True
        assert config.image.extract_images is True

    def test_from_dict_creation(self):
        """딕셔너리에서 설정 생성 테스트"""
        config_dict = {
            'heading': {
                'max_level': 4,
                'add_toc': True
            },
            'paragraph': {
                'max_line_length': 100
            },
            'list': {
                'bullet_marker': '*'
            }
        }
        
        config = MarkdownConfig.from_dict(config_dict)
        
        assert config.heading.max_level == 4
        assert config.heading.add_toc is True
        assert config.paragraph.max_line_length == 100
        assert config.list.bullet_marker == '*'

    def test_to_dict_conversion(self):
        """설정을 딕셔너리로 변환 테스트"""
        config = MarkdownConfig()
        config.heading.max_level = 5
        config.paragraph.max_line_length = 90
        
        result_dict = config.to_dict()
        
        assert result_dict['heading']['max_level'] == 5
        assert result_dict['paragraph']['max_line_length'] == 90
        assert 'table' in result_dict
        assert 'image' in result_dict

    def test_config_validation(self):
        """설정 유효성 검사 테스트"""
        config = MarkdownConfig()
        warnings = config.validate()
        
        # 기본 설정은 경고가 없어야 함
        assert isinstance(warnings, list)

    def test_config_validation_with_warnings(self):
        """경고가 있는 설정 검증 테스트"""
        config = MarkdownConfig()
        config.heading.max_level = 2
        config.heading.min_level = 3  # max보다 큰 min
        config.image.quality = 150    # 범위 초과
        
        warnings = config.validate()
        
        assert len(warnings) > 0
        assert any("최대 레벨이 최소 레벨보다 작습니다" in w for w in warnings)
        assert any("이미지 품질은 1-100 범위여야 합니다" in w for w in warnings)


class TestConfigPresets:
    """설정 프리셋 테스트"""

    def test_github_preset(self):
        """GitHub 프리셋 테스트"""
        config = ConfigPresets.github_flavored()
        
        assert config.heading.add_toc is True
        assert config.heading.heading_ids is True
        assert config.list.bullet_marker == "-"

    def test_minimal_preset(self):
        """최소 프리셋 테스트"""
        config = ConfigPresets.minimal()
        
        assert config.metadata.include_yaml_frontmatter is False
        assert config.image.extract_images is False
        assert config.heading.add_toc is False

    def test_documentation_preset(self):
        """문서화 프리셋 테스트"""
        config = ConfigPresets.documentation()
        
        assert config.heading.add_toc is True
        assert config.heading.toc_max_level == 4
        assert config.paragraph.max_line_length == 100

    def test_publishing_preset(self):
        """출판 프리셋 테스트"""
        config = ConfigPresets.publishing()
        
        assert config.paragraph.max_line_length == 80
        assert config.image.max_width == 800
        assert config.image.quality == 90


class TestConfigManager:
    """ConfigManager 클래스 테스트"""

    def test_default_config(self):
        """기본 설정 로드 테스트"""
        manager = ConfigManager()
        config = manager.get_default_config()
        
        assert isinstance(config, AppConfig)
        assert config.conversion.title_font_threshold == 1.2
        assert config.output.encoding == 'utf-8'

    def test_preset_config_github(self):
        """GitHub 프리셋 설정 테스트"""
        manager = ConfigManager()
        config = manager.get_preset_config('github')
        
        assert isinstance(config, AppConfig)
        assert config.markdown.heading.add_toc is True
        assert config.markdown.heading.heading_ids is True

    def test_preset_config_invalid(self):
        """잘못된 프리셋 이름 테스트"""
        manager = ConfigManager()
        
        with pytest.raises(ConfigurationError) as exc_info:
            manager.get_preset_config('invalid_preset')
        
        assert "알 수 없는 프리셋" in str(exc_info.value)

    def test_cli_options_merge(self):
        """CLI 옵션 병합 테스트"""
        manager = ConfigManager()
        base_config = manager.get_default_config()
        
        cli_options = {
            'extract_images': False,
            'encoding': 'utf-16',
            'verbose': 2,
            'quiet': True
        }
        
        merged_config = manager.merge_cli_options(base_config, cli_options)
        
        assert merged_config.conversion.extract_images is False
        assert merged_config.output.encoding == 'utf-16'
        assert merged_config.logging.level == 'DEBUG'  # verbose=2
        assert merged_config.logging.console_output is False  # quiet=True

    def test_save_and_load_config(self):
        """설정 저장 및 로드 테스트"""
        manager = ConfigManager()
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # 설정 저장
            config = manager.get_default_config()
            config.conversion.extract_images = False
            config.output.encoding = 'utf-16'
            
            manager.save_config(config, temp_path)
            
            # 설정 로드
            loaded_config = manager.load_config(temp_path)
            
            assert loaded_config.conversion.extract_images is False
            assert loaded_config.output.encoding == 'utf-16'
            
        finally:
            # 임시 파일 삭제
            if temp_path.exists():
                temp_path.unlink()

    def test_load_nonexistent_config(self):
        """존재하지 않는 설정 파일 로드 테스트"""
        manager = ConfigManager()
        
        # 존재하지 않는 파일 경로
        nonexistent_path = Path("nonexistent_config.yaml")
        
        with pytest.raises(ConfigurationError):
            manager.load_config(nonexistent_path)

    def test_create_sample_config(self):
        """샘플 설정 파일 생성 테스트"""
        manager = ConfigManager()
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            manager.create_sample_config(temp_path)
            
            # 파일이 생성되었는지 확인
            assert temp_path.exists()
            
            # 파일 내용 확인
            content = temp_path.read_text(encoding='utf-8')
            assert "PDF to Markdown 변환기 설정 파일" in content
            assert "conversion:" in content
            assert "output:" in content
            assert "logging:" in content
            assert "markdown:" in content
            
        finally:
            # 임시 파일 삭제
            if temp_path.exists():
                temp_path.unlink()


class TestConfigIntegration:
    """설정 모듈 통합 테스트"""

    def test_full_workflow(self):
        """전체 설정 워크플로우 테스트"""
        manager = ConfigManager()
        
        # 1. 기본 설정 생성
        config = manager.get_default_config()
        assert isinstance(config, AppConfig)
        
        # 2. CLI 옵션 적용
        cli_options = {
            'extract_images': True,
            'verbose': 1,
            'encoding': 'utf-8'
        }
        config = manager.merge_cli_options(config, cli_options)
        
        # 3. 프리셋 설정과 비교
        github_config = manager.get_preset_config('github')
        
        # 4. 설정 검증
        config.validate()
        github_config.validate()
        
        # 모든 과정이 성공적으로 완료되어야 함
        assert config.conversion.extract_images is True
        assert github_config.markdown.heading.add_toc is True


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 