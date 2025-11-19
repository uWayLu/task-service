"""
文件管理相關 API
"""
from flask import jsonify
from . import api_bp


@api_bp.route('/documents/types', methods=['GET'])
def get_document_types():
    """
    取得支援的文件類型列表
    
    Returns:
        JSON: 文件類型清單
    """
    document_types = {
        'bank_statement': {
            'name': '銀行對帳單',
            'description': '銀行定期提供的帳戶交易明細',
            'extracted_fields': [
                'account_number',
                'opening_balance',
                'closing_balance',
                'transactions'
            ]
        },
        'credit_card': {
            'name': '信用卡帳單',
            'description': '信用卡的每月消費帳單',
            'extracted_fields': [
                'card_number',
                'due_date',
                'total_amount_due',
                'minimum_payment',
                'transactions'
            ]
        },
        'transaction_notice': {
            'name': '交易通知',
            'description': '單筆交易的即時通知',
            'extracted_fields': [
                'transaction_date',
                'merchant',
                'amount',
                'transaction_type'
            ]
        }
    }
    
    return jsonify({
        'status': 'success',
        'data': document_types
    })


@api_bp.route('/documents/stats', methods=['GET'])
def get_document_stats():
    """
    取得文件處理統計（範例）
    實際使用需要資料庫支援
    
    Returns:
        JSON: 統計資訊
    """
    # 這裡是範例資料，實際應從資料庫取得
    stats = {
        'total_processed': 0,
        'by_type': {
            'bank_statement': 0,
            'credit_card': 0,
            'transaction_notice': 0
        },
        'last_24h': 0
    }
    
    return jsonify({
        'status': 'success',
        'data': stats,
        'note': '需要資料庫支援才能顯示實際統計'
    })

