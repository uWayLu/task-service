# 測試範例

## 使用 curl 測試 API

### 1. 健康檢查

```bash
curl http://localhost:5000/api/health
```

### 2. 測試銀行對帳單處理

```bash
curl -X POST http://localhost:5000/api/webhook/gmail \
  -F "file=@bank_statement.pdf" \
  -F "document_type=bank_statement" \
  -F "sender=bank@example.com" \
  -F "subject=您的銀行對帳單 2024年10月" \
  -F "date=2024-11-01"
```

### 3. 測試信用卡帳單處理

```bash
curl -X POST http://localhost:5000/api/webhook/gmail \
  -F "file=@credit_card_statement.pdf" \
  -F "document_type=credit_card" \
  -F "sender=card@bank.com" \
  -F "subject=信用卡帳單 2024-10" \
  -F "date=2024-11-01"
```

### 4. 測試交易通知處理

```bash
curl -X POST http://localhost:5000/api/webhook/gmail \
  -F "file=@transaction_notice.pdf" \
  -F "document_type=transaction_notice" \
  -F "sender=notify@bank.com" \
  -F "subject=交易通知 - 消費提醒" \
  -F "date=2024-11-18"
```

## 使用 Python 測試

### 基本測試

```python
import requests

# 測試健康檢查
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# 測試檔案上傳
files = {'file': open('statement.pdf', 'rb')}
data = {
    'document_type': 'bank_statement',
    'sender': 'bank@example.com',
    'subject': '銀行對帳單',
    'date': '2024-11-18'
}

response = requests.post(
    'http://localhost:5000/api/webhook/gmail',
    files=files,
    data=data
)

print(response.json())
```

### 使用測試腳本

專案已包含 `test_api.py` 測試腳本：

```bash
python test_api.py
```

## 模擬測試資料

### 銀行對帳單 PDF 內容範例

如果你沒有實際的 PDF 檔案，可以建立包含以下內容的測試 PDF：

```
銀行名稱：測試銀行
帳號：1234567890

對帳單期間：2024-10-01 至 2024-10-31

期初餘額：$50,000.00
期末餘額：$48,500.00

交易明細：
2024-10-05  轉帳支出     -$1,500.00
2024-10-10  ATM提款      -$2,000.00
2024-10-15  薪資入帳     +$10,000.00
2024-10-20  信用卡繳款   -$5,000.00
2024-10-25  超商消費     -$500.00

總存款：$10,000.00
總提款：$11,500.00
```

### 信用卡帳單 PDF 內容範例

```
銀行信用卡帳單
卡號：****-****-****-1234

帳單週期：2024-10-01 至 2024-10-31
繳款截止日：2024-11-20

本期應繳總額：$25,000.00
最低應繳金額：$2,000.00
上期結餘：$15,000.00
本期新增消費：$10,000.00

消費明細：
2024-10-05  超市購物      $1,500
2024-10-10  加油站        $800
2024-10-15  餐廳消費      $2,000
2024-10-20  網路購物      $3,500
2024-10-25  百貨公司      $2,200
```

## 預期回應格式

### 銀行對帳單回應

```json
{
  "status": "success",
  "message": "文件處理完成",
  "data": {
    "document_type": "bank_statement",
    "summary": {
      "account_number": "1234567890",
      "statement_period": {
        "dates": ["2024-10-01", "2024-10-31"]
      },
      "opening_balance": 50000.0,
      "closing_balance": 48500.0,
      "total_deposits": 10000.0,
      "total_withdrawals": 11500.0,
      "transaction_count": 5
    },
    "transactions": [...],
    "metadata": {
      "sender": "bank@example.com",
      "subject": "銀行對帳單",
      "date": "2024-11-18"
    },
    "total_pages": 1,
    "processed_at": "2024-11-18T10:30:00.000000"
  }
}
```

### 錯誤回應範例

```json
{
  "status": "error",
  "message": "未提供 PDF 檔案"
}
```

## 效能測試

### 使用 Apache Bench

```bash
# 安裝 Apache Bench
sudo apt-get install apache2-utils

# 測試健康檢查端點（1000 請求，10 併發）
ab -n 1000 -c 10 http://localhost:5000/api/health
```

### 使用 wrk

```bash
# 安裝 wrk
sudo apt-get install wrk

# 測試（持續 30 秒，10 執行緒，100 連線）
wrk -t10 -c100 -d30s http://localhost:5000/api/health
```

## 除錯技巧

### 啟用詳細日誌

在 `.env` 檔案中設定：

```env
FLASK_DEBUG=1
```

### 查看處理後的檔案

如果要保留上傳的檔案以供檢查，設定：

```env
DELETE_AFTER_PROCESS=false
```

檔案將保存在 `uploads/` 資料夾中。

### 使用 Python 偵錯器

```python
# 在 app.py 中加入斷點
import pdb; pdb.set_trace()
```

