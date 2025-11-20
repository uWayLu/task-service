"""
Extractors Package

提供各種文件的資訊提取器
"""

from .base_extractor import BaseExtractor
from .fubon_credit_card_extractor import FubonCreditCardExtractor

__all__ = ['BaseExtractor', 'FubonCreditCardExtractor']

