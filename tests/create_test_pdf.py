#!/usr/bin/env python3
"""
테스트용 PDF 파일 생성 스크립트

PyMuPDF와 pdfplumber 테스트를 위한 샘플 PDF 파일들을 생성합니다.
"""

import sys
from pathlib import Path


def create_simple_pdf():
    """간단한 텍스트가 포함된 PDF 생성"""
    try:
        import fitz  # PyMuPDF
        
        # 새 PDF 문서 생성
        doc = fitz.open()
        
        # 첫 번째 페이지 추가
        page = doc.new_page()
        
        # 제목 추가 (큰 폰트)
        page.insert_text((50, 100), "PDF to Markdown 변환기 테스트", 
                         fontsize=20, color=(0, 0, 0))
        
        # 부제목 추가 (중간 폰트)
        page.insert_text((50, 150), "1. 기본 텍스트 추출 테스트", 
                         fontsize=16, color=(0, 0, 0))
        
        # 본문 텍스트 추가
        page.insert_text((50, 200), "이 문서는 PDF to Markdown 변환기의", 
                         fontsize=12, color=(0, 0, 0))
        page.insert_text((50, 220), "기본 기능을 테스트하기 위한 샘플 문서입니다.", 
                         fontsize=12, color=(0, 0, 0))
        
        # 리스트 형태 텍스트 추가
        page.insert_text((50, 260), "주요 기능:", 
                         fontsize=14, color=(0, 0, 0))
        page.insert_text((70, 280), "• PDF 파일 읽기", 
                         fontsize=12, color=(0, 0, 0))
        page.insert_text((70, 300), "• 텍스트 추출", 
                         fontsize=12, color=(0, 0, 0))
        page.insert_text((70, 320), "• Markdown 변환", 
                         fontsize=12, color=(0, 0, 0))
        
        # 두 번째 페이지 추가
        page2 = doc.new_page()
        page2.insert_text((50, 100), "2. 멀티 페이지 테스트", 
                          fontsize=16, color=(0, 0, 0))
        page2.insert_text((50, 150), "이 페이지는 여러 페이지로 구성된", 
                          fontsize=12, color=(0, 0, 0))
        page2.insert_text((50, 170), "PDF 문서의 처리를 테스트합니다.", 
                          fontsize=12, color=(0, 0, 0))
        
        # 파일 저장
        output_path = Path("test_files/sample.pdf")
        output_path.parent.mkdir(exist_ok=True)
        doc.save(str(output_path))
        doc.close()
        
        print(f"✅ 간단한 테스트 PDF 생성 완료: {output_path}")
        return True
        
    except ImportError:
        print("❌ PyMuPDF가 설치되지 않아 테스트 PDF를 생성할 수 없습니다.")
        return False
    except Exception as e:
        print(f"❌ 테스트 PDF 생성 실패: {e}")
        return False


def create_table_pdf():
    """테이블이 포함된 PDF 생성"""
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open()
        page = doc.new_page()
        
        # 제목
        page.insert_text((50, 50), "테이블 테스트 문서", 
                         fontsize=18, color=(0, 0, 0))
        
        # 간단한 테이블 형태 텍스트 (실제 테이블은 아니지만 테스트용)
        y_pos = 120
        page.insert_text((50, y_pos), "이름", fontsize=12, color=(0, 0, 0))
        page.insert_text((150, y_pos), "나이", fontsize=12, color=(0, 0, 0))
        page.insert_text((250, y_pos), "직업", fontsize=12, color=(0, 0, 0))
        
        y_pos += 30
        page.insert_text((50, y_pos), "김철수", fontsize=12, color=(0, 0, 0))
        page.insert_text((150, y_pos), "30", fontsize=12, color=(0, 0, 0))
        page.insert_text((250, y_pos), "개발자", fontsize=12, color=(0, 0, 0))
        
        y_pos += 20
        page.insert_text((50, y_pos), "이영희", fontsize=12, color=(0, 0, 0))
        page.insert_text((150, y_pos), "25", fontsize=12, color=(0, 0, 0))
        page.insert_text((250, y_pos), "디자이너", fontsize=12, color=(0, 0, 0))
        
        # 간단한 선을 그어서 테이블처럼 보이게 만들기
        # 수평선
        page.draw_line((40, 110), (350, 110), width=1)  # 헤더 위
        page.draw_line((40, 140), (350, 140), width=1)  # 헤더 아래
        page.draw_line((40, 190), (350, 190), width=1)  # 마지막 행 아래
        
        # 수직선
        page.draw_line((40, 110), (40, 190), width=1)   # 왼쪽
        page.draw_line((140, 110), (140, 190), width=1) # 이름-나이 사이
        page.draw_line((240, 110), (240, 190), width=1) # 나이-직업 사이
        page.draw_line((350, 110), (350, 190), width=1) # 오른쪽
        
        # 저장
        output_path = Path("test_files/table_sample.pdf")
        output_path.parent.mkdir(exist_ok=True)
        doc.save(str(output_path))
        doc.close()
        
        print(f"✅ 테이블 테스트 PDF 생성 완료: {output_path}")
        return True
        
    except ImportError:
        print("❌ PyMuPDF가 설치되지 않아 테이블 테스트 PDF를 생성할 수 없습니다.")
        return False
    except Exception as e:
        print(f"❌ 테이블 테스트 PDF 생성 실패: {e}")
        return False


def main():
    """테스트 PDF 파일들 생성"""
    print("🔧 테스트용 PDF 파일 생성 중...")
    print()
    
    success_count = 0
    
    if create_simple_pdf():
        success_count += 1
    
    if create_table_pdf():
        success_count += 1
    
    print()
    print(f"📊 생성 결과: {success_count}/2 개 파일 생성 완료")
    
    if success_count > 0:
        print("✅ 테스트용 PDF 파일 생성 성공")
        print("📁 생성된 파일:")
        for pdf_file in Path("test_files").glob("*.pdf"):
            print(f"   - {pdf_file}")
        return True
    else:
        print("❌ 테스트용 PDF 파일 생성 실패")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 