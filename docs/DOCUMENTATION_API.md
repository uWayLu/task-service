# 文件 API 使用指南

## 💡 概述

我們實作了透過 HTTP 訪問文件的功能，但需要了解優缺點。

## 📊 方案比較

### 方案 1：HTTP 文件瀏覽（已實作）

**優點：**
- ✅ 方便內部查閱
- ✅ 不需要額外工具
- ✅ 支援格式化顯示
- ✅ 可以直接分享連結

**缺點：**
- ⚠️ 增加伺服器負擔
- ⚠️ 需要維護渲染邏輯
- ⚠️ SEO 不友善
- ⚠️ 不適合公開文件

**適用場景：**
- 內部團隊使用
- 快速查閱
- 開發/測試環境

### 方案 2：Swagger/OpenAPI（推薦給 API）

**優點：**
- ✅ 自動生成
- ✅ 互動式測試
- ✅ 標準化
- ✅ 工具支援完善

**缺點：**
- ⚠️ 只適合 API 文件
- ⚠️ 需要額外配置

**適用場景：**
- API 端點文件
- 對外提供的 API

### 方案 3：GitHub Pages / Read the Docs

**優點：**
- ✅ 專業外觀
- ✅ SEO 友善
- ✅ 版本控制
- ✅ 免費託管

**缺點：**
- ⚠️ 需要額外設定
- ⚠️ 更新需要 push

**適用場景：**
- 公開專案
- 詳細文件
- 長期維護

## 🚀 使用我們的文件 API

### 安裝依賴

```bash
pip install markdown==3.5.1
```

### 訪問文件

**1. 文件列表**
```
http://localhost:12345/api/docs
```

顯示所有可用文件的漂亮列表頁面。

**2. 查看特定文件**
```
http://localhost:12345/api/docs/README.md
http://localhost:12345/api/docs/QUICKSTART.md
http://localhost:12345/api/docs/HOW_TO_ADD_API.md
```

渲染為格式化的 HTML 頁面。

**3. 下載原始檔案**
```
http://localhost:12345/api/docs/raw/README.md
```

下載原始 Markdown 檔案。

### 截圖預覽

訪問 `http://localhost:12345/api/docs` 會看到：

```
┌─────────────────────────────────────────┐
│     📚 Task Service 文件中心            │
│     所有專案文件都在這裡                │
└─────────────────────────────────────────┘

📖 核心文件
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 📘 專案說明  │ │ 🚀 快速開始  │ │ 🔧 API 指南  │
│ 快速了解專案 │ │ 5分鐘啟動    │ │ 如何新增API  │
└──────────────┘ └──────────────┘ └──────────────┘
...
```

## ⚙️ 配置選項

### 啟用/停用文件 API

在生產環境可能想停用：

```python
# app.py
import os

def create_app():
    app = Flask(__name__)
    
    # 只在開發環境啟用文件瀏覽
    if os.getenv('FLASK_ENV') == 'development':
        from api import api_bp
        app.register_blueprint(api_bp)
    else:
        # 生產環境：只註冊需要的路由
        from api import health, webhook, document
        # 不註冊 docs
```

### 自訂樣式

編輯 `api/docs.py` 中的 `HTML_TEMPLATE` 可以修改外觀。

## 🎯 建議做法

### 小型/內部專案（我們的情況）

```
✅ 使用 HTTP 文件瀏覽（已實作）
✅ 簡單方便
✅ 適合團隊內部
```

### API 專案（進階）

```
✅ 加入 Swagger/OpenAPI
  → 自動生成 API 文件
  → 互動式測試

✅ HTTP 文件瀏覽作為補充
  → 通用文件（README, 教學等）
```

### 開源/公開專案

```
✅ GitHub Pages
  → 專業外觀
  → SEO 友善
  → 版本控制

⚠️ HTTP 文件瀏覽（可選）
  → 內部開發使用
```

## 📚 完整範例：加入 Swagger

如果想加入 API 文件（推薦）：

### 1. 安裝依賴

```bash
pip install flask-swagger-ui
```

### 2. 建立 Swagger 配置

```python
# api/swagger.py
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs/swagger'
API_URL = '/static/swagger.json'

swagger_bp = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Task Service API"
    }
)
```

### 3. 註冊 Blueprint

```python
# app.py
from api.swagger import swagger_bp
app.register_blueprint(swagger_bp)
```

### 4. 建立 Swagger JSON

```json
// static/swagger.json
{
  "swagger": "2.0",
  "info": {
    "title": "Task Service API",
    "version": "1.0.0"
  },
  "paths": {
    "/api/health": {
      "get": {
        "summary": "健康檢查",
        "responses": {
          "200": {
            "description": "服務正常"
          }
        }
      }
    }
  }
}
```

訪問：`http://localhost:12345/api/docs/swagger`

## 🔒 安全性考量

### 生產環境建議

1. **停用文件 API**（如果是敏感專案）
   ```python
   if os.getenv('ENABLE_DOCS') == 'true':
       from . import docs
   ```

2. **加入認證**
   ```python
   @api_bp.route('/docs')
   @require_auth  # 需要登入
   def docs_index():
       pass
   ```

3. **限制存取**
   ```python
   # 只允許內網
   if not request.remote_addr.startswith('192.168.'):
       abort(403)
   ```

## 💡 最終建議

### 對於你的專案

**✅ 建議使用 HTTP 文件瀏覽**

因為：
1. 內部團隊使用
2. 方便開發時查閱
3. 不需要額外設定
4. 簡單直觀

**⚠️ 生產環境可以考慮：**
1. 停用文件 API（設定環境變數）
2. 或加入簡單認證
3. 只在開發環境啟用

**🚀 未來可以加入：**
1. Swagger/OpenAPI（API 文件）
2. GitHub Pages（公開文件）

---

**現在你可以：**
```bash
# 1. 安裝 markdown
pip install markdown

# 2. 啟動服務
python app.py

# 3. 訪問文件
open http://localhost:12345/api/docs
```

**效果：** 漂亮的文件瀏覽介面！📚✨

