# PDF 密碼處理完整指南

## 📋 目錄

1. [快速開始](#快速開始)
2. [密碼配置](#密碼配置)
3. [使用方式](#使用方式)
4. [Google Apps Script 整合](#google-apps-script-整合)
5. [安全性建議](#安全性建議)

---

## 快速開始

### 問題說明

財務 PDF 檔案（銀行對帳單、信用卡帳單）常使用密碼保護：
- 身分證字號（如 `A123456789`）
- 生日 `YYYYMMDD`（如 `19900101`）
- 統一編號（如 `12345678`）

### 立即使用

```bash
# Console 測試
python cli.py parse document.pdf --password A123456789

# HTTP API
curl -X POST http://localhost:12345/api/webhook/gmail \
  -F "file=@encrypted.pdf" \
  -F "document_type=bank_statement" \
  -F "password=A123456789"
```

---

## 密碼配置

### 方法 1：預設密碼列表（推薦）

在 `.env` 檔案中設定，系統會自動嘗試：

```env
# 逗號分隔（簡單）
PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678

# 或編號方式（推薦）
PDF_PASSWORD_1=A123456789      # 我的身分證
PDF_PASSWORD_2=19900101        # 我的生日
PDF_PASSWORD_3=B987654321      # 配偶身分證
PDF_PASSWORD_4=19850615        # 配偶生日
```

**優點：** 不用每次都提供密碼，系統自動嘗試！

### 方法 2：手動提供密碼

```bash
# Console
python cli.py parse encrypted.pdf --password A123456789

# API
curl -X POST http://localhost:12345/api/webhook/gmail \
  -F "file=@encrypted.pdf" \
  -F "password=A123456789"
```

### 配置範例

#### 個人使用
```env
# .env
PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678
```

#### 多銀行帳戶
```env
PDF_PASSWORD_1=A123456789    # 中信銀行（身分證）
PDF_PASSWORD_2=19900101      # 國泰世華（生日）
PDF_PASSWORD_3=12345         # 台新銀行（統編後5碼）
```

#### 公司環境
```env
PDF_PASSWORD_1=A111111111    # 員工1
PDF_PASSWORD_2=B222222222    # 員工2
PDF_PASSWORD_3=companypass   # 公司統一密碼
```

---

## 使用方式

### Console CLI

```bash
# 使用 cli.py（統一工具）
python cli.py parse encrypted.pdf --password A123456789

# 或使用測試工具
python test_pdf_parser.py encrypted.pdf --password A123456789

# 自動嘗試預設密碼（需先設定 .env）
python cli.py parse encrypted.pdf
```

### HTTP API

#### Webhook 端點
```bash
curl -X POST http://localhost:12345/api/webhook/gmail \
  -F "file=@encrypted.pdf" \
  -F "document_type=bank_statement" \
  -F "password=A123456789"
```

#### 測試端點
```bash
curl -X POST http://localhost:12345/api/test/parse-pdf \
  -F "file=@encrypted.pdf" \
  -F "password=A123456789"
```

### Python 程式碼

```python
from utils.pdf_parser import PDFParser

parser = PDFParser()

# 無密碼 PDF
result = parser.extract_text('normal.pdf')

# 有密碼 PDF
result = parser.extract_text('encrypted.pdf', password='A123456789')

# 自動嘗試預設密碼
result = parser.extract_text('encrypted.pdf')

# 檢查是否加密
if result.get('is_encrypted'):
    print(f"PDF 已解密: {result.get('password_hint', 'N/A')}")
```

### 回應格式

#### 成功解密
```json
{
  "status": "success",
  "data": {
    "text": "PDF 內容...",
    "is_encrypted": true,
    "password_used": true,
    "password_hint": "A***9",
    "total_pages": 3
  }
}
```

#### 需要密碼
```json
{
  "status": "error",
  "message": "PDF 檔案有密碼保護，請提供密碼。",
  "error_code": "PDF_ENCRYPTED",
  "hint": "請在 password 參數中提供 PDF 密碼"
}
```

---

## Google Apps Script 整合

### 情境 1：使用預設密碼（最簡單）

在 API 伺服器設定 `.env`，Script 不需要提供密碼：

```javascript
function processEmail(message) {
  var attachment = message.getAttachments()[0];
  
  // 不提供密碼，讓伺服器自動嘗試
  var response = UrlFetchApp.fetch(API_URL, {
    method: 'post',
    payload: {
      'file': attachment.copyBlob(),
      'document_type': 'bank_statement'
    }
  });
  
  return JSON.parse(response.getContentText());
}
```

### 情境 2：從信件內容提取密碼

```javascript
function processEncryptedEmail(message) {
  var attachment = message.getAttachments()[0];
  var password = extractPasswordFromEmail(message);
  
  var response = UrlFetchApp.fetch(API_URL, {
    method: 'post',
    payload: {
      'file': attachment.copyBlob(),
      'password': password
    }
  });
  
  return JSON.parse(response.getContentText());
}

function extractPasswordFromEmail(message) {
  var body = message.getPlainBody();
  
  // 身分證字號
  var idMatch = body.match(/密碼[:：]?\s*([A-Z]\d{9})/);
  if (idMatch) return idMatch[1];
  
  // 生日
  var birthdayMatch = body.match(/密碼[:：]?\s*(\d{8})/);
  if (birthdayMatch) return birthdayMatch[1];
  
  // 預設密碼
  return PropertiesService.getScriptProperties()
    .getProperty('PDF_PASSWORD');
}
```

### 情境 3：根據寄件者選擇密碼

```javascript
// 設定密碼對應表
function setupPasswordMapping() {
  var props = PropertiesService.getScriptProperties();
  props.setProperties({
    'password_bank_ctbc': 'A123456789',
    'password_card_fubon': '19900101',
    'password_default': '12345678'
  });
}

// 根據寄件者選擇密碼
function getPasswordForSender(sender) {
  var props = PropertiesService.getScriptProperties();
  
  if (sender.includes('ctbc')) {
    return props.getProperty('password_bank_ctbc');
  } else if (sender.includes('fubon')) {
    return props.getProperty('password_card_fubon');
  }
  
  return props.getProperty('password_default');
}
```

---

## 安全性建議

### 1. 保護 .env 檔案

```bash
# 確保不被提交
echo ".env" >> .gitignore

# 設定檔案權限（Linux/Mac）
chmod 600 .env
```

### 2. 使用 HTTPS

```bash
# ❌ 不安全（HTTP）
http://api.example.com/webhook?password=secret

# ✅ 安全（HTTPS）
https://api.example.com/webhook
```

### 3. 不記錄密碼

```python
# ❌ 不好
logger.info(f"使用密碼: {password}")

# ✅ 好
logger.info("使用提供的密碼")
if password_used:
    logger.info(f"密碼提示: {password[0]}***{password[-1]}")
```

### 4. 環境變數管理

```bash
# 生產環境使用 secrets manager
# AWS Secrets Manager
# Google Secret Manager
# HashiCorp Vault
```

### 5. 定期輪換密碼

如果 PDF 密碼改變，記得更新 `.env` 並重啟服務。

---

## 常見密碼格式

### 台灣銀行/信用卡

| 機構 | 常見密碼格式 | 範例 |
|------|-------------|------|
| 中信銀行 | 身分證字號 | A123456789 |
| 國泰世華 | 生日 YYYYMMDD | 19900101 |
| 台新銀行 | 統編後5碼 | 12345 |
| 富邦銀行 | 身分證後6碼 | 123456 |

### 預設密碼範例

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
```

---

## 測試與除錯

### 測試預設密碼配置

```bash
# 1. 設定 .env
echo "PDF_DEFAULT_PASSWORDS=A123456789,19900101" >> .env

# 2. 測試（不提供密碼）
python cli.py parse encrypted.pdf

# 3. 查看輸出
# ✅ 使用預設密碼成功解密
# 密碼提示: A***9
```

### 檢查載入的密碼數量

```python
from utils.pdf_parser import PDFParser

parser = PDFParser()
print(f"已載入 {len(parser.default_passwords)} 個預設密碼")
```

### 建立測試用加密 PDF

```python
# create_encrypted_pdf.py
import PyPDF2

def encrypt_pdf(input_pdf, output_pdf, password):
    pdf_reader = PyPDF2.PdfReader(input_pdf)
    pdf_writer = PyPDF2.PdfWriter()
    
    for page in pdf_reader.pages:
        pdf_writer.add_page(page)
    
    pdf_writer.encrypt(password)
    
    with open(output_pdf, 'wb') as f:
        pdf_writer.write(f)

# 使用
encrypt_pdf('normal.pdf', 'encrypted.pdf', 'A123456789')
```

---

## 故障排除

### 問題 1：所有密碼都失敗

**檢查：**
- PDF 密碼是否正確
- `.env` 檔案是否載入
- 密碼格式是否正確（大小寫、空格）

```bash
# 驗證 .env
cat .env | grep PDF_PASSWORD
```

### 問題 2：API 回應密碼錯誤

**檢查：**
- 確認 PDF 確實加密
- 密碼在 HTTP 傳輸中沒有被轉換
- 伺服器日誌中的錯誤訊息

### 問題 3：預設密碼不生效

**檢查：**
- 重啟服務以載入新的 `.env`
- 確認環境變數格式正確
- 使用 `os.getenv('PDF_DEFAULT_PASSWORDS')` 驗證

---

## 完整配置範例

```env
# ========================================
# Task Service 配置
# ========================================

# Flask 基本配置
SECRET_KEY=your-super-secret-key-here
PORT=5000

# 檔案上傳
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216
DELETE_AFTER_PROCESS=true

# ========================================  
# PDF 密碼配置
# ========================================

# 方法 1: 逗號分隔（簡單）
PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678

# 方法 2: 編號（推薦）
# 個人
PDF_PASSWORD_1=A123456789      # 我的身分證
PDF_PASSWORD_2=19900101        # 我的生日

# 配偶
PDF_PASSWORD_3=B987654321      # 配偶身分證
PDF_PASSWORD_4=19850615        # 配偶生日

# 公司
PDF_PASSWORD_5=12345678        # 公司統編

# 備用
PDF_PASSWORD_6=backup_pass
```

---

## 總結

✅ **三種使用方式：**
1. 設定 `.env` 預設密碼（推薦）- 自動嘗試
2. Console/API 手動提供密碼
3. Google Apps Script 智慧提取密碼

✅ **安全性：**
- 保護 `.env` 檔案
- 使用 HTTPS 傳輸
- 不記錄明文密碼

✅ **彈性配置：**
- 支援多個密碼
- 可註解說明用途
- 方便管理更新

---

**相關文件：**
- [PDF 測試指南](PDF_TESTING.md)
- [快速開始](QUICKSTART.md)
- [CLI 工具使用](../cli.py)

