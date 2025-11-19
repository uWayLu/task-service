# Task Service API - 專案總結

## 專案概述

Task Service API 是一個專為處理 Gmail Apps Script webhook 而設計的 Flask 應用程式，主要用於解析和處理財務相關的 PDF 文件，包括銀行對帳單、信用卡帳單和交易通知。

## 核心功能

### 1. Webhook 接收
- 接收來自 Gmail Apps Script 的 POST 請求
- 處理 multipart/form-data 格式的檔案上傳
- 支援額外的元資料參數（寄件者、主旨、日期等）

### 2. PDF 解析
- **文字提取**：使用 pdfplumber 進行高精度文字提取
- **元資料提取**：使用 PyPDF2 提取 PDF 基本資訊
- **智能解析**：自動識別數字、日期、金額等關鍵資訊

### 3. 文件分類處理

#### 銀行對帳單 (bank_statement)
提取資訊：
- 帳號
- 對帳期間
- 期初餘額
- 期末餘額
- 總存款金額
- 總提款金額
- 交易記錄列表

#### 信用卡帳單 (credit_card)
提取資訊：
- 卡號（遮罩格式）
- 帳單週期
- 繳款截止日
- 應繳總額
- 最低應繳金額
- 上期結餘
- 本期新增消費
- 消費明細列表

#### 交易通知 (transaction_notice)
提取資訊：
- 交易日期
- 商家名稱
- 交易金額
- 交易類型（消費/退款/轉帳/提款）

### 4. 回應格式
統一的 JSON 回應格式：
```json
{
  "status": "success",
  "message": "文件處理完成",
  "data": {
    "document_type": "...",
    "summary": { ... },
    "transactions": [ ... ],
    "metadata": { ... },
    "total_pages": 0,
    "processed_at": "2024-11-18T10:30:00"
  }
}
```

## 技術架構

### 後端框架
- **Flask 3.0.0**：輕量級 Web 框架
- **Gunicorn**：生產級 WSGI HTTP 伺服器
- **Flask-CORS**：跨域資源共享支援

### PDF 處理
- **pdfplumber**：高精度 PDF 文字提取
- **PyPDF2**：PDF 元資料與結構處理

### 環境管理
- **python-dotenv**：環境變數管理
- **虛擬環境**：隔離專案依賴

## 專案結構

```
task-service/
│
├── app.py                          # Flask 主應用程式
│   ├── 路由定義
│   ├── 錯誤處理
│   └── 應用配置
│
├── config.py                       # 配置管理
│   ├── 開發環境配置
│   ├── 生產環境配置
│   └── 配置工廠
│
├── utils/                          # 工具模組
│   ├── __init__.py
│   ├── pdf_parser.py              # PDF 解析器
│   │   ├── 文字提取
│   │   ├── 元資料提取
│   │   ├── 數字提取
│   │   ├── 日期提取
│   │   └── 金額提取
│   │
│   └── document_processor.py      # 文件處理器
│       ├── 文件分類
│       ├── 銀行對帳單處理
│       ├── 信用卡帳單處理
│       ├── 交易通知處理
│       └── 資訊提取輔助方法
│
├── examples/                       # 範例程式碼
│   ├── gmail_webhook.gs           # Google Apps Script 整合範例
│   └── test_samples.md            # 測試範例說明
│
├── uploads/                        # 上傳檔案暫存目錄
│
├── requirements.txt                # Python 依賴清單
├── Dockerfile                      # Docker 映像定義
├── docker-compose.yml              # Docker Compose 配置
├── .dockerignore                   # Docker 忽略檔案
├── .gitignore                      # Git 忽略檔案
├── run.sh                          # 啟動腳本
├── test_api.py                     # API 測試腳本
│
└── docs/                           # 文件目錄
    ├── README.md                   # 專案說明
    ├── QUICKSTART.md              # 快速開始指南
    ├── DEPLOYMENT.md              # 部署指南
    ├── CHANGELOG.md               # 更新日誌
    └── PROJECT_SUMMARY.md         # 專案總結（本檔案）
```

## API 端點

### 1. 健康檢查
```
GET /
GET /api/health
```

### 2. Gmail Webhook
```
POST /api/webhook/gmail

參數：
- file: PDF 檔案（必填）
- document_type: 文件類型（必填）
- sender: 寄件者（選填）
- subject: 主旨（選填）
- date: 日期（選填）
```

## 工作流程

```
Gmail 收到郵件
    ↓
Apps Script 觸發
    ↓
提取 PDF 附件
    ↓
POST 到 /api/webhook/gmail
    ↓
Task Service 接收請求
    ↓
驗證檔案類型與大小
    ↓
儲存到 uploads/
    ↓
PDF 解析（提取文字）
    ↓
文件分類處理
    ↓
提取關鍵資訊
    ↓
返回 JSON 摘要
    ↓
Apps Script 接收回應
    ↓
更新 Google Sheets/Calendar
```

## 部署選項

### 1. 本地開發
```bash
./run.sh
```

### 2. Docker
```bash
docker-compose up -d
```

### 3. 雲端平台
- Heroku
- Railway
- Render
- Google Cloud Run
- AWS ECS

### 4. 傳統伺服器
- Nginx + Gunicorn
- Apache + mod_wsgi
- Systemd service

## 安全性考量

### 已實作
✅ 檔案類型白名單（只接受 PDF）
✅ 檔案大小限制（預設 16MB）
✅ 安全的檔案名稱處理
✅ 環境變數保護敏感資訊
✅ CORS 設定
✅ 錯誤訊息不暴露內部資訊

### 建議實作
⚠️ API 金鑰認證
⚠️ Rate Limiting
⚠️ Webhook 簽名驗證
⚠️ HTTPS 加密
⚠️ 請求日誌記錄
⚠️ 定期安全性更新

## 效能考量

### 最佳化措施
- 處理後自動刪除檔案
- Gunicorn 多 Worker 配置
- Docker 映像分層優化
- 適當的超時設定

### 效能限制
- PDF 大小：16MB
- 處理時間：取決於 PDF 複雜度
- 併發處理：取決於 Worker 數量

## 監控與日誌

### 健康檢查
```bash
curl http://localhost:5000/api/health
```

### 日誌位置
- 應用日誌：stdout/stderr
- 存取日誌：Gunicorn access log
- 錯誤日誌：Gunicorn error log

### 推薦監控工具
- Prometheus + Grafana
- ELK Stack（Elasticsearch, Logstash, Kibana）
- Cloud provider 原生監控

## 整合範例

### Google Apps Script
```javascript
function processEmail(message) {
  var attachment = message.getAttachments()[0];
  var response = UrlFetchApp.fetch(API_URL, {
    method: 'post',
    payload: {
      'file': attachment.copyBlob(),
      'document_type': 'bank_statement',
      'sender': message.getFrom(),
      'subject': message.getSubject()
    }
  });
  
  var result = JSON.parse(response.getContentText());
  updateGoogleSheets(result.data);
}
```

### Python Client
```python
import requests

files = {'file': open('statement.pdf', 'rb')}
data = {'document_type': 'bank_statement'}

response = requests.post(
    'http://api.example.com/api/webhook/gmail',
    files=files,
    data=data
)

result = response.json()
```

## 測試策略

### 單元測試
- PDF 解析器測試
- 文件處理器測試
- 資訊提取測試

### 整合測試
- API 端點測試
- 檔案上傳測試
- 錯誤處理測試

### 測試工具
```bash
# 使用內建測試腳本
python test_api.py

# 使用 curl
curl -X POST http://localhost:5000/api/webhook/gmail \
  -F "file=@test.pdf" \
  -F "document_type=bank_statement"
```

## 擴展性考量

### 水平擴展
- 使用 Load Balancer
- 無狀態設計
- 共享儲存（如 S3）

### 垂直擴展
- 增加 CPU/記憶體
- 調整 Worker 數量
- 優化 PDF 處理邏輯

### 功能擴展
- 新增文件類型：修改 `document_processor.py`
- 新增提取邏輯：擴展 `pdf_parser.py`
- 新增 API 端點：修改 `app.py`

## 常見使用案例

### 案例 1：自動記帳
Gmail → Apps Script → Task Service → Google Sheets

### 案例 2：帳單提醒
Gmail → Apps Script → Task Service → Google Calendar

### 案例 3：消費分析
Gmail → Apps Script → Task Service → 資料庫 → Dashboard

## 故障排除

### PDF 解析失敗
- 確認 PDF 非掃描檔
- 檢查 PDF 編碼
- 查看詳細錯誤日誌

### API 呼叫失敗
- 確認服務運行中
- 檢查網路連線
- 驗證請求格式

### 記憶體不足
- 減少 Worker 數量
- 增加伺服器記憶體
- 限制同時處理數量

## 未來發展方向

### 短期（v1.1）
- API 認證
- Rate Limiting
- OCR 支援

### 中期（v1.2）
- 資料庫整合
- 非同步處理
- 管理介面

### 長期（v2.0）
- AI 文件分類
- 智能資料提取
- 多租戶支援

## 貢獻指南

### 如何貢獻
1. Fork 專案
2. 建立 feature branch
3. 提交變更
4. 開啟 Pull Request

### 程式碼規範
- 遵循 PEP 8
- 加入適當的註解
- 編寫單元測試
- 更新文件

## 授權

MIT License

## 聯絡資訊

- GitHub Issues：報告問題
- Pull Requests：貢獻代碼
- Discussions：功能討論

## 資源連結

### 內部文件
- [README.md](README.md) - 專案說明
- [QUICKSTART.md](QUICKSTART.md) - 快速開始
- [DEPLOYMENT.md](DEPLOYMENT.md) - 部署指南
- [CHANGELOG.md](CHANGELOG.md) - 更新日誌

### 外部資源
- Flask 文件：https://flask.palletsprojects.com/
- pdfplumber 文件：https://github.com/jsvine/pdfplumber
- Google Apps Script：https://developers.google.com/apps-script

---

**版本**：1.0.0  
**最後更新**：2024-11-18  
**狀態**：Production Ready ✅

