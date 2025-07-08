#!/usr/bin/env python3
"""
PDF to Markdown 변환기 CLI 진입점

사용법:
    python main.py convert input.pdf [output.md]
    python main.py create-config config.yaml
    python main.py list-presets
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # CLI 모듈 import
    from src.pdf_to_markdown.main import cli
    
    if __name__ == '__main__':
        # CLI 실행
        cli()
        
except ImportError as e:
    print(f"❌ 모듈 import 오류: {e}")
    print("\n📋 해결 방법:")
    print("1. 의존성 설치 확인:")
    print("   pip install -r requirements.txt")
    print()
    print("2. 환경 변수 확인:")
    print("   PYTHONPATH에 프로젝트 루트가 포함되어 있는지 확인")
    print()
    print("3. 의존성 자동 설치:")
    print("   python install_and_verify.py")
    
    sys.exit(1)
    
except Exception as e:
    print(f"❌ 예상치 못한 오류: {e}")
    print("\n🔍 디버그 정보:")
    print(f"Python 버전: {sys.version}")
    print(f"현재 디렉토리: {os.getcwd()}")
    print(f"프로젝트 루트: {project_root}")
    
    sys.exit(1) 