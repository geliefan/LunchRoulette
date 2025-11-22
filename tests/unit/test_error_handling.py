#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
エラーハンドリングの統合テスト
様々なエラー状況での動作をテスト
"""

import pytest
import tempfile
import os
import requests
from unittest.mock import patch, Mock, MagicMock
from lunch_roulette.services.cache_service import CacheService
from lunch_roulette.services.location_service import LocationService
from lunch_roulette.services.weather_service import WeatherService
from lunch_roulette.services.restaurant_service import RestaurantService
from lunch_roulette.utils.distance_calculator import DistanceCalculator
from lunch_roulette.utils.error_handler import ErrorHandler


class TestErrorHandling:
    """エラーハンドリングの統合テスト"""

    @pytest.fixture
    def temp_db_path(self):
        """テスト用の一時データベースファイルパス"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            temp_path = temp_file.name
        yield temp_path
        # テスト後にファイルを削除（Windowsでの権限エラー対策）
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        except (PermissionError, OSError):
            # Windows環境でファイルが使用中の場合は無視
            pass

    @pytest.fixture
    def cache_service(self, temp_db_path):
        """テスト用CacheServiceインスタンス"""
        return CacheService(db_path=temp_db_path)

    def test_cache_service_database_error_handling(self, temp_db_path):
        """CacheService データベースエラーハンドリングテスト"""
        cache_service = CacheService(db_path='/invalid/path/cache.db')

        # データベースアクセスエラー時の動作確認
        result = cache_service.set_cached_data('test_key', {'data': 'test'})
        assert result is False

        retrieved_data = cache_service.get_cached_data('test_key')
        assert retrieved_data is None

        delete_result = cache_service.delete_cached_data('test_key')
        assert delete_result is False

    def test_cache_service_serialization_error_handling(self, cache_service):
        """CacheService シリアライゼーションエラーハンドリングテスト"""
        # シリアライズできないオブジェクト
        def unserializable_data(x):
            return x  # 関数オブジェクト

        with pytest.raises(ValueError, match="データのシリアライズに失敗"):
            cache_service.serialize_data(unserializable_data)

        # 無効なJSON文字列
        with pytest.raises(ValueError, match="データのデシリアライズに失敗"):
            cache_service.deserialize_data("invalid json {")

    @patch('location_service.requests.get')
    def test_location_service_network_error_handling(self, mock_get, cache_service):
        """LocationService ネットワークエラーハンドリングテスト"""
        location_service = LocationService(cache_service=cache_service)

        # ネットワークエラーをシミュレート
        mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")

        result = location_service.get_location_from_ip('192.168.1.1')

        # デフォルト位置が返されることを確認
        assert result['source'] == 'default'
        assert result['city'] == '東京'
        assert result['latitude'] == 35.6812
        assert result['longitude'] == 139.7671

    @patch('location_service.requests.get')
    def test_location_service_api_error_handling(self, mock_get, cache_service):
        """LocationService APIエラーハンドリングテスト"""
        location_service = LocationService(cache_service=cache_service)

        # APIエラーレスポンスをシミュレート
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'error': True,
            'reason': 'Invalid IP address'
        }
        mock_get.return_value = mock_response

        result = location_service.get_location_from_ip('invalid.ip')

        # デフォルト位置が返されることを確認
        assert result['source'] == 'default'

    @patch('location_service.requests.get')
    def test_location_service_rate_limit_handling(self, mock_get, cache_service):
        """LocationService レート制限ハンドリングテスト"""
        location_service = LocationService(cache_service=cache_service)

        # 事前にキャッシュデータを設定
        cache_service.generate_cache_key('location', ip='192.168.1.1')
        old_data = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '渋谷区',
            'source': 'ipapi.co'
        }

        # 期限切れキャッシュを直接データベースに挿入
        with patch('lunch_roulette.services.location_service.get_db_connection') as mock_get_db_connection:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_get_db_connection.return_value.__enter__.return_value = mock_conn
            mock_conn.execute.return_value = mock_cursor
            mock_cursor.fetchone.return_value = {
                'data': cache_service.serialize_data(old_data)
            }

            # レート制限エラーをシミュレート
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")
            mock_get.return_value = mock_response

            result = location_service.get_location_from_ip('192.168.1.1')

            # フォールバックキャッシュデータが返されることを確認
            assert result['source'] == 'fallback_cache'

    @patch('weather_service.requests.get')
    def test_weather_service_api_error_handling(self, mock_get, cache_service):
        """WeatherService APIエラーハンドリングテスト"""
        weather_service = WeatherService(api_key="test_key", cache_service=cache_service)

        # 認証エラーをシミュレート
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_get.return_value = mock_response

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # デフォルト天気情報が返されることを確認
        assert result['source'] == 'default'
        assert result['temperature'] == 20.0
        assert result['condition'] == 'clear'

    def test_weather_service_no_api_key_handling(self, cache_service):
        """WeatherService APIキーなしハンドリングテスト"""
        weather_service = WeatherService(api_key=None, cache_service=cache_service)

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # デフォルト天気情報が返されることを確認
        assert result['source'] == 'default'

    @patch('restaurant_service.requests.get')
    def test_restaurant_service_api_error_handling(self, mock_get, cache_service):
        """RestaurantService APIエラーハンドリングテスト"""
        restaurant_service = RestaurantService(api_key="test_key", cache_service=cache_service)

        # HTTPエラーをシミュレート
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Internal Server Error")
        mock_get.return_value = mock_response

        result = restaurant_service.search_restaurants(35.6812, 139.7671)

        # 空のリストが返されることを確認
        assert result == []

    def test_restaurant_service_no_api_key_handling(self, cache_service):
        """RestaurantService APIキーなしハンドリングテスト"""
        restaurant_service = RestaurantService(api_key=None, cache_service=cache_service)

        result = restaurant_service.search_restaurants(35.6812, 139.7671)

        # 空のリストが返されることを確認
        assert result == []

    def test_distance_calculator_invalid_input_handling(self):
        """DistanceCalculator 無効入力ハンドリングテスト"""
        error_handler = ErrorHandler()
        distance_calculator = DistanceCalculator(error_handler=error_handler)

        # 無効な座標での計算
        with pytest.raises(ValueError):
            distance_calculator.calculate_distance(95.0, 139.0, 35.0, 139.0)

        with pytest.raises(ValueError):
            distance_calculator.calculate_distance("invalid", 139.0, 35.0, 139.0)

    def test_distance_calculator_calculation_error_handling(self):
        """DistanceCalculator 計算エラーハンドリングテスト"""
        mock_error_handler = Mock()
        mock_error_handler.handle_distance_calculation_error.return_value = {
            'message': 'Distance calculation error',
            'fallback_distance': 0.5
        }

        distance_calculator = DistanceCalculator(error_handler=mock_error_handler)

        # mathモジュールでエラーを発生させる
        with patch('math.sin', side_effect=Exception("Math error")):
            result = distance_calculator.calculate_distance(35.0, 139.0, 36.0, 140.0)

            # エラーハンドラーが呼ばれ、概算距離が返されることを確認
            mock_error_handler.handle_distance_calculation_error.assert_called_once()
            assert isinstance(result, float)
            assert result > 0

    def test_distance_calculator_walking_distance_error_handling(self):
        """DistanceCalculator 徒歩距離計算エラーハンドリングテスト"""
        mock_error_handler = Mock()
        mock_error_handler.handle_distance_calculation_error.return_value = {
            'message': 'Walking distance calculation error'
        }

        distance_calculator = DistanceCalculator(error_handler=mock_error_handler)

        # calculate_distanceでエラーを発生させる
        with patch.object(distance_calculator, 'calculate_distance', side_effect=Exception("Distance error")):
            result = distance_calculator.calculate_walking_distance(35.0, 139.0, 36.0, 140.0)

            # エラー時にデフォルト値が返されることを確認
            assert result['distance_km'] == 0.5
            assert result['distance_m'] == 500
            assert result['walking_time_minutes'] == 8
            assert 'error_info' in result

    def test_error_handler_distance_calculation_error(self):
        """ErrorHandler 距離計算エラーハンドリングテスト"""
        error_handler = ErrorHandler()

        test_error = ValueError("Test distance calculation error")
        result = error_handler.handle_distance_calculation_error(test_error)

        assert 'message' in result
        assert 'error_type' in result
        assert 'timestamp' in result
        assert result['error_type'] == 'ValueError'

    def test_multiple_service_error_cascade(self, cache_service):
        """複数サービスエラーカスケードテスト"""
        # すべてのサービスでエラーが発生する状況をシミュレート

        # LocationService: ネットワークエラー
        with patch('lunch_roulette.services.location_service.requests.get', side_effect=requests.exceptions.ConnectionError("Network error")):
            location_service = LocationService(cache_service=cache_service)
            location_result = location_service.get_location_from_ip('192.168.1.1')
            assert location_result['source'] == 'default'

        # WeatherService: APIキーなし
        weather_service = WeatherService(api_key=None, cache_service=cache_service)
        weather_result = weather_service.get_current_weather(35.6812, 139.7671)
        assert weather_result['source'] == 'default'

        # RestaurantService: APIキーなし
        restaurant_service = RestaurantService(api_key=None, cache_service=cache_service)
        restaurant_result = restaurant_service.search_restaurants(35.6812, 139.7671)
        assert restaurant_result == []

        # DistanceCalculator: 計算エラー
        mock_error_handler = Mock()
        mock_error_handler.handle_distance_calculation_error.return_value = {
            'message': 'Error'
        }
        distance_calculator = DistanceCalculator(error_handler=mock_error_handler)

        with patch('math.sin', side_effect=Exception("Math error")):
            distance_result = distance_calculator.calculate_distance(35.0, 139.0, 36.0, 140.0)
            assert isinstance(distance_result, float)

    def test_graceful_degradation_scenario(self, cache_service):
        """グレースフルデグラデーションシナリオテスト"""
        # 一部のサービスが利用できない状況での動作確認

        # LocationService: 成功（キャッシュから取得）
        location_service = LocationService(cache_service=cache_service)
        cache_key = cache_service.generate_cache_key('location', ip='auto')
        cache_service.set_cached_data(cache_key, {
            'latitude': 35.6812,
            'longitude': 139.7671,
            'city': '東京',
            'source': 'ipapi.co'
        })
        location_result = location_service.get_location_from_ip()
        assert location_result['source'] == 'ipapi.co'

        # WeatherService: APIエラー → デフォルト天気
        with patch('lunch_roulette.services.weather_service.requests.get', side_effect=requests.exceptions.HTTPError("API Error")):
            weather_service = WeatherService(api_key="test_key", cache_service=cache_service)
            weather_result = weather_service.get_current_weather(35.6812, 139.7671)
            assert weather_result['source'] == 'default'

        # RestaurantService: APIエラー → 空リスト
        with patch('lunch_roulette.services.restaurant_service.requests.get', side_effect=requests.exceptions.HTTPError("API Error")):
            restaurant_service = RestaurantService(api_key="test_key", cache_service=cache_service)
            restaurant_result = restaurant_service.search_restaurants(35.6812, 139.7671)
            assert restaurant_result == []

        # システム全体としては部分的に動作することを確認
        assert location_result is not None
        assert weather_result is not None
        assert restaurant_result is not None  # 空リストでもNone ではない


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
