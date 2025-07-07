#!/usr/bin/env python3
"""간단한 PDFReader 테스트"""

import sys
from pathlib import Path

sys.path.insert(0, 'src')

def main():
    print("=== PDF Reader 테스트 ===")
    
    # Import 테스트
    try:
        from pdf_to_markdown.pdf_reader import PDFReader
        print("✅ PDFReader import 성공")
    except Exception as e:
        print(f"❌ Import 실패: {e}")
        return
    
    # PDF 파일 확인
    pdf_path = Path('test_files/sample.pdf')
    if not pdf_path.exists():
        print("❌ 테스트 PDF 파일이 없습니다")
        return
    
    print(f"✅ PDF 파일 발견: {pdf_path}")
    
    # PDFReader 테스트
    try:
        reader = PDFReader(pdf_path)
        print("✅ PDFReader 초기화 성공")
        
        # 메타데이터 추출
        metadata = reader.get_document_info()
        print(f"✅ 메타데이터: {metadata.page_count}페이지")
        
        # 텍스트 추출
        with reader:
            text_blocks = reader.extract_page_text(0)
            print(f"✅ 텍스트 추출: {len(text_blocks)}개 블록")
            
            if text_blocks:
                print(f"   첫 블록: \"{text_blocks[0].text[:30]}...\"")
        
        print("🎉 테스트 성공!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 