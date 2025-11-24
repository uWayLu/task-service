#!/usr/bin/env python3
"""
Task Service CLI - 統一的命令列工具

功能：
1. PDF 解析（支援密碼）
2. 個資遮罩
3. AI 分析
4. Schema 驗證
5. 完整的文件處理流程

使用範例：
    # 基本 PDF 解析
    python cli.py parse document.pdf
    
    # 有密碼的 PDF
    python cli.py parse document.pdf --password A123456789
    
    # 遮罩個資
    python cli.py mask document.pdf --output masked.txt
    
    # AI 分析（自動遮罩）
    python cli.py analyze document.pdf --provider openai
    
    # 完整流程（解析→遮罩→AI分析→驗證）
    python cli.py process document.pdf --ai --validate
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數（.env 檔案）
load_dotenv()

# 添加專案根目錄到 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pdf_parser import PDFParser
from utils.privacy_masker import PrivacyMasker
from utils.ai_integrator import AIIntegrator, AIProvider
from utils.schema_validator import SchemaValidator
from utils.extraction_manager import ExtractionManager


class Colors:
    """終端機顏色"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """印出標題"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_success(text):
    """印出成功訊息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """印出錯誤訊息"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    """印出警告訊息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    """印出資訊"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.RESET}")


def save_output(content, output_file, file_type="txt"):
    """儲存輸出檔案"""
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_type == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                if isinstance(content, str):
                    f.write(content)
                else:
                    json.dump(content, f, ensure_ascii=False, indent=2)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print_success(f"已儲存至: {output_path}")
        return True
    except Exception as e:
        print_error(f"儲存失敗: {e}")
        return False


def cmd_parse(args):
    """解析 PDF 文件"""
    print_header(f"📄 解析 PDF: {args.file}")
    
    if not os.path.exists(args.file):
        print_error(f"檔案不存在: {args.file}")
        return 1
    
    try:
        parser = PDFParser()
        result = parser.extract_text(args.file, args.password)
        
        print_success("解析完成")
        print_info(f"總頁數: {result['total_pages']}")
        print_info(f"文字長度: {len(result['text'])} 字元")
        
        if args.output:
            save_output(result['text'], args.output, "txt")
        else:
            print("\n" + "─" * 60)
            print(result['text'][:500])  # 顯示前 500 字元
            if len(result['text']) > 500:
                print(f"\n... (還有 {len(result['text']) - 500} 個字元)")
            print("─" * 60)
        
        return 0
        
    except PermissionError as e:
        print_error(f"PDF 已加密: {e}")
        
        # 檢查是否有載入預設密碼
        parser = PDFParser()
        if parser.default_passwords:
            print_info(f"已嘗試 {len(parser.default_passwords)} 個預設密碼，但都失敗")
            print_warning("請檢查 .env 中的密碼是否正確，或使用 --password 參數手動提供")
        else:
            print_warning("請使用 --password 參數提供密碼，或在 .env 中設定 PDF_DEFAULT_PASSWORDS")
        
        return 1
    except Exception as e:
        print_error(f"解析失敗: {e}")
        return 1


def cmd_mask(args):
    """遮罩個資"""
    print_header(f"🛡️  遮罩個資: {args.file}")
    
    if not os.path.exists(args.file):
        print_error(f"檔案不存在: {args.file}")
        return 1
    
    try:
        # 先解析 PDF
        parser = PDFParser()
        pdf_result = parser.extract_text(args.file, args.password)
        text = pdf_result['text']
        
        # 遮罩個資
        mask_types = args.types.split(',') if args.types else None
        masker = PrivacyMasker(mask_types=mask_types)
        result = masker.mask(text)
        
        print_success(f"遮罩完成，共遮罩 {result.mask_count} 項敏感資訊")
        
        # 顯示敏感資訊統計
        if result.sensitive_items:
            type_counts = {}
            for item in result.sensitive_items:
                type_name = item['type_name']
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
            
            print_info("敏感資訊統計:")
            for type_name, count in type_counts.items():
                print(f"  - {type_name}: {count} 項")
        
        # 儲存結果
        if args.output:
            save_output(result.masked, args.output, "txt")
        
        # 儲存詳細報告
        if args.report:
            report = {
                'file': args.file,
                'processed_at': datetime.now().isoformat(),
                'mask_count': result.mask_count,
                'sensitive_items': result.sensitive_items
            }
            save_output(report, args.report, "json")
        
        return 0
        
    except PermissionError as e:
        print_error(f"PDF 已加密: {e}")
        parser = PDFParser()
        if parser.default_passwords:
            print_info(f"已嘗試 {len(parser.default_passwords)} 個預設密碼，但都失敗")
            print_warning("請檢查 .env 中的密碼是否正確，或使用 --password 參數手動提供")
        else:
            print_warning("請使用 --password 參數提供密碼，或在 .env 中設定 PDF_DEFAULT_PASSWORDS")
        return 1
    except Exception as e:
        print_error(f"遮罩失敗: {e}")
        return 1


def cmd_analyze(args):
    """AI 分析文件"""
    print_header(f"🤖 AI 分析: {args.file}")
    
    if not os.path.exists(args.file):
        print_error(f"檔案不存在: {args.file}")
        return 1
    
    try:
        # 解析 PDF
        parser = PDFParser()
        pdf_result = parser.extract_text(args.file, args.password)
        text = pdf_result['text']
        
        # 遮罩個資（如果需要）
        if not args.no_mask:
            print_info("遮罩個資中...")
            masker = PrivacyMasker()
            mask_result = masker.mask(text)
            text = mask_result.masked
            print_success(f"已遮罩 {mask_result.mask_count} 項敏感資訊")
        
        # AI 分析
        print_info(f"使用 {args.provider} 進行分析...")
        
        provider_map = {
            'openai': AIProvider.OPENAI,
            'claude': AIProvider.CLAUDE
        }
        
        provider = provider_map.get(args.provider, AIProvider.OPENAI)
        integrator = AIIntegrator(provider=provider, model=args.model)
        
        ai_result = integrator.analyze_document(
            text,
            document_type=args.doc_type,
            instructions=args.instructions
        )
        
        if ai_result.success:
            print_success("AI 分析完成")
            
            # 嘗試解析 JSON
            try:
                parsed = json.loads(ai_result.content)
                print("\n" + json.dumps(parsed, ensure_ascii=False, indent=2))
                
                if args.output:
                    save_output(parsed, args.output, "json")
            except json.JSONDecodeError:
                print("\n" + ai_result.content)
                
                if args.output:
                    save_output(ai_result.content, args.output, "txt")
            
            # 顯示使用量
            if ai_result.usage:
                print_info(f"Token 使用: {ai_result.usage}")
            
            return 0
        else:
            print_error(f"AI 分析失敗: {ai_result.error}")
            return 1
        
    except PermissionError as e:
        print_error(f"PDF 已加密: {e}")
        parser = PDFParser()
        if parser.default_passwords:
            print_info(f"已嘗試 {len(parser.default_passwords)} 個預設密碼，但都失敗")
            print_warning("請檢查 .env 中的密碼是否正確，或使用 --password 參數手動提供")
        else:
            print_warning("請使用 --password 參數提供密碼，或在 .env 中設定 PDF_DEFAULT_PASSWORDS")
        return 1
    except Exception as e:
        print_error(f"分析失敗: {e}")
        return 1


def cmd_process(args):
    """完整處理流程"""
    print_header(f"⚙️  完整處理: {args.file}")
    
    if not os.path.exists(args.file):
        print_error(f"檔案不存在: {args.file}")
        return 1
    
    try:
        output_dir = Path(args.output) if args.output else Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = Path(args.file).stem
        
        # 步驟 1: 解析 PDF
        print_info("步驟 1/4: 解析 PDF...")
        parser = PDFParser()
        pdf_result = parser.extract_text(args.file, args.password)
        text = pdf_result['text']
        
        original_file = output_dir / f"{base_name}_original.txt"
        save_output(text, original_file, "txt")
        print_success("PDF 解析完成")
        
        # 步驟 2: 遮罩個資
        print_info("步驟 2/4: 遮罩個資...")
        masker = PrivacyMasker()
        mask_result = masker.mask(text)
        
        masked_file = output_dir / f"{base_name}_masked.txt"
        save_output(mask_result.masked, masked_file, "txt")
        print_success(f"已遮罩 {mask_result.mask_count} 項敏感資訊")
        
        # 步驟 3: 結構化提取
        print_info("步驟 3/4: 結構化提取...")
        extractor = ExtractionManager(enable_ai_fallback=False)
        extraction_result = extractor.extract(
            mask_result.masked,
            metadata={'filename': args.file},
            validate=args.validate
        )
        
        extracted_file = output_dir / f"{base_name}_extracted.json"
        save_output(extraction_result, extracted_file, "json")
        
        if extraction_result['success']:
            print_success(f"提取成功 (方法: {extraction_result['method']})")
        else:
            print_warning(f"提取失敗: {extraction_result.get('errors')}")
        
        # 步驟 4: AI 分析（可選）
        if args.ai:
            print_info("步驟 4/4: AI 分析...")
            provider = AIProvider.OPENAI if args.provider == 'openai' else AIProvider.CLAUDE
            integrator = AIIntegrator(provider=provider)
            
            ai_result = integrator.analyze_document(
                mask_result.masked,
                document_type='financial'
            )
            
            if ai_result.success:
                ai_file = output_dir / f"{base_name}_ai_analysis.json"
                try:
                    parsed = json.loads(ai_result.content)
                    save_output(parsed, ai_file, "json")
                    print_success("AI 分析完成")
                except json.JSONDecodeError:
                    ai_file = output_dir / f"{base_name}_ai_analysis.txt"
                    save_output(ai_result.content, ai_file, "txt")
                    print_success("AI 分析完成")
            else:
                print_warning(f"AI 分析失敗: {ai_result.error}")
        
        # 生成最終報告
        report = {
            'file': args.file,
            'processed_at': datetime.now().isoformat(),
            'steps': {
                'parsing': {
                    'status': 'success',
                    'pages': pdf_result['total_pages'],
                    'text_length': len(text)
                },
                'masking': {
                    'status': 'success',
                    'masked_count': mask_result.mask_count,
                    'sensitive_types': list(set(item['type_name'] for item in mask_result.sensitive_items))
                },
                'extraction': {
                    'status': 'success' if extraction_result['success'] else 'failed',
                    'method': extraction_result.get('method'),
                    'data': extraction_result.get('data')
                }
            },
            'output_files': {
                'original': str(original_file),
                'masked': str(masked_file),
                'extracted': str(extracted_file)
            }
        }
        
        report_file = output_dir / f"{base_name}_report.json"
        save_output(report, report_file, "json")
        
        print_header("✅ 處理完成")
        print_info(f"所有檔案已儲存至: {output_dir}")
        
        return 0
        
    except PermissionError as e:
        print_error(f"PDF 已加密: {e}")
        parser = PDFParser()
        if parser.default_passwords:
            print_info(f"已嘗試 {len(parser.default_passwords)} 個預設密碼，但都失敗")
            print_warning("請檢查 .env 中的密碼是否正確，或使用 --password 參數手動提供")
        else:
            print_warning("請使用 --password 參數提供密碼，或在 .env 中設定 PDF_DEFAULT_PASSWORDS")
        return 1
    except Exception as e:
        print_error(f"處理失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_validate(args):
    """驗證 JSON 資料"""
    print_header(f"✓ 驗證資料: {args.file}")
    
    if not os.path.exists(args.file):
        print_error(f"檔案不存在: {args.file}")
        return 1
    
    try:
        # 讀取資料
        with open(args.file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 驗證
        validator = SchemaValidator()
        
        if args.schema:
            # 使用指定的 schema
            with open(args.schema, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            result = validator.validate(data, schema)
        else:
            # 自動偵測類型並驗證
            doc_type = data.get('document_type', 'unknown')
            result = validator.validate_by_type(data, doc_type)
        
        if result['valid']:
            print_success("驗證通過")
            return 0
        else:
            print_error("驗證失敗")
            for error in result['errors']:
                print(f"  - {error}")
            return 1
        
    except Exception as e:
        print_error(f"驗證失敗: {e}")
        return 1


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='Task Service CLI - PDF 文件處理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 解析 PDF
  %(prog)s parse document.pdf
  
  # 解析有密碼的 PDF
  %(prog)s parse document.pdf --password A123456789
  
  # 遮罩個資並儲存
  %(prog)s mask document.pdf --output masked.txt
  
  # AI 分析
  %(prog)s analyze document.pdf --provider openai
  
  # 完整處理流程
  %(prog)s process document.pdf --ai --validate
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用指令')
    
    # parse 指令
    parse_parser = subparsers.add_parser('parse', help='解析 PDF 文件')
    parse_parser.add_argument('file', help='PDF 檔案路徑')
    parse_parser.add_argument('--password', '-p', help='PDF 密碼')
    parse_parser.add_argument('--output', '-o', help='輸出檔案路徑')
    
    # mask 指令
    mask_parser = subparsers.add_parser('mask', help='遮罩個資')
    mask_parser.add_argument('file', help='PDF 檔案路徑')
    mask_parser.add_argument('--password', '-p', help='PDF 密碼')
    mask_parser.add_argument('--output', '-o', help='輸出檔案路徑')
    mask_parser.add_argument('--types', '-t', help='遮罩類型（逗號分隔）')
    mask_parser.add_argument('--report', '-r', help='詳細報告路徑（JSON）')
    
    # analyze 指令
    analyze_parser = subparsers.add_parser('analyze', help='AI 分析文件')
    analyze_parser.add_argument('file', help='PDF 檔案路徑')
    analyze_parser.add_argument('--password', '-p', help='PDF 密碼')
    analyze_parser.add_argument('--provider', default='openai', choices=['openai', 'claude'], help='AI 服務提供者')
    analyze_parser.add_argument('--model', help='AI 模型')
    analyze_parser.add_argument('--doc-type', default='financial', help='文件類型')
    analyze_parser.add_argument('--instructions', help='額外指示')
    analyze_parser.add_argument('--no-mask', action='store_true', help='不遮罩個資')
    analyze_parser.add_argument('--output', '-o', help='輸出檔案路徑')
    
    # process 指令
    process_parser = subparsers.add_parser('process', help='完整處理流程')
    process_parser.add_argument('file', help='PDF 檔案路徑')
    process_parser.add_argument('--password', '-p', help='PDF 密碼')
    process_parser.add_argument('--output', '-o', default='output', help='輸出目錄')
    process_parser.add_argument('--ai', action='store_true', help='啟用 AI 分析')
    process_parser.add_argument('--provider', default='openai', choices=['openai', 'claude'], help='AI 服務提供者')
    process_parser.add_argument('--validate', action='store_true', help='驗證提取結果')
    
    # validate 指令
    validate_parser = subparsers.add_parser('validate', help='驗證 JSON 資料')
    validate_parser.add_argument('file', help='JSON 檔案路徑')
    validate_parser.add_argument('--schema', '-s', help='Schema 檔案路徑')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 執行對應指令
    commands = {
        'parse': cmd_parse,
        'mask': cmd_mask,
        'analyze': cmd_analyze,
        'process': cmd_process,
        'validate': cmd_validate
    }
    
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())

