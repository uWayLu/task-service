"""
API 測試腳本
用於測試 webhook endpoint
"""
import requests
import os


def test_health_check():
    """測試健康檢查端點"""
    print("測試健康檢查端點...")
    response = requests.get('http://localhost:5000/api/health')
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {response.json()}\n")


def test_webhook_with_file(pdf_path, document_type='bank_statement'):
    """
    測試 webhook 端點
    
    Args:
        pdf_path: PDF 檔案路徑
        document_type: 文件類型
    """
    print(f"測試 webhook 端點 (文件類型: {document_type})...")
    
    if not os.path.exists(pdf_path):
        print(f"錯誤: 找不到檔案 {pdf_path}")
        return
    
    url = 'http://localhost:5000/api/webhook/gmail'
    
    # 準備檔案和表單資料
    files = {
        'file': open(pdf_path, 'rb')
    }
    
    data = {
        'document_type': document_type,
        'sender': 'bank@example.com',
        'subject': '您的銀行對帳單',
        'date': '2024-11-18'
    }
    
    try:
        response = requests.post(url, files=files, data=data)
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}\n")
    except Exception as e:
        print(f"錯誤: {str(e)}\n")
    finally:
        files['file'].close()


def test_webhook_without_file():
    """測試沒有檔案的情況"""
    print("測試沒有檔案的錯誤處理...")
    url = 'http://localhost:5000/api/webhook/gmail'
    data = {'document_type': 'bank_statement'}
    
    response = requests.post(url, data=data)
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {response.json()}\n")


if __name__ == '__main__':
    print("=" * 50)
    print("Task Service API 測試")
    print("=" * 50 + "\n")
    
    # 測試健康檢查
    test_health_check()
    
    # 測試沒有檔案的情況
    test_webhook_without_file()
    
    # 測試有檔案的情況（需要提供實際的 PDF 檔案路徑）
    # test_webhook_with_file('path/to/your/test.pdf', 'bank_statement')
    # test_webhook_with_file('path/to/your/test.pdf', 'credit_card')
    # test_webhook_with_file('path/to/your/test.pdf', 'transaction_notice')
    
    print("\n提示: 若要測試檔案上傳功能，請解除註解並提供實際的 PDF 檔案路徑")

