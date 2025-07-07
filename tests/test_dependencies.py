#!/usr/bin/env python3
"""
의존성 라이브러리 검증 스크립트

Phase 1.2에서 설치된 라이브러리들의 기본 동작을 테스트합니다.
"""

import sys
import io
from pathlib import Path


def test_pymupdf():
    """PyMuPDF (fitz) 라이브러리 기본 동작 테스트"""
    print("🔍 PyMuPDF (fitz) 테스트 중...")
    
    try:
        import fitz
        print(f"   ✅ PyMuPDF 버전: {fitz.version}")
        
        # 빈 PDF 문서 생성 테스트
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((100, 100), "Hello, PyMuPDF!")
        doc.close()
        print("   ✅ PDF 문서 생성/편집 기능 정상")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ PyMuPDF import 실패: {e}")
        return False
    except Exception as e:
        print(f"   ❌ PyMuPDF 기능 테스트 실패: {e}")
        return False


def test_pdfplumber():
    """pdfplumber 라이브러리 기본 동작 테스트"""
    print("🔍 pdfplumber 테스트 중...")
    
    try:
        import pdfplumber
        print(f"   ✅ pdfplumber 버전: {pdfplumber.__version__}")
        
        # pdfplumber 기본 기능 확인
        # 실제 PDF 파일이 없으므로 import만 확인
        print("   ✅ pdfplumber import 성공")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ pdfplumber import 실패: {e}")
        return False
    except Exception as e:
        print(f"   ❌ pdfplumber 기능 테스트 실패: {e}")
        return False


def test_pillow():
    """Pillow (PIL) 라이브러리 기본 동작 테스트"""
    print("🔍 Pillow (PIL) 테스트 중...")
    
    try:
        from PIL import Image, ImageDraw
        import PIL
        print(f"   ✅ Pillow 버전: {PIL.__version__}")
        
        # 간단한 이미지 생성 테스트
        img = Image.new('RGB', (100, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Test", fill='black')
        print("   ✅ 이미지 생성/편집 기능 정상")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Pillow import 실패: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Pillow 기능 테스트 실패: {e}")
        return False


def test_click():
    """Click 라이브러리 기본 동작 테스트"""
    print("🔍 Click 테스트 중...")
    
    try:
        import click
        print(f"   ✅ Click 버전: {click.__version__}")
        
        # 간단한 CLI 명령어 정의 테스트
        @click.command()
        @click.option('--name', default='World', help='이름을 입력하세요.')
        def hello(name):
            """간단한 인사 명령어"""
            click.echo(f'Hello {name}!')
        
        print("   ✅ Click CLI 명령어 정의 기능 정상")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Click import 실패: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Click 기능 테스트 실패: {e}")
        return False


def test_pyyaml():
    """PyYAML 라이브러리 기본 동작 테스트"""
    print("🔍 PyYAML 테스트 중...")
    
    try:
        import yaml
        print(f"   ✅ PyYAML 버전: {yaml.__version__}")
        
        # YAML 읽기/쓰기 테스트
        test_data = {
            'conversion': {
                'title_font_threshold': 1.2,
                'extract_images': True
            },
            'output': {
                'encoding': 'utf-8'
            }
        }
        
        yaml_string = yaml.dump(test_data)
        parsed_data = yaml.safe_load(yaml_string)
        
        assert parsed_data == test_data
        print("   ✅ YAML 읽기/쓰기 기능 정상")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ PyYAML import 실패: {e}")
        return False
    except Exception as e:
        print(f"   ❌ PyYAML 기능 테스트 실패: {e}")
        return False


def test_tqdm():
    """tqdm 라이브러리 기본 동작 테스트"""
    print("🔍 tqdm 테스트 중...")
    
    try:
        from tqdm import tqdm
        import time
        print(f"   ✅ tqdm 버전: {tqdm.__version__}")
        
        # 간단한 진행률 바 테스트
        items = range(5)
        for item in tqdm(items, desc="테스트 진행률", leave=False):
            time.sleep(0.1)  # 짧은 지연
        
        print("   ✅ 진행률 표시 기능 정상")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ tqdm import 실패: {e}")
        return False
    except Exception as e:
        print(f"   ❌ tqdm 기능 테스트 실패: {e}")
        return False


def test_development_tools():
    """개발 도구들 기본 동작 테스트"""
    print("🔍 개발 도구들 테스트 중...")
    
    tools = [
        ('black', 'black'),
        ('isort', 'isort'), 
        ('flake8', 'flake8'),
        ('mypy', 'mypy'),
        ('pytest', 'pytest'),
        ('pytest-cov', 'pytest_cov'),
        ('pre-commit', 'pre_commit')
    ]
    
    success_count = 0
    for tool_name, import_name in tools:
        try:
            __import__(import_name)
            print(f"   ✅ {tool_name} import 성공")
            success_count += 1
        except ImportError:
            print(f"   ❌ {tool_name} import 실패")
    
    print(f"   📊 개발 도구 설치 현황: {success_count}/{len(tools)}")
    return success_count == len(tools)


def main():
    """전체 의존성 검증 실행"""
    print("=" * 50)
    print("🚀 PDF to Markdown 변환기 - 의존성 검증")
    print("=" * 50)
    print()
    
    # 주요 라이브러리 테스트
    main_tests = [
        ("PyMuPDF", test_pymupdf),
        ("pdfplumber", test_pdfplumber), 
        ("Pillow", test_pillow),
        ("Click", test_click),
        ("PyYAML", test_pyyaml),
        ("tqdm", test_tqdm)
    ]
    
    success_count = 0
    total_count = len(main_tests)
    
    for test_name, test_func in main_tests:
        try:
            if test_func():
                success_count += 1
            print()
        except Exception as e:
            print(f"   💥 {test_name} 테스트 중 예외 발생: {e}")
            print()
    
    # 개발 도구 테스트
    print("=" * 30)
    test_development_tools()
    print()
    
    # 결과 요약
    print("=" * 50)
    print("📊 검증 결과 요약")
    print("=" * 50)
    print(f"주요 라이브러리: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("🎉 모든 주요 라이브러리가 정상적으로 설치되고 동작합니다!")
        print("✅ Phase 1.2 의존성 검증 완료")
        return True
    else:
        print(f"⚠️  {total_count - success_count}개의 라이브러리에 문제가 있습니다.")
        print("❌ 누락된 라이브러리를 다시 설치해주세요.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 