# Task Service API

一個用於處理 Gmail Apps Script Webhook 的財務文件處理服務，專門處理銀行對帳單、信用卡帳單和交易通知等 PDF 文件。

## 功能特色

- ✅ 接收來自 Gmail Apps Script 的 Webhook 請求
- ✅ 處理 PDF 檔案上傳
- ✅ 自動解析 PDF 內容
- ✅ 智能識別文件類型（對帳單、信用卡帳單、交易通知）
- ✅ 提取關鍵財務資訊
- ✅ 返回結構化摘要資料給 Apps Script

## 技術架構

- **Framework**: Flask 3.0.0
- **PDF 處理**: pdfplumber + PyPDF2
- **語言**: Python 3.8+

## 專案結構

```
task-service/
├── app.py                          # Flask 主應用程式
├── config.py                       # 配置檔案
├── requirements.txt                # Python 依賴套件
├── .gitignore                      # Git 忽略檔案
├── run.sh                          # 啟動腳本
├── test_api.py                     # API 測試腳本
├── utils/                          # 工具模組
│   ├── __init__.py
│   ├── pdf_parser.py              # PDF 解析器
│   └── document_processor.py      # 文件處理器
├── uploads/                        # 上傳檔案暫存（自動建立）
└── README.md
```

## 快速開始

### 1. 環境設定

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate   # Windows

# 安裝依賴套件
pip install -r requirements.txt
```

### 2. 設定環境變數

建立 `.env` 檔案：

```env
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here
PORT=5000
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216
DELETE_AFTER_PROCESS=true
```

### 3. 啟動服務

#### 方法 A: 使用啟動腳本（推薦）

```bash
./run.sh
```

#### 方法 B: 手動啟動

```bash
python app.py
```

服務將運行在 `http://localhost:5000`

### 4. 測試服務

```bash
# 測試健康檢查
curl http://localhost:5000/api/health

# 使用測試腳本
python test_api.py
```

## API 端點

### 1. 健康檢查

```
GET /
GET /api/health
```

**回應範例:**
```json
{
  "status": "healthy",
  "service": "task-service",
  "upload_folder": "./uploads"
}
```

### 2. Gmail Webhook

```
POST /api/webhook/gmail
```

**請求參數:**

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| file | File | ✅ | PDF 檔案 |
| document_type | String | ✅ | 文件類型 |
| sender | String | ❌ | 寄件者信箱 |
| subject | String | ❌ | 郵件主旨 |
| date | String | ❌ | 郵件日期 |

**文件類型 (document_type):**
- `bank_statement` - 銀行對帳單
- `credit_card` - 信用卡帳單
- `transaction_notice` - 交易通知
- `unknown` - 未知類型

**請求範例 (curl):**

```bash
curl -X POST http://localhost:5000/api/webhook/gmail \
  -F "file=@statement.pdf" \
  -F "document_type=bank_statement" \
  -F "sender=bank@example.com" \
  -F "subject=您的銀行對帳單" \
  -F "date=2024-11-18"
```

**回應範例 (銀行對帳單):**

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
      "opening_balance": 50000.00,
      "closing_balance": 48500.00,
      "total_deposits": 10000.00,
      "total_withdrawals": 11500.00,
      "transaction_count": 25
    },
    "transactions": [
      {
        "date": "2024-10-15",
        "amount": 1500.00,
        "description": "轉帳支出"
      }
    ],
    "metadata": {
      "sender": "bank@example.com",
      "subject": "您的銀行對帳單",
      "date": "2024-11-18"
    },
    "total_pages": 3,
    "processed_at": "2024-11-18T10:30:00"
  }
}
```

**回應範例 (信用卡帳單):**

```json
{
  "status": "success",
  "message": "文件處理完成",
  "data": {
    "document_type": "credit_card",
    "summary": {
      "card_number": "****-****-****-1234",
      "billing_period": {
        "start_date": "2024-10-01",
        "end_date": "2024-10-31"
      },
      "due_date": "2024-11-20",
      "minimum_payment": 2000.00,
      "total_amount_due": 25000.00,
      "previous_balance": 15000.00,
      "new_charges": 10000.00,
      "transaction_count": 15
    },
    "transactions": [...],
    "metadata": {...},
    "total_pages": 5,
    "processed_at": "2024-11-18T10:30:00"
  }
}
```

## 與 Google Apps Script 整合

### Apps Script 範例

```javascript
function onEmailReceived(e) {
  // 取得郵件附件
  var attachments = GmailApp.getMessageById(e.messageId).getAttachments();
  
  attachments.forEach(function(attachment) {
    if (attachment.getContentType() === 'application/pdf') {
      // 準備要傳送的資料
      var formData = {
        'file': attachment.copyBlob(),
        'document_type': detectDocumentType(e.subject),
        'sender': e.from,
        'subject': e.subject,
        'date': e.date
      };
      
      // 呼叫 Task Service API
      var response = UrlFetchApp.fetch('https://your-service-url/api/webhook/gmail', {
        method: 'post',
        payload: formData
      });
      
      var result = JSON.parse(response.getContentText());
      
      // 根據回應類型處理結果
      if (result.data.document_type === 'bank_statement') {
        updateGoogleSheets(result.data);
      } else if (result.data.document_type === 'credit_card') {
        updateGoogleCalendar(result.data);
      }
    }
  });
}

function detectDocumentType(subject) {
  if (subject.includes('對帳單')) return 'bank_statement';
  if (subject.includes('信用卡') || subject.includes('帳單')) return 'credit_card';
  if (subject.includes('交易通知')) return 'transaction_notice';
  return 'unknown';
}

function updateGoogleSheets(data) {
  // 更新 Google Sheets 邏輯
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('對帳單');
  sheet.appendRow([
    data.summary.account_number,
    data.summary.closing_balance,
    data.processed_at
  ]);
}

function updateGoogleCalendar(data) {
  // 更新 Google Calendar 邏輯
  var calendar = CalendarApp.getDefaultCalendar();
  calendar.createEvent(
    '信用卡帳單到期',
    new Date(data.summary.due_date),
    new Date(data.summary.due_date),
    {
      description: '應繳金額: ' + data.summary.total_amount_due
    }
  );
}
```

## PDF 解析功能

### 支援的資訊提取

#### 銀行對帳單
- 帳號
- 對帳期間
- 期初/期末餘額
- 總存款/總提款金額
- 交易記錄

#### 信用卡帳單
- 卡號（遮罩）
- 帳單週期
- 繳款截止日
- 應繳總額
- 最低應繳金額
- 消費明細

#### 交易通知
- 交易日期
- 交易金額
- 商家資訊
- 交易類型

## 部署建議

### 使用 Gunicorn (生產環境)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用 Docker

建立 `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

建立並運行容器:

```bash
docker build -t task-service .
docker run -p 5000:5000 -e SECRET_KEY=your-secret task-service
```

## 開發指南

### 新增文件處理器

1. 在 `utils/document_processor.py` 中新增處理方法
2. 在 `process_document` 方法中註冊新類型
3. 實作解析邏輯

### 測試

```bash
# 安裝測試依賴
pip install pytest pytest-cov

# 執行測試
pytest

# 產生覆蓋率報告
pytest --cov=. --cov-report=html
```

## 安全性建議

1. **SECRET_KEY**: 在生產環境中使用強隨機金鑰
2. **HTTPS**: 部署時使用 HTTPS 協定
3. **認證**: 建議加入 API 金鑰或 Token 驗證
4. **檔案驗證**: 已內建 PDF 檔案類型和大小檢查
5. **日誌**: 建議配置適當的日誌記錄

## 故障排除

### 常見問題

**Q: PDF 解析失敗**
A: 確保 PDF 不是掃描檔（圖片），或考慮加入 OCR 功能

**Q: 中文內容無法正確解析**
A: 檢查 PDF 是否使用正確的中文編碼

**Q: 記憶體使用過高**
A: 調整 `MAX_CONTENT_LENGTH` 限制檔案大小，或增加 Worker 數量

## 授權

MIT License

## 聯絡資訊

如有問題或建議，歡迎提出 Issue。

---

**注意**: 本服務處理財務敏感資訊，請確保在安全的環境中運行，並遵守相關隱私法規。
