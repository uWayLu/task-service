#!/usr/bin/env python3
"""
PDF 遮罩效果測試工具

測試 PDF 解析後的個資遮罩效果
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from utils.pdf_parser import PDFParser
from utils.privacy_masker import PrivacyMasker, SmartPrivacyMasker

# 載入環境變數
load_dotenv()


def print_section(title):
    """印出區塊標題"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_pdf_masking(pdf_path, password=None, aggressive=False, mask_types=None):
    """
    測試 PDF 遮罩效果
    
    Args:
        pdf_path: PDF 檔案路徑
        password: PDF 密碼
        aggressive: 是否使用積極模式
        mask_types: 要遮罩的類型列表
    """
    
    # 1. 解析 PDF
    print_section("📄 步驟 1: 解析 PDF")
    
    parser = PDFParser()
    
    try:
        result = parser.extract_text(pdf_path, password)
        original_text = result['text']
        
        print(f"✅ PDF 解析成功")
        print(f"   - 頁數: {result['total_pages']}")
        print(f"   - 文字長度: {len(original_text)} 字元")
        
        if result.get('is_encrypted'):
            print(f"   - 加密狀態: 已加密（已解密）")
            if result.get('password_used'):
                print(f"   - 使用密碼: {result.get('password_hint', '***')}")
    
    except PermissionError as e:
        print(f"❌ PDF 加密錯誤: {str(e)}")
        print(f"\n💡 提示: 使用 --password 參數提供密碼")
        return
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        return
    
    # 2. 偵測敏感資訊
    print_section("🔍 步驟 2: 偵測敏感資訊")
    
    if aggressive:
        masker = SmartPrivacyMasker(aggressive=True)
        print("使用模式: 智慧積極模式")
    elif mask_types:
        masker = PrivacyMasker(mask_types=mask_types)
        print(f"使用模式: 選擇性遮罩 ({', '.join(mask_types)})")
    else:
        masker = PrivacyMasker()
        print("使用模式: 標準模式")
    
    sensitive_items = masker.detect(original_text)
    
    if sensitive_items:
        print(f"\n✅ 偵測到 {len(sensitive_items)} 個敏感資料：")
        
        # 統計各類型
        type_counts = {}
        for item in sensitive_items:
            type_name = item['type_name']
            if type_name not in type_counts:
                type_counts[type_name] = []
            type_counts[type_name].append(item['masked'])
        
        for type_name, items in type_counts.items():
            print(f"\n   📌 {type_name} ({len(items)} 個)：")
            for i, masked_value in enumerate(items[:3], 1):  # 只顯示前 3 個
                print(f"      {i}. {masked_value}")
            if len(items) > 3:
                print(f"      ... 還有 {len(items) - 3} 個")
    else:
        print("ℹ️  未偵測到敏感資料")
    
    # 3. 遮罩處理
    print_section("🔒 步驟 3: 執行遮罩")
    
    mask_result = masker.mask(original_text)
    masked_text = mask_result.masked
    
    print(f"✅ 遮罩完成")
    print(f"   - 遮罩項目: {mask_result.mask_count} 個")
    print(f"   - 原始長度: {len(original_text)} 字元")
    print(f"   - 遮罩後長度: {len(masked_text)} 字元")
    
    # 4. 顯示對比
    print_section("📊 步驟 4: 原始 vs 遮罩對比")
    
    # 取前 1000 字元顯示
    preview_length = 1000
    
    print("\n🔓 原始文字（前 1000 字元）：")
    print("-" * 70)
    print(original_text[:preview_length])
    if len(original_text) > preview_length:
        print(f"\n... 還有 {len(original_text) - preview_length} 字元")
    print("-" * 70)
    
    print("\n🔒 遮罩後文字（前 1000 字元）：")
    print("-" * 70)
    print(masked_text[:preview_length])
    if len(masked_text) > preview_length:
        print(f"\n... 還有 {len(masked_text) - preview_length} 字元")
    print("-" * 70)
    
    # 5. 儲存結果（選填）
    print_section("💾 步驟 5: 儲存結果")
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 儲存原始文字
    original_file = output_dir / f"{Path(pdf_path).stem}_original.txt"
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(original_text)
    print(f"✅ 原始文字已儲存: {original_file}")
    
    # 儲存遮罩文字
    masked_file = output_dir / f"{Path(pdf_path).stem}_masked.txt"
    with open(masked_file, 'w', encoding='utf-8') as f:
        f.write(masked_text)
    print(f"✅ 遮罩文字已儲存: {masked_file}")
    
    # 儲存敏感資料清單
    report_file = output_dir / f"{Path(pdf_path).stem}_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"PDF 個資遮罩報告\n")
        f.write(f"=" * 70 + "\n\n")
        f.write(f"檔案: {pdf_path}\n")
        f.write(f"頁數: {result['total_pages']}\n")
        f.write(f"遮罩模式: {'智慧積極模式' if aggressive else '標準模式'}\n")
        f.write(f"遮罩項目: {mask_result.mask_count} 個\n\n")
        
        f.write(f"敏感資料清單：\n")
        f.write(f"-" * 70 + "\n")
        
        for item in mask_result.sensitive_items:
            f.write(f"\n{item['type_name']}:\n")
            f.write(f"  原始: {item['original']}\n")
            f.write(f"  遮罩: {item['masked']}\n")
    
    print(f"✅ 遮罩報告已儲存: {report_file}")
    
    # 6. 統計摘要
    print_section("📈 統計摘要")
    
    print(f"""
✨ 測試完成！

📊 統計資訊：
   - PDF 頁數: {result['total_pages']}
   - 原始文字: {len(original_text):,} 字元
   - 遮罩項目: {mask_result.mask_count} 個
   - 遮罩類型: {len(type_counts)} 種
   
📁 輸出檔案：
   - 原始文字: {original_file}
   - 遮罩文字: {masked_file}
   - 遮罩報告: {report_file}

💡 提示：
   - 使用 diff 比較: diff {original_file} {masked_file}
   - 查看報告: cat {report_file}
   - 測試 AI 分析: curl -X POST http://localhost:12345/api/ai/mask-and-analyze -F "file=@{pdf_path}"
    """)


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='測試 PDF 個資遮罩效果',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 基本測試
  python test_pdf_masking.py statement.pdf
  
  # 有密碼的 PDF
  python test_pdf_masking.py statement.pdf --password A123456789
  
  # 積極模式（遮罩更多資訊）
  python test_pdf_masking.py statement.pdf --aggressive
  
  # 只遮罩特定類型
  python test_pdf_masking.py statement.pdf --types taiwan_id,phone,address
        """
    )
    
    parser.add_argument('pdf_file', help='PDF 檔案路徑')
    parser.add_argument('--password', '-p', help='PDF 密碼（如果有加密）')
    parser.add_argument('--aggressive', '-a', action='store_true', 
                       help='使用積極模式（遮罩更多資訊，包含金額）')
    parser.add_argument('--types', '-t', help='要遮罩的類型（逗號分隔）')
    
    args = parser.parse_args()
    
    # 檢查檔案
    if not Path(args.pdf_file).exists():
        print(f"❌ 錯誤: 找不到檔案 '{args.pdf_file}'")
        return 1
    
    # 解析遮罩類型
    mask_types = None
    if args.types:
        mask_types = [t.strip() for t in args.types.split(',')]
    
    # 執行測試
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "PDF 個資遮罩測試工具" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        test_pdf_masking(
            args.pdf_file,
            password=args.password,
            aggressive=args.aggressive,
            mask_types=mask_types
        )
        return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  測試已中斷")
        return 1
    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

