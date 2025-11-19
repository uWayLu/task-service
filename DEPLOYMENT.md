# 部署指南

本文件說明如何部署 Task Service API 到各種環境。

## 目錄

- [本地開發](#本地開發)
- [Docker 部署](#docker-部署)
- [雲端平台部署](#雲端平台部署)
- [反向代理設定](#反向代理設定)
- [監控與日誌](#監控與日誌)

## 本地開發

### 快速啟動

```bash
# 使用啟動腳本
./run.sh
```

### 手動啟動

```bash
# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
# 編輯 .env 檔案

# 啟動服務
python app.py
```

## Docker 部署

### 使用 Docker Compose（推薦）

```bash
# 建立並啟動容器
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down

# 重新建立容器
docker-compose up -d --build
```

### 使用 Docker 指令

```bash
# 建立映像
docker build -t task-service:latest .

# 啟動容器
docker run -d \
  --name task-service \
  -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -v $(pwd)/uploads:/app/uploads \
  task-service:latest

# 查看日誌
docker logs -f task-service

# 停止容器
docker stop task-service
docker rm task-service
```

### Docker 環境變數設定

建立 `.env` 檔案：

```env
SECRET_KEY=your-production-secret-key-here
FLASK_ENV=production
PORT=5000
MAX_CONTENT_LENGTH=16777216
DELETE_AFTER_PROCESS=true
```

## 雲端平台部署

### Heroku

```bash
# 登入 Heroku
heroku login

# 建立應用
heroku create task-service-api

# 設定環境變數
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production

# 部署
git push heroku main

# 查看日誌
heroku logs --tail
```

建立 `Procfile`：

```
web: gunicorn app:app
```

### Railway

1. 連接 GitHub 儲存庫
2. 選擇專案目錄
3. Railway 會自動偵測 Dockerfile
4. 設定環境變數
5. 部署

### Render

1. 建立新的 Web Service
2. 連接 GitHub 儲存庫
3. 設定：
   - Environment: Docker
   - Build Command: `docker build -t task-service .`
   - Start Command: `gunicorn app:app`
4. 設定環境變數
5. 部署

### Google Cloud Run

```bash
# 安裝 gcloud CLI
# https://cloud.google.com/sdk/docs/install

# 認證
gcloud auth login

# 設定專案
gcloud config set project YOUR_PROJECT_ID

# 建立容器映像
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/task-service

# 部署到 Cloud Run
gcloud run deploy task-service \
  --image gcr.io/YOUR_PROJECT_ID/task-service \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated \
  --set-env-vars SECRET_KEY=your-secret-key

# 查看服務 URL
gcloud run services describe task-service --region asia-east1
```

### AWS ECS (Elastic Container Service)

1. 建立 ECR 儲存庫
2. 推送 Docker 映像到 ECR
3. 建立 ECS 叢集
4. 定義任務
5. 建立服務
6. 設定 Load Balancer

```bash
# 登入 ECR
aws ecr get-login-password --region ap-northeast-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com

# 建立儲存庫
aws ecr create-repository --repository-name task-service

# 標記映像
docker tag task-service:latest YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/task-service:latest

# 推送映像
docker push YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/task-service:latest
```

## 反向代理設定

### Nginx

建立 `/etc/nginx/sites-available/task-service`：

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 增加超時時間（處理大檔案）
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        
        # 增加上傳大小限制
        client_max_body_size 20M;
    }
}
```

啟用網站：

```bash
sudo ln -s /etc/nginx/sites-available/task-service /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 使用 Let's Encrypt 設定 HTTPS

```bash
# 安裝 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 取得憑證
sudo certbot --nginx -d api.yourdomain.com

# 自動更新憑證
sudo certbot renew --dry-run
```

### Apache

建立 `/etc/apache2/sites-available/task-service.conf`：

```apache
<VirtualHost *:80>
    ServerName api.yourdomain.com
    
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    # 增加超時時間
    ProxyTimeout 300
    
    # 日誌
    ErrorLog ${APACHE_LOG_DIR}/task-service-error.log
    CustomLog ${APACHE_LOG_DIR}/task-service-access.log combined
</VirtualHost>
```

啟用設定：

```bash
sudo a2enmod proxy proxy_http
sudo a2ensite task-service
sudo systemctl restart apache2
```

## 使用 Systemd 管理服務

建立 `/etc/systemd/system/task-service.service`：

```ini
[Unit]
Description=Task Service API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/www-data/task-service
Environment="PATH=/home/www-data/task-service/venv/bin"
ExecStart=/home/www-data/task-service/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    --access-logfile /var/log/task-service/access.log \
    --error-logfile /var/log/task-service/error.log \
    app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

啟用並啟動服務：

```bash
# 建立日誌目錄
sudo mkdir -p /var/log/task-service
sudo chown www-data:www-data /var/log/task-service

# 啟用服務
sudo systemctl daemon-reload
sudo systemctl enable task-service
sudo systemctl start task-service

# 查看狀態
sudo systemctl status task-service

# 查看日誌
sudo journalctl -u task-service -f
```

## 監控與日誌

### 日誌設定

在 `app.py` 中加入：

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    # 檔案日誌
    file_handler = RotatingFileHandler(
        'logs/task-service.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Task Service startup')
```

### 使用 Prometheus 監控

安裝 prometheus-flask-exporter：

```bash
pip install prometheus-flask-exporter
```

在 `app.py` 中加入：

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
```

訪問 `http://localhost:5000/metrics` 查看指標。

### 健康檢查

API 提供健康檢查端點：

```bash
curl http://localhost:5000/api/health
```

設定定期健康檢查：

```bash
# 使用 cron 每分鐘檢查
* * * * * curl -f http://localhost:5000/api/health || systemctl restart task-service
```

## 效能優化

### Gunicorn 設定

```bash
# 根據 CPU 核心數調整 workers
gunicorn \
  --workers $(( 2 * $(nproc) + 1 )) \
  --worker-class gevent \
  --timeout 120 \
  --keep-alive 5 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --bind 0.0.0.0:5000 \
  app:app
```

### 快取設定

安裝 Redis：

```bash
pip install redis flask-caching
```

在 `app.py` 中加入：

```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})
```

## 安全性檢查清單

- [ ] 設定強隨機 SECRET_KEY
- [ ] 使用 HTTPS
- [ ] 設定防火牆規則
- [ ] 限制檔案上傳大小
- [ ] 實作 API 認證（API Key 或 JWT）
- [ ] 啟用 rate limiting
- [ ] 定期更新依賴套件
- [ ] 設定適當的 CORS 政策
- [ ] 保護敏感資訊（不要提交 .env 到版本控制）
- [ ] 定期備份資料

## 備份與還原

### 備份

```bash
# 備份上傳檔案
tar -czf uploads-backup-$(date +%Y%m%d).tar.gz uploads/

# 備份日誌
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# 備份設定
cp .env env-backup-$(date +%Y%m%d)
```

### 還原

```bash
# 還原上傳檔案
tar -xzf uploads-backup-20241118.tar.gz

# 還原日誌
tar -xzf logs-backup-20241118.tar.gz
```

## 疑難排解

### 服務無法啟動

```bash
# 檢查端口是否被占用
sudo lsof -i :5000

# 檢查日誌
journalctl -u task-service -n 50

# 檢查權限
ls -la /home/www-data/task-service
```

### PDF 解析失敗

- 確認 PDF 不是掃描檔案（圖片格式）
- 檢查 PDF 是否損壞
- 查看詳細錯誤日誌

### 記憶體使用過高

- 減少 Gunicorn workers 數量
- 增加伺服器記憶體
- 優化 PDF 處理邏輯

## 擴展建議

### 水平擴展

使用 Load Balancer 分散流量到多個實例：

```
                     ┌─> Task Service 1
Load Balancer ───────┼─> Task Service 2
                     └─> Task Service 3
```

### 非同步處理

使用 Celery 處理耗時任務：

```bash
pip install celery redis
```

### 資料庫整合

如需儲存處理結果：

```bash
pip install flask-sqlalchemy psycopg2-binary
```

## 支援

如遇問題，請查看：
- 專案 README.md
- 測試範例：examples/test_samples.md
- GitHub Issues

---

更新日期：2024-11-18

