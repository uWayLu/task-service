FROM python:3.11-slim

LABEL maintainer="Task Service"
LABEL description="Flask API for processing financial PDF documents from Gmail webhooks"

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 建立上傳資料夾
RUN mkdir -p uploads

# 設定環境變數
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5000

# 暴露端口
EXPOSE 5000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/api/health')"

# 使用 gunicorn 啟動應用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]

