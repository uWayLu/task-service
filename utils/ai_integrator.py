"""
AI 整合模組

支援：
1. OpenAI API (GPT-4, GPT-3.5)
2. Anthropic Claude API
3. 自訂 API 端點
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class AIProvider(Enum):
    """AI 服務提供者"""
    OPENAI = "openai"
    CLAUDE = "claude"
    CUSTOM = "custom"


@dataclass
class AIResponse:
    """AI 回應"""
    success: bool
    content: str
    provider: str
    model: str
    usage: Optional[Dict] = None
    raw_response: Optional[Dict] = None
    error: Optional[str] = None


class AIIntegrator:
    """AI 整合器"""
    
    # API 端點
    ENDPOINTS = {
        AIProvider.OPENAI: "https://api.openai.com/v1/chat/completions",
        AIProvider.CLAUDE: "https://api.anthropic.com/v1/messages"
    }
    
    # 預設模型
    DEFAULT_MODELS = {
        AIProvider.OPENAI: "gpt-4-turbo-preview",
        AIProvider.CLAUDE: "claude-3-sonnet-20240229"
    }
    
    def __init__(
        self,
        provider: AIProvider = AIProvider.OPENAI,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        custom_endpoint: Optional[str] = None
    ):
        """
        初始化 AI 整合器
        
        Args:
            provider: AI 服務提供者
            api_key: API 金鑰（從環境變數讀取）
            model: 使用的模型
            custom_endpoint: 自訂 API 端點
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key()
        self.model = model or self._get_default_model()
        self.endpoint = custom_endpoint or self.ENDPOINTS.get(provider)
        
        if not self.api_key:
            raise ValueError(f"未設定 API 金鑰（{provider.value}）")
    
    def _get_api_key(self) -> Optional[str]:
        """從環境變數取得 API 金鑰"""
        if self.provider == AIProvider.OPENAI:
            return os.getenv('OPENAI_API_KEY')
        elif self.provider == AIProvider.CLAUDE:
            return os.getenv('ANTHROPIC_API_KEY')
        return os.getenv('AI_API_KEY')
    
    def _get_default_model(self) -> str:
        """取得預設模型"""
        return self.DEFAULT_MODELS.get(self.provider, "gpt-3.5-turbo")
    
    def analyze_document(
        self,
        text: str,
        document_type: str = "financial",
        instructions: Optional[str] = None
    ) -> AIResponse:
        """
        分析文件內容
        
        Args:
            text: 文件文字內容
            document_type: 文件類型（financial/bank_statement/credit_card 等）
            instructions: 額外指示
            
        Returns:
            AIResponse: AI 分析結果
        """
        # 建立提示詞
        prompt = self._build_prompt(text, document_type, instructions)
        
        # 呼叫 AI API
        return self._call_api(prompt)
    
    def _build_prompt(
        self,
        text: str,
        document_type: str,
        instructions: Optional[str] = None
    ) -> str:
        """建立提示詞"""
        
        # 基礎提示
        base_prompts = {
            "financial": """
你是一個專業的金融文件分析助手。請分析以下文件並提取關鍵資訊。

請以 JSON 格式返回以下資訊：
{
    "document_type": "文件類型",
    "summary": "文件摘要",
    "key_information": {
        "金額": "總金額",
        "日期": "相關日期",
        "機構": "金融機構名稱"
    },
    "transactions": [
        {
            "date": "交易日期",
            "description": "交易描述",
            "amount": "金額"
        }
    ],
    "recommendations": ["建議事項"]
}
""",
            "bank_statement": """
你是銀行對帳單分析專家。請分析以下對帳單並提取：
1. 帳戶資訊
2. 期初/期末餘額
3. 所有交易記錄
4. 統計資訊（收入、支出、結餘）

請以結構化的 JSON 格式返回。
""",
            "credit_card": """
你是信用卡帳單分析專家。請分析以下帳單並提取：
1. 帳單週期
2. 應繳金額與到期日
3. 消費明細
4. 重要提醒事項

請以結構化的 JSON 格式返回。
"""
        }
        
        prompt = base_prompts.get(document_type, base_prompts["financial"])
        
        if instructions:
            prompt += f"\n\n額外指示：{instructions}"
        
        prompt += f"\n\n文件內容：\n{text}"
        
        return prompt
    
    def _call_api(self, prompt: str) -> AIResponse:
        """呼叫 AI API"""
        try:
            if self.provider == AIProvider.OPENAI:
                return self._call_openai(prompt)
            elif self.provider == AIProvider.CLAUDE:
                return self._call_claude(prompt)
            else:
                return self._call_custom(prompt)
        except Exception as e:
            return AIResponse(
                success=False,
                content="",
                provider=self.provider.value,
                model=self.model,
                error=str(e)
            )
    
    def _call_openai(self, prompt: str) -> AIResponse:
        """呼叫 OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一個專業的金融文件分析助手，擅長從文件中提取關鍵資訊。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        response = requests.post(self.endpoint, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        return AIResponse(
            success=True,
            content=result['choices'][0]['message']['content'],
            provider=self.provider.value,
            model=self.model,
            usage=result.get('usage'),
            raw_response=result
        )
    
    def _call_claude(self, prompt: str) -> AIResponse:
        """呼叫 Claude API"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": self.model,
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = requests.post(self.endpoint, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        return AIResponse(
            success=True,
            content=result['content'][0]['text'],
            provider=self.provider.value,
            model=self.model,
            usage=result.get('usage'),
            raw_response=result
        )
    
    def _call_custom(self, prompt: str) -> AIResponse:
        """呼叫自訂 API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": prompt,
            "model": self.model
        }
        
        response = requests.post(self.endpoint, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        return AIResponse(
            success=True,
            content=result.get('content', result.get('response', '')),
            provider=self.provider.value,
            model=self.model,
            raw_response=result
        )
    
    def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any]
    ) -> AIResponse:
        """
        提取結構化資料
        
        Args:
            text: 文字內容
            schema: 期望的資料結構
            
        Returns:
            AIResponse: 結構化資料
        """
        schema_str = json.dumps(schema, ensure_ascii=False, indent=2)
        
        prompt = f"""
請從以下文字中提取資訊，並按照指定的結構返回 JSON 格式資料。

期望的資料結構：
{schema_str}

文字內容：
{text}

請嚴格按照上述結構返回 JSON 格式資料。
"""
        
        return self._call_api(prompt)
    
    def summarize(self, text: str, max_length: int = 200) -> AIResponse:
        """
        摘要文字
        
        Args:
            text: 原始文字
            max_length: 最大長度
            
        Returns:
            AIResponse: 摘要結果
        """
        prompt = f"""
請將以下文字摘要為 {max_length} 字以內的重點摘要。

文字內容：
{text}

請提供簡潔的摘要。
"""
        
        return self._call_api(prompt)


def analyze_financial_document(
    text: str,
    provider: str = "openai",
    api_key: Optional[str] = None
) -> Dict:
    """
    快速分析金融文件
    
    Args:
        text: 文件內容
        provider: AI 服務提供者
        api_key: API 金鑰
        
    Returns:
        分析結果
    """
    provider_enum = AIProvider(provider)
    integrator = AIIntegrator(provider=provider_enum, api_key=api_key)
    response = integrator.analyze_document(text, document_type="financial")
    
    if response.success:
        try:
            # 嘗試解析 JSON
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "success": True,
                "content": response.content,
                "raw": True
            }
    else:
        return {
            "success": False,
            "error": response.error
        }


# 匯出
__all__ = [
    'AIIntegrator',
    'AIProvider',
    'AIResponse',
    'analyze_financial_document'
]

