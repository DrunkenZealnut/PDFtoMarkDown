# 📄 PDF to Markdown 변환기

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

고품질 PDF 문서를 Markdown 형식으로 변환하는 Python 라이브러리 및 CLI 도구입니다. 
한국어 완벽 지원, 웹 접근성 준수, 그리고 사용자 친화적인 인터페이스를 제공합니다.

## ✨ 주요 기능

### 🔄 포괄적인 변환 기능
- **텍스트 추출**: 모든 텍스트 콘텐츠를 정확하게 추출
- **구조 인식**: 제목, 단락, 리스트, 테이블 자동 감지
- **이미지 처리**: 이미지 추출 및 참조 링크 생성
- **메타데이터**: 문서 정보 및 YAML Front Matter 지원

### ⚙️ 고급 설정 옵션
- **프리셋 시스템**: GitHub, 문서화, 출판용 등 사전 정의된 설정
- **사용자 정의**: YAML 설정 파일을 통한 세부 옵션 조정
- **다양한 출력**: 인코딩, 줄바꿈, 이미지 형식 선택 가능

### 🖥️ 사용자 친화적 인터페이스
- **CLI 도구**: 직관적인 명령행 인터페이스
- **Python API**: 프로그래밍 방식 통합 지원
- **진행률 표시**: 실시간 변환 진행 상황 표시
- **상세한 로깅**: 디버깅 및 모니터링 지원

### 🌐 웹 접근성 및 국제화
- **WCAG 2.1 AA 준수**: 웹 접근성 표준 따름
- **한국어 완벽 지원**: 모든 메시지와 문서가 한국어
- **유니코드 지원**: 다양한 언어의 문서 처리 가능

## 🚀 빠른 시작

### 설치

```bash
# PyPI에서 설치 (추후 배포 예정)
pip install pdf-to-markdown

# 개발 버전 설치
git clone https://github.com/yourusername/pdf-to-markdown.git
cd pdf-to-markdown
pip install -e .
```

### 기본 사용법

#### CLI 사용

```bash
# 기본 변환
pdf2md convert document.pdf output.md

# 이미지 포함 변환
pdf2md convert document.pdf output.md --extract-images

# GitHub 프리셋 사용
pdf2md convert document.pdf output.md --preset github

# 일괄 처리
pdf2md convert input_folder/ --batch --output-dir output_folder/

# 상세한 로그와 함께
pdf2md convert document.pdf output.md --verbose --verbose
```

#### Python API 사용

```python
from pdf_to_markdown import convert_pdf, convert_directory

# 단일 파일 변환
result = convert_pdf('document.pdf', 'output.md')
if result.success:
    print(f"변환 완료: {result.output_file}")
else:
    print(f"변환 실패: {result.error_message}")

# 일괄 변환
results = convert_directory('input_folder/', 'output_folder/')
print(f"성공: {sum(1 for r in results if r.success)}")
```

## 📋 설치 요구사항

### 시스템 요구사항
- **Python**: 3.8 이상
- **운영체제**: Windows, macOS, Linux
- **메모리**: 최소 512MB (대용량 PDF의 경우 더 많이 필요)

### Python 의존성
```
pymupdf>=1.23.0      # PDF 읽기 및 텍스트 추출
pdfplumber>=0.10.0   # 테이블 및 구조 분석
Pillow>=10.0.0       # 이미지 처리
click>=8.1.0         # CLI 인터페이스
pyyaml>=6.0          # 설정 파일 처리
tqdm>=4.65.0         # 진행률 표시
```

## 🛠️ 상세 사용법

### CLI 명령어

#### 기본 명령어
```bash
# 도움말 확인
pdf2md --help
pdf2md convert --help

# 버전 정보
pdf2md version

# 사용 가능한 프리셋 목록
pdf2md list-presets
```

#### 변환 옵션
```bash
# 이미지 추출 및 저장
pdf2md convert input.pdf output.md --extract-images

# 특정 인코딩 사용
pdf2md convert input.pdf output.md --encoding utf-16

# 이미지 형식 지정
pdf2md convert input.pdf output.md --image-format jpeg

# 조용한 모드 (최소한의 출력)
pdf2md convert input.pdf output.md --quiet

# 드라이런 (실제 변환 없이 미리보기)
pdf2md convert input.pdf output.md --dry-run
```

#### 설정 파일 사용
```bash
# 샘플 설정 파일 생성
pdf2md create-config my_config.yaml

# 설정 파일 사용
pdf2md convert input.pdf output.md --config my_config.yaml
```

### 프리셋 시스템

#### GitHub 프리셋
```bash
pdf2md convert document.pdf output.md --preset github
```
- 목차(TOC) 자동 생성
- 제목 ID 추가
- GitHub Flavored Markdown 스타일

#### 문서화 프리셋
```bash
pdf2md convert document.pdf output.md --preset documentation
```
- 상세한 메타데이터 포함
- 긴 줄 길이 (100자)
- 처리 정보 포함

#### 최소 프리셋
```bash
pdf2md convert document.pdf output.md --preset minimal
```
- 빠른 변환을 위한 최소 설정
- 이미지 추출 비활성화
- 메타데이터 최소화

#### 출판 프리셋
```bash
pdf2md convert document.pdf output.md --preset publishing
```
- 고품질 이미지 (90% 품질)
- 최적화된 줄 길이 (80자)
- 유니코드 정규화

### 설정 파일 예제

```yaml
# config.yaml
conversion:
  title_font_threshold: 1.2
  extract_images: true
  merge_paragraphs: false
  table_detection: true

output:
  encoding: utf-8
  image_format: png
  create_output_dir: true

markdown:
  heading:
    max_level: 6
    add_toc: true
    heading_ids: true
  
  paragraph:
    max_line_length: 80
    preserve_line_breaks: false
  
  table:
    format_type: standard
    align_columns: true
  
  image:
    extract_images: true
    max_width: 800
    quality: 85
```

## 🔌 Python API

### 기본 사용법

```python
from pdf_to_markdown import (
    convert_pdf, 
    convert_directory, 
    create_config,
    PDFToMarkdownConverter
)

# 1. 간단한 변환
result = convert_pdf('input.pdf', 'output.md')
print(f"성공: {result.success}")

# 2. 설정을 사용한 변환
converter = PDFToMarkdownConverter.from_preset('github')
result = converter.convert_file('input.pdf', 'output.md')

# 3. 일괄 처리
results = convert_directory('pdf_folder/', 'md_folder/')
success_count = sum(1 for r in results if r.success)
print(f"{success_count}/{len(results)} 파일 변환 완료")
```

### 고급 사용법

```python
from pdf_to_markdown.config import AppConfig, ConfigManager
from pdf_to_markdown.converter import PDFToMarkdownConverter

# 설정 관리자 사용
config_manager = ConfigManager()

# 사용자 정의 설정
config = config_manager.get_default_config()
config.conversion.extract_images = True
config.markdown.heading.add_toc = True

# 변환기 생성 및 사용
converter = PDFToMarkdownConverter(config)
result = converter.convert_file('input.pdf', 'output.md')

# 통계 확인
stats = converter.get_stats()
print(f"성공률: {stats['success_rate']:.1f}%")
print(f"평균 처리 시간: {stats['average_processing_time']:.2f}초")
```

### 에러 처리

```python
from pdf_to_markdown import convert_pdf
from pdf_to_markdown.exceptions import (
    PDFProcessingError,
    ConfigurationError,
    FileAccessError
)

try:
    result = convert_pdf('input.pdf', 'output.md')
    
    if not result.success:
        print(f"변환 실패: {result.error_message}")
        
except PDFProcessingError as e:
    print(f"PDF 처리 오류: {e}")
except FileAccessError as e:
    print(f"파일 접근 오류: {e}")
except Exception as e:
    print(f"예상치 못한 오류: {e}")
```

## 🧪 개발 및 테스트

### 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/yourusername/pdf-to-markdown.git
cd pdf-to-markdown

# 개발 의존성 설치
make install-dev

# Pre-commit 훅 설정
make setup-hooks
```

### 코드 품질 관리

```bash
# 코드 포맷팅
make format

# 린팅 실행
make lint

# 테스트 실행
make test

# 커버리지 포함 테스트
make test-cov

# 모든 품질 검사
make check
```

### 테스트 실행

```bash
# 전체 테스트
pytest

# 특정 모듈 테스트
pytest tests/test_config.py

# 커버리지 리포트
pytest --cov=src/pdf_to_markdown --cov-report=html
```

## 📊 성능 지표

### 벤치마크 결과
- **처리 속도**: 평균 0.5-2초/페이지
- **메모리 사용량**: 일반적으로 100-300MB
- **지원 파일 크기**: 최대 500MB (메모리에 따라 변동)

### 최적화 팁
1. **큰 파일**: `--batch` 옵션으로 메모리 효율성 향상
2. **빠른 변환**: `--preset minimal` 사용
3. **고품질**: `--preset publishing` 사용

## 🐛 문제 해결

### 자주 발생하는 문제

#### 1. PDF 파일을 읽을 수 없음
```bash
# 해결책: 파일 권한 확인
ls -la input.pdf

# 다른 위치로 파일 복사 후 재시도
cp input.pdf temp.pdf
pdf2md convert temp.pdf output.md
```

#### 2. 메모리 부족 오류
```bash
# 해결책: 최소 프리셋 사용
pdf2md convert large_file.pdf output.md --preset minimal

# 또는 배치 처리 사용
pdf2md convert large_file.pdf output.md --batch
```

#### 3. 이미지가 추출되지 않음
```bash
# 해결책: 이미지 추출 명시적 활성화
pdf2md convert input.pdf output.md --extract-images

# 설정 파일에서 확인
pdf2md create-config config.yaml
# config.yaml 편집 후
pdf2md convert input.pdf output.md --config config.yaml
```

### 로그 확인

```bash
# 상세 로그로 문제 진단
pdf2md convert input.pdf output.md --verbose --verbose

# 로그 파일 저장
pdf2md convert input.pdf output.md -vv 2> debug.log
```

## 🤝 기여하기

### 기여 방법
1. 저장소 포크
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

### 개발 가이드라인
- **코드 스타일**: Black, isort 사용
- **타입 힌트**: 모든 함수에 타입 힌트 추가
- **테스트**: 새 기능에 대한 테스트 작성
- **문서화**: 한국어로 주석 및 문서 작성

## 📜 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- **PyMuPDF**: PDF 처리의 핵심 라이브러리
- **pdfplumber**: 테이블 및 구조 분석
- **Click**: 사용자 친화적인 CLI 인터페이스
- **모든 기여자들**: 이 프로젝트를 더 좋게 만들어 주신 분들

## 📞 지원 및 연락

- **이슈 리포트**: [GitHub Issues](https://github.com/yourusername/pdf-to-markdown/issues)
- **기능 요청**: [GitHub Discussions](https://github.com/yourusername/pdf-to-markdown/discussions)
- **이메일**: your.email@example.com

---

📚 **더 많은 정보**: [Wiki](https://github.com/yourusername/pdf-to-markdown/wiki) | [API 문서](https://pdf-to-markdown.readthedocs.io/) | [예제 모음](examples/)

Made with ❤️ in Korea 🇰🇷 