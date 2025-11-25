#!/usr/bin/env python3
"""
測試自訂姓名遮罩功能
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

from utils.privacy_masker import PrivacyMasker

def test_custom_names():
    """測試自訂姓名遮罩"""
    print("=" * 60)
    print("🔒 自訂姓名遮罩測試")
    print("=" * 60)
    
    # 測試文字
    test_text = """
    姓名：王小明
    聯絡人：張三
    負責人：李四
    身分證：A123456789
    手機：0912345678
    """
    
    print("\n📄 原始文字：")
    print(test_text)
    
    # 測試 1: 從環境變數讀取
    print("\n" + "-" * 60)
    print("測試 1: 從環境變數讀取自訂姓名")
    print("-" * 60)
    
    masker = PrivacyMasker()
    
    if masker.custom_names:
        print(f"✅ 已載入 {len(masker.custom_names)} 個自訂姓名: {masker.custom_names}")
    else:
        print("⚠️  未找到自訂姓名（請在 .env 中設定 PRIVACY_CUSTOM_NAMES）")
        print("   使用測試姓名: 王小明, 張三, 李四")
        masker.add_custom_names(['王小明', '張三', '李四'])
    
    result = masker.mask(test_text)
    
    print("\n🔐 遮罩後文字：")
    print(result.masked)
    
    print(f"\n📊 統計資訊：")
    print(f"   - 遮罩項目: {result.mask_count} 個")
    print(f"\n   - 敏感資料列表：")
    for item in result.sensitive_items:
        print(f"     • {item['type_name']}: {item['original']} → {item['masked']}")
    
    # 測試 2: 手動指定姓名
    print("\n\n" + "-" * 60)
    print("測試 2: 手動指定自訂姓名")
    print("-" * 60)
    
    masker2 = PrivacyMasker(custom_names=['測試姓名', '另一個名字'])
    result2 = masker2.mask("聯絡人：測試姓名，負責人：另一個名字")
    
    print(f"原始: 聯絡人：測試姓名，負責人：另一個名字")
    print(f"遮罩: {result2.masked}")
    print(f"遮罩項目: {result2.mask_count} 個")


if __name__ == '__main__':
    try:
        test_custom_names()
        print("\n\n" + "=" * 60)
        print("✅ 測試完成")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

