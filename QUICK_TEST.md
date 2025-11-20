# 🧪 快速測試指南

## PDF 遮罩測試

### 最簡單的方式

```bash
# 測試 PDF 遮罩效果（一鍵完成）
python test_pdf_masking.py your-file.pdf
```

這會：
1. ✅ 解析 PDF
2. ✅ 偵測敏感資訊
3. ✅ 執行遮罩
4. ✅ 顯示前後對比
5. ✅ 儲存結果到 `output/` 目錄

### 有密碼的 PDF

```bash
python test_pdf_masking.py your-file.pdf --password A123456789
```

### 積極模式（遮罩更多資訊）

```bash
# 會額外遮罩金額、長數字等
python test_pdf_masking.py your-file.pdf --aggressive
```

### 只遮罩特定類型

```bash
# 只遮罩身分證、電話、地址
python test_pdf_masking.py your-file.pdf --types taiwan_id,phone,address
```

## 查看結果

測試完成後，檢查 `output/` 目錄：

```bash
# 查看原始文字
cat output/your-file_original.txt

# 查看遮罩後文字
cat output/your-file_masked.txt

# 查看遮罩報告
cat output/your-file_report.txt

# 比較差異
diff output/your-file_original.txt output/your-file_masked.txt
```

## HTTP API 測試

如果你想透過 API 測試：

```bash
# 1. 啟動服務（終端 1）
python app.py

# 2. 測試偵測（終端 2）
curl -X POST http://localhost:12345/api/ai/detect-sensitive \
  -F "file=@your-file.pdf"

# 3. 測試遮罩 + AI 分析（需要 API Key）
curl -X POST http://localhost:12345/api/ai/mask-and-analyze \
  -F "file=@your-file.pdf" \
  -F "provider=openai"
```

## 完整測試流程

```bash
# 1. 測試個資遮罩功能（用範例文字）
python test_privacy.py

# 2. 測試你的 PDF 檔案
python test_pdf_masking.py your-file.pdf

# 3. 查看結果
ls -lh output/
cat output/your-file_report.txt

# 4. 如果有 AI API Key，測試 AI 分析
export OPENAI_API_KEY=your-key
python app.py &
curl -X POST http://localhost:12345/api/ai/mask-and-analyze \
  -F "file=@your-file.pdf"
```

## 支援的遮罩類型

| 類型代碼 | 說明 | 範例 |
|---------|------|------|
| `taiwan_id` | 身分證字號 | A123456789 |
| `phone` | 手機號碼 | 0912345678 |
| `landline` | 市話 | 02-12345678 |
| `credit_card` | 信用卡號 | 1234-5678-9012-3456 |
| `email` | 電子郵件 | test@example.com |
| `bank_account` | 銀行帳號 | 1234567890123 |
| `address` | 地址 | 台北市中正區忠孝東路100號 |
| `date_of_birth` | 出生日期 | 80年5月15日 |

## 常見問題

### Q: 測試後找不到輸出檔案？

A: 輸出檔案在 `output/` 目錄中：

```bash
ls -la output/
```

### Q: PDF 有密碼怎麼辦？

A: 使用 `--password` 參數：

```bash
python test_pdf_masking.py file.pdf --password YOUR_PASSWORD
```

或設定預設密碼在 `.env`：

```env
PDF_DEFAULT_PASSWORDS=password1,password2,password3
```

### Q: 想要遮罩更多資訊？

A: 使用積極模式：

```bash
python test_pdf_masking.py file.pdf --aggressive
```

### Q: 只想遮罩部分資訊？

A: 指定類型：

```bash
python test_pdf_masking.py file.pdf --types taiwan_id,phone
```

## 下一步

- 📖 [完整 AI 整合文件](docs/AI_INTEGRATION.md)
- 🛡️ [個資遮罩詳細說明](docs/PRIVACY_MASKING.md)
- 🔒 [PDF 密碼處理](docs/PDF_PASSWORD_HANDLING.md)

