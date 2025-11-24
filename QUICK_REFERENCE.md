# 快速參考指南

## 🚀 常用指令

### 啟動服務

```bash
# HTTP API 服務
python app.py

# 指定端口
PORT=8080 python app.py
```

### Console CLI

```bash
# 查看幫助
python cli.py --help
python cli.py parse --help

# 解析 PDF
python cli.py parse document.pdf
python cli.py parse encrypted.pdf --password A123456789

# 遮罩個資
python cli.py mask document.pdf --output masked.txt
python cli.py mask document.pdf --types taiwan_id,phone

# AI 分析
python cli.py analyze document.pdf --provider openai
python cli.py analyze document.pdf --provider claude --no-mask

# 完整流程
python cli.py process document.pdf --ai --validate --output ./output

# 驗證資料
python cli.py validate data.json --schema schemas/bank_statement_schema.json
```

### HTTP API

```bash
# 健康檢查
curl http://localhost:12345/api/health

# 處理 PDF
curl -X POST http://localhost:12345/api/webhook/gmail \
  -F "file=@document.pdf" \
  -F "document_type=bank_statement" \
  -F "password=A123456789" \
  -F "mask_privacy=true"

# AI 分析
curl -X POST http://localhost:12345/api/ai/mask-and-analyze \
  -F "file=@document.pdf" \
  -F "provider=openai"

# 偵測敏感資訊
curl -X POST http://localhost:12345/api/ai/detect-sensitive \
  -F "file=@document.pdf"
```

## 📝 配置檔案

### .env 範例

```env
# Flask
SECRET_KEY=your-secret-key
PORT=5000
FLASK_DEBUG=0

# 檔案上傳
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216
DELETE_AFTER_PROCESS=true

# PDF 密碼（任選其一或混用）
PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678
PDF_PASSWORD_1=A123456789
PDF_PASSWORD_2=19900101

# AI API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

## 📂 重要路徑

| 路徑 | 用途 |
|------|------|
| `app.py` | Flask 主程式 |
| `cli.py` | Console CLI 工具 |
| `api/` | API 路由模組 |
| `utils/` | 工具模組 |
| `docs/` | 詳細文件 |
| `todo/` | TODO 管理 |
| `schemas/` | JSON Schema 定義 |
| `test_files/` | 測試 PDF |
| `output/` | 處理結果輸出 |

## 🎯 快速任務

### 任務 1：處理一個 PDF

```bash
python cli.py process document.pdf --output ./output
```

結果：
- `output/document_original.txt` - 原始文字
- `output/document_masked.txt` - 遮罩後文字
- `output/document_extracted.json` - 提取資料
- `output/document_report.json` - 處理報告

### 任務 2：測試密碼功能

```bash
# 1. 設定預設密碼
echo "PDF_DEFAULT_PASSWORDS=A123456789" >> .env

# 2. 測試（不提供密碼）
python cli.py parse encrypted.pdf

# 3. 自動解密成功！
```

### 任務 3：設定 AI 分析

```bash
# 1. 設定 API Key
export OPENAI_API_KEY=sk-your-key

# 2. 分析文件
python cli.py analyze document.pdf --provider openai

# 3. 查看結果
```

### 任務 4：撰寫待辦事項

```bash
# 1. 複製範本
cp todo/template.md todo/active/my_feature.md

# 2. 編輯待辦事項
vim todo/active/my_feature.md

# 3. 請 AI 實現
"請實現 todo/active/my_feature.md"
```

## 🔧 常見問題

### 問題 1：PDF 密碼錯誤

**解決：**
```bash
# 方法 1：提供正確密碼
python cli.py parse document.pdf --password CORRECT_PASSWORD

# 方法 2：設定預設密碼
echo "PDF_DEFAULT_PASSWORDS=password1,password2" >> .env
```

### 問題 2：找不到模組

**解決：**
```bash
# 確認在專案根目錄
pwd

# 安裝依賴
pip install -r requirements.txt

# 啟動虛擬環境（如果使用）
source venv/bin/activate
```

### 問題 3：AI API 錯誤

**解決：**
```bash
# 檢查 API Key
echo $OPENAI_API_KEY

# 設定 API Key
export OPENAI_API_KEY=sk-your-key

# 測試
python test_ai.py
```

### 問題 4：端口被佔用

**解決：**
```bash
# 使用其他端口
PORT=8080 python app.py

# 或找出佔用的程序
lsof -i :12345
kill -9 <PID>
```

## 📚 文件連結

- [完整 README](README.md) - 專案總覽
- [快速開始](docs/QUICKSTART.md) - 5 分鐘上手
- [CLI 工具](cli.py) - Console 使用
- [PDF 密碼](docs/PDF_PASSWORD.md) - 密碼處理
- [個資遮罩](docs/PRIVACY_MASKING.md) - 遮罩功能
- [AI 整合](docs/AI_INTEGRATION.md) - AI 分析
- [TODO 管理](todo/README.md) - 撰寫待辦事項

## 🎨 範例輸出

### Console CLI

```bash
$ python cli.py process document.pdf --ai --validate

============================================================
⚙️  完整處理: document.pdf
============================================================

ℹ 步驟 1/4: 解析 PDF...
✓ PDF 解析完成
✓ 已儲存至: output/document_original.txt

ℹ 步驟 2/4: 遮罩個資...
✓ 已遮罩 7 項敏感資訊
✓ 已儲存至: output/document_masked.txt

ℹ 步驟 3/4: 結構化提取...
✓ 提取成功 (方法: credit_card)
✓ 已儲存至: output/document_extracted.json

ℹ 步驟 4/4: AI 分析...
✓ AI 分析完成
✓ 已儲存至: output/document_ai_analysis.json

============================================================
✅ 處理完成
============================================================
ℹ 所有檔案已儲存至: output
```

### HTTP API 回應

```json
{
  "status": "success",
  "message": "文件處理完成（結構化提取）",
  "data": {
    "document_type": "credit_card",
    "card_info": {
      "last_4_digits": "1234",
      "card_type": "VISA"
    },
    "billing_cycle": {
      "start_date": "2024-10-01",
      "end_date": "2024-10-31"
    }
  },
  "extraction_method": "credit_card",
  "privacy_masking": {
    "masked_count": 7,
    "sensitive_types": ["身分證字號", "電話號碼", "地址"]
  }
}
```

---

**更多資訊：** 查看 [完整文件](docs/)

