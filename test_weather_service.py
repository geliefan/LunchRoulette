#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeatherServiceの単体テスチE
OpenWeatherMap APIから天気情報を取得する機�EをテスチE
"""

import pytest
import requests
import os

from unittest.mock import Mock, patch, MagicMock
from weather_service import WeatherService
from cache_service import CacheService


class TestWeatherService:
    """WeatherServiceクラスの単体テスチE""

    @pytest.fixture
    def mock_cache_service(self):
        """モチE��CacheServiceインスタンス"""
        mock_cache = Mock(spec=CacheService)
        mock_cache.generate_cache_key.return_value = "weather_test_key"
        mock_cache.get_cached_data.return_value = None
        mock_cache.set_cached_data.return_value = True
        return mock_cache

    @pytest.fixture
    def weather_service(self, mock_cache_service):
        """チE��ト用WeatherServiceインスタンス"""
        return WeatherService(api_key="test_api_key", cache_service=mock_cache_service)

    @pytest.fixture
    def weather_service_no_key(self, mock_cache_service):
        """APIキーなし�EWeatherServiceインスタンス"""
        return WeatherService(api_key=None, cache_service=mock_cache_service)

    def test_init_with_api_key(self, mock_cache_service):
        """APIキーありの初期化テスチE""
        service = WeatherService(api_key="test_key", cache_service=mock_cache_service)
        assert service.api_key == "test_key"
        assert service.api_base_url == "https://api.openweathermap.org/data/3.0/onecall"
        assert service.timeout == 10
        assert service.cache_service is not None

    def test_init_without_api_key(self, mock_cache_service):
        """APIキーなし�E初期化テスチE""
        with patch.dict(os.environ, {}, clear=True):
            service = WeatherService(api_key=None, cache_service=mock_cache_service)
            assert service.api_key is None

    def test_init_with_env_api_key(self, mock_cache_service):
        """環墁E��数からのAPIキー取得テスチE""
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'env_api_key'}):
            service = WeatherService(cache_service=mock_cache_service)
            assert service.api_key == 'env_api_key'

    def test_default_weather_constant(self):
        """チE��ォルト天気定数チE��チE""
        assert WeatherService.DEFAULT_WEATHER['temperature'] == 20.0
        assert WeatherService.DEFAULT_WEATHER['condition'] == 'clear'
        assert WeatherService.DEFAULT_WEATHER['description'] == '晴めE
        assert WeatherService.DEFAULT_WEATHER['uv_index'] == 3.0

    def test_condition_mapping(self):
        """天気状況�EチE��ングチE��チE""
        mapping = WeatherService.CONDITION_MAPPING
        assert mapping['clear'] == '晴めE
        assert mapping['rain'] == '雨'
        assert mapping['clouds'] == '曁E��'
        assert mapping['snow'] == '雪'

    @patch('weather_service.requests.get')
    def test_get_current_weather_success(self, mock_get, weather_service, mock_cache_service):
        """天気情報取得�E功テスチE""
        # モチE��APIレスポンス
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'current': {
                'dt': 1640995200,  # 2022-01-01 00:00:00 UTC
                'temp': 25.5,
                'feels_like': 27.0,
                'humidity': 65,
                'pressure': 1013,
                'visibility': 10000,
                'uvi': 5.2,
                'wind_speed': 3.5,
                'wind_deg': 180,
                'clouds': 20,
                'sunrise': 1640995200,
                'sunset': 1641038400,
                'weather': [{
                    'main': 'Clear',
                    'description': '晴めE,
                    'icon': '01d'
                }]
            }
        }
        mock_get.return_value = mock_response

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # 結果の検証
        assert result['temperature'] == 25.5
        assert result['feels_like'] == 27.0
        assert result['condition'] == 'clear'
        assert result['description'] == '晴めE
        assert result['uv_index'] == 5.2
        assert result['humidity'] == 65
        assert result['pressure'] == 1013
        assert result['wind_speed'] == 3.5
        assert result['clouds'] == 20
        assert result['icon'] == '01d'
        assert result['source'] == 'openweathermap'

        # APIが正しく呼ばれたことを確誁E
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]['params']['lat'] == 35.6812
        assert call_args[1]['params']['lon'] == 139.7671
        assert call_args[1]['params']['appid'] == 'test_api_key'
        assert call_args[1]['params']['units'] == 'metric'
        assert call_args[1]['params']['lang'] == 'ja'

        # キャチE��ュに保存されたことを確誁E
        mock_cache_service.set_cached_data.assert_called_once()

    def test_get_current_weather_cached(self, weather_service, mock_cache_service):
        """キャチE��ュされた天気情報取得テスチE""
        # キャチE��ュチE�Eタを設宁E
        cached_data = {
            'temperature': 22.0,
            'condition': 'clouds',
            'description': '曁E��',
            'source': 'openweathermap'
        }
        mock_cache_service.get_cached_data.return_value = cached_data

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # キャチE��ュチE�Eタが返されることを確誁E
        assert result == cached_data

        # APIが呼ばれなぁE��とを確誁E
        mock_cache_service.get_cached_data.assert_called_once()

    def test_get_current_weather_no_api_key(self, weather_service_no_key):
        """APIキーなし�E天気情報取得テスチE""
        result = weather_service_no_key.get_current_weather(35.6812, 139.7671)

        # チE��ォルト天気情報が返されることを確誁E
        assert result['source'] == 'default'
        assert result['temperature'] == 20.0
        assert result['condition'] == 'clear'
        assert result['description'] == '晴めE

    @patch('weather_service.requests.get')
    def test_get_current_weather_http_error(self, mock_get, weather_service):
        """HTTP エラー時�EチE��チE""
        # HTTPエラーをシミュレーチE
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # チE��ォルト天気情報が返されることを確誁E
        assert result['source'] == 'default'

    @patch('weather_service.requests.get')
    def test_get_current_weather_rate_limit(self, mock_get, weather_service, mock_cache_service):
        """レート制限エラー時�EチE��チE""
        # レート制限エラーをシミュレーチE
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")
        mock_get.return_value = mock_response

        # フォールバックキャチE��ュチE�Eタを設宁E
        fallback_data = {
            'temperature': 20.0,
            'condition': 'clear',
            'source': 'fallback_cache'
        }

        with patch.object(weather_service, '_get_fallback_cache_data', return_value=fallback_data):
            result = weather_service.get_current_weather(35.6812, 139.7671)

            # フォールバックチE�Eタが返されることを確誁E
            assert result == fallback_data

    @patch('weather_service.requests.get')
    def test_get_current_weather_network_error(self, mock_get, weather_service):
        """ネットワークエラー時�EチE��チE""
        # ネットワークエラーをシミュレーチE
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # チE��ォルト天気情報が返されることを確誁E
        assert result['source'] == 'default'

    def test_format_weather_data_success(self, weather_service):
        """天気情報チE�Eタ整形成功チE��チE""
        api_data = {
            'current': {
                'dt': 1640995200,
                'temp': 25.5,
                'feels_like': 27.0,
                'humidity': 65,
                'pressure': 1013,
                'visibility': 10000,
                'uvi': 5.2,
                'wind_speed': 3.5,
                'wind_deg': 180,
                'clouds': 20,
                'sunrise': 1640995200,
                'sunset': 1641038400,
                'weather': [{
                    'main': 'Clear',
                    'description': '晴めE,
                    'icon': '01d'
                }]
            }
        }

        result = weather_service._format_weather_data(api_data)

        assert result['temperature'] == 25.5
        assert result['feels_like'] == 27.0
        assert result['condition'] == 'clear'
        assert result['description'] == '晴めE
        assert result['uv_index'] == 5.2
        assert result['humidity'] == 65
        assert result['pressure'] == 1013
        assert result['visibility'] == 10000
        assert result['wind_speed'] == 3.5
        assert result['wind_direction'] == 180
        assert result['clouds'] == 20
        assert result['icon'] == '01d'
        assert result['source'] == 'openweathermap'
        assert '06:00' in result['sunrise']  # 時刻フォーマット�E確誁E
        assert '15:00' in result['sunset']   # 時刻フォーマット�E確誁E

    def test_format_weather_data_missing_fields(self, weather_service):
        """天気情報チE�Eタ整形�E�フィールド不足�E�テスチE""
        api_data = {
            'current': {
                'dt': 1640995200,
                'temp': 25.5,
                'feels_like': 27.0,
                'weather': [{
                    'main': 'Clear',
                    'description': '晴めE,
                    'icon': '01d'
                }]
                # 他�Eフィールド�E不足
            }
        }

        result = weather_service._format_weather_data(api_data)

        assert result['temperature'] == 25.5
        assert result['condition'] == 'clear'
        assert result['uv_index'] == 0  # チE��ォルト値
        assert result['humidity'] == 0  # チE��ォルト値
        assert result['pressure'] == 1013  # チE��ォルト値

    def test_format_weather_data_invalid_structure(self, weather_service):
        """天気情報チE�Eタ整形�E�無効な構造�E�テスチE""
        api_data = {
            'invalid': 'structure'
        }

        with pytest.raises(KeyError):
            weather_service._format_weather_data(api_data)

    def test_get_weather_summary(self, weather_service, mock_cache_service):
        """天気要紁E��得テスチE""
        # キャチE��ュチE�Eタを設宁E
        cached_data = {
            'temperature': 25.0,
            'description': '晴めE,
            'uv_index': 5.0
        }
        mock_cache_service.get_cached_data.return_value = cached_data

        result = weather_service.get_weather_summary(35.6812, 139.7671)

        assert result == "晴めE25.0°C UV持E��5.0"

    def test_is_good_weather_for_walking_good(self, weather_service, mock_cache_service):
        """徒歩に適した天気判定（良好�E�テスチE""
        # 良好な天気データを設宁E
        good_weather = {
            'condition': 'clear',
            'temperature': 22.0,
            'wind_speed': 2.0
        }
        mock_cache_service.get_cached_data.return_value = good_weather

        result = weather_service.is_good_weather_for_walking(35.6812, 139.7671)

        assert result is True

    def test_is_good_weather_for_walking_rain(self, weather_service, mock_cache_service):
        """徒歩に適した天気判定（雨�E�テスチE""
        # 雨の天気データを設宁E
        rainy_weather = {
            'condition': 'rain',
            'temperature': 22.0,
            'wind_speed': 2.0
        }
        mock_cache_service.get_cached_data.return_value = rainy_weather

        result = weather_service.is_good_weather_for_walking(35.6812, 139.7671)

        assert result is False

    def test_is_good_weather_for_walking_extreme_temp(self, weather_service, mock_cache_service):
        """徒歩に適した天気判定（極端な気温�E�テスチE""
        # 極端に暑い天気データを設宁E
        hot_weather = {
            'condition': 'clear',
            'temperature': 40.0,
            'wind_speed': 2.0
        }
        mock_cache_service.get_cached_data.return_value = hot_weather

        result = weather_service.is_good_weather_for_walking(35.6812, 139.7671)

        assert result is False

        # 極端に寒い天気データを設宁E
        cold_weather = {
            'condition': 'clear',
            'temperature': -5.0,
            'wind_speed': 2.0
        }
        mock_cache_service.get_cached_data.return_value = cold_weather

        result = weather_service.is_good_weather_for_walking(35.6812, 139.7671)

        assert result is False

    def test_is_good_weather_for_walking_strong_wind(self, weather_service, mock_cache_service):
        """徒歩に適した天気判定（強風�E�テスチE""
        # 強風の天気データを設宁E
        windy_weather = {
            'condition': 'clear',
            'temperature': 22.0,
            'wind_speed': 15.0
        }
        mock_cache_service.get_cached_data.return_value = windy_weather

        result = weather_service.is_good_weather_for_walking(35.6812, 139.7671)

        assert result is False

    def test_get_weather_icon_url(self, weather_service):
        """天気アイコンURL取得テスチE""
        icon_code = '01d'
        result = weather_service.get_weather_icon_url(icon_code)

        expected_url = "https://openweathermap.org/img/wn/01d@2x.png"
        assert result == expected_url

    def test_is_default_weather(self, weather_service):
        """チE��ォルト天気判定テスチE""
        # チE��ォルト天氁E
        default_weather = {'source': 'default', 'temperature': 20.0}
        assert weather_service.is_default_weather(default_weather) is True

        # API取得天氁E
        api_weather = {'source': 'openweathermap', 'temperature': 25.0}
        assert weather_service.is_default_weather(api_weather) is False

    def test_validate_weather_data_valid(self, weather_service):
        """天気情報チE�Eタ妥当性検証�E�有効�E�テスチE""
        valid_data = {
            'temperature': 25.0,
            'condition': 'clear',
            'description': '晴めE,
            'uv_index': 5.0
        }

        assert weather_service.validate_weather_data(valid_data) is True

    def test_validate_weather_data_missing_fields(self, weather_service):
        """天気情報チE�Eタ妥当性検証�E�フィールド不足�E�テスチE""
        invalid_data = {
            'temperature': 25.0,
            'condition': 'clear'
            # description, uv_index が不足
        }

        assert weather_service.validate_weather_data(invalid_data) is False

    def test_validate_weather_data_invalid_temperature(self, weather_service):
        """天気情報チE�Eタ妥当性検証�E�無効な気温�E�テスチE""
        # 気温が篁E��夁E
        invalid_temp_data = {
            'temperature': -60.0,  # -50°C未満
            'condition': 'clear',
            'description': '晴めE,
            'uv_index': 5.0
        }
        assert weather_service.validate_weather_data(invalid_temp_data) is False

        # 気温が篁E��外（高温�E�E
        invalid_temp_data = {
            'temperature': 70.0,  # 60°C趁E��
            'condition': 'clear',
            'description': '晴めE,
            'uv_index': 5.0
        }
        assert weather_service.validate_weather_data(invalid_temp_data) is False

    def test_validate_weather_data_invalid_uv_index(self, weather_service):
        """天気情報チE�Eタ妥当性検証�E�無効なUV持E���E�テスチE""
        # UV持E��が篁E��夁E
        invalid_uv_data = {
            'temperature': 25.0,
            'condition': 'clear',
            'description': '晴めE,
            'uv_index': -1.0  # 0未満
        }
        assert weather_service.validate_weather_data(invalid_uv_data) is False

        # UV持E��が篁E��外（高値�E�E
        invalid_uv_data = {
            'temperature': 25.0,
            'condition': 'clear',
            'description': '晴めE,
            'uv_index': 20.0  # 15趁E��
        }
        assert weather_service.validate_weather_data(invalid_uv_data) is False

    def test_get_default_weather(self, weather_service):
        """チE��ォルト天気情報取得テスチE""
        result = weather_service._get_default_weather()

        assert result['source'] == 'default'
        assert result['temperature'] == 20.0
        assert result['condition'] == 'clear'
        assert result['description'] == '晴めE
        assert result['uv_index'] == 3.0
        assert 'feels_like' in result
        assert 'sunrise' in result
        assert 'sunset' in result
        assert 'timestamp' in result

    @patch('weather_service.get_db_connection')
    def test_get_fallback_cache_data_success(self, mock_get_db_connection, weather_service):
        """フォールバックキャチE��ュチE�Eタ取得�E功テスチE""
        # モチE��チE�Eタベ�Eス接続を設宁E
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # フォールバックチE�EタをモチE��
        fallback_data = {
            'temperature': 22.0,
            'condition': 'clear',
            'description': '晴めE
        }
        mock_cursor.fetchone.return_value = {
            'data': weather_service.cache_service.serialize_data(fallback_data)
        }

        with patch.object(weather_service.cache_service, 'deserialize_data', return_value=fallback_data):
            result = weather_service._get_fallback_cache_data('test_key')

            assert result is not None
            assert result['source'] == 'fallback_cache'

    @patch('weather_service.get_db_connection')
    def test_get_fallback_cache_data_not_found(self, mock_get_db_connection, weather_service):
        """フォールバックキャチE��ュチE�Eタ取得（データなし）テスチE""
        # モチE��チE�Eタベ�Eス接続を設宁E
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # チE�Eタが見つからなぁE��合をモチE��
        mock_cursor.fetchone.return_value = None

        result = weather_service._get_fallback_cache_data('test_key')

        assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
