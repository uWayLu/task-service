# PDF 密碼處理指南

## 🔒 問題說明

許多財務 PDF 檔案（銀行對帳單、信用卡帳單）會使用密碼保護，常見的密碼格式：
- 身分證字號
- 生日 (YYYYMMDD)
- 統一編號
- 自訂密碼

## ✅ 已實作功能

我們的 PDF parser 現在支援：

1. **自動檢測加密**
   - 在解析前檢查 PDF 是否加密
   - 提供友善的錯誤訊息

2. **密碼解密**
   - 支援透過參數傳入密碼
   - 自動解密並提取內容

3. **錯誤處理**
   - 密碼錯誤時返回明確錯誤
   - 未提供密碼時提示需要密碼

## 🚀 使用方式

### 方法 1：API 請求（帶密碼）

```bash
# Gmail Webhook（帶密碼）
curl -X POST http://localhost:12345/api/webhook/gmail \
  -F "file=@encrypted.pdf" \
  -F "document_type=bank_statement" \
  -F "password=A123456789"  # ← 加入密碼參數

# 測試 API（帶密碼）
curl -X POST http://localhost:12345/api/test/parse-pdf \
  -F "file=@encrypted.pdf" \
  -F "password=A123456789"
```

### 方法 2：Console 測試

```bash
# 修改 test_pdf_parser.py 支援密碼
python test_pdf_parser.py encrypted.pdf --password A123456789
```

### 方法 3：Python 程式碼

```python
from utils.pdf_parser import PDFParser

parser = PDFParser()

# 無密碼 PDF
result = parser.extract_text('normal.pdf')

# 有密碼 PDF
result = parser.extract_text('encrypted.pdf', password='A123456789')

# 檢查是否加密
if result.get('is_encrypted'):
    print(f"PDF 已解密: {result['encryption_info']}")
```

## 📊 回應格式

### 成功解密

```json
{
  "status": "success",
  "data": {
    "text": "PDF 內容...",
    "is_encrypted": true,
    "encryption_info": "PDF 使用密碼保護",
    "total_pages": 3,
    "metadata": {
      "decrypted": true
    }
  }
}
```

### 需要密碼

```json
{
  "status": "error",
  "message": "PDF 檔案有密碼保護，請提供密碼。",
  "error_code": "PDF_ENCRYPTED",
  "hint": "請在 password 參數中提供 PDF 密碼"
}
```

### 密碼錯誤

```json
{
  "status": "error",
  "message": "密碼錯誤或無法解密 PDF",
  "error_code": "PDF_ENCRYPTED"
}
```

## 🔧 Google Apps Script 整合

### 情境 1：已知密碼（如身分證）

```javascript
function processEncryptedEmail(message) {
  var attachment = message.getAttachments()[0];
  
  // 從信件主旨或內容推測密碼
  var password = extractPasswordFromEmail(message);
  
  var response = UrlFetchApp.fetch(API_URL, {
    method: 'post',
    payload: {
      'file': attachment.copyBlob(),
      'document_type': 'bank_statement',
      'password': password  // ← 傳入密碼
    }
  });
  
  return JSON.parse(response.getContentText());
}

function extractPasswordFromEmail(message) {
  var body = message.getPlainBody();
  
  // 常見密碼模式
  // 1. 身分證字號（通常在信件中）
  var idMatch = body.match(/密碼[:：]?\s*([A-Z]\d{9})/);
  if (idMatch) return idMatch[1];
  
  // 2. 生日
  var birthdayMatch = body.match(/密碼[:：]?\s*(\d{8})/);
  if (birthdayMatch) return birthdayMatch[1];
  
  // 3. 從設定中取得預設密碼
  return PropertiesService.getScriptProperties().getProperty('PDF_PASSWORD');
}
```

### 情境 2：嘗試多個密碼

```javascript
function tryMultiplePasswords(attachment) {
  // 常見密碼清單
  var passwords = [
    getIdNumber(),           // 身分證
    getBirthday(),           // 生日
    getBusinessNumber(),     // 統一編號
    getCustomPassword()      // 自訂密碼
  ];
  
  for (var i = 0; i < passwords.length; i++) {
    try {
      var response = UrlFetchApp.fetch(API_URL, {
        method: 'post',
        payload: {
          'file': attachment.copyBlob(),
          'password': passwords[i]
        },
        muteHttpExceptions: true
      });
      
      var result = JSON.parse(response.getContentText());
      
      if (result.status === 'success') {
        Logger.log('成功使用密碼: ' + passwords[i]);
        return result;
      }
    } catch (e) {
      continue;
    }
  }
  
  throw new Error('所有密碼都失敗');
}
```

### 情境 3：儲存密碼對應

```javascript
// 設定密碼對應表
function setupPasswordMapping() {
  var props = PropertiesService.getScriptProperties();
  
  props.setProperties({
    'password_bank_ctbc': 'A123456789',      // 中信銀行
    'password_card_fubon': '19900101',       // 富邦信用卡
    'password_default': '12345678'           // 預設密碼
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

## 🧪 測試密碼保護的 PDF

### 建立測試用加密 PDF

```python
# create_encrypted_pdf.py
import PyPDF2
from pathlib import Path

def encrypt_pdf(input_pdf, output_pdf, password):
    """加密 PDF 檔案"""
    pdf_reader = PyPDF2.PdfReader(input_pdf)
    pdf_writer = PyPDF2.PdfWriter()
    
    # 複製所有頁面
    for page in pdf_reader.pages:
        pdf_writer.add_page(page)
    
    # 加密
    pdf_writer.encrypt(password)
    
    # 儲存
    with open(output_pdf, 'wb') as f:
        pdf_writer.write(f)

# 使用範例
encrypt_pdf('normal.pdf', 'encrypted.pdf', 'A123456789')
```

### 測試腳本

```bash
# 測試無密碼 PDF
python test_pdf_parser.py normal.pdf

# 測試有密碼 PDF（應該失敗）
python test_pdf_parser.py encrypted.pdf

# 測試有密碼 PDF（提供密碼）
python test_pdf_parser.py encrypted.pdf --password A123456789
```

## 🔍 常見密碼格式

### 台灣銀行/信用卡常見密碼

| 機構 | 常見密碼格式 | 範例 |
|------|-------------|------|
| 中信銀行 | 身分證字號 | A123456789 |
| 國泰世華 | 生日 (YYYYMMDD) | 19900101 |
| 台新銀行 | 統一編號後5碼 | 12345 |
| 富邦銀行 | 身分證後6碼 | 123456 |
| 玉山銀行 | 自訂密碼 | - |

### 自動推測密碼

```python
def guess_password(sender_email, subject):
    """根據寄件者和主旨推測可能的密碼"""
    passwords = []
    
    # 根據銀行推測
    if 'ctbc' in sender_email:
        # 中信通常用身分證
        passwords.append(get_id_number())
    
    elif 'cathay' in sender_email:
        # 國泰通常用生日
        passwords.append(get_birthday())
    
    # 加入常見預設密碼
    passwords.extend([
        '00000000',  # 常見預設
        '12345678',
        get_last_6_digits_of_id()
    ])
    
    return passwords
```

## ⚠️ 安全性注意事項

### 1. 不要記錄密碼

```python
# ❌ 不好的做法
logger.info(f"使用密碼: {password}")

# ✅ 好的做法
logger.info("嘗試使用提供的密碼")
```

### 2. 密碼傳輸

```bash
# ❌ HTTP（明文傳輸）
http://api.example.com/webhook?password=secret

# ✅ HTTPS（加密傳輸）
https://api.example.com/webhook
```

### 3. 密碼儲存

```javascript
// ❌ 明文儲存在程式碼中
var password = 'A123456789';

// ✅ 使用 Properties Service
var password = PropertiesService.getScriptProperties()
  .getProperty('PDF_PASSWORD');
```

## 📝 更新 test_pdf_parser.py

```python
# 在 argparse 中加入密碼參數
parser.add_argument('-p', '--password', 
                   help='PDF 密碼（如果檔案有加密）')

# 使用密碼
result = parser.extract_text(args.pdf_file, args.password)
```

## 🎯 最佳實踐

1. **優先使用環境變數儲存密碼**
   ```bash
   export PDF_PASSWORD_BANK="A123456789"
   ```

2. **建立密碼對應表**
   ```json
   {
     "bank_ctbc": "A123456789",
     "card_fubon": "19900101"
   }
   ```

3. **提供清晰的錯誤訊息**
   - 告訴使用者需要密碼
   - 提示可能的密碼格式

4. **實作密碼重試機制**
   - 嘗試常見密碼
   - 記錄成功的密碼模式

## 📚 相關文件

- [PDF 測試指南](PDF_TESTING.md)
- [API 文件](../README.md)

---

**現在你可以處理加密的 PDF 了！** 🔓

