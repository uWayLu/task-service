"""
個資遮罩工具

功能：
1. 自動偵測敏感資訊
2. 遮罩個人資料
3. 支援台灣常見個資格式
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MaskResult:
    """遮罩結果"""
    original: str
    masked: str
    sensitive_items: List[Dict[str, str]]
    mask_count: int


class PrivacyMasker:
    """個資遮罩器"""
    
    # 個資類型與正則表達式
    PATTERNS = {
        'taiwan_id': {
            'pattern': r'[A-Z][12]\d{8}',
            'name': '身分證字號',
            'mask': lambda m: m[0] + '*' * 8 + m[-1]
        },
        'phone': {
            'pattern': r'09\d{8}',
            'name': '手機號碼',
            'mask': lambda m: m[:4] + '****' + m[-2:]
        },
        'landline': {
            'pattern': r'0\d{1,2}-?\d{6,8}',
            'name': '市話',
            'mask': lambda m: re.sub(r'\d{4,}', lambda x: '*' * len(x.group()), m)
        },
        'credit_card': {
            'pattern': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'name': '信用卡號',
            'mask': lambda m: '**** **** **** ' + m.replace('-', '').replace(' ', '')[-4:]
        },
        'email': {
            'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'name': '電子郵件',
            'mask': lambda m: m[0] + '***@' + m.split('@')[1]
        },
        'bank_account': {
            'pattern': r'\b\d{10,16}\b',
            'name': '銀行帳號',
            'mask': lambda m: '*' * (len(m) - 4) + m[-4:]
        },
        'address': {
            # 台灣地址格式
            'pattern': r'[縣市][^縣市]{0,3}[鄉鎮市區][^鄉鎮市區]{0,10}[路街段巷弄號][\d\-之]*號?',
            'name': '地址',
            'mask': lambda m: m[:6] + '***'
        },
        'date_of_birth': {
            # 民國或西元年份
            'pattern': r'(\d{2,3}年\d{1,2}月\d{1,2}日|\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            'name': '出生日期',
            'mask': lambda m: '****/**/**'
        }
    }
    
    def __init__(self, mask_types: Optional[List[str]] = None):
        """
        初始化遮罩器
        
        Args:
            mask_types: 要遮罩的類型列表（None 表示全部）
        """
        self.mask_types = mask_types or list(self.PATTERNS.keys())
        self.compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict:
        """編譯正則表達式"""
        compiled = {}
        for mask_type in self.mask_types:
            if mask_type in self.PATTERNS:
                pattern_info = self.PATTERNS[mask_type]
                compiled[mask_type] = {
                    'regex': re.compile(pattern_info['pattern']),
                    'name': pattern_info['name'],
                    'mask_func': pattern_info['mask']
                }
        return compiled
    
    def mask(self, text: str) -> MaskResult:
        """
        遮罩文字中的敏感資訊
        
        Args:
            text: 原始文字
            
        Returns:
            MaskResult: 遮罩結果
        """
        masked_text = text
        sensitive_items = []
        mask_count = 0
        
        # 依序處理每種類型
        for mask_type, pattern_info in self.compiled_patterns.items():
            matches = pattern_info['regex'].finditer(masked_text)
            
            for match in matches:
                original_value = match.group()
                masked_value = pattern_info['mask_func'](original_value)
                
                # 記錄敏感資料
                sensitive_items.append({
                    'type': mask_type,
                    'type_name': pattern_info['name'],
                    'original': original_value,
                    'masked': masked_value,
                    'position': match.span()
                })
                
                # 替換文字
                masked_text = masked_text.replace(original_value, masked_value)
                mask_count += 1
        
        return MaskResult(
            original=text,
            masked=masked_text,
            sensitive_items=sensitive_items,
            mask_count=mask_count
        )
    
    def mask_dict(self, data: Dict) -> Dict:
        """
        遮罩字典中的敏感資訊
        
        Args:
            data: 原始資料字典
            
        Returns:
            遮罩後的字典
        """
        masked_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                result = self.mask(value)
                masked_data[key] = result.masked
            elif isinstance(value, dict):
                masked_data[key] = self.mask_dict(value)
            elif isinstance(value, list):
                masked_data[key] = [
                    self.mask_dict(item) if isinstance(item, dict) 
                    else self.mask(item).masked if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                masked_data[key] = value
        
        return masked_data
    
    def detect(self, text: str) -> List[Dict]:
        """
        僅偵測敏感資訊，不進行遮罩
        
        Args:
            text: 要檢查的文字
            
        Returns:
            偵測到的敏感資料列表
        """
        result = self.mask(text)
        return result.sensitive_items
    
    def get_mask_types(self) -> List[Dict[str, str]]:
        """
        取得支援的遮罩類型
        
        Returns:
            遮罩類型列表
        """
        return [
            {
                'type': mask_type,
                'name': info['name']
            }
            for mask_type, info in self.PATTERNS.items()
        ]


class SmartPrivacyMasker(PrivacyMasker):
    """智慧個資遮罩器（加強版）"""
    
    def __init__(self, mask_types: Optional[List[str]] = None, aggressive: bool = False):
        """
        初始化智慧遮罩器
        
        Args:
            mask_types: 要遮罩的類型列表
            aggressive: 是否使用積極模式（更嚴格的遮罩）
        """
        super().__init__(mask_types)
        self.aggressive = aggressive
        
        # 積極模式：額外遮罩規則
        if aggressive:
            self.PATTERNS.update({
                'amount': {
                    'pattern': r'NT?\$?\s*[\d,]+(?:\.\d+)?(?:元)?',
                    'name': '金額',
                    'mask': lambda m: 'NT$ ***'
                },
                'numbers': {
                    'pattern': r'\b\d{6,}\b',
                    'name': '長數字',
                    'mask': lambda m: '*' * len(m)
                }
            })
            self.compiled_patterns = self._compile_patterns()
    
    def mask_with_context(self, text: str, context_keywords: List[str] = None) -> MaskResult:
        """
        根據上下文智慧遮罩
        
        Args:
            text: 原始文字
            context_keywords: 上下文關鍵字（如 '帳單', '消費' 等）
            
        Returns:
            遮罩結果
        """
        # 根據關鍵字調整遮罩策略
        if context_keywords:
            if any(kw in text for kw in ['帳單', '消費', '交易']):
                # 金融文件：保留金額，遮罩其他
                self.mask_types = [t for t in self.mask_types if t != 'amount']
            elif any(kw in text for kw in ['身分證', '戶籍']):
                # 身分文件：全面遮罩
                self.aggressive = True
        
        return self.mask(text)


def quick_mask(text: str, types: Optional[List[str]] = None) -> str:
    """
    快速遮罩函數
    
    Args:
        text: 要遮罩的文字
        types: 遮罩類型（None 表示全部）
        
    Returns:
        遮罩後的文字
    """
    masker = PrivacyMasker(mask_types=types)
    return masker.mask(text).masked


def detect_sensitive_info(text: str) -> List[Dict]:
    """
    快速偵測敏感資訊
    
    Args:
        text: 要檢查的文字
        
    Returns:
        偵測到的敏感資料列表
    """
    masker = PrivacyMasker()
    return masker.detect(text)


# 匯出主要類別與函數
__all__ = [
    'PrivacyMasker',
    'SmartPrivacyMasker', 
    'MaskResult',
    'quick_mask',
    'detect_sensitive_info'
]

