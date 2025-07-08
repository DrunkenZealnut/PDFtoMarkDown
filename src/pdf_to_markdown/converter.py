"""
PDF to Markdown 변환기 통합 모듈

전체 변환 프로세스를 관리하고 조율하는 메인 컨버터 클래스입니다.
"""

import logging
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field

from .config import AppConfig
from .pdf_reader import PDFReader
from .text_parser import TextParser
from .markdown_generator import MarkdownGenerator
from .ui_utils import ProgressReporter, StatusReporter, ConversionStats, BatchProgressReporter
from .data_models import DocumentContent, DocumentMetadata
from .text_structures import DocumentStructure
from .exceptions import PDFProcessingError, ConfigurationError


@dataclass
class ConversionResult:
    """변환 결과 정보"""
    success: bool
    input_file: Path
    output_file: Optional[Path] = None
    processing_time: float = 0.0
    stats: Optional[ConversionStats] = None
    error_message: str = ""
    warning_messages: List[str] = field(default_factory=list)
    
    @property
    def is_success(self) -> bool:
        """변환 성공 여부"""
        return self.success and self.output_file is not None
    
    @property
    def file_size_mb(self) -> float:
        """출력 파일 크기 (MB)"""
        if self.output_file and self.output_file.exists():
            return self.output_file.stat().st_size / (1024 * 1024)
        return 0.0


class PDFToMarkdownConverter:
    """PDF to Markdown 통합 변환기"""
    
    def __init__(self, config: AppConfig):
        """
        변환기 초기화
        
        Args:
            config: 애플리케이션 설정
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 구성 요소 초기화
        self.text_parser = TextParser(
            title_font_threshold=config.conversion.title_font_threshold,
            merge_paragraphs=config.conversion.merge_paragraphs,
            table_detection=config.conversion.table_detection
        )
        self.markdown_generator = MarkdownGenerator(config.markdown)
        
        # 통계 정보
        self.conversion_count = 0
        self.success_count = 0
        self.total_processing_time = 0.0
    
    def convert_file(self, 
                    pdf_path: Path, 
                    output_path: Optional[Path] = None,
                    quiet: bool = False) -> ConversionResult:
        """
        단일 PDF 파일을 Markdown으로 변환합니다
        
        Args:
            pdf_path: 입력 PDF 파일 경로
            output_path: 출력 Markdown 파일 경로 (None이면 자동 생성)
            quiet: 조용한 모드 (진행률 표시 안함)
            
        Returns:
            ConversionResult: 변환 결과
        """
        start_time = time.time()
        
        # 출력 경로 설정
        if output_path is None:
            output_path = pdf_path.with_suffix('.md')
        
        # 변환 통계 초기화
        stats = ConversionStats(start_time=datetime.now())
        
        self.logger.info(f"파일 변환 시작: {pdf_path} → {output_path}")
        
        try:
            # 1. PDF 읽기
            self.logger.debug("PDF 파일 읽기 시작")
            pdf_reader = PDFReader(
                pdf_path, 
                extract_images=self.config.conversion.extract_images
            )
            
            document = pdf_reader.extract_document()
            stats.total_pages = document.metadata.page_count
            
            # 빈 페이지 건너뛰기 확인
            if (self.config.conversion.skip_empty_pages and 
                not self._has_meaningful_content(document)):
                self.logger.warning(f"빈 문서로 판단되어 건너뜀: {pdf_path}")
                return ConversionResult(
                    success=False,
                    input_file=pdf_path,
                    error_message="빈 문서 (건너뜀)",
                    processing_time=time.time() - start_time
                )
            
            self.logger.info(f"PDF 읽기 완료: {document.metadata.page_count}페이지")
            
            # 2. 진행률 리포터 설정
            progress_reporter = None
            if not quiet:
                progress_reporter = ProgressReporter(
                    total_pages=document.metadata.page_count,
                    quiet=quiet
                )
                progress_reporter.update(1, "문서 구조 분석 중...")
            
            # 3. 텍스트 구조 분석
            self.logger.debug("문서 구조 분석 시작")
            structure = self.text_parser.analyze_document_structure(document)
            
            if progress_reporter:
                progress_reporter.update(30, "Markdown 생성 중...")
            
            # 4. 신뢰도 확인
            if structure.confidence_score < self.config.conversion.min_confidence:
                self.logger.warning(
                    f"낮은 신뢰도 ({structure.confidence_score:.2f}): {pdf_path}"
                )
                stats.warnings.append(f"낮은 분석 신뢰도: {structure.confidence_score:.2f}")
            
            # 5. Markdown 생성
            self.logger.debug("Markdown 생성 시작")
            markdown_text = self.markdown_generator.generate_markdown(
                structure, document, output_path.parent
            )
            
            if progress_reporter:
                progress_reporter.update(80, "파일 저장 중...")
            
            # 6. 파일 저장
            self._save_output_file(
                markdown_text, output_path, document, structure, stats
            )
            
            if progress_reporter:
                progress_reporter.update(100, "완료")
            
            # 7. 결과 통계 업데이트
            stats.end_time = datetime.now()
            stats.processed_pages = document.metadata.page_count
            stats.total_elements = structure.total_elements
            stats.headings_found = structure.heading_count
            stats.paragraphs_found = structure.paragraph_count
            stats.lists_found = structure.list_count
            stats.tables_found = structure.table_count
            
            # 이미지 통계
            if self.config.conversion.extract_images:
                all_images = []
                for page in document.pages:
                    all_images.extend(page.images)
                stats.images_found = len(all_images)
                stats.images_extracted = len(all_images)  # 실제로는 저장된 이미지 수
            
            # 출력 파일 크기
            if output_path.exists():
                stats.output_file_size = output_path.stat().st_size
            
            # 경고 메시지 수집
            stats.warnings.extend(structure.analysis_warnings)
            
            # 진행률 완료
            if progress_reporter:
                progress_reporter.finish(stats)
            
            # 성공 결과 반환
            processing_time = time.time() - start_time
            self.conversion_count += 1
            self.success_count += 1
            self.total_processing_time += processing_time
            
            self.logger.info(f"변환 완료: {pdf_path} ({processing_time:.2f}초)")
            
            return ConversionResult(
                success=True,
                input_file=pdf_path,
                output_file=output_path,
                processing_time=processing_time,
                stats=stats,
                warning_messages=stats.warnings
            )
            
        except PDFProcessingError as e:
            # PDF 처리 관련 오류
            error_msg = str(e)
            self.logger.error(f"PDF 처리 오류: {error_msg}")
            
            processing_time = time.time() - start_time
            self.conversion_count += 1
            
            return ConversionResult(
                success=False,
                input_file=pdf_path,
                processing_time=processing_time,
                error_message=error_msg
            )
            
        except Exception as e:
            # 예상치 못한 오류
            error_msg = f"예상치 못한 오류: {str(e)}"
            self.logger.exception(f"변환 중 예외 발생: {pdf_path}")
            
            processing_time = time.time() - start_time
            self.conversion_count += 1
            
            return ConversionResult(
                success=False,
                input_file=pdf_path,
                processing_time=processing_time,
                error_message=error_msg
            )
    
    def convert_batch(self, 
                     pdf_files: List[Path], 
                     output_dir: Path,
                     quiet: bool = False) -> List[ConversionResult]:
        """
        여러 PDF 파일을 일괄 변환합니다
        
        Args:
            pdf_files: 변환할 PDF 파일 목록
            output_dir: 출력 디렉토리
            quiet: 조용한 모드
            
        Returns:
            List[ConversionResult]: 변환 결과 목록
        """
        self.logger.info(f"일괄 변환 시작: {len(pdf_files)}개 파일")
        
        # 출력 디렉토리 생성
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        # 일괄 처리 진행률 리포터
        batch_reporter = None
        if not quiet:
            batch_reporter = BatchProgressReporter(
                total_files=len(pdf_files),
                quiet=quiet
            )
        
        try:
            for i, pdf_file in enumerate(pdf_files):
                if batch_reporter:
                    batch_reporter.start_file(pdf_file, i)
                
                # 출력 파일 경로 생성
                output_file = output_dir / f"{pdf_file.stem}.md"
                
                # 단일 파일 변환
                result = self.convert_file(pdf_file, output_file, quiet=True)
                results.append(result)
                
                # 진행률 업데이트
                if batch_reporter:
                    batch_reporter.finish_file(
                        success=result.success,
                        error_message=result.error_message
                    )
                
                # 개별 결과 로깅
                if result.success:
                    self.logger.info(f"변환 성공: {pdf_file.name}")
                else:
                    self.logger.error(f"변환 실패: {pdf_file.name} - {result.error_message}")
            
            # 일괄 처리 완료
            if batch_reporter:
                batch_reporter.finish()
            
            # 전체 통계
            successful = sum(1 for r in results if r.success)
            self.logger.info(f"일괄 변환 완료: {successful}/{len(pdf_files)} 성공")
            
            return results
            
        except KeyboardInterrupt:
            self.logger.warning("사용자에 의해 일괄 변환 중단됨")
            if batch_reporter:
                batch_reporter.finish()
            return results
        
        except Exception as e:
            self.logger.exception("일괄 변환 중 예상치 못한 오류 발생")
            if batch_reporter:
                batch_reporter.finish()
            raise
    
    def _has_meaningful_content(self, document: DocumentContent) -> bool:
        """문서에 의미있는 콘텐츠가 있는지 확인"""
        total_text_length = 0
        
        for page in document.pages:
            for text_block in page.text_blocks:
                # 공백을 제거한 실제 텍스트 길이
                clean_text = text_block.text.strip()
                if clean_text:
                    total_text_length += len(clean_text)
        
        # 최소 100자 이상의 텍스트가 있어야 의미있는 문서로 판단
        return total_text_length >= 100
    
    def _save_output_file(self, 
                         markdown_text: str,
                         output_path: Path,
                         document: DocumentContent,
                         structure: DocumentStructure,
                         stats: ConversionStats) -> None:
        """출력 파일 저장"""
        try:
            # 디렉토리 생성
            if self.config.output.create_output_dir:
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 기존 파일 백업
            if (output_path.exists() and 
                self.config.output.backup_existing):
                backup_path = output_path.with_suffix('.bak')
                output_path.rename(backup_path)
                self.logger.info(f"기존 파일 백업: {backup_path}")
            
            # 이미지 수집
            all_images = []
            if self.config.conversion.extract_images:
                for page in document.pages:
                    all_images.extend(page.images)
            
            # Markdown 파일 저장
            self.markdown_generator.save_markdown(
                markdown_text, 
                output_path, 
                all_images if all_images else None
            )
            
            self.logger.debug(f"파일 저장 완료: {output_path}")
            
        except Exception as e:
            error_msg = f"파일 저장 실패: {str(e)}"
            self.logger.error(error_msg)
            stats.errors.append(error_msg)
            raise PDFProcessingError(error_msg, str(output_path))
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """변환 통계 반환"""
        return {
            'total_conversions': self.conversion_count,
            'successful_conversions': self.success_count,
            'failed_conversions': self.conversion_count - self.success_count,
            'success_rate': (self.success_count / self.conversion_count * 100) if self.conversion_count > 0 else 0,
            'total_processing_time': self.total_processing_time,
            'average_processing_time': (self.total_processing_time / self.conversion_count) if self.conversion_count > 0 else 0,
        }
    
    def reset_stats(self):
        """통계 초기화"""
        self.conversion_count = 0
        self.success_count = 0
        self.total_processing_time = 0.0


class ConversionManager:
    """변환 관리자 - 고수준 변환 인터페이스"""
    
    @staticmethod
    def convert_single_file(pdf_path: Path,
                          output_path: Optional[Path] = None,
                          config: Optional[AppConfig] = None,
                          quiet: bool = False) -> ConversionResult:
        """
        단일 파일 변환 편의 메서드
        
        Args:
            pdf_path: PDF 파일 경로
            output_path: 출력 파일 경로
            config: 설정 (None이면 기본 설정)
            quiet: 조용한 모드
            
        Returns:
            ConversionResult: 변환 결과
        """
        from .config import ConfigManager
        
        if config is None:
            config_manager = ConfigManager()
            config = config_manager.get_default_config()
        
        converter = PDFToMarkdownConverter(config)
        return converter.convert_file(pdf_path, output_path, quiet)
    
    @staticmethod
    def convert_directory(input_dir: Path,
                         output_dir: Optional[Path] = None,
                         config: Optional[AppConfig] = None,
                         pattern: str = "*.pdf",
                         quiet: bool = False) -> List[ConversionResult]:
        """
        디렉토리 내 모든 PDF 파일 변환
        
        Args:
            input_dir: 입력 디렉토리
            output_dir: 출력 디렉토리 (None이면 입력 디렉토리와 동일)
            config: 설정
            pattern: 파일 패턴
            quiet: 조용한 모드
            
        Returns:
            List[ConversionResult]: 변환 결과 목록
        """
        from .config import ConfigManager
        
        if config is None:
            config_manager = ConfigManager()
            config = config_manager.get_default_config()
        
        if output_dir is None:
            output_dir = input_dir
        
        # PDF 파일 검색
        pdf_files = list(input_dir.glob(pattern))
        if not pdf_files:
            raise ValueError(f"디렉토리에 PDF 파일이 없습니다: {input_dir}")
        
        converter = PDFToMarkdownConverter(config)
        return converter.convert_batch(pdf_files, output_dir, quiet) 