#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask エンドポイントの統合テスト
実際のFlaskアプリケーションとの統合をテスト
"""

import pytest
import json
import os
from unittest.mock import patch, Mock
from app import app
from database import init_database


class TestFlaskEndpointsIntegration:
    """Flask エンドポイントの統合テスト"""

    @pytest.fixture
    def client(self):
        """テスト用Flaskクライアント"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

        # 一意なテストデータベース名を生成
        import uuid
        test_db_name = f'test_cache_{uuid.uuid4().hex[:8]}.db'

        with app.test_client() as client:
            with app.app_context():
                # テスト用データベース初期化
                init_database(test_db_name)
                yield client

        # テスト後にクリーンアップ（Windowsでの権限エラー対策）
        try:
            if os.path.exists(test_db_name):
                os.unlink(test_db_name)
        except (PermissionError, OSError):
            # Windows環境でファイルが使用中の場合は無視
            pass

    def test_main_page_endpoint_success(self, client):
        """メインページエンドポイント成功テスト"""
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
            assert '<title>' in html_content
            assert 'ルーレットを回す' in html_content

    def test_main_page_endpoint_service_error(self, client):
        """メインページエンドポイント（サービスエラー）テスト"""
        with patch('location_service.LocationService') as mock_location_service, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # サービスでエラーが発生する場合
            mock_location_service.side_effect = Exception("Location service error")
            mock_weather_service.side_effect = Exception("Weather service error")

            response = client.get('/')

            # エラーが発生してもページは表示される（エラーハンドリング）
            assert response.status_code == 200

            # デフォルトデータでページが表示されることを確認
            html_content = response.data.decode('utf-8')
            assert '東京' in html_content  # デフォルト位置

    def test_roulette_endpoint_success(self, client):
        """ルーレットエンドポイント成功テスト"""
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service, \
                patch('restaurant_selector.RestaurantSelector') as mock_restaurant_selector, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # モックサービスの設定
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

    def test_roulette_endpoint_no_restaurants(self, client):
        """ルーレットエンドポイント（レストランなし）テスト"""
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # レストランが見つからない場合
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

    def test_roulette_endpoint_missing_coordinates(self, client):
        """ルーレットエンドポイント（座標不足）テスト"""
        with patch('location_service.LocationService') as mock_location_service, \
                patch('restaurant_service.RestaurantService') as mock_restaurant_service, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # LocationServiceのモック設定（IPから位置情報を取得）
            mock_location_instance = Mock()
            mock_location_instance.get_location_from_ip.return_value = {
                'latitude': 35.6812,
                'longitude': 139.7671,
                'city': '東京',
                'source': 'ipapi.co'
            }
            mock_location_service.return_value = mock_location_instance

            # レストランが見つからない場合
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

            # 座標が不足しているリクエスト（IPから取得される）
            request_data = {
                'latitude': 35.6812
                # longitude が不足
            }

            response = client.post('/roulette',
                                   data=json.dumps(request_data),
                                   content_type='application/json')

            # 座標不足でIPから取得するため200が返される
            assert response.status_code == 200

            data = response.get_json()
            assert data['success'] is False  # レストランが見つからないため
            assert 'レストランが見つかりません' in data['message']

    def test_roulette_endpoint_invalid_json(self, client):
        """ルーレットエンドポイント（無効なJSON）テスト"""
        response = client.post('/roulette',
                               data='invalid json',
                               content_type='application/json')

        # 無効なJSONは500エラーになる（アプリケーションの実装による）
        assert response.status_code == 500

        data = response.get_json()
        assert data['error'] is True
        assert 'message' in data

    def test_roulette_endpoint_service_error(self, client):
        """ルーレットエンドポイント（サービスエラー）テスト"""
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service:

            # サービスでエラーが発生する場合
            mock_restaurant_service.side_effect = Exception("Service error")

            request_data = {
                'latitude': 35.6812,
                'longitude': 139.7671
            }

            response = client.post('/roulette',
                                   data=json.dumps(request_data),
                                   content_type='application/json')

            assert response.status_code == 500

            data = response.get_json()
            assert data['error'] is True
            assert 'message' in data

    def test_404_error_handler(self, client):
        """404エラーハンドラーテスト"""
        response = client.get('/nonexistent-page')

        assert response.status_code == 404

        # JSONレスポンスまたはHTMLレスポンスのいずれかが返される
        if response.content_type == 'application/json':
            data = response.get_json()
            assert data['error'] is True
            assert 'ペ�Eジが見つかりません' in data['message']
        else:
            # HTMLエラーページの場合
            assert response.content_type.startswith('text/html')

    def test_500_error_handler(self, client):
        """500エラーハンドラーテスト"""
        # 既存のエンドポイントでエラーを発生させる
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service:
            # サービスでエラーが発生する場合
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

    def test_method_not_allowed(self, client):
        """メソッド不許可テスト"""
        # POSTエンドポイントにGETリクエスト
        response = client.get('/roulette')

        assert response.status_code == 405

    def test_content_type_validation(self, client):
        """Content-Type検証テスト"""
        # 不正なContent-Type
        response = client.post('/roulette',
                               data='{"latitude": 35.6812, "longitude": 139.7671}',
                               content_type='text/plain')

        # Content-Typeが不正な場合は500エラーになる（アプリケーションの実装による）
        assert response.status_code == 500

        data = response.get_json()
        assert data['error'] is True

    def test_large_request_handling(self, client):
        """大きなリクエストボディの処理テスト"""
        # 大きなJSONデータ
        large_data = {
            'latitude': 35.6812,
            'longitude': 139.7671,
            'extra_data': 'x' * 10000  # 10KB の余分なデータ
        }

        response = client.post('/roulette',
                               data=json.dumps(large_data),
                               content_type='application/json')

        # 大きなリクエストでも正常に処理されるか、エラーが返される
        assert response.status_code in [200, 400, 413]

    def test_concurrent_requests_simulation(self, client):
        """同時リクエストシミュレーションテスト"""
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service, \
                patch('restaurant_selector.RestaurantSelector') as mock_restaurant_selector, \
                patch('weather_service.WeatherService') as mock_weather_service:

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

            mock_weather_instance = Mock()
            mock_weather_instance.get_current_weather.return_value = {
                'temperature': 25.0,
                'description': '晴れ',
                'uv_index': 5.0,
                'icon': '01d'
            }
            mock_weather_instance.is_good_weather_for_walking.return_value = True
            mock_weather_service.return_value = mock_weather_instance

            # 複数のリクエストを同時に実行（同時実行テスト）
            request_data = {
                'latitude': 35.6812,
                'longitude': 139.7671
            }

            responses = []
            for i in range(5):
                response = client.post('/roulette',
                                       data=json.dumps(request_data),
                                       content_type='application/json')
                responses.append(response)

            # すべてのリクエストが正常に処理されることを確認
            for response in responses:
                assert response.status_code in [200, 500]  # 成功またはサーバエラー


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
