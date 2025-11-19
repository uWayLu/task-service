# Flask 專案結構指南

Flask 非常靈活，但社群有一些約定俗成的結構模式。

## 📊 Flask 專案結構的演進

### 1️⃣ 小型專案（Single Module）

**官方入門推薦**

```
my-app/
├── app.py              # 所有程式碼
├── requirements.txt
└── templates/          # Jinja2 模板（如果需要）
    └── index.html
```

**適用：**
- ✅ 學習 Flask
- ✅ 原型開發
- ✅ 微服務（單一功能）
- ✅ < 500 行程式碼

---

### 2️⃣ 中型專案（Function-based）

**我們目前使用的結構** ⭐

```
task-service/
├── app.py                      # 主程式
├── config.py                   # 配置
├── requirements.txt
│
├── api/                        # Blueprint: API 路由
│   ├── __init__.py            # 註冊 Blueprint
│   ├── health.py              # 功能模組
│   ├── webhook.py
│   └── document.py
│
└── utils/                      # 工具函式
    ├── pdf_parser.py
    └── document_processor.py
```

**適用：**
- ✅ API 服務（我們的情況）
- ✅ 中型專案（500-2000 行）
- ✅ 功能模組化
- ✅ 團隊協作

**優點：**
- 清晰的功能分離
- 易於測試
- 擴展性好
- 符合 Flask Blueprint 慣例

---

### 3️⃣ 大型專案（Application Factory）

**Flask 官方推薦的可擴展結構**

```
my-app/
├── instance/                   # 實例配置（不提交）
│   └── config.py
│
├── myapp/                      # 應用程式套件
│   ├── __init__.py            # Application Factory
│   │
│   ├── models/                 # 資料模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── document.py
│   │
│   ├── views/                  # 視圖/路由
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── api.py
│   │
│   ├── services/               # 業務邏輯
│   │   ├── __init__.py
│   │   ├── pdf_service.py
│   │   └── document_service.py
│   │
│   ├── utils/                  # 工具函式
│   │   └── helpers.py
│   │
│   ├── templates/              # Jinja2 模板
│   └── static/                 # 靜態檔案
│
├── tests/                      # 測試
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
│
├── migrations/                 # 資料庫遷移
├── config.py                   # 配置檔案
├── requirements.txt
└── run.py                      # 啟動腳本
```

**適用：**
- ✅ 大型應用（> 2000 行）
- ✅ 需要多環境配置
- ✅ 有資料庫
- ✅ 團隊開發

---

### 4️⃣ 企業級專案（Domain-Driven Design）

```
my-app/
├── app/
│   ├── domain/                 # 領域模型
│   │   ├── entities/
│   │   ├── repositories/
│   │   └── services/
│   │
│   ├── infrastructure/         # 基礎設施
│   │   ├── database/
│   │   ├── external_api/
│   │   └── messaging/
│   │
│   ├── application/            # 應用層
│   │   ├── use_cases/
│   │   └── dto/
│   │
│   └── presentation/           # 表現層
│       ├── api/
│       └── web/
│
├── tests/
└── ...
```

**適用：**
- ✅ 複雜業務邏輯
- ✅ 大型團隊
- ✅ 長期維護

---

## 🎯 我們的結構分析

### 目前結構

```
task-service/
├── app.py                      # ✅ 主程式（Application Factory）
├── config.py                   # ✅ 配置管理
│
├── api/                        # ✅ Blueprint 模組（路由）
│   ├── __init__.py
│   ├── health.py
│   ├── webhook.py
│   ├── document.py
│   └── test.py
│
├── utils/                      # ✅ 工具模組
│   ├── pdf_parser.py
│   └── document_processor.py
│
├── docs/                       # ✅ 文件
├── examples/                   # ✅ 範例
├── test_files/                 # ✅ 測試資料
└── tests/                      # ⚠️ 待加入：單元測試
```

### 符合的 Flask 慣例 ✅

1. **Blueprint 架構** ✅
   - 使用 Blueprint 組織路由
   - 模組化設計
   - URL 前綴 (`/api`)

2. **Application Factory** ✅
   ```python
   def create_app():
       app = Flask(__name__)
       # 配置...
       app.register_blueprint(api_bp)
       return app
   ```

3. **配置分離** ✅
   - `config.py` 管理配置
   - `.env` 環境變數
   - 開發/生產環境分離

4. **模組命名** ✅
   - `snake_case` 檔案名稱
   - 清晰的模組職責

### 可以改進的地方 ⚠️

1. **tests/ 目錄** ⚠️
   ```
   tests/
   ├── __init__.py
   ├── conftest.py              # pytest 配置
   ├── test_pdf_parser.py
   └── test_api.py
   ```

2. **instance/ 目錄**（如需要）⚠️
   ```
   instance/
   └── config.py                # 不提交的配置
   ```

---

## 📚 Flask 官方建議

### 來源：Flask 官方文件

1. **小型應用** → 單檔案
2. **中型應用** → Blueprint
3. **大型應用** → Application Factory + 套件結構

### Blueprint 最佳實踐

```python
# ✅ 我們的做法（正確）
api/
├── __init__.py              # 定義並註冊 Blueprint
├── health.py                # 路由模組
└── webhook.py

# api/__init__.py
from flask import Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

from . import health, webhook  # 導入路由
```

### Application Factory 模式

```python
# ✅ 我們的做法（符合）
def create_app():
    app = Flask(__name__)
    # 配置
    # 註冊 Blueprint
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
```

---

## 🌟 社群流行結構

### Cookiecutter Flask

**社群維護的專案模板**

```
project/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   └── forms.py
├── tests/
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
└── manage.py
```

### Flask-RESTful 風格

**API 專案常見結構**

```
api-project/
├── app/
│   ├── __init__.py
│   ├── resources/           # API 資源
│   │   ├── user.py
│   │   └── document.py
│   ├── models/
│   └── schemas/             # Marshmallow schemas
├── tests/
└── run.py
```

### Flask-RESTX 風格

**有 Swagger 的 API 專案**

```
api-project/
├── app/
│   ├── __init__.py
│   ├── apis/
│   │   ├── __init__.py      # Namespace
│   │   ├── health.py
│   │   └── documents.py
│   └── models/
└── run.py
```

---

## 🔄 結構演進建議

### 階段 1：現在（中型專案）✅

```
task-service/
├── app.py
├── api/                     # Blueprint
└── utils/                   # 工具
```

**維持現狀，因為：**
- ✅ 符合 Flask 慣例
- ✅ 適合專案規模
- ✅ 清晰易懂
- ✅ 易於擴展

### 階段 2：如果加入資料庫

```
task-service/
├── app/                     # 改成套件
│   ├── __init__.py         # Application Factory
│   ├── models/             # ORM 模型
│   ├── api/                # Blueprint
│   ├── services/           # 業務邏輯
│   └── utils/
├── migrations/             # Alembic 遷移
├── tests/
└── run.py
```

### 階段 3：如果變成大型應用

```
task-service/
├── app/
│   ├── domain/             # 領域邏輯
│   ├── infrastructure/     # 資料存取
│   ├── application/        # 用例
│   └── presentation/       # API/Web
├── tests/
└── ...
```

---

## 📝 命名慣例比較

### 我們的命名 vs Flask 慣例

| 項目 | 我們的做法 | Flask 慣例 | 說明 |
|------|-----------|-----------|------|
| 主程式 | `app.py` | `app.py` 或 `run.py` | ✅ 都可以 |
| Blueprint | `api/` | 通常 `views/` 或 `blueprints/` | ✅ 語意化更好 |
| 工具 | `utils/` | `utils/` 或 `helpers/` | ✅ 標準 |
| 配置 | `config.py` | `config.py` | ✅ 標準 |
| 測試 | `test_*.py` | `tests/` 目錄 | ⚠️ 建議統一到 tests/ |

---

## 💡 其他 Python Web 框架比較

### Django 結構（供參考）

```
django-project/
├── myproject/              # 專案設定
│   ├── settings.py
│   └── urls.py
├── myapp/                  # 應用程式
│   ├── models.py
│   ├── views.py
│   └── urls.py
└── manage.py
```

**特點：**
- 更嚴格的結構
- 自動生成
- 約定大於配置

### FastAPI 結構

```
fastapi-project/
├── app/
│   ├── main.py
│   ├── routers/            # 路由
│   ├── models/
│   └── schemas/            # Pydantic
└── tests/
```

**特點：**
- 類似 Flask Blueprint
- 重視型別提示

---

## 🎓 建議

### 對於我們的專案

**✅ 保持現有結構**，因為：

1. **符合 Flask 慣例**
   - Blueprint 架構 ✅
   - Application Factory ✅
   - 模組化設計 ✅

2. **適合專案規模**
   - API 服務（不需要模板）
   - 中型專案（< 2000 行）
   - 清晰的功能分離

3. **易於擴展**
   - 新增 API：只要在 `api/` 加檔案
   - 新增功能：在 `utils/` 或新建目錄
   - 加資料庫：可以平滑過渡

### 建議的小改進

1. **加入 tests/ 目錄**
   ```bash
   mkdir tests
   touch tests/__init__.py
   touch tests/conftest.py
   ```

2. **可選：改名 utils/ → services/**
   ```
   services/          # 更語意化
   ├── pdf_service.py
   └── document_service.py
   ```
   但 `utils/` 也完全沒問題！

3. **如果需要：加入 instance/**
   ```
   instance/
   └── config.py     # 本地配置（不提交）
   ```

---

## 📖 參考資源

### 官方文件
- [Flask Patterns](https://flask.palletsprojects.com/patterns/)
- [Application Factories](https://flask.palletsprojects.com/patterns/appfactories/)
- [Blueprints](https://flask.palletsprojects.com/blueprints/)

### 社群模板
- [Cookiecutter Flask](https://github.com/cookiecutter-flask/cookiecutter-flask)
- [Flask-RESTful](https://flask-restful.readthedocs.io/)
- [Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

### 最佳實踐
- [Flask Best Practices](https://www.digitalocean.com/community/tutorials/how-to-structure-large-flask-applications)
- [Structuring Flask Apps](https://exploreflask.com/en/latest/blueprints.html)

---

## 🎯 結論

### 我們的結構評分

| 方面 | 評分 | 說明 |
|------|------|------|
| **符合 Flask 慣例** | ⭐⭐⭐⭐⭐ | 完全符合 |
| **適合專案規模** | ⭐⭐⭐⭐⭐ | 完美匹配 |
| **可維護性** | ⭐⭐⭐⭐⭐ | 清晰易懂 |
| **可擴展性** | ⭐⭐⭐⭐☆ | 易於擴展 |
| **測試友善** | ⭐⭐⭐⭐☆ | 加入 tests/ 更好 |

### 總結

**✅ 我們的結構是標準且推薦的 Flask 中型專案結構**

- 使用了 Blueprint（Flask 官方推薦）
- Application Factory 模式（最佳實踐）
- 模組化設計（社群慣例）
- 適合 API 服務（符合需求）

**不需要改變，除非：**
- 專案變得非常大（> 5000 行）
- 需要加入資料庫
- 需要更複雜的業務邏輯

**現在的結構可以用到專案結束！** 🎉

