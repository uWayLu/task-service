"""
PDF 解析工具
使用 pdfplumber 和 PyPDF2 來提取 PDF 內容
"""
import pdfplumber
import PyPDF2
from typing import Dict, List, Any
import re


class PDFParser:
    """PDF 解析器"""
    
    def __init__(self):
        self.content = ""
        self.pages = []
        
    def extract_text(self, filepath: str) -> Dict[str, Any]:
        """
        從 PDF 檔案中提取文字內容
        
        Args:
            filepath: PDF 檔案路徑
            
        Returns:
            包含文字內容和元資料的字典
        """
        try:
            # 使用 pdfplumber 提取文字（更準確）
            text_content = self._extract_with_pdfplumber(filepath)
            
            # 使用 PyPDF2 提取元資料
            metadata = self._extract_metadata(filepath)
            
            return {
                'text': text_content,
                'pages': self.pages,
                'metadata': metadata,
                'total_pages': len(self.pages)
            }
            
        except Exception as e:
            raise Exception(f'PDF 解析失敗: {str(e)}')
    
    def _extract_with_pdfplumber(self, filepath: str) -> str:
        """使用 pdfplumber 提取文字"""
        full_text = []
        self.pages = []
        
        with pdfplumber.open(filepath) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    full_text.append(text)
                    self.pages.append({
                        'page_number': page_num,
                        'text': text,
                        'width': page.width,
                        'height': page.height
                    })
        
        return '\n\n'.join(full_text)
    
    def _extract_metadata(self, filepath: str) -> Dict[str, Any]:
        """使用 PyPDF2 提取 PDF 元資料"""
        metadata = {}
        
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if pdf_reader.metadata:
                    metadata = {
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                    }
                
                metadata['num_pages'] = len(pdf_reader.pages)
                
        except Exception as e:
            metadata['error'] = str(e)
        
        return metadata
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """
        從文字中提取數字
        
        Args:
            text: 要解析的文字
            
        Returns:
            數字列表
        """
        # 匹配各種數字格式：1,234.56 或 1234.56 或 $1,234.56
        pattern = r'[\$]?[\d,]+\.?\d*'
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            # 移除貨幣符號和逗號
            clean_number = match.replace('$', '').replace(',', '')
            try:
                numbers.append(float(clean_number))
            except ValueError:
                continue
        
        return numbers
    
    @staticmethod
    def extract_dates(text: str) -> List[str]:
        """
        從文字中提取日期
        
        Args:
            text: 要解析的文字
            
        Returns:
            日期字串列表
        """
        # 匹配常見日期格式
        patterns = [
            r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?',  # 2024-01-15 或 2024年01月15日
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',          # 01/15/2024
            r'\d{4}\.\d{1,2}\.\d{1,2}',              # 2024.01.15
        ]
        
        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return dates
    
    @staticmethod
    def extract_amounts(text: str) -> Dict[str, List[float]]:
        """
        從文字中提取金額資訊
        
        Args:
            text: 要解析的文字
            
        Returns:
            包含不同類型金額的字典
        """
        amounts = {
            'all_amounts': [],
            'totals': [],
            'balances': []
        }
        
        # 提取所有數字
        all_numbers = PDFParser.extract_numbers(text)
        amounts['all_amounts'] = all_numbers
        
        # 提取總額相關數字
        total_pattern = r'(?:總額|合計|總計|Total|Amount)[\s:：]*[\$]?([\d,]+\.?\d*)'
        total_matches = re.findall(total_pattern, text, re.IGNORECASE)
        for match in total_matches:
            try:
                amounts['totals'].append(float(match.replace(',', '')))
            except ValueError:
                continue
        
        # 提取餘額相關數字
        balance_pattern = r'(?:餘額|結餘|Balance)[\s:：]*[\$]?([\d,]+\.?\d*)'
        balance_matches = re.findall(balance_pattern, text, re.IGNORECASE)
        for match in balance_matches:
            try:
                amounts['balances'].append(float(match.replace(',', '')))
            except ValueError:
                continue
        
        return amounts

