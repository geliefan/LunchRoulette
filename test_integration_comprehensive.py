#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
統合テスト
Flask エンドポイント、データベース操作、エラーハンドリングの統合テスト

このテストファイルは以下をカバーします:
- Flask エンドポイントのテストケース
- データベース操作のテストケース
- エラーハンドリングのテストケース
"""

import pytest
import json
import tempfile
import os
import sqlite3
import requests
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

from app import app
from database import init_database, cleanup_expired_cache, get_cache_stats
from cache_service import CacheService
from location_service import LocationService
from weather_service import WeatherService
from restaurant_service import RestaurantService
from distance_calculator import DistanceCalculator
from error_handler import ErrorHandler


class TestComprehensiveIntegration:
    """統合テストクラス"""

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
            pass

    @pytest.fixture
    def cache_service(self, temp_db_path):
        """テスト用CacheServiceインスタンス"""
        init_database(temp_db_path)
        return CacheService(db_path=temp_db_path)

    @pytest.fixture
    def client(self, temp_db_path):
        """テスト用Flaskクライアント"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DATABASE'] = temp_db_path

        with app.test_client() as client:
            with app.app_context():
                init_database(temp_db_path)
                yield client

    # =============================================================================
    # Flask エンドポイントのテストケース
    # =============================================================================

    def test_main_page_endpoint_integration(self, client):
        """メインページエンドポイント統合テスト"""
        with patch('location_service.LocationService') as mock_location_service, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # モックサービスの設定
            mock_location_instance = Mock()
            mock_location_instance.get_location_from_ip.return_value = {
                'city': '東京',
                'region': '東京都',
                'latitude': 35.6812,
                'longitude': 139.7671,
                'source': 'ipapi.co'
            }
            mock_location_service.return_value = mock_location_instance

            mock_weather_instance = Mock()
            mock_weather_instance.get_current_weather.return_value = {
                'temperature': 25.0,
                'description': '晴れ',
                'uv_index': 5.0,
                'icon': '01d',
                'source': 'openweathermap'
            }
            mock_weather_instance.get_weather_icon_url.return_value = 'https://openweathermap.org/img/wn/01d@2x.png'
            mock_weather_instance.get_weather_summary.return_value = '晴れ 25°C UV指数 5'
            mock_weather_instance.is_good_weather_for_walking.return_value = True
            mock_weather_service.return_value = mock_weather_instance

            response = client.get('/')

            assert response.status_code == 200
            assert response.content_type.startswith('text/html')

            # HTMLコンテンツの基本確認
            html_content = response.data.decode('utf-8')
            assert '<!DOCTYPE html>' in html_content
            assert 'ルーレットを回す' in html_content

    def test_roulette_endpoint_success_integration(self, client):
        """ルーレットエンドポイント成功統合テスト"""
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service, \
                patch('restaurant_selector.RestaurantSelector') as mock_restaurant_selector, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # レストランサービスのモック
            mock_restaurant_instance = Mock()
            mock_restaurant_instance.search_lunch_restaurants.return_value = [{
                'id': 'J001234567',
                'name': 'テストレストラン',
                'genre': '和食',
                'lat': 35.6815,
                'lng': 139.7675,
                'budget_average': 1000,
                'address': '東京都千代田区',
                'urls': {'pc': 'http://example.com'},
                'photo': 'http://example.com/photo.jpg'
            }]
            mock_restaurant_service.return_value = mock_restaurant_instance

            # レストランセレクターのモック
            mock_selector_instance = Mock()
            mock_selector_instance.select_random_restaurant.return_value = {
                'id': 'J001234567',
                'name': 'テストレストラン',
                'genre': '和食',
                'address': '東京都千代田区',
                'catch': 'おいしいレストラン',
                'display_info': {
                    'budget_display': '¥1,000',
                    'photo_url': 'http://example.com/photo.jpg',
                    'hotpepper_url': 'http://example.com',
                    'map_url': 'https://maps.google.com',
                    'summary': 'テストレストラン - 和食',
                    'access_display': '徒歩5分',
                    'hours_display': '11:00-14:00'
                },
                'distance_info': {
                    'distance_km': 0.5,
                    'distance_display': '500m',
                    'walking_time_minutes': 8,
                    'time_display': '徒歩8分'
                }
            }
            mock_restaurant_selector.return_value = mock_selector_instance

            # 天気サービスのモック
            mock_weather_instance = Mock()
            mock_weather_instance.get_current_weather.return_value = {
                'temperature': 25.0,
                'description': '晴れ',
                'uv_index': 5.0,
                'icon': '01d',
                'source': 'openweathermap'
            }
            mock_weather_instance.is_good_weather_for_walking.return_value = True
            mock_weather_service.return_value = mock_weather_instance

            # リクエストデータ
            request_data = {
                'latitude': 35.6812,
                'longitude': 139.7671
            }

            response = client.post('/roulette',
                                   data=json.dumps(request_data),
                                   content_type='application/json')

            assert response.status_code == 200
            assert response.content_type == 'application/json'

            # レスポンスデータの確認
            data = response.get_json()
            assert data['success'] is True
            assert 'restaurant' in data
            assert 'distance' in data
            assert data['restaurant']['name'] == 'テストレストラン'
            assert data['distance']['distance_display'] == '500m'

    def test_roulette_endpoint_no_restaurants_integration(self, client):
        """ルーレットエンドポイント（レストランなし）統合テスト"""
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # レストランが見つからなぁE��吁E
            mock_restaurant_instance = Mock()
            mock_restaurant_instance.search_lunch_restaurants.return_value = []
            mock_restaurant_service.return_value = mock_restaurant_instance

            mock_weather_instance = Mock()
            mock_weather_instance.get_current_weather.return_value = {
                'temperature': 25.0,
                'description': '晴れ',
                'uv_index': 5.0,
                'icon': '01d'
            }
            mock_weather_instance.is_good_weather_for_walking.return_value = True
            mock_weather_service.return_value = mock_weather_instance

            request_data = {
                'latitude': 35.6812,
                'longitude': 139.7671
            }

            response = client.post('/roulette',
                                   data=json.dumps(request_data),
                                   content_type='application/json')

            assert response.status_code == 200

            data = response.get_json()
            assert data['success'] is False
            assert 'レストランが見つかりません' in data['message']

    def test_error_handlers_integration(self, client):
        """エラーハンドラー統合テスト"""
        # 404エラーテスト
        response = client.get('/nonexistent-page')
        assert response.status_code == 404

        if response.content_type == 'application/json':
            data = response.get_json()
            assert data['error'] is True
            assert 'ページが見つかりません' in data['message']

        # 500エラーテスト（サービスエラーを発生させる）
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service:
            mock_restaurant_service.side_effect = Exception("Test error")

            request_data = {
                'latitude': 35.6812,
                'longitude': 139.7671
            }

            response = client.post('/roulette',
                                   data=json.dumps(request_data),
                                   content_type='application/json')

            assert response.status_code == 500

            if response.content_type == 'application/json':
                data = response.get_json()
                assert data['error'] is True
                assert 'message' in data

    def test_database_statistics_integration(self, temp_db_path):
        """データベース統計統合テスト"""
        init_database(temp_db_path)

        # テストデータを挿入
        with sqlite3.connect(temp_db_path) as conn:
            # 有効なキャッシュ
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key1', '{"test": "valid1"}', (datetime.now() + timedelta(hours=1)).isoformat()))

            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key2', '{"test": "valid2"}', (datetime.now() + timedelta(hours=2)).isoformat()))

            # 期限切れキャッシュ
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('expired_key', '{"test": "expired"}', (datetime.now() - timedelta(hours=1)).isoformat()))

            conn.commit()

        stats = get_cache_stats(temp_db_path)

        assert stats['total_records'] == 3
        assert stats['valid_records'] == 2
        assert stats['expired_records'] == 1
        assert stats['database_size'] > 0

    def test_cache_service_error_handling_integration(self, temp_db_path):
        """CacheService エラーハンドリング統合テスト"""
        # 無効なパスでCacheServiceを作成
        cache_service = CacheService(db_path='/invalid/path/cache.db')

        # データベースアクセスエラー時の動作確認
        result = cache_service.set_cached_data('test_key', {'data': 'test'})
        assert result is False

        retrieved_data = cache_service.get_cached_data('test_key')
        assert retrieved_data is None

        delete_result = cache_service.delete_cached_data('test_key')
        assert delete_result is False

    @patch('location_service.requests.get')
    def test_location_service_error_handling_integration(self, mock_get, cache_service):
        """LocationService エラーハンドリング統合テスト"""
        location_service = LocationService(cache_service=cache_service)

        # ネットワークエラーをシミュレート
        mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")

        result = location_service.get_location_from_ip('192.168.1.1')

        # デフォルト位置が返されることを確認
        assert result['source'] == 'default'
        assert result['city'] == '東京'
        assert result['latitude'] == 35.6812
        assert result['longitude'] == 139.7671

    def test_weather_service_error_handling_integration(self, cache_service):
        """WeatherService エラーハンドリング統合テスト"""
        # APIキーなしでWeatherServiceを作成
        weather_service = WeatherService(api_key=None, cache_service=cache_service)

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # デフォルト天気情報が返されることを確認
        assert result['source'] == 'default'
        assert result['temperature'] == 20.0
        assert result['condition'] == 'clear'

    def test_restaurant_service_error_handling_integration(self, cache_service):
        """RestaurantService エラーハンドリング統合テスト"""
        # APIキーなしでRestaurantServiceを作成
        restaurant_service = RestaurantService(api_key=None, cache_service=cache_service)

        result = restaurant_service.search_restaurants(35.6812, 139.7671)

        # 空のリストが返されることを確認
        assert result == []

    def test_distance_calculator_error_handling_integration(self):
        """DistanceCalculator エラーハンドリング統合テスト"""
        error_handler = ErrorHandler()
        distance_calculator = DistanceCalculator(error_handler=error_handler)

        # 無効な座標での計算（エラーハンドリングされる）
        result = distance_calculator.calculate_distance(95.0, 139.0, 35.0, 139.0)

        # エラーハンドリングにより概算値が返される
        assert isinstance(result, float)
        assert result > 0

    def test_error_handler_integration(self):
        """ErrorHandler 統合テスト"""
        error_handler = ErrorHandler()

        # API エラーハンドリングテスト
        test_error = requests.exceptions.HTTPError("Test error")
        error_type, error_info = error_handler.handle_api_error('test_service', test_error, True)

        assert error_info['service_name'] == 'test_service'
        assert error_info['fallback_available'] is True
        assert 'user_message' in error_info
        assert 'suggestion' in error_info

        # ユーザーフレンドリーメッセージ作成テスト
        user_message = error_handler.create_user_friendly_message(error_info)
        assert 'message' in user_message
        assert 'suggestion' in user_message
        assert 'severity' in user_message

    def test_full_application_flow_integration(self, client):
        """アプリケーション全体フロー統合テスト"""
        # 1. メインページアクセス
        response = client.get('/')
        assert response.status_code == 200

        # 2. ルーレット実行（実際のサービスを使用）
        request_data = {
            'latitude': 35.6812,
            'longitude': 139.7671
        }

        response = client.post('/roulette',
                               data=json.dumps(request_data),
                               content_type='application/json')

        # APIキーが設定されていない場合、またはレストランが見つからない場合
        assert response.status_code == 200
        data = response.get_json()

        # 成功またはレストランが見つからないエラー
        if data.get('success'):
            assert 'restaurant' in data
            assert 'distance' in data
        else:
            assert 'レストランが見つかりません' in data['message']

    def test_concurrent_database_access_integration(self, temp_db_path):
        """同時データベースアクセス統合テスト"""
        init_database(temp_db_path)

        # 複数のCacheServiceインスタンスで同じデータベースにアクセス
        cache_service1 = CacheService(db_path=temp_db_path)
        cache_service2 = CacheService(db_path=temp_db_path)

        # 異なるキーでデータを保存
        key1 = cache_service1.generate_cache_key('test1', param='value1')
        key2 = cache_service2.generate_cache_key('test2', param='value2')

        data1 = {'service': 1, 'data': 'test1'}
        data2 = {'service': 2, 'data': 'test2'}

        result1 = cache_service1.set_cached_data(key1, data1)
        result2 = cache_service2.set_cached_data(key2, data2)

        assert result1 is True
        assert result2 is True

        # 両方のデータが正しく保存されていることを確認
        retrieved_data1 = cache_service1.get_cached_data(key1)
        retrieved_data2 = cache_service2.get_cached_data(key2)

        assert retrieved_data1 == data1
        assert retrieved_data2 == data2

    def test_graceful_degradation_integration(self, cache_service):
        """グレースフルデグラデーション統合テスト"""
        # 一部のサービスが利用できない状況での動作確認

        # LocationService: 成功し、キャッシュから取得
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

        # WeatherService: APIキーなし → デフォルト天気
        weather_service = WeatherService(api_key=None, cache_service=cache_service)
        weather_result = weather_service.get_current_weather(35.6812, 139.7671)
        assert weather_result['source'] == 'default'

        # RestaurantService: APIキーなし → 空リスト
        restaurant_service = RestaurantService(api_key=None, cache_service=cache_service)
        restaurant_result = restaurant_service.search_restaurants(35.6812, 139.7671)
        assert restaurant_result == []

        # システム全体としては部分的に動作することを確認
        assert location_result is not None
        assert weather_result is not None
        assert restaurant_result is not None  # 空リストでもNoneではない


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
