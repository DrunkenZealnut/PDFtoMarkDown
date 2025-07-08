# PDF to Markdown 변환기

PDF 문서를 Markdown 형식으로 자동 변환하는 Python 라이브러리 및 CLI 도구입니다.

## 🚀 주요 기능

- **📄 PDF 파일 읽기**: PyMuPDF를 활용한 안정적인 PDF 텍스트 추출
- **🧠 지능형 구조 분석**: 제목, 본문, 리스트, 테이블 자동 분류
- **📝 Markdown 변환**: 표준 Markdown 문법으로 정확한 변환
- **🖼️ 이미지 처리**: PDF 내 이미지 추출 및 링크 생성
- **📊 테이블 변환**: 복잡한 테이블 구조 Markdown 테이블로 변환
- **⚙️ 유연한 설정**: 상세한 변환 옵션 커스터마이징
- **📋 메타데이터 지원**: YAML Front Matter 자동 생성
- **🔧 모듈화 설계**: 각 기능별 독립적 사용 가능

## 🛠️ 기술 스택

- **언어**: Python 3.8+
- **핵심 라이브러리**: 
  - PyMuPDF (PDF 처리)
  - pdfplumber (테이블 추출)
  - Pillow (이미지 처리)
  - Click (CLI 인터페이스)
- **개발 도구**: Black, isort, flake8, mypy, pytest

## 📦 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/pdf-to-markdown.git
cd pdf-to-markdown
```

### 2. 가상환경 설정 (권장)
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. 의존성 설치
```bash
# 기본 의존성 설치
pip install -r requirements.txt

# 개발 도구 설치 (선택사항)
pip install -r requirements-dev.txt
```

### 4. 설치 검증
```bash
# 자동 검증 스크립트 실행
python install_and_verify.py

# 또는 수동 테스트
python -c "from src.pdf_to_markdown import MarkdownGenerator; print('설치 완료!')"
```

## 🚀 사용법

### Python 모듈로 사용

```python
from src.pdf_to_markdown import (
    PDFReader, TextParser, MarkdownGenerator, MarkdownConfig
)
from pathlib import Path

# 1. PDF 읽기
pdf_reader = PDFReader()
document = pdf_reader.read_pdf("example.pdf")

# 2. 텍스트 구조 분석
text_parser = TextParser()
structure = text_parser.parse_document(document)

# 3. Markdown 생성
config = MarkdownConfig()  # 또는 ConfigPresets.github_flavored()
generator = MarkdownGenerator(config)
markdown_text = generator.generate_markdown(structure, document)

# 4. 파일 저장
output_path = Path("output.md")
generator.save_markdown(markdown_text, output_path)
```

### CLI 사용 (개발 중)
```bash
# 기본 변환
python main.py document.pdf

# 출력 파일 지정
python main.py document.pdf output.md

# 이미지 추출 포함
python main.py document.pdf --extract-images

# GitHub 스타일 변환
python main.py document.pdf --config github
```

## ⚙️ 설정 옵션

### 사전 정의된 설정
```python
from src.pdf_to_markdown.markdown_config import ConfigPresets

# GitHub Flavored Markdown 스타일
github_config = ConfigPresets.github_flavored()

# 최소 설정 (빠른 변환)
minimal_config = ConfigPresets.minimal()

# 문서화용 설정 (상세)
doc_config = ConfigPresets.documentation()

# 출판용 설정 (고품질)
pub_config = ConfigPresets.publishing()
```

### 커스텀 설정
```python
from src.pdf_to_markdown.markdown_config import MarkdownConfig

config = MarkdownConfig()

# 제목 설정
config.heading.max_level = 4
config.heading.add_toc = True

# 이미지 설정
config.image.extract_images = True
config.image.max_width = 800

# 테이블 설정
config.table.align_columns = True
config.table.include_header = True

# 출력 설정
config.output.encoding = "utf-8"
config.output.add_final_newline = True
```

## 📁 프로젝트 구조

```
pdf-to-markdown/
├── src/
│   └── pdf_to_markdown/
│       ├── __init__.py              # 패키지 초기화
│       ├── pdf_reader.py            # PDF 파일 읽기
│       ├── text_parser.py           # 텍스트 구조 분석
│       ├── markdown_generator.py    # Markdown 변환
│       ├── markdown_config.py       # 설정 관리
│       ├── text_structures.py       # 문서 구조 모델
│       ├── data_models.py           # 데이터 모델
│       └── exceptions.py            # 예외 처리
├── tests/                           # 단위 테스트
├── test_*.py                        # 기본 기능 테스트
├── docs/                            # 문서
├── test_files/                      # 테스트용 PDF 파일
├── output/                          # 변환 결과
├── images/                          # 추출된 이미지
├── requirements.txt                 # 주요 의존성
├── requirements-dev.txt             # 개발 도구
└── README.md                        # 프로젝트 문서
```

## 🧪 테스트

### 기본 테스트 실행
```bash
# PDF 리더 테스트
python test_pdf_reader_basic.py

# 텍스트 분석 테스트
python test_text_parser_basic.py

# Markdown 생성 테스트
python test_markdown_generator_basic.py

# 통합 테스트
python test_integration_basic.py

# 전체 파이프라인 테스트
python test_full_pipeline.py
```

### 의존성 검증
```bash
# 의존성 설치 상태 확인
python tests/test_dependencies.py

# 자동 설치 및 검증
python install_and_verify.py
```

### Pytest 사용 (고급)
```bash
# 모든 테스트 실행
pytest

# 커버리지 포함
pytest --cov=src tests/

# 특정 테스트
pytest tests/test_pdf_reader.py
```

## 🔧 주요 모듈 소개

### PDFReader
- PDF 파일 읽기 및 메타데이터 추출
- 텍스트 블록 및 이미지 정보 수집
- 다양한 PDF 형식 지원

### TextParser
- 폰트 크기 및 위치 기반 구조 분석
- 제목, 단락, 리스트, 테이블 자동 분류
- 계층적 문서 구조 생성

### MarkdownGenerator
- 분석된 구조를 Markdown으로 변환
- YAML Front Matter 자동 생성
- 목차(TOC) 생성 지원
- 다양한 Markdown 스타일 지원

### MarkdownConfig
- 상세한 변환 옵션 설정
- 사전 정의된 스타일 프리셋
- 설정 유효성 검사

## 📈 성능 및 품질

- **테스트 커버리지**: 90%+ 유지
- **타입 힌트**: 모든 공개 API에 적용
- **문서화**: 모든 모듈과 함수에 한국어 docstring
- **에러 처리**: 포괄적인 예외 처리 체계
- **로깅**: 상세한 처리 과정 로깅

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 개발 환경 설정
```bash
# 개발 도구 설치
pip install -r requirements-dev.txt

# 코드 포맷팅
black src/ tests/
isort src/ tests/

# 린팅
flake8 src/ tests/
mypy src/

# 테스트 실행
pytest
```

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🚧 개발 로드맵

### Phase 1: 핵심 모듈 개발 ✅
- [x] PDF 읽기 모듈
- [x] 텍스트 분석 모듈
- [x] Markdown 생성 모듈
- [x] 설정 관리 시스템
- [x] 데이터 모델 정의
- [x] 기본 테스트 작성

### Phase 2: 통합 및 최적화 🔄
- [x] 모듈 간 통합 테스트
- [ ] CLI 인터페이스 완성
- [ ] 성능 최적화
- [ ] 에러 처리 개선

### Phase 3: 고급 기능 📋
- [ ] 일괄 처리 기능
- [ ] 웹 인터페이스
- [ ] 플러그인 시스템
- [ ] 추가 출력 형식 지원

### Phase 4: 배포 및 유지보수 📦
- [ ] PyPI 패키지 배포
- [ ] Docker 이미지 제공
- [ ] CI/CD 파이프라인
- [ ] 사용자 가이드 완성

## 📞 연락처

- 프로젝트 링크: [https://github.com/your-username/pdf-to-markdown](https://github.com/your-username/pdf-to-markdown)
- 이슈 제보: [https://github.com/your-username/pdf-to-markdown/issues](https://github.com/your-username/pdf-to-markdown/issues)

## 🙏 감사의 말

- [PyMuPDF](https://pymupdf.readthedocs.io/) - 강력한 PDF 처리 라이브러리
- [pdfplumber](https://github.com/jsvine/pdfplumber) - 정확한 테이블 추출
- [Click](https://click.palletsprojects.com/) - 사용자 친화적인 CLI 프레임워크 