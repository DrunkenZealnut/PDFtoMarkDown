"""
성능 모니터링 및 최적화 모듈

PDF to Markdown 변환 과정의 성능을 모니터링하고 최적화합니다.
"""

import time
import psutil
import gc
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import contextmanager
import logging


@dataclass
class PerformanceMetrics:
    """성능 지표 데이터 클래스"""
    
    processing_time: float = 0.0
    memory_usage_mb: float = 0.0
    peak_memory_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    pages_per_second: float = 0.0
    elements_per_second: float = 0.0


class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self):
        """성능 모니터 초기화"""
        self.logger = logging.getLogger(__name__)
        self._start_time: Optional[float] = None
        self._start_memory: Optional[float] = None
        self._peak_memory: float = 0.0
        self._metrics_history: List[PerformanceMetrics] = []
    
    @contextmanager
    def monitor_conversion(self, pages_count: int = 0, elements_count: int = 0):
        """
        변환 작업 성능 모니터링
        
        Args:
            pages_count: 처리할 페이지 수
            elements_count: 처리할 요소 수
            
        Yields:
            PerformanceMetrics: 성능 지표
        """
        # 시작 시점 측정
        start_time = time.time()
        start_memory = self._get_memory_usage()
        start_cpu = psutil.cpu_percent()
        
        self._peak_memory = start_memory
        
        try:
            yield
            
        finally:
            # 종료 시점 측정
            end_time = time.time()
            end_memory = self._get_memory_usage()
            end_cpu = psutil.cpu_percent()
            
            # 성능 지표 계산
            processing_time = end_time - start_time
            memory_usage = end_memory - start_memory
            cpu_usage = (start_cpu + end_cpu) / 2
            
            # 처리율 계산
            pages_per_second = pages_count / processing_time if processing_time > 0 else 0
            elements_per_second = elements_count / processing_time if processing_time > 0 else 0
            
            # 성능 지표 생성
            metrics = PerformanceMetrics(
                processing_time=processing_time,
                memory_usage_mb=memory_usage,
                peak_memory_mb=self._peak_memory,
                cpu_usage_percent=cpu_usage,
                pages_per_second=pages_per_second,
                elements_per_second=elements_per_second
            )
            
            self._metrics_history.append(metrics)
            self._log_performance(metrics, pages_count, elements_count)
    
    def _get_memory_usage(self) -> float:
        """현재 메모리 사용량 반환 (MB)"""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            # 최대 메모리 사용량 업데이트
            if memory_mb > self._peak_memory:
                self._peak_memory = memory_mb
                
            return memory_mb
        except Exception as e:
            self.logger.warning(f"메모리 사용량 측정 실패: {e}")
            return 0.0
    
    def _log_performance(self, metrics: PerformanceMetrics, pages: int, elements: int):
        """성능 지표 로깅"""
        self.logger.info(f"성능 지표:")
        self.logger.info(f"  처리 시간: {metrics.processing_time:.2f}초")
        self.logger.info(f"  메모리 사용: {metrics.memory_usage_mb:.1f}MB")
        self.logger.info(f"  최대 메모리: {metrics.peak_memory_mb:.1f}MB")
        self.logger.info(f"  CPU 사용률: {metrics.cpu_usage_percent:.1f}%")
        
        if pages > 0:
            self.logger.info(f"  페이지/초: {metrics.pages_per_second:.2f}")
        if elements > 0:
            self.logger.info(f"  요소/초: {metrics.elements_per_second:.2f}")
    
    def get_average_metrics(self) -> Optional[PerformanceMetrics]:
        """평균 성능 지표 반환"""
        if not self._metrics_history:
            return None
        
        count = len(self._metrics_history)
        
        return PerformanceMetrics(
            processing_time=sum(m.processing_time for m in self._metrics_history) / count,
            memory_usage_mb=sum(m.memory_usage_mb for m in self._metrics_history) / count,
            peak_memory_mb=max(m.peak_memory_mb for m in self._metrics_history),
            cpu_usage_percent=sum(m.cpu_usage_percent for m in self._metrics_history) / count,
            pages_per_second=sum(m.pages_per_second for m in self._metrics_history) / count,
            elements_per_second=sum(m.elements_per_second for m in self._metrics_history) / count
        )
    
    def clear_history(self):
        """성능 지표 히스토리 초기화"""
        self._metrics_history.clear()
        self._peak_memory = 0.0


class MemoryOptimizer:
    """메모리 최적화 도구"""
    
    def __init__(self):
        """메모리 최적화기 초기화"""
        self.logger = logging.getLogger(__name__)
    
    def optimize_memory_usage(self):
        """메모리 사용량 최적화"""
        try:
            # 가비지 컬렉션 강제 실행
            collected = gc.collect()
            
            if collected > 0:
                self.logger.debug(f"가비지 컬렉션으로 {collected}개 객체 정리")
            
            # 메모리 통계 로깅
            memory_info = psutil.Process().memory_info()
            self.logger.debug(f"현재 메모리 사용량: {memory_info.rss / 1024 / 1024:.1f}MB")
            
        except Exception as e:
            self.logger.warning(f"메모리 최적화 실패: {e}")
    
    @contextmanager
    def memory_limit_context(self, max_memory_mb: float = 500.0):
        """
        메모리 사용량 제한 컨텍스트
        
        Args:
            max_memory_mb: 최대 메모리 사용량 (MB)
        """
        try:
            yield
            
        finally:
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            if current_memory > max_memory_mb:
                self.logger.warning(
                    f"메모리 사용량 초과: {current_memory:.1f}MB > {max_memory_mb}MB"
                )
                self.optimize_memory_usage()


class ProcessingOptimizer:
    """처리 최적화 도구"""
    
    def __init__(self):
        """처리 최적화기 초기화"""
        self.logger = logging.getLogger(__name__)
    
    def optimize_text_processing(self, text: str) -> str:
        """
        텍스트 처리 최적화
        
        Args:
            text: 원본 텍스트
            
        Returns:
            str: 최적화된 텍스트
        """
        if not text:
            return text
        
        # 문자열 연산 최적화
        lines = text.split('\n')
        
        # 빈 줄 제거 (메모리 절약)
        non_empty_lines = [line for line in lines if line.strip()]
        
        # join 사용으로 메모리 효율성 향상
        return '\n'.join(non_empty_lines)
    
    def batch_process_elements(self, elements: List[Any], batch_size: int = 100) -> List[Any]:
        """
        요소를 배치로 처리하여 메모리 효율성 향상
        
        Args:
            elements: 처리할 요소 목록
            batch_size: 배치 크기
            
        Returns:
            List[Any]: 처리된 요소 목록
        """
        processed_elements = []
        
        for i in range(0, len(elements), batch_size):
            batch = elements[i:i + batch_size]
            
            # 배치 처리
            processed_batch = self._process_batch(batch)
            processed_elements.extend(processed_batch)
            
            # 메모리 정리
            if i % (batch_size * 10) == 0:  # 10배치마다
                gc.collect()
        
        return processed_elements
    
    def _process_batch(self, batch: List[Any]) -> List[Any]:
        """
        단일 배치 처리
        
        Args:
            batch: 처리할 배치
            
        Returns:
            List[Any]: 처리된 배치
        """
        # 실제 처리 로직 (하위 클래스에서 구현)
        return batch


class StreamingProcessor:
    """스트리밍 처리기"""
    
    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB 청크
        """
        스트리밍 처리기 초기화
        
        Args:
            chunk_size: 청크 크기 (바이트)
        """
        self.chunk_size = chunk_size
        self.logger = logging.getLogger(__name__)
    
    def process_large_file(self, file_path: str, processor_func: callable):
        """
        대용량 파일 스트리밍 처리
        
        Args:
            file_path: 파일 경로
            processor_func: 처리 함수
        """
        try:
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    # 청크 처리
                    processor_func(chunk)
                    
                    # 메모리 정리
                    gc.collect()
                    
        except Exception as e:
            self.logger.error(f"스트리밍 처리 실패: {e}")
            raise


class PerformanceBenchmark:
    """성능 벤치마크"""
    
    def __init__(self):
        """벤치마크 초기화"""
        self.logger = logging.getLogger(__name__)
        self.results: Dict[str, Any] = {}
    
    def benchmark_conversion_speed(self, converter, test_files: List[str]) -> Dict[str, float]:
        """
        변환 속도 벤치마크
        
        Args:
            converter: 변환기 인스턴스
            test_files: 테스트 파일 목록
            
        Returns:
            Dict[str, float]: 벤치마크 결과
        """
        results = {}
        
        for file_path in test_files:
            start_time = time.time()
            
            try:
                # 변환 실행 (실제 구현에서는 converter.convert_file 사용)
                # result = converter.convert_file(file_path)
                pass
                
            except Exception as e:
                self.logger.error(f"벤치마크 실패 ({file_path}): {e}")
                continue
            
            processing_time = time.time() - start_time
            results[file_path] = processing_time
        
        return results
    
    def generate_performance_report(self, metrics: PerformanceMetrics) -> str:
        """
        성능 보고서 생성
        
        Args:
            metrics: 성능 지표
            
        Returns:
            str: 성능 보고서
        """
        report_lines = [
            "=== 성능 보고서 ===",
            f"처리 시간: {metrics.processing_time:.2f}초",
            f"메모리 사용량: {metrics.memory_usage_mb:.1f}MB",
            f"최대 메모리: {metrics.peak_memory_mb:.1f}MB",
            f"CPU 사용률: {metrics.cpu_usage_percent:.1f}%",
            f"페이지 처리율: {metrics.pages_per_second:.2f} 페이지/초",
            f"요소 처리율: {metrics.elements_per_second:.2f} 요소/초",
            "",
            "=== 성능 기준 ===",
            "✓ 페이지당 처리 시간 < 2초" if metrics.processing_time < 2 else "✗ 페이지당 처리 시간 >= 2초",
            "✓ 메모리 사용량 < 500MB" if metrics.peak_memory_mb < 500 else "✗ 메모리 사용량 >= 500MB",
            "✓ CPU 사용률 < 80%" if metrics.cpu_usage_percent < 80 else "✗ CPU 사용률 >= 80%",
        ]
        
        return "\n".join(report_lines)


# 성능 최적화를 위한 데코레이터
def performance_monitor(func):
    """성능 모니터링 데코레이터"""
    def wrapper(*args, **kwargs):
        monitor = PerformanceMonitor()
        
        with monitor.monitor_conversion():
            result = func(*args, **kwargs)
        
        # 평균 성능 지표 로깅
        avg_metrics = monitor.get_average_metrics()
        if avg_metrics:
            logging.getLogger(func.__module__).info(
                f"{func.__name__} 성능: {avg_metrics.processing_time:.2f}초, "
                f"{avg_metrics.memory_usage_mb:.1f}MB"
            )
        
        return result
    
    return wrapper


def memory_optimized(max_memory_mb: float = 500.0):
    """메모리 최적화 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            optimizer = MemoryOptimizer()
            
            with optimizer.memory_limit_context(max_memory_mb):
                result = func(*args, **kwargs)
            
            return result
        
        return wrapper
    
    return decorator 