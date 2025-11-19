# 資料目錄

這個資料夾用來存放**處理後的資料和持久化資料**。

## 📂 用途

- 儲存處理結果（如需要）
- 統計資料
- 快取資料
- 設定檔案

## 📋 建議的資料結構

```
data/
├── processed/              # 處理後的結果
│   ├── 2024-11/
│   │   ├── bank_statements/
│   │   ├── credit_cards/
│   │   └── transactions/
│   └── archive/           # 歷史資料
│
├── cache/                 # 快取資料
│   └── pdf_cache/
│
├── config/                # 配置檔案
│   ├── bank_patterns.json
│   └── extraction_rules.json
│
└── stats/                 # 統計資料
    └── processing_stats.json
```

## 🔧 使用範例

### 儲存處理結果

```python
# 在 document_processor.py 中
import json
from datetime import datetime
from pathlib import Path

def save_result(result, filename):
    """儲存處理結果"""
    date_str = datetime.now().strftime('%Y-%m')
    doc_type = result['document_type']
    
    # 建立目錄
    output_dir = Path('data/processed') / date_str / f"{doc_type}s"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 儲存檔案
    output_file = output_dir / f"{filename}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
```

### 讀取設定檔

```python
def load_bank_patterns():
    """載入銀行格式設定"""
    config_file = Path('data/config/bank_patterns.json')
    if config_file.exists():
        with open(config_file) as f:
            return json.load(f)
    return {}
```

## ⚠️ 注意事項

1. **不要提交敏感資料**
   - `data/` 資料夾已被 `.gitignore` 忽略
   - 確保不包含真實個人資訊

2. **定期清理**
   - 設定資料保留期限
   - 定期清理舊資料

3. **備份重要資料**
   - 設定檔案應該備份
   - 統計資料可定期匯出

## 📊 資料格式範例

### 處理結果 (processed)

```json
{
  "document_type": "bank_statement",
  "processed_at": "2024-11-19T10:30:00",
  "summary": {
    "account_number": "1234567890",
    "closing_balance": 48500.00
  }
}
```

### 統計資料 (stats)

```json
{
  "total_processed": 150,
  "by_type": {
    "bank_statement": 50,
    "credit_card": 80,
    "transaction_notice": 20
  },
  "last_updated": "2024-11-19T10:30:00"
}
```

### 設定檔案 (config)

```json
{
  "banks": {
    "ctbc": {
      "name": "中國信託",
      "account_pattern": "\\d{3}-\\d{7}",
      "date_format": "YYYY/MM/DD"
    }
  }
}
```

