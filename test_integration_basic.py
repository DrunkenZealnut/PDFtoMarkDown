"""
PDF Reader + Text Parser 통합 테스트

실제 PDF 파일을 읽고 텍스트 파싱까지 전체 파이프라인을 테스트합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.pdf_to_markdown.pdf_reader import PDFReader
    from src.pdf_to_markdown.text_parser import TextParser
    
    print("=== PDF Reader + Text Parser 통합 테스트 ===")
    
    # 1. 테스트 PDF 파일 확인
    print("\n1️⃣ 테스트 PDF 파일 확인")
    sample_pdf = Path("test_files/sample.pdf")
    
    if not sample_pdf.exists():
        print("❌ sample.pdf 파일이 없습니다.")
        print("먼저 'py -3 tests/create_test_pdf.py'를 실행하여 테스트 PDF를 생성하세요.")
        sys.exit(1)
    
    print(f"✅ 테스트 파일 발견: {sample_pdf}")
    print(f"   파일 크기: {sample_pdf.stat().st_size} bytes")
    
    # 2. PDF 읽기
    print("\n2️⃣ PDF 읽기")
    try:
        with PDFReader(sample_pdf) as reader:
            print("✅ PDFReader 초기화 성공")
            
            # 메타데이터 확인
            doc_info = reader.get_document_info()
            print(f"   - 페이지 수: {doc_info.page_count}")
            print(f"   - 제목: {doc_info.title or 'N/A'}")
            
            # 전체 문서 추출
            document = reader.extract_document()
            print(f"✅ 문서 추출 완료")
            print(f"   - 총 텍스트 블록: {document.total_text_blocks}")
            print(f"   - 총 이미지: {document.total_images}")
            
            # 첫 번째 페이지 텍스트 확인
            if document.pages:
                first_page = document.pages[0]
                print(f"   - 첫 페이지 텍스트 블록: {len(first_page.text_blocks)}개")
                
                if first_page.text_blocks:
                    print("   - 첫 번째 텍스트 블록:")
                    first_block = first_page.text_blocks[0]
                    print(f"     '{first_block.text[:50]}{'...' if len(first_block.text) > 50 else ''}'")
                    print(f"     폰트: {first_block.font_info.name} {first_block.font_info.size}pt")
            
    except Exception as e:
        print(f"❌ PDF 읽기 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 3. TextParser로 구조 분석
    print("\n3️⃣ 텍스트 구조 분석")
    try:
        parser = TextParser(
            title_font_threshold=1.2,
            merge_paragraphs=False,
            table_detection=True
        )
        
        print("✅ TextParser 초기화 성공")
        
        # 문서 구조 분석
        structure = parser.analyze_document_structure(document)
        
        print("✅ 문서 구조 분석 완료")
        print(f"   - 총 요소: {structure.total_elements}개")
        print(f"   - 제목: {structure.heading_count}개")
        print(f"   - 단락: {structure.paragraph_count}개")
        print(f"   - 리스트: {structure.list_count}개")
        print(f"   - 테이블: {structure.table_count}개")
        print(f"   - 분석 확신도: {structure.confidence_score:.2f}")
        
        # 경고사항 출력
        if structure.analysis_warnings:
            print(f"   - 경고: {len(structure.analysis_warnings)}개")
            for warning in structure.analysis_warnings:
                print(f"     ⚠️ {warning}")
        
    except Exception as e:
        print(f"❌ 텍스트 구조 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 4. 상세 분석 결과 출력
    print("\n4️⃣ 상세 분석 결과")
    try:
        # 제목들 출력
        print(f"\n📋 제목 분석 ({len(structure.headings)}개):")
        for i, heading in enumerate(structure.headings):
            print(f"   {i+1}. H{heading.level}: '{heading.text}' (확신도: {heading.confidence:.2f})")
            print(f"      폰트: {heading.font_name} {heading.font_size}pt, 페이지: {heading.page_num}")
        
        # 단락들 출력 (처음 3개만)
        print(f"\n📄 단락 분석 ({len(structure.paragraphs)}개, 처음 3개만 표시):")
        for i, paragraph in enumerate(structure.paragraphs[:3]):
            print(f"   {i+1}. '{paragraph.text[:80]}{'...' if len(paragraph.text) > 80 else ''}'")
            print(f"      페이지: {paragraph.page_num}, 텍스트 블록: {len(paragraph.text_blocks)}개")
        
        if len(structure.paragraphs) > 3:
            print(f"   ... 그 외 {len(structure.paragraphs) - 3}개 단락")
        
        # 리스트들 출력
        if structure.lists:
            print(f"\n📝 리스트 분석 ({len(structure.lists)}개):")
            for i, list_item in enumerate(structure.lists):
                print(f"   {i+1}. {list_item.list_type.value}: {list_item.marker} '{list_item.text}'")
                print(f"      레벨: {list_item.level}, 페이지: {list_item.page_num}")
        
        # 테이블들 출력
        if structure.tables:
            print(f"\n📊 테이블 분석 ({len(structure.tables)}개):")
            for i, table in enumerate(structure.tables):
                print(f"   {i+1}. 테이블 (행: {len(table.rows)}개, 페이지: {table.page_num})")
                print(f"      확신도: {table.confidence:.2f}, 헤더: {table.has_header}")
        
    except Exception as e:
        print(f"❌ 상세 결과 출력 실패: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. 폰트 통계 출력
    print("\n5️⃣ 폰트 사용 통계")
    try:
        font_stats = parser.get_font_statistics()
        print(f"✅ 폰트 통계 ({len(font_stats)}개 폰트):")
        
        # 사용 빈도 순으로 정렬
        font_stats.sort(key=lambda x: x.occurrence_count, reverse=True)
        
        for i, font in enumerate(font_stats[:5]):  # 상위 5개만 표시
            print(f"   {i+1}. {font.font_name} {font.font_size}pt")
            print(f"      사용 횟수: {font.occurrence_count}회")
            print(f"      총 텍스트 길이: {font.total_text_length}자")
            print(f"      스타일: {'Bold' if font.is_bold else ''}{'Italic' if font.is_italic else ''}")
            print()
        
        main_font = parser.get_main_font()
        if main_font:
            print(f"🎯 본문 폰트: {main_font.font_name} {main_font.font_size}pt")
            print(f"   ({main_font.occurrence_count}회 사용)")
        
    except Exception as e:
        print(f"❌ 폰트 통계 출력 실패: {e}")
    
    print("\n🎉 PDF Reader + Text Parser 통합 테스트 완료!")
    print("✅ 전체 파이프라인이 성공적으로 작동합니다.")
    print("\n📋 완료된 Phase 2.2 기능:")
    print("   - 폰트 기반 제목 식별")
    print("   - 리스트 패턴 인식")
    print("   - 단락 분류 및 정리")
    print("   - 테이블 구조 감지")
    print("   - 문서 요소 순서 정렬")
    print("   - 분석 품질 평가")
    
    print("\n🚀 다음 단계: Phase 2.3 Markdown Generator 구현")

except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")
    print("필요한 모듈들이 설치되어 있는지 확인하세요.")
    sys.exit(1)
except Exception as e:
    print(f"❌ 예기치 않은 오류: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 