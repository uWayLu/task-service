#!/usr/bin/env python3
"""
AI 整合測試工具

測試 AI API 整合功能
"""

import os
from dotenv import load_dotenv
from utils.ai_integrator import AIIntegrator, AIProvider, analyze_financial_document

# 載入環境變數
load_dotenv()


def check_api_keys():
    """檢查 API 金鑰"""
    print("=" * 60)
    print("🔑 API 金鑰檢查")
    print("=" * 60)
    print()
    
    openai_key = os.getenv('OPENAI_API_KEY')
    claude_key = os.getenv('ANTHROPIC_API_KEY')
    custom_key = os.getenv('AI_API_KEY')
    
    results = []
    
    if openai_key:
        masked = openai_key[:10] + '...' + openai_key[-4:] if len(openai_key) > 14 else '***'
        results.append(('OpenAI', '✅', masked))
    else:
        results.append(('OpenAI', '❌', '未設定'))
    
    if claude_key:
        masked = claude_key[:10] + '...' + claude_key[-4:] if len(claude_key) > 14 else '***'
        results.append(('Claude', '✅', masked))
    else:
        results.append(('Claude', '❌', '未設定'))
    
    if custom_key:
        results.append(('Custom', '✅', '***'))
    else:
        results.append(('Custom', '❌', '未設定'))
    
    for provider, status, key in results:
        print(f"{status} {provider:15s} {key}")
    
    print()
    
    if not openai_key and not claude_key:
        print("⚠️  未設定任何 AI API 金鑰")
        print()
        print("請在 .env 檔案中設定：")
        print("  OPENAI_API_KEY=sk-your-key-here")
        print("  或")
        print("  ANTHROPIC_API_KEY=sk-ant-your-key-here")
        return False
    
    return True


def test_basic_analysis():
    """基本分析測試"""
    print("=" * 60)
    print("🧪 基本 AI 分析測試")
    print("=" * 60)
    print()
    
    # 測試文字
    test_text = """
    台灣銀行 對帳單
    
    帳號：123-456-7890123
    戶名：王小明
    對帳期間：2024/01/01 - 2024/01/31
    
    期初餘額：NT$ 50,000
    期末餘額：NT$ 45,500
    
    交易明細：
    2024/01/05  轉帳    -5,000  全聯消費
    2024/01/10  存款     8,000  薪資入帳
    2024/01/15  轉帳    -3,500  水電費
    2024/01/20  提款    -4,000  ATM 提款
    """
    
    provider = AIProvider.OPENAI if os.getenv('OPENAI_API_KEY') else AIProvider.CLAUDE
    
    print(f"使用 AI 服務: {provider.value}")
    print()
    print("分析文字：")
    print("-" * 60)
    print(test_text)
    print("-" * 60)
    print()
    
    try:
        integrator = AIIntegrator(provider=provider)
        response = integrator.analyze_document(test_text, document_type="bank_statement")
        
        if response.success:
            print("✅ 分析成功")
            print()
            print("分析結果：")
            print("-" * 60)
            print(response.content)
            print("-" * 60)
            
            if response.usage:
                print()
                print("使用量：")
                print(f"  - 輸入 tokens: {response.usage.get('prompt_tokens', 'N/A')}")
                print(f"  - 輸出 tokens: {response.usage.get('completion_tokens', 'N/A')}")
                print(f"  - 總計 tokens: {response.usage.get('total_tokens', 'N/A')}")
        else:
            print("❌ 分析失敗")
            print(f"錯誤：{response.error}")
    
    except ValueError as e:
        print(f"❌ 設定錯誤: {str(e)}")
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def test_summarize():
    """摘要測試"""
    print("\n\n" + "=" * 60)
    print("📝 文字摘要測試")
    print("=" * 60)
    print()
    
    long_text = """
    本期信用卡帳單包含多筆消費記錄。主要消費項目包括餐飲、交通、購物等。
    其中餐飲類消費共計 5,234 元，包含多次外食和咖啡店消費。
    交通類支出為 1,200 元，主要是計程車和停車費。
    購物類消費 8,500 元，包含服飾、日用品等。
    本期應繳總額為 15,689 元，繳款期限為 2024 年 2 月 15 日。
    最低應繳金額為 1,569 元。建議全額繳清以避免循環利息。
    """
    
    provider = AIProvider.OPENAI if os.getenv('OPENAI_API_KEY') else AIProvider.CLAUDE
    
    print(f"使用 AI 服務: {provider.value}")
    print()
    print("原始文字：")
    print(long_text)
    print()
    
    try:
        integrator = AIIntegrator(provider=provider)
        response = integrator.summarize(long_text, max_length=100)
        
        if response.success:
            print("✅ 摘要成功")
            print()
            print("摘要結果：")
            print("-" * 60)
            print(response.content)
            print("-" * 60)
        else:
            print("❌ 摘要失敗")
            print(f"錯誤：{response.error}")
    
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


def test_structured_extraction():
    """結構化資料提取測試"""
    print("\n\n" + "=" * 60)
    print("📊 結構化資料提取測試")
    print("=" * 60)
    print()
    
    text = """
    信用卡帳單
    卡號：**** **** **** 1234
    本期應繳：NT$ 12,345
    繳款期限：2024/02/20
    最低應繳：NT$ 1,235
    """
    
    schema = {
        "card_last4": "卡號後4碼",
        "amount_due": "應繳金額（數字）",
        "due_date": "繳款期限（YYYY/MM/DD）",
        "minimum_payment": "最低應繳（數字）"
    }
    
    provider = AIProvider.OPENAI if os.getenv('OPENAI_API_KEY') else AIProvider.CLAUDE
    
    print(f"使用 AI 服務: {provider.value}")
    print()
    print("文字內容：")
    print(text)
    print()
    print("期望結構：")
    print(schema)
    print()
    
    try:
        integrator = AIIntegrator(provider=provider)
        response = integrator.extract_structured_data(text, schema)
        
        if response.success:
            print("✅ 提取成功")
            print()
            print("提取結果：")
            print("-" * 60)
            print(response.content)
            print("-" * 60)
        else:
            print("❌ 提取失敗")
            print(f"錯誤：{response.error}")
    
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")


if __name__ == '__main__':
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 18 + "AI 整合測試工具" + " " * 18 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # 檢查 API 金鑰
    if not check_api_keys():
        print()
        print("⚠️  請先設定 API 金鑰才能進行測試")
        exit(1)
    
    try:
        # 執行測試
        test_basic_analysis()
        test_summarize()
        test_structured_extraction()
        
        print("\n\n" + "=" * 60)
        print("✅ 所有測試完成")
        print("=" * 60)
        print()
        
        print("💡 提示：")
        print("  - 使用 HTTP API 測試：python app.py")
        print("  - 查看文件：http://localhost:12345/api/docs")
        print("  - AI 整合說明：docs/AI_INTEGRATION.md")
        
    except KeyboardInterrupt:
        print("\n\n測試已中斷")
    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

