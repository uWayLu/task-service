#!/usr/bin/env python3
"""
個資遮罩測試工具

測試個資偵測與遮罩功能
"""

from utils.privacy_masker import PrivacyMasker, SmartPrivacyMasker, detect_sensitive_info


def test_basic_masking():
    """基本遮罩測試"""
    print("=" * 60)
    print("🔒 基本個資遮罩測試")
    print("=" * 60)
    
    # 測試文字
    test_text = """
    姓名：王小明
    身分證字號：A123456789
    手機：0912345678
    市話：02-12345678
    電子郵件：example@gmail.com
    信用卡號：1234-5678-9012-3456
    銀行帳號：1234567890123
    地址：台北市中正區忠孝東路100號
    出生日期：80年5月15日
    
    交易金額：NT$ 12,345 元
    """
    
    masker = PrivacyMasker()
    result = masker.mask(test_text)
    
    print("\n📄 原始文字：")
    print(test_text)
    
    print("\n🔐 遮罩後文字：")
    print(result.masked)
    
    print(f"\n📊 統計資訊：")
    print(f"   - 偵測到 {result.mask_count} 個敏感資料")
    print(f"\n   - 敏感資料列表：")
    for item in result.sensitive_items:
        print(f"     • {item['type_name']}: {item['original']} → {item['masked']}")


def test_smart_masking():
    """智慧遮罩測試"""
    print("\n\n" + "=" * 60)
    print("🧠 智慧遮罩測試（積極模式）")
    print("=" * 60)
    
    test_text = """
    2024年1月帳單
    本期應繳：NT$ 25,680 元
    繳費期限：2024/01/25
    戶名：王小明
    帳號：0912345678901234
    """
    
    masker = SmartPrivacyMasker(aggressive=True)
    result = masker.mask(test_text)
    
    print("\n📄 原始文字：")
    print(test_text)
    
    print("\n🔐 遮罩後文字（積極模式）：")
    print(result.masked)
    
    print(f"\n📊 遮罩了 {result.mask_count} 個項目")


def test_detection_only():
    """僅偵測測試"""
    print("\n\n" + "=" * 60)
    print("🔍 僅偵測敏感資訊（不遮罩）")
    print("=" * 60)
    
    test_text = """
    客戶資料：
    張三 - A234567890 - 0923456789
    李四 - B123456789 - 0934567890
    """
    
    items = detect_sensitive_info(test_text)
    
    print(f"\n找到 {len(items)} 個敏感資料：")
    for item in items:
        print(f"  • {item['type_name']}: {item['masked']}")


def test_selective_masking():
    """選擇性遮罩測試"""
    print("\n\n" + "=" * 60)
    print("🎯 選擇性遮罩（僅遮罩身分證與電話）")
    print("=" * 60)
    
    test_text = """
    姓名：王小明
    身分證：A123456789
    手機：0912345678
    Email: test@example.com
    地址：台北市信義區
    """
    
    # 僅遮罩身分證和電話
    masker = PrivacyMasker(mask_types=['taiwan_id', 'phone'])
    result = masker.mask(test_text)
    
    print("\n📄 原始文字：")
    print(test_text)
    
    print("\n🔐 遮罩後（僅身分證與電話）：")
    print(result.masked)


def test_supported_types():
    """顯示支援的遮罩類型"""
    print("\n\n" + "=" * 60)
    print("📋 支援的個資類型")
    print("=" * 60)
    
    masker = PrivacyMasker()
    types = masker.get_mask_types()
    
    print("\n支援的遮罩類型：")
    for i, type_info in enumerate(types, 1):
        print(f"  {i}. {type_info['name']} ({type_info['type']})")


if __name__ == '__main__':
    try:
        test_basic_masking()
        test_smart_masking()
        test_detection_only()
        test_selective_masking()
        test_supported_types()
        
        print("\n\n" + "=" * 60)
        print("✅ 所有測試完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

