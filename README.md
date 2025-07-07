# PDF to Markdown 변환기

PDF 문서를 Markdown 형식으로 자동 변환하는 Python CLI 도구입니다.

## 🚀 주요 기능

- **📄 PDF 파일 읽기 및 분석**: 다양한 PDF 형식 지원
- **📝 텍스트 추출 및 구조 인식**: 제목, 본문, 리스트 자동 분류
- **🔄 Markdown 형식 변환**: 표준 Markdown 문법으로 변환
- **🖼️ 이미지 추출 및 링크 생성**: PDF 내 이미지 자동 추출
- **📊 테이블 인식 및 변환**: 복잡한 테이블 구조 보존
- **💻 CLI 인터페이스**: 사용자 친화적인 명령행 도구
- **⚙️ 설정 파일 지원**: 변환 옵션 커스터마이징
- **📦 일괄 처리 기능**: 여러 PDF 파일 동시 변환

## 🛠️ 기술 스택

- **언어**: Python 3.8+
- **주요 라이브러리**: 
  - PyMuPDF (PDF 처리)
  - pdfplumber (테이블 추출)
  - Pillow (이미지 처리)
  - Click (CLI 인터페이스)
- **개발 도구**: Black, isort, flake8, mypy, pytest

## 📚 문서

- [개발 계획서](개발_계획서.md) - 전체 개발 로드맵과 단계별 계획
- [Phase 1.2 가이드](PHASE_1_2_GUIDE.md) - 의존성 라이브러리 설치 및 검증 가이드

## 📦 설치 방법

### 🚨 현재 단계: Phase 1.2 - 의존성 설치 및 검증

이 프로젝트는 현재 **Phase 1.2** 단계에 있습니다. 아래 방법 중 하나를 선택하여 의존성을 설치하고 검증하세요.

### 방법 1: 자동 설치 및 검증 (권장)
```bash
# Python 3.8+ 설치 후 실행
python install_and_verify.py
```

### 방법 2: 수동 설치
```bash
# 1. 저장소 클론
git clone https://github.com/your-username/pdf-to-markdown.git
cd pdf-to-markdown

# 2. 가상환경 생성 및 활성화 (권장)
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 개발 도구 설치 (선택사항)
pip install -r requirements-dev.txt

# 5. 검증 실행
python tests/test_dependencies.py
```

**📖 상세한 설치 가이드**: [Phase 1.2 가이드](PHASE_1_2_GUIDE.md)를 참조하세요.

## 🚀 사용법

### 기본 사용법
```bash
python main.py document.pdf
```

### 출력 파일 지정
```bash
python main.py document.pdf output.md
```

### 이미지 추출 포함
```bash
python main.py document.pdf --extract-images
```

### 일괄 처리
```bash
python main.py *.pdf --batch --output-dir ./output
```

### 상세 로그
```bash
python main.py document.pdf --verbose
```

## ⚙️ 설정 옵션

설정 파일(`config.yaml`)을 통해 변환 옵션을 커스터마이징할 수 있습니다:

```yaml
conversion:
  title_font_threshold: 1.2
  extract_images: true
  preserve_formatting: true
  merge_paragraphs: false
  table_detection: true

output:
  encoding: 'utf-8'
  line_ending: '\n'
  indent_size: 2
  image_format: 'png'
```

## 📁 프로젝트 구조

```
pdf-to-markdown/
├── src/
│   └── pdf_to_markdown/
│       ├── pdf_reader.py          # PDF 파일 읽기 모듈
│       ├── text_parser.py         # 텍스트 구조 분석 모듈
│       ├── markdown_converter.py  # Markdown 변환 모듈
│       ├── config.py              # 설정 관리 모듈
│       └── main.py                # CLI 메인 인터페이스
├── tests/                         # 테스트 파일들
├── docs/                          # 문서
├── test_files/                    # 테스트용 PDF 파일들
├── output/                        # 변환된 Markdown 파일들
├── images/                        # 추출된 이미지들
├── requirements.txt               # 주요 의존성
├── requirements-dev.txt           # 개발 도구 의존성
└── README.md                      # 프로젝트 문서
```

## 🧪 테스트

```bash
# 모든 테스트 실행
pytest

# 커버리지 포함
pytest --cov=src tests/

# 특정 테스트 파일
pytest tests/test_pdf_reader.py
```

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

# pre-commit 훅 설정
pre-commit install

# 코드 포맷팅
black src/ tests/
isort src/ tests/

# 린팅
flake8 src/ tests/
mypy src/
```

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🚧 개발 상태

- [x] 프로젝트 초기 설정
- [ ] 핵심 모듈 개발
- [ ] CLI 인터페이스 구현
- [ ] 테스트 작성
- [ ] 문서화 완성
- [ ] 배포 준비

## 📞 연락처

- 프로젝트 링크: [https://github.com/your-username/pdf-to-markdown](https://github.com/your-username/pdf-to-markdown)
- 이슈 제보: [https://github.com/your-username/pdf-to-markdown/issues](https://github.com/your-username/pdf-to-markdown/issues)

## 🙏 감사의 말

- [PyMuPDF](https://pymupdf.readthedocs.io/) - 강력한 PDF 처리 라이브러리
- [pdfplumber](https://github.com/jsvine/pdfplumber) - 테이블 추출 기능
- [Click](https://click.palletsprojects.com/) - 사용자 친화적인 CLI 프레임워크 