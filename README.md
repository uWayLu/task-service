# Task Service API

Gmail Apps Script Webhook 財務文件處理服務

## 功能摘要

接收 Gmail webhook → 解析 PDF 附件 → 提取財務資訊 → 返回結構化資料

支援文件類型：
- 📊 銀行對帳單
- 💳 信用卡帳單  
- 💰 交易通知

## 快速開始

```bash
# 1. 安裝依賴
./run.sh

# 2. 啟動服務
python app.py

# 3. 測試
curl http://localhost:12345/
```

## 專案架構

```
task-service/
├── app.py              # 主程式 (Blueprint 架構)
├── api/                # API 路由模組
│   ├── health.py       # 健康檢查
│   ├── webhook.py      # Webhook 處理
│   └── document.py     # 文件管理
├── utils/              # 工具模組
│   ├── pdf_parser.py   # PDF 解析
│   └── document_processor.py  # 文件處理
├── docs/               # 詳細文件
└── examples/           # 範例程式碼
```

## API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | 服務資訊 |
| `/api/health` | GET | 健康檢查 |
| `/api/webhook/gmail` | POST | 處理 PDF webhook |
| `/api/documents/types` | GET | 文件類型列表 |

## 測試 PDF 解析

```bash
# 方法 1: Console 測試（推薦）
python test_pdf_parser.py your-file.pdf

# 方法 2: HTTP API
curl -X POST http://localhost:12345/api/test/parse-pdf \
  -F "file=@your-file.pdf"
```

## TODO

### 待完成功能
- [ ] API 金鑰認證
- [ ] Rate Limiting
- [ ] OCR 支援（掃描檔）
- [ ] 資料庫整合
- [ ] 非同步處理
- [ ] 管理後台

### 計劃改進
- [ ] 提升 PDF 解析準確度
- [ ] 支援更多銀行格式
- [ ] 批次處理功能
- [ ] Webhook 重試機制

## 文件

- 📚 [快速開始指南](docs/QUICKSTART.md)
- 🚀 [部署指南](docs/DEPLOYMENT.md)
- 🔧 [如何新增 API](docs/HOW_TO_ADD_API.md)
- 📝 [更新日誌](docs/CHANGELOG.md)
- 🏗️ [專案總結](docs/PROJECT_SUMMARY.md)

## 技術堆疊

- Flask 3.0.0 - Web 框架
- pdfplumber 0.11.0 - PDF 解析
- PyPDF2 3.0.1 - PDF 元資料
- Gunicorn 21.2.0 - WSGI 伺服器

## 授權

MIT License

---

**需要協助？** 查看 [文件目錄](docs/) 或提交 Issue
