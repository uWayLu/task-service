#!/bin/bash
# PDF 密碼測試腳本

echo "================================================"
echo "PDF 密碼保護測試腳本"
echo "================================================"
echo ""

# 檢查是否提供 PDF 檔案
if [ -z "$1" ]; then
    echo "❌ 錯誤: 請提供 PDF 檔案路徑"
    echo ""
    echo "使用方式:"
    echo "  $0 <pdf_file> [password]"
    echo ""
    echo "範例:"
    echo "  $0 test_files/encrypted.pdf"
    echo "  $0 test_files/encrypted.pdf A123456789"
    exit 1
fi

PDF_FILE="$1"
PASSWORD="${2:-}"

# 檢查檔案是否存在
if [ ! -f "$PDF_FILE" ]; then
    echo "❌ 錯誤: 找不到檔案 '$PDF_FILE'"
    exit 1
fi

echo "📄 測試檔案: $PDF_FILE"
echo ""

# 測試 1: 無密碼測試（檢查是否加密）
echo "🔍 測試 1: 檢查 PDF 是否加密"
echo "----------------------------------------"

if [ -n "$PASSWORD" ]; then
    echo "   使用密碼: $PASSWORD"
    python test_pdf_parser.py "$PDF_FILE" --password "$PASSWORD"
    TEST1_RESULT=$?
else
    echo "   不提供密碼"
    python test_pdf_parser.py "$PDF_FILE"
    TEST1_RESULT=$?
fi

echo ""

# 測試 2: HTTP API 測試
if [ $TEST1_RESULT -eq 0 ]; then
    echo "✅ Console 測試成功"
    echo ""
    echo "🌐 測試 2: HTTP API 測試"
    echo "----------------------------------------"
    echo "   啟動服務並測試 API..."
    
    # 檢查服務是否運行
    if curl -s http://localhost:12345/api/health > /dev/null 2>&1; then
        echo "   ✓ 服務已運行"
        
        if [ -n "$PASSWORD" ]; then
            echo "   發送帶密碼的請求..."
            curl -X POST http://localhost:12345/api/test/parse-pdf \
                -F "file=@$PDF_FILE" \
                -F "password=$PASSWORD" \
                2>/dev/null | python -m json.tool
        else
            echo "   發送不帶密碼的請求..."
            curl -X POST http://localhost:12345/api/test/parse-pdf \
                -F "file=@$PDF_FILE" \
                2>/dev/null | python -m json.tool
        fi
    else
        echo "   ⚠️  服務未運行，跳過 HTTP 測試"
        echo "   提示: 執行 'python app.py' 啟動服務"
    fi
else
    echo "❌ Console 測試失敗"
    
    if [ -z "$PASSWORD" ]; then
        echo ""
        echo "💡 這個 PDF 可能有密碼保護"
        echo "   請提供密碼重試:"
        echo "   $0 $PDF_FILE <your_password>"
    fi
fi

echo ""
echo "================================================"
echo "測試完成"
echo "================================================"

