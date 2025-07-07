# Phase 1.2: 의존성 라이브러리 설치 및 검증 가이드

## 📋 개요
이 가이드는 **개발_계획서.md**의 Phase 1.2에 따라 필요한 라이브러리를 설치하고 기본 동작을 검증하는 과정을 안내합니다.

## 🚀 사전 요구사항

### Python 설치 확인
다음 명령어로 Python 설치 상태를 확인하세요:

```bash
# Windows
python --version

# macOS/Linux (또는 Windows에서 py 런처 사용)
py --version
```

**Python 3.8 이상**이 설치되어 있어야 합니다.

### Python 설치가 필요한 경우
1. **공식 사이트 방문**: https://www.python.org/downloads/
2. **최신 안정 버전 다운로드** (3.8 이상)
3. **설치 시 주의사항**: "Add Python to PATH" 옵션 반드시 체크
4. **설치 확인**: 새 터미널에서 `python --version` 실행

## 🛠️ 자동 설치 및 검증 (권장)

### 1. 자동화 스크립트 실행
```bash
python install_and_verify.py
```

이 스크립트는 다음 작업을 자동으로 수행합니다:
- ✅ Python 버전 확인
- 📦 주요 라이브러리 설치 (`requirements.txt`)
- 🔧 개발 도구 설치 (`requirements-dev.txt`)
- 🧪 모든 라이브러리 기본 동작 검증
- 📄 테스트용 PDF 파일 생성

### 2. 결과 확인
성공 시 다음과 같은 메시지를 확인할 수 있습니다:
```
🎉 Phase 1.2 의존성 설치 및 검증 완료!
✅ 다음 단계 (Phase 2: 핵심 모듈 개발)로 진행 가능합니다.
```

## 🔧 수동 설치 및 검증

자동화 스크립트가 작동하지 않는 경우 수동으로 진행하세요.

### 1. 가상환경 설정 (권장)
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 주요 라이브러리 설치
```bash
pip install -r requirements.txt
```

**설치되는 라이브러리:**
- `pymupdf>=1.23.0` - PDF 처리
- `pdfplumber>=0.10.0` - 테이블 추출
- `Pillow>=10.0.0` - 이미지 처리
- `click>=8.1.0` - CLI 인터페이스
- `pyyaml>=6.0` - 설정 파일 처리
- `tqdm>=4.65.0` - 진행률 표시

### 3. 개발 도구 설치 (선택사항)
```bash
pip install -r requirements-dev.txt
```

**설치되는 도구:**
- `black` - 코드 포맷터
- `isort` - import 정렬
- `flake8` - 코드 린터
- `mypy` - 타입 체커
- `pytest` - 테스트 프레임워크
- `pytest-cov` - 테스트 커버리지
- `pre-commit` - Git 훅 관리

### 4. 의존성 검증
```bash
python tests/test_dependencies.py
```

### 5. 테스트 PDF 파일 생성
```bash
python tests/create_test_pdf.py
```

## 📊 검증 결과 해석

### ✅ 성공적인 검증 결과
```
🚀 PDF to Markdown 변환기 - 의존성 검증
🔍 PyMuPDF (fitz) 테스트 중...
   ✅ PyMuPDF 버전: 1.23.x
   ✅ PDF 문서 생성/편집 기능 정상

🔍 pdfplumber 테스트 중...
   ✅ pdfplumber 버전: 0.10.x
   ✅ pdfplumber import 성공

... (다른 라이브러리들)

📊 검증 결과 요약
주요 라이브러리: 6/6 성공
🎉 모든 주요 라이브러리가 정상적으로 설치되고 동작합니다!
✅ Phase 1.2 의존성 검증 완료
```

### ❌ 문제가 있는 경우
특정 라이브러리에서 오류가 발생하면:

1. **pip 업그레이드**:
   ```bash
   python -m pip install --upgrade pip
   ```

2. **라이브러리 개별 설치**:
   ```bash
   pip install pymupdf
   pip install pdfplumber
   # ... (문제가 있는 라이브러리만)
   ```

3. **가상환경 재생성**:
   ```bash
   deactivate  # 가상환경 비활성화
   rmdir /s venv  # Windows (또는 rm -rf venv)
   python -m venv venv  # 재생성
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 📂 생성되는 파일들

검증 완료 후 다음 파일들이 생성됩니다:

```
test_files/
├── sample.pdf          # 기본 텍스트 테스트용 PDF
└── table_sample.pdf    # 테이블 테스트용 PDF
```

## 🧪 개별 라이브러리 테스트

각 라이브러리를 개별적으로 테스트하려면:

### PyMuPDF 테스트
```python
import fitz
doc = fitz.open()
page = doc.new_page()
page.insert_text((100, 100), "Hello PyMuPDF!")
doc.close()
print("PyMuPDF 정상 동작")
```

### pdfplumber 테스트
```python
import pdfplumber
print(f"pdfplumber 버전: {pdfplumber.__version__}")
```

### Click 테스트
```python
import click

@click.command()
def hello():
    click.echo("Click 정상 동작!")

if __name__ == '__main__':
    hello()
```

## 🚨 일반적인 문제 해결

### 문제 1: "python 명령을 찾을 수 없음"
**해결책**: Python 설치 시 PATH 등록을 하지 않은 경우
- Python 재설치하며 "Add Python to PATH" 체크
- 또는 환경변수에 Python 경로 수동 추가

### 문제 2: pip 설치 오류
**해결책**: 
```bash
python -m ensurepip --default-pip
python -m pip install --upgrade pip
```

### 문제 3: 가상환경 활성화 오류 (Windows PowerShell)
**해결책**: 실행 정책 변경
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 문제 4: 특정 라이브러리 설치 실패
**해결책**: 
- 관리자 권한으로 실행
- Microsoft Visual C++ Build Tools 설치 (Windows)
- 인터넷 연결 상태 확인

## ✅ 완료 체크리스트

Phase 1.2 완료를 위한 체크리스트:

- [ ] Python 3.8 이상 설치 확인
- [ ] 가상환경 생성 및 활성화
- [ ] requirements.txt 라이브러리 설치 완료
- [ ] requirements-dev.txt 개발 도구 설치 완료
- [ ] 의존성 검증 스크립트 성공 실행
- [ ] 테스트 PDF 파일 생성 완료
- [ ] 모든 주요 라이브러리 정상 동작 확인

## 🚀 다음 단계

Phase 1.2 완료 후:
1. **Git 커밋**: 현재 상태를 커밋
2. **Phase 2 시작**: 핵심 모듈 개발 착수
3. **개발 환경 설정**: IDE/에디터에서 Python 환경 연결

---

**Phase 1.2 완료 시 Phase 2로 진행할 준비가 완료됩니다!** 🎉 