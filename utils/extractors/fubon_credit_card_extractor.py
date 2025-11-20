"""
富邦信用卡帳單提取器

針對富邦銀行信用卡帳單格式進行規則提取
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_extractor import BaseExtractor


class FubonCreditCardExtractor(BaseExtractor):
    """富邦信用卡帳單提取器"""
    
    def __init__(self):
        super().__init__()
        self.extraction_method = "rule_based"
        self.confidence = 0.0
    
    def can_extract(self, text: str) -> bool:
        """判斷是否為富邦信用卡帳單"""
        indicators = [
            '台北富邦',
            '富邦',
            '本期應繳總額',
            '繳款截止日',
            '循環信用利率'
        ]
        
        matches = sum(1 for indicator in indicators if indicator in text)
        can = matches >= 3
        
        if can:
            self.confidence = min(0.95, 0.6 + (matches * 0.1))
        
        return can
    
    def get_schema_path(self) -> str:
        """取得 Schema 路徑"""
        return "schemas/credit_card_schema.json"
    
    def extract(self, text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """提取富邦信用卡帳單資訊"""
        
        result = {
            "document_type": "credit_card",
            "bank_name": "台北富邦銀行",
            "statement_period": self._extract_statement_period(text),
            "payment_info": self._extract_payment_info(text),
            "card_info": self._extract_card_info(text),
            "interest_info": self._extract_interest_info(text),
            "transactions": self._extract_transactions(text),
            "summary": {}
        }
        
        # 計算統計摘要
        result["summary"] = self._calculate_summary(result["transactions"])
        
        # 加入元資料
        if metadata:
            result = self.add_metadata(
                result,
                source_file=metadata.get('filename'),
                total_pages=metadata.get('total_pages')
            )
        
        return result
    
    def _extract_statement_period(self, text: str) -> Dict:
        """提取帳單期間"""
        period = {}
        
        # 提取帳單年月：113/08
        match = re.search(r'帳單年月[^\d]*(\d{2,3})/(\d{1,2})', text)
        if match:
            year_roc = int(match.group(1))  # 民國年
            month = int(match.group(2))
            year_ad = year_roc + 1911  # 轉西元
            
            period['year'] = year_ad
            period['month'] = month
        
        # 提取結帳日：113/08/24
        match = re.search(r'帳單結帳日[^\d]*(\d{2,3})/(\d{1,2})/(\d{1,2})', text)
        if match:
            year_roc = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            year_ad = year_roc + 1911
            
            period['statement_date'] = f"{year_ad:04d}-{month:02d}-{day:02d}"
        
        return period
    
    def _extract_payment_info(self, text: str) -> Dict:
        """提取繳款資訊"""
        payment = {}
        
        # 本期應繳總額：7,483元
        match = re.search(r'本期應繳總額[^\d]*?([\d,]+)元?', text)
        if match:
            payment['total_amount_due'] = float(match.group(1).replace(',', ''))
        
        # 最低應繳金額
        match = re.search(r'最低應繳金額[^\d]*?([\d,]+)', text)
        if match:
            payment['minimum_payment'] = float(match.group(1).replace(',', ''))
        
        # 前期應繳總額
        match = re.search(r'前期應繳總額[^\d]*?([\d,]+)', text)
        if match:
            payment['previous_balance'] = float(match.group(1).replace(',', ''))
        
        # 繳款截止日：113/09/09
        match = re.search(r'繳款截止日[^\d]*(\d{2,3})/(\d{1,2})/(\d{1,2})', text)
        if match:
            year_roc = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            year_ad = year_roc + 1911
            
            payment['due_date'] = f"{year_ad:04d}-{month:02d}-{day:02d}"
        
        # 自動扣繳資訊
        auto_debit_match = re.search(r'自動轉帳.*?扣繳帳號[:：](\d+[\*]+\d+)', text)
        if auto_debit_match:
            payment['auto_debit'] = {
                'enabled': True,
                'account_number': auto_debit_match.group(1),
                'amount_type': 'total'  # 預設全額
            }
            
            if '本期應繳總額' in text:
                payment['auto_debit']['amount_type'] = 'total'
        
        # 本期新增
        match = re.search(r'本期新增[^\d]*?[\+\-]?\s*([\d,]+)', text)
        if match:
            payment['new_charges'] = float(match.group(1).replace(',', ''))
        
        return payment
    
    def _extract_card_info(self, text: str) -> Dict:
        """提取信用卡資訊"""
        card = {}
        
        # 卡片類型與末4碼：JCB晶緻正卡末４碼6317
        match = re.search(r'([\w\s]+卡)末[４4]碼(\d{4})', text)
        if match:
            card['card_type'] = match.group(1).strip()
            card['card_last4'] = match.group(2)
        
        # 信用額度
        match = re.search(r'信用額度[^\d]*?([\d,]+)', text)
        if match:
            card['credit_limit'] = float(match.group(1).replace(',', ''))
        
        # 預借現金額度
        match = re.search(r'(?:國內)?預借現金額度[^\d]*?([\d,]+)', text)
        if match:
            card['cash_advance_limit'] = float(match.group(1).replace(',', ''))
        
        return card
    
    def _extract_interest_info(self, text: str) -> Dict:
        """提取利率資訊"""
        interest = {}
        
        # 循環信用利率：8.62%
        match = re.search(r'循環信用(?:年)?利率[^\d]*([\d.]+)%', text)
        if match:
            interest['revolving_apr'] = float(match.group(1))
        
        # 帳單分期利率：5.62%
        match = re.search(r'帳單分期(?:年)?利率[^\d]*([\d.]+)%', text)
        if match:
            interest['installment_apr'] = float(match.group(1))
        
        # 年度累計利息/費用：6/468
        match = re.search(r'年度累計利息[/／]費用[^\d]*([\d,]+)[/／]([\d,]+)', text)
        if match:
            interest['annual_interest_fee'] = float(match.group(1).replace(',', ''))
        
        return interest
    
    def _extract_transactions(self, text: str) -> List[Dict]:
        """提取交易明細"""
        transactions = []
        
        # 尋找交易記錄區塊
        lines = text.split('\n')
        
        in_transaction_section = False
        
        for line in lines:
            # 判斷是否進入交易區
            if '消費日期' in line and '消費說明' in line:
                in_transaction_section = True
                continue
            
            # 判斷是否離開交易區
            if in_transaction_section and ('第' in line and '頁' in line or '本期應繳金額' in line):
                in_transaction_section = False
            
            if not in_transaction_section:
                continue
            
            # 解析交易記錄
            # 格式：113/08/10 GOOGLE PLAY APP 100001 113/08/16 1130814/ JPY 1000.00/ JPN 221
            # 或：112/07/19 環台聯合企業有限公司 (14/24期) 113/08/24 TWD 3,908
            
            # 日期格式
            date_pattern = r'(\d{2,3})/(\d{1,2})/(\d{1,2})'
            
            if re.search(date_pattern, line):
                transaction = self._parse_transaction_line(line)
                if transaction:
                    transactions.append(transaction)
        
        return transactions
    
    def _parse_transaction_line(self, line: str) -> Optional[Dict]:
        """解析單筆交易"""
        try:
            # 提取消費日期
            match = re.search(r'^(\d{2,3})/(\d{1,2})/(\d{1,2})', line)
            if not match:
                return None
            
            year_roc = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            year_ad = year_roc + 1911
            
            transaction = {
                'transaction_date': f"{year_ad:04d}-{month:02d}-{day:02d}"
            }
            
            # 提取入帳日期（第二個日期）
            dates = re.findall(r'(\d{2,3})/(\d{1,2})/(\d{1,2})', line)
            if len(dates) >= 2:
                year_roc2 = int(dates[1][0])
                month2 = int(dates[1][1])
                day2 = int(dates[1][2])
                year_ad2 = year_roc2 + 1911
                transaction['post_date'] = f"{year_ad2:04d}-{month2:02d}-{day2:02d}"
            
            # 提取金額（最後的數字）
            amount_match = re.search(r'([\d,]+)$', line.strip())
            if amount_match:
                amount = float(amount_match.group(1).replace(',', ''))
                
                # 判斷是收入還是支出
                if '繳款' in line or '扣繳' in line:
                    amount = -amount  # 繳款為負數
                
                transaction['amount'] = amount
            else:
                return None
            
            # 提取描述（在第一個日期和最後日期之間的文字）
            parts = re.split(r'\d{2,3}/\d{1,2}/\d{1,2}', line)
            if len(parts) >= 2:
                description = parts[1].strip()
                # 移除金額相關的尾部
                description = re.sub(r'\s+[\d,]+$', '', description)
                description = re.sub(r'TWD|JPY|USD|EUR', '', description).strip()
                transaction['description'] = description
                transaction['merchant'] = description.split()[0] if description else ''
            
            # 提取幣別
            currency_match = re.search(r'(TWD|JPY|USD|EUR|CNY)', line)
            if currency_match:
                transaction['currency'] = currency_match.group(1)
                
                # 提取外幣金額
                foreign_amount_match = re.search(r'([\d,]+\.\d+)/', line)
                if foreign_amount_match:
                    transaction['foreign_amount'] = float(foreign_amount_match.group(1).replace(',', ''))
            else:
                transaction['currency'] = 'TWD'
            
            # 判斷交易類型
            if '繳款' in line or '扣繳' in line:
                transaction['transaction_type'] = 'payment'
            elif '分期' in line:
                transaction['transaction_type'] = 'installment'
                
                # 提取分期資訊
                installment_match = re.search(r'\((\d+)/(\d+)期\)', line)
                if installment_match:
                    transaction['installment_info'] = {
                        'current_period': int(installment_match.group(1)),
                        'total_periods': int(installment_match.group(2))
                    }
                    
                    # 提取尚未到期金額
                    remaining_match = re.search(r'尚有未到期金額NT\$\s*([\d,]+)', line)
                    if remaining_match:
                        transaction['installment_info']['remaining_amount'] = float(
                            remaining_match.group(1).replace(',', '')
                        )
            elif '服務費' in line or '手續費' in line:
                transaction['transaction_type'] = 'fee'
            else:
                transaction['transaction_type'] = 'purchase'
            
            return transaction
        
        except Exception as e:
            # 解析失敗就跳過
            return None
    
    def _calculate_summary(self, transactions: List[Dict]) -> Dict:
        """計算統計摘要"""
        summary = {
            'total_transactions': len(transactions),
            'total_purchases': 0.0,
            'total_payments': 0.0,
            'total_fees': 0.0,
            'categories': {}
        }
        
        for txn in transactions:
            amount = txn.get('amount', 0)
            txn_type = txn.get('transaction_type', 'purchase')
            
            if txn_type == 'purchase':
                summary['total_purchases'] += amount
            elif txn_type == 'payment':
                summary['total_payments'] += abs(amount)
            elif txn_type == 'fee':
                summary['total_fees'] += amount
            
            # 簡單的分類（可以更精細）
            merchant = txn.get('merchant', 'other')
            if merchant not in summary['categories']:
                summary['categories'][merchant] = 0
            summary['categories'][merchant] += amount
        
        return summary

