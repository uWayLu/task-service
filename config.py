"""
配置檔案
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基礎配置"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    DELETE_AFTER_PROCESS = os.getenv('DELETE_AFTER_PROCESS', 'true').lower() == 'true'
    
    # PDF 處理設定
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # 文件類型
    DOCUMENT_TYPES = {
        'bank_statement': '銀行對帳單',
        'credit_card': '信用卡帳單',
        'transaction_notice': '交易通知'
    }


class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    FLASK_ENV = 'production'


# 根據環境變數選擇配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """取得配置"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])

