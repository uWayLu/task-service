# AI 整合說明文件

## 📋 概述

本專案整合了 AI 服務用於分析金融文件，支援：
- ✅ OpenAI (GPT-4, GPT-3.5)
- ✅ Anthropic Claude
- ✅ 自訂 API 端點

## 🔧 環境設定

### OpenAI

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

### Anthropic Claude

```env
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### 自訂 API

```env
AI_API_KEY=your-custom-key
AI_API_ENDPOINT=https://your-endpoint.com/api
```

## 📡 API 端點

### 1. 分析文件（不遮罩個資）

**端點**: `POST /api/ai/analyze-document`

**參數**:
- `file`: PDF 檔案（必填）
- `password`: PDF 密碼（選填）
- `provider`: AI 服務提供者 (`openai`/`claude`，預設 `openai`)
- `model`: 模型名稱（選填）
- `document_type`: 文件類型（選填，預設 `financial`）

**範例**:
```bash
curl -X POST http://localhost:12345/api/ai/analyze-document \
  -F "file=@statement.pdf" \
  -F "provider=openai" \
  -F "document_type=bank_statement"
```

**回應**:
```json
{
  "success": true,
  "analysis": {
    "document_type": "銀行對帳單",
    "summary": "...",
    "key_information": {...},
    "transactions": [...]
  },
  "metadata": {
    "provider": "openai",
    "model": "gpt-4-turbo-preview",
    "pages": 5,
    "usage": {...}
  }
}
```

### 2. 遮罩個資後分析

**端點**: `POST /api/ai/mask-and-analyze`

**參數**:
- `file`: PDF 檔案（必填）
- `password`: PDF 密碼（選填）
- `provider`: AI 服務提供者（選填）
- `model`: 模型名稱（選填）
- `document_type`: 文件類型（選填）
- `mask_types`: 要遮罩的類型，逗號分隔（選填）
- `aggressive`: 是否使用積極模式 (`true`/`false`，預設 `false`)

**範例**:
```bash
# 自動遮罩所有個資
curl -X POST http://localhost:12345/api/ai/mask-and-analyze \
  -F "file=@statement.pdf" \
  -F "provider=openai"

# 僅遮罩特定類型
curl -X POST http://localhost:12345/api/ai/mask-and-analyze \
  -F "file=@statement.pdf" \
  -F "mask_types=taiwan_id,phone,address"

# 積極模式（遮罩更多資訊）
curl -X POST http://localhost:12345/api/ai/mask-and-analyze \
  -F "file=@statement.pdf" \
  -F "aggressive=true"
```

**回應**:
```json
{
  "success": true,
  "analysis": {...},
  "masking": {
    "masked_count": 5,
    "sensitive_items": [
      {"type": "身分證字號", "masked_value": "A*********9"},
      {"type": "手機號碼", "masked_value": "0912****78"}
    ]
  },
  "metadata": {...}
}
```

### 3. 偵測敏感資訊

**端點**: `POST /api/ai/detect-sensitive`

**參數**:
- `file`: PDF 檔案（必填）
- `password`: PDF 密碼（選填）
- `mask_types`: 要偵測的類型，逗號分隔（選填）

**範例**:
```bash
curl -X POST http://localhost:12345/api/ai/detect-sensitive \
  -F "file=@statement.pdf"
```

**回應**:
```json
{
  "success": true,
  "sensitive_count": 8,
  "sensitive_items": [
    {
      "type": "身分證字號",
      "count": 2,
      "examples": ["A*********9", "B*********1"]
    },
    {
      "type": "手機號碼",
      "count": 3,
      "examples": ["0912****78", "0923****89"]
    }
  ],
  "metadata": {
    "pages": 5
  }
}
```

### 4. 取得支援的遮罩類型

**端點**: `GET /api/ai/mask-types`

**範例**:
```bash
curl http://localhost:12345/api/ai/mask-types
```

**回應**:
```json
{
  "mask_types": [
    {"type": "taiwan_id", "name": "身分證字號"},
    {"type": "phone", "name": "手機號碼"},
    {"type": "landline", "name": "市話"},
    {"type": "credit_card", "name": "信用卡號"},
    {"type": "email", "name": "電子郵件"},
    {"type": "bank_account", "name": "銀行帳號"},
    {"type": "address", "name": "地址"},
    {"type": "date_of_birth", "name": "出生日期"}
  ]
}
```

## 🔒 個資遮罩類型

### 支援的個資類型

| 類型 | 說明 | 範例 | 遮罩後 |
|-----|------|------|--------|
| `taiwan_id` | 身分證字號 | A123456789 | A*********9 |
| `phone` | 手機號碼 | 0912345678 | 0912****78 |
| `landline` | 市話 | 02-12345678 | 02-****5678 |
| `credit_card` | 信用卡號 | 1234-5678-9012-3456 | **** **** **** 3456 |
| `email` | 電子郵件 | test@example.com | t***@example.com |
| `bank_account` | 銀行帳號 | 1234567890123 | *********0123 |
| `address` | 地址 | 台北市中正區忠孝東路100號 | 台北市中正區*** |
| `date_of_birth` | 出生日期 | 80年5月15日 | ****/**/** |

### 積極模式額外遮罩

積極模式（`aggressive=true`）會額外遮罩：
- 金額（NT$ 12,345 → NT$ ***）
- 長數字（超過 6 位數）

## 🧪 程式碼範例

### Python

```python
from utils.privacy_masker import PrivacyMasker, SmartPrivacyMasker
from utils.ai_integrator import AIIntegrator, AIProvider

# 基本遮罩
masker = PrivacyMasker()
result = masker.mask("身分證：A123456789")
print(result.masked)  # 身分證：A*********9

# 智慧遮罩（積極模式）
smart_masker = SmartPrivacyMasker(aggressive=True)
result = smart_masker.mask("金額：NT$ 12,345")
print(result.masked)  # 金額：NT$ ***

# AI 分析
integrator = AIIntegrator(provider=AIProvider.OPENAI)
response = integrator.analyze_document(text, document_type="bank_statement")
print(response.content)
```

### 測試工具

```bash
# 測試個資遮罩
python test_privacy.py

# 測試 AI 整合（需要先設定 API Key）
curl -X POST http://localhost:12345/api/ai/mask-and-analyze \
  -F "file=@test.pdf"
```

## 📝 使用建議

### 何時使用遮罩

**建議遮罩的情況**：
- ✅ 傳送給第三方 AI 服務
- ✅ 儲存分析結果
- ✅ 產生報告或匯出資料
- ✅ 記錄日誌

**可以不遮罩的情況**：
- ❌ 內部處理
- ❌ 需要完整資料進行精確分析
- ❌ 使用自架 AI 模型

### 遮罩策略建議

1. **一般金融文件**：使用預設遮罩
   ```bash
   -F "file=@document.pdf"
   ```

2. **敏感身分文件**：使用積極模式
   ```bash
   -F "file=@document.pdf" -F "aggressive=true"
   ```

3. **僅需要交易資訊**：選擇性遮罩
   ```bash
   -F "file=@document.pdf" -F "mask_types=taiwan_id,address,date_of_birth"
   ```

## ⚠️ 注意事項

1. **API 金鑰安全**
   - 不要將 API 金鑰提交到版本控制
   - 使用環境變數管理金鑰
   - 定期更換金鑰

2. **成本控制**
   - OpenAI/Claude 為計量收費
   - 建議設定使用上限
   - 監控 API 使用量

3. **資料隱私**
   - 遮罩後的資料仍可能含有敏感資訊
   - 建議使用自架模型處理高敏感資料
   - 遵守相關資料保護法規

4. **錯誤處理**
   - AI API 可能失敗或超時
   - 建議實作重試機制
   - 記錄錯誤以便除錯

## 🔄 更新 Webhook 整合個資遮罩

原有的 Gmail webhook 也支援個資遮罩：

```bash
# Gmail Apps Script 呼叫時加入 mask_privacy 參數
curl -X POST http://your-server/api/webhook/gmail \
  -F "file=@attachment.pdf" \
  -F "message_id=xxx" \
  -F "mask_privacy=true"
```

回應會包含遮罩資訊：
```json
{
  "success": true,
  "document_type": "...",
  "summary": "...",
  "privacy_masking": {
    "masked_count": 5,
    "sensitive_types": ["身分證字號", "手機號碼"]
  }
}
```

## 📚 相關文件

- [個資遮罩實作](PRIVACY_MASKING.md)
- [AI 模型選擇指南](AI_MODEL_GUIDE.md)
- [API 金鑰管理](API_KEY_MANAGEMENT.md)

