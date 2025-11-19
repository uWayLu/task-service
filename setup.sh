#!/bin/bash
# 專案環境設定腳本

echo "🚀 Task Service 環境設定"
echo "================================"

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 Python3"
    exit 1
fi

echo "✅ Python: $(python3 --version)"

# 建立虛擬環境（如果不存在）
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 建立虛擬環境..."
    python3 -m venv venv
    echo "✅ 虛擬環境已建立"
fi

# 啟動虛擬環境
echo ""
echo "🔧 安裝依賴套件..."
source venv/bin/activate

# 升級 pip
pip install --upgrade pip

# 安裝套件
pip install -r requirements.txt

echo ""
echo "================================"
echo "✅ 環境設定完成！"
echo ""
echo "接下來："
echo "  1. 啟動虛擬環境: source venv/bin/activate"
echo "  2. 檢查環境: python test_env.py"
echo "  3. 測試 PDF: python test_pdf_parser.py your-file.pdf"
echo "  4. 啟動服務: python app.py"

