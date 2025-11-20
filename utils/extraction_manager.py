"""
提取管理器

管理多個提取器，支援規則提取和 AI fallback
"""

from typing import Dict, Any, List, Optional
from .extractors.base_extractor import BaseExtractor
from .extractors.fubon_credit_card_extractor import FubonCreditCardExtractor
from .schema_validator import SchemaValidator
from .ai_integrator import AIIntegrator, AIProvider


class ExtractionManager:
    """提取管理器"""
    
    def __init__(self, enable_ai_fallback: bool = False, ai_provider: str = "openai"):
        """
        初始化管理器
        
        Args:
            enable_ai_fallback: 是否啟用 AI fallback
            ai_provider: AI 服務提供者
        """
        self.extractors: List[BaseExtractor] = []
        self.validator = SchemaValidator()
        self.enable_ai_fallback = enable_ai_fallback
        self.ai_provider = ai_provider
        
        # 註冊提取器
        self._register_extractors()
    
    def _register_extractors(self):
        """註冊所有提取器"""
        self.extractors = [
            FubonCreditCardExtractor(),
            # 可以繼續加入其他銀行的提取器
        ]
    
    def extract(self, text: str, metadata: Optional[Dict] = None, 
                validate: bool = True) -> Dict[str, Any]:
        """
        提取資訊
        
        Args:
            text: PDF 文字內容
            metadata: 額外的元資料
            validate: 是否驗證輸出
            
        Returns:
            提取結果
        """
        result = {
            'success': False,
            'method': None,
            'data': None,
            'validation': None,
            'errors': []
        }
        
        # 1. 嘗試規則提取
        for extractor in self.extractors:
            if extractor.can_extract(text):
                try:
                    data = extractor.extract(text, metadata)
                    result['success'] = True
                    result['method'] = 'rule_based'
                    result['data'] = data
                    result['extractor'] = extractor.__class__.__name__
                    
                    # 驗證輸出
                    if validate:
                        schema_name = self._get_schema_name(data.get('document_type'))
                        if schema_name:
                            validation_result = self.validator.validate_with_details(
                                data, schema_name
                            )
                            result['validation'] = validation_result
                            
                            # 如果驗證失敗且啟用 AI fallback
                            if not validation_result['valid'] and self.enable_ai_fallback:
                                result['errors'].append(
                                    "規則提取驗證失敗，嘗試 AI fallback"
                                )
                                ai_result = self._try_ai_extraction(text, data.get('document_type'))
                                if ai_result['success']:
                                    return ai_result
                    
                    return result
                
                except Exception as e:
                    result['errors'].append(f"規則提取失敗: {str(e)}")
        
        # 2. 如果規則提取失敗，嘗試 AI
        if not result['success'] and self.enable_ai_fallback:
            result = self._try_ai_extraction(text)
        
        # 3. 都失敗
        if not result['success']:
            result['errors'].append("無法識別文件類型或提取失敗")
        
        return result
    
    def _try_ai_extraction(self, text: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """嘗試 AI 提取"""
        result = {
            'success': False,
            'method': 'ai',
            'data': None,
            'validation': None,
            'errors': []
        }
        
        try:
            provider_enum = AIProvider(self.ai_provider)
            integrator = AIIntegrator(provider=provider_enum)
            
            # 使用 AI 分析
            ai_response = integrator.analyze_document(
                text,
                document_type=document_type or 'financial'
            )
            
            if ai_response.success:
                # 嘗試解析 AI 返回的 JSON
                import json
                try:
                    data = json.loads(ai_response.content)
                    result['success'] = True
                    result['data'] = data
                    
                    # 驗證 AI 提取的結果
                    if document_type:
                        schema_name = self._get_schema_name(document_type)
                        if schema_name:
                            validation_result = self.validator.validate_with_details(
                                data, schema_name
                            )
                            result['validation'] = validation_result
                
                except json.JSONDecodeError:
                    # AI 沒有返回 JSON，保留原始內容
                    result['data'] = {
                        'raw_content': ai_response.content
                    }
                    result['success'] = True
            else:
                result['errors'].append(f"AI 提取失敗: {ai_response.error}")
        
        except Exception as e:
            result['errors'].append(f"AI 提取錯誤: {str(e)}")
        
        return result
    
    def _get_schema_name(self, document_type: str) -> Optional[str]:
        """根據文件類型取得 Schema 名稱"""
        schema_mapping = {
            'credit_card': 'credit_card_schema',
            'bank_statement': 'bank_statement_schema'
        }
        return schema_mapping.get(document_type)
    
    def get_available_extractors(self) -> List[Dict[str, str]]:
        """取得可用的提取器列表"""
        return [
            {
                'name': extractor.__class__.__name__,
                'description': extractor.__class__.__doc__ or '',
                'confidence': extractor.confidence
            }
            for extractor in self.extractors
        ]
    
    def get_available_schemas(self) -> List[Dict[str, Any]]:
        """取得可用的 Schema 列表"""
        schema_names = self.validator.list_schemas()
        return [
            self.validator.get_schema_info(name)
            for name in schema_names
        ]


# 快速使用函數
def quick_extract(text: str, validate: bool = True, 
                  enable_ai: bool = False) -> Dict[str, Any]:
    """
    快速提取函數
    
    Args:
        text: PDF 文字內容
        validate: 是否驗證
        enable_ai: 是否啟用 AI fallback
        
    Returns:
        提取結果
    """
    manager = ExtractionManager(enable_ai_fallback=enable_ai)
    return manager.extract(text, validate=validate)


__all__ = [
    'ExtractionManager',
    'quick_extract'
]

