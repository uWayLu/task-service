#!/bin/bash
# Webhook 測試腳本

if [ $# -lt 1 ]; then
    echo "使用方式: $0 <pdf_file> [password]"
    echo ""
    echo "範例:"
    echo "  $0 statement.pdf"
    echo "  $0 statement.pdf A123456789"
    exit 1
fi

PDF_FILE="$1"
PASSWORD="${2:-}"
BASE_URL="http://localhost:12345"

echo "======================================================================"
echo "  Webhook 測試腳本"
echo "======================================================================"
echo ""
echo "📄 檔案: $PDF_FILE"
if [ -n "$PASSWORD" ]; then
    echo "🔑 密碼: $PASSWORD"
fi
echo ""

# 檢查檔案
if [ ! -f "$PDF_FILE" ]; then
    echo "❌ 錯誤: 找不到檔案 '$PDF_FILE'"
    exit 1
fi

# 檢查服務是否啟動
if ! curl -s "$BASE_URL/api/health" > /dev/null; then
    echo "❌ 錯誤: 服務未啟動"
    echo "請先執行: python app.py"
    exit 1
fi

echo "✅ 服務運行中"
echo ""

# 測試 1: 基本測試（結構化提取）
echo "======================================================================"
echo "測試 1: 結構化提取"
echo "======================================================================"
echo ""

CMD="curl -X POST $BASE_URL/api/webhook/gmail \
  -F 'file=@$PDF_FILE' \
  -F 'document_type=credit_card' \
  -F 'structured=true'"

if [ -n "$PASSWORD" ]; then
    CMD="$CMD -F 'password=$PASSWORD'"
fi

echo "執行: $CMD"
echo ""

eval $CMD | jq .

echo ""
echo ""

# 測試 2: 加入個資遮罩
echo "======================================================================"
echo "測試 2: 結構化提取 + 個資遮罩"
echo "======================================================================"
echo ""

CMD="curl -X POST $BASE_URL/api/webhook/gmail \
  -F 'file=@$PDF_FILE' \
  -F 'document_type=credit_card' \
  -F 'structured=true' \
  -F 'mask_privacy=true'"

if [ -n "$PASSWORD" ]; then
    CMD="$CMD -F 'password=$PASSWORD'"
fi

echo "執行: $CMD"
echo ""

eval $CMD | jq .

echo ""
echo ""

# 測試 3: 傳統方法（不使用結構化）
echo "======================================================================"
echo "測試 3: 傳統處理方法"
echo "======================================================================"
echo ""

CMD="curl -X POST $BASE_URL/api/webhook/gmail \
  -F 'file=@$PDF_FILE' \
  -F 'document_type=credit_card' \
  -F 'structured=false'"

if [ -n "$PASSWORD" ]; then
    CMD="$CMD -F 'password=$PASSWORD'"
fi

echo "執行: $CMD"
echo ""

eval $CMD | jq .

echo ""
echo ""
echo "======================================================================"
echo "✅ 測試完成"
echo "======================================================================"
echo ""
echo "💡 提示："
echo "  - 查看完整回應: 使用上面的 curl 指令"
echo "  - 儲存結果: curl ... > result.json"
echo "  - 驗證 Schema: cat result.json | jq '.validation'"
echo "  - 查看交易: cat result.json | jq '.data.transactions'"


