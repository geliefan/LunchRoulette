#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｮ邨ｱ蜷医ユ繧ｹ繝・
蜷・ｨｮ繧ｨ繝ｩ繝ｼ迥ｶ豕√〒縺ｮ蜍穂ｽ懊ｒ繝・せ繝・
"""

import pytest
import tempfile
import os
import requests
from unittest.mock import patch, Mock, MagicMock
from cache_service import CacheService
from location_service import LocationService
from weather_service import WeatherService
from restaurant_service import RestaurantService
from distance_calculator import DistanceCalculator
from error_handler import ErrorHandler


class TestErrorHandling:
    """繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｮ邨ｱ蜷医ユ繧ｹ繝・""

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
            # Windows迺ｰ蠅・〒繝輔ぃ繧､繝ｫ縺御ｽｿ逕ｨ荳ｭ縺ｮ蝣ｴ蜷医・辟｡隕・
            pass

    @pytest.fixture
    def cache_service(self, temp_db_path):
        """繝・せ繝育畑CacheService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ"""
        return CacheService(db_path=temp_db_path)

    def test_cache_service_database_error_handling(self, temp_db_path):
        """CacheService 繝・・繧ｿ繝吶・繧ｹ繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        cache_service = CacheService(db_path='/invalid/path/cache.db')

        # 繝・・繧ｿ繝吶・繧ｹ繧｢繧ｯ繧ｻ繧ｹ繧ｨ繝ｩ繝ｼ譎ゅ・蜍穂ｽ懃｢ｺ隱・
        result = cache_service.set_cached_data('test_key', {'data': 'test'})
        assert result is False

        retrieved_data = cache_service.get_cached_data('test_key')
        assert retrieved_data is None

        delete_result = cache_service.delete_cached_data('test_key')
        assert delete_result is False

    def test_cache_service_serialization_error_handling(self, cache_service):
        """CacheService 繧ｷ繝ｪ繧｢繝ｩ繧､繧ｼ繝ｼ繧ｷ繝ｧ繝ｳ繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        # 繧ｷ繝ｪ繧｢繝ｩ繧､繧ｺ縺ｧ縺阪↑縺・が繝悶ず繧ｧ繧ｯ繝・
        def unserializable_data(x):
            return x  # 髢｢謨ｰ繧ｪ繝悶ず繧ｧ繧ｯ繝・

        with pytest.raises(ValueError, match="繝・・繧ｿ縺ｮ繧ｷ繝ｪ繧｢繝ｩ繧､繧ｺ縺ｫ螟ｱ謨・):
            cache_service.serialize_data(unserializable_data)

        # 辟｡蜉ｹ縺ｪJSON譁・ｭ怜・
        with pytest.raises(ValueError, match="繝・・繧ｿ縺ｮ繝・す繝ｪ繧｢繝ｩ繧､繧ｺ縺ｫ螟ｱ謨・):
            cache_service.deserialize_data("invalid json {")

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

    @patch('location_service.requests.get')
    def test_location_service_api_error_handling(self, mock_get, cache_service):
        """LocationService API繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        location_service = LocationService(cache_service=cache_service)

        # API繧ｨ繝ｩ繝ｼ繝ｬ繧ｹ繝昴Φ繧ｹ繧偵す繝溘Η繝ｬ繝ｼ繝・
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'error': True,
            'reason': 'Invalid IP address'
        }
        mock_get.return_value = mock_response

        result = location_service.get_location_from_ip('invalid.ip')

        # 繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result['source'] == 'default'

    @patch('location_service.requests.get')
    def test_location_service_rate_limit_handling(self, mock_get, cache_service):
        """LocationService 繝ｬ繝ｼ繝亥宛髯舌ワ繝ｳ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        location_service = LocationService(cache_service=cache_service)

        # 莠句燕縺ｫ繧ｭ繝｣繝・す繝･繝・・繧ｿ繧定ｨｭ螳・
        cache_service.generate_cache_key('location', ip='192.168.1.1')
        old_data = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '蜊・ｻ｣逕ｰ蛹ｺ',
            'source': 'ipapi.co'
        }

        # 譛滄剞蛻・ｌ繧ｭ繝｣繝・す繝･繧堤峩謗･繝・・繧ｿ繝吶・繧ｹ縺ｫ謖ｿ蜈･
        with patch('location_service.get_db_connection') as mock_get_db_connection:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_get_db_connection.return_value.__enter__.return_value = mock_conn
            mock_conn.execute.return_value = mock_cursor
            mock_cursor.fetchone.return_value = {
                'data': cache_service.serialize_data(old_data)
            }

            # 繝ｬ繝ｼ繝亥宛髯舌お繝ｩ繝ｼ繧偵す繝溘Η繝ｬ繝ｼ繝・
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")
            mock_get.return_value = mock_response

            result = location_service.get_location_from_ip('192.168.1.1')

            # 繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繧ｭ繝｣繝・す繝･繝・・繧ｿ縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
            assert result['source'] == 'fallback_cache'

    @patch('weather_service.requests.get')
    def test_weather_service_api_error_handling(self, mock_get, cache_service):
        """WeatherService API繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        weather_service = WeatherService(api_key="test_key", cache_service=cache_service)

        # 隱崎ｨｼ繧ｨ繝ｩ繝ｼ繧偵す繝溘Η繝ｬ繝ｼ繝・
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_get.return_value = mock_response

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # 繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌玲ュ蝣ｱ縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result['source'] == 'default'
        assert result['temperature'] == 20.0
        assert result['condition'] == 'clear'

    def test_weather_service_no_api_key_handling(self, cache_service):
        """WeatherService API繧ｭ繝ｼ縺ｪ縺励ワ繝ｳ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        weather_service = WeatherService(api_key=None, cache_service=cache_service)

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # 繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌玲ュ蝣ｱ縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result['source'] == 'default'

    @patch('restaurant_service.requests.get')
    def test_restaurant_service_api_error_handling(self, mock_get, cache_service):
        """RestaurantService API繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        restaurant_service = RestaurantService(api_key="test_key", cache_service=cache_service)

        # HTTP繧ｨ繝ｩ繝ｼ繧偵す繝溘Η繝ｬ繝ｼ繝・
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Internal Server Error")
        mock_get.return_value = mock_response

        result = restaurant_service.search_restaurants(35.6812, 139.7671)

        # 遨ｺ縺ｮ繝ｪ繧ｹ繝医′霑斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result == []

    def test_restaurant_service_no_api_key_handling(self, cache_service):
        """RestaurantService API繧ｭ繝ｼ縺ｪ縺励ワ繝ｳ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        restaurant_service = RestaurantService(api_key=None, cache_service=cache_service)

        result = restaurant_service.search_restaurants(35.6812, 139.7671)

        # 遨ｺ縺ｮ繝ｪ繧ｹ繝医′霑斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result == []

    def test_distance_calculator_invalid_input_handling(self):
        """DistanceCalculator 辟｡蜉ｹ蜈･蜉帙ワ繝ｳ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        error_handler = ErrorHandler()
        distance_calculator = DistanceCalculator(error_handler=error_handler)

        # 辟｡蜉ｹ縺ｪ蠎ｧ讓吶〒縺ｮ險育ｮ・
        with pytest.raises(ValueError):
            distance_calculator.calculate_distance(95.0, 139.0, 35.0, 139.0)

        with pytest.raises(ValueError):
            distance_calculator.calculate_distance("invalid", 139.0, 35.0, 139.0)

    def test_distance_calculator_calculation_error_handling(self):
        """DistanceCalculator 險育ｮ励お繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        mock_error_handler = Mock()
        mock_error_handler.handle_distance_calculation_error.return_value = {
            'message': 'Distance calculation error',
            'fallback_distance': 0.5
        }

        distance_calculator = DistanceCalculator(error_handler=mock_error_handler)

        # math繝｢繧ｸ繝･繝ｼ繝ｫ縺ｧ繧ｨ繝ｩ繝ｼ繧堤匱逕溘＆縺帙ｋ
        with patch('math.sin', side_effect=Exception("Math error")):
            result = distance_calculator.calculate_distance(35.0, 139.0, 36.0, 140.0)

            # 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ縺悟他縺ｰ繧後∵ｦらｮ苓ｷ晞屬縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
            mock_error_handler.handle_distance_calculation_error.assert_called_once()
            assert isinstance(result, float)
            assert result > 0

    def test_distance_calculator_walking_distance_error_handling(self):
        """DistanceCalculator 蠕呈ｭｩ霍晞屬險育ｮ励お繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        mock_error_handler = Mock()
        mock_error_handler.handle_distance_calculation_error.return_value = {
            'message': 'Walking distance calculation error'
        }

        distance_calculator = DistanceCalculator(error_handler=mock_error_handler)

        # calculate_distance縺ｧ繧ｨ繝ｩ繝ｼ繧堤匱逕溘＆縺帙ｋ
        with patch.object(distance_calculator, 'calculate_distance', side_effect=Exception("Distance error")):
            result = distance_calculator.calculate_walking_distance(35.0, 139.0, 36.0, 140.0)

            # 繧ｨ繝ｩ繝ｼ譎ゅ・繝・ヵ繧ｩ繝ｫ繝亥､縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
            assert result['distance_km'] == 0.5
            assert result['distance_m'] == 500
            assert result['walking_time_minutes'] == 8
            assert 'error_info' in result

    def test_error_handler_distance_calculation_error(self):
        """ErrorHandler 霍晞屬險育ｮ励お繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        error_handler = ErrorHandler()

        test_error = ValueError("Test distance calculation error")
        result = error_handler.handle_distance_calculation_error(test_error)

        assert 'message' in result
        assert 'error_type' in result
        assert 'timestamp' in result
        assert result['error_type'] == 'ValueError'

    def test_multiple_service_error_cascade(self, cache_service):
        """隍・焚繧ｵ繝ｼ繝薙せ繧ｨ繝ｩ繝ｼ繧ｫ繧ｹ繧ｱ繝ｼ繝峨ユ繧ｹ繝・""
        # 縺吶∋縺ｦ縺ｮ繧ｵ繝ｼ繝薙せ縺ｧ繧ｨ繝ｩ繝ｼ縺檎匱逕溘☆繧狗憾豕√ｒ繧ｷ繝溘Η繝ｬ繝ｼ繝・

        # LocationService: 繝阪ャ繝医Ρ繝ｼ繧ｯ繧ｨ繝ｩ繝ｼ
        with patch('location_service.requests.get', side_effect=requests.exceptions.ConnectionError("Network error")):
            location_service = LocationService(cache_service=cache_service)
            location_result = location_service.get_location_from_ip('192.168.1.1')
            assert location_result['source'] == 'default'

        # WeatherService: API繧ｭ繝ｼ縺ｪ縺・
        weather_service = WeatherService(api_key=None, cache_service=cache_service)
        weather_result = weather_service.get_current_weather(35.6812, 139.7671)
        assert weather_result['source'] == 'default'

        # RestaurantService: API繧ｭ繝ｼ縺ｪ縺・
        restaurant_service = RestaurantService(api_key=None, cache_service=cache_service)
        restaurant_result = restaurant_service.search_restaurants(35.6812, 139.7671)
        assert restaurant_result == []

        # DistanceCalculator: 險育ｮ励お繝ｩ繝ｼ
        mock_error_handler = Mock()
        mock_error_handler.handle_distance_calculation_error.return_value = {
            'message': 'Error'
        }
        distance_calculator = DistanceCalculator(error_handler=mock_error_handler)

        with patch('math.sin', side_effect=Exception("Math error")):
            distance_result = distance_calculator.calculate_distance(35.0, 139.0, 36.0, 140.0)
            assert isinstance(distance_result, float)

    def test_graceful_degradation_scenario(self, cache_service):
        """繧ｰ繝ｬ繝ｼ繧ｹ繝輔Ν繝・げ繝ｩ繝・・繧ｷ繝ｧ繝ｳ繧ｷ繝翫Μ繧ｪ繝・せ繝・""
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

        # WeatherService: API繧ｨ繝ｩ繝ｼ 竊・繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌・
        with patch('weather_service.requests.get', side_effect=requests.exceptions.HTTPError("API Error")):
            weather_service = WeatherService(api_key="test_key", cache_service=cache_service)
            weather_result = weather_service.get_current_weather(35.6812, 139.7671)
            assert weather_result['source'] == 'default'

        # RestaurantService: API繧ｨ繝ｩ繝ｼ 竊・遨ｺ繝ｪ繧ｹ繝・
        with patch('restaurant_service.requests.get', side_effect=requests.exceptions.HTTPError("API Error")):
            restaurant_service = RestaurantService(api_key="test_key", cache_service=cache_service)
            restaurant_result = restaurant_service.search_restaurants(35.6812, 139.7671)
            assert restaurant_result == []

        # 繧ｷ繧ｹ繝・Β蜈ｨ菴薙→縺励※縺ｯ驛ｨ蛻・噪縺ｫ蜍穂ｽ懊☆繧九％縺ｨ繧堤｢ｺ隱・
        assert location_result is not None
        assert weather_result is not None
        assert restaurant_result is not None  # 遨ｺ繝ｪ繧ｹ繝医〒繧・None 縺ｧ縺ｯ縺ｪ縺・


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
