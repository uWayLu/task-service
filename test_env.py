#!/usr/bin/env python3
"""
環境變數測試工具
檢查 .env 配置是否正確載入
"""

import os
from dotenv import load_dotenv
from utils.pdf_parser import PDFParser

# 載入環境變數
load_dotenv()

print("=" * 60)
print("🔍 環境變數檢查")
print("=" * 60)
print()

# 檢查 .env 檔案
env_file = '.env'
if os.path.exists(env_file):
    print(f"✅ 找到 .env 檔案")
    
    # 顯示相關配置
    print(f"\n📋 PDF 密碼相關配置:")
    print("-" * 60)
    
    # 檢查 PDF_DEFAULT_PASSWORDS
    default_passwords = os.getenv('PDF_DEFAULT_PASSWORDS')
    if default_passwords:
        print(f"PDF_DEFAULT_PASSWORDS: {default_passwords}")
        passwords = [p.strip() for p in default_passwords.split(',') if p.strip()]
        print(f"  → 解析出 {len(passwords)} 個密碼")
    else:
        print("PDF_DEFAULT_PASSWORDS: (未設定)")
    
    # 檢查編號密碼
    numbered_passwords = []
    i = 1
    while True:
        pwd = os.getenv(f'PDF_PASSWORD_{i}')
        if not pwd:
            break
        numbered_passwords.append(pwd)
        print(f"PDF_PASSWORD_{i}: {pwd}")
        i += 1
    
    if numbered_passwords:
        print(f"  → 找到 {len(numbered_passwords)} 個編號密碼")
    else:
        print("PDF_PASSWORD_1, 2, 3...: (未設定)")
    
else:
    print(f"❌ 找不到 .env 檔案")
    print(f"   請建立 .env 檔案並設定 PDF_DEFAULT_PASSWORDS")

print()
print("-" * 60)

# 測試 PDFParser
print(f"\n🔧 PDFParser 狀態:")
print("-" * 60)

parser = PDFParser()

if parser.default_passwords:
    print(f"✅ 已載入 {len(parser.default_passwords)} 個預設密碼")
    print(f"\n密碼列表（遮罩顯示）:")
    for i, pwd in enumerate(parser.default_passwords, 1):
        # 遮罩顯示
        if len(pwd) > 2:
            masked = f"{pwd[0]}{'*' * (len(pwd) - 2)}{pwd[-1]}"
        else:
            masked = "***"
        print(f"  {i}. {masked}")
else:
    print(f"⚠️  未載入任何預設密碼")
    print(f"\n建議:")
    print(f"  1. 建立或編輯 .env 檔案")
    print(f"  2. 加入以下設定:")
    print(f"     PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678")

print()
print("=" * 60)
print()

# 給出建議
if not parser.default_passwords:
    print("💡 快速設定:")
    print("-" * 60)
    print("執行以下指令設定預設密碼:")
    print()
    print("cat >> .env << 'EOF'")
    print("# PDF 預設密碼")
    print("PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678")
    print("EOF")
    print()
    print("然後重新執行此測試")
else:
    print("✅ 配置正常！可以開始測試 PDF 解析")
    print()
    print("測試指令:")
    print("  python test_pdf_parser.py your-encrypted-file.pdf")

