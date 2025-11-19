# 故障排除指南

## 🔍 PDF 密碼問題

### 問題：測試還是不給過 / 密碼失敗

#### 步驟 1：檢查環境變數是否載入

```bash
# 執行環境變數測試工具
python test_env.py
```

**預期輸出：**
```
✅ 找到 .env 檔案
✅ 已載入 3 個預設密碼
```

**如果顯示 "未載入任何預設密碼"：**

#### 步驟 2：檢查 .env 檔案

```bash
# 查看 .env 是否存在
ls -la .env

# 查看內容
cat .env | grep PDF
```

**應該看到：**
```env
PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678
```

**如果沒有，建立設定：**

```bash
cat >> .env << 'EOF'
# PDF 預設密碼
PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678
EOF
```

#### 步驟 3：確認密碼正確

```bash
# 測試特定密碼
python test_pdf_parser.py your-file.pdf --password YOUR_PASSWORD

# 如果成功，將該密碼加入 .env
echo "PDF_DEFAULT_PASSWORDS=YOUR_PASSWORD" >> .env
```

#### 步驟 4：測試自動解密

```bash
# 不提供密碼（應該自動嘗試）
python test_pdf_parser.py your-file.pdf
```

### 常見錯誤與解決

#### 錯誤 1：找不到 .env

```
❌ 找不到 .env 檔案
```

**解決：**
```bash
# 複製範例檔案
cp .env.example .env

# 或建立新的
cat > .env << 'EOF'
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key
PORT=12345

# PDF 預設密碼
PDF_DEFAULT_PASSWORDS=YOUR_PASSWORD_HERE
EOF
```

#### 錯誤 2：密碼格式錯誤

```
⚠️ 未載入任何預設密碼
```

**檢查格式：**
```env
# ✅ 正確
PDF_DEFAULT_PASSWORDS=pass1,pass2,pass3

# ❌ 錯誤（有空格）
PDF_DEFAULT_PASSWORDS = pass1,pass2,pass3

# ❌ 錯誤（有引號）
PDF_DEFAULT_PASSWORDS="pass1,pass2,pass3"
```

#### 錯誤 3：所有密碼都失敗

```
🔒 所有密碼都無法解密 PDF（嘗試了 3 個密碼）
```

**可能原因：**
1. 密碼確實不對
2. PDF 使用特殊加密

**解決：**
```bash
# 1. 確認 PDF 的正確密碼
# 2. 用其他 PDF 閱讀器測試密碼
# 3. 手動提供密碼測試
python test_pdf_parser.py file.pdf --password CORRECT_PASSWORD

# 4. 如果成功，更新 .env
```

#### 錯誤 4：環境變數沒有載入

```python
# Python 測試
from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv('PDF_DEFAULT_PASSWORDS'))
# 如果輸出 None，表示沒載入
```

**解決：**
```bash
# 確認 .env 位置（必須在專案根目錄）
pwd
ls -la .env

# 確認 python-dotenv 已安裝
pip install python-dotenv
```

## 🧪 完整測試流程

```bash
# 1. 檢查環境
python test_env.py

# 2. 測試已知密碼
python test_pdf_parser.py test.pdf --password KNOWN_PASSWORD

# 3. 測試自動解密
python test_pdf_parser.py test.pdf

# 4. 測試 HTTP API
python app.py &
curl -X POST http://localhost:12345/api/test/parse-pdf \
  -F "file=@test.pdf"
```

## 📊 診斷檢查清單

### 環境配置

- [ ] `.env` 檔案存在於專案根目錄
- [ ] `PDF_DEFAULT_PASSWORDS` 有設定
- [ ] 密碼格式正確（逗號分隔，無空格）
- [ ] 已安裝 `python-dotenv`
- [ ] 已執行 `load_dotenv()`

### PDF 檔案

- [ ] PDF 確實是加密的
- [ ] 知道正確的密碼
- [ ] 用其他工具測試過密碼
- [ ] PDF 不是掃描檔
- [ ] PDF 沒有損壞

### 程式碼

- [ ] `from dotenv import load_dotenv`
- [ ] `load_dotenv()` 在程式開始時執行
- [ ] `PDFParser()` 初始化
- [ ] 檢查 `parser.default_passwords`

## 🔧 快速修復腳本

```bash
#!/bin/bash
# fix_pdf_password.sh

echo "🔧 PDF 密碼問題修復腳本"
echo "================================"

# 1. 檢查 .env
if [ ! -f .env ]; then
    echo "❌ 找不到 .env 檔案，正在建立..."
    cp .env.example .env
    echo "✅ 已建立 .env"
fi

# 2. 檢查密碼設定
if ! grep -q "PDF_DEFAULT_PASSWORDS" .env; then
    echo "⚠️  未設定預設密碼，正在加入..."
    echo "" >> .env
    echo "# PDF 預設密碼" >> .env
    echo "PDF_DEFAULT_PASSWORDS=A123456789,19900101,12345678" >> .env
    echo "✅ 已加入預設密碼"
fi

# 3. 測試環境
echo ""
echo "測試環境變數載入..."
python test_env.py

echo ""
echo "================================"
echo "修復完成！請執行:"
echo "  python test_pdf_parser.py your-file.pdf"
```

## 💡 進階除錯

### 啟用詳細日誌

```python
# 在 test_pdf_parser.py 開頭加入
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 手動測試密碼載入

```python
# test_manual.py
from dotenv import load_dotenv
import os

load_dotenv()

# 檢查環境變數
pwd = os.getenv('PDF_DEFAULT_PASSWORDS')
print(f"環境變數: {pwd}")

# 測試 Parser
from utils.pdf_parser import PDFParser
parser = PDFParser()
print(f"載入密碼數: {len(parser.default_passwords)}")
print(f"密碼列表: {parser.default_passwords}")
```

### 測試 PDF 是否真的加密

```python
# test_encryption.py
import PyPDF2

pdf_file = 'your-file.pdf'

with open(pdf_file, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    print(f"是否加密: {reader.is_encrypted}")
    
    if reader.is_encrypted:
        # 測試密碼
        result = reader.decrypt('YOUR_PASSWORD')
        if result > 0:
            print("✅ 密碼正確")
        else:
            print("❌ 密碼錯誤")
```

## 📞 還是無法解決？

請提供以下資訊：

1. **環境測試結果**
   ```bash
   python test_env.py > debug.txt
   ```

2. **錯誤訊息**
   ```bash
   python test_pdf_parser.py file.pdf 2>&1 | tee error.log
   ```

3. **環境資訊**
   ```bash
   python --version
   pip list | grep -E "pdfplumber|PyPDF2|python-dotenv"
   ```

4. **PDF 資訊**
   ```bash
   file your-file.pdf
   pdfinfo your-file.pdf  # 如果有安裝
   ```

