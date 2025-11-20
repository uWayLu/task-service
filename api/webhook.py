"""
Webhook 相關 API
處理來自 Gmail Apps Script 的請求
"""
import os
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from . import api_bp
from utils.pdf_parser import PDFParser
from utils.document_processor import DocumentProcessor
from utils.privacy_masker import PrivacyMasker


def allowed_file(filename):
    """檢查檔案類型是否允許"""
    ALLOWED_EXTENSIONS = {'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api_bp.route('/webhook/gmail', methods=['POST'])
def gmail_webhook():
    """
    接收 Gmail Apps Script webhook
    處理財務相關 PDF 文件
    
    Form Data:
        file: PDF 檔案
        document_type: 文件類型 ('bank_statement', 'credit_card', 'transaction_notice')
        sender: 寄件者信箱 (選填)
        subject: 郵件主旨 (選填)
        date: 郵件日期 (選填)
    
    Returns:
        JSON: 處理結果摘要
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
        pdf_password = request.form.get('password', '')  # PDF 密碼（選填）
        mask_privacy = request.form.get('mask_privacy', 'false').lower() == 'true'  # 是否遮罩個資
        
        # 儲存檔案
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # 解析 PDF
        pdf_parser = PDFParser()
        try:
            pdf_content = pdf_parser.extract_text(filepath, pdf_password or None)
        except PermissionError as e:
            # 清理檔案
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({
                'status': 'error',
                'message': str(e),
                'error_code': 'PDF_ENCRYPTED',
                'hint': '請在 password 參數中提供 PDF 密碼'
            }), 403
        
        # 遮罩個資（如果需要）
        mask_info = None
        if mask_privacy:
            masker = PrivacyMasker()
            mask_result = masker.mask(pdf_content['text'])
            pdf_content['text'] = mask_result.masked
            mask_info = {
                'masked_count': mask_result.mask_count,
                'sensitive_types': list(set(item['type_name'] for item in mask_result.sensitive_items))
            }
        
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
        
        # 加入遮罩資訊
        if mask_info:
            result['privacy_masking'] = mask_info
        
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
        current_app.logger.error(f'處理請求時發生錯誤: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': f'處理失敗: {str(e)}'
        }), 500


@api_bp.route('/webhook/test', methods=['POST'])
def test_webhook():
    """
    測試用 webhook 端點
    不處理檔案，只返回收到的參數
    
    Returns:
        JSON: 收到的參數
    """
    return jsonify({
        'status': 'success',
        'message': '測試端點',
        'received_data': {
            'form': dict(request.form),
            'files': [f for f in request.files.keys()],
            'headers': dict(request.headers)
        }
    })

