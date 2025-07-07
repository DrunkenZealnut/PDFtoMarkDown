#!/usr/bin/env python3
"""
Phase 1.2: 의존성 라이브러리 설치 및 검증 자동화 스크립트

이 스크립트는 다음 작업을 수행합니다:
1. 주요 라이브러리 설치
2. 개발 도구 설치 
3. 기본 동작 검증
4. 테스트 PDF 파일 생성
"""

import subprocess
import sys
from pathlib import Path


def check_python():
    """Python 설치 상태 확인"""
    print("🔍 Python 설치 상태 확인 중...")
    try:
        python_version = sys.version
        print(f"   ✅ Python 버전: {python_version}")
        
        if sys.version_info < (3, 8):
            print("   ⚠️  Python 3.8 이상이 권장됩니다.")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ Python 확인 실패: {e}")
        return False


def run_pip_install(requirements_file):
    """pip install 실행"""
    print(f"📦 {requirements_file} 설치 중...")
    
    try:
        # pip install 실행
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ], capture_output=True, text=True, check=True)
        
        print(f"   ✅ {requirements_file} 설치 완료")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {requirements_file} 설치 실패:")
        print(f"   오류: {e.stderr}")
        return False
    except Exception as e:
        print(f"   ❌ 예상치 못한 오류: {e}")
        return False


def run_verification():
    """의존성 검증 스크립트 실행"""
    print("🧪 의존성 검증 실행 중...")
    
    try:
        # 검증 스크립트 실행
        result = subprocess.run([
            sys.executable, "tests/test_dependencies.py"
        ], capture_output=True, text=True)
        
        # 결과 출력
        print(result.stdout)
        if result.stderr:
            print("오류 메시지:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"   ❌ 검증 스크립트 실행 실패: {e}")
        return False


def create_test_files():
    """테스트 PDF 파일 생성"""
    print("📄 테스트 PDF 파일 생성 중...")
    
    try:
        result = subprocess.run([
            sys.executable, "tests/create_test_pdf.py"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("경고/오류:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"   ❌ 테스트 PDF 생성 실패: {e}")
        return False


def main():
    """Phase 1.2 전체 실행"""
    print("=" * 60)
    print("🚀 Phase 1.2: 의존성 라이브러리 설치 및 검증")
    print("=" * 60)
    print()
    
    # 1. Python 상태 확인
    if not check_python():
        print("❌ Python 설치 또는 버전에 문제가 있습니다.")
        return False
    print()
    
    # 2. 주요 라이브러리 설치
    if not run_pip_install("requirements.txt"):
        print("❌ 주요 라이브러리 설치에 실패했습니다.")
        return False
    print()
    
    # 3. 개발 도구 설치
    if not run_pip_install("requirements-dev.txt"):
        print("⚠️  개발 도구 설치에 실패했지만 계속 진행합니다.")
    print()
    
    # 4. 의존성 검증
    print("=" * 40)
    verification_success = run_verification()
    print("=" * 40)
    print()
    
    # 5. 테스트 파일 생성
    test_files_success = create_test_files()
    print()
    
    # 최종 결과
    print("=" * 60)
    print("📊 Phase 1.2 완료 결과")
    print("=" * 60)
    
    if verification_success:
        print("✅ 주요 라이브러리 설치 및 검증 성공")
    else:
        print("❌ 라이브러리 검증에 문제가 있습니다.")
    
    if test_files_success:
        print("✅ 테스트 PDF 파일 생성 성공")
    else:
        print("⚠️  테스트 PDF 파일 생성에 실패했습니다.")
    
    print()
    print("📁 현재 프로젝트 구조:")
    for item in sorted(Path(".").glob("*")):
        if item.is_dir() and not item.name.startswith('.'):
            print(f"   📂 {item.name}/")
        elif item.is_file() and item.suffix in ['.py', '.txt', '.md']:
            print(f"   📄 {item.name}")
    
    print()
    if verification_success:
        print("🎉 Phase 1.2 의존성 설치 및 검증 완료!")
        print("✅ 다음 단계 (Phase 2: 핵심 모듈 개발)로 진행 가능합니다.")
        return True
    else:
        print("🚨 일부 문제가 발생했습니다. 오류를 해결한 후 다시 시도해주세요.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 