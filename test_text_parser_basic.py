"""
Text Parser 기본 기능 테스트

TextParser 클래스의 핵심 기능들을 단계별로 테스트합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.pdf_to_markdown.text_parser import TextParser
    from src.pdf_to_markdown.data_models import TextBlock, FontInfo, FontStyle, DocumentContent, PageInfo
    from src.pdf_to_markdown.text_structures import ElementType, ListType
    
    print("=== Text Parser 기본 테스트 ===")
    
    # 1. TextParser 초기화 테스트
    print("\n1️⃣ TextParser 초기화 테스트")
    try:
        parser = TextParser(
            title_font_threshold=1.2,
            merge_paragraphs=False,
            table_detection=True
        )
        print("✅ TextParser 초기화 성공")
        print(f"   - 제목 폰트 임계값: {parser.title_font_threshold}")
        print(f"   - 단락 병합: {parser.merge_paragraphs}")
        print(f"   - 테이블 감지: {parser.table_detection}")
    except Exception as e:
        print(f"❌ TextParser 초기화 실패: {e}")
        sys.exit(1)
    
    # 2. 테스트용 텍스트 블록 생성
    print("\n2️⃣ 테스트 데이터 생성")
    try:
        # 폰트 정보들
        title_font = FontInfo("Arial", 18.0, FontStyle.BOLD, (0, 0, 0))
        subtitle_font = FontInfo("Arial", 14.0, FontStyle.BOLD, (0, 0, 0))
        body_font = FontInfo("Arial", 12.0, FontStyle.NORMAL, (0, 0, 0))
        
        # 텍스트 블록들
        text_blocks = [
            # 제목
            TextBlock(
                text="주요 제목",
                bbox=(50, 700, 200, 720),
                font_info=title_font,
                page_num=1
            ),
            # 부제목
            TextBlock(
                text="부제목 예시",
                bbox=(50, 650, 150, 665),
                font_info=subtitle_font,
                page_num=1
            ),
            # 본문
            TextBlock(
                text="이것은 본문 텍스트입니다. 일반적인 단락의 예시입니다.",
                bbox=(50, 600, 350, 615),
                font_info=body_font,
                page_num=1
            ),
            # 리스트
            TextBlock(
                text="• 첫 번째 리스트 항목",
                bbox=(70, 570, 250, 585),
                font_info=body_font,
                page_num=1
            ),
            TextBlock(
                text="• 두 번째 리스트 항목",
                bbox=(70, 550, 250, 565),
                font_info=body_font,
                page_num=1
            ),
            TextBlock(
                text="1. 번호가 있는 리스트",
                bbox=(70, 520, 220, 535),
                font_info=body_font,
                page_num=1
            ),
            # 추가 본문
            TextBlock(
                text="마지막 단락입니다.",
                bbox=(50, 480, 180, 495),
                font_info=body_font,
                page_num=1
            )
        ]
        
        print(f"✅ {len(text_blocks)}개 테스트 텍스트 블록 생성")
        for i, block in enumerate(text_blocks):
            print(f"   {i+1}. {block.text[:30]}... (폰트: {block.font_info.size}pt)")
        
    except Exception as e:
        print(f"❌ 테스트 데이터 생성 실패: {e}")
        sys.exit(1)
    
    # 3. 폰트 통계 분석 테스트
    print("\n3️⃣ 폰트 통계 분석 테스트")
    try:
        parser._analyze_font_statistics(text_blocks)
        
        print("✅ 폰트 통계 분석 완료")
        print(f"   - 폰트 종류: {len(parser.get_font_statistics())}개")
        
        main_font = parser.get_main_font()
        if main_font:
            print(f"   - 본문 폰트: {main_font.font_name} {main_font.font_size}pt")
            print(f"   - 본문 폰트 사용 횟수: {main_font.occurrence_count}회")
        
    except Exception as e:
        print(f"❌ 폰트 통계 분석 실패: {e}")
    
    # 4. 제목 식별 테스트
    print("\n4️⃣ 제목 식별 테스트")
    try:
        headings = parser.identify_headings(text_blocks)
        
        print(f"✅ {len(headings)}개 제목 식별됨")
        for heading in headings:
            print(f"   - H{heading.level}: {heading.text} (확신도: {heading.confidence:.2f})")
        
    except Exception as e:
        print(f"❌ 제목 식별 실패: {e}")
    
    # 5. 단락 식별 테스트
    print("\n5️⃣ 단락 식별 테스트")
    try:
        headings = parser.identify_headings(text_blocks)
        paragraphs = parser.identify_paragraphs(text_blocks, headings)
        
        print(f"✅ {len(paragraphs)}개 단락 식별됨")
        for i, paragraph in enumerate(paragraphs):
            print(f"   {i+1}. {paragraph.text[:50]}{'...' if len(paragraph.text) > 50 else ''}")
        
    except Exception as e:
        print(f"❌ 단락 식별 실패: {e}")
    
    # 6. 리스트 식별 테스트
    print("\n6️⃣ 리스트 식별 테스트")
    try:
        lists = parser.identify_lists(text_blocks)
        
        print(f"✅ {len(lists)}개 리스트 항목 식별됨")
        for list_item in lists:
            print(f"   - {list_item.list_type.value}: {list_item.marker} {list_item.text}")
        
    except Exception as e:
        print(f"❌ 리스트 식별 실패: {e}")
    
    # 7. 전체 문서 구조 분석 테스트
    print("\n7️⃣ 전체 문서 구조 분석 테스트")
    try:
        # DocumentContent 생성
        page_info = PageInfo(
            page_num=1,
            width=612.0,
            height=792.0,
            rotation=0,
            text_blocks=text_blocks,
            images=[]
        )
        
        # Mock metadata (실제로는 PDFReader에서 제공)
        from src.pdf_to_markdown.data_models import DocumentMetadata
        
        metadata = DocumentMetadata(
            title="테스트 문서",
            author="Test",
            page_count=1
        )
        
        document = DocumentContent(
            metadata=metadata,
            pages=[page_info],
            total_text_blocks=len(text_blocks),
            total_images=0
        )
        
        # 문서 구조 분석
        structure = parser.analyze_document_structure(document)
        
        print("✅ 문서 구조 분석 완료")
        print(f"   - 총 요소: {structure.total_elements}개")
        print(f"   - 제목: {structure.heading_count}개")
        print(f"   - 단락: {structure.paragraph_count}개") 
        print(f"   - 리스트: {structure.list_count}개")
        print(f"   - 테이블: {structure.table_count}개")
        print(f"   - 분석 확신도: {structure.confidence_score:.2f}")
        
        if structure.analysis_warnings:
            print(f"   - 경고: {len(structure.analysis_warnings)}개")
            for warning in structure.analysis_warnings:
                print(f"     ⚠️ {warning}")
        
    except Exception as e:
        print(f"❌ 문서 구조 분석 실패: {e}")
        import traceback
        traceback.print_exc()
    
    # 8. 리스트 패턴 매칭 테스트
    print("\n8️⃣ 리스트 패턴 매칭 테스트")
    try:
        test_patterns = [
            "• 불릿 포인트",
            "- 대시 리스트",
            "* 별표 리스트",
            "+ 플러스 리스트",
            "1. 번호 리스트",
            "2) 괄호 번호",
            "(3) 양괄호 번호",
            "a. 소문자 알파벳",
            "A. 대문자 알파벳",
            "i. 로마 숫자 소문자",
            "II. 로마 숫자 대문자"
        ]
        
        print("✅ 리스트 패턴 매칭 테스트")
        
        import re
        for text in test_patterns:
            found = False
            for list_type, patterns in parser.list_patterns.items():
                for pattern in patterns:
                    match = re.match(pattern, text)
                    if match:
                        marker = match.group(0).strip()
                        content = text[len(match.group(0)):].strip()
                        print(f"   ✅ '{text}' → {list_type.value} (마커: '{marker}')")
                        found = True
                        break
                if found:
                    break
            
            if not found:
                print(f"   ❌ '{text}' → 패턴 매칭 실패")
        
    except Exception as e:
        print(f"❌ 리스트 패턴 매칭 테스트 실패: {e}")
    
    print("\n🎉 Text Parser 기본 테스트 완료!")
    print("\n다음 단계: Markdown Generator 모듈 구현")

except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")
    print("src/pdf_to_markdown/ 디렉토리와 관련 파일들이 있는지 확인하세요.")
    sys.exit(1)
except Exception as e:
    print(f"❌ 예기치 않은 오류: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 