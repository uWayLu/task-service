# 文件目錄

本專案的詳細文件都放在這個資料夾中。

## 📚 文件列表

### 新手入門
- **[QUICKSTART.md](QUICKSTART.md)** - 5 分鐘快速開始指南
  - 環境設定
  - 啟動服務
  - 基本測試

### 開發相關
- **[HOW_TO_ADD_API.md](HOW_TO_ADD_API.md)** - 如何新增 API 端點
  - Blueprint 架構說明
  - 新增路由的完整步驟
  - 範例程式碼
  - 最佳實踐

- **[MIGRATION_NOTE.md](MIGRATION_NOTE.md)** - 架構遷移說明
  - 從單檔案到模組化的變更
  - 檔案變更清單
  - 如何使用新架構

### 部署相關
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - 完整部署指南
  - Docker 部署
  - 雲端平台部署 (Heroku, GCP, AWS)
  - Nginx 反向代理設定
  - Systemd 服務管理
  - 監控與日誌

### 專案管理
- **[CHANGELOG.md](CHANGELOG.md)** - 版本更新日誌
  - 版本歷史
  - 功能變更記錄
  - 未來規劃

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - 專案技術總結
  - 架構詳細說明
  - 技術選型
  - 工作流程
  - 擴展性考量

## 🎯 推薦閱讀順序

### 如果你是新手
1. [QUICKSTART.md](QUICKSTART.md) - 先讓服務跑起來
2. [HOW_TO_ADD_API.md](HOW_TO_ADD_API.md) - 學習如何新增功能
3. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 了解整體架構

### 如果你要部署
1. [QUICKSTART.md](QUICKSTART.md) - 確認本地運行正常
2. [DEPLOYMENT.md](DEPLOYMENT.md) - 選擇部署方式
3. [CHANGELOG.md](CHANGELOG.md) - 查看當前版本狀態

### 如果你要擴展功能
1. [HOW_TO_ADD_API.md](HOW_TO_ADD_API.md) - 學習新增 API
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 了解現有架構
3. [MIGRATION_NOTE.md](MIGRATION_NOTE.md) - 理解設計決策

## 📝 其他資源

### 範例程式碼
查看 `examples/` 資料夾：
- `gmail_webhook.gs` - Google Apps Script 整合範例
- `test_samples.md` - API 測試範例

### 測試工具
- `test_api.py` - API 測試腳本
- `test_pdf_parser.py` - PDF 解析測試工具

## 💡 快速參考

### 常用指令
```bash
# 啟動服務
python app.py

# 測試 API
python test_api.py

# 測試 PDF 解析
python test_pdf_parser.py your-file.pdf

# Docker 部署
docker-compose up -d
```

### 重要路徑
- 主程式：`app.py`
- API 路由：`api/`
- 工具模組：`utils/`
- 文件：`docs/`
- 範例：`examples/`

## 🔗 外部連結

- [Flask 官方文件](https://flask.palletsprojects.com/)
- [pdfplumber 文件](https://github.com/jsvine/pdfplumber)
- [Google Apps Script 文件](https://developers.google.com/apps-script)

---

**提示**：文件持續更新中，如有疑問歡迎提出 Issue。

