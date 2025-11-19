"""
文件處理器
根據文件類型（對帳單、信用卡帳單、消費通知）進行不同處理
"""
from typing import Dict, Any, List
import re
from datetime import datetime
from .pdf_parser import PDFParser


class DocumentProcessor:
    """文件處理器"""
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        
    def process_document(self, document_type: str, content: Dict[str, Any], 
                        metadata: Dict[str, str]) -> Dict[str, Any]:
        """
        根據文件類型處理文件
        
        Args:
            document_type: 文件類型
            content: PDF 解析後的內容
            metadata: 郵件元資料
            
        Returns:
            處理結果摘要
        """
        # 根據文件類型選擇處理方法
        processors = {
            'bank_statement': self._process_bank_statement,
            'credit_card': self._process_credit_card,
            'transaction_notice': self._process_transaction_notice,
            'unknown': self._process_unknown
        }
        
        processor = processors.get(document_type, self._process_unknown)
        return processor(content, metadata)
    
    def _process_bank_statement(self, content: Dict[str, Any], 
                                metadata: Dict[str, str]) -> Dict[str, Any]:
        """
        處理銀行對帳單
        提取帳戶餘額、交易記錄等資訊
        """
        text = content.get('text', '')
        
        # 提取金額資訊
        amounts = PDFParser.extract_amounts(text)
        
        # 提取日期資訊
        dates = PDFParser.extract_dates(text)
        
        # 提取帳號資訊
        account_number = self._extract_account_number(text)
        
        # 提取期初/期末餘額
        balances = self._extract_balances(text)
        
        # 提取交易記錄
        transactions = self._extract_transactions(text)
        
        return {
            'document_type': 'bank_statement',
            'summary': {
                'account_number': account_number,
                'statement_period': {
                    'dates': dates[:2] if len(dates) >= 2 else dates,
                },
                'opening_balance': balances.get('opening_balance'),
                'closing_balance': balances.get('closing_balance'),
                'total_deposits': balances.get('total_deposits'),
                'total_withdrawals': balances.get('total_withdrawals'),
                'transaction_count': len(transactions),
            },
            'transactions': transactions[:10],  # 只返回前 10 筆交易作為摘要
            'all_amounts': amounts.get('all_amounts', []),
            'metadata': metadata,
            'total_pages': content.get('total_pages', 0),
            'processed_at': datetime.now().isoformat()
        }
    
    def _process_credit_card(self, content: Dict[str, Any], 
                            metadata: Dict[str, str]) -> Dict[str, Any]:
        """
        處理信用卡帳單
        提取應繳金額、到期日、消費明細等資訊
        """
        text = content.get('text', '')
        
        # 提取應繳金額
        payment_info = self._extract_payment_info(text)
        
        # 提取繳款截止日
        due_date = self._extract_due_date(text)
        
        # 提取卡號
        card_number = self._extract_card_number(text)
        
        # 提取消費明細
        transactions = self._extract_credit_transactions(text)
        
        # 提取帳單週期
        billing_period = self._extract_billing_period(text)
        
        return {
            'document_type': 'credit_card',
            'summary': {
                'card_number': card_number,
                'billing_period': billing_period,
                'due_date': due_date,
                'minimum_payment': payment_info.get('minimum_payment'),
                'total_amount_due': payment_info.get('total_amount_due'),
                'previous_balance': payment_info.get('previous_balance'),
                'new_charges': payment_info.get('new_charges'),
                'transaction_count': len(transactions),
            },
            'transactions': transactions[:10],  # 只返回前 10 筆交易作為摘要
            'metadata': metadata,
            'total_pages': content.get('total_pages', 0),
            'processed_at': datetime.now().isoformat()
        }
    
    def _process_transaction_notice(self, content: Dict[str, Any], 
                                   metadata: Dict[str, str]) -> Dict[str, Any]:
        """
        處理交易通知
        提取單筆交易資訊
        """
        text = content.get('text', '')
        
        # 提取交易金額
        amounts = PDFParser.extract_amounts(text)
        
        # 提取交易日期
        dates = PDFParser.extract_dates(text)
        
        # 提取商家資訊
        merchant = self._extract_merchant_info(text)
        
        # 提取交易類型
        transaction_type = self._extract_transaction_type(text)
        
        return {
            'document_type': 'transaction_notice',
            'summary': {
                'transaction_date': dates[0] if dates else None,
                'merchant': merchant,
                'transaction_type': transaction_type,
                'amount': amounts.get('all_amounts', [None])[0],
                'all_amounts': amounts.get('all_amounts', []),
            },
            'metadata': metadata,
            'total_pages': content.get('total_pages', 0),
            'processed_at': datetime.now().isoformat()
        }
    
    def _process_unknown(self, content: Dict[str, Any], 
                        metadata: Dict[str, str]) -> Dict[str, Any]:
        """
        處理未知類型文件
        提取基本資訊
        """
        text = content.get('text', '')
        
        # 提取所有數字和日期
        amounts = PDFParser.extract_amounts(text)
        dates = PDFParser.extract_dates(text)
        
        return {
            'document_type': 'unknown',
            'summary': {
                'text_preview': text[:500] + '...' if len(text) > 500 else text,
                'dates_found': dates,
                'amounts_found': amounts.get('all_amounts', []),
            },
            'metadata': metadata,
            'total_pages': content.get('total_pages', 0),
            'processed_at': datetime.now().isoformat()
        }
    
    # ===== 輔助方法 =====
    
    @staticmethod
    def _extract_account_number(text: str) -> str:
        """提取帳號"""
        patterns = [
            r'帳號[:：\s]*(\d{10,})',
            r'Account(?:\s+Number)?[:：\s]*(\d{10,})',
            r'戶號[:：\s]*(\d{10,})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def _extract_card_number(text: str) -> str:
        """提取卡號（遮罩後的）"""
        patterns = [
            r'卡號[:：\s]*([\d*-]+)',
            r'Card(?:\s+Number)?[:：\s]*([\d*-]+)',
            r'\d{4}[-\s*]+\d{4}[-\s*]+\d{4}[-\s*]+\d{4}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if match.lastindex else match.group(0)
        return None
    
    @staticmethod
    def _extract_balances(text: str) -> Dict[str, float]:
        """提取期初/期末餘額"""
        balances = {}
        
        # 期初餘額
        opening_patterns = [
            r'期初餘額[:：\s]*[\$]?([\d,]+\.?\d*)',
            r'Opening Balance[:：\s]*[\$]?([\d,]+\.?\d*)',
        ]
        
        # 期末餘額
        closing_patterns = [
            r'期末餘額[:：\s]*[\$]?([\d,]+\.?\d*)',
            r'Closing Balance[:：\s]*[\$]?([\d,]+\.?\d*)',
            r'結餘[:：\s]*[\$]?([\d,]+\.?\d*)',
        ]
        
        for pattern in opening_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    balances['opening_balance'] = float(match.group(1).replace(',', ''))
                    break
                except ValueError:
                    pass
        
        for pattern in closing_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    balances['closing_balance'] = float(match.group(1).replace(',', ''))
                    break
                except ValueError:
                    pass
        
        return balances
    
    @staticmethod
    def _extract_transactions(text: str) -> List[Dict[str, Any]]:
        """提取交易記錄（簡化版）"""
        # 這裡只做簡單的行解析，實際情況可能需要更複雜的邏輯
        transactions = []
        lines = text.split('\n')
        
        for line in lines:
            # 嘗試找出包含日期和金額的行
            dates = PDFParser.extract_dates(line)
            amounts = PDFParser.extract_numbers(line)
            
            if dates and amounts:
                transactions.append({
                    'date': dates[0],
                    'amount': amounts[0] if amounts else None,
                    'description': line.strip()
                })
        
        return transactions
    
    @staticmethod
    def _extract_credit_transactions(text: str) -> List[Dict[str, Any]]:
        """提取信用卡交易記錄（簡化版）"""
        return DocumentProcessor._extract_transactions(text)
    
    @staticmethod
    def _extract_payment_info(text: str) -> Dict[str, float]:
        """提取繳款資訊"""
        payment_info = {}
        
        patterns = {
            'minimum_payment': [
                r'最低應繳金額[:：\s]*[\$]?([\d,]+\.?\d*)',
                r'Minimum Payment[:：\s]*[\$]?([\d,]+\.?\d*)',
            ],
            'total_amount_due': [
                r'本期應繳總額[:：\s]*[\$]?([\d,]+\.?\d*)',
                r'Total Amount Due[:：\s]*[\$]?([\d,]+\.?\d*)',
                r'應繳金額[:：\s]*[\$]?([\d,]+\.?\d*)',
            ],
            'new_charges': [
                r'本期新增消費[:：\s]*[\$]?([\d,]+\.?\d*)',
                r'New Charges[:：\s]*[\$]?([\d,]+\.?\d*)',
            ]
        }
        
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        payment_info[key] = float(match.group(1).replace(',', ''))
                        break
                    except ValueError:
                        pass
        
        return payment_info
    
    @staticmethod
    def _extract_due_date(text: str) -> str:
        """提取繳款截止日"""
        patterns = [
            r'繳款截止日[:：\s]*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)',
            r'Due Date[:：\s]*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'到期日[:：\s]*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def _extract_billing_period(text: str) -> Dict[str, str]:
        """提取帳單週期"""
        period = {}
        
        pattern = r'帳單週期[:：\s]*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)\s*[至~-]\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)'
        match = re.search(pattern, text)
        
        if match:
            period['start_date'] = match.group(1)
            period['end_date'] = match.group(2)
        
        return period
    
    @staticmethod
    def _extract_merchant_info(text: str) -> str:
        """提取商家資訊"""
        # 尋找常見的商家資訊模式
        patterns = [
            r'商家[:：\s]*([^\n]+)',
            r'Merchant[:：\s]*([^\n]+)',
            r'消費地點[:：\s]*([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def _extract_transaction_type(text: str) -> str:
        """提取交易類型"""
        transaction_types = {
            '消費': ['消費', 'Purchase', 'Debit'],
            '退款': ['退款', 'Refund', 'Credit'],
            '轉帳': ['轉帳', 'Transfer'],
            '提款': ['提款', 'Withdrawal', 'ATM'],
        }
        
        text_lower = text.lower()
        for trans_type, keywords in transaction_types.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return trans_type
        
        return '其他'

