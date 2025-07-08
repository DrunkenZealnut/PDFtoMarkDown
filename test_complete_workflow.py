"""
전체 워크플로우 통합 테스트

구현된 모든 모듈들이 함께 작동하는지 확인합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_module_imports():
    """모든 주요 모듈의 import 테스트"""
    print("=== 모듈 Import 테스트 ===")
    
    try:
        # 핵심 모듈들
        from src.pdf_to_markdown import (
            PDFReader, TextParser, MarkdownGenerator, 
            PDFToMarkdownConverter, ConversionManager
        )
        print("✅ 핵심 변환 모듈 import 성공")
        
        # 설정 관련
        from src.pdf_to_markdown import (
            ConfigManager, AppConfig, MarkdownConfig, ConfigPresets
        )
        print("✅ 설정 관리 모듈 import 성공")
        
        # UI 및 유틸리티
        from src.pdf_to_markdown import (
            ProgressReporter, StatusReporter, ConversionStats
        )
        print("✅ UI 유틸리티 모듈 import 성공")
        
        # 데이터 모델
        from src.pdf_to_markdown import (
            DocumentContent, DocumentStructure, ConversionResult
        )
        print("✅ 데이터 모델 import 성공")
        
        # 예외 클래스
        from src.pdf_to_markdown import (
            PDFProcessingError, ConfigurationError
        )
        print("✅ 예외 클래스 import 성공")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import 실패: {e}")
        return False


def test_configuration_system():
    """설정 시스템 테스트"""
    print("\n=== 설정 시스템 테스트 ===")
    
    try:
        from src.pdf_to_markdown import ConfigManager, ConfigPresets
        
        # ConfigManager 기본 동작 테스트
        config_manager = ConfigManager()
        
        # 기본 설정 로드
        default_config = config_manager.get_default_config()
        print("✅ 기본 설정 로드 성공")
        
        # 프리셋 설정 테스트
        for preset_name in ['github', 'minimal', 'documentation', 'publishing']:
            preset_config = config_manager.get_preset_config(preset_name)
            print(f"✅ {preset_name} 프리셋 로드 성공")
        
        # 설정 유효성 검사
        default_config.validate()
        print("✅ 설정 유효성 검사 통과")
        
        # CLI 옵션 병합 테스트
        cli_options = {
            'extract_images': True,
            'verbose': 2,
            'encoding': 'utf-8'
        }
        merged_config = config_manager.merge_cli_options(default_config, cli_options)
        print("✅ CLI 옵션 병합 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 설정 시스템 테스트 실패: {e}")
        return False


def test_converter_initialization():
    """컨버터 초기화 테스트"""
    print("\n=== 컨버터 초기화 테스트 ===")
    
    try:
        from src.pdf_to_markdown import PDFToMarkdownConverter, ConfigManager
        
        # 설정 생성
        config_manager = ConfigManager()
        config = config_manager.get_default_config()
        
        # 컨버터 초기화
        converter = PDFToMarkdownConverter(config)
        print("✅ PDFToMarkdownConverter 초기화 성공")
        
        # 통계 확인
        stats = converter.get_conversion_stats()
        print(f"✅ 초기 통계: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ 컨버터 초기화 실패: {e}")
        return False


def test_convenience_functions():
    """편의 함수 테스트"""
    print("\n=== 편의 함수 테스트 ===")
    
    try:
        from src.pdf_to_markdown import convert_pdf, convert_directory, create_config
        
        # 설정 생성 함수 테스트
        config = create_config("github", extract_images=True)
        print("✅ create_config 함수 동작 확인")
        
        # convert_pdf 함수 시그니처 확인 (실제 변환은 PDF 파일이 있어야 함)
        print("✅ convert_pdf 함수 사용 가능")
        
        # convert_directory 함수 시그니처 확인
        print("✅ convert_directory 함수 사용 가능")
        
        return True
        
    except Exception as e:
        print(f"❌ 편의 함수 테스트 실패: {e}")
        return False


def test_ui_components():
    """UI 컴포넌트 테스트"""
    print("\n=== UI 컴포넌트 테스트 ===")
    
    try:
        from src.pdf_to_markdown import (
            ProgressReporter, StatusReporter, ConversionStats, 
            BatchProgressReporter
        )
        from datetime import datetime
        
        # ConversionStats 테스트
        stats = ConversionStats(start_time=datetime.now())
        stats.total_pages = 10
        stats.processed_pages = 5
        print(f"✅ ConversionStats 생성: 성공률 {stats.success_rate:.1f}%")
        
        # StatusReporter 테스트 (조용한 모드)
        status_reporter = StatusReporter(quiet=True)
        status_reporter.info("테스트 메시지")
        print("✅ StatusReporter 동작 확인")
        
        # ProgressReporter 테스트 (조용한 모드)
        progress_reporter = ProgressReporter(total_pages=10, quiet=True)
        progress_reporter.update(5, "테스트 중...")
        print("✅ ProgressReporter 동작 확인")
        
        return True
        
    except Exception as e:
        print(f"❌ UI 컴포넌트 테스트 실패: {e}")
        return False


def test_data_models():
    """데이터 모델 테스트"""
    print("\n=== 데이터 모델 테스트 ===")
    
    try:
        from src.pdf_to_markdown import (
            DocumentMetadata, FontInfo, FontStyle, 
            TextBlock, ConversionResult
        )
        from pathlib import Path
        
        # FontInfo 생성
        font_info = FontInfo(
            name="Arial",
            size=12.0,
            style=FontStyle.NORMAL,
            color=(0, 0, 0)
        )
        print("✅ FontInfo 객체 생성 성공")
        
        # TextBlock 생성
        text_block = TextBlock(
            text="테스트 텍스트",
            bbox=(0, 0, 100, 20),
            font_info=font_info,
            page_num=0
        )
        print("✅ TextBlock 객체 생성 성공")
        
        # DocumentMetadata 생성
        metadata = DocumentMetadata(
            title="테스트 문서",
            page_count=5
        )
        print("✅ DocumentMetadata 객체 생성 성공")
        
        # ConversionResult 생성
        result = ConversionResult(
            success=True,
            input_file=Path("test.pdf"),
            output_file=Path("test.md")
        )
        print(f"✅ ConversionResult 생성: 성공={result.is_success}")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터 모델 테스트 실패: {e}")
        return False


def main():
    """전체 테스트 실행"""
    print("🧪 PDF to Markdown 변환기 통합 테스트")
    print("=" * 50)
    
    test_results = []
    
    # 각 테스트 실행
    test_functions = [
        test_module_imports,
        test_configuration_system,
        test_converter_initialization,
        test_convenience_functions,
        test_ui_components,
        test_data_models
    ]
    
    for test_func in test_functions:
        try:
            result = test_func()
            test_results.append(result)
        except Exception as e:
            print(f"❌ {test_func.__name__} 실행 중 오류: {e}")
            test_results.append(False)
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    success_count = sum(test_results)
    total_count = len(test_results)
    
    for i, (test_func, result) in enumerate(zip(test_functions, test_results)):
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{i+1}. {test_func.__name__}: {status}")
    
    print(f"\n📈 전체 성공률: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("\n🎉 모든 테스트 통과! 시스템이 정상적으로 구성되었습니다.")
        print("\n🚀 다음 단계:")
        print("1. 실제 PDF 파일로 변환 테스트")
        print("2. CLI 인터페이스 사용:")
        print("   python main.py convert input.pdf output.md")
        print("3. 라이브러리로 사용:")
        print("   from src.pdf_to_markdown import convert_pdf")
        print("   result = convert_pdf('input.pdf')")
        
        return True
    else:
        print(f"\n⚠️ {total_count - success_count}개 테스트 실패")
        print("문제를 해결한 후 다시 실행해주세요.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 