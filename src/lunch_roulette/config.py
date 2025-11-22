"""
アプリケーション設定管理モジュール
"""

import os
from typing import Dict, Any


class Config:
    """基本設定クラス"""
    
    # Flask設定
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # データベース設定
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'cache.db')
    
    # API設定
    WEATHERAPI_KEY = os.environ.get('WEATHERAPI_KEY', 'weather_api_key')  # WeatherAPI.com APIキー
    HOTPEPPER_API_KEY = os.environ.get('HOTPEPPER_API_KEY')
    
    # キャッシュ設定
    CACHE_TTL_MINUTES = int(os.environ.get('CACHE_TTL_MINUTES', '10'))
    
    # 位置情報設定
    DEFAULT_LATITUDE = float(os.environ.get('DEFAULT_LATITUDE', '35.6812'))
    DEFAULT_LONGITUDE = float(os.environ.get('DEFAULT_LONGITUDE', '139.7671'))
    
    # レストラン検索設定
    SEARCH_RADIUS_KM = float(os.environ.get('SEARCH_RADIUS_KM', '1.0'))
    MAX_BUDGET_YEN = int(os.environ.get('MAX_BUDGET_YEN', '1200'))


class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True


class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False


class TestConfig(Config):
    """テスト環境設定"""
    TESTING = True
    DATABASE_PATH = ':memory:'


# 設定マップ
config_map: Dict[str, Any] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> type:
    """設定クラスを取得"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config_map.get(config_name, DevelopmentConfig)