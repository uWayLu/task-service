"""
JSON Schema 驗證工具

用於驗證提取的資料是否符合定義的 Schema
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

try:
    from jsonschema import validate, ValidationError, Draft7Validator
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print("警告: jsonschema 套件未安裝，請執行：pip install jsonschema")


class SchemaValidator:
    """JSON Schema 驗證器"""
    
    def __init__(self, schemas_dir: str = "schemas"):
        """
        初始化驗證器
        
        Args:
            schemas_dir: Schema 檔案目錄
        """
        self.schemas_dir = Path(schemas_dir)
        self.schemas_cache = {}
    
    def load_schema(self, schema_name: str) -> Dict:
        """
        載入 Schema
        
        Args:
            schema_name: Schema 名稱（不含 .json 副檔名）
            
        Returns:
            Schema 字典
        """
        if schema_name in self.schemas_cache:
            return self.schemas_cache[schema_name]
        
        schema_path = self.schemas_dir / f"{schema_name}.json"
        
        if not schema_path.exists():
            raise FileNotFoundError(f"找不到 Schema 檔案: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        self.schemas_cache[schema_name] = schema
        return schema
    
    def validate(self, data: Dict, schema_name: str) -> Tuple[bool, Optional[List[str]]]:
        """
        驗證資料
        
        Args:
            data: 要驗證的資料
            schema_name: Schema 名稱
            
        Returns:
            (是否通過驗證, 錯誤訊息列表)
        """
        if not JSONSCHEMA_AVAILABLE:
            return False, ["jsonschema 套件未安裝"]
        
        try:
            schema = self.load_schema(schema_name)
            validate(instance=data, schema=schema)
            return True, None
        
        except ValidationError as e:
            errors = [f"驗證失敗: {e.message}"]
            
            # 提供更詳細的錯誤路徑
            if e.path:
                path = " -> ".join(str(p) for p in e.path)
                errors.append(f"錯誤位置: {path}")
            
            if e.schema_path:
                schema_path = " -> ".join(str(p) for p in e.schema_path)
                errors.append(f"Schema 路徑: {schema_path}")
            
            return False, errors
        
        except FileNotFoundError as e:
            return False, [str(e)]
        
        except Exception as e:
            return False, [f"驗證時發生錯誤: {str(e)}"]
    
    def validate_with_details(self, data: Dict, schema_name: str) -> Dict[str, Any]:
        """
        驗證資料並返回詳細結果
        
        Args:
            data: 要驗證的資料
            schema_name: Schema 名稱
            
        Returns:
            驗證結果字典
        """
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'schema_name': schema_name
        }
        
        if not JSONSCHEMA_AVAILABLE:
            result['errors'] = ["jsonschema 套件未安裝"]
            return result
        
        try:
            schema = self.load_schema(schema_name)
            validator = Draft7Validator(schema)
            
            # 收集所有錯誤
            errors = list(validator.iter_errors(data))
            
            if not errors:
                result['valid'] = True
            else:
                result['errors'] = [
                    {
                        'message': e.message,
                        'path': list(e.path),
                        'schema_path': list(e.schema_path),
                        'validator': e.validator
                    }
                    for e in errors
                ]
            
            # 檢查警告（選填欄位缺失等）
            result['warnings'] = self._check_warnings(data, schema)
            
        except FileNotFoundError as e:
            result['errors'] = [{'message': str(e)}]
        except Exception as e:
            result['errors'] = [{'message': f"驗證時發生錯誤: {str(e)}"}]
        
        return result
    
    def _check_warnings(self, data: Dict, schema: Dict) -> List[str]:
        """檢查警告（非必填但建議填寫的欄位）"""
        warnings = []
        
        # 檢查選填但重要的欄位
        optional_important_fields = {
            'credit_card': [
                'summary',
                'interest_info.annual_interest_fee',
                'card_info.credit_limit'
            ],
            'bank_statement': [
                'summary',
                'balance_info.available_balance'
            ]
        }
        
        doc_type = data.get('document_type')
        if doc_type in optional_important_fields:
            for field_path in optional_important_fields[doc_type]:
                if not self._has_field(data, field_path):
                    warnings.append(f"建議填寫欄位: {field_path}")
        
        return warnings
    
    def _has_field(self, data: Dict, field_path: str) -> bool:
        """檢查是否有某個欄位"""
        parts = field_path.split('.')
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        
        return current is not None
    
    def list_schemas(self) -> List[str]:
        """列出所有可用的 Schema"""
        if not self.schemas_dir.exists():
            return []
        
        return [
            f.stem for f in self.schemas_dir.glob('*.json')
            if f.is_file()
        ]
    
    def get_schema_info(self, schema_name: str) -> Dict[str, Any]:
        """
        取得 Schema 資訊
        
        Args:
            schema_name: Schema 名稱
            
        Returns:
            Schema 資訊
        """
        try:
            schema = self.load_schema(schema_name)
            
            return {
                'name': schema_name,
                'title': schema.get('title', ''),
                'description': schema.get('description', ''),
                'required_fields': schema.get('required', []),
                'properties': list(schema.get('properties', {}).keys())
            }
        
        except Exception as e:
            return {
                'name': schema_name,
                'error': str(e)
            }


def quick_validate(data: Dict, schema_name: str) -> bool:
    """
    快速驗證函數
    
    Args:
        data: 要驗證的資料
        schema_name: Schema 名稱（如 'credit_card_schema'）
        
    Returns:
        是否通過驗證
    """
    validator = SchemaValidator()
    is_valid, errors = validator.validate(data, schema_name)
    
    if not is_valid and errors:
        print(f"驗證失敗：")
        for error in errors:
            print(f"  - {error}")
    
    return is_valid


# 匯出
__all__ = [
    'SchemaValidator',
    'quick_validate'
]

