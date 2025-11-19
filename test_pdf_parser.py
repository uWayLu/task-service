#!/usr/bin/env python3
"""
PDF 解析器測試工具

用途：
1. 測試 PDF 解析功能
2. 查看解析結果
3. 除錯 PDF 處理問題

使用方式：
    python test_pdf_parser.py <pdf_file> [options]

範例：
    python test_pdf_parser.py statement.pdf
    python test_pdf_parser.py statement.pdf --verbose
    python test_pdf_parser.py statement.pdf --output result.json
"""

import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from utils.pdf_parser import PDFParser
from utils.document_processor import DocumentProcessor

# 載入環境變數
load_dotenv()


def print_separator(char='=', length=60):
    """印出分隔線"""
    print(char * length)


def print_section(title):
    """印出區塊標題"""
    print_separator()
    print(f"📋 {title}")
    print_separator()


def format_json(data, indent=2):
    """格式化 JSON 輸出"""
    return json.dumps(data, ensure_ascii=False, indent=indent)


def test_pdf_basic(pdf_path, verbose=False, password=None):
    """
    基本 PDF 解析測試
    
    Args:
        pdf_path: PDF 檔案路徑
        verbose: 是否顯示詳細資訊
        password: PDF 密碼
    """
    print_section("PDF 基本資訊")
    
    parser = PDFParser()
    
    # 顯示載入的預設密碼數量
    if parser.default_passwords:
        print(f"🔑 已載入 {len(parser.default_passwords)} 個預設密碼")
    
    try:
        result = parser.extract_text(pdf_path, password)
        
        print(f"檔案路徑: {pdf_path}")
        print(f"總頁數: {result['total_pages']}")
        print(f"文字長度: {len(result['text'])} 字元")
        
        # 顯示加密狀態
        if result.get('is_encrypted'):
            print(f"🔒 加密狀態: 已加密（已解密）")
            print(f"   {result.get('encryption_info', '')}")
            if result.get('password_used'):
                print(f"   使用密碼: {result.get('password_hint', '***')}")
        else:
            print(f"🔓 加密狀態: 無加密")
        
        # 顯示元資料
        if result.get('metadata'):
            print("\n元資料:")
            for key, value in result['metadata'].items():
                if value:
                    print(f"  {key}: {value}")
        
        # 顯示每頁資訊
        if verbose and result.get('pages'):
            print(f"\n每頁詳細資訊:")
            for page in result['pages']:
                print(f"  第 {page['page_number']} 頁:")
                print(f"    大小: {page['width']:.1f} x {page['height']:.1f}")
                print(f"    字元數: {len(page['text'])}")
        
        return result
        
    except PermissionError as e:
        print(f"🔒 PDF 加密錯誤: {str(e)}")
        print(f"\n💡 提示:")
        if parser.default_passwords:
            print(f"   - 已嘗試 {len(parser.default_passwords)} 個預設密碼，都失敗了")
            print(f"   - 請使用 --password 參數提供正確密碼")
        else:
            print(f"   - 未設定預設密碼（在 .env 中設定 PDF_DEFAULT_PASSWORDS）")
            print(f"   - 或使用 --password 參數提供密碼")
        print(f"\n   範例: python test_pdf_parser.py {pdf_path} --password YOUR_PASSWORD")
        return None
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        return None


def test_pdf_extraction(pdf_path, password=None):
    """
    測試資訊提取功能
    
    Args:
        pdf_path: PDF 檔案路徑
        password: PDF 密碼
    """
    print_section("資訊提取測試")
    
    parser = PDFParser()
    
    try:
        result = parser.extract_text(pdf_path, password)
        text = result['text']
        
        # 測試數字提取
        numbers = parser.extract_numbers(text)
        print(f"\n找到的數字 ({len(numbers)} 個):")
        for i, num in enumerate(numbers[:10], 1):  # 只顯示前 10 個
            print(f"  {i}. {num:,.2f}")
        if len(numbers) > 10:
            print(f"  ... 還有 {len(numbers) - 10} 個")
        
        # 測試日期提取
        dates = parser.extract_dates(text)
        print(f"\n找到的日期 ({len(dates)} 個):")
        for i, date in enumerate(dates[:10], 1):
            print(f"  {i}. {date}")
        if len(dates) > 10:
            print(f"  ... 還有 {len(dates) - 10} 個")
        
        # 測試金額提取
        amounts = parser.extract_amounts(text)
        print(f"\n金額資訊:")
        print(f"  所有金額: {len(amounts['all_amounts'])} 個")
        if amounts['totals']:
            print(f"  總額: {amounts['totals']}")
        if amounts['balances']:
            print(f"  餘額: {amounts['balances']}")
        
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def test_document_processing(pdf_path, doc_type='unknown', password=None):
    """
    測試文件處理功能
    
    Args:
        pdf_path: PDF 檔案路徑
        doc_type: 文件類型
        password: PDF 密碼
    """
    print_section(f"文件處理測試 (類型: {doc_type})")
    
    parser = PDFParser()
    processor = DocumentProcessor()
    
    try:
        # 解析 PDF
        pdf_content = parser.extract_text(pdf_path, password)
        
        # 處理文件
        result = processor.process_document(
            document_type=doc_type,
            content=pdf_content,
            metadata={
                'filename': Path(pdf_path).name,
                'test_mode': True
            }
        )
        
        # 顯示處理結果
        print(f"\n文件類型: {result['document_type']}")
        print(f"總頁數: {result['total_pages']}")
        print(f"處理時間: {result['processed_at']}")
        
        print("\n摘要資訊:")
        summary = result['summary']
        for key, value in summary.items():
            if value is not None:
                print(f"  {key}: {value}")
        
        # 顯示交易記錄
        if result.get('transactions'):
            print(f"\n交易記錄 (前 5 筆):")
            for i, trans in enumerate(result['transactions'][:5], 1):
                print(f"  {i}. {trans}")
        
        return result
        
    except PermissionError as e:
        print(f"🔒 PDF 加密錯誤: {str(e)}")
        print(f"\n💡 提示: 請使用 --password 參數提供密碼")
        return None
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def show_text_preview(pdf_path, lines=20, password=None):
    """
    顯示 PDF 文字預覽
    
    Args:
        pdf_path: PDF 檔案路徑
        lines: 顯示行數
        password: PDF 密碼
    """
    print_section("PDF 文字內容預覽")
    
    parser = PDFParser()
    
    try:
        result = parser.extract_text(pdf_path, password)
        text_lines = result['text'].split('\n')
        
        print(f"\n前 {lines} 行內容:\n")
        for i, line in enumerate(text_lines[:lines], 1):
            if line.strip():
                print(f"{i:3d} | {line}")
        
        if len(text_lines) > lines:
            print(f"\n... 還有 {len(text_lines) - lines} 行")
        
    except PermissionError as e:
        print(f"🔒 PDF 加密錯誤: {str(e)}")
        print(f"\n💡 提示: 請使用 --password 參數提供密碼")
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def save_result(result, output_path):
    """
    儲存結果到檔案
    
    Args:
        result: 解析結果
        output_path: 輸出檔案路徑
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 結果已儲存到: {output_path}")
    except Exception as e:
        print(f"❌ 儲存失敗: {str(e)}")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='PDF 解析器測試工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  %(prog)s statement.pdf
  %(prog)s statement.pdf --type bank_statement
  %(prog)s statement.pdf --verbose --preview 30
  %(prog)s statement.pdf --output result.json
  %(prog)s statement.pdf --all
        """
    )
    
    parser.add_argument('pdf_file', help='PDF 檔案路徑')
    parser.add_argument('-t', '--type', 
                       choices=['bank_statement', 'credit_card', 'transaction_notice', 'unknown'],
                       default='unknown',
                       help='文件類型 (預設: unknown)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='顯示詳細資訊')
    parser.add_argument('-p', '--preview', type=int, metavar='N',
                       help='顯示前 N 行文字內容')
    parser.add_argument('-o', '--output', metavar='FILE',
                       help='輸出結果到 JSON 檔案')
    parser.add_argument('-a', '--all', action='store_true',
                       help='執行所有測試')
    parser.add_argument('--password', 
                       help='PDF 密碼（如果檔案有加密）')
    
    args = parser.parse_args()
    
    # 檢查檔案是否存在
    if not Path(args.pdf_file).exists():
        print(f"❌ 錯誤: 找不到檔案 '{args.pdf_file}'")
        sys.exit(1)
    
    # 顯示標題
    print_separator('=', 70)
    print(f"🔍 PDF 解析器測試工具")
    print_separator('=', 70)
    print()
    
    # 執行測試
    try:
        # 基本資訊
        basic_result = test_pdf_basic(args.pdf_file, args.verbose, args.password)
        print()
        
        if not basic_result:
            sys.exit(1)
        
        # 資訊提取測試
        if args.all or args.verbose:
            test_pdf_extraction(args.pdf_file, args.password)
            print()
        
        # 文字預覽
        if args.preview:
            show_text_preview(args.pdf_file, args.preview, args.password)
            print()
        
        # 文件處理測試
        doc_result = test_document_processing(args.pdf_file, args.type, args.password)
        print()
        
        # 儲存結果
        if args.output and doc_result:
            save_result(doc_result, args.output)
        
        # 最終總結
        print_separator('=', 70)
        print("✅ 測試完成")
        print_separator('=', 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  測試中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 發生錯誤: {str(e)}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

