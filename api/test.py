"""
測試用 API
提供 PDF 解析測試的 HTTP 介面
"""
import os
from flask import jsonify, request, current_app
from werkzeug.utils import secure_filename
from . import api_bp
from utils.pdf_parser import PDFParser
from utils.document_processor import DocumentProcessor


@api_bp.route('/test/parse-pdf', methods=['POST'])
def test_parse_pdf():
    """
    測試 PDF 解析功能
    
    Form Data:
        file: PDF 檔案
        
    Returns:
        JSON: 完整的解析結果（包含文字、元資料、提取的資訊）
    """
    try:
        # 檢查檔案
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': '未提供 PDF 檔案'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': '檔案名稱為空'
            }), 400
        
        # 獲取密碼（如果有）
        pdf_password = request.form.get('password', '')
        
        # 儲存檔案
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # 解析 PDF
        parser = PDFParser()
        try:
            result = parser.extract_text(filepath, pdf_password or None)
        except PermissionError as e:
            # 清理檔案
            os.remove(filepath)
            
            return jsonify({
                'status': 'error',
                'message': str(e),
                'error_code': 'PDF_ENCRYPTED',
                'hint': '這個 PDF 有密碼保護。請在 password 參數中提供密碼。'
            }), 403
        
        # 提取額外資訊
        text = result['text']
        numbers = parser.extract_numbers(text)
        dates = parser.extract_dates(text)
        amounts = parser.extract_amounts(text)
        
        # 刪除檔案
        os.remove(filepath)
        
        # 返回結果
        return jsonify({
            'status': 'success',
            'message': '解析完成',
            'data': {
                'filename': filename,
                'total_pages': result['total_pages'],
                'text_length': len(text),
                'text_preview': text[:500] + '...' if len(text) > 500 else text,
                'full_text': text,  # 完整文字
                'metadata': result['metadata'],
                'extracted': {
                    'numbers': numbers[:20],  # 前 20 個數字
                    'dates': dates[:20],      # 前 20 個日期
                    'amounts': {
                        'all': amounts['all_amounts'][:20],
                        'totals': amounts['totals'],
                        'balances': amounts['balances']
                    }
                },
                'pages': [
                    {
                        'page_number': p['page_number'],
                        'text_length': len(p['text']),
                        'size': f"{p['width']:.1f}x{p['height']:.1f}"
                    }
                    for p in result['pages']
                ]
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'解析 PDF 時發生錯誤: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': f'解析失敗: {str(e)}'
        }), 500


@api_bp.route('/test/process-document', methods=['POST'])
def test_process_document():
    """
    測試完整文件處理流程
    
    Form Data:
        file: PDF 檔案
        document_type: 文件類型 (選填，預設 unknown)
        
    Returns:
        JSON: 處理結果（包含摘要、交易記錄等）
    """
    try:
        # 檢查檔案
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': '未提供 PDF 檔案'
            }), 400
        
        file = request.files['file']
        document_type = request.form.get('document_type', 'unknown')
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': '檔案名稱為空'
            }), 400
        
        # 獲取密碼（如果有）
        pdf_password = request.form.get('password', '')
        
        # 儲存檔案
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # 解析 PDF
        parser = PDFParser()
        try:
            pdf_content = parser.extract_text(filepath, pdf_password or None)
        except PermissionError as e:
            # 清理檔案
            os.remove(filepath)
            
            return jsonify({
                'status': 'error',
                'message': str(e),
                'error_code': 'PDF_ENCRYPTED',
                'hint': '這個 PDF 有密碼保護。請在 password 參數中提供密碼。'
            }), 403
        
        # 處理文件
        processor = DocumentProcessor()
        result = processor.process_document(
            document_type=document_type,
            content=pdf_content,
            metadata={
                'filename': filename,
                'test_mode': True
            }
        )
        
        # 刪除檔案
        os.remove(filepath)
        
        # 返回結果
        return jsonify({
            'status': 'success',
            'message': '處理完成',
            'data': result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'處理文件時發生錯誤: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': f'處理失敗: {str(e)}'
        }), 500

