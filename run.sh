#!/bin/bash

# Task Service 啟動腳本

echo "=========================================="
echo "Task Service API"
echo "=========================================="

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "建立虛擬環境..."
    python3 -m venv venv
fi

# 啟動虛擬環境
echo "啟動虛擬環境..."
source venv/bin/activate

# 安裝依賴
echo "安裝依賴套件..."
pip install -r requirements.txt

# 建立上傳資料夾
mkdir -p uploads

# 設定環境變數（如果沒有 .env 檔案）
if [ ! -f ".env" ]; then
    echo "建立 .env 檔案..."
    cat > .env << EOL
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
PORT=12345
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216
DELETE_AFTER_PROCESS=true
EOL
fi

# 啟動 Flask 應用
echo "啟動 Flask 應用..."
echo "服務將運行在 http://localhost:12345"
echo "按 Ctrl+C 停止服務"
echo "=========================================="

python app.py

