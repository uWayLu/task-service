"""
健康檢查相關 API
"""
from flask import jsonify
from . import api_bp


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康檢查端點
    
    Returns:
        JSON: 服務狀態資訊
    """
    return jsonify({
        'status': 'healthy',
        'service': 'task-service',
        'version': '1.0.0'
    })


@api_bp.route('/ping', methods=['GET'])
def ping():
    """
    簡單的 ping 端點
    
    Returns:
        JSON: pong 回應
    """
    return jsonify({'message': 'pong'})

