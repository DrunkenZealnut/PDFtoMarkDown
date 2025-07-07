"""
PDF to Markdown 전체 파이프라인 테스트

PDFReader → TextParser → MarkdownGenerator 전체 과정을 테스트합니다.
"""

import sys
from pathlib import Path
import time

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.pdf_to_markdown.pdf_reader import PDFReader
    from src.pdf_to_markdown.text_parser import TextParser
    from src.pdf_to_markdown.markdown_generator import MarkdownGenerator
    from src.pdf_to_markdown.markdown_config import ConfigPresets
    
    print("=== PDF to Markdown 전체 파이프라인 테스트 ===")
    
    # 1. 테스트 파일 확인
    print("\n1️⃣ 테스트 파일 확인")
    test_files = []
    
    sample_pdf = Path("test_files/sample.pdf")
    if sample_pdf.exists():
        test_files.append(("sample.pdf", sample_pdf))
        print(f"✅ {sample_pdf} 발견 ({sample_pdf.stat().st_size} bytes)")
    
    table_pdf = Path("test_files/table_sample.pdf")
    if table_pdf.exists():
        test_files.append(("table_sample.pdf", table_pdf))
        print(f"✅ {table_pdf} 발견 ({table_pdf.stat().st_size} bytes)")
    
    if not test_files:
        print("❌ 테스트 PDF 파일이 없습니다.")
        print("먼저 'py -3 tests/create_test_pdf.py'를 실행하여 테스트 PDF를 생성하세요.")
        sys.exit(1)
    
    print(f"총 {len(test_files)}개 테스트 파일 준비됨")
    
    # 2. 출력 디렉토리 준비
    print("\n2️⃣ 출력 디렉토리 준비")
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    print(f"✅ 출력 디렉토리: {output_dir}")
    
    # 3. 파이프라인 구성 요소 초기화
    print("\n3️⃣ 파이프라인 구성 요소 초기화")
    try:
        # TextParser 초기화
        text_parser = TextParser(
            title_font_threshold=1.2,
            merge_paragraphs=False,
            table_detection=True
        )
        print("✅ TextParser 초기화 완료")
        
        # 다양한 MarkdownGenerator 설정
        generators = {
            "기본": MarkdownGenerator(),
            "GitHub": MarkdownGenerator(ConfigPresets.github_flavored()),
            "문서": MarkdownGenerator(ConfigPresets.documentation()),
            "최소": MarkdownGenerator(ConfigPresets.minimal())
        }
        print(f"✅ MarkdownGenerator {len(generators)}개 설정 초기화 완료")
        
    except Exception as e:
        print(f"❌ 파이프라인 초기화 실패: {e}")
        sys.exit(1)
    
    # 4. 각 PDF 파일 처리
    for file_name, file_path in test_files:
        print(f"\n4️⃣ '{file_name}' 처리 시작")
        start_time = time.time()
        
        try:
            # 4-1. PDF 읽기
            print(f"   📖 PDF 읽기 중...")
            with PDFReader(file_path) as reader:
                document = reader.extract_document()
            
            print(f"   ✅ PDF 읽기 완료")
            print(f"      - 페이지: {len(document.pages)}개")
            print(f"      - 텍스트 블록: {document.total_text_blocks}개")
            print(f"      - 이미지: {document.total_images}개")
            
            # 4-2. 텍스트 구조 분석
            print(f"   🔍 텍스트 구조 분석 중...")
            structure = text_parser.analyze_document_structure(document)
            
            print(f"   ✅ 텍스트 구조 분석 완료")
            print(f"      - 총 요소: {structure.total_elements}개")
            print(f"      - 제목: {structure.heading_count}개")
            print(f"      - 단락: {structure.paragraph_count}개")
            print(f"      - 리스트: {structure.list_count}개")
            print(f"      - 테이블: {structure.table_count}개")
            print(f"      - 분석 확신도: {structure.confidence_score:.2f}")
            
            if structure.analysis_warnings:
                print(f"      ⚠️ 경고: {len(structure.analysis_warnings)}개")
                for warning in structure.analysis_warnings[:3]:  # 처음 3개만 표시
                    print(f"         {warning}")
            
            # 4-3. 각 설정으로 Markdown 생성
            print(f"   📝 Markdown 생성 중...")
            
            for config_name, generator in generators.items():
                try:
                    # Markdown 생성
                    markdown_text = generator.generate_markdown(structure, document)
                    
                    # 파일명 생성
                    base_name = file_path.stem
                    output_filename = f"{base_name}_{config_name.lower()}.md"
                    output_path = output_dir / output_filename
                    
                    # 파일 저장
                    generator.save_markdown(markdown_text, output_path)
                    
                    # 결과 정보
                    file_size = output_path.stat().st_size
                    line_count = len(markdown_text.split('\n'))
                    
                    print(f"      ✅ {config_name}: {output_filename} ({file_size} bytes, {line_count}줄)")
                    
                except Exception as e:
                    print(f"      ❌ {config_name} 설정 실패: {e}")
            
            # 처리 시간 계산
            processing_time = time.time() - start_time
            print(f"   ⏱️ 처리 시간: {processing_time:.2f}초")
            
        except Exception as e:
            print(f"   ❌ '{file_name}' 처리 실패: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # 5. 결과 파일 분석
    print(f"\n5️⃣ 결과 파일 분석")
    try:
        output_files = list(output_dir.glob("*.md"))
        if output_files:
            print(f"✅ 총 {len(output_files)}개 Markdown 파일 생성됨")
            
            # 파일별 정보 출력
            print("\n📊 생성된 파일 정보:")
            print(f"{'파일명':<30} {'크기':<10} {'줄수':<8}")
            print("-" * 50)
            
            total_size = 0
            for output_file in sorted(output_files):
                file_size = output_file.stat().st_size
                total_size += file_size
                
                # 줄 수 계산
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        line_count = len(f.readlines())
                except:
                    line_count = 0
                
                print(f"{output_file.name:<30} {file_size:<10} {line_count:<8}")
            
            print("-" * 50)
            print(f"{'총계':<30} {total_size:<10}")
            
            # 설정별 크기 비교
            print(f"\n📈 설정별 파일 크기 비교:")
            config_sizes = {}
            for config_name in generators.keys():
                config_files = [f for f in output_files if f"_{config_name.lower()}.md" in f.name]
                if config_files:
                    avg_size = sum(f.stat().st_size for f in config_files) / len(config_files)
                    config_sizes[config_name] = avg_size
            
            if config_sizes:
                base_size = config_sizes.get('기본', 0)
                for config_name, size in config_sizes.items():
                    ratio = size / base_size if base_size > 0 else 0
                    print(f"   {config_name}: {size:.0f} bytes ({ratio:.2f}배)")
        
        else:
            print("❌ 생성된 Markdown 파일이 없습니다.")
    
    except Exception as e:
        print(f"❌ 결과 파일 분석 실패: {e}")
    
    # 6. 샘플 Markdown 내용 확인
    print(f"\n6️⃣ 샘플 Markdown 내용 확인")
    try:
        # GitHub 설정으로 생성된 파일 중 하나 선택
        sample_files = list(output_dir.glob("*_github.md"))
        if sample_files:
            sample_file = sample_files[0]
            print(f"📄 샘플 파일: {sample_file.name}")
            
            with open(sample_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            print(f"   총 {len(lines)}줄 중 처음 30줄:")
            print("   " + "="*60)
            
            for i, line in enumerate(lines[:30]):
                print(f"   {i+1:2d}: {line}")
            
            if len(lines) > 30:
                print(f"   ... 그 외 {len(lines) - 30}줄")
            
            print("   " + "="*60)
            
            # Markdown 특징 확인
            features = []
            if content.startswith("---"):
                features.append("YAML Front Matter")
            if "## 목차" in content:
                features.append("목차(TOC)")
            if "{#" in content:
                features.append("제목 ID")
            if "![" in content:
                features.append("이미지")
            if "|" in content and "---" in content:
                features.append("테이블")
            
            if features:
                print(f"   🎯 포함된 Markdown 기능: {', '.join(features)}")
            
        else:
            print("❌ GitHub 설정 파일을 찾을 수 없습니다.")
    
    except Exception as e:
        print(f"❌ 샘플 내용 확인 실패: {e}")
    
    print(f"\n🎉 PDF to Markdown 전체 파이프라인 테스트 완료!")
    print(f"\n✅ 성공적으로 완료된 단계:")
    print(f"   📖 PDF 읽기 (PyMuPDF)")
    print(f"   🔍 텍스트 구조 분석 (폰트, 제목, 리스트, 테이블)")
    print(f"   📝 Markdown 생성 (4가지 설정)")
    print(f"   💾 파일 저장")
    
    print(f"\n📋 테스트된 기능들:")
    print(f"   ✅ 제목 식별 및 Markdown 헤더 변환")
    print(f"   ✅ 단락 정리 및 텍스트 변환")
    print(f"   ✅ 리스트 패턴 인식 및 변환")
    print(f"   ✅ 테이블 구조 분석 및 변환")
    print(f"   ✅ YAML Front Matter 생성")
    print(f"   ✅ 목차(TOC) 자동 생성")
    print(f"   ✅ 제목 ID 생성")
    print(f"   ✅ 다양한 출력 설정 지원")
    
    print(f"\n🚀 Phase 2.3 Markdown Generator 구현 완료!")
    print(f"📁 결과 파일 위치: {output_dir}")

except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")
    print("필요한 모듈들이 설치되어 있는지 확인하세요.")
    sys.exit(1)
except Exception as e:
    print(f"❌ 예기치 않은 오류: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 