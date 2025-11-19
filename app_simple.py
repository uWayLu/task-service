"""
Task Service API - Gmail Webhook 財務文件處理服務
接收來自 Gmail Apps Script 的 webhook，處理財務相關 PDF 文件
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from utils.pdf_parser import PDFParser
from utils.document_processor import DocumentProcessor

# 載入環境變數
load_dotenv()

# 初始化 Flask 應用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', './uploads')

# 啟用 CORS
CORS(app)

# 確保上傳資料夾存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 允許的檔案類型
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """檢查檔案類型是否允許"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def index():
    """健康檢查端點"""
    return jsonify({
        'status': 'success',
        'message': 'Task Service API is running',
        'version': '1.0.0'
    })


@app.route('/api/webhook/gmail', methods=['POST'])
def gmail_webhook():
    """
    接收 Gmail Apps Script webhook
    處理財務相關 PDF 文件
    
    Expected payload:
    - file: PDF 檔案
    - document_type: 文件類型 ('bank_statement', 'credit_card', 'transaction_notice')
    - sender: 寄件者信箱
    - subject: 郵件主旨
    - date: 郵件日期
    """
    try:
        # 檢查是否有檔案
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': '未提供 PDF 檔案'
            }), 400
        
        file = request.files['file']
        
        # 檢查檔案名稱
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': '檔案名稱為空'
            }), 400
        
        # 檢查檔案類型
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': '只接受 PDF 檔案'
            }), 400
        
        # 獲取表單參數
        document_type = request.form.get('document_type', 'unknown')
        sender = request.form.get('sender', '')
        subject = request.form.get('subject', '')
        email_date = request.form.get('date', '')
        
        # 儲存檔案
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 解析 PDF
        pdf_parser = PDFParser()
        pdf_content = pdf_parser.extract_text(filepath)
        
        # 處理文件
        processor = DocumentProcessor()
        result = processor.process_document(
            document_type=document_type,
            content=pdf_content,
            metadata={
                'sender': sender,
                'subject': subject,
                'date': email_date,
                'filename': filename
            }
        )
        
        # 刪除已處理的檔案（可選）
        if os.getenv('DELETE_AFTER_PROCESS', 'true').lower() == 'true':
            os.remove(filepath)
        
        # 返回處理結果
        return jsonify({
            'status': 'success',
            'message': '文件處理完成',
            'data': result
        }), 200
        
    except Exception as e:
        app.logger.error(f'處理請求時發生錯誤: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': f'處理失敗: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'service': 'task-service',
        'upload_folder': app.config['UPLOAD_FOLDER']
    })


@app.errorhandler(413)
def too_large(e):
    """檔案過大錯誤處理"""
    return jsonify({
        'status': 'error',
        'message': '檔案大小超過限制（最大 16MB）'
    }), 413


@app.errorhandler(500)
def internal_error(e):
    """內部錯誤處理"""
    return jsonify({
        'status': 'error',
        'message': '伺服器內部錯誤'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)

