#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
譛邨らｵｱ蜷医ユ繧ｹ繝・
Flask 繧ｨ繝ｳ繝峨・繧､繝ｳ繝医√ョ繝ｼ繧ｿ繝吶・繧ｹ謫堺ｽ懊√お繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｮ邨ｱ蜷医ユ繧ｹ繝・

縺薙・繝・せ繝医ヵ繧｡繧､繝ｫ縺ｯ task 9.2 縺ｮ隕∽ｻｶ繧呈ｺ縺溘＠縺ｾ縺・
- Flask 繧ｨ繝ｳ繝峨・繧､繝ｳ繝医・繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・
- 繝・・繧ｿ繝吶・繧ｹ謫堺ｽ懊・繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・
- 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｮ繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・
"""

import pytest
import json
import tempfile
import os
import sqlite3
import requests
from unittest.mock import patch
from datetime import datetime, timedelta

from app import app
from database import init_database, get_db_connection, cleanup_expired_cache, get_cache_stats
from cache_service import CacheService
from location_service import LocationService
from weather_service import WeatherService
from restaurant_service import RestaurantService
from distance_calculator import DistanceCalculator
from error_handler import ErrorHandler


class TestIntegrationFinal:
    """譛邨らｵｱ蜷医ユ繧ｹ繝医け繝ｩ繧ｹ"""

    @pytest.fixture
    def temp_db_path(self):
        """繝・せ繝育畑縺ｮ荳譎ゅョ繝ｼ繧ｿ繝吶・繧ｹ繝輔ぃ繧､繝ｫ繝代せ"""
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

    def test_main_page_endpoint_loads_successfully(self, client):
        """繝｡繧､繝ｳ繝壹・繧ｸ繧ｨ繝ｳ繝峨・繧､繝ｳ繝域ｭ｣蟶ｸ隱ｭ縺ｿ霎ｼ縺ｿ繝・せ繝・""
        response = client.get('/')

        assert response.status_code == 200
        assert response.content_type.startswith('text/html')

        # HTML繧ｳ繝ｳ繝・Φ繝・・蝓ｺ譛ｬ遒ｺ隱・
        html_content = response.data.decode('utf-8')
        assert '<!DOCTYPE html>' in html_content
        assert '繝ｫ繝ｼ繝ｬ繝・ヨ繧貞屓縺・ in html_content
        assert '<title>' in html_content

    def test_roulette_endpoint_with_coordinates(self, client):
        """繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝亥ｺｧ讓呎欠螳壹ユ繧ｹ繝・""
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
        # API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺・↑縺・ｴ蜷医・繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｉ縺ｪ縺・
        if data.get('success'):
            assert 'restaurant' in data
            assert 'distance' in data
        else:
            assert data['success'] is False
            assert 'message' in data

    def test_roulette_endpoint_without_coordinates(self, client):
        """繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝亥ｺｧ讓吶↑縺励ユ繧ｹ繝・""
        request_data = {}

        response = client.post('/roulette',
                               data=json.dumps(request_data),
                               content_type='application/json')

        assert response.status_code == 200
        assert response.content_type == 'application/json'

        data = response.get_json()
        # 蠎ｧ讓吶′縺ｪ縺・ｴ蜷医・IP縺九ｉ蜿門ｾ励＆繧後ｋ
        assert 'success' in data

    def test_roulette_endpoint_invalid_json(self, client):
        """繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝育┌蜉ｹJSON繝・せ繝・""
        response = client.post('/roulette',
                               data='invalid json',
                               content_type='application/json')

        # 辟｡蜉ｹ縺ｪJSON縺ｯ500繧ｨ繝ｩ繝ｼ縺ｫ縺ｪ繧・
        assert response.status_code == 500

        data = response.get_json()
        assert data['error'] is True
        assert 'message' in data

    def test_404_error_handler(self, client):
        """404繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ繝・せ繝・""
        response = client.get('/nonexistent-page')

        assert response.status_code == 404

        if response.content_type == 'application/json':
            data = response.get_json()
            assert data['error'] is True
            assert '繝壹・繧ｸ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ' in data['message']

    def test_method_not_allowed(self, client):
        """繝｡繧ｽ繝・ラ荳崎ｨｱ蜿ｯ繝・せ繝・""
        # POST繧ｨ繝ｳ繝峨・繧､繝ｳ繝医↓GET繝ｪ繧ｯ繧ｨ繧ｹ繝・
        response = client.get('/roulette')

        assert response.status_code == 405

    def test_endpoint_with_large_request(self, client):
        """螟ｧ縺阪↑繝ｪ繧ｯ繧ｨ繧ｹ繝亥・逅・ユ繧ｹ繝・""
        large_data = {
            'latitude': 35.6812,
            'longitude': 139.7671,
            'extra_data': 'x' * 10000  # 10KB 縺ｮ菴吝・縺ｪ繝・・繧ｿ
        }

        response = client.post('/roulette',
                               data=json.dumps(large_data),
                               content_type='application/json')

        # 螟ｧ縺阪↑繝ｪ繧ｯ繧ｨ繧ｹ繝医〒繧ょ・逅・＆繧後ｋ・亥ｿ・ｦ√↑驛ｨ蛻・・縺ｿ菴ｿ逕ｨ・・
        assert response.status_code in [200, 413]

    # =============================================================================
    # 繝・・繧ｿ繝吶・繧ｹ謫堺ｽ懊・繝・せ繝医こ繝ｼ繧ｹ
    # =============================================================================

    def test_database_initialization(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹悶ユ繧ｹ繝・""
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

    def test_database_connection(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ謗･邯壹ユ繧ｹ繝・""
        init_database(temp_db_path)

        with get_db_connection(temp_db_path) as conn:
            assert conn is not None

            # 蝓ｺ譛ｬ逧・↑繧ｯ繧ｨ繝ｪ螳溯｡後ユ繧ｹ繝・
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            count = cursor.fetchone()[0]
            assert count == 0

    def test_cache_crud_operations(self, cache_service):
        """繧ｭ繝｣繝・す繝･CRUD謫堺ｽ懊ユ繧ｹ繝・""
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

    def test_cache_expiration_cleanup(self, temp_db_path):
        """繧ｭ繝｣繝・す繝･譛滄剞蛻・ｌ繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・繝・せ繝・""
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

    def test_database_statistics(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ邨ｱ險医ユ繧ｹ繝・""
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

    def test_database_concurrent_access(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ蜷梧凾繧｢繧ｯ繧ｻ繧ｹ繝・せ繝・""
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

    def test_database_transaction_rollback(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ繝医Λ繝ｳ繧ｶ繧ｯ繧ｷ繝ｧ繝ｳ繝ｭ繝ｼ繝ｫ繝舌ャ繧ｯ繝・せ繝・""
        init_database(temp_db_path)

        try:
            with get_db_connection(temp_db_path) as conn:
                # 豁｣蟶ｸ縺ｪ繝・・繧ｿ謖ｿ蜈･
                conn.execute("""
                    INSERT INTO cache (cache_key, data, expires_at)
                    VALUES (?, ?, ?)
                """, ('test_key', '{"test": "data"}', datetime.now() + timedelta(hours=1)))

                # 諢丞峙逧・↓繧ｨ繝ｩ繝ｼ繧堤匱逕溘＆縺帙ｋ・育┌蜉ｹ縺ｪSQL・・
                conn.execute("INVALID SQL STATEMENT")

        except sqlite3.Error:
            # 繧ｨ繝ｩ繝ｼ縺檎匱逕溘☆繧九％縺ｨ繧呈悄蠕・
            pass

        # 繝医Λ繝ｳ繧ｶ繧ｯ繧ｷ繝ｧ繝ｳ縺後Ο繝ｼ繝ｫ繝舌ャ繧ｯ縺輔ｌ縺ｦ縺・ｋ縺薙→繧堤｢ｺ隱・
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            count = cursor.fetchone()[0]
            assert count == 0

    # =============================================================================
    # 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｮ繝・せ繝医こ繝ｼ繧ｹ
    # =============================================================================

    def test_cache_service_database_error_handling(self):
        """CacheService 繝・・繧ｿ繝吶・繧ｹ繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
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
    def test_location_service_network_error_handling(self, mock_get, cache_service):
        """LocationService 繝阪ャ繝医Ρ繝ｼ繧ｯ繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        location_service = LocationService(cache_service=cache_service)

        # 繝阪ャ繝医Ρ繝ｼ繧ｯ繧ｨ繝ｩ繝ｼ繧偵す繝溘Η繝ｬ繝ｼ繝・
        mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")

        result = location_service.get_location_from_ip('192.168.1.1')

        # 繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result['source'] == 'default'
        assert result['city'] == '譚ｱ莠ｬ'
        assert result['latitude'] == 35.6812
        assert result['longitude'] == 139.7671

    def test_weather_service_no_api_key_handling(self, cache_service):
        """WeatherService API繧ｭ繝ｼ縺ｪ縺励ワ繝ｳ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        weather_service = WeatherService(api_key=None, cache_service=cache_service)

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # 繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌玲ュ蝣ｱ縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result['source'] == 'default'
        assert result['temperature'] == 20.0
        assert result['condition'] == 'clear'

    def test_restaurant_service_no_api_key_handling(self, cache_service):
        """RestaurantService API繧ｭ繝ｼ縺ｪ縺励ワ繝ｳ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        restaurant_service = RestaurantService(api_key=None, cache_service=cache_service)

        result = restaurant_service.search_restaurants(35.6812, 139.7671)

        # 遨ｺ縺ｮ繝ｪ繧ｹ繝医′霑斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result == []

    def test_distance_calculator_error_handling(self):
        """DistanceCalculator 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        error_handler = ErrorHandler()
        distance_calculator = DistanceCalculator(error_handler=error_handler)

        # 辟｡蜉ｹ縺ｪ蠎ｧ讓吶〒縺ｮ險育ｮ暦ｼ医お繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺輔ｌ繧具ｼ・
        result = distance_calculator.calculate_distance(95.0, 139.0, 35.0, 139.0)

        # 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｫ繧医ｊ讎らｮ怜､縺瑚ｿ斐＆繧後ｋ
        assert isinstance(result, float)
        assert result > 0

    def test_error_handler_basic_functionality(self):
        """ErrorHandler 蝓ｺ譛ｬ讖溯・繝・せ繝・""
        error_handler = ErrorHandler()

        # 霍晞屬險育ｮ励お繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・
        test_error = ValueError("Test distance calculation error")
        result = error_handler.handle_distance_calculation_error(test_error)

        assert 'message' in result
        assert 'suggestion' in result
        assert 'severity' in result
        assert result['fallback_used'] is True

    def test_service_graceful_degradation(self, cache_service):
        """繧ｵ繝ｼ繝薙せ繧ｰ繝ｬ繝ｼ繧ｹ繝輔Ν繝・げ繝ｩ繝・・繧ｷ繝ｧ繝ｳ繝・せ繝・""
        # LocationService: 繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ菴ｿ逕ｨ
        location_service = LocationService(cache_service=cache_service)
        location_result = location_service.get_location_from_ip('invalid.ip')
        assert location_result['source'] == 'default'

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

    def test_application_error_recovery(self, client):
        """繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧ｨ繝ｩ繝ｼ蝗槫ｾｩ繝・せ繝・""
        # 1. 豁｣蟶ｸ縺ｪ繝ｪ繧ｯ繧ｨ繧ｹ繝・
        response = client.get('/')
        assert response.status_code == 200

        # 2. 繧ｨ繝ｩ繝ｼ縺檎匱逕溘☆繧九Μ繧ｯ繧ｨ繧ｹ繝・
        response = client.post('/roulette',
                               data='invalid json',
                               content_type='application/json')
        assert response.status_code == 500

        # 3. 蜀榊ｺｦ豁｣蟶ｸ縺ｪ繝ｪ繧ｯ繧ｨ繧ｹ繝茨ｼ医い繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺悟屓蠕ｩ縺励※縺・ｋ縺薙→繧堤｢ｺ隱搾ｼ・
        response = client.get('/')
        assert response.status_code == 200

    # =============================================================================
    # 邨ｱ蜷医す繝翫Μ繧ｪ繝・せ繝・
    # =============================================================================

    def test_full_application_workflow(self, client):
        """繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ蜈ｨ菴薙Ρ繝ｼ繧ｯ繝輔Ο繝ｼ繝・せ繝・""
        # 1. 繝｡繧､繝ｳ繝壹・繧ｸ繧｢繧ｯ繧ｻ繧ｹ
        response = client.get('/')
        assert response.status_code == 200

        # 2. 繝ｫ繝ｼ繝ｬ繝・ヨ螳溯｡・
        request_data = {
            'latitude': 35.6812,
            'longitude': 139.7671
        }

        response = client.post('/roulette',
                               data=json.dumps(request_data),
                               content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()

        # 謌仙粥縺ｾ縺溘・繧ｨ繝ｩ繝ｼ繝ｬ繧ｹ繝昴Φ繧ｹ縺瑚ｿ斐＆繧後ｋ
        assert 'success' in data or 'error' in data

        # 3. 蟄伜惠縺励↑縺・・繝ｼ繧ｸ繧｢繧ｯ繧ｻ繧ｹ・・04繧ｨ繝ｩ繝ｼ・・
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_database_and_cache_integration(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ縺ｨ繧ｭ繝｣繝・す繝･邨ｱ蜷医ユ繧ｹ繝・""
        # 繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹・
        init_database(temp_db_path)

        # 繧ｭ繝｣繝・す繝･繧ｵ繝ｼ繝薙せ菴懈・
        cache_service = CacheService(db_path=temp_db_path)

        # 繝・・繧ｿ菫晏ｭ倥・蜿門ｾ励・蜑企勁縺ｮ荳騾｣縺ｮ豬√ｌ
        test_data = {'integration': 'test', 'timestamp': datetime.now().isoformat()}
        cache_key = cache_service.generate_cache_key('integration', test='final')

        # 菫晏ｭ・
        assert cache_service.set_cached_data(cache_key, test_data, ttl=300) is True

        # 蜿門ｾ・
        retrieved = cache_service.get_cached_data(cache_key)
        assert retrieved == test_data

        # 邨ｱ險育｢ｺ隱・
        stats = get_cache_stats(temp_db_path)
        assert stats['total_records'] >= 1
        assert stats['valid_records'] >= 1

        # 蜑企勁
        assert cache_service.delete_cached_data(cache_key) is True

        # 蜑企勁蠕檎｢ｺ隱・
        assert cache_service.get_cached_data(cache_key) is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
