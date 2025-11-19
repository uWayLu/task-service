"""
文件瀏覽 API
提供透過 HTTP 訪問 Markdown 文件的功能
"""
import os
from pathlib import Path
from flask import jsonify, render_template_string, send_file, abort
from . import api_bp

# Markdown 渲染（需要安裝 markdown 套件）
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


# 簡單的 HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Task Service 文件</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: #2c3e50;
            color: white;
            padding: 20px 0;
            margin-bottom: 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        header .container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        header h1 {
            font-size: 24px;
        }
        .back-link {
            color: #3498db;
            text-decoration: none;
            font-size: 14px;
        }
        .back-link:hover {
            text-decoration: underline;
        }
        .content {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .content h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .content h2 {
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        .content h3 {
            color: #555;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        .content p {
            margin-bottom: 15px;
        }
        .content ul, .content ol {
            margin-left: 20px;
            margin-bottom: 15px;
        }
        .content li {
            margin-bottom: 5px;
        }
        .content code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .content pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin-bottom: 15px;
        }
        .content pre code {
            background: none;
            color: inherit;
            padding: 0;
        }
        .content blockquote {
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            color: #555;
            font-style: italic;
        }
        .content table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .content table th,
        .content table td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        .content table th {
            background: #3498db;
            color: white;
            font-weight: bold;
        }
        .content table tr:nth-child(even) {
            background: #f9f9f9;
        }
        .content a {
            color: #3498db;
            text-decoration: none;
        }
        .content a:hover {
            text-decoration: underline;
        }
        footer {
            text-align: center;
            padding: 20px;
            color: #777;
            font-size: 14px;
        }
        .error {
            background: #e74c3c;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .warning {
            background: #f39c12;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>📚 {{ title }}</h1>
            <a href="/api/docs" class="back-link">← 返回文件列表</a>
        </div>
    </header>
    
    <div class="container">
        <div class="content">
            {{ content|safe }}
        </div>
    </div>
    
    <footer>
        <p>Task Service API © 2024</p>
    </footer>
</body>
</html>
"""

# 文件列表模板
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文件中心 - Task Service</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }
        header p {
            font-size: 16px;
            opacity: 0.9;
        }
        .docs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .doc-card {
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none;
            color: inherit;
            display: block;
        }
        .doc-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }
        .doc-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 20px;
        }
        .doc-card p {
            color: #666;
            font-size: 14px;
            margin-bottom: 15px;
        }
        .doc-card .meta {
            font-size: 12px;
            color: #999;
        }
        .section-title {
            font-size: 24px;
            color: #2c3e50;
            margin: 40px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        footer {
            text-align: center;
            padding: 20px;
            color: #777;
            font-size: 14px;
        }
        .icon {
            font-size: 24px;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>📚 Task Service 文件中心</h1>
            <p>所有專案文件都在這裡</p>
        </div>
    </header>
    
    <div class="container">
        <h2 class="section-title">📖 核心文件</h2>
        <div class="docs-grid">
            {% for doc in docs %}
            <a href="/api/docs/{{ doc.filename }}" class="doc-card">
                <h3>{{ doc.icon }} {{ doc.title }}</h3>
                <p>{{ doc.description }}</p>
                <div class="meta">{{ doc.filename }}</div>
            </a>
            {% endfor %}
        </div>
        
        <h2 class="section-title">🔗 快速連結</h2>
        <div class="docs-grid">
            <a href="/" class="doc-card">
                <h3>🏠 API 首頁</h3>
                <p>查看 API 服務資訊</p>
            </a>
            <a href="/api/health" class="doc-card">
                <h3>💚 健康檢查</h3>
                <p>檢查服務狀態</p>
            </a>
            <a href="/api/documents/types" class="doc-card">
                <h3>📄 文件類型</h3>
                <p>查看支援的文件類型</p>
            </a>
        </div>
    </div>
    
    <footer>
        <p>Task Service API © 2024 | <a href="https://github.com" style="color: #667eea;">GitHub</a></p>
    </footer>
</body>
</html>
"""


@api_bp.route('/docs', methods=['GET'])
def docs_index():
    """
    文件列表首頁
    顯示所有可用的文件
    """
    docs = [
        {
            'filename': 'README.md',
            'title': '專案說明',
            'description': '快速了解專案功能與使用方式',
            'icon': '📘'
        },
        {
            'filename': 'QUICKSTART.md',
            'title': '快速開始',
            'description': '5 分鐘快速啟動指南',
            'icon': '🚀'
        },
        {
            'filename': 'HOW_TO_ADD_API.md',
            'title': 'API 開發指南',
            'description': '如何新增和擴展 API 端點',
            'icon': '🔧'
        },
        {
            'filename': 'PDF_TESTING.md',
            'title': 'PDF 測試指南',
            'description': '如何測試 PDF 解析功能',
            'icon': '🧪'
        },
        {
            'filename': 'DEPLOYMENT.md',
            'title': '部署指南',
            'description': '各種環境的部署方式',
            'icon': '☁️'
        },
        {
            'filename': 'FILE_ORGANIZATION.md',
            'title': '檔案組織',
            'description': '專案檔案結構說明',
            'icon': '📁'
        },
        {
            'filename': 'FLASK_PROJECT_STRUCTURES.md',
            'title': 'Flask 專案結構',
            'description': 'Flask 最佳實踐與結構演進',
            'icon': '🏗️'
        },
        {
            'filename': 'CHANGELOG.md',
            'title': '更新日誌',
            'description': '版本歷史與變更記錄',
            'icon': '📝'
        },
    ]
    
    return render_template_string(INDEX_TEMPLATE, docs=docs)


@api_bp.route('/docs/<path:filename>', methods=['GET'])
def view_doc(filename):
    """
    查看特定文件
    支援 Markdown 渲染
    
    Args:
        filename: 文件檔名（如 README.md）
    """
    # 安全性：只允許 .md 檔案
    if not filename.endswith('.md'):
        return jsonify({
            'status': 'error',
            'message': '只支援 Markdown 檔案'
        }), 400
    
    # 檢查檔案位置（支援根目錄和 docs/ 目錄）
    root_dir = Path(__file__).parent.parent
    possible_paths = [
        root_dir / filename,           # 根目錄
        root_dir / 'docs' / filename,  # docs 目錄
    ]
    
    doc_path = None
    for path in possible_paths:
        if path.exists() and path.is_file():
            doc_path = path
            break
    
    if not doc_path:
        abort(404)
    
    # 讀取檔案
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'讀取檔案失敗: {str(e)}'
        }), 500
    
    # 渲染 Markdown
    if MARKDOWN_AVAILABLE:
        # 使用 markdown 套件渲染
        html_content = markdown.markdown(
            content,
            extensions=[
                'fenced_code',      # 程式碼區塊
                'tables',           # 表格
                'toc',              # 目錄
                'nl2br',            # 換行
            ]
        )
    else:
        # 如果沒有 markdown 套件，顯示純文字
        html_content = f'<pre>{content}</pre>'
        html_content += '<div class="warning">⚠️ 未安裝 markdown 套件，顯示原始內容。執行 <code>pip install markdown</code> 以啟用格式化顯示。</div>'
    
    # 取得標題
    title = filename.replace('.md', '').replace('_', ' ').title()
    
    return render_template_string(
        HTML_TEMPLATE,
        title=title,
        content=html_content
    )


@api_bp.route('/docs/raw/<path:filename>', methods=['GET'])
def raw_doc(filename):
    """
    下載原始 Markdown 檔案
    
    Args:
        filename: 文件檔名
    """
    if not filename.endswith('.md'):
        return jsonify({
            'status': 'error',
            'message': '只支援 Markdown 檔案'
        }), 400
    
    root_dir = Path(__file__).parent.parent
    possible_paths = [
        root_dir / filename,
        root_dir / 'docs' / filename,
    ]
    
    doc_path = None
    for path in possible_paths:
        if path.exists() and path.is_file():
            doc_path = path
            break
    
    if not doc_path:
        abort(404)
    
    return send_file(
        doc_path,
        mimetype='text/markdown',
        as_attachment=True,
        download_name=filename
    )

