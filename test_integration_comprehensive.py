#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
蛹・峡逧・ｵｱ蜷医ユ繧ｹ繝・
Flask 繧ｨ繝ｳ繝峨・繧､繝ｳ繝医√ョ繝ｼ繧ｿ繝吶・繧ｹ謫堺ｽ懊√お繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｮ邨ｱ蜷医ユ繧ｹ繝・

縺薙・繝・せ繝医ヵ繧｡繧､繝ｫ縺ｯ莉･荳九ｒ繧ｫ繝舌・縺励∪縺・
- Flask 繧ｨ繝ｳ繝峨・繧､繝ｳ繝医・繝・せ繝医こ繝ｼ繧ｹ
- 繝・・繧ｿ繝吶・繧ｹ謫堺ｽ懊・繝・せ繝医こ繝ｼ繧ｹ
- 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｮ繝・せ繝医こ繝ｼ繧ｹ
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
    """蛹・峡逧・ｵｱ蜷医ユ繧ｹ繝医け繝ｩ繧ｹ"""

    @pytest.fixture
    def temp_db_path(self):
        """繝・せ繝育畑縺ｮ荳譎ゅョ繝ｼ繧ｿ繝吶・繧ｹ繝輔ぃ繧､繝ｫ繝代せ"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            temp_path = temp_file.name
        yield temp_path
        # 繝・せ繝亥ｾ後↓繝輔ぃ繧､繝ｫ繧貞炎髯､・・indows縺ｧ縺ｮ讓ｩ髯舌お繝ｩ繝ｼ蟇ｾ遲厄ｼ・
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        except (PermissionError, OSError):
            pass

    @pytest.fixture
    def cache_service(self, temp_db_path):
        """繝・せ繝育畑CacheService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ"""
        init_database(temp_db_path)
        return CacheService(db_path=temp_db_path)

    @pytest.fixture
    def client(self, temp_db_path):
        """繝・せ繝育畑Flask繧ｯ繝ｩ繧､繧｢繝ｳ繝・""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DATABASE'] = temp_db_path

        with app.test_client() as client:
            with app.app_context():
                init_database(temp_db_path)
                yield client

    # =============================================================================
    # Flask 繧ｨ繝ｳ繝峨・繧､繝ｳ繝医・繝・せ繝医こ繝ｼ繧ｹ
    # =============================================================================

    def test_main_page_endpoint_integration(self, client):
        """繝｡繧､繝ｳ繝壹・繧ｸ繧ｨ繝ｳ繝峨・繧､繝ｳ繝育ｵｱ蜷医ユ繧ｹ繝・""
        with patch('location_service.LocationService') as mock_location_service, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # 繝｢繝・け繧ｵ繝ｼ繝薙せ縺ｮ險ｭ螳・
            mock_location_instance = Mock()
            mock_location_instance.get_location_from_ip.return_value = {
                'city': '譚ｱ莠ｬ',
                'region': '譚ｱ莠ｬ驛ｽ',
                'latitude': 35.6812,
                'longitude': 139.7671,
                'source': 'ipapi.co'
            }
            mock_location_service.return_value = mock_location_instance

            mock_weather_instance = Mock()
            mock_weather_instance.get_current_weather.return_value = {
                'temperature': 25.0,
                'description': '譎ｴ繧・,
                'uv_index': 5.0,
                'icon': '01d',
                'source': 'openweathermap'
            }
            mock_weather_instance.get_weather_icon_url.return_value = 'https://openweathermap.org/img/wn/01d@2x.png'
            mock_weather_instance.get_weather_summary.return_value = '譎ｴ繧・25ﾂｰC UV謖・焚5'
            mock_weather_instance.is_good_weather_for_walking.return_value = True
            mock_weather_service.return_value = mock_weather_instance

            response = client.get('/')

            assert response.status_code == 200
            assert response.content_type.startswith('text/html')

            # HTML繧ｳ繝ｳ繝・Φ繝・・蝓ｺ譛ｬ遒ｺ隱・
            html_content = response.data.decode('utf-8')
            assert '<!DOCTYPE html>' in html_content
            assert '繝ｫ繝ｼ繝ｬ繝・ヨ繧貞屓縺・ in html_content

    def test_roulette_endpoint_success_integration(self, client):
        """繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝域・蜉溽ｵｱ蜷医ユ繧ｹ繝・""
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service, \
                patch('restaurant_selector.RestaurantSelector') as mock_restaurant_selector, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # 繝ｬ繧ｹ繝医Λ繝ｳ繧ｵ繝ｼ繝薙せ縺ｮ繝｢繝・け
            mock_restaurant_instance = Mock()
            mock_restaurant_instance.search_lunch_restaurants.return_value = [{
                'id': 'J001234567',
                'name': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ',
                'genre': '蜥碁｣・,
                'lat': 35.6815,
                'lng': 139.7675,
                'budget_average': 1000,
                'address': '譚ｱ莠ｬ驛ｽ蜊・ｻ｣逕ｰ蛹ｺ',
                'urls': {'pc': 'http://example.com'},
                'photo': 'http://example.com/photo.jpg'
            }]
            mock_restaurant_service.return_value = mock_restaurant_instance

            # 繝ｬ繧ｹ繝医Λ繝ｳ繧ｻ繝ｬ繧ｯ繧ｿ繝ｼ縺ｮ繝｢繝・け
            mock_selector_instance = Mock()
            mock_selector_instance.select_random_restaurant.return_value = {
                'id': 'J001234567',
                'name': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ',
                'genre': '蜥碁｣・,
                'address': '譚ｱ莠ｬ驛ｽ蜊・ｻ｣逕ｰ蛹ｺ',
                'catch': '縺翫＞縺励＞繝ｬ繧ｹ繝医Λ繝ｳ',
                'display_info': {
                    'budget_display': 'ﾂ･1,000',
                    'photo_url': 'http://example.com/photo.jpg',
                    'hotpepper_url': 'http://example.com',
                    'map_url': 'https://maps.google.com',
                    'summary': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ - 蜥碁｣・,
                    'access_display': '蠕呈ｭｩ5蛻・,
                    'hours_display': '11:00-14:00'
                },
                'distance_info': {
                    'distance_km': 0.5,
                    'distance_display': '500m',
                    'walking_time_minutes': 8,
                    'time_display': '蠕呈ｭｩ邏・蛻・
                }
            }
            mock_restaurant_selector.return_value = mock_selector_instance

            # 螟ｩ豌励し繝ｼ繝薙せ縺ｮ繝｢繝・け
            mock_weather_instance = Mock()
            mock_weather_instance.get_current_weather.return_value = {
                'temperature': 25.0,
                'description': '譎ｴ繧・,
                'uv_index': 5.0,
                'icon': '01d',
                'source': 'openweathermap'
            }
            mock_weather_instance.is_good_weather_for_walking.return_value = True
            mock_weather_service.return_value = mock_weather_instance

            # 繝ｪ繧ｯ繧ｨ繧ｹ繝医ョ繝ｼ繧ｿ
            request_data = {
                'latitude': 35.6812,
                'longitude': 139.7671
            }

            response = client.post('/roulette',
                                   data=json.dumps(request_data),
                                   content_type='application/json')

            assert response.status_code == 200
            assert response.content_type == 'application/json'

            # 繝ｬ繧ｹ繝昴Φ繧ｹ繝・・繧ｿ縺ｮ遒ｺ隱・
            data = response.get_json()
            assert data['success'] is True
            assert 'restaurant' in data
            assert 'distance' in data
            assert data['restaurant']['name'] == '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ'
            assert data['distance']['distance_display'] == '500m'

    def test_roulette_endpoint_no_restaurants_integration(self, client):
        """繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝茨ｼ医Ξ繧ｹ繝医Λ繝ｳ縺ｪ縺暦ｼ臥ｵｱ蜷医ユ繧ｹ繝・""
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # 繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷・
            mock_restaurant_instance = Mock()
            mock_restaurant_instance.search_lunch_restaurants.return_value = []
            mock_restaurant_service.return_value = mock_restaurant_instance

            mock_weather_instance = Mock()
            mock_weather_instance.get_current_weather.return_value = {
                'temperature': 25.0,
                'description': '譎ｴ繧・,
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
            assert '繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ' in data['message']

    def test_error_handlers_integration(self, client):
        """繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ邨ｱ蜷医ユ繧ｹ繝・""
        # 404繧ｨ繝ｩ繝ｼ繝・せ繝・
        response = client.get('/nonexistent-page')
        assert response.status_code == 404

        if response.content_type == 'application/json':
            data = response.get_json()
            assert data['error'] is True
            assert '繝壹・繧ｸ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ' in data['message']

        # 500繧ｨ繝ｩ繝ｼ繝・せ繝茨ｼ医し繝ｼ繝薙せ繧ｨ繝ｩ繝ｼ繧堤匱逕溘＆縺帙ｋ・・
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

    # =============================================================================
    # 繝・・繧ｿ繝吶・繧ｹ謫堺ｽ懊・繝・せ繝医こ繝ｼ繧ｹ
    # =============================================================================

    def test_database_initialization_integration(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹也ｵｱ蜷医ユ繧ｹ繝・""
        result = init_database(temp_db_path)

        assert result is True
        assert os.path.exists(temp_db_path)

        # 繝・・繝悶Ν縺御ｽ懈・縺輔ｌ縺ｦ縺・ｋ縺薙→繧堤｢ｺ隱・
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='cache'
            """)
            table_exists = cursor.fetchone() is not None
            assert table_exists is True

    def test_cache_operations_integration(self, cache_service):
        """繧ｭ繝｣繝・す繝･謫堺ｽ懃ｵｱ蜷医ユ繧ｹ繝・""
        # 繝・・繧ｿ菫晏ｭ・
        test_data = {'message': 'Hello Integration', 'number': 42}
        cache_key = cache_service.generate_cache_key('integration_test', param='value')

        result = cache_service.set_cached_data(cache_key, test_data, ttl=300)
        assert result is True

        # 繝・・繧ｿ蜿門ｾ・
        retrieved_data = cache_service.get_cached_data(cache_key)
        assert retrieved_data == test_data

        # 繝・・繧ｿ蜑企勁
        delete_result = cache_service.delete_cached_data(cache_key)
        assert delete_result is True

        # 蜑企勁蠕後・蜿門ｾ礼｢ｺ隱・
        retrieved_after_delete = cache_service.get_cached_data(cache_key)
        assert retrieved_after_delete is None

    def test_cache_expiration_integration(self, temp_db_path):
        """繧ｭ繝｣繝・す繝･譛滄剞蛻・ｌ邨ｱ蜷医ユ繧ｹ繝・""
        init_database(temp_db_path)

        # 繝・せ繝医ョ繝ｼ繧ｿ繧呈諺蜈･・域怏蜉ｹ繝ｻ譛滄剞蛻・ｌ豺ｷ蝨ｨ・・
        with sqlite3.connect(temp_db_path) as conn:
            # 譛牙柑縺ｪ繧ｭ繝｣繝・す繝･
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key', '{"test": "valid"}', datetime.now() + timedelta(hours=1)))

            # 譛滄剞蛻・ｌ繧ｭ繝｣繝・す繝･
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('expired_key', '{"test": "expired"}', datetime.now() - timedelta(hours=1)))

            conn.commit()

        # 繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・螳溯｡・
        deleted_count = cleanup_expired_cache(temp_db_path)
        assert deleted_count == 1

        # 譛牙柑縺ｪ繧ｭ繝｣繝・す繝･縺ｮ縺ｿ谿九▲縺ｦ縺・ｋ縺薙→繧堤｢ｺ隱・
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            remaining_count = cursor.fetchone()[0]
            assert remaining_count == 1

    def test_database_statistics_integration(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ邨ｱ險育ｵｱ蜷医ユ繧ｹ繝・""
        init_database(temp_db_path)

        # 繝・せ繝医ョ繝ｼ繧ｿ繧呈諺蜈･
        with sqlite3.connect(temp_db_path) as conn:
            # 譛牙柑縺ｪ繧ｭ繝｣繝・す繝･
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key1', '{"test": "valid1"}', datetime.now() + timedelta(hours=1)))

            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key2', '{"test": "valid2"}', datetime.now() + timedelta(hours=2)))

            # 譛滄剞蛻・ｌ繧ｭ繝｣繝・す繝･
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('expired_key', '{"test": "expired"}', datetime.now() - timedelta(hours=1)))

            conn.commit()

        stats = get_cache_stats(temp_db_path)

        assert stats['total_records'] == 3
        assert stats['valid_records'] == 2
        assert stats['expired_records'] == 1
        assert stats['database_size'] > 0

    # =============================================================================
    # 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｮ繝・せ繝医こ繝ｼ繧ｹ
    # =============================================================================

    def test_cache_service_error_handling_integration(self, temp_db_path):
        """CacheService 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ邨ｱ蜷医ユ繧ｹ繝・""
        # 辟｡蜉ｹ縺ｪ繝代せ縺ｧCacheService繧剃ｽ懈・
        cache_service = CacheService(db_path='/invalid/path/cache.db')

        # 繝・・繧ｿ繝吶・繧ｹ繧｢繧ｯ繧ｻ繧ｹ繧ｨ繝ｩ繝ｼ譎ゅ・蜍穂ｽ懃｢ｺ隱・
        result = cache_service.set_cached_data('test_key', {'data': 'test'})
        assert result is False

        retrieved_data = cache_service.get_cached_data('test_key')
        assert retrieved_data is None

        delete_result = cache_service.delete_cached_data('test_key')
        assert delete_result is False

    @patch('location_service.requests.get')
    def test_location_service_error_handling_integration(self, mock_get, cache_service):
        """LocationService 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ邨ｱ蜷医ユ繧ｹ繝・""
        location_service = LocationService(cache_service=cache_service)

        # 繝阪ャ繝医Ρ繝ｼ繧ｯ繧ｨ繝ｩ繝ｼ繧偵す繝溘Η繝ｬ繝ｼ繝・
        mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")

        result = location_service.get_location_from_ip('192.168.1.1')

        # 繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result['source'] == 'default'
        assert result['city'] == '譚ｱ莠ｬ'
        assert result['latitude'] == 35.6812
        assert result['longitude'] == 139.7671

    def test_weather_service_error_handling_integration(self, cache_service):
        """WeatherService 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ邨ｱ蜷医ユ繧ｹ繝・""
        # API繧ｭ繝ｼ縺ｪ縺励〒WeatherService繧剃ｽ懈・
        weather_service = WeatherService(api_key=None, cache_service=cache_service)

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # 繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌玲ュ蝣ｱ縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result['source'] == 'default'
        assert result['temperature'] == 20.0
        assert result['condition'] == 'clear'

    def test_restaurant_service_error_handling_integration(self, cache_service):
        """RestaurantService 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ邨ｱ蜷医ユ繧ｹ繝・""
        # API繧ｭ繝ｼ縺ｪ縺励〒RestaurantService繧剃ｽ懈・
        restaurant_service = RestaurantService(api_key=None, cache_service=cache_service)

        result = restaurant_service.search_restaurants(35.6812, 139.7671)

        # 遨ｺ縺ｮ繝ｪ繧ｹ繝医′霑斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result == []

    def test_distance_calculator_error_handling_integration(self):
        """DistanceCalculator 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ邨ｱ蜷医ユ繧ｹ繝・""
        error_handler = ErrorHandler()
        distance_calculator = DistanceCalculator(error_handler=error_handler)

        # 辟｡蜉ｹ縺ｪ蠎ｧ讓吶〒縺ｮ險育ｮ暦ｼ医お繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺輔ｌ繧具ｼ・
        result = distance_calculator.calculate_distance(95.0, 139.0, 35.0, 139.0)

        # 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｫ繧医ｊ讎らｮ怜､縺瑚ｿ斐＆繧後ｋ
        assert isinstance(result, float)
        assert result > 0

    def test_error_handler_integration(self):
        """ErrorHandler 邨ｱ蜷医ユ繧ｹ繝・""
        error_handler = ErrorHandler()

        # API 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・
        test_error = requests.exceptions.HTTPError("Test error")
        error_type, error_info = error_handler.handle_api_error('test_service', test_error, True)

        assert error_info['service_name'] == 'test_service'
        assert error_info['fallback_available'] is True
        assert 'user_message' in error_info
        assert 'suggestion' in error_info

        # 繝ｦ繝ｼ繧ｶ繝ｼ繝輔Ξ繝ｳ繝峨Μ繝ｼ繝｡繝・そ繝ｼ繧ｸ菴懈・繝・せ繝・
        user_message = error_handler.create_user_friendly_message(error_info)
        assert 'message' in user_message
        assert 'suggestion' in user_message
        assert 'severity' in user_message

    # =============================================================================
    # 隍・粋逧・↑邨ｱ蜷医ユ繧ｹ繝・
    # =============================================================================

    def test_full_application_flow_integration(self, client):
        """繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ蜈ｨ菴薙ヵ繝ｭ繝ｼ邨ｱ蜷医ユ繧ｹ繝・""
        # 1. 繝｡繧､繝ｳ繝壹・繧ｸ繧｢繧ｯ繧ｻ繧ｹ
        response = client.get('/')
        assert response.status_code == 200

        # 2. 繝ｫ繝ｼ繝ｬ繝・ヨ螳溯｡鯉ｼ亥ｮ滄圀縺ｮ繧ｵ繝ｼ繝薙せ繧剃ｽｿ逕ｨ・・
        request_data = {
            'latitude': 35.6812,
            'longitude': 139.7671
        }

        response = client.post('/roulette',
                               data=json.dumps(request_data),
                               content_type='application/json')

        # API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺・↑縺・ｴ蜷医・繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｉ縺ｪ縺・
        assert response.status_code == 200
        data = response.get_json()

        # 謌仙粥縺ｾ縺溘・繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｉ縺ｪ縺・お繝ｩ繝ｼ
        if data.get('success'):
            assert 'restaurant' in data
            assert 'distance' in data
        else:
            assert '繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ' in data['message']

    def test_concurrent_database_access_integration(self, temp_db_path):
        """蜷梧凾繝・・繧ｿ繝吶・繧ｹ繧｢繧ｯ繧ｻ繧ｹ邨ｱ蜷医ユ繧ｹ繝・""
        init_database(temp_db_path)

        # 隍・焚縺ｮCacheService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ縺ｧ蜷後§繝・・繧ｿ繝吶・繧ｹ縺ｫ繧｢繧ｯ繧ｻ繧ｹ
        cache_service1 = CacheService(db_path=temp_db_path)
        cache_service2 = CacheService(db_path=temp_db_path)

        # 逡ｰ縺ｪ繧九く繝ｼ縺ｧ繝・・繧ｿ繧剃ｿ晏ｭ・
        key1 = cache_service1.generate_cache_key('test1', param='value1')
        key2 = cache_service2.generate_cache_key('test2', param='value2')

        data1 = {'service': 1, 'data': 'test1'}
        data2 = {'service': 2, 'data': 'test2'}

        result1 = cache_service1.set_cached_data(key1, data1)
        result2 = cache_service2.set_cached_data(key2, data2)

        assert result1 is True
        assert result2 is True

        # 荳｡譁ｹ縺ｮ繝・・繧ｿ縺梧ｭ｣縺励￥菫晏ｭ倥＆繧後※縺・ｋ縺薙→繧堤｢ｺ隱・
        retrieved_data1 = cache_service1.get_cached_data(key1)
        retrieved_data2 = cache_service2.get_cached_data(key2)

        assert retrieved_data1 == data1
        assert retrieved_data2 == data2

    def test_graceful_degradation_integration(self, cache_service):
        """繧ｰ繝ｬ繝ｼ繧ｹ繝輔Ν繝・げ繝ｩ繝・・繧ｷ繝ｧ繝ｳ邨ｱ蜷医ユ繧ｹ繝・""
        # 荳驛ｨ縺ｮ繧ｵ繝ｼ繝薙せ縺悟茜逕ｨ縺ｧ縺阪↑縺・憾豕√〒縺ｮ蜍穂ｽ懃｢ｺ隱・

        # LocationService: 謌仙粥・医く繝｣繝・す繝･縺九ｉ・・
        location_service = LocationService(cache_service=cache_service)
        cache_key = cache_service.generate_cache_key('location', ip='auto')
        cache_service.set_cached_data(cache_key, {
            'latitude': 35.6812,
            'longitude': 139.7671,
            'city': '譚ｱ莠ｬ',
            'source': 'ipapi.co'
        })
        location_result = location_service.get_location_from_ip()
        assert location_result['source'] == 'ipapi.co'

        # WeatherService: API繧ｭ繝ｼ縺ｪ縺・竊・繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌・
        weather_service = WeatherService(api_key=None, cache_service=cache_service)
        weather_result = weather_service.get_current_weather(35.6812, 139.7671)
        assert weather_result['source'] == 'default'

        # RestaurantService: API繧ｭ繝ｼ縺ｪ縺・竊・遨ｺ繝ｪ繧ｹ繝・
        restaurant_service = RestaurantService(api_key=None, cache_service=cache_service)
        restaurant_result = restaurant_service.search_restaurants(35.6812, 139.7671)
        assert restaurant_result == []

        # 繧ｷ繧ｹ繝・Β蜈ｨ菴薙→縺励※縺ｯ驛ｨ蛻・噪縺ｫ蜍穂ｽ懊☆繧九％縺ｨ繧堤｢ｺ隱・
        assert location_result is not None
        assert weather_result is not None
        assert restaurant_result is not None  # 遨ｺ繝ｪ繧ｹ繝医〒繧・None 縺ｧ縺ｯ縺ｪ縺・


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
