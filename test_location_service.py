#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LocationService縺ｮ蜊倅ｽ薙ユ繧ｹ繝・
IP繧｢繝峨Ξ繧ｹ縺九ｉ菴咲ｽｮ諠・ｱ繧貞叙蠕励☆繧区ｩ溯・繧偵ユ繧ｹ繝・
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from location_service import LocationService
from cache_service import CacheService


class TestLocationService:
    """LocationService繧ｯ繝ｩ繧ｹ縺ｮ蜊倅ｽ薙ユ繧ｹ繝・""

    @pytest.fixture
    def mock_cache_service(self):
        """繝｢繝・けCacheService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ"""
        mock_cache = Mock(spec=CacheService)
        mock_cache.generate_cache_key.return_value = "location_test_key"
        mock_cache.get_cached_data.return_value = None
        mock_cache.set_cached_data.return_value = True
        return mock_cache

    @pytest.fixture
    def location_service(self, mock_cache_service):
        """繝・せ繝育畑LocationService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ"""
        return LocationService(cache_service=mock_cache_service)

    def test_init(self):
        """蛻晄悄蛹悶ユ繧ｹ繝・""
        service = LocationService()
        assert service.api_base_url == "https://ipapi.co"
        assert service.timeout == 10
        assert service.cache_service is not None

    def test_default_location_constant(self):
        """繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ螳壽焚繝・せ繝・""
        assert LocationService.DEFAULT_LOCATION['latitude'] == 35.6812
        assert LocationService.DEFAULT_LOCATION['longitude'] == 139.7671
        assert LocationService.DEFAULT_LOCATION['city'] == '譚ｱ莠ｬ'
        assert LocationService.DEFAULT_LOCATION['country'] == '譌･譛ｬ'

    @patch('location_service.requests.get')
    def test_get_location_from_ip_success(self, mock_get, location_service, mock_cache_service):
        """菴咲ｽｮ諠・ｱ蜿門ｾ玲・蜉溘ユ繧ｹ繝・""
        # 繝｢繝・けAPI繝ｬ繧ｹ繝昴Φ繧ｹ
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '蜊・ｻ｣逕ｰ蛹ｺ',
            'region': '譚ｱ莠ｬ驛ｽ',
            'country_name': '譌･譛ｬ',
            'country_code': 'JP',
            'postal': '100-0001',
            'timezone': 'Asia/Tokyo'
        }
        mock_get.return_value = mock_response

        result = location_service.get_location_from_ip('192.168.1.1')

        # 邨先棡縺ｮ讀懆ｨｼ
        assert result['latitude'] == 35.6762
        assert result['longitude'] == 139.6503
        assert result['city'] == '蜊・ｻ｣逕ｰ蛹ｺ'
        assert result['region'] == '譚ｱ莠ｬ驛ｽ'
        assert result['country'] == '譌･譛ｬ'
        assert result['country_code'] == 'JP'
        assert result['source'] == 'ipapi.co'

        # API縺梧ｭ｣縺励￥蜻ｼ縺ｰ繧後◆縺薙→繧堤｢ｺ隱・
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'https://ipapi.co/192.168.1.1/json/' in call_args[0][0]

        # 繧ｭ繝｣繝・す繝･縺ｫ菫晏ｭ倥＆繧後◆縺薙→繧堤｢ｺ隱・
        mock_cache_service.set_cached_data.assert_called_once()

    @patch('location_service.requests.get')
    def test_get_location_from_ip_auto_detect(self, mock_get, location_service):
        """閾ｪ蜍肘P讀懷・繝・せ繝・""
        # 繝｢繝・けAPI繝ｬ繧ｹ繝昴Φ繧ｹ
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '譚ｱ莠ｬ',
            'region': '譚ｱ莠ｬ驛ｽ',
            'country_name': '譌･譛ｬ',
            'country_code': 'JP'
        }
        mock_get.return_value = mock_response

        location_service.get_location_from_ip()

        # 閾ｪ蜍墓､懷・逕ｨURL縺悟他縺ｰ繧後◆縺薙→繧堤｢ｺ隱・
        call_args = mock_get.call_args
        assert call_args[0][0] == 'https://ipapi.co/json/'

    def test_get_location_from_ip_cached(self, location_service, mock_cache_service):
        """繧ｭ繝｣繝・す繝･縺輔ｌ縺滉ｽ咲ｽｮ諠・ｱ蜿門ｾ励ユ繧ｹ繝・""
        # 繧ｭ繝｣繝・す繝･繝・・繧ｿ繧定ｨｭ螳・
        cached_data = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '譚ｱ莠ｬ',
            'source': 'ipapi.co'
        }
        mock_cache_service.get_cached_data.return_value = cached_data

        result = location_service.get_location_from_ip('192.168.1.1')

        # 繧ｭ繝｣繝・す繝･繝・・繧ｿ縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result == cached_data

        # API縺悟他縺ｰ繧後↑縺・％縺ｨ繧堤｢ｺ隱・
        mock_cache_service.get_cached_data.assert_called_once()

    @patch('location_service.requests.get')
    def test_get_location_from_ip_http_error(self, mock_get, location_service):
        """HTTP 繧ｨ繝ｩ繝ｼ譎ゅ・繝・せ繝・""
        # HTTP繧ｨ繝ｩ繝ｼ繧偵す繝溘Η繝ｬ繝ｼ繝・
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        result = location_service.get_location_from_ip('invalid.ip')

        # 繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result['source'] == 'default'
        assert result['city'] == '譚ｱ莠ｬ'
        assert result['latitude'] == 35.6812
        assert result['longitude'] == 139.7671

    @patch('location_service.requests.get')
    def test_get_location_from_ip_rate_limit(self, mock_get, location_service, mock_cache_service):
        """繝ｬ繝ｼ繝亥宛髯舌お繝ｩ繝ｼ譎ゅ・繝・せ繝・""
        # 繝ｬ繝ｼ繝亥宛髯舌お繝ｩ繝ｼ繧偵す繝溘Η繝ｬ繝ｼ繝・
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")
        mock_get.return_value = mock_response

        # 繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繧ｭ繝｣繝・す繝･繝・・繧ｿ繧定ｨｭ螳・
        fallback_data = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '譚ｱ莠ｬ',
            'source': 'fallback_cache'
        }

        with patch.object(location_service, '_get_fallback_cache_data', return_value=fallback_data):
            result = location_service.get_location_from_ip('192.168.1.1')

            # 繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繝・・繧ｿ縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
            assert result == fallback_data

    @patch('location_service.requests.get')
    def test_get_location_from_ip_network_error(self, mock_get, location_service):
        """繝阪ャ繝医Ρ繝ｼ繧ｯ繧ｨ繝ｩ繝ｼ譎ゅ・繝・せ繝・""
        # 繝阪ャ繝医Ρ繝ｼ繧ｯ繧ｨ繝ｩ繝ｼ繧偵す繝溘Η繝ｬ繝ｼ繝・
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        result = location_service.get_location_from_ip('192.168.1.1')

        # 繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert result['source'] == 'default'
        assert result['city'] == '譚ｱ莠ｬ'

    @patch('location_service.requests.get')
    def test_get_location_from_ip_api_error_response(self, mock_get, location_service):
        """API 繧ｨ繝ｩ繝ｼ繝ｬ繧ｹ繝昴Φ繧ｹ譎ゅ・繝・せ繝・""
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

    def test_format_location_data_success(self, location_service):
        """菴咲ｽｮ諠・ｱ繝・・繧ｿ謨ｴ蠖｢謌仙粥繝・せ繝・""
        api_data = {
            'latitude': '35.6762',
            'longitude': '139.6503',
            'city': '蜊・ｻ｣逕ｰ蛹ｺ',
            'region': '譚ｱ莠ｬ驛ｽ',
            'country_name': '譌･譛ｬ',
            'country_code': 'JP',
            'postal': '100-0001',
            'timezone': 'Asia/Tokyo'
        }

        result = location_service._format_location_data(api_data)

        assert result['latitude'] == 35.6762
        assert result['longitude'] == 139.6503
        assert result['city'] == '蜊・ｻ｣逕ｰ蛹ｺ'
        assert result['region'] == '譚ｱ莠ｬ驛ｽ'
        assert result['country'] == '譌･譛ｬ'
        assert result['country_code'] == 'JP'
        assert result['postal'] == '100-0001'
        assert result['timezone'] == 'Asia/Tokyo'
        assert result['source'] == 'ipapi.co'

    def test_format_location_data_missing_fields(self, location_service):
        """菴咲ｽｮ諠・ｱ繝・・繧ｿ謨ｴ蠖｢・医ヵ繧｣繝ｼ繝ｫ繝我ｸ崎ｶｳ・峨ユ繧ｹ繝・""
        api_data = {
            'latitude': '35.6762',
            'longitude': '139.6503'
            # 莉悶・繝輔ぅ繝ｼ繝ｫ繝峨・荳崎ｶｳ
        }

        result = location_service._format_location_data(api_data)

        assert result['latitude'] == 35.6762
        assert result['longitude'] == 139.6503
        assert result['city'] == '荳肴・'
        assert result['region'] == '荳肴・'
        assert result['country'] == '荳肴・'
        assert result['country_code'] == 'XX'

    def test_format_location_data_invalid_coordinates(self, location_service):
        """菴咲ｽｮ諠・ｱ繝・・繧ｿ謨ｴ蠖｢・育┌蜉ｹ縺ｪ蠎ｧ讓呻ｼ峨ユ繧ｹ繝・""
        api_data = {
            'latitude': 'invalid',
            'longitude': 'invalid',
            'city': '譚ｱ莠ｬ'
        }

        with pytest.raises(KeyError):
            location_service._format_location_data(api_data)

    def test_get_coordinates(self, location_service, mock_cache_service):
        """蠎ｧ讓吝叙蠕励ユ繧ｹ繝・""
        # 繧ｭ繝｣繝・す繝･繝・・繧ｿ繧定ｨｭ螳・
        cached_data = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '譚ｱ莠ｬ'
        }
        mock_cache_service.get_cached_data.return_value = cached_data

        lat, lon = location_service.get_coordinates('192.168.1.1')

        assert lat == 35.6762
        assert lon == 139.6503

    def test_is_default_location(self, location_service):
        """繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ蛻､螳壹ユ繧ｹ繝・""
        # 繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ
        default_location = {'source': 'default', 'city': '譚ｱ莠ｬ'}
        assert location_service.is_default_location(default_location) is True

        # API蜿門ｾ嶺ｽ咲ｽｮ
        api_location = {'source': 'ipapi.co', 'city': '螟ｧ髦ｪ'}
        assert location_service.is_default_location(api_location) is False

    def test_validate_location_data_valid(self, location_service):
        """菴咲ｽｮ諠・ｱ繝・・繧ｿ螯･蠖捺ｧ讀懆ｨｼ・域怏蜉ｹ・峨ユ繧ｹ繝・""
        valid_data = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '譚ｱ莠ｬ',
            'region': '譚ｱ莠ｬ驛ｽ',
            'country': '譌･譛ｬ'
        }

        assert location_service.validate_location_data(valid_data) is True

    def test_validate_location_data_missing_fields(self, location_service):
        """菴咲ｽｮ諠・ｱ繝・・繧ｿ螯･蠖捺ｧ讀懆ｨｼ・医ヵ繧｣繝ｼ繝ｫ繝我ｸ崎ｶｳ・峨ユ繧ｹ繝・""
        invalid_data = {
            'latitude': 35.6762,
            'longitude': 139.6503
            # city, region, country 縺御ｸ崎ｶｳ
        }

        assert location_service.validate_location_data(invalid_data) is False

    def test_validate_location_data_invalid_coordinates(self, location_service):
        """菴咲ｽｮ諠・ｱ繝・・繧ｿ螯･蠖捺ｧ讀懆ｨｼ・育┌蜉ｹ縺ｪ蠎ｧ讓呻ｼ峨ユ繧ｹ繝・""
        # 邱ｯ蠎ｦ縺檎ｯ・峇螟・
        invalid_lat_data = {
            'latitude': 95.0,  # 90蠎ｦ繧定ｶ・∴繧・
            'longitude': 139.6503,
            'city': '譚ｱ莠ｬ',
            'region': '譚ｱ莠ｬ驛ｽ',
            'country': '譌･譛ｬ'
        }
        assert location_service.validate_location_data(invalid_lat_data) is False

        # 邨悟ｺｦ縺檎ｯ・峇螟・
        invalid_lon_data = {
            'latitude': 35.6762,
            'longitude': 185.0,  # 180蠎ｦ繧定ｶ・∴繧・
            'city': '譚ｱ莠ｬ',
            'region': '譚ｱ莠ｬ驛ｽ',
            'country': '譌･譛ｬ'
        }
        assert location_service.validate_location_data(invalid_lon_data) is False

    def test_validate_location_data_invalid_types(self, location_service):
        """菴咲ｽｮ諠・ｱ繝・・繧ｿ螯･蠖捺ｧ讀懆ｨｼ・育┌蜉ｹ縺ｪ蝙具ｼ峨ユ繧ｹ繝・""
        invalid_type_data = {
            'latitude': 'invalid',  # 譁・ｭ怜・
            'longitude': 139.6503,
            'city': '譚ｱ莠ｬ',
            'region': '譚ｱ莠ｬ驛ｽ',
            'country': '譌･譛ｬ'
        }

        assert location_service.validate_location_data(invalid_type_data) is False

    @patch('location_service.get_db_connection')
    def test_get_fallback_cache_data_success(self, mock_get_db_connection, location_service):
        """繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繧ｭ繝｣繝・す繝･繝・・繧ｿ蜿門ｾ玲・蜉溘ユ繧ｹ繝・""
        # 繝｢繝・け繝・・繧ｿ繝吶・繧ｹ謗･邯壹ｒ險ｭ螳・
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # 繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繝・・繧ｿ繧偵Δ繝・け
        fallback_data = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '譚ｱ莠ｬ'
        }
        mock_cursor.fetchone.return_value = {
            'data': location_service.cache_service.serialize_data(fallback_data)
        }

        with patch.object(location_service.cache_service, 'deserialize_data', return_value=fallback_data):
            result = location_service._get_fallback_cache_data('test_key')

            assert result is not None
            assert result['source'] == 'fallback_cache'

    @patch('location_service.get_db_connection')
    def test_get_fallback_cache_data_not_found(self, mock_get_db_connection, location_service):
        """繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繧ｭ繝｣繝・す繝･繝・・繧ｿ蜿門ｾ暦ｼ医ョ繝ｼ繧ｿ縺ｪ縺暦ｼ峨ユ繧ｹ繝・""
        # 繝｢繝・け繝・・繧ｿ繝吶・繧ｹ謗･邯壹ｒ險ｭ螳・
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # 繝・・繧ｿ縺瑚ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷医ｒ繝｢繝・け
        mock_cursor.fetchone.return_value = None

        result = location_service._get_fallback_cache_data('test_key')

        assert result is None

    def test_get_default_location(self, location_service):
        """繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ蜿門ｾ励ユ繧ｹ繝・""
        result = location_service._get_default_location()

        assert result['source'] == 'default'
        assert result['city'] == '譚ｱ莠ｬ'
        assert result['latitude'] == 35.6812
        assert result['longitude'] == 139.7671
        assert result['country'] == '譌･譛ｬ'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
