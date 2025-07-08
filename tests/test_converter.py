"""
변환기 모듈 테스트

converter.py의 기능을 테스트합니다.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 테스트 대상 모듈 import
from src.pdf_to_markdown.converter import PDFToMarkdownConverter
from src.pdf_to_markdown.config import AppConfig, ConversionConfig, OutputConfig, LoggingConfig
from src.pdf_to_markdown.markdown_config import MarkdownConfig
from src.pdf_to_markdown.data_models import ConversionResult, ConversionStats
from src.pdf_to_markdown.exceptions import PDFProcessingError, FileAccessError


class TestPDFToMarkdownConverter:
    """PDFToMarkdownConverter 클래스 테스트"""

    def test_initialization(self):
        """변환기 초기화 테스트"""
        config = AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=MarkdownConfig()
        )
        
        converter = PDFToMarkdownConverter(config)
        
        assert converter.config == config
        assert isinstance(converter.stats, ConversionStats)
        assert converter.stats.total_conversions == 0

    def test_get_stats(self):
        """통계 조회 테스트"""
        config = AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=MarkdownConfig()
        )
        
        converter = PDFToMarkdownConverter(config)
        stats = converter.get_stats()
        
        assert isinstance(stats, dict)
        assert 'total_conversions' in stats
        assert 'successful_conversions' in stats
        assert 'failed_conversions' in stats
        assert 'success_rate' in stats

    @patch('src.pdf_to_markdown.converter.PDFReader')
    @patch('src.pdf_to_markdown.converter.TextParser')
    @patch('src.pdf_to_markdown.converter.MarkdownGenerator')
    def test_convert_file_success(self, mock_generator, mock_parser, mock_reader):
        """파일 변환 성공 테스트"""
        # Mock 객체 설정
        mock_reader_instance = Mock()
        mock_reader.return_value = mock_reader_instance
        
        mock_document = Mock()
        mock_document.metadata.page_count = 2
        mock_reader_instance.extract_document.return_value = mock_document
        
        mock_parser_instance = Mock()
        mock_parser.return_value = mock_parser_instance
        
        mock_structure = Mock()
        mock_structure.total_elements = 10
        mock_parser_instance.analyze_document_structure.return_value = mock_structure
        
        mock_generator_instance = Mock()
        mock_generator.return_value = mock_generator_instance
        mock_generator_instance.generate_markdown.return_value = "# Test\n\nContent"
        
        # 테스트 실행
        config = AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=MarkdownConfig()
        )
        
        converter = PDFToMarkdownConverter(config)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "test.pdf"
            output_path = Path(temp_dir) / "test.md"
            
            # 가짜 PDF 파일 생성
            input_path.write_bytes(b"fake pdf content")
            
            result = converter.convert_file(input_path, output_path)
            
            # 결과 검증
            assert isinstance(result, ConversionResult)
            assert result.success is True
            assert result.input_file == input_path
            assert result.output_file == output_path
            assert result.pages_processed == 2
            assert result.elements_found == 10

    def test_convert_file_nonexistent_input(self):
        """존재하지 않는 입력 파일 테스트"""
        config = AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=MarkdownConfig()
        )
        
        converter = PDFToMarkdownConverter(config)
        
        nonexistent_path = Path("nonexistent.pdf")
        output_path = Path("output.md")
        
        result = converter.convert_file(nonexistent_path, output_path)
        
        assert isinstance(result, ConversionResult)
        assert result.success is False
        assert "존재하지 않습니다" in result.error_message

    @patch('src.pdf_to_markdown.converter.PDFReader')
    def test_convert_file_pdf_processing_error(self, mock_reader):
        """PDF 처리 오류 테스트"""
        # PDF 읽기에서 예외 발생 설정
        mock_reader.side_effect = PDFProcessingError("PDF 파일 손상")
        
        config = AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=MarkdownConfig()
        )
        
        converter = PDFToMarkdownConverter(config)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "test.pdf"
            output_path = Path(temp_dir) / "test.md"
            
            # 가짜 PDF 파일 생성
            input_path.write_bytes(b"fake pdf content")
            
            result = converter.convert_file(input_path, output_path)
            
            assert isinstance(result, ConversionResult)
            assert result.success is False
            assert "PDF 파일 손상" in result.error_message

    def test_convert_batch_empty_list(self):
        """빈 파일 목록 일괄 변환 테스트"""
        config = AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=MarkdownConfig()
        )
        
        converter = PDFToMarkdownConverter(config)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            results = converter.convert_batch([], output_dir)
            
            assert isinstance(results, list)
            assert len(results) == 0

    @patch('src.pdf_to_markdown.converter.PDFReader')
    @patch('src.pdf_to_markdown.converter.TextParser')
    @patch('src.pdf_to_markdown.converter.MarkdownGenerator')
    def test_convert_batch_success(self, mock_generator, mock_parser, mock_reader):
        """일괄 변환 성공 테스트"""
        # Mock 객체 설정
        mock_reader_instance = Mock()
        mock_reader.return_value = mock_reader_instance
        
        mock_document = Mock()
        mock_document.metadata.page_count = 1
        mock_reader_instance.extract_document.return_value = mock_document
        
        mock_parser_instance = Mock()
        mock_parser.return_value = mock_parser_instance
        
        mock_structure = Mock()
        mock_structure.total_elements = 5
        mock_parser_instance.analyze_document_structure.return_value = mock_structure
        
        mock_generator_instance = Mock()
        mock_generator.return_value = mock_generator_instance
        mock_generator_instance.generate_markdown.return_value = "# Test\n\nContent"
        
        # 테스트 실행
        config = AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=MarkdownConfig()
        )
        
        converter = PDFToMarkdownConverter(config)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 가짜 PDF 파일들 생성
            pdf_files = []
            for i in range(3):
                pdf_path = Path(temp_dir) / f"test{i}.pdf"
                pdf_path.write_bytes(b"fake pdf content")
                pdf_files.append(pdf_path)
            
            output_dir = Path(temp_dir) / "output"
            results = converter.convert_batch(pdf_files, output_dir)
            
            # 결과 검증
            assert isinstance(results, list)
            assert len(results) == 3
            
            for result in results:
                assert isinstance(result, ConversionResult)
                assert result.success is True

    def test_update_stats_success(self):
        """성공적인 변환 통계 업데이트 테스트"""
        config = AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=MarkdownConfig()
        )
        
        converter = PDFToMarkdownConverter(config)
        
        # 성공적인 결과 생성
        result = ConversionResult(
            success=True,
            input_file=Path("test.pdf"),
            output_file=Path("test.md"),
            pages_processed=5,
            elements_found=20,
            processing_time=2.5
        )
        
        initial_stats = converter.get_stats()
        converter._update_stats(result)
        updated_stats = converter.get_stats()
        
        assert updated_stats['total_conversions'] == initial_stats['total_conversions'] + 1
        assert updated_stats['successful_conversions'] == initial_stats['successful_conversions'] + 1
        assert updated_stats['total_processing_time'] > initial_stats['total_processing_time']

    def test_update_stats_failure(self):
        """실패한 변환 통계 업데이트 테스트"""
        config = AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=MarkdownConfig()
        )
        
        converter = PDFToMarkdownConverter(config)
        
        # 실패한 결과 생성
        result = ConversionResult(
            success=False,
            input_file=Path("test.pdf"),
            error_message="처리 실패",
            processing_time=1.0
        )
        
        initial_stats = converter.get_stats()
        converter._update_stats(result)
        updated_stats = converter.get_stats()
        
        assert updated_stats['total_conversions'] == initial_stats['total_conversions'] + 1
        assert updated_stats['failed_conversions'] == initial_stats['failed_conversions'] + 1

    def test_success_rate_calculation(self):
        """성공률 계산 테스트"""
        config = AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=MarkdownConfig()
        )
        
        converter = PDFToMarkdownConverter(config)
        
        # 성공 및 실패 결과 추가
        success_result = ConversionResult(
            success=True,
            input_file=Path("success.pdf"),
            output_file=Path("success.md"),
            processing_time=1.0
        )
        
        failure_result = ConversionResult(
            success=False,
            input_file=Path("failure.pdf"),
            error_message="실패",
            processing_time=0.5
        )
        
        converter._update_stats(success_result)
        converter._update_stats(success_result)  # 2번 성공
        converter._update_stats(failure_result)  # 1번 실패
        
        stats = converter.get_stats()
        assert stats['success_rate'] == 2 / 3 * 100  # 66.67%

    def test_average_processing_time_calculation(self):
        """평균 처리 시간 계산 테스트"""
        config = AppConfig(
            conversion=ConversionConfig(),
            output=OutputConfig(),
            logging=LoggingConfig(),
            markdown=MarkdownConfig()
        )
        
        converter = PDFToMarkdownConverter(config)
        
        # 여러 결과 추가
        times = [1.0, 2.0, 3.0]
        for time in times:
            result = ConversionResult(
                success=True,
                input_file=Path(f"test{time}.pdf"),
                output_file=Path(f"test{time}.md"),
                processing_time=time
            )
            converter._update_stats(result)
        
        stats = converter.get_stats()
        expected_avg = sum(times) / len(times)
        assert stats['average_processing_time'] == expected_avg


class TestConversionStats:
    """ConversionStats 클래스 테스트"""

    def test_initialization(self):
        """통계 초기화 테스트"""
        stats = ConversionStats()
        
        assert stats.total_conversions == 0
        assert stats.successful_conversions == 0
        assert stats.failed_conversions == 0
        assert stats.total_processing_time == 0.0

    def test_add_success(self):
        """성공 추가 테스트"""
        stats = ConversionStats()
        stats.add_success(2.5)
        
        assert stats.total_conversions == 1
        assert stats.successful_conversions == 1
        assert stats.failed_conversions == 0
        assert stats.total_processing_time == 2.5

    def test_add_failure(self):
        """실패 추가 테스트"""
        stats = ConversionStats()
        stats.add_failure(1.0)
        
        assert stats.total_conversions == 1
        assert stats.successful_conversions == 0
        assert stats.failed_conversions == 1
        assert stats.total_processing_time == 1.0

    def test_success_rate_no_conversions(self):
        """변환이 없을 때 성공률 테스트"""
        stats = ConversionStats()
        assert stats.success_rate == 0

    def test_success_rate_with_conversions(self):
        """변환이 있을 때 성공률 테스트"""
        stats = ConversionStats()
        stats.add_success(1.0)
        stats.add_success(1.0)
        stats.add_failure(1.0)
        
        assert stats.success_rate == 2 / 3 * 100

    def test_average_processing_time_no_conversions(self):
        """변환이 없을 때 평균 처리 시간 테스트"""
        stats = ConversionStats()
        assert stats.average_processing_time == 0

    def test_average_processing_time_with_conversions(self):
        """변환이 있을 때 평균 처리 시간 테스트"""
        stats = ConversionStats()
        stats.add_success(2.0)
        stats.add_success(4.0)
        stats.add_failure(1.0)
        
        assert stats.average_processing_time == 7.0 / 3

    def test_to_dict(self):
        """딕셔너리 변환 테스트"""
        stats = ConversionStats()
        stats.add_success(2.0)
        stats.add_failure(1.0)
        
        result_dict = stats.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['total_conversions'] == 2
        assert result_dict['successful_conversions'] == 1
        assert result_dict['failed_conversions'] == 1
        assert result_dict['success_rate'] == 50.0
        assert result_dict['total_processing_time'] == 3.0
        assert result_dict['average_processing_time'] == 1.5


class TestConversionResult:
    """ConversionResult 클래스 테스트"""

    def test_successful_result_creation(self):
        """성공적인 결과 생성 테스트"""
        input_file = Path("test.pdf")
        output_file = Path("test.md")
        
        result = ConversionResult(
            success=True,
            input_file=input_file,
            output_file=output_file,
            pages_processed=5,
            elements_found=20,
            processing_time=2.5
        )
        
        assert result.success is True
        assert result.input_file == input_file
        assert result.output_file == output_file
        assert result.pages_processed == 5
        assert result.elements_found == 20
        assert result.processing_time == 2.5
        assert result.error_message is None

    def test_failed_result_creation(self):
        """실패한 결과 생성 테스트"""
        input_file = Path("test.pdf")
        error_message = "PDF 파일을 읽을 수 없습니다"
        
        result = ConversionResult(
            success=False,
            input_file=input_file,
            error_message=error_message,
            processing_time=1.0
        )
        
        assert result.success is False
        assert result.input_file == input_file
        assert result.output_file is None
        assert result.pages_processed == 0
        assert result.elements_found == 0
        assert result.processing_time == 1.0
        assert result.error_message == error_message


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 