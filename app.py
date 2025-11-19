"""
Task Service API - Gmail Webhook 財務文件處理服務
接收來自 Gmail Apps Script 的 webhook，處理財務相關 PDF 文件

模組化架構：使用 Blueprint 組織路由，方便未來擴展
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


def create_app():
    """
    應用程式工廠模式
    建立並配置 Flask 應用
    
    Returns:
        Flask: 配置好的 Flask 應用實例
    """
    app = Flask(__name__)
    
    # ========== 基本配置 ==========
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', './uploads')
    
    # 啟用 CORS
    CORS(app)
    
    # 確保上傳資料夾存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # ========== 註冊 Blueprint ==========
    # 所有 /api/* 的路由都在 api/ 資料夾中定義
    from api import api_bp
    app.register_blueprint(api_bp)
    
    # ========== 根路由 ==========
    @app.route('/', methods=['GET'])
    def index():
        """
        API 首頁 - 顯示服務資訊和可用端點
        """
        return jsonify({
            'status': 'success',
            'message': 'Task Service API is running',
            'version': '1.0.0',
            'architecture': 'modular (Blueprint)',
            'endpoints': {
                'root': '/',
                'health': '/api/health',
                'ping': '/api/ping',
                'webhook': '/api/webhook/gmail',
                'webhook_test': '/api/webhook/test',
                'document_types': '/api/documents/types',
                'document_stats': '/api/documents/stats'
            },
            'docs': {
                'readme': 'README.md',
                'quickstart': 'QUICKSTART.md',
                'deployment': 'DEPLOYMENT.md'
            }
        })
    
    # ========== 全域錯誤處理 ==========
    @app.errorhandler(413)
    def too_large(e):
        """檔案過大錯誤處理"""
        return jsonify({
            'status': 'error',
            'message': '檔案大小超過限制（最大 16MB）'
        }), 413
    
    @app.errorhandler(404)
    def not_found(e):
        """404 錯誤處理"""
        return jsonify({
            'status': 'error',
            'message': '找不到該端點',
            'tip': '訪問根路徑 / 查看所有可用端點'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        """方法不允許錯誤處理"""
        return jsonify({
            'status': 'error',
            'message': 'HTTP 方法不允許'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(e):
        """內部錯誤處理"""
        app.logger.error(f'伺服器內部錯誤: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': '伺服器內部錯誤'
        }), 500
    
    return app


# ========== 應用程式入口 ==========
if __name__ == '__main__':
    # 建立應用實例
    app = create_app()
    
    # 從環境變數取得配置
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    
    # 啟動訊息
    print("=" * 60)
    print("🚀 Task Service API")
    print("=" * 60)
    print(f"📍 運行位址: http://localhost:{port}")
    print(f"🔧 除錯模式: {'開啟' if debug else '關閉'}")
    print(f"📂 上傳目錄: {app.config['UPLOAD_FOLDER']}")
    print("📦 架構模式: 模組化 (Blueprint)")
    print("=" * 60)
    print("📚 可用端點:")
    print("   - GET  /                    (服務資訊)")
    print("   - GET  /api/health          (健康檢查)")
    print("   - GET  /api/ping            (快速測試)")
    print("   - POST /api/webhook/gmail   (Gmail Webhook)")
    print("   - GET  /api/documents/types (文件類型列表)")
    print("=" * 60)
    print("按 Ctrl+C 停止服務\n")
    
    # 啟動應用
    app.run(host='0.0.0.0', port=port, debug=debug)
