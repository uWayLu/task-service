# PDF 密碼配置指南

## 🎯 功能說明

系統支援在 `.env` 檔案中設定預設密碼列表，當遇到加密的 PDF 時會自動嘗試這些密碼。

## 📝 配置方式

### 方法 1：逗號分隔（推薦簡單情況）

```env
# .env
PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678,B987654321
```

- 使用逗號分隔多個密碼
- 會按順序嘗試
- 適合密碼數量較少的情況

### 方法 2：編號密碼（推薦複雜情況）

```env
# .env
PDF_PASSWORD_1=A123456789     # 身分證字號
PDF_PASSWORD_2=19900101       # 生日 YYYYMMDD
PDF_PASSWORD_3=12345678       # 統一編號
PDF_PASSWORD_4=B987654321     # 備用身分證
PDF_PASSWORD_5=19850615       # 備用生日
```

- 每個密碼單獨一行
- 從 1 開始編號
- 可以加註解說明
- 適合管理多個密碼

### 方法 3：混合使用

```env
# .env
# 主要密碼列表
PDF_DEFAULT_PASSWORDS=A123456789,19900101

# 特殊密碼
PDF_PASSWORD_1=special_password_1
PDF_PASSWORD_2=special_password_2
```

系統會合併所有密碼並依序嘗試。

## 🔧 使用範例

### 範例 1：設定常用密碼

```env
# .env - 個人使用
PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678
```

### 範例 2：多用戶環境

```env
# .env - 公司使用
PDF_PASSWORD_1=A111111111    # 員工1身分證
PDF_PASSWORD_2=B222222222    # 員工2身分證
PDF_PASSWORD_3=20241119      # 公司統編後8碼
PDF_PASSWORD_4=companypass   # 公司統一密碼
```

### 範例 3：不同銀行

```env
# .env - 多銀行帳戶
PDF_PASSWORD_1=A123456789    # 中信銀行（身分證）
PDF_PASSWORD_2=19900101      # 國泰世華（生日）
PDF_PASSWORD_3=12345        # 台新銀行（統編後5碼）
```

## 🚀 測試配置

### 1. 設定 .env

```bash
# 複製範例檔案
cp .env.example .env

# 編輯設定
vim .env
```

加入你的密碼：

```env
PDF_DEFAULT_PASSWORDS=YOUR_ID_NUMBER,YOUR_BIRTHDAY
```

### 2. 測試自動解密

```bash
# 不提供密碼（會自動嘗試預設密碼）
python test_pdf_parser.py encrypted.pdf

# 輸出會顯示：
# ✅ 使用預設密碼成功解密
# 密碼提示: A***9
```

### 3. HTTP API 測試

```bash
# 不提供密碼參數（會自動嘗試）
curl -X POST http://localhost:12345/api/test/parse-pdf \
  -F "file=@encrypted.pdf"

# 回應：
{
  "status": "success",
  "data": {
    "is_encrypted": true,
    "password_used": true,
    "password_hint": "A***9"
  }
}
```

## 📊 密碼嘗試流程

```
收到加密 PDF
    ↓
1. 先嘗試提供的密碼（如果有）
    ↓ 失敗
2. 嘗試 PDF_DEFAULT_PASSWORDS
    ↓ 失敗
3. 嘗試 PDF_PASSWORD_1
    ↓ 失敗
4. 嘗試 PDF_PASSWORD_2
    ↓ 失敗
5. ...
    ↓ 失敗
❌ 所有密碼都失敗
```

## 🔍 查看配置

### 檢查已載入的密碼數量

```python
from utils.pdf_parser import PDFParser

parser = PDFParser()
print(f"已載入 {len(parser.default_passwords)} 個預設密碼")
```

### 測試特定密碼

```bash
# 提供密碼（優先使用，不嘗試預設密碼）
python test_pdf_parser.py encrypted.pdf --password SPECIFIC_PASSWORD
```

### 停用自動嘗試

```python
# 在程式中停用
parser = PDFParser()
result = parser.extract_text(filepath, password=None, auto_try_defaults=False)
```

## 🎯 常見密碼格式

### 台灣常見格式

```env
# 身分證字號
PDF_PASSWORD_1=A123456789

# 生日 YYYYMMDD
PDF_PASSWORD_2=19900101

# 生日 MMDDYYYY
PDF_PASSWORD_3=01011990

# 統一編號
PDF_PASSWORD_4=12345678

# 身分證後6碼
PDF_PASSWORD_5=123456

# 電話後4碼
PDF_PASSWORD_6=1234
```

### 信用卡常見格式

```env
# 完整身分證
PDF_PASSWORD_1=A123456789

# 生日
PDF_PASSWORD_2=19900101

# 卡號後4碼
PDF_PASSWORD_3=1234

# 預設密碼
PDF_PASSWORD_4=0000
```

## ⚠️ 安全性建議

### 1. .env 檔案保護

```bash
# 確保 .env 不會被提交
echo ".env" >> .gitignore

# 設定檔案權限（只有自己可讀）
chmod 600 .env
```

### 2. 生產環境

```env
# 生產環境建議
# 1. 使用環境變數管理工具（如 Vault）
# 2. 定期更換密碼
# 3. 限制存取權限

# 範例：從外部注入
# export PDF_DEFAULT_PASSWORDS=$(vault read secret/pdf_passwords)
```

### 3. 密碼輪換

```bash
# 定期更新密碼
# 1. 更新 .env
# 2. 重啟服務
sudo systemctl restart task-service
```

### 4. 審計日誌

```python
# 記錄密碼使用（但不記錄密碼內容）
if result.get('password_used'):
    logger.info(f"PDF 使用密碼解密: {result['password_hint']}")
```

## 📋 完整配置範例

```env
# ========================================
# Task Service 配置
# ========================================

# Flask 基本配置
FLASK_APP=app.py
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-super-secret-key-here
PORT=5000

# 檔案上傳配置
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216
DELETE_AFTER_PROCESS=true

# ========================================
# PDF 密碼配置
# ========================================

# 方法 1: 逗號分隔（簡單情況）
PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678

# 方法 2: 編號密碼（推薦）
# 個人資訊
PDF_PASSWORD_1=A123456789      # 我的身分證
PDF_PASSWORD_2=19900101        # 我的生日

# 配偶資訊
PDF_PASSWORD_3=B987654321      # 配偶身分證
PDF_PASSWORD_4=19850615        # 配偶生日

# 公司資訊
PDF_PASSWORD_5=12345678        # 公司統編

# 備用密碼
PDF_PASSWORD_6=backup_pass     # 備用密碼1
PDF_PASSWORD_7=default_pass    # 備用密碼2

# ========================================
# 其他配置
# ========================================
ENABLE_DOCS_API=true
```

## 🧪 測試腳本

```bash
#!/bin/bash
# test_default_passwords.sh

echo "測試預設密碼配置..."

# 1. 檢查 .env
if [ ! -f .env ]; then
    echo "❌ 找不到 .env 檔案"
    exit 1
fi

# 2. 檢查是否設定密碼
if grep -q "PDF_DEFAULT_PASSWORDS" .env || grep -q "PDF_PASSWORD_1" .env; then
    echo "✅ 找到密碼配置"
else
    echo "⚠️  未設定預設密碼"
fi

# 3. 測試解密
if [ -f "test_files/encrypted.pdf" ]; then
    echo "測試自動解密..."
    python test_pdf_parser.py test_files/encrypted.pdf
else
    echo "⚠️  找不到測試檔案"
fi
```

## 💡 最佳實踐

### 1. 密碼組織

```env
# 按用途分組
# === 個人帳戶 ===
PDF_PASSWORD_1=personal_id
PDF_PASSWORD_2=personal_birthday

# === 銀行帳戶 ===
PDF_PASSWORD_3=bank_password_1
PDF_PASSWORD_4=bank_password_2

# === 信用卡 ===
PDF_PASSWORD_5=card_password_1
```

### 2. 註解說明

```env
# 中信銀行對帳單密碼（身分證字號）
PDF_PASSWORD_1=A123456789

# 國泰世華信用卡密碼（生日）
PDF_PASSWORD_2=19900101
```

### 3. 定期檢查

```bash
# 每月檢查一次密碼是否仍有效
# 移除無效的密碼
# 更新過期的密碼
```

## 🎉 總結

- ✅ 在 `.env` 設定預設密碼
- ✅ 系統自動嘗試
- ✅ 支援多種格式
- ✅ 安全性考量
- ✅ 不記錄明文密碼

現在你可以：

```bash
# 1. 設定 .env
echo "PDF_DEFAULT_PASSWORDS=A123456789,19900101" >> .env

# 2. 測試（不需要提供密碼）
python test_pdf_parser.py encrypted.pdf

# 3. 自動解密成功！
```

**更多資訊：** 查看 [PDF_PASSWORD_HANDLING.md](PDF_PASSWORD_HANDLING.md)

