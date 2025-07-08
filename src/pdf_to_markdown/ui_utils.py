"""
UI 유틸리티 모듈

사용자 인터페이스 관련 기능들을 제공합니다.
- 진행률 표시 (Progress Bar)
- 상태 메시지 리포팅
- 변환 결과 요약
"""

import sys
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("Warning: tqdm이 설치되지 않았습니다. 기본 진행률 표시를 사용합니다.")


@dataclass
class ConversionStats:
    """변환 통계 정보"""
    start_time: datetime
    end_time: Optional[datetime] = None
    total_pages: int = 0
    processed_pages: int = 0
    total_elements: int = 0
    headings_found: int = 0
    paragraphs_found: int = 0
    lists_found: int = 0
    tables_found: int = 0
    images_found: int = 0
    images_extracted: int = 0
    output_file_size: int = 0
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    @property
    def processing_time(self) -> timedelta:
        """처리 시간 계산"""
        end = self.end_time or datetime.now()
        return end - self.start_time
    
    @property
    def pages_per_second(self) -> float:
        """초당 처리 페이지 수"""
        total_seconds = self.processing_time.total_seconds()
        if total_seconds > 0:
            return self.processed_pages / total_seconds
        return 0.0
    
    @property
    def success_rate(self) -> float:
        """성공률 (%)"""
        if self.total_pages > 0:
            return (self.processed_pages / self.total_pages) * 100
        return 0.0


class ProgressReporter:
    """진행률 리포터"""
    
    def __init__(self, total_pages: int, quiet: bool = False, use_tqdm: bool = True):
        """
        진행률 리포터 초기화
        
        Args:
            total_pages: 전체 페이지 수
            quiet: 조용한 모드 (최소한의 출력)
            use_tqdm: tqdm 사용 여부
        """
        self.total_pages = total_pages
        self.quiet = quiet
        self.use_tqdm = use_tqdm and HAS_TQDM and not quiet
        
        self.current_page = 0
        self.start_time = datetime.now()
        
        # tqdm 진행률 바
        self._progress_bar = None
        if self.use_tqdm:
            self._progress_bar = tqdm(
                total=total_pages,
                desc="PDF 변환 중",
                unit="페이지",
                ncols=80,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
            )
        
        self.logger = logging.getLogger(__name__)
    
    def update(self, current_page: int, status: str = ""):
        """
        진행률 업데이트
        
        Args:
            current_page: 현재 처리 중인 페이지 번호 (0부터 시작)
            status: 현재 상태 메시지
        """
        self.current_page = current_page
        
        if self.use_tqdm and self._progress_bar:
            # tqdm 업데이트
            self._progress_bar.n = current_page
            if status:
                self._progress_bar.set_description(f"PDF 변환 중: {status}")
            self._progress_bar.refresh()
        elif not self.quiet:
            # 기본 진행률 표시
            percent = (current_page / self.total_pages) * 100 if self.total_pages > 0 else 0
            elapsed = datetime.now() - self.start_time
            
            status_msg = f"진행률: {current_page}/{self.total_pages} ({percent:.1f}%) - {elapsed}"
            if status:
                status_msg += f" - {status}"
            
            print(f"\r{status_msg}", end="", flush=True)
    
    def update_status(self, message: str):
        """상태 메시지만 업데이트"""
        if self.use_tqdm and self._progress_bar:
            self._progress_bar.set_description(f"PDF 변환 중: {message}")
            self._progress_bar.refresh()
        elif not self.quiet:
            print(f"\r{message}", end="", flush=True)
    
    def increment(self, status: str = ""):
        """진행률 1 증가"""
        self.update(self.current_page + 1, status)
    
    def finish(self, stats: ConversionStats):
        """
        진행률 완료 처리
        
        Args:
            stats: 변환 통계 정보
        """
        if self.use_tqdm and self._progress_bar:
            self._progress_bar.close()
        elif not self.quiet:
            print()  # 줄바꿈
        
        # 완료 메시지 표시
        if not self.quiet:
            self._show_completion_summary(stats)
    
    def _show_completion_summary(self, stats: ConversionStats):
        """완료 요약 정보 표시"""
        print("\n" + "="*60)
        print("🎉 변환 완료!")
        print("="*60)
        
        # 기본 통계
        print(f"📊 처리 통계:")
        print(f"   ⏱️  처리 시간: {stats.processing_time}")
        print(f"   📄 처리 페이지: {stats.processed_pages}/{stats.total_pages}")
        print(f"   ⚡ 처리 속도: {stats.pages_per_second:.2f} 페이지/초")
        print(f"   ✅ 성공률: {stats.success_rate:.1f}%")
        
        # 문서 요소 통계
        if stats.total_elements > 0:
            print(f"\n📝 문서 요소:")
            print(f"   🏷️  제목: {stats.headings_found}개")
            print(f"   📄 단락: {stats.paragraphs_found}개")
            print(f"   📋 리스트: {stats.lists_found}개")
            print(f"   📊 테이블: {stats.tables_found}개")
            
            if stats.images_found > 0:
                print(f"   🖼️  이미지: {stats.images_found}개 (추출: {stats.images_extracted}개)")
        
        # 출력 파일 정보
        if stats.output_file_size > 0:
            size_mb = stats.output_file_size / (1024 * 1024)
            print(f"\n📁 출력 파일: {size_mb:.2f} MB")
        
        # 경고 및 오류
        if stats.warnings:
            print(f"\n⚠️  경고 {len(stats.warnings)}개:")
            for warning in stats.warnings[:5]:  # 최대 5개만 표시
                print(f"   • {warning}")
            if len(stats.warnings) > 5:
                print(f"   ... 및 {len(stats.warnings) - 5}개 더")
        
        if stats.errors:
            print(f"\n❌ 오류 {len(stats.errors)}개:")
            for error in stats.errors[:3]:  # 최대 3개만 표시
                print(f"   • {error}")
            if len(stats.errors) > 3:
                print(f"   ... 및 {len(stats.errors) - 3}개 더")
        
        print("="*60)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.use_tqdm and self._progress_bar:
            self._progress_bar.close()


class StatusReporter:
    """상태 리포터"""
    
    def __init__(self, quiet: bool = False, log_level: str = "INFO"):
        """
        상태 리포터 초기화
        
        Args:
            quiet: 조용한 모드
            log_level: 로그 레벨
        """
        self.quiet = quiet
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.now()
        
        # 메시지 카운터
        self.message_counts = {
            'info': 0,
            'warning': 0,
            'error': 0,
            'debug': 0
        }
    
    def info(self, message: str, show_time: bool = False):
        """정보 메시지"""
        self.message_counts['info'] += 1
        self._log_message("ℹ️", message, "info", show_time)
    
    def warning(self, message: str, show_time: bool = False):
        """경고 메시지"""
        self.message_counts['warning'] += 1
        self._log_message("⚠️", message, "warning", show_time)
    
    def error(self, message: str, show_time: bool = False):
        """오류 메시지"""
        self.message_counts['error'] += 1
        self._log_message("❌", message, "error", show_time)
    
    def success(self, message: str, show_time: bool = False):
        """성공 메시지"""
        self._log_message("✅", message, "info", show_time)
    
    def debug(self, message: str, show_time: bool = False):
        """디버그 메시지"""
        self.message_counts['debug'] += 1
        self._log_message("🔍", message, "debug", show_time)
    
    def _log_message(self, icon: str, message: str, level: str, show_time: bool):
        """메시지 로깅"""
        # 로거에 기록
        getattr(self.logger, level)(message)
        
        # 콘솔 출력 (조용한 모드가 아닌 경우)
        if not self.quiet:
            timestamp = ""
            if show_time:
                elapsed = datetime.now() - self.start_time
                timestamp = f"[{elapsed}] "
            
            print(f"{timestamp}{icon} {message}")
    
    def show_summary(self, stats: ConversionStats):
        """변환 완료 요약 표시"""
        if self.quiet:
            return
        
        print(f"\n📈 처리 요약:")
        print(f"   메시지: 정보 {self.message_counts['info']}개, "
              f"경고 {self.message_counts['warning']}개, "
              f"오류 {self.message_counts['error']}개")
        
        if stats.errors:
            print(f"   ❌ 치명적 오류: {len(stats.errors)}개")
        
        print(f"   ⏱️  총 처리 시간: {stats.processing_time}")


class BatchProgressReporter:
    """일괄 처리용 진행률 리포터"""
    
    def __init__(self, total_files: int, quiet: bool = False):
        """
        일괄 처리 진행률 리포터 초기화
        
        Args:
            total_files: 전체 파일 수
            quiet: 조용한 모드
        """
        self.total_files = total_files
        self.quiet = quiet
        self.current_file = 0
        self.successful_files = 0
        self.failed_files = 0
        
        self.start_time = datetime.now()
        
        # 파일별 진행률 바
        self._file_progress = None
        if HAS_TQDM and not quiet:
            self._file_progress = tqdm(
                total=total_files,
                desc="파일 처리 중",
                unit="파일",
                position=0,
                leave=True
            )
    
    def start_file(self, file_path: Path, file_index: int):
        """파일 처리 시작"""
        self.current_file = file_index + 1
        
        if self._file_progress:
            self._file_progress.set_description(f"처리 중: {file_path.name}")
        elif not self.quiet:
            print(f"\n[{self.current_file}/{self.total_files}] {file_path.name}")
    
    def finish_file(self, success: bool, error_message: str = ""):
        """파일 처리 완료"""
        if success:
            self.successful_files += 1
        else:
            self.failed_files += 1
        
        if self._file_progress:
            self._file_progress.update(1)
            if not success and error_message:
                self._file_progress.write(f"❌ 오류: {error_message}")
        elif not self.quiet:
            status = "✅ 완료" if success else f"❌ 실패: {error_message}"
            print(f"   {status}")
    
    def finish(self):
        """일괄 처리 완료"""
        if self._file_progress:
            self._file_progress.close()
        
        if not self.quiet:
            elapsed = datetime.now() - self.start_time
            print(f"\n🎯 일괄 처리 완료:")
            print(f"   ✅ 성공: {self.successful_files}개")
            print(f"   ❌ 실패: {self.failed_files}개")
            print(f"   ⏱️  소요 시간: {elapsed}")
            
            if self.total_files > 0:
                success_rate = (self.successful_files / self.total_files) * 100
                print(f"   📊 성공률: {success_rate:.1f}%")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file_progress:
            self._file_progress.close()


def format_file_size(size_bytes: int) -> str:
    """파일 크기를 읽기 쉬운 형식으로 변환"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"


def format_duration(duration: timedelta) -> str:
    """시간 간격을 읽기 쉬운 형식으로 변환"""
    total_seconds = int(duration.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}초"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}분 {seconds}초"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}시간 {minutes}분" 