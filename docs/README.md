# 📚 文件目錄

本專案的所有文件都在這個資料夾中。

## 🚀 快速開始

| 文件 | 說明 | 適合 |
|------|------|------|
| [QUICKSTART.md](QUICKSTART.md) | 5 分鐘快速開始 | 新手 |
| [CLI 工具](../cli.py) | Console 命令列工具 | 開發者 |
| [主要 README](../README.md) | 專案總覽 | 所有人 |

## 📖 核心文件

### 開發相關

- **[HOW_TO_ADD_API.md](HOW_TO_ADD_API.md)** - 如何新增 API 端點
  - Blueprint 架構說明
  - 完整開發範例
  - 最佳實踐

- **[FLASK_STRUCTURE.md](FLASK_STRUCTURE.md)** - Flask 專案結構
  - 架構說明
  - 為什麼這樣設計
  - 如何擴展

- **[FILE_ORGANIZATION.md](FILE_ORGANIZATION.md)** - 檔案組織指南
  - 各資料夾用途
  - 檔案放置規則
  - 版本控制規範

### 功能文件

- **[PDF_PASSWORD.md](PDF_PASSWORD.md)** - PDF 密碼處理完整指南
  - 密碼配置方式
  - API 使用方法
  - Apps Script 整合
  - 安全性建議

- **[PDF_TESTING.md](PDF_TESTING.md)** - PDF 測試指南
  - 測試方法
  - 測試案例
  - 故障排除

- **[PRIVACY_MASKING.md](PRIVACY_MASKING.md)** - 個資遮罩功能
  - 遮罩類型
  - 使用方式
  - 自訂規則

- **[AI_INTEGRATION.md](AI_INTEGRATION.md)** - AI 整合說明
  - OpenAI/Claude 設定
  - API 使用方式
  - 提示詞設計

### 部署與維護

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - 部署指南
  - Docker 部署
  - 雲端平台部署
  - 生產環境配置

- **[CHANGELOG.md](CHANGELOG.md)** - 版本更新日誌
  - 版本歷史
  - 功能變更
  - 未來規劃

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - 專案技術總結
  - 完整架構說明
  - 技術選型理由
  - 工作流程

## 🎯 推薦閱讀順序

### 如果你是新手

1. [QUICKSTART.md](QUICKSTART.md) - 先讓服務跑起來
2. [HOW_TO_ADD_API.md](HOW_TO_ADD_API.md) - 學習如何新增功能
3. [FLASK_STRUCTURE.md](FLASK_STRUCTURE.md) - 了解架構設計

### 如果你要部署

1. [QUICKSTART.md](QUICKSTART.md) - 確認本地運行正常
2. [DEPLOYMENT.md](DEPLOYMENT.md) - 選擇部署方式
3. [CHANGELOG.md](CHANGELOG.md) - 查看當前版本狀態

### 如果你要擴展功能

1. [HOW_TO_ADD_API.md](HOW_TO_ADD_API.md) - 學習新增 API
2. [FLASK_STRUCTURE.md](FLASK_STRUCTURE.md) - 了解架構
3. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 了解技術細節

### 如果你要處理 PDF

1. [PDF_PASSWORD.md](PDF_PASSWORD.md) - 密碼處理
2. [PDF_TESTING.md](PDF_TESTING.md) - 測試方法
3. [PRIVACY_MASKING.md](PRIVACY_MASKING.md) - 個資保護

## 💡 快速參考

### 常用指令

```bash
# 啟動服務
python app.py

# Console 工具
python cli.py parse document.pdf
python cli.py mask document.pdf --output masked.txt
python cli.py process document.pdf --ai

# 測試 API
curl http://localhost:12345/api/health

# Docker 部署
docker-compose up -d
```

### 重要路徑

```
app.py          # 主程式
cli.py          # Console 工具
api/            # API 路由
utils/          # 工具模組
docs/           # 文件（本資料夾）
todo/           # TODO 管理
schemas/        # JSON Schema
```

## 📝 其他資源

### 範例程式碼

查看 `examples/` 資料夾：
- `gmail_webhook.gs` - Google Apps Script 整合
- `test_samples.md` - API 測試範例

### 測試工具

```bash
# PDF 測試
python test_pdf_parser.py document.pdf

# API 測試
python test_api.py

# AI 測試
python test_ai.py

# 個資遮罩測試
python test_privacy.py
```

### 需求管理

查看 `todo/` 資料夾：
- 撰寫待辦事項
- AI 解析並實現
- 追蹤進度

## 🔗 外部連結

- [Flask 官方文件](https://flask.palletsprojects.com/)
- [pdfplumber 文件](https://github.com/jsvine/pdfplumber)
- [Google Apps Script](https://developers.google.com/apps-script)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic Claude](https://docs.anthropic.com/)

## 📊 文件清單

目前文件概覽：

| 類別 | 文件數量 | 狀態 |
|------|---------|------|
| 快速開始 | 1 | ✅ |
| 開發指南 | 3 | ✅ |
| 功能說明 | 4 | ✅ |
| 部署維護 | 3 | ✅ |
| **總計** | **11** | **✅** |

## 🆕 最近更新

- 新增 `PDF_PASSWORD.md` - 合併密碼處理相關文件
- 新增 `FLASK_STRUCTURE.md` - 簡化架構說明
- 新增 CLI 工具文件
- 整理並刪除重複文件

## 💬 需要協助？

- 查看對應文件
- 訪問 [線上文件](http://localhost:12345/api/docs)（啟動服務後）
- 在 `todo/` 資料夾撰寫待辦事項
- 提交 Issue

---

**提示**：所有文件都持續更新，如有疑問歡迎反饋！📚✨
