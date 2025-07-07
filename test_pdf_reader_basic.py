#!/usr/bin/env python3
"""
PDF Reader 기본 기능 테스트 스크립트

Phase 2.1에서 구현한 PDFReader 클래스의 핵심 기능들을 테스트합니다.
"""

import sys
from pathlib import Path

# 프로젝트 소스 경로 추가
sys.path.insert(0, 'src')

def test_basic_functionality():
    """기본 기능 테스트"""
    print("=" * 50)
    print("🧪 PDF Reader 기본 기능 테스트")
    print("=" * 50)
    print()
    
    # 1. 모듈 import 테스트
    print("1️⃣ 모듈 import 테스트...")
    try:
        from pdf_to_markdown.pdf_reader import PDFReader
        from pdf_to_markdown.data_models import DocumentMetadata, FontStyle
        from pdf_to_markdown.exceptions import FileNotFoundError
        print("   ✅ 모든 모듈 import 성공")
    except Exception as e:
        print(f"   ❌ Import 실패: {e}")
        return False
    print()
    
    # 2. 테스트 파일 확인
    print("2️⃣ 테스트 파일 확인...")
    pdf_path = Path('test_files/sample.pdf')
    table_pdf_path = Path('test_files/table_sample.pdf')
    
    if pdf_path.exists():
        print(f"   ✅ 기본 PDF 파일 발견: {pdf_path} ({pdf_path.stat().st_size} bytes)")
    else:
        print("   ❌ 기본 PDF 파일이 없습니다")
        return False
    
    if table_pdf_path.exists():
        print(f"   ✅ 테이블 PDF 파일 발견: {table_pdf_path} ({table_pdf_path.stat().st_size} bytes)")
    else:
        print("   ⚠️  테이블 PDF 파일이 없습니다")
    print()
    
    # 3. PDFReader 초기화 테스트
    print("3️⃣ PDFReader 초기화 테스트...")
    try:
                 reader = PDFReader(pdf_path)
         print(f"   ✅ PDFReader 초기화 성공: {reader.pdf_path}")
         print(f"   📊 초기 상태: 이미지 추출={reader.should_extract_images}")
    except Exception as e:
        print(f"   ❌ 초기화 실패: {e}")
        return False
    print()
    
    # 4. 문서 메타데이터 추출 테스트
    print("4️⃣ 문서 메타데이터 추출 테스트...")
    try:
        metadata = reader.get_document_info()
        print(f"   ✅ 메타데이터 추출 성공")
        print(f"   📄 페이지 수: {metadata.page_count}")
        print(f"   📏 파일 크기: {metadata.file_size} bytes")
        print(f"   🔒 암호화: {metadata.is_encrypted}")
        if metadata.title:
            print(f"   📝 제목: {metadata.title}")
    except Exception as e:
        print(f"   ❌ 메타데이터 추출 실패: {e}")
        return False
    print()
    
    # 5. 문서 열기/닫기 테스트
    print("5️⃣ 문서 열기/닫기 테스트...")
    try:
        doc = reader.open_document()
        print(f"   ✅ 문서 열기 성공: {doc.page_count}페이지")
        print(f"   📊 상태: is_open={reader._is_open}")
        
        reader.close_document()
        print(f"   ✅ 문서 닫기 성공: is_open={reader._is_open}")
    except Exception as e:
        print(f"   ❌ 문서 열기/닫기 실패: {e}")
        return False
    print()
    
    # 6. 컨텍스트 매니저 테스트
    print("6️⃣ 컨텍스트 매니저 테스트...")
    try:
        with reader as r:
            print(f"   ✅ 컨텍스트 진입: is_open={r._is_open}")
        print(f"   ✅ 컨텍스트 종료: is_open={reader._is_open}")
    except Exception as e:
        print(f"   ❌ 컨텍스트 매니저 실패: {e}")
        return False
    print()
    
    # 7. 페이지 텍스트 추출 테스트
    print("7️⃣ 페이지 텍스트 추출 테스트...")
    try:
        with reader:
            text_blocks = reader.extract_page_text(0)
            print(f"   ✅ 첫 페이지 텍스트 추출 성공: {len(text_blocks)}개 블록")
            
            if text_blocks:
                first_block = text_blocks[0]
                print(f"   📝 첫 번째 블록: \"{first_block.text[:30]}...\"")
                print(f"   🔤 폰트: {first_block.font_info.name}")
                print(f"   📏 크기: {first_block.font_info.size}")
                print(f"   🎨 스타일: {first_block.font_info.style.value}")
                
            # 통계 확인
            stats = reader.get_processing_stats()
            print(f"   📊 추출 통계: {stats.text_blocks_extracted}개 블록")
    except Exception as e:
        print(f"   ❌ 텍스트 추출 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()
    
    # 8. 이미지 추출 테스트
    print("8️⃣ 이미지 추출 테스트...")
    try:
        with reader:
            images = reader.extract_images(0)
            print(f"   ✅ 첫 페이지 이미지 추출 성공: {len(images)}개 이미지")
            
            if images:
                first_image = images[0]
                print(f"   🖼️  첫 번째 이미지: {first_image.width}x{first_image.height}")
                print(f"   📎 형식: {first_image.format}")
                print(f"   💾 크기: {len(first_image.data)} bytes")
    except Exception as e:
        print(f"   ❌ 이미지 추출 실패: {e}")
        return False
    print()
    
    # 9. 전체 문서 추출 테스트
    print("9️⃣ 전체 문서 추출 테스트...")
    try:
        document = reader.extract_document()
        print(f"   ✅ 전체 문서 추출 성공")
        print(f"   📄 페이지 수: {len(document.pages)}")
        print(f"   📝 총 텍스트 블록: {document.total_text_blocks}")
        print(f"   🖼️  총 이미지: {document.total_images}")
        
        # 최종 통계
        final_stats = reader.get_processing_stats()
        print(f"   ⏱️  처리 시간: {final_stats.processing_time:.2f}초")
        print(f"   📊 처리된 페이지: {final_stats.processed_pages}/{final_stats.total_pages}")
        print(f"   ⚠️  오류 수: {len(final_stats.errors)}")
        print(f"   💡 경고 수: {len(final_stats.warnings)}")
    except Exception as e:
        print(f"   ❌ 전체 문서 추출 실패: {e}")
        return False
    print()
    
    # 10. 오류 처리 테스트
    print("🔟 오류 처리 테스트...")
    try:
        # 존재하지 않는 파일
        try:
            PDFReader(Path("nonexistent.pdf"))
            print("   ❌ 존재하지 않는 파일 처리 실패")
            return False
        except FileNotFoundError:
            print("   ✅ 존재하지 않는 파일 예외 처리 성공")
        
        # 잘못된 페이지 번호
        try:
            with reader:
                reader.extract_page_text(-1)
            print("   ❌ 잘못된 페이지 번호 처리 실패")
            return False
        except Exception:
            print("   ✅ 잘못된 페이지 번호 예외 처리 성공")
            
    except Exception as e:
        print(f"   ❌ 오류 처리 테스트 실패: {e}")
        return False
    print()
    
    return True


def test_table_pdf():
    """테이블 PDF 추가 테스트"""
    table_pdf_path = Path('test_files/table_sample.pdf')
    if not table_pdf_path.exists():
        print("⚠️  테이블 PDF 파일이 없어 테이블 테스트를 건너뜁니다.")
        return True
    
    print("📊 테이블 PDF 추가 테스트...")
    try:
        reader = PDFReader(table_pdf_path)
        with reader:
            text_blocks = reader.extract_page_text(0)
            all_text = " ".join(block.text for block in text_blocks)
            print(f"   ✅ 테이블 PDF 텍스트 추출 성공: {len(all_text)}문자")
            print(f"   📝 내용 미리보기: \"{all_text[:50]}...\"")
        return True
    except Exception as e:
        print(f"   ❌ 테이블 PDF 테스트 실패: {e}")
        return False


def main():
    """메인 테스트 실행"""
    success = True
    
    # 기본 기능 테스트
    if not test_basic_functionality():
        success = False
    
    # 테이블 PDF 테스트
    if not test_table_pdf():
        success = False
    
    # 결과 요약
    print("=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    if success:
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("✅ Phase 2.1 PDF Reader 모듈 구현 완료")
        print()
        print("🚀 다음 단계: Phase 2.2 Text Parser 모듈 구현")
        return True
    else:
        print("❌ 일부 테스트가 실패했습니다.")
        print("🔧 오류를 수정한 후 다시 시도해주세요.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 