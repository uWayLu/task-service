# Task Service API

Gmail Apps Script Webhook 財務文件處理服務

## 功能摘要

接收 Gmail webhook → 解析 PDF 附件 → 提取財務資訊 → 返回結構化資料

### 支援文件類型

- 📊 銀行對帳單
- 💳 信用卡帳單  
- 💰 交易通知

### 核心功能

- 🔒 **密碼保護 PDF**：自動嘗試預設密碼或手動提供
- 🛡️ **個資遮罩保護**：自動偵測並遮罩敏感資訊（身分證、電話、地址等）
- 🤖 **AI 智慧分析**：整合 OpenAI/Claude 進行文件分析
- ✅ **Schema 驗證**：使用 JSON Schema 驗證提取結果
- 🖥️ **雙介面支援**：HTTP API + Console CLI

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 啟動服務

```bash
# HTTP API 服務
python app.py

# 或使用 Console CLI
python cli.py --help
```

### 3. 測試

```bash
# 測試 HTTP API
curl http://localhost:12345/api/health

# 測試 Console CLI
python cli.py parse test_files/113年08月富邦.pdf
```

## 使用方式

### Console CLI（推薦）

```bash
# 基本 PDF 解析
python cli.py parse document.pdf

# 解析有密碼的 PDF
python cli.py parse document.pdf --password A123456789

# 遮罩個資
python cli.py mask document.pdf --output masked.txt

# AI 分析（自動遮罩）
python cli.py analyze document.pdf --provider openai

# 完整流程（解析→遮罩→AI分析→驗證）
python cli.py process document.pdf --ai --validate
```

### HTTP API

```bash
# 處理 PDF webhook
curl -X POST http://localhost:12345/api/webhook/gmail \
  -F "file=@statement.pdf" \
  -F "document_type=bank_statement" \
  -F "password=A123456789" \
  -F "mask_privacy=true"

# AI 分析文件
curl -X POST http://localhost:12345/api/ai/mask-and-analyze \
  -F "file=@statement.pdf" \
  -F "provider=openai"

# 偵測敏感資訊
curl -X POST http://localhost:12345/api/ai/detect-sensitive \
  -F "file=@statement.pdf"
```

## 專案架構

```
task-service/
├── app.py                 # Flask 主程式 (Blueprint 架構)
├── cli.py                 # Console CLI 工具 ⭐ 新增
│
├── api/                   # API 路由模組
│   ├── health.py          # 健康檢查
│   ├── webhook.py         # Webhook 處理（支援密碼 + 遮罩）
│   ├── document.py        # 文件管理
│   ├── test.py            # 測試 API
│   ├── docs.py            # 文件瀏覽
│   └── ai.py              # AI 整合 API ⭐
│
├── utils/                 # 工具模組
│   ├── pdf_parser.py      # PDF 解析（支援密碼）
│   ├── document_processor.py      # 文件處理
│   ├── privacy_masker.py          # 個資遮罩 ⭐
│   ├── ai_integrator.py           # AI 整合 ⭐
│   ├── schema_validator.py        # Schema 驗證
│   ├── extraction_manager.py      # 提取管理器
│   └── extractors/                # 結構化提取器
│
├── docs/                  # 📚 詳細文件
├── todo/                  # 📝 TODO 管理資料夾 ⭐ 新增
├── schemas/               # JSON Schema 定義
├── test_files/            # 測試 PDF
└── output/                # 處理結果輸出
```

## API 端點

| 端點 | 方法 | 說明 | 密碼 | 遮罩 |
|------|------|------|------|------|
| `/` | GET | 服務資訊 | - | - |
| `/api/health` | GET | 健康檢查 | - | - |
| `/api/webhook/gmail` | POST | 處理 PDF webhook | ✅ | ✅ |
| `/api/documents/types` | GET | 文件類型列表 | - | - |
| `/api/test/parse-pdf` | POST | 測試 PDF 解析 | ✅ | - |
| `/api/ai/analyze-document` | POST | AI 分析（不遮罩） | ✅ | ❌ |
| `/api/ai/mask-and-analyze` | POST | AI 分析（遮罩） | ✅ | ✅ |
| `/api/ai/detect-sensitive` | POST | 偵測敏感資訊 | ✅ | ✅ |
| `/api/docs` | GET | 文件瀏覽 | - | - |

## 功能詳解

### 🔒 密碼保護 PDF

#### 方式 1：預設密碼（推薦）

在 `.env` 設定預設密碼，系統自動嘗試：

```env
# .env
PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678
```

設定後無需每次提供密碼！

#### 方式 2：手動提供密碼

```bash
# Console
python cli.py parse encrypted.pdf --password A123456789

# HTTP API
curl -X POST http://localhost:12345/api/webhook/gmail \
  -F "file=@encrypted.pdf" \
  -F "password=A123456789"
```

**詳細說明：** [PDF 密碼處理指南](docs/PDF_PASSWORD.md)

### 🛡️ 個資遮罩

自動偵測並遮罩敏感個人資料：

- 身分證字號
- 手機號碼
- 市話
- 信用卡號
- 電子郵件
- 銀行帳號
- 地址
- 出生日期

```bash
# Console
python cli.py mask document.pdf --output masked.txt

# HTTP API（在 webhook 中啟用）
curl -X POST http://localhost:12345/api/webhook/gmail \
  -F "file=@statement.pdf" \
  -F "mask_privacy=true"
```

**詳細說明：** [個資遮罩功能](docs/PRIVACY_MASKING.md)

### 🤖 AI 智慧分析

支援 OpenAI/Claude 自動分析金融文件並提取關鍵資訊。

```bash
# 設定 API Key
export OPENAI_API_KEY=sk-your-key-here
# 或
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Console（自動遮罩個資）
python cli.py analyze document.pdf --provider openai

# HTTP API
curl -X POST http://localhost:12345/api/ai/mask-and-analyze \
  -F "file=@statement.pdf" \
  -F "provider=openai"
```

**詳細說明：** [AI 整合說明](docs/AI_INTEGRATION.md)

### ✅ Schema 驗證

使用 JSON Schema 定義和驗證提取結果：

```bash
# Console
python cli.py validate extracted_data.json --schema schemas/bank_statement_schema.json

# 完整流程（自動驗證）
python cli.py process document.pdf --validate
```

Schema 定義位於 `schemas/` 資料夾：
- `bank_statement_schema.json` - 銀行對帳單
- `credit_card_schema.json` - 信用卡帳單

## TODO 管理

新功能：在 `todo/` 資料夾撰寫待辦事項和需求，供 AI 解析與完成！

```bash
# 1. 複製範本
cp todo/template.md todo/active/my_feature.md

# 2. 編輯待辦事項
vim todo/active/my_feature.md

# 3. 請 AI 實現
"請實現 todo/active/my_feature.md 中的功能"
```

**詳細說明：** [TODO 管理指南](todo/README.md)

## 測試

### Console 測試

```bash
# PDF 解析
python test_pdf_parser.py test_files/113年08月富邦.pdf

# 有密碼的 PDF
python test_pdf_parser.py encrypted.pdf --password A123456789

# 個資遮罩
python test_privacy.py

# AI 分析
python test_ai.py
```

### HTTP API 測試

```bash
# 健康檢查
curl http://localhost:12345/api/health

# 測試 PDF 解析
curl -X POST http://localhost:12345/api/test/parse-pdf \
  -F "file=@test_files/113年08月富邦.pdf"

# Webhook 測試
./test_webhook.sh test_files/113年08月富邦.pdf
```

### 使用 CLI 測試

```bash
# 解析
python cli.py parse test_files/113年08月富邦.pdf

# 遮罩
python cli.py mask test_files/113年08月富邦.pdf --output output/masked.txt

# 完整流程
python cli.py process test_files/113年08月富邦.pdf --ai --validate
```

## 部署

### Docker

```bash
docker-compose up -d
```

### 傳統部署

```bash
# 使用 gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**詳細說明：** [部署指南](docs/DEPLOYMENT.md)

## 文件

### 快速開始
- 📚 [快速開始指南](docs/QUICKSTART.md) - 5 分鐘上手

### 開發相關
- 🔧 [如何新增 API](docs/HOW_TO_ADD_API.md) - 完整開發指南
- 🏗️ [Flask 專案結構](docs/FLASK_STRUCTURE.md) - 架構說明
- 📁 [檔案組織說明](docs/FILE_ORGANIZATION.md) - 檔案放置規則

### 功能文件
- 🔒 [PDF 密碼處理](docs/PDF_PASSWORD.md) - 密碼配置與使用 ⭐
- 🧪 [PDF 測試指南](docs/PDF_TESTING.md) - 測試方法
- 🛡️ [個資遮罩功能](docs/PRIVACY_MASKING.md) - 個資保護 ⭐
- 🤖 [AI 整合說明](docs/AI_INTEGRATION.md) - AI API 使用 ⭐

### 部署與維護
- 🚀 [部署指南](docs/DEPLOYMENT.md) - 完整部署方案
- 📝 [更新日誌](docs/CHANGELOG.md) - 版本歷史
- 📊 [專案總結](docs/PROJECT_SUMMARY.md) - 技術架構

### 線上文件
```bash
# 啟動服務後訪問
http://localhost:12345/api/docs
```

## 環境變數配置

```env
# Flask 基本配置
SECRET_KEY=your-super-secret-key-here
PORT=5000
FLASK_DEBUG=0

# 檔案上傳
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216
DELETE_AFTER_PROCESS=true

# PDF 密碼（預設密碼）
PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678

# AI API Keys（可選）
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# 功能開關
ENABLE_DOCS_API=true
```

複製並編輯：

```bash
cp .env.example .env
vim .env
```

## 技術堆疊

- **Flask 3.0.0** - Web 框架
- **pdfplumber 0.11.0** - PDF 文字提取
- **PyPDF2 3.0.1** - PDF 元資料與加密處理
- **requests 2.31.0** - HTTP 請求（AI API）
- **jsonschema 4.20.0** - JSON Schema 驗證
- **gunicorn 21.2.0** - WSGI 伺服器
- **markdown 3.5.1** - 文件渲染

## TODO

### 已完成 ✅
- [x] PDF 密碼保護支援
- [x] 個資遮罩保護
- [x] AI 智慧分析（OpenAI/Claude）
- [x] Console CLI 工具
- [x] 結構化資料提取
- [x] Schema 驗證
- [x] 需求管理資料夾

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
- [ ] 單元測試完善

## 需要協助？

- 📚 查看 [文件目錄](docs/)
- 🌐 訪問 [線上文件](http://localhost:12345/api/docs)
- 📝 在 [todo/](todo/) 撰寫待辦事項
- 🐛 提交 Issue

## 授權

MIT License

---

**注意**：本服務處理財務敏感資訊，請確保在安全的環境中運行，並使用 HTTPS 傳輸密碼。

**最後更新：** 2024-11-24
