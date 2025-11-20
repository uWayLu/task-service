#!/usr/bin/env python3
"""
結構化資訊提取測試工具

測試基於規則的提取 + JSON Schema 驗證
"""

import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from utils.pdf_parser import PDFParser
from utils.extraction_manager import ExtractionManager
from utils.schema_validator import SchemaValidator

# 載入環境變數
load_dotenv()


def print_section(title):
    """印出區塊標題"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_extraction(pdf_path, password=None, enable_ai=False, save_json=False):
    """
    測試資訊提取
    
    Args:
        pdf_path: PDF 檔案路徑
        password: PDF 密碼
        enable_ai: 是否啟用 AI fallback
        save_json: 是否儲存 JSON
    """
    
    # 1. 解析 PDF
    print_section("📄 步驟 1: 解析 PDF")
    
    parser = PDFParser()
    
    try:
        result = parser.extract_text(pdf_path, password)
        text = result['text']
        
        print(f"✅ PDF 解析成功")
        print(f"   - 頁數: {result['total_pages']}")
        print(f"   - 文字長度: {len(text)} 字元")
    
    except PermissionError as e:
        print(f"❌ PDF 加密錯誤: {str(e)}")
        print(f"\n💡 提示: 使用 --password 參數提供密碼")
        return
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        return
    
    # 2. 資訊提取
    print_section("🔍 步驟 2: 結構化資訊提取")
    
    manager = ExtractionManager(enable_ai_fallback=enable_ai)
    
    metadata = {
        'filename': Path(pdf_path).name,
        'total_pages': result['total_pages']
    }
    
    extraction_result = manager.extract(text, metadata=metadata, validate=True)
    
    if not extraction_result['success']:
        print(f"❌ 提取失敗")
        for error in extraction_result['errors']:
            print(f"   - {error}")
        return
    
    print(f"✅ 提取成功")
    print(f"   - 方法: {extraction_result['method']}")
    if 'extractor' in extraction_result:
        print(f"   - 提取器: {extraction_result['extractor']}")
    
    data = extraction_result['data']
    
    # 3. 顯示關鍵資訊
    print_section("📊 步驟 3: 關鍵資訊")
    
    if data.get('document_type') == 'credit_card':
        print_credit_card_info(data)
    elif data.get('document_type') == 'bank_statement':
        print_bank_statement_info(data)
    else:
        print(f"文件類型: {data.get('document_type', '未知')}")
    
    # 4. Schema 驗證
    print_section("✅ 步驟 4: Schema 驗證")
    
    validation = extraction_result.get('validation')
    if validation:
        if validation['valid']:
            print(f"✅ 通過驗證")
            print(f"   - Schema: {validation['schema_name']}")
            
            if validation.get('warnings'):
                print(f"\n⚠️  警告:")
                for warning in validation['warnings']:
                    print(f"   - {warning}")
        else:
            print(f"❌ 驗證失敗")
            print(f"   - Schema: {validation['schema_name']}")
            print(f"\n錯誤:")
            for error in validation['errors']:
                if isinstance(error, dict):
                    print(f"   - {error.get('message', error)}")
                else:
                    print(f"   - {error}")
    else:
        print("ℹ️  未進行驗證")
    
    # 5. 儲存 JSON
    if save_json:
        print_section("💾 步驟 5: 儲存 JSON")
        
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        filename = Path(pdf_path).stem
        json_file = output_dir / f"{filename}_extracted.json"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON 已儲存: {json_file}")
        
        # 儲存驗證報告
        if validation:
            report_file = output_dir / f"{filename}_validation.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(validation, f, ensure_ascii=False, indent=2)
            print(f"✅ 驗證報告已儲存: {report_file}")
    
    # 6. 摘要
    print_section("📈 摘要")
    
    print(f"""
✨ 提取完成！

📊 提取方式: {extraction_result['method']}
📄 文件類型: {data.get('document_type', '未知')}
✅ Schema 驗證: {'通過' if validation and validation['valid'] else '失敗' if validation else '未驗證'}

💡 提示：
   - 查看完整 JSON: cat {output_dir / f"{Path(pdf_path).stem}_extracted.json"}
   - 格式化顯示: cat output/*.json | jq .
   - 比較原始與提取: diff <(cat "{pdf_path}") <(cat output/*.json)
    """)


def print_credit_card_info(data: dict):
    """顯示信用卡資訊"""
    print("\n🏦 銀行名稱:", data.get('bank_name', ''))
    
    # 帳單期間
    period = data.get('statement_period', {})
    if period:
        print(f"\n📅 帳單期間:")
        print(f"   - 年月: {period.get('year', '')} 年 {period.get('month', '')} 月")
        if period.get('statement_date'):
            print(f"   - 結帳日: {period['statement_date']}")
    
    # 繳款資訊
    payment = data.get('payment_info', {})
    if payment:
        print(f"\n💰 繳款資訊:")
        print(f"   - 本期應繳: NT$ {payment.get('total_amount_due', 0):,.0f}")
        print(f"   - 最低應繳: NT$ {payment.get('minimum_payment', 0):,.0f}")
        if payment.get('due_date'):
            print(f"   - 繳款期限: {payment['due_date']}")
        if payment.get('auto_debit'):
            auto = payment['auto_debit']
            print(f"   - 自動扣繳: {'已設定' if auto.get('enabled') else '未設定'}")
            if auto.get('account_number'):
                print(f"     帳號: {auto['account_number']}")
    
    # 卡片資訊
    card = data.get('card_info', {})
    if card:
        print(f"\n💳 卡片資訊:")
        if card.get('card_type'):
            print(f"   - 卡片: {card['card_type']}")
        if card.get('card_last4'):
            print(f"   - 末4碼: {card['card_last4']}")
        if card.get('credit_limit'):
            print(f"   - 信用額度: NT$ {card['credit_limit']:,.0f}")
    
    # 利率資訊
    interest = data.get('interest_info', {})
    if interest:
        print(f"\n📊 利率資訊:")
        if interest.get('revolving_apr'):
            print(f"   - 循環利率: {interest['revolving_apr']}%")
        if interest.get('installment_apr'):
            print(f"   - 分期利率: {interest['installment_apr']}%")
    
    # 交易統計
    summary = data.get('summary', {})
    if summary:
        print(f"\n📈 交易統計:")
        print(f"   - 交易筆數: {summary.get('total_transactions', 0)}")
        if summary.get('total_purchases'):
            print(f"   - 消費總額: NT$ {summary['total_purchases']:,.0f}")
        if summary.get('total_payments'):
            print(f"   - 繳款總額: NT$ {summary['total_payments']:,.0f}")
    
    # 顯示前 5 筆交易
    transactions = data.get('transactions', [])
    if transactions:
        print(f"\n💸 最近交易 (前 5 筆):")
        for i, txn in enumerate(transactions[:5], 1):
            print(f"\n   {i}. {txn.get('description', '')}")
            print(f"      日期: {txn.get('transaction_date', '')}")
            print(f"      金額: NT$ {txn.get('amount', 0):,.0f}")
            if txn.get('transaction_type'):
                print(f"      類型: {txn['transaction_type']}")
        
        if len(transactions) > 5:
            print(f"\n   ... 還有 {len(transactions) - 5} 筆交易")


def print_bank_statement_info(data: dict):
    """顯示銀行對帳單資訊"""
    print("\n🏦 銀行名稱:", data.get('bank_name', ''))
    
    account = data.get('account_info', {})
    if account:
        print(f"\n💼 帳戶資訊:")
        print(f"   - 帳號: {account.get('account_number', '')}")
        print(f"   - 戶名: {account.get('account_name', '')}")
    
    balance = data.get('balance_info', {})
    if balance:
        print(f"\n💰 餘額資訊:")
        print(f"   - 期初餘額: NT$ {balance.get('opening_balance', 0):,.0f}")
        print(f"   - 期末餘額: NT$ {balance.get('closing_balance', 0):,.0f}")
        if balance.get('total_deposits'):
            print(f"   - 存款總額: NT$ {balance['total_deposits']:,.0f}")
        if balance.get('total_withdrawals'):
            print(f"   - 提款總額: NT$ {balance['total_withdrawals']:,.0f}")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='測試結構化資訊提取',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 基本測試（純規則提取）
  python test_extraction.py statement.pdf
  
  # 有密碼的 PDF
  python test_extraction.py statement.pdf --password A123456789
  
  # 啟用 AI fallback（規則失敗時使用 AI）
  python test_extraction.py statement.pdf --enable-ai
  
  # 儲存 JSON 結果
  python test_extraction.py statement.pdf --save-json
        """
    )
    
    parser.add_argument('pdf_file', help='PDF 檔案路徑')
    parser.add_argument('--password', '-p', help='PDF 密碼（如果有加密）')
    parser.add_argument('--enable-ai', '-a', action='store_true', 
                       help='啟用 AI fallback（規則失敗時使用）')
    parser.add_argument('--save-json', '-s', action='store_true',
                       help='儲存 JSON 結果到 output/ 目錄')
    
    args = parser.parse_args()
    
    # 檢查檔案
    if not Path(args.pdf_file).exists():
        print(f"❌ 錯誤: 找不到檔案 '{args.pdf_file}'")
        return 1
    
    # 執行測試
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 18 + "結構化資訊提取測試" + " " * 18 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        test_extraction(
            args.pdf_file,
            password=args.password,
            enable_ai=args.enable_ai,
            save_json=args.save_json
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

