# Task Service API

Gmail Apps Script Webhook 財務文件處理服務

## 功能摘要

接收 Gmail webhook → 解析 PDF 附件 → 提取財務資訊 → 返回結構化資料

支援文件類型：
- 📊 銀行對帳單
- 💳 信用卡帳單  
- 💰 交易通知
- 🔒 **支援密碼保護的 PDF**
- 🛡️ **自動個資遮罩保護**
- 🤖 **AI 智慧分析（OpenAI/Claude）**

## 快速開始

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 啟動服務
python app.py

# 3. 測試（無密碼 PDF）
curl http://localhost:12345/api/health

# 4. 測試（有密碼 PDF）
python test_pdf_parser.py your-file.pdf --password YOUR_PASSWORD
```

## 專案架構

```
task-service/
├── app.py              # 主程式 (Blueprint 架構)
├── api/                # API 路由模組
│   ├── health.py       # 健康檢查
│   ├── webhook.py      # Webhook 處理（支援密碼 + 個資遮罩）
│   ├── document.py     # 文件管理
│   ├── test.py         # 測試 API
│   ├── docs.py         # 文件瀏覽
│   └── ai.py           # AI 整合 API ⭐ 新增
├── utils/              # 工具模組
│   ├── pdf_parser.py   # PDF 解析（支援密碼）
│   ├── document_processor.py  # 文件處理
│   ├── privacy_masker.py      # 個資遮罩 ⭐ 新增
│   └── ai_integrator.py       # AI 整合 ⭐ 新增
├── docs/               # 詳細文件
└── examples/           # 範例程式碼
```

## API 端點

| 端點 | 方法 | 說明 | 支援密碼 | 個資遮罩 |
|------|------|------|---------|---------|
| `/` | GET | 服務資訊 | - | - |
| `/api/health` | GET | 健康檢查 | - | - |
| `/api/webhook/gmail` | POST | 處理 PDF webhook | ✅ | ✅ |
| `/api/documents/types` | GET | 文件類型列表 | - | - |
| `/api/test/parse-pdf` | POST | 測試 PDF 解析 | ✅ | - |
| `/api/docs` | GET | 文件瀏覽 | - | - |
| `/api/ai/analyze-document` | POST | AI 分析文件（不遮罩） | ✅ | ❌ |
| `/api/ai/mask-and-analyze` | POST | AI 分析文件（遮罩個資） | ✅ | ✅ |
| `/api/ai/detect-sensitive` | POST | 偵測敏感資訊 | ✅ | ✅ |
| `/api/ai/mask-types` | GET | 支援的遮罩類型 | - | - |

## 測試 PDF 解析

### Console 測試（推薦）

```bash
# 無密碼 PDF
python test_pdf_parser.py normal.pdf

# 有密碼 PDF
python test_pdf_parser.py encrypted.pdf --password A123456789

# 詳細測試
python test_pdf_parser.py encrypted.pdf --password A123456789 --all

# 快速測試腳本
./test_password.sh encrypted.pdf A123456789
```

### HTTP API 測試

```bash
# 啟動服務
python app.py

# 測試有密碼的 PDF
curl -X POST http://localhost:12345/api/test/parse-pdf \
  -F "file=@encrypted.pdf" \
  -F "password=A123456789"
```

## 🔒 密碼保護 PDF 處理

### 預設密碼設定（推薦）

在 `.env` 檔案中設定預設密碼，系統會自動嘗試：

```env
# .env
PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678
```

設定後，即使不提供密碼參數，系統也會自動嘗試解密！

### 手動提供密碼

```bash
# Console 測試
python test_pdf_parser.py encrypted.pdf --password A123456789

# HTTP API
curl -X POST http://localhost:12345/api/webhook/gmail \
  -F "file=@statement.pdf" \
  -F "document_type=bank_statement" \
  -F "password=A123456789"
```

### 常見密碼格式
- **身分證字號**：`A123456789`
- **生日**：`19900101` (YYYYMMDD)
- **統一編號**：`12345678`

**詳細文件：**
- [PDF 密碼配置指南](docs/PDF_PASSWORD_CONFIG.md) - 如何設定預設密碼
- [PDF 密碼處理指南](docs/PDF_PASSWORD_HANDLING.md) - 完整使用說明

## 🛡️ 個資保護與 AI 分析

### 個資遮罩

自動偵測並遮罩敏感個人資料：身分證、電話、地址、信用卡號等。

```bash
# 測試個資遮罩功能
python test_privacy.py

# Webhook 中啟用個資遮罩
curl -X POST http://localhost:12345/api/webhook/gmail \
  -F "file=@statement.pdf" \
  -F "mask_privacy=true"
```

### AI 智慧分析

支援 OpenAI/Claude 自動分析金融文件並提取關鍵資訊。

```bash
# 設定 API Key（選擇其中一種）
export OPENAI_API_KEY=sk-your-key-here
# 或
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# 分析文件（自動遮罩個資）
curl -X POST http://localhost:12345/api/ai/mask-and-analyze \
  -F "file=@statement.pdf" \
  -F "provider=openai"

# 偵測文件中的敏感資訊
curl -X POST http://localhost:12345/api/ai/detect-sensitive \
  -F "file=@statement.pdf"
```

**詳細文件：**
- [AI 整合說明](docs/AI_INTEGRATION.md) - AI API 使用指南
- [個資遮罩功能](docs/PRIVACY_MASKING.md) - 個資保護詳細說明

## TODO

### 待完成功能
- [ ] API 金鑰認證
- [ ] Rate Limiting
- [ ] OCR 支援（掃描檔）
- [ ] 資料庫整合
- [ ] 非同步處理
- [ ] 管理後台
- [x] 密碼保護 PDF 支援 ✅
- [x] 個資遮罩保護 ✅
- [x] AI 智慧分析（OpenAI/Claude） ✅

### 計劃改進
- [ ] 提升 PDF 解析準確度
- [ ] 支援更多銀行格式
- [ ] 批次處理功能
- [ ] Webhook 重試機制
- [ ] 密碼自動推測

## 文件

- 📚 [快速開始指南](docs/QUICKSTART.md)
- 🚀 [部署指南](docs/DEPLOYMENT.md)
- 🔧 [如何新增 API](docs/HOW_TO_ADD_API.md)
- 🧪 [PDF 測試指南](docs/PDF_TESTING.md)
- 🔒 [PDF 密碼處理](docs/PDF_PASSWORD_HANDLING.md)
- ⚙️ [PDF 密碼配置](docs/PDF_PASSWORD_CONFIG.md)
- 🤖 [**AI 整合說明**](docs/AI_INTEGRATION.md) ⭐ 新功能
- 🛡️ [**個資遮罩功能**](docs/PRIVACY_MASKING.md) ⭐ 新功能
- 📁 [檔案組織說明](docs/FILE_ORGANIZATION.md)
- 🏗️ [Flask 專案結構](docs/FLASK_PROJECT_STRUCTURES.md)
- 📝 [更新日誌](docs/CHANGELOG.md)
- 🌐 [線上文件瀏覽](http://localhost:12345/api/docs)

## 技術堆疊

- Flask 3.0.0 - Web 框架
- pdfplumber 0.11.0 - PDF 解析
- PyPDF2 3.0.1 - PDF 元資料（支援加密）
- requests 2.31.0 - HTTP 請求（AI API）
- Gunicorn 21.2.0 - WSGI 伺服器
- markdown 3.5.1 - 文件渲染

## 授權

MIT License

---

**需要協助？** 
- 查看 [文件目錄](docs/)
- 訪問 [線上文件](http://localhost:12345/api/docs)
- 提交 Issue

**注意**：本服務處理財務敏感資訊，請確保在安全的環境中運行，並使用 HTTPS 傳輸密碼。
