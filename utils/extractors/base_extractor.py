"""
基礎提取器

定義提取器的基礎介面
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime
from pathlib import Path


class BaseExtractor(ABC):
    """基礎提取器抽象類別"""
    
    def __init__(self):
        self.confidence = 0.0
        self.extraction_method = "rule_based"
    
    @abstractmethod
    def can_extract(self, text: str) -> bool:
        """
        判斷是否能夠提取此文件
        
        Args:
            text: PDF 文字內容
            
        Returns:
            是否能提取
        """
        pass
    
    @abstractmethod
    def extract(self, text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        提取資訊
        
        Args:
            text: PDF 文字內容
            metadata: 額外的元資料
            
        Returns:
            提取的結構化資料
        """
        pass
    
    @abstractmethod
    def get_schema_path(self) -> str:
        """
        取得 JSON Schema 路徑
        
        Returns:
            Schema 檔案路徑
        """
        pass
    
    def load_schema(self) -> Dict:
        """載入 JSON Schema"""
        schema_path = self.get_schema_path()
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def add_metadata(self, data: Dict, source_file: str = None, total_pages: int = None) -> Dict:
        """
        加入元資料
        
        Args:
            data: 提取的資料
            source_file: 來源檔案
            total_pages: 總頁數
            
        Returns:
            加入元資料後的資料
        """
        if 'metadata' not in data:
            data['metadata'] = {}
        
        data['metadata'].update({
            'extracted_at': datetime.now().isoformat(),
            'extraction_method': self.extraction_method,
            'confidence': self.confidence
        })
        
        if source_file:
            data['metadata']['source_file'] = source_file
        
        if total_pages:
            data['metadata']['total_pages'] = total_pages
        
        return data

