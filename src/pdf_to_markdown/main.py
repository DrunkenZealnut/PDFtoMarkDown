"""
PDF to Markdown 변환기 CLI 인터페이스

Click 라이브러리를 사용한 명령행 도구입니다.
"""

import logging
import sys
import click
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime

from .config import ConfigManager, AppConfig
from .exceptions import PDFProcessingError, ConfigurationError
from .pdf_reader import PDFReader
from .text_parser import TextParser
from .markdown_generator import MarkdownGenerator


def setup_logging(config: AppConfig) -> None:
    """로깅 설정"""
    # 로그 레벨 설정
    level = getattr(logging, config.logging.level.upper())
    
    # 로그 포맷 설정
    formatter = logging.Formatter(config.logging.format)
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 콘솔 핸들러 추가
    if config.logging.console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 파일 핸들러 추가
    if config.logging.file_path:
        file_path = Path(config.logging.file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def validate_input_file(ctx, param, value):
    """입력 파일 유효성 검사"""
    if value is None:
        return value
    
    path = Path(value)
    if not path.exists():
        raise click.BadParameter(f"파일을 찾을 수 없습니다: {path}")
    
    if not path.is_file():
        raise click.BadParameter(f"디렉토리가 아닌 파일이어야 합니다: {path}")
    
    if path.suffix.lower() != '.pdf':
        raise click.BadParameter(f"PDF 파일이어야 합니다: {path}")
    
    return path


def validate_config_file(ctx, param, value):
    """설정 파일 유효성 검사"""
    if value is None:
        return value
    
    path = Path(value)
    if not path.exists():
        raise click.BadParameter(f"설정 파일을 찾을 수 없습니다: {path}")
    
    if path.suffix.lower() not in ['.yaml', '.yml']:
        raise click.BadParameter(f"YAML 파일이어야 합니다: {path}")
    
    return path


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """PDF to Markdown 변환기"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument('input_file', 
                type=click.Path(exists=True, path_type=Path),
                callback=validate_input_file)
@click.argument('output_file', 
                required=False,
                type=click.Path(path_type=Path))
@click.option('--extract-images', '-i', 
              is_flag=True, 
              help='이미지 추출 및 저장')
@click.option('--batch', '-b',
              is_flag=True,
              help='일괄 처리 모드 (입력이 디렉토리인 경우)')
@click.option('--config', '-c',
              type=click.Path(path_type=Path),
              callback=validate_config_file,
              help='설정 파일 경로 (.yaml)')
@click.option('--preset', '-p',
              type=click.Choice(['github', 'minimal', 'documentation', 'publishing']),
              help='사전 정의된 설정 프리셋')
@click.option('--verbose', '-v',
              count=True,
              help='상세 로그 (반복 가능: -v, -vv, -vvv)')
@click.option('--quiet', '-q',
              is_flag=True,
              help='최소한의 출력만 표시')
@click.option('--output-dir', '-o',
              type=click.Path(path_type=Path),
              help='출력 디렉토리 (일괄 처리용)')
@click.option('--image-format',
              type=click.Choice(['png', 'jpeg', 'webp', 'original']),
              help='이미지 출력 형식')
@click.option('--encoding',
              type=click.Choice(['utf-8', 'utf-16', 'ascii']),
              help='출력 파일 인코딩')
@click.option('--dry-run',
              is_flag=True,
              help='실제 변환 없이 처리 과정만 확인')
def convert(input_file: Path,
           output_file: Optional[Path],
           extract_images: bool,
           batch: bool,
           config: Optional[Path],
           preset: Optional[str],
           verbose: int,
           quiet: bool,
           output_dir: Optional[Path],
           image_format: Optional[str],
           encoding: Optional[str],
           dry_run: bool):
    """PDF 파일을 Markdown으로 변환합니다"""
    
    try:
        # 설정 로드
        config_manager = ConfigManager()
        
        if preset:
            app_config = config_manager.get_preset_config(preset)
            click.echo(f"프리셋 사용: {preset}")
        else:
            app_config = config_manager.load_config(config)
        
        # CLI 옵션 병합
        cli_options = {
            'extract_images': extract_images,
            'verbose': verbose,
            'quiet': quiet,
            'image_format': image_format,
            'encoding': encoding,
        }
        
        # None이 아닌 값만 필터링
        cli_options = {k: v for k, v in cli_options.items() if v is not None}
        
        if cli_options:
            app_config = config_manager.merge_cli_options(app_config, cli_options)
        
        # 로깅 설정
        setup_logging(app_config)
        logger = logging.getLogger(__name__)
        
        logger.info("PDF to Markdown 변환 시작")
        logger.info(f"입력 파일: {input_file}")
        
        # 일괄 처리 모드 확인
        if batch and input_file.is_dir():
            pdf_files = list(input_file.glob("*.pdf"))
            if not pdf_files:
                click.echo(f"❌ 디렉토리에 PDF 파일이 없습니다: {input_file}", err=True)
                sys.exit(1)
            
            click.echo(f"📁 일괄 처리: {len(pdf_files)}개 파일 발견")
            _convert_batch(pdf_files, output_dir or input_file, app_config, dry_run)
        else:
            # 단일 파일 처리
            if not output_file:
                output_file = input_file.with_suffix('.md')
            
            _convert_single_file(input_file, output_file, app_config, dry_run)
        
        click.echo("✅ 변환 완료!")
        
    except (PDFProcessingError, ConfigurationError) as e:
        click.echo(f"❌ 오류: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n🛑 사용자에 의해 중단됨", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ 예상치 못한 오류: {e}", err=True)
        logger.exception("예상치 못한 오류 발생")
        sys.exit(1)


def _convert_single_file(input_file: Path, 
                        output_file: Path, 
                        config: AppConfig,
                        dry_run: bool) -> None:
    """단일 파일 변환"""
    logger = logging.getLogger(__name__)
    
    if dry_run:
        click.echo(f"🔍 [DRY RUN] {input_file} → {output_file}")
        click.echo(f"   - 이미지 추출: {config.conversion.extract_images}")
        click.echo(f"   - 출력 인코딩: {config.output.encoding}")
        click.echo(f"   - 이미지 형식: {config.output.image_format}")
        return
    
    # 진행률 표시
    with click.progressbar(length=100, label='PDF 변환 중') as bar:
        # 1. PDF 읽기
        bar.update(10)
        click.echo("📖 PDF 파일 읽는 중...")
        
        pdf_reader = PDFReader(input_file, extract_images=config.conversion.extract_images)
        document = pdf_reader.extract_document()
        
        logger.info(f"PDF 읽기 완료: {document.metadata.page_count}페이지")
        
        # 2. 텍스트 분석
        bar.update(30)
        click.echo("🔍 문서 구조 분석 중...")
        
        text_parser = TextParser(
            title_font_threshold=config.conversion.title_font_threshold,
            merge_paragraphs=config.conversion.merge_paragraphs,
            table_detection=config.conversion.table_detection
        )
        structure = text_parser.analyze_document_structure(document)
        
        logger.info(f"구조 분석 완료: {structure.total_elements}개 요소")
        
        # 3. Markdown 생성
        bar.update(50)
        click.echo("📝 Markdown 생성 중...")
        
        generator = MarkdownGenerator(config.markdown)
        markdown_text = generator.generate_markdown(structure, document, output_file.parent)
        
        # 4. 파일 저장
        bar.update(90)
        click.echo("💾 파일 저장 중...")
        
        # 출력 디렉토리 생성
        if config.output.create_output_dir:
            output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 기존 파일 백업
        if output_file.exists() and config.output.backup_existing:
            backup_path = output_file.with_suffix(f'.{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak')
            output_file.rename(backup_path)
            click.echo(f"📋 기존 파일 백업: {backup_path}")
        
        # 모든 페이지의 이미지 수집
        all_images = []
        if config.conversion.extract_images:
            for page in document.pages:
                all_images.extend(page.images)
        
        generator.save_markdown(markdown_text, output_file, all_images if all_images else None)
        
        bar.update(100)
    
    # 결과 요약
    click.echo(f"📄 출력 파일: {output_file}")
    click.echo(f"📊 통계:")
    click.echo(f"   - 페이지 수: {document.metadata.page_count}")
    click.echo(f"   - 요소 수: {structure.total_elements}")
    click.echo(f"   - 제목: {structure.heading_count}")
    click.echo(f"   - 단락: {structure.paragraph_count}")
    click.echo(f"   - 리스트: {structure.list_count}")
    click.echo(f"   - 테이블: {structure.table_count}")
    
    if config.conversion.extract_images and document.images:
        click.echo(f"   - 이미지: {len(document.images)}")


def _convert_batch(pdf_files: List[Path],
                  output_dir: Path,
                  config: AppConfig,
                  dry_run: bool) -> None:
    """일괄 파일 변환"""
    logger = logging.getLogger(__name__)
    
    if dry_run:
        click.echo(f"🔍 [DRY RUN] 일괄 처리: {len(pdf_files)}개 파일")
        for pdf_file in pdf_files:
            output_file = output_dir / f"{pdf_file.stem}.md"
            click.echo(f"   {pdf_file} → {output_file}")
        return
    
    # 출력 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    error_count = 0
    
    with click.progressbar(pdf_files, label='일괄 변환 중') as bar:
        for pdf_file in bar:
            try:
                output_file = output_dir / f"{pdf_file.stem}.md"
                _convert_single_file(pdf_file, output_file, config, False)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                logger.error(f"파일 변환 실패 {pdf_file}: {e}")
                click.echo(f"❌ {pdf_file.name}: {e}", err=True)
    
    # 결과 요약
    click.echo(f"\n📊 일괄 처리 완료:")
    click.echo(f"   - 성공: {success_count}개")
    click.echo(f"   - 실패: {error_count}개")
    click.echo(f"   - 출력 디렉토리: {output_dir}")


@cli.command()
@click.argument('output_path', type=click.Path(path_type=Path))
def create_config(output_path: Path):
    """샘플 설정 파일을 생성합니다"""
    try:
        config_manager = ConfigManager()
        config_manager.create_sample_config(output_path)
        click.echo(f"✅ 샘플 설정 파일 생성: {output_path}")
        click.echo("📝 파일을 편집하여 변환 옵션을 설정하세요")
        
    except Exception as e:
        click.echo(f"❌ 설정 파일 생성 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--all', '-a', is_flag=True, help='모든 프리셋 표시')
def list_presets(all: bool):
    """사용 가능한 설정 프리셋을 표시합니다"""
    presets = {
        'github': 'GitHub Flavored Markdown 스타일',
        'minimal': '최소 설정 (빠른 변환)',
        'documentation': '문서화용 (상세한 형식)',
        'publishing': '출판용 (고품질 변환)'
    }
    
    click.echo("📋 사용 가능한 프리셋:")
    for name, description in presets.items():
        click.echo(f"  {name:12} - {description}")
    
    if all:
        click.echo("\n💡 사용법:")
        click.echo("  pdf2md convert input.pdf --preset github")
        click.echo("  pdf2md convert input.pdf --preset minimal -v")


@cli.command()
def version():
    """버전 정보를 표시합니다"""
    from . import __version__, __author__
    click.echo(f"PDF to Markdown 변환기 v{__version__}")
    click.echo(f"작성자: {__author__}")


if __name__ == '__main__':
    cli() 