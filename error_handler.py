#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ErrorHandler - エラーハンドリングとメッセージ管理クラス
アプリケーション全体のエラー処理とユーザーフレンドリーなメッセージ表示を提供

このクラスは以下の機能を提供します:
- API エラーの分類と適切なメッセージ生成
- フォールバック機能の管理
- エラーログの記録
- ユーザー向けエラーメッセージの国際化対応
"""

import logging
from typing import Dict, Optional, Any, Tuple
from enum import Enum
from datetime import datetime


class ErrorType(Enum):
    """エラータイプの定義"""
    API_RATE_LIMIT = "api_rate_limit"
    API_AUTH_ERROR = "api_auth_error"
    API_NETWORK_ERROR = "api_network_error"
    API_TIMEOUT = "api_timeout"
    DATA_PARSING_ERROR = "data_parsing_error"
    LOCATION_NOT_FOUND = "location_not_found"
    RESTAURANT_NOT_FOUND = "restaurant_not_found"
    DISTANCE_CALCULATION_ERROR = "distance_calculation_error"
    CACHE_ERROR = "cache_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorHandler:
    """
    アプリケーション全体のエラーハンドリングを管理するクラス
    
    エラーの分類、ログ記録、ユーザーフレンドリーなメッセージ生成、
    フォールバック機能の提供を行う。
    """
    
    # エラーメッセージのマッピング
    ERROR_MESSAGES = {
        ErrorType.API_RATE_LIMIT: {
            'user_message': 'APIの利用制限に達しました。キャッシュされたデータを使用します。',
            'suggestion': 'しばらく時間を置いてから再度お試しください。',
            'severity': 'warning'
        },
        ErrorType.API_AUTH_ERROR: {
            'user_message': 'API認証エラーが発生しました。',
            'suggestion': 'システム管理者にお問い合わせください。',
            'severity': 'error'
        },
        ErrorType.API_NETWORK_ERROR: {
            'user_message': 'ネットワーク接続エラーが発生しました。',
            'suggestion': 'インターネット接続を確認してください。',
            'severity': 'warning'
        },
        ErrorType.API_TIMEOUT: {
            'user_message': 'APIの応答がタイムアウトしました。',
            'suggestion': 'しばらく時間を置いてから再度お試しください。',
            'severity': 'warning'
        },
        ErrorType.DATA_PARSING_ERROR: {
            'user_message': 'データの処理中にエラーが発生しました。',
            'suggestion': 'デフォルトデータを使用します。',
            'severity': 'warning'
        },
        ErrorType.LOCATION_NOT_FOUND: {
            'user_message': '位置情報を取得できませんでした。',
            'suggestion': '東京駅を基準に検索します。',
            'severity': 'info'
        },
        ErrorType.RESTAURANT_NOT_FOUND: {
            'user_message': '近くにレストランが見つかりませんでした。',
            'suggestion': '検索範囲を広げるか、条件を変更してお試しください。',
            'severity': 'info'
        },
        ErrorType.DISTANCE_CALCULATION_ERROR: {
            'user_message': '距離の計算中にエラーが発生しました。',
            'suggestion': '概算距離を表示します。',
            'severity': 'warning'
        },
        ErrorType.CACHE_ERROR: {
            'user_message': 'キャッシュシステムでエラーが発生しました。',
            'suggestion': 'データの取得に時間がかかる場合があります。',
            'severity': 'warning'
        },
        ErrorType.UNKNOWN_ERROR: {
            'user_message': '予期しないエラーが発生しました。',
            'suggestion': 'しばらく時間を置いてから再度お試しください。',
            'severity': 'error'
        }
    }
    
    def __init__(self, logger_name: str = 'lunch_roulette'):
        """
        ErrorHandlerを初期化
        
        Args:
            logger_name (str): ロガー名
        """
        self.logger = logging.getLogger(logger_name)
        self.error_count = {}  # エラー発生回数の記録
    
    def handle_api_error(self, service_name: str, error: Exception, 
                        fallback_available: bool = False) -> Tuple[ErrorType, Dict[str, Any]]:
        """
        API エラーを処理し、適切なエラータイプとメッセージを返す
        
        Args:
            service_name (str): サービス名（例: "weather", "restaurant", "location"）
            error (Exception): 発生したエラー
            fallback_available (bool): フォールバックデータが利用可能かどうか
            
        Returns:
            tuple: (エラータイプ, エラー情報辞書)
        """
        error_type = self._classify_error(error)
        error_info = self._create_error_info(service_name, error_type, error, fallback_available)
        
        # エラーログを記録
        self._log_error(service_name, error_type, error, fallback_available)
        
        # エラー発生回数を記録
        self._increment_error_count(error_type)
        
        return error_type, error_info
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """
        エラーを分類してErrorTypeを返す
        
        Args:
            error (Exception): 発生したエラー
            
        Returns:
            ErrorType: 分類されたエラータイプ
        """
        import requests
        
        if isinstance(error, requests.exceptions.HTTPError):
            if hasattr(error, 'response') and error.response.status_code == 429:
                return ErrorType.API_RATE_LIMIT
            elif hasattr(error, 'response') and error.response.status_code == 401:
                return ErrorType.API_AUTH_ERROR
            else:
                return ErrorType.API_NETWORK_ERROR
        elif isinstance(error, requests.exceptions.Timeout):
            return ErrorType.API_TIMEOUT
        elif isinstance(error, requests.exceptions.RequestException):
            return ErrorType.API_NETWORK_ERROR
        elif isinstance(error, (ValueError, KeyError)):
            return ErrorType.DATA_PARSING_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
    def _create_error_info(self, service_name: str, error_type: ErrorType, 
                          error: Exception, fallback_available: bool) -> Dict[str, Any]:
        """
        エラー情報辞書を作成
        
        Args:
            service_name (str): サービス名
            error_type (ErrorType): エラータイプ
            error (Exception): 発生したエラー
            fallback_available (bool): フォールバックデータが利用可能かどうか
            
        Returns:
            dict: エラー情報辞書
        """
        error_config = self.ERROR_MESSAGES.get(error_type, self.ERROR_MESSAGES[ErrorType.UNKNOWN_ERROR])
        
        return {
            'error_type': error_type.value,
            'service_name': service_name,
            'user_message': error_config['user_message'],
            'suggestion': error_config['suggestion'],
            'severity': error_config['severity'],
            'fallback_available': fallback_available,
            'timestamp': datetime.now().isoformat(),
            'technical_details': str(error)
        }
    
    def _log_error(self, service_name: str, error_type: ErrorType, 
                   error: Exception, fallback_available: bool) -> None:
        """
        エラーログを記録
        
        Args:
            service_name (str): サービス名
            error_type (ErrorType): エラータイプ
            error (Exception): 発生したエラー
            fallback_available (bool): フォールバックデータが利用可能かどうか
        """
        log_message = (
            f"[{service_name}] {error_type.value}: {str(error)} "
            f"(フォールバック利用可能: {fallback_available})"
        )
        
        if error_type in [ErrorType.API_AUTH_ERROR, ErrorType.UNKNOWN_ERROR]:
            self.logger.error(log_message)
        elif error_type in [ErrorType.API_RATE_LIMIT, ErrorType.API_NETWORK_ERROR, 
                           ErrorType.API_TIMEOUT, ErrorType.DATA_PARSING_ERROR]:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _increment_error_count(self, error_type: ErrorType) -> None:
        """
        エラー発生回数をカウント
        
        Args:
            error_type (ErrorType): エラータイプ
        """
        if error_type not in self.error_count:
            self.error_count[error_type] = 0
        self.error_count[error_type] += 1
    
    def get_error_statistics(self) -> Dict[str, int]:
        """
        エラー統計情報を取得
        
        Returns:
            dict: エラータイプ別の発生回数
        """
        return {error_type.value: count for error_type, count in self.error_count.items()}
    
    def create_user_friendly_message(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        ユーザーフレンドリーなエラーメッセージを作成
        
        Args:
            error_info (dict): エラー情報辞書
            
        Returns:
            dict: ユーザー向けメッセージ
        """
        return {
            'message': error_info['user_message'],
            'suggestion': error_info['suggestion'],
            'severity': error_info['severity'],
            'fallback_used': error_info['fallback_available'],
            'service_affected': error_info['service_name']
        }
    
    def handle_location_error(self, error: Exception, fallback_available: bool = True) -> Dict[str, Any]:
        """
        位置情報エラーを処理
        
        Args:
            error (Exception): 発生したエラー
            fallback_available (bool): フォールバックデータが利用可能かどうか
            
        Returns:
            dict: エラー処理結果
        """
        error_type, error_info = self.handle_api_error('location', error, fallback_available)
        
        # 位置情報特有の処理
        if not fallback_available:
            error_info['user_message'] = '位置情報を取得できませんでした。東京駅を基準に検索します。'
            error_info['suggestion'] = 'より正確な結果を得るには、位置情報の許可を有効にしてください。'
        
        return self.create_user_friendly_message(error_info)
    
    def handle_restaurant_error(self, error: Exception, fallback_available: bool = False) -> Dict[str, Any]:
        """
        レストラン検索エラーを処理
        
        Args:
            error (Exception): 発生したエラー
            fallback_available (bool): フォールバックデータが利用可能かどうか
            
        Returns:
            dict: エラー処理結果
        """
        error_type, error_info = self.handle_api_error('restaurant', error, fallback_available)
        
        # レストラン検索特有の処理
        if error_type == ErrorType.API_RATE_LIMIT and fallback_available:
            error_info['user_message'] = 'API制限のため、以前の検索結果を表示しています。'
            error_info['suggestion'] = '最新の情報を取得するには、しばらく時間を置いてください。'
        
        return self.create_user_friendly_message(error_info)
    
    def handle_weather_error(self, error: Exception, fallback_available: bool = True) -> Dict[str, Any]:
        """
        天気情報エラーを処理
        
        Args:
            error (Exception): 発生したエラー
            fallback_available (bool): フォールバックデータが利用可能かどうか
            
        Returns:
            dict: エラー処理結果
        """
        error_type, error_info = self.handle_api_error('weather', error, fallback_available)
        
        # 天気情報特有の処理
        if not fallback_available:
            error_info['user_message'] = '天気情報を取得できませんでした。標準的な天気情報を表示します。'
            error_info['suggestion'] = '実際の天気は異なる場合があります。'
        
        return self.create_user_friendly_message(error_info)
    
    def handle_distance_calculation_error(self, error: Exception) -> Dict[str, Any]:
        """
        距離計算エラーを処理
        
        Args:
            error (Exception): 発生したエラー
            
        Returns:
            dict: エラー処理結果
        """
        error_info = {
            'error_type': ErrorType.DISTANCE_CALCULATION_ERROR.value,
            'service_name': 'distance_calculator',
            'user_message': '距離の計算中にエラーが発生しました。',
            'suggestion': '概算距離を表示します。',
            'severity': 'warning',
            'fallback_available': True,
            'timestamp': datetime.now().isoformat(),
            'technical_details': str(error)
        }
        
        self._log_error('distance_calculator', ErrorType.DISTANCE_CALCULATION_ERROR, error, True)
        self._increment_error_count(ErrorType.DISTANCE_CALCULATION_ERROR)
        
        return self.create_user_friendly_message(error_info)
    
    def is_critical_error(self, error_type: ErrorType) -> bool:
        """
        クリティカルエラーかどうかを判定
        
        Args:
            error_type (ErrorType): エラータイプ
            
        Returns:
            bool: クリティカルエラーの場合True
        """
        critical_errors = [ErrorType.API_AUTH_ERROR, ErrorType.UNKNOWN_ERROR]
        return error_type in critical_errors
    
    def should_retry(self, error_type: ErrorType) -> bool:
        """
        リトライすべきエラーかどうかを判定
        
        Args:
            error_type (ErrorType): エラータイプ
            
        Returns:
            bool: リトライすべき場合True
        """
        retry_errors = [ErrorType.API_NETWORK_ERROR, ErrorType.API_TIMEOUT]
        return error_type in retry_errors
    
    def get_retry_delay(self, error_type: ErrorType, attempt_count: int) -> int:
        """
        リトライ遅延時間を取得
        
        Args:
            error_type (ErrorType): エラータイプ
            attempt_count (int): 試行回数
            
        Returns:
            int: 遅延時間（秒）
        """
        base_delays = {
            ErrorType.API_NETWORK_ERROR: 5,
            ErrorType.API_TIMEOUT: 10,
            ErrorType.API_RATE_LIMIT: 60
        }
        
        base_delay = base_delays.get(error_type, 5)
        # 指数バックオフ
        return min(base_delay * (2 ** (attempt_count - 1)), 300)  # 最大5分


# 使用例とテスト用コード
if __name__ == '__main__':
    """
    ErrorHandlerのテスト実行
    """
    print("ErrorHandler テスト実行")
    print("=" * 40)
    
    # ErrorHandlerインスタンス作成
    error_handler = ErrorHandler()
    
    # テスト用エラー
    import requests
    
    # レート制限エラーのテスト
    print("1. レート制限エラーテスト:")
    rate_limit_error = requests.exceptions.HTTPError()
    rate_limit_error.response = type('Response', (), {'status_code': 429})()
    
    error_type, error_info = error_handler.handle_api_error('weather', rate_limit_error, True)
    user_message = error_handler.create_user_friendly_message(error_info)
    print(f"   エラータイプ: {error_type.value}")
    print(f"   ユーザーメッセージ: {user_message['message']}")
    print(f"   提案: {user_message['suggestion']}")
    
    # ネットワークエラーのテスト
    print("\n2. ネットワークエラーテスト:")
    network_error = requests.exceptions.ConnectionError("Connection failed")
    
    location_error = error_handler.handle_location_error(network_error, False)
    print(f"   メッセージ: {location_error['message']}")
    print(f"   提案: {location_error['suggestion']}")
    
    # エラー統計の表示
    print("\n3. エラー統計:")
    stats = error_handler.get_error_statistics()
    for error_type, count in stats.items():
        print(f"   {error_type}: {count}回")
    
    print("\nテスト完了")