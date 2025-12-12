#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最終統合テスト
Flask エンドポイント、データベース操作、エラーハンドリングの統合テスト

このテストファイルは task 9.2 の要件を満たします:
- Flask エンドポイントのテストケースを作成
- データベース操作のテストケースを作成
- エラーハンドリングのテストケースを作成
"""

import pytest
import json
import tempfile
import os
import sqlite3
import requests
from unittest.mock import patch
from datetime import datetime, timedelta

from lunch_roulette.app import app
from lunch_roulette.models.database import init_database, get_db_connection, cleanup_expired_cache, get_cache_stats
from lunch_roulette.services.cache_service import CacheService
from lunch_roulette.services.location_service import LocationService
from lunch_roulette.services.weather_service import WeatherService
from lunch_roulette.services.restaurant_service import RestaurantService
from lunch_roulette.utils.distance_calculator import DistanceCalculator
from lunch_roulette.utils.error_handler import ErrorHandler


class TestIntegrationFinal:
    """最終統合テストクラス"""

    @pytest.fixture
    def temp_db_path(self):
        """テスト用の一時データベースファイルパス"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            temp_path = temp_file.name
        yield temp_path
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

    def test_main_page_endpoint_loads_successfully(self, client):
        """メインページエンドポイント正常読み込みテスト"""
        response = client.get('/')

        assert response.status_code == 200
        assert response.content_type.startswith('text/html')

        # HTMLコンテンツの基本確認
        html_content = response.data.decode('utf-8')
        assert '<!DOCTYPE html>' in html_content
        assert 'ルーレットを回す' in html_content
        assert '<title>' in html_content

    def test_roulette_endpoint_with_coordinates(self, client):
        """ルーレットエンドポイント座標指定テスト"""
        request_data = {
            'latitude': 35.6812,
            'longitude': 139.7671
        }

        response = client.post('/roulette',
                               data=json.dumps(request_data),
                               content_type='application/json')

        assert response.status_code == 200
        assert response.content_type == 'application/json'

        data = response.get_json()
        # APIキーが設定されていない場合、またはレストランが見つからない場合
        if data.get('success'):
            assert 'restaurant' in data
            assert 'distance' in data
        else:
            assert data['success'] is False
            assert 'message' in data

    def test_roulette_endpoint_without_coordinates(self, client):
        """ルーレットエンドポイント座標なしテスト"""
        request_data = {}

        response = client.post('/roulette',
                               data=json.dumps(request_data),
                               content_type='application/json')

        assert response.status_code == 200
        assert response.content_type == 'application/json'

        data = response.get_json()
        # 座標がない場合、IPから取得される
        assert 'success' in data

    def test_roulette_endpoint_invalid_json(self, client):
        """ルーレットエンドポイント無効JSONテスト"""
        response = client.post('/roulette',
                               data='invalid json',
                               content_type='application/json')

        # 無効なJSONは500エラーになる
        assert response.status_code == 500

        data = response.get_json()
        assert data['error'] is True
        assert 'message' in data

    def test_404_error_handler(self, client):
        """404エラーハンドラーテスト"""
        response = client.get('/nonexistent-page')

        assert response.status_code == 404

        if response.content_type == 'application/json':
            data = response.get_json()
            assert data['error'] is True
            assert 'ページが見つかりません' in data['message']

    def test_method_not_allowed(self, client):
        """メソッド不許可テスト"""
        # POSTエンドポイントにGETリクエスト
        response = client.get('/roulette')

        assert response.status_code == 405

    def test_endpoint_with_large_request(self, client):
        """大きなリクエスト処理テスト"""
        large_data = {
            'latitude': 35.6812,
            'longitude': 139.7671,
            'extra_data': 'x' * 10000  # 10KB の余分なデータ
        }

        response = client.post('/roulette',
                               data=json.dumps(large_data),
                               content_type='application/json')

        # 大きなリクエストでも処理される（適切な部分のみ使用）
        assert response.status_code in [200, 413]

    # =============================================================================
    # データベース操作のテストケース
    # =============================================================================

    def test_database_initialization(self, temp_db_path):
        """データベース初期化テスト"""
        result = init_database(temp_db_path)

        assert result is True
        assert os.path.exists(temp_db_path)

        # テーブルが作成されていることを確認
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='cache'
            """)
            table_exists = cursor.fetchone() is not None
            assert table_exists is True

    def test_database_connection(self, temp_db_path):
        """データベース接続テスト"""
        init_database(temp_db_path)

        with get_db_connection(temp_db_path) as conn:
            assert conn is not None

            # 基本的なクエリ実行テスト
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            count = cursor.fetchone()[0]
            assert count == 0

    def test_cache_crud_operations(self, cache_service):
        """キャッシュCRUD操作テスト"""
        # データ保存
        test_data = {'message': 'Hello Integration', 'number': 42}
        cache_key = cache_service.generate_cache_key('integration_test', param='value')

        result = cache_service.set_cached_data(cache_key, test_data, ttl=300)
        assert result is True

        # データ取得
        retrieved_data = cache_service.get_cached_data(cache_key)
        assert retrieved_data == test_data

        # データ削除
        delete_result = cache_service.delete_cached_data(cache_key)
        assert delete_result is True

        # 削除後の確認
        retrieved_after_delete = cache_service.get_cached_data(cache_key)
        assert retrieved_after_delete is None

    def test_cache_expiration_cleanup(self, temp_db_path):
        """キャッシュ期限切れクリーンアップテスト"""
        init_database(temp_db_path)

        # テストデータを挿入（有効・期限切れ混在）
        with sqlite3.connect(temp_db_path) as conn:
            # 有効なキャッシュ
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key', '{"test": "valid"}', datetime.now() + timedelta(hours=1)))

            # 期限切れキャッシュ
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('expired_key', '{"test": "expired"}', datetime.now() - timedelta(hours=1)))

            conn.commit()

        # クリーンアップ実行
        deleted_count = cleanup_expired_cache(temp_db_path)
        assert deleted_count == 1

        # 有効なキャッシュのみ残っていることを確認
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            remaining_count = cursor.fetchone()[0]
            assert remaining_count == 1

    def test_database_transaction_rollback(self, temp_db_path):
        """データベーストランザクションロールバックテスト"""
        init_database(temp_db_path)

        try:
            with get_db_connection(temp_db_path) as conn:
                # 正常なデータ挿入
                conn.execute("""
                    INSERT INTO cache (cache_key, data, expires_at)
                    VALUES (?, ?, ?)
                """, ('test_key', '{"test": "data"}', datetime.now() + timedelta(hours=1)))

                # 意図的にエラーを発生させる（無効なSQL）
                conn.execute("INVALID SQL STATEMENT")

        except sqlite3.Error:
            # エラーが発生することを期待
            pass

        # トランザクションがロールバックされていることを確認
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            count = cursor.fetchone()[0]
            assert count == 0

    # =============================================================================
    # エラーハンドリングのテストケース
    # =============================================================================

    def test_cache_service_database_error_handling(self):
        """CacheService データベースエラーハンドリングテスト"""
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

    def test_weather_service_no_api_key_handling(self, cache_service):
        """WeatherService APIキーなしハンドリングテスト"""
        weather_service = WeatherService(api_key=None, cache_service=cache_service)

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # デフォルト天気情報が返されることを確認
        assert result['source'] == 'default'
        assert result['temperature'] == 20.0
        assert result['condition'] == 'sunny'

    def test_restaurant_service_no_api_key_handling(self, cache_service):
        """RestaurantService APIキーなしハンドリングテスト"""
        restaurant_service = RestaurantService(api_key=None, cache_service=cache_service)

        result = restaurant_service.search_restaurants(35.6812, 139.7671)

        # 空のリストが返されることを確認
        assert result == []

    def test_distance_calculator_error_handling(self):
        """DistanceCalculator エラーハンドリングテスト"""
        error_handler = ErrorHandler()
        distance_calculator = DistanceCalculator(error_handler=error_handler)

        # 無効な座標での計算（エラーハンドリングされる）
        result = distance_calculator.calculate_distance(95.0, 139.0, 35.0, 139.0)

        # エラーハンドリングにより概算値が返される
        assert isinstance(result, float)
        assert result > 0

    def test_error_handler_basic_functionality(self):
        """ErrorHandler 基本機能テスト"""
        error_handler = ErrorHandler()

        # 距離計算エラーハンドリングテスト
        test_error = ValueError("Test distance calculation error")
        result = error_handler.handle_distance_calculation_error(test_error)

        assert 'message' in result
        assert 'suggestion' in result
        assert 'severity' in result
        assert result['fallback_used'] is True

    def test_service_graceful_degradation(self, cache_service):
        """サービスグレースフルデグラデーションテスト"""
        # LocationService: デフォルト位置使用
        location_service = LocationService(cache_service=cache_service)
        location_result = location_service.get_location_from_ip('invalid.ip')
        assert location_result['source'] == 'default'

        # WeatherService: APIキーなしでデフォルト天気
        weather_service = WeatherService(api_key=None, cache_service=cache_service)
        weather_result = weather_service.get_current_weather(35.6812, 139.7671)
        assert weather_result['source'] == 'default'

        # RestaurantService: APIキーなしで空リスト
        restaurant_service = RestaurantService(api_key=None, cache_service=cache_service)
        restaurant_result = restaurant_service.search_restaurants(35.6812, 139.7671)
        assert restaurant_result == []

        # システム全体としては正常に動作することを確認
        assert location_result is not None
        assert weather_result is not None
        assert restaurant_result is not None  # 空リストでNone ではない

    def test_application_error_recovery(self, client):
        """アプリケーションエラー回復テスト"""
        # 1. 正常なリクエスト
        response = client.get('/')
        assert response.status_code == 200

        # 2. エラーが発生するリクエスト
        response = client.post('/roulette',
                               data='invalid json',
                               content_type='application/json')
        assert response.status_code == 500

        # 3. 再度正常なリクエスト（アプリケーションが回復していることを確認）
        response = client.get('/')
        assert response.status_code == 200

    # =============================================================================
    # 統合シナリオテスト
    # =============================================================================

    def test_full_application_workflow(self, client):
        """アプリケーション全体ワークフローテスト"""
        # 1. メインページアクセス
        response = client.get('/')
        assert response.status_code == 200

        # 2. ルーレット実行
        request_data = {
            'latitude': 35.6812,
            'longitude': 139.7671
        }

        response = client.post('/roulette',
                               data=json.dumps(request_data),
                               content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()

        # 成功またはエラーレスポンスが返される
        assert 'success' in data or 'error' in data

        # 3. 存在しないページアクセスで404エラー
        response = client.get('/nonexistent')
        assert response.status_code == 404


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
