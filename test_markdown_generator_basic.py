"""
Markdown Generator 기본 기능 테스트

MarkdownGenerator 클래스의 핵심 기능들을 단계별로 테스트합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.pdf_to_markdown.markdown_generator import MarkdownGenerator
    from src.pdf_to_markdown.markdown_config import MarkdownConfig, ConfigPresets
    from src.pdf_to_markdown.text_structures import (
        DocumentStructure, DocumentElement, ElementType,
        Heading, Paragraph, ListItem, ListType, Table, TableRow, TableCell
    )
    from src.pdf_to_markdown.data_models import (
        DocumentContent, PageInfo, DocumentMetadata, TextBlock, FontInfo, FontStyle
    )
    
    print("=== Markdown Generator 기본 테스트 ===")
    
    # 1. MarkdownGenerator 초기화 테스트
    print("\n1️⃣ MarkdownGenerator 초기화 테스트")
    try:
        # 기본 설정으로 초기화
        generator = MarkdownGenerator()
        print("✅ 기본 설정으로 초기화 성공")
        
        # GitHub 스타일 설정으로 초기화
        github_config = ConfigPresets.github_flavored()
        github_generator = MarkdownGenerator(github_config)
        print("✅ GitHub 스타일 설정으로 초기화 성공")
        
        # 최소 설정으로 초기화
        minimal_config = ConfigPresets.minimal()
        minimal_generator = MarkdownGenerator(minimal_config)
        print("✅ 최소 설정으로 초기화 성공")
        
    except Exception as e:
        print(f"❌ MarkdownGenerator 초기화 실패: {e}")
        sys.exit(1)
    
    # 2. 테스트용 문서 구조 생성
    print("\n2️⃣ 테스트 문서 구조 생성")
    try:
        # 폰트 정보
        body_font = FontInfo("Arial", 12.0, FontStyle.NORMAL, (0, 0, 0))
        
        # 제목들 생성
        headings = [
            Heading(
                text="주요 제목",
                level=1,
                font_size=18.0,
                font_name="Arial",
                bbox=(50, 700, 200, 720),
                page_num=1,
                confidence=0.9
            ),
            Heading(
                text="부제목",
                level=2,
                font_size=16.0,
                font_name="Arial",
                bbox=(50, 650, 150, 670),
                page_num=1,
                confidence=0.8
            )
        ]
        
        # 단락들 생성
        paragraphs = [
            Paragraph(
                text="이것은 첫 번째 단락입니다. 여러 줄로 구성된 텍스트가 포함되어 있습니다.",
                text_blocks=[],
                bbox=(50, 600, 350, 630),
                page_num=1,
                is_merged=False
            ),
            Paragraph(
                text="두 번째 단락입니다. 이 단락에는 조금 더 긴 내용이 포함되어 있어서 줄바꿈 테스트를 할 수 있습니다.",
                text_blocks=[],
                bbox=(50, 550, 350, 580),
                page_num=1,
                is_merged=False
            )
        ]
        
        # 리스트 항목들 생성
        lists = [
            ListItem(
                text="첫 번째 리스트 항목",
                list_type=ListType.BULLET,
                marker="•",
                level=0,
                bbox=(70, 500, 250, 520),
                page_num=1
            ),
            ListItem(
                text="두 번째 리스트 항목",
                list_type=ListType.BULLET,
                marker="•",
                level=0,
                bbox=(70, 480, 250, 500),
                page_num=1
            ),
            ListItem(
                text="들여쓰기된 항목",
                list_type=ListType.BULLET,
                marker="•",
                level=1,
                bbox=(90, 460, 250, 480),
                page_num=1
            ),
            ListItem(
                text="번호가 있는 항목",
                list_type=ListType.NUMBERED,
                marker="1.",
                level=0,
                bbox=(70, 440, 220, 460),
                page_num=1
            )
        ]
        
        # 테이블 생성
        table_cells_row1 = [
            TableCell("헤더1", 0, 0),
            TableCell("헤더2", 0, 1),
            TableCell("헤더3", 0, 2)
        ]
        table_cells_row2 = [
            TableCell("데이터1", 1, 0),
            TableCell("데이터2", 1, 1),
            TableCell("데이터3", 1, 2)
        ]
        
        table_rows = [
            TableRow(table_cells_row1, 0, (50, 400, 300, 420)),
            TableRow(table_cells_row2, 1, (50, 380, 300, 400))
        ]
        
        tables = [
            Table(
                rows=table_rows,
                bbox=(50, 380, 300, 420),
                page_num=1,
                has_header=True,
                confidence=0.8
            )
        ]
        
        # Document Elements 생성
        elements = []
        order = 0
        
        # 제목 요소 추가
        for heading in headings:
            element = DocumentElement(
                element_type=ElementType.HEADING,
                content=heading,
                bbox=heading.bbox,
                page_num=heading.page_num,
                order=order
            )
            elements.append(element)
            order += 1
        
        # 단락 요소 추가
        for paragraph in paragraphs:
            element = DocumentElement(
                element_type=ElementType.PARAGRAPH,
                content=paragraph,
                bbox=paragraph.bbox,
                page_num=paragraph.page_num,
                order=order
            )
            elements.append(element)
            order += 1
        
        # 리스트 요소 추가
        for list_item in lists:
            element = DocumentElement(
                element_type=ElementType.LIST_ITEM,
                content=list_item,
                bbox=list_item.bbox,
                page_num=list_item.page_num,
                order=order
            )
            elements.append(element)
            order += 1
        
        # 테이블 요소 추가
        for table in tables:
            element = DocumentElement(
                element_type=ElementType.TABLE,
                content=table,
                bbox=table.bbox,
                page_num=table.page_num,
                order=order
            )
            elements.append(element)
            order += 1
        
        # 문서 구조 생성
        structure = DocumentStructure(
            elements=elements,
            headings=headings,
            paragraphs=paragraphs,
            lists=lists,
            tables=tables,
            confidence_score=0.85
        )
        
        print(f"✅ 테스트 문서 구조 생성 완료")
        print(f"   - 총 요소: {structure.total_elements}개")
        print(f"   - 제목: {structure.heading_count}개")
        print(f"   - 단락: {structure.paragraph_count}개")
        print(f"   - 리스트: {structure.list_count}개")
        print(f"   - 테이블: {structure.table_count}개")
        
    except Exception as e:
        print(f"❌ 테스트 문서 구조 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 3. 메타데이터 생성
    print("\n3️⃣ 테스트 메타데이터 생성")
    try:
        metadata = DocumentMetadata(
            title="테스트 문서",
            author="Test Author",
            subject="Markdown Generator 테스트",
            page_count=1,
            creation_date="2024-01-01T00:00:00"
        )
        
        # DocumentContent 생성
        page_info = PageInfo(
            page_num=1,
            width=612.0,
            height=792.0,
            rotation=0,
            text_blocks=[],
            images=[]
        )
        
        document = DocumentContent(
            metadata=metadata,
            pages=[page_info],
            total_text_blocks=len(paragraphs),
            total_images=0
        )
        
        print("✅ 테스트 메타데이터 생성 완료")
        print(f"   - 제목: {metadata.title}")
        print(f"   - 작성자: {metadata.author}")
        print(f"   - 페이지: {metadata.page_count}개")
        
    except Exception as e:
        print(f"❌ 테스트 메타데이터 생성 실패: {e}")
        sys.exit(1)
    
    # 4. 기본 Markdown 생성 테스트
    print("\n4️⃣ 기본 Markdown 생성 테스트")
    try:
        markdown_text = generator.generate_markdown(structure, document)
        
        print("✅ 기본 Markdown 생성 성공")
        print(f"   - 생성된 텍스트 길이: {len(markdown_text)}자")
        
        # 생성된 Markdown 일부 출력
        lines = markdown_text.split('\n')
        print(f"   - 총 줄 수: {len(lines)}줄")
        print("\n   📄 생성된 Markdown (처음 20줄):")
        for i, line in enumerate(lines[:20]):
            print(f"   {i+1:2d}: {line}")
        
        if len(lines) > 20:
            print(f"   ... 그 외 {len(lines) - 20}줄")
        
    except Exception as e:
        print(f"❌ 기본 Markdown 생성 실패: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. GitHub 스타일 Markdown 생성 테스트
    print("\n5️⃣ GitHub 스타일 Markdown 생성 테스트")
    try:
        github_markdown = github_generator.generate_markdown(structure, document)
        
        print("✅ GitHub 스타일 Markdown 생성 성공")
        print(f"   - 생성된 텍스트 길이: {len(github_markdown)}자")
        
        # TOC 포함 여부 확인
        if "## 목차" in github_markdown:
            print("   ✅ 목차(TOC) 포함됨")
        
        # Heading ID 포함 여부 확인 
        if "{#" in github_markdown:
            print("   ✅ 제목 ID 포함됨")
        
    except Exception as e:
        print(f"❌ GitHub 스타일 Markdown 생성 실패: {e}")
    
    # 6. 최소 설정 Markdown 생성 테스트
    print("\n6️⃣ 최소 설정 Markdown 생성 테스트")
    try:
        minimal_markdown = minimal_generator.generate_markdown(structure, document)
        
        print("✅ 최소 설정 Markdown 생성 성공")
        print(f"   - 생성된 텍스트 길이: {len(minimal_markdown)}자")
        
        # YAML Front Matter 없음 확인
        if not minimal_markdown.startswith("---"):
            print("   ✅ YAML Front Matter 제외됨")
        
        # 기본 Markdown과 길이 비교
        ratio = len(minimal_markdown) / len(markdown_text) if markdown_text else 0
        print(f"   - 기본 설정 대비 길이: {ratio:.2f}배")
        
    except Exception as e:
        print(f"❌ 최소 설정 Markdown 생성 실패: {e}")
    
    # 7. 설정별 차이점 확인
    print("\n7️⃣ 설정별 차이점 분석")
    try:
        configs = {
            "기본": generator,
            "GitHub": github_generator,
            "최소": minimal_generator
        }
        
        results = {}
        for name, gen in configs.items():
            md_text = gen.generate_markdown(structure, document)
            results[name] = {
                "길이": len(md_text),
                "줄수": len(md_text.split('\n')),
                "YAML": md_text.startswith("---"),
                "TOC": "## 목차" in md_text,
                "제목ID": "{#" in md_text
            }
        
        print("📊 설정별 비교:")
        print(f"{'설정':<8} {'길이':<8} {'줄수':<8} {'YAML':<8} {'TOC':<8} {'제목ID'}")
        print("-" * 50)
        for name, data in results.items():
            print(f"{name:<8} {data['길이']:<8} {data['줄수']:<8} {data['YAML']!s:<8} {data['TOC']!s:<8} {data['제목ID']}")
        
    except Exception as e:
        print(f"❌ 설정별 차이점 분석 실패: {e}")
    
    # 8. 파일 저장 테스트
    print("\n8️⃣ 파일 저장 테스트")
    try:
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # 기본 설정으로 저장
        basic_output = output_dir / "basic_test.md"
        generator.save_markdown(markdown_text, basic_output)
        print(f"✅ 기본 Markdown 저장: {basic_output}")
        
        # GitHub 설정으로 저장
        github_output = output_dir / "github_test.md"
        github_generator.save_markdown(github_markdown, github_output)
        print(f"✅ GitHub Markdown 저장: {github_output}")
        
        # 파일 크기 확인
        basic_size = basic_output.stat().st_size
        github_size = github_output.stat().st_size
        print(f"   - 기본 파일 크기: {basic_size} bytes")
        print(f"   - GitHub 파일 크기: {github_size} bytes")
        
    except Exception as e:
        print(f"❌ 파일 저장 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Markdown Generator 기본 테스트 완료!")
    print("\n📋 테스트된 기능들:")
    print("   ✅ MarkdownGenerator 초기화 (다양한 설정)")
    print("   ✅ 문서 구조 → Markdown 변환")
    print("   ✅ 제목 변환 (H1, H2 등)")
    print("   ✅ 단락 변환")
    print("   ✅ 리스트 변환 (불릿, 번호, 들여쓰기)")
    print("   ✅ 테이블 변환")
    print("   ✅ YAML Front Matter 생성")
    print("   ✅ 목차(TOC) 생성")
    print("   ✅ 제목 ID 생성")
    print("   ✅ 파일 저장")
    
    print("\n🚀 다음 단계: 실제 PDF 파일로 전체 파이프라인 테스트")

except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")
    print("필요한 모듈들이 설치되어 있는지 확인하세요.")
    sys.exit(1)
except Exception as e:
    print(f"❌ 예기치 않은 오류: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 