# 快速開始指南

這份指南將幫助你在 5 分鐘內啟動 Task Service API。

## 📋 前置需求

- Python 3.8 或更高版本
- pip（Python 套件管理器）

## 🚀 快速啟動（3 步驟）

### 步驟 1：安裝依賴

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境（Linux/Mac）
source venv/bin/activate

# 或在 Windows
# .\venv\Scripts\activate

# 安裝套件
pip install -r requirements.txt
```

### 步驟 2：設定環境變數

建立 `.env` 檔案：

```bash
cat > .env << 'EOF'
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-for-testing
PORT=5000
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216
DELETE_AFTER_PROCESS=true
EOF
```

或直接執行啟動腳本（會自動建立）：

```bash
chmod +x run.sh
./run.sh
```

### 步驟 3：啟動服務

```bash
python app.py
```

服務現在運行在 `http://localhost:5000` 🎉

## ✅ 測試服務

### 測試 1：健康檢查

```bash
curl http://localhost:5000/api/health
```

預期回應：

```json
{
  "status": "healthy",
  "service": "task-service",
  "upload_folder": "./uploads"
}
```

### 測試 2：使用測試腳本

```bash
python test_api.py
```

### 測試 3：上傳 PDF（需要準備測試 PDF）

```bash
curl -X POST http://localhost:5000/api/webhook/gmail \
  -F "file=@your-test-file.pdf" \
  -F "document_type=bank_statement" \
  -F "sender=test@example.com" \
  -F "subject=測試帳單" \
  -F "date=2024-11-18"
```

## 🐳 使用 Docker（更簡單）

如果你有安裝 Docker：

```bash
# 一行指令啟動
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down
```

## 📝 下一步

1. **整合 Google Apps Script**
   - 查看 `examples/gmail_webhook.gs`
   - 設定 Gmail 觸發器

2. **客製化設定**
   - 編輯 `.env` 檔案
   - 修改文件處理邏輯

3. **部署到生產環境**
   - 閱讀 `DEPLOYMENT.md`
   - 選擇適合的部署方式

## 🔍 API 端點總覽

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | 服務資訊 |
| `/api/health` | GET | 健康檢查 |
| `/api/webhook/gmail` | POST | 處理 PDF webhook |

## 📚 文件類型

API 支援三種文件類型：

1. **bank_statement** - 銀行對帳單
   - 提取帳號、餘額、交易記錄
   
2. **credit_card** - 信用卡帳單
   - 提取卡號、到期日、應繳金額
   
3. **transaction_notice** - 交易通知
   - 提取交易日期、金額、商家

## 🛠️ 疑難排解

### 問題：模組找不到

```bash
# 確認虛擬環境已啟動
which python
# 應該顯示 .../venv/bin/python

# 重新安裝依賴
pip install -r requirements.txt
```

### 問題：端口被佔用

```bash
# 查看誰在使用 5000 端口
lsof -i :5000

# 或修改 .env 中的 PORT
PORT=8000
```

### 問題：權限錯誤

```bash
# 確保 uploads 目錄可寫
chmod 755 uploads/

# 或讓腳本自動建立
mkdir -p uploads
```

## 💡 提示

- 開發時保持 `DELETE_AFTER_PROCESS=false` 以便檢查上傳的檔案
- 使用 `FLASK_DEBUG=1` 查看詳細錯誤訊息
- 查看 `examples/test_samples.md` 了解更多測試範例

## 🎯 常見使用場景

### 場景 1：本地開發測試

```bash
./run.sh
```

### 場景 2：Docker 容器運行

```bash
docker-compose up -d
```

### 場景 3：生產環境部署

```bash
# 使用 Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📞 需要幫助？

- 查看完整文件：`README.md`
- 部署指南：`DEPLOYMENT.md`
- 測試範例：`examples/test_samples.md`
- Apps Script 整合：`examples/gmail_webhook.gs`

---

現在你已經準備好開始使用 Task Service API 了！🚀

