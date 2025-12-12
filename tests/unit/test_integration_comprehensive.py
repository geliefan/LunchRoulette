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

from lunch_roulette.app import app
from lunch_roulette.models.database import init_database, cleanup_expired_cache, get_cache_stats
from lunch_roulette.services.cache_service import CacheService
from lunch_roulette.services.location_service import LocationService
from lunch_roulette.services.weather_service import WeatherService
from lunch_roulette.services.restaurant_service import RestaurantService
from lunch_roulette.utils.distance_calculator import DistanceCalculator
from lunch_roulette.utils.error_handler import ErrorHandler


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
        with patch('lunch_roulette.services.restaurant_service.RestaurantService') as mock_restaurant_service:
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

    @patch('lunch_roulette.services.location_service.requests.get')
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
        assert result['condition'] == 'sunny'

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
        mock_response = Mock()
        mock_response.status_code = 500
        test_error = requests.exceptions.HTTPError("Test error")
        test_error.response = mock_response
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
            # APIキーがない場合は汎用エラーメッセージになる
            assert 'message' in data
            assert data['success'] is False

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
