# 更新日誌

所有重要的專案變更都會記錄在此檔案中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
版本號遵循 [語義化版本](https://semver.org/lang/zh-TW/)。

## [1.0.0] - 2025-11-18

### 新增

#### 核心功能
- 建立 Flask API 主應用程式
- 實作 Gmail Webhook 接收端點 (`/api/webhook/gmail`)
- 實作健康檢查端點 (`/api/health`)
- PDF 檔案上傳與驗證功能
- 自動化檔案清理機制

#### PDF 處理
- PDF 文字提取功能（使用 pdfplumber）
- PDF 元資料提取（使用 PyPDF2）
- 智能數字提取（支援各種貨幣格式）
- 日期提取（支援多種日期格式）
- 金額資訊提取

#### 文件處理器
- 銀行對帳單處理器
  - 帳號提取
  - 期初/期末餘額識別
  - 交易記錄解析
  - 存款/提款總額計算
  
- 信用卡帳單處理器
  - 卡號識別（遮罩格式）
  - 繳款截止日提取
  - 應繳金額計算
  - 最低應繳金額識別
  - 消費明細解析
  
- 交易通知處理器
  - 交易日期提取
  - 商家資訊識別
  - 交易類型分類
  - 交易金額提取

#### 配置與工具
- 環境變數配置系統
- 開發/生產環境分離
- 檔案大小限制設定
- CORS 支援
- 錯誤處理中間件

#### 部署支援
- Docker 支援
  - Dockerfile
  - docker-compose.yml
  - .dockerignore
- Gunicorn 生產伺服器配置
- 健康檢查機制
- 啟動腳本 (run.sh)

#### 文件
- 完整的 README.md
- 快速開始指南 (QUICKSTART.md)
- 部署指南 (DEPLOYMENT.md)
- 更新日誌 (CHANGELOG.md)

#### 範例與測試
- Google Apps Script 整合範例 (`examples/gmail_webhook.gs`)
- 測試範例文件 (`examples/test_samples.md`)
- API 測試腳本 (`test_api.py`)
- curl 測試指令範例

#### 安全性
- SECRET_KEY 配置
- 檔案類型白名單
- 檔案大小限制（預設 16MB）
- 安全的檔案名稱處理

### 技術規格

#### 依賴套件
- Flask 3.0.0 - Web 框架
- Flask-CORS 4.0.0 - 跨域資源共享
- pdfplumber 0.11.0 - PDF 文字提取
- PyPDF2 3.0.1 - PDF 元資料處理
- python-dotenv 1.0.0 - 環境變數管理
- Werkzeug 3.0.1 - WSGI 工具
- gunicorn 21.2.0 - WSGI HTTP 伺服器

#### API 規格
- RESTful API 設計
- JSON 回應格式
- multipart/form-data 檔案上傳
- 適當的 HTTP 狀態碼
- 結構化錯誤訊息

#### 專案結構
```
task-service/
├── app.py                      # 主應用程式
├── config.py                   # 配置管理
├── requirements.txt            # Python 依賴
├── Dockerfile                  # Docker 映像定義
├── docker-compose.yml          # Docker Compose 配置
├── run.sh                      # 啟動腳本
├── test_api.py                 # 測試腳本
├── utils/                      # 工具模組
│   ├── pdf_parser.py          # PDF 解析器
│   └── document_processor.py  # 文件處理器
├── examples/                   # 範例程式碼
├── uploads/                    # 上傳檔案目錄
└── docs/                       # 文件
```

### 已知限制

- PDF 必須包含可選取的文字（不支援掃描檔/圖片 PDF）
- 中文內容可能因 PDF 編碼而有解析差異
- 複雜的表格格式可能需要額外調整
- 目前不支援加密的 PDF 檔案
- 大型 PDF（>16MB）會被拒絕

### 未來規劃

#### v1.1.0（短期）
- [ ] 加入 API 認證機制（API Key）
- [ ] 實作 Rate Limiting
- [ ] 加入請求日誌記錄
- [ ] 支援 OCR（處理掃描檔）
- [ ] 批次處理多個 PDF
- [ ] Webhook 重試機制

#### v1.2.0（中期）
- [ ] 資料庫整合（儲存處理記錄）
- [ ] 非同步任務處理（Celery）
- [ ] WebSocket 即時通知
- [ ] 管理介面（Dashboard）
- [ ] 進階分析功能
- [ ] 多語言支援

#### v2.0.0（長期）
- [ ] 機器學習文件分類
- [ ] 智能資料提取
- [ ] 自動化測試套件
- [ ] 效能監控與追蹤
- [ ] 插件系統
- [ ] 多租戶支援

### 安全性更新

- 實作檔案類型驗證
- 實作檔案大小限制
- 使用安全的檔案名稱處理
- 環境變數保護敏感資訊

### 效能最佳化

- 處理後自動清理檔案
- Gunicorn 多 Worker 支援
- Docker 映像最佳化
- 適當的錯誤處理避免記憶體洩漏

## [Unreleased]

### 計劃中
- API 版本控制
- 更多文件類型支援
- Webhook 簽名驗證
- 詳細的使用統計

---

## 版本號說明

- **MAJOR version**（主版號）：不相容的 API 變更
- **MINOR version**（次版號）：向下相容的功能新增
- **PATCH version**（修訂號）：向下相容的問題修正

## 貢獻指南

如果你想貢獻代碼或報告問題，請：

1. Fork 專案
2. 建立 feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit 你的變更 (`git commit -m 'Add some AmazingFeature'`)
4. Push 到 branch (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

---

最後更新：2024-11-18

