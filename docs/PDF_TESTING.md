# PDF 測試指南

本指南說明如何測試 PDF 解析功能。

## 🎯 測試方式

### 方法 1：Console 測試（推薦用於開發）

使用 `test_pdf_parser.py` 腳本進行測試。

#### 基本使用

```bash
# 最簡單的測試
python test_pdf_parser.py your-file.pdf

# 指定文件類型
python test_pdf_parser.py statement.pdf --type bank_statement

# 顯示詳細資訊
python test_pdf_parser.py statement.pdf --verbose

# 預覽文字內容（前 30 行）
python test_pdf_parser.py statement.pdf --preview 30

# 執行完整測試
python test_pdf_parser.py statement.pdf --all

# 儲存結果到 JSON
python test_pdf_parser.py statement.pdf --output result.json
```

#### 輸出範例

```
======================================================================
🔍 PDF 解析器測試工具
======================================================================

============================================================
📋 PDF 基本資訊
============================================================
檔案路徑: statement.pdf
總頁數: 3
文字長度: 2456 字元

元資料:
  author: Bank System
  creator: PDF Generator
  num_pages: 3

============================================================
📋 資訊提取測試
============================================================

找到的數字 (25 個):
  1. 1,234,567.00
  2. 50,000.00
  3. 48,500.00
  ... 還有 22 個

找到的日期 (8 個):
  1. 2024-10-01
  2. 2024-10-31
  3. 2024-10-15

金額資訊:
  所有金額: 25 個
  總額: [10000.0, 11500.0]
  餘額: [50000.0, 48500.0]

============================================================
📋 文件處理測試 (類型: bank_statement)
============================================================

文件類型: bank_statement
總頁數: 3
處理時間: 2024-11-19T10:30:00

摘要資訊:
  account_number: 1234567890
  opening_balance: 50000.0
  closing_balance: 48500.0
  transaction_count: 25
```

### 方法 2：HTTP API（推薦用於整合測試）

啟動服務後使用 API 測試。

#### 啟動服務

```bash
python app.py
```

#### API 端點

##### 1. 測試 PDF 解析

```bash
curl -X POST http://localhost:12345/api/test/parse-pdf \
  -F "file=@statement.pdf"
```

**回應範例：**

```json
{
  "status": "success",
  "message": "解析完成",
  "data": {
    "filename": "statement.pdf",
    "total_pages": 3,
    "text_length": 2456,
    "text_preview": "銀行對帳單\n帳號: 1234567890...",
    "full_text": "完整文字內容...",
    "metadata": {
      "author": "Bank System",
      "num_pages": 3
    },
    "extracted": {
      "numbers": [1234567, 50000, 48500, ...],
      "dates": ["2024-10-01", "2024-10-31", ...],
      "amounts": {
        "all": [50000.0, 48500.0, ...],
        "totals": [10000.0],
        "balances": [50000.0, 48500.0]
      }
    },
    "pages": [
      {"page_number": 1, "text_length": 856, "size": "612.0x792.0"},
      {"page_number": 2, "text_length": 1200, "size": "612.0x792.0"},
      {"page_number": 3, "text_length": 400, "size": "612.0x792.0"}
    ]
  }
}
```

##### 2. 測試文件處理

```bash
curl -X POST http://localhost:12345/api/test/process-document \
  -F "file=@statement.pdf" \
  -F "document_type=bank_statement"
```

**回應範例：**

```json
{
  "status": "success",
  "message": "處理完成",
  "data": {
    "document_type": "bank_statement",
    "summary": {
      "account_number": "1234567890",
      "opening_balance": 50000.0,
      "closing_balance": 48500.0,
      "transaction_count": 25
    },
    "transactions": [...],
    "total_pages": 3,
    "processed_at": "2024-11-19T10:30:00"
  }
}
```

## 🔍 測試場景

### 場景 1：快速驗證 PDF 可讀性

```bash
python test_pdf_parser.py your-file.pdf
```

**適用時機：**
- 收到新的 PDF 檔案
- 確認 PDF 不是掃描檔
- 檢查基本資訊

### 場景 2：檢查資訊提取準確度

```bash
python test_pdf_parser.py your-file.pdf --all
```

**適用時機：**
- 驗證數字提取是否正確
- 檢查日期格式是否被識別
- 確認金額提取邏輯

### 場景 3：查看原始文字內容

```bash
python test_pdf_parser.py your-file.pdf --preview 50
```

**適用時機：**
- 除錯解析問題
- 了解 PDF 結構
- 設計新的提取規則

### 場景 4：測試文件分類

```bash
# 測試銀行對帳單
python test_pdf_parser.py bank.pdf --type bank_statement

# 測試信用卡帳單
python test_pdf_parser.py card.pdf --type credit_card

# 測試交易通知
python test_pdf_parser.py notice.pdf --type transaction_notice
```

**適用時機：**
- 驗證文件分類邏輯
- 檢查摘要資訊提取
- 測試不同銀行格式

### 場景 5：整合測試（HTTP）

```bash
# 啟動服務
python app.py

# 使用 curl 測試
curl -X POST http://localhost:12345/api/test/parse-pdf \
  -F "file=@test.pdf" | python -m json.tool
```

**適用時機：**
- 模擬 webhook 請求
- 測試完整流程
- 驗證 API 回應格式

## 📊 測試檢查清單

使用此清單確保 PDF 解析功能正常：

- [ ] PDF 檔案可以成功讀取
- [ ] 提取的文字內容完整
- [ ] 頁數正確
- [ ] 數字提取正確（金額、帳號等）
- [ ] 日期格式被正確識別
- [ ] 文件類型分類正確
- [ ] 摘要資訊提取完整
- [ ] 交易記錄解析正確
- [ ] API 回應格式正確
- [ ] 錯誤處理正常

## 🐛 常見問題

### 問題：PDF 解析失敗

**可能原因：**
- PDF 是掃描檔（圖片格式）
- PDF 加密
- PDF 損壞

**解決方法：**
```bash
# 查看錯誤詳情
python test_pdf_parser.py your-file.pdf --verbose
```

### 問題：提取的數字不正確

**可能原因：**
- PDF 使用特殊字體
- 數字格式不符合預期

**解決方法：**
```bash
# 查看原始文字
python test_pdf_parser.py your-file.pdf --preview 100

# 檢查提取規則
# 編輯 utils/pdf_parser.py 中的 extract_numbers 方法
```

### 問題：中文內容亂碼

**可能原因：**
- PDF 編碼問題
- 缺少中文字型

**解決方法：**
- 確認 PDF 文字可以複製
- 嘗試用其他 PDF 閱讀器打開

### 問題：API 回應超時

**可能原因：**
- PDF 檔案太大
- 處理時間過長

**解決方法：**
```bash
# 檢查 PDF 大小
ls -lh your-file.pdf

# 調整超時設定（在 app.py 中）
# 或使用 console 測試替代
python test_pdf_parser.py your-file.pdf
```

## 💡 進階用法

### 批次測試多個 PDF

```bash
#!/bin/bash
# batch_test.sh

for pdf in pdfs/*.pdf; do
    echo "測試: $pdf"
    python test_pdf_parser.py "$pdf" --type bank_statement
    echo "---"
done
```

### 比較不同 PDF 解析結果

```bash
# 解析並儲存結果
python test_pdf_parser.py bank1.pdf -o result1.json
python test_pdf_parser.py bank2.pdf -o result2.json

# 比較差異
diff result1.json result2.json
```

### 使用 Python 腳本測試

```python
from utils.pdf_parser import PDFParser

parser = PDFParser()
result = parser.extract_text('your-file.pdf')

print(f"總頁數: {result['total_pages']}")
print(f"文字長度: {len(result['text'])}")

# 自訂處理邏輯
for page in result['pages']:
    print(f"第 {page['page_number']} 頁: {len(page['text'])} 字元")
```

## 📝 測試報告範本

```markdown
# PDF 解析測試報告

**測試日期：** 2024-11-19
**測試人員：** Your Name
**PDF 檔案：** bank_statement_202411.pdf

## 測試結果

### 基本資訊
- ✅ 檔案可讀取
- ✅ 總頁數：3
- ✅ 文字提取完整

### 資訊提取
- ✅ 帳號：1234567890
- ✅ 期初餘額：50,000.00
- ✅ 期末餘額：48,500.00
- ⚠️  部分交易日期格式不一致

### 建議改進
1. 統一日期格式處理
2. 加強金額提取規則

## 備註
使用指令：`python test_pdf_parser.py bank_statement_202411.pdf --all`
```

---

**提示**：建議先用 Console 測試確認解析正確，再整合到 HTTP API 使用。

