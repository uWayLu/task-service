# 如何新增 API 端點

本專案使用 **Blueprint** 模組化架構，所有 API 路由都在 `api/` 資料夾中定義。

## 📁 目前的結構

```
task-service/
├── app.py                      # 主程式（自動載入 Blueprint）
└── api/                        # API 路由模組
    ├── __init__.py            # Blueprint 註冊
    ├── health.py              # 健康檢查 API
    ├── webhook.py             # Webhook API
    └── document.py            # 文件管理 API
```

## 🚀 快速新增 API（3 步驟）

### 範例：新增「報表」功能

#### 步驟 1：建立新的路由檔案

```bash
touch api/reports.py
```

編輯 `api/reports.py`：

```python
"""
報表相關 API
"""
from flask import jsonify, request
from . import api_bp


@api_bp.route('/reports', methods=['GET'])
def list_reports():
    """
    取得報表列表
    
    Returns:
        JSON: 報表清單
    """
    # 實際應從資料庫查詢
    reports = [
        {'id': 1, 'name': '每月財務報表', 'created_at': '2024-11-01'},
        {'id': 2, 'name': '信用卡分析', 'created_at': '2024-11-15'}
    ]
    
    return jsonify({
        'status': 'success',
        'data': reports,
        'total': len(reports)
    })


@api_bp.route('/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """
    取得特定報表
    
    Args:
        report_id: 報表 ID
        
    Returns:
        JSON: 報表詳細資料
    """
    report = {
        'id': report_id,
        'name': '每月財務報表',
        'data': {'income': 50000, 'expense': 30000}
    }
    
    return jsonify({
        'status': 'success',
        'data': report
    })


@api_bp.route('/reports/generate', methods=['POST'])
def generate_report():
    """
    產生新報表
    
    Request Body:
        {
            "type": "monthly",
            "date_range": {"start": "2024-11-01", "end": "2024-11-30"}
        }
        
    Returns:
        JSON: 新報表資訊
    """
    data = request.json
    
    # 驗證輸入
    if not data or 'type' not in data:
        return jsonify({
            'status': 'error',
            'message': '缺少必要參數: type'
        }), 400
    
    # 產生報表邏輯
    new_report = {
        'id': 3,
        'type': data['type'],
        'status': 'processing',
        'message': '報表產生中，請稍後查詢'
    }
    
    return jsonify({
        'status': 'success',
        'data': new_report
    }), 201
```

#### 步驟 2：註冊路由

編輯 `api/__init__.py`，加入一行導入：

```python
"""
API Blueprint Package
"""
from flask import Blueprint

# 建立 API Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 導入路由（避免循環導入）
from . import health, webhook, document
from . import reports  # ← 加這一行就好！

__all__ = ['api_bp']
```

#### 步驟 3：測試新 API

```bash
# 啟動服務
python app.py

# 測試 API
curl http://localhost:12345/api/reports
curl http://localhost:12345/api/reports/1
curl -X POST http://localhost:12345/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{"type": "monthly"}'
```

## ✅ 就這麼簡單！

- ✨ **不需要修改 `app.py`**
- ✨ **不需要重啟服務**（開發模式下自動重載）
- ✨ **自動掛載到 `/api/` 路徑下**

## 📚 更多範例

### 範例 1：帶參數的 GET 請求

```python
@api_bp.route('/search', methods=['GET'])
def search():
    """搜尋功能"""
    keyword = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    return jsonify({
        'keyword': keyword,
        'page': page,
        'results': []
    })

# 使用方式
# curl "http://localhost:12345/api/search?q=銀行&page=2"
```

### 範例 2：需要檔案上傳的 POST

```python
@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """檔案上傳"""
    if 'file' not in request.files:
        return jsonify({'error': '沒有檔案'}), 400
    
    file = request.files['file']
    # 處理檔案...
    
    return jsonify({'message': '上傳成功'})

# 使用方式
# curl -X POST http://localhost:12345/api/upload -F "file=@test.pdf"
```

### 範例 3：RESTful 完整 CRUD

```python
# api/users.py

from . import api_bp

@api_bp.route('/users', methods=['GET'])
def list_users():
    """列出所有使用者"""
    return jsonify({'users': []})

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """取得特定使用者"""
    return jsonify({'user': {'id': user_id}})

@api_bp.route('/users', methods=['POST'])
def create_user():
    """建立新使用者"""
    data = request.json
    return jsonify({'user': data}), 201

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新使用者"""
    data = request.json
    return jsonify({'user': data})

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """刪除使用者"""
    return jsonify({'message': 'deleted'}), 204
```

## 🎯 最佳實踐

### 1. 檔案命名規範

```
api/
├── auth.py          # 認證相關
├── users.py         # 使用者管理
├── documents.py     # 文件處理
├── reports.py       # 報表功能
└── analytics.py     # 分析統計
```

**建議**：
- ✅ 使用複數名詞（reports, users）
- ✅ 小寫 + 底線（snake_case）
- ✅ 一個檔案一個功能模組

### 2. 路由命名規範

```python
# ✅ 好的命名
@api_bp.route('/reports')
@api_bp.route('/documents/types')
@api_bp.route('/analytics/summary')

# ❌ 避免的命名
@api_bp.route('/getReports')      # 不要在 URL 中使用動詞
@api_bp.route('/document_types')  # 使用 / 分隔，不用底線
@api_bp.route('/Analytics')       # 統一小寫
```

### 3. 回應格式統一

```python
# 成功回應
return jsonify({
    'status': 'success',
    'data': {...},
    'message': '操作成功'  # 選填
}), 200

# 錯誤回應
return jsonify({
    'status': 'error',
    'message': '錯誤描述',
    'error_code': 'INVALID_INPUT'  # 選填
}), 400
```

### 4. 加入文件註解

```python
@api_bp.route('/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """
    取得特定報表
    
    Args:
        report_id (int): 報表 ID
        
    Query Parameters:
        format (str): 回傳格式 (json/pdf)
        
    Returns:
        JSON: 報表詳細資料
        
    Raises:
        404: 報表不存在
    """
    pass
```

## 🔧 進階技巧

### 1. 共用邏輯（裝飾器）

```python
# api/decorators.py

from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    """API 金鑰認證裝飾器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != 'your-secret-key':
            return jsonify({'error': '未授權'}), 401
        return f(*args, **kwargs)
    return decorated


# 使用方式
from .decorators import require_api_key

@api_bp.route('/admin/users', methods=['GET'])
@require_api_key
def admin_users():
    """需要認證的 API"""
    return jsonify({'users': []})
```

### 2. 錯誤處理

```python
@api_bp.route('/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    try:
        # 查詢報表
        report = fetch_report(report_id)
        
        if not report:
            return jsonify({
                'status': 'error',
                'message': '報表不存在'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': report
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'參數錯誤: {str(e)}'
        }), 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': '伺服器錯誤'
        }), 500
```

### 3. 使用資料庫（範例）

```python
# 假設你有資料庫連接
from models import db, Report

@api_bp.route('/reports', methods=['GET'])
def list_reports():
    """從資料庫查詢報表"""
    reports = Report.query.all()
    
    return jsonify({
        'status': 'success',
        'data': [r.to_dict() for r in reports]
    })
```

## 📋 Checklist

新增 API 時確認：

- [ ] 在 `api/` 下建立新檔案
- [ ] 在 `api/__init__.py` 中導入
- [ ] 路由加上 `@api_bp.route(...)`
- [ ] 函式加上文件註解
- [ ] 統一回應格式
- [ ] 處理錯誤情況
- [ ] 測試 API 功能
- [ ] 更新 README（如需要）

## 🎉 恭喜！

你已經掌握了在本專案中新增 API 的方法。

**記住**：
- 所有路由自動掛載到 `/api/` 路徑下
- 修改後開發模式會自動重載
- 保持程式碼清晰和模組化

有問題？查看現有的 `api/webhook.py` 或 `api/document.py` 作為範例！

