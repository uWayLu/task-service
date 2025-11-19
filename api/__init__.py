"""
API Blueprint Package
"""
from flask import Blueprint

# 建立 API Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 導入路由（避免循環導入）
from . import health, webhook, document, test

__all__ = ['api_bp']

