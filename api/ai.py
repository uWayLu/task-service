"""
AI 處理相關 API

端點：
- POST /api/ai/analyze-document: 分析文件並提取資訊
- POST /api/ai/mask-and-analyze: 遮罩個資後分析
- POST /api/ai/detect-sensitive: 偵測敏感資訊
"""

from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
from . import api_bp
from utils.pdf_parser import PDFParser
from utils.privacy_masker import PrivacyMasker, SmartPrivacyMasker, detect_sensitive_info
from utils.ai_integrator import AIIntegrator, AIProvider


@api_bp.route('/ai/analyze-document', methods=['POST'])
def analyze_document():
    """
    分析文件（不遮罩）
    
    Request:
        - file: PDF 檔案
        - password: PDF 密碼（選填）
        - provider: AI 服務（openai/claude，預設 openai）
        - model: 模型名稱（選填）
        - document_type: 文件類型（選填）
    
    Response:
        {
            "success": true,
            "analysis": {...},
            "metadata": {...}
        }
    """
    try:
        # 檢查檔案
        if 'file' not in request.files:
            return jsonify({'error': '未提供檔案'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未選擇檔案'}), 400
        
        # 取得參數
        password = request.form.get('password')
        provider = request.form.get('provider', 'openai')
        model = request.form.get('model')
        document_type = request.form.get('document_type', 'financial')
        
        # 儲存暫存檔案
        filename = secure_filename(file.filename)
        temp_path = f"/tmp/{filename}"
        file.save(temp_path)
        
        try:
            # 解析 PDF
            parser = PDFParser()
            result = parser.extract_text(temp_path, password)
            
            if not result['success']:
                return jsonify({
                    'error': 'PDF 解析失敗',
                    'details': result.get('error')
                }), 400
            
            # 取得文字內容
            text = result['text']
            
            # AI 分析
            provider_enum = AIProvider(provider)
            integrator = AIIntegrator(provider=provider_enum, model=model)
            ai_response = integrator.analyze_document(text, document_type)
            
            if not ai_response.success:
                return jsonify({
                    'error': 'AI 分析失敗',
                    'details': ai_response.error
                }), 500
            
            # 返回結果
            return jsonify({
                'success': True,
                'analysis': ai_response.content,
                'metadata': {
                    'provider': ai_response.provider,
                    'model': ai_response.model,
                    'pages': result['total_pages'],
                    'usage': ai_response.usage
                }
            })
            
        finally:
            # 清理暫存檔案
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/ai/mask-and-analyze', methods=['POST'])
def mask_and_analyze():
    """
    遮罩個資後分析文件
    
    Request:
        - file: PDF 檔案
        - password: PDF 密碼（選填）
        - provider: AI 服務（openai/claude，預設 openai）
        - model: 模型名稱（選填）
        - document_type: 文件類型（選填）
        - mask_types: 要遮罩的類型（逗號分隔，選填）
        - aggressive: 是否使用積極模式（選填）
    
    Response:
        {
            "success": true,
            "analysis": {...},
            "masking": {
                "masked_count": 5,
                "sensitive_items": [...]
            },
            "metadata": {...}
        }
    """
    try:
        # 檢查檔案
        if 'file' not in request.files:
            return jsonify({'error': '未提供檔案'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未選擇檔案'}), 400
        
        # 取得參數
        password = request.form.get('password')
        provider = request.form.get('provider', 'openai')
        model = request.form.get('model')
        document_type = request.form.get('document_type', 'financial')
        mask_types = request.form.get('mask_types', '').split(',') if request.form.get('mask_types') else None
        aggressive = request.form.get('aggressive', 'false').lower() == 'true'
        
        # 儲存暫存檔案
        filename = secure_filename(file.filename)
        temp_path = f"/tmp/{filename}"
        file.save(temp_path)
        
        try:
            # 解析 PDF
            parser = PDFParser()
            result = parser.extract_text(temp_path, password)
            
            if not result['success']:
                return jsonify({
                    'error': 'PDF 解析失敗',
                    'details': result.get('error')
                }), 400
            
            # 取得文字內容
            text = result['text']
            
            # 遮罩個資
            if mask_types:
                masker = PrivacyMasker(mask_types=mask_types)
            else:
                masker = SmartPrivacyMasker(aggressive=aggressive)
            
            mask_result = masker.mask(text)
            masked_text = mask_result.masked
            
            # AI 分析（使用遮罩後的文字）
            provider_enum = AIProvider(provider)
            integrator = AIIntegrator(provider=provider_enum, model=model)
            ai_response = integrator.analyze_document(masked_text, document_type)
            
            if not ai_response.success:
                return jsonify({
                    'error': 'AI 分析失敗',
                    'details': ai_response.error
                }), 500
            
            # 返回結果
            return jsonify({
                'success': True,
                'analysis': ai_response.content,
                'masking': {
                    'masked_count': mask_result.mask_count,
                    'sensitive_items': [
                        {
                            'type': item['type_name'],
                            'masked_value': item['masked']
                        }
                        for item in mask_result.sensitive_items
                    ]
                },
                'metadata': {
                    'provider': ai_response.provider,
                    'model': ai_response.model,
                    'pages': result['total_pages'],
                    'usage': ai_response.usage
                }
            })
            
        finally:
            # 清理暫存檔案
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/ai/detect-sensitive', methods=['POST'])
def detect_sensitive():
    """
    偵測敏感資訊（不進行 AI 分析）
    
    Request:
        - file: PDF 檔案
        - password: PDF 密碼（選填）
        - mask_types: 要偵測的類型（逗號分隔，選填）
    
    Response:
        {
            "success": true,
            "sensitive_count": 5,
            "sensitive_items": [
                {
                    "type": "身分證字號",
                    "masked_value": "A*********1",
                    "count": 2
                }
            ]
        }
    """
    try:
        # 檢查檔案
        if 'file' not in request.files:
            return jsonify({'error': '未提供檔案'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未選擇檔案'}), 400
        
        # 取得參數
        password = request.form.get('password')
        mask_types = request.form.get('mask_types', '').split(',') if request.form.get('mask_types') else None
        
        # 儲存暫存檔案
        filename = secure_filename(file.filename)
        temp_path = f"/tmp/{filename}"
        file.save(temp_path)
        
        try:
            # 解析 PDF
            parser = PDFParser()
            result = parser.extract_text(temp_path, password)
            
            if not result['success']:
                return jsonify({
                    'error': 'PDF 解析失敗',
                    'details': result.get('error')
                }), 400
            
            # 偵測敏感資訊
            masker = PrivacyMasker(mask_types=mask_types)
            sensitive_items = masker.detect(result['text'])
            
            # 統計
            type_counts = {}
            for item in sensitive_items:
                type_name = item['type_name']
                if type_name not in type_counts:
                    type_counts[type_name] = {
                        'type': type_name,
                        'count': 0,
                        'examples': []
                    }
                type_counts[type_name]['count'] += 1
                if len(type_counts[type_name]['examples']) < 3:
                    type_counts[type_name]['examples'].append(item['masked'])
            
            return jsonify({
                'success': True,
                'sensitive_count': len(sensitive_items),
                'sensitive_items': list(type_counts.values()),
                'metadata': {
                    'pages': result['total_pages']
                }
            })
            
        finally:
            # 清理暫存檔案
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/ai/mask-types', methods=['GET'])
def get_mask_types():
    """
    取得支援的遮罩類型
    
    Response:
        {
            "mask_types": [
                {"type": "taiwan_id", "name": "身分證字號"},
                ...
            ]
        }
    """
    masker = PrivacyMasker()
    return jsonify({
        'mask_types': masker.get_mask_types()
    })

