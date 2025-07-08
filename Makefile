# PDF to Markdown 변환기 - 개발 및 배포 명령어
.PHONY: help install install-dev clean format lint test test-cov build upload setup-hooks run-hooks

# 기본 도움말
help:
	@echo "📋 사용 가능한 명령어:"
	@echo ""
	@echo "🔧 개발 환경 설정:"
	@echo "  install      - 패키지 설치"
	@echo "  install-dev  - 개발 의존성 포함 설치"
	@echo "  setup-hooks  - pre-commit 훅 설정"
	@echo ""
	@echo "🧹 코드 품질:"
	@echo "  format       - 코드 포맷팅 (black, isort)"
	@echo "  lint         - 코드 린팅 (flake8, mypy)"
	@echo "  run-hooks    - pre-commit 훅 실행"
	@echo ""
	@echo "🧪 테스트:"
	@echo "  test         - 단위 테스트 실행"
	@echo "  test-cov     - 커버리지 포함 테스트"
	@echo ""
	@echo "📦 빌드 및 배포:"
	@echo "  build        - 배포 패키지 빌드"
	@echo "  upload       - PyPI 업로드"
	@echo "  clean        - 빌드 파일 정리"

# 패키지 설치
install:
	@echo "📦 패키지 설치 중..."
	pip install -e .

# 개발 환경 설치
install-dev:
	@echo "🔧 개발 환경 설치 중..."
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt

# Pre-commit 훅 설정
setup-hooks:
	@echo "🪝 Pre-commit 훅 설정 중..."
	pre-commit install
	pre-commit autoupdate

# Pre-commit 훅 실행
run-hooks:
	@echo "🔍 Pre-commit 훅 실행 중..."
	pre-commit run --all-files

# 코드 포맷팅
format:
	@echo "✨ 코드 포맷팅 중..."
	black src/ tests/ main.py test_complete_workflow.py
	isort src/ tests/ main.py test_complete_workflow.py

# 코드 린팅
lint:
	@echo "🔍 코드 린팅 중..."
	flake8 src/ tests/ main.py test_complete_workflow.py --max-line-length=88 --extend-ignore=E203,W503
	mypy src/ --ignore-missing-imports

# 단위 테스트
test:
	@echo "🧪 단위 테스트 실행 중..."
	pytest tests/ -v

# 커버리지 포함 테스트
test-cov:
	@echo "📊 커버리지 테스트 실행 중..."
	pytest tests/ --cov=src/pdf_to_markdown --cov-report=term-missing --cov-report=html

# 빌드 파일 정리
clean:
	@echo "🧹 빌드 파일 정리 중..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# 배포 패키지 빌드
build: clean
	@echo "📦 배포 패키지 빌드 중..."
	python -m build

# PyPI 업로드 (테스트)
upload-test: build
	@echo "🚀 TestPyPI 업로드 중..."
	twine upload --repository testpypi dist/*

# PyPI 업로드 (프로덕션)
upload: build
	@echo "🚀 PyPI 업로드 중..."
	twine upload dist/*

# 전체 개발 환경 설정
dev-setup: install-dev setup-hooks
	@echo "✅ 개발 환경 설정 완료!"

# 코드 품질 체크 (CI용)
check: format lint test-cov
	@echo "✅ 모든 품질 검사 통과!"

# 로컬 테스트 실행
demo:
	@echo "🎬 데모 실행 중..."
	python main.py convert test_files/sample.pdf demo_output.md --verbose
	@echo "📄 결과 파일: demo_output.md" 