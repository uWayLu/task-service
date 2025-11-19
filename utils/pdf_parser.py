"""
PDF 解析工具
使用 pdfplumber 和 PyPDF2 來提取 PDF 內容
"""
import os
import pdfplumber
import PyPDF2
from typing import Dict, List, Any, Optional
import re


class PDFParser:
    """PDF 解析器"""
    
    def __init__(self):
        self.content = ""
        self.pages = []
        self.default_passwords = self._load_default_passwords()
    
    def _load_default_passwords(self) -> List[str]:
        """
        從環境變數載入預設密碼列表
        
        支援兩種格式：
        1. PDF_DEFAULT_PASSWORDS=pass1,pass2,pass3
        2. PDF_PASSWORD_1=pass1, PDF_PASSWORD_2=pass2, ...
        
        Returns:
            密碼列表
        """
        passwords = []
        
        # 方法 1: 逗號分隔的密碼列表
        default_passwords = os.getenv('PDF_DEFAULT_PASSWORDS', '')
        if default_passwords:
            passwords.extend([p.strip() for p in default_passwords.split(',') if p.strip()])
        
        # 方法 2: 編號的密碼
        i = 1
        while True:
            password = os.getenv(f'PDF_PASSWORD_{i}')
            if not password:
                break
            passwords.append(password.strip())
            i += 1
        
        return passwords
        
    def extract_text(self, filepath: str, password: Optional[str] = None, 
                     auto_try_defaults: bool = True) -> Dict[str, Any]:
        """
        從 PDF 檔案中提取文字內容
        
        Args:
            filepath: PDF 檔案路徑
            password: PDF 密碼（如果有加密）
            auto_try_defaults: 是否自動嘗試預設密碼（預設 True）
            
        Returns:
            包含文字內容和元資料的字典
            
        Raises:
            Exception: PDF 解析失敗
            PermissionError: PDF 有密碼保護但所有密碼都失敗
        """
        # 先檢查是否加密
        is_encrypted, encryption_info = self._check_encryption(filepath)
        
        if is_encrypted:
            # 建立要嘗試的密碼列表
            passwords_to_try = []
            
            # 如果提供了密碼，優先使用
            if password:
                passwords_to_try.append(password)
            
            # 如果啟用自動嘗試，加入預設密碼
            if auto_try_defaults and self.default_passwords:
                passwords_to_try.extend(self.default_passwords)
            
            # 如果沒有任何密碼可嘗試
            if not passwords_to_try:
                raise PermissionError(
                    'PDF 檔案有密碼保護，請提供密碼或設定預設密碼。\n'
                    f'加密資訊: {encryption_info}\n'
                    '提示: 在 .env 中設定 PDF_DEFAULT_PASSWORDS'
                )
            
            # 嘗試所有密碼
            last_error = None
            used_password = None
            
            for pwd in passwords_to_try:
                try:
                    text_content = self._extract_with_pdfplumber(filepath, pwd)
                    metadata = self._extract_metadata(filepath, pwd)
                    used_password = pwd
                    break  # 成功就跳出
                except Exception as e:
                    last_error = e
                    continue  # 失敗就試下一個
            else:
                # 所有密碼都失敗
                tried_count = len(passwords_to_try)
                raise PermissionError(
                    f'所有密碼都無法解密 PDF（嘗試了 {tried_count} 個密碼）\n'
                    f'最後錯誤: {str(last_error)}'
                )
        else:
            # 無加密，正常處理
            try:
                text_content = self._extract_with_pdfplumber(filepath, None)
                metadata = self._extract_metadata(filepath, None)
                used_password = None
            except Exception as e:
                raise Exception(f'PDF 解析失敗: {str(e)}')
        
        result = {
            'text': text_content,
            'pages': self.pages,
            'metadata': metadata,
            'total_pages': len(self.pages),
            'is_encrypted': is_encrypted,
            'encryption_info': encryption_info if is_encrypted else None
        }
        
        # 如果有使用密碼，記錄（但不顯示密碼內容）
        if used_password:
            result['password_used'] = True
            result['password_hint'] = f'{used_password[0]}***{used_password[-1]}' if len(used_password) > 2 else '***'
        
        return result
    
    def _check_encryption(self, filepath: str) -> tuple[bool, Optional[str]]:
        """
        檢查 PDF 是否加密
        
        Returns:
            (是否加密, 加密資訊)
        """
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if pdf_reader.is_encrypted:
                    # 獲取加密資訊
                    encryption_info = "PDF 使用密碼保護"
                    
                    # 嘗試獲取更多資訊
                    try:
                        if hasattr(pdf_reader, '_encryption'):
                            encryption_info += f" (加密方法: {pdf_reader._encryption})"
                    except:
                        pass
                    
                    return True, encryption_info
                
                return False, None
                
        except Exception as e:
            # 如果檢查失敗，假設沒有加密
            return False, f"無法檢查加密狀態: {str(e)}"
    
    def _extract_with_pdfplumber(self, filepath: str, password: Optional[str] = None) -> str:
        """
        使用 pdfplumber 提取文字
        
        Args:
            filepath: PDF 檔案路徑
            password: 密碼（如果需要）
        """
        full_text = []
        self.pages = []
        
        try:
            # pdfplumber 開啟時可以傳入密碼
            open_kwargs = {'password': password} if password else {}
            
            with pdfplumber.open(filepath, **open_kwargs) as pdf:
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
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'password' in error_msg or 'encrypted' in error_msg:
                raise PermissionError('PDF 需要密碼或密碼錯誤')
            raise
    
    def _extract_metadata(self, filepath: str, password: Optional[str] = None) -> Dict[str, Any]:
        """
        使用 PyPDF2 提取 PDF 元資料
        
        Args:
            filepath: PDF 檔案路徑
            password: 密碼（如果需要）
        """
        metadata = {}
        
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # 如果加密，嘗試解密
                if pdf_reader.is_encrypted:
                    if password:
                        decrypt_result = pdf_reader.decrypt(password)
                        if decrypt_result == 0:
                            raise PermissionError('密碼錯誤')
                        metadata['decrypted'] = True
                    else:
                        raise PermissionError('PDF 需要密碼')
                
                # 提取元資料
                if pdf_reader.metadata:
                    metadata.update({
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                    })
                
                metadata['num_pages'] = len(pdf_reader.pages)
                metadata['is_encrypted'] = pdf_reader.is_encrypted
                
        except PermissionError:
            raise
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

