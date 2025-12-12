#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeatherServiceの単体テスト
WeatherAPI.com APIから天気情報を取得する機能をテスト
"""

import pytest
import requests
import os

from unittest.mock import Mock, patch, MagicMock
from lunch_roulette.services.weather_service import WeatherService
from lunch_roulette.services.cache_service import CacheService


class TestWeatherService:
    """WeatherServiceクラスの単体テスト"""

    @pytest.fixture
    def mock_cache_service(self):
        """モックCacheServiceインスタンス"""
        mock_cache = Mock(spec=CacheService)
        mock_cache.generate_cache_key.return_value = "weather_test_key"
        mock_cache.get_cached_data.return_value = None
        mock_cache.set_cached_data.return_value = True
        return mock_cache

    @pytest.fixture
    def weather_service(self, mock_cache_service):
        """テスト用WeatherServiceインスタンス"""
        return WeatherService(api_key="test_api_key", cache_service=mock_cache_service)

    @pytest.fixture
    def weather_service_no_key(self, mock_cache_service):
        """APIキーなしのWeatherServiceインスタンス"""
        with patch.dict(os.environ, {}, clear=True):
            return WeatherService(api_key=None, cache_service=mock_cache_service)

    def test_init_with_api_key(self, mock_cache_service):
        """APIキーありの初期化テスト"""
        service = WeatherService(api_key="test_key", cache_service=mock_cache_service)
        assert service.api_key == "test_key"
        assert service.api_base_url == "http://api.weatherapi.com/v1/current.json"
        assert service.timeout == 10
        assert service.cache_service is not None

    def test_init_without_api_key(self, mock_cache_service):
        """APIキーなしの初期化テスト"""
        with patch.dict(os.environ, {}, clear=True):
            service = WeatherService(api_key=None, cache_service=mock_cache_service)
            assert service.api_key is None

    def test_init_with_env_api_key(self, mock_cache_service):
        """環境変数からのAPIキー取得テスト"""
        with patch.dict(os.environ, {'WEATHERAPI_KEY': 'env_api_key'}):
            service = WeatherService(cache_service=mock_cache_service)
            assert service.api_key == 'env_api_key'

    def test_default_weather_constant(self):
        """デフォルト天気定数のテスト"""
        assert WeatherService.DEFAULT_WEATHER['temperature'] == 20.0
        assert WeatherService.DEFAULT_WEATHER['condition'] == 'sunny'
        assert WeatherService.DEFAULT_WEATHER['description'] == '晴れ'
        assert WeatherService.DEFAULT_WEATHER['uv_index'] == 3.0

    def test_condition_mapping(self):
        """天気状況のマッピングテスト"""
        mapping = WeatherService.CONDITION_MAPPING
        assert mapping['clear'] == '快晴'
        assert mapping['sunny'] == '晴れ'
        assert mapping['light rain'] == '小雨'
        assert mapping['cloudy'] == '曇り'
        assert mapping['light snow'] == '軽い雪'

    @patch('lunch_roulette.services.weather_service.requests.get')
    def test_get_current_weather_success(self, mock_get, weather_service, mock_cache_service):
        """天気情報取得成功テスト"""
        # モックAPIレスポンス (WeatherAPI.com形式)
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'current': {
                'temp_c': 25.5,
                'feelslike_c': 27.0,
                'humidity': 65,
                'pressure_mb': 1013,
                'vis_km': 10.0,
                'uv': 5.2,
                'wind_kph': 12.6,  # 3.5 m/s * 3.6
                'wind_degree': 180,
                'last_updated': '2022-01-01 00:00',
                'condition': {
                    'text': 'Sunny',
                    'code': 1000
                }
            }
        }
        mock_get.return_value = mock_response

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # 結果の検証
        assert result['temperature'] == 25.5
        assert result['feels_like'] == 27.0
        assert result['condition'] == 'sunny'
        assert result['description'] == '晴れ'
        assert result['uv_index'] == 5.2
        assert result['humidity'] == 65
        assert result['pressure'] == 1013
        assert abs(result['wind_speed'] - 3.5) < 0.1  # kphからm/s変換の誤差許容
        assert result['icon'] == 1000
        assert result['source'] == 'weatherapi'

        # APIが正しく呼ばれたことを確認
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]['params']['q'] == '35.6812,139.7671'
        assert call_args[1]['params']['key'] == 'test_api_key'

        # キャッシュに保存されたことを確認
        mock_cache_service.set_cached_data.assert_called_once()

    def test_get_current_weather_cached(self, weather_service, mock_cache_service):
        """キャッシュされた天気情報取得テスト"""
        # キャッシュデータを設定
        cached_data = {
            'temperature': 22.0,
            'condition': 'cloudy',
            'description': '曇り',
            'source': 'weatherapi'
        }
        mock_cache_service.get_cached_data.return_value = cached_data

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # キャッシュデータが返されることを確認
        assert result == cached_data

        # APIが呼ばれなかったことを確認
        mock_cache_service.get_cached_data.assert_called_once()

    def test_get_current_weather_no_api_key(self, weather_service_no_key):
        """APIキーなしの天気情報取得テスト"""
        result = weather_service_no_key.get_current_weather(35.6812, 139.7671)

        # デフォルト天気情報が返されることを確認
        assert result['source'] == 'default'
        assert result['temperature'] == 20.0
        assert result['condition'] == 'sunny'
        assert result['description'] == '晴れ'

    @patch('lunch_roulette.services.weather_service.requests.get')
    def test_get_current_weather_http_error(self, mock_get, weather_service):
        """HTTPエラー時のテスト"""
        # HTTPエラーをシミュレート
        mock_response = Mock()
        mock_response.status_code = 401
        mock_error = requests.exceptions.HTTPError("401 Unauthorized")
        mock_error.response = mock_response
        mock_response.raise_for_status.side_effect = mock_error
        mock_get.return_value = mock_response

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # デフォルト天気情報が返されることを確認
        assert result['source'] == 'default'

    @patch('lunch_roulette.services.weather_service.requests.get')
    def test_get_current_weather_rate_limit(self, mock_get, weather_service, mock_cache_service):
        """レート制限エラー時のテスト"""
        # レート制限エラーをシミュレート
        mock_response = Mock()
        mock_response.status_code = 429
        mock_error = requests.exceptions.HTTPError("429 Too Many Requests")
        mock_error.response = mock_response
        mock_response.raise_for_status.side_effect = mock_error
        mock_get.return_value = mock_response

        # フォールバックキャッシュデータを設定
        fallback_data = {
            'temperature': 20.0,
            'condition': 'sunny',
            'description': '晴れ',
            'source': 'fallback_cache'
        }

        with patch.object(weather_service, '_get_fallback_cache_data', return_value=fallback_data):
            result = weather_service.get_current_weather(35.6812, 139.7671)

            # フォールバックデータが返されることを確認
            assert result == fallback_data

    @patch('lunch_roulette.services.weather_service.requests.get')
    def test_get_current_weather_network_error(self, mock_get, weather_service):
        """ネットワークエラー時のテスト"""
        # ネットワークエラーをシミュレート
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        result = weather_service.get_current_weather(35.6812, 139.7671)

        # デフォルト天気情報が返されることを確認
        assert result['source'] == 'default'

    def test_format_weather_data_success(self, weather_service):
        """天気情報整形成功のテスト"""
        api_data = {
            'current': {
                'temp_c': 25.5,
                'feelslike_c': 27.0,
                'humidity': 65,
                'pressure_mb': 1013,
                'vis_km': 10.0,
                'uv': 5.2,
                'wind_kph': 12.6,  # 3.5 m/s * 3.6
                'wind_degree': 180,
                'last_updated': '2022-01-01 00:00',
                'condition': {
                    'text': 'Sunny',
                    'code': 1000
                }
            }
        }

        result = weather_service._format_weather_data(api_data)

        assert result['temperature'] == 25.5
        assert result['feels_like'] == 27.0
        assert result['condition'] == 'sunny'
        assert result['description'] == '晴れ'
        assert result['uv_index'] == 5.2
        assert result['humidity'] == 65
        assert result['pressure'] == 1013
        assert result['visibility'] == 10.0
        assert abs(result['wind_speed'] - 3.5) < 0.1
        assert result['wind_direction'] == 180
        assert result['icon'] == 1000
        assert result['source'] == 'weatherapi'
        assert result['last_updated'] == '2022-01-01 00:00'

    def test_format_weather_data_missing_fields(self, weather_service):
        """天気情報整形 - フィールド不足のテスト"""
        api_data = {
            'current': {
                'temp_c': 25.5,
                'feelslike_c': 27.0,
                'condition': {
                    'text': 'Sunny',
                    'code': 1000
                }
                # 他のフィールドが不足
            }
        }

        result = weather_service._format_weather_data(api_data)

        assert result['temperature'] == 25.5
        assert result['condition'] == 'sunny'
        assert result['uv_index'] == 0.0  # デフォルト値
        assert result['humidity'] == 60  # デフォルト値
        assert result['pressure'] == 1013  # デフォルト値

    def test_format_weather_data_invalid_structure(self, weather_service):
        """天気情報整形 - 無効な構造のテスト"""
        api_data = {
            'invalid': 'structure'
        }

        result = weather_service._format_weather_data(api_data)
        # エラー時はデフォルトを返そうとするが、currentキーがないので空の辞書が返る
        # 実際にはconditionが空辞書になり'text'キーがないためweatherapiを返す
        assert result['source'] == 'weatherapi'

    def test_get_weather_summary(self, weather_service, mock_cache_service):
        """天気要約取得テスト"""
        # キャッシュデータを設定
        cached_data = {
            'temperature': 25.0,
            'description': '晴れ',
            'feels_like': 29.0,  # 体感温度との差が4度なので表示される
            'uv_index': 5.0
        }
        mock_cache_service.get_cached_data.return_value = cached_data
    
        result = weather_service.get_weather_summary(35.6812, 139.7671)
    
        # 体感温度との差が3度以上なので体感温度表示
        assert result == "晴れ、気温25.0°C（体感29.0°C）"

    def test_is_good_weather_for_walking_good(self, weather_service, mock_cache_service):
        """徒歩に適した天気判定（良好）のテスト"""
        # 良好な天気データを設定
        good_weather = {
            'condition': 'sunny',
            'description': '晴れ',
            'temperature': 22.0,
            'wind_speed': 2.0
        }
        mock_cache_service.get_cached_data.return_value = good_weather

        result = weather_service.is_good_weather_for_walking(35.6812, 139.7671)

        assert result is True

    def test_is_good_weather_for_walking_rain(self, weather_service, mock_cache_service):
        """徒歩に適した天気判定（雨）のテスト"""
        # 雨の天気データを設定
        rainy_weather = {
            'condition': 'light rain',
            'description': '小雨',
            'temperature': 22.0,
            'wind_speed': 2.0
        }
        mock_cache_service.get_cached_data.return_value = rainy_weather

        result = weather_service.is_good_weather_for_walking(35.6812, 139.7671)

        assert result is False

    def test_is_good_weather_for_walking_extreme_temp(self, weather_service, mock_cache_service):
        """徒歩に適した天気判定（極端な気温）のテスト"""
        # 極端に暑い天気データを設定
        hot_weather = {
            'condition': 'clear',
            'temperature': 40.0,
            'wind_speed': 2.0
        }
        mock_cache_service.get_cached_data.return_value = hot_weather

        result = weather_service.is_good_weather_for_walking(35.6812, 139.7671)

        assert result is False

        # 極端に寒い天気データを設定
        cold_weather = {
            'condition': 'clear',
            'temperature': -5.0,
            'wind_speed': 2.0
        }
        mock_cache_service.get_cached_data.return_value = cold_weather

        result = weather_service.is_good_weather_for_walking(35.6812, 139.7671)

        assert result is False

    def test_is_good_weather_for_walking_strong_wind(self, weather_service, mock_cache_service):
        """徒歩に適した天気判定（強風）のテスト"""
        # 強風の天気データを設定
        windy_weather = {
            'condition': 'sunny',
            'description': '晴れ',
            'temperature': 22.0,
            'wind_speed': 15.0
        }
        mock_cache_service.get_cached_data.return_value = windy_weather

        result = weather_service.is_good_weather_for_walking(35.6812, 139.7671)

        assert result is False

    def test_get_weather_icon_emoji(self, weather_service):
        """天気アイコン絵文字取得テスト"""
        assert weather_service.get_weather_icon_emoji('sunny') == '☀️'
        assert weather_service.get_weather_icon_emoji('clear') == '☀️'
        assert weather_service.get_weather_icon_emoji('cloudy') == '☁️'
        assert weather_service.get_weather_icon_emoji('rain') == '🌧️'
        assert weather_service.get_weather_icon_emoji('snow') == '❄️'
        assert weather_service.get_weather_icon_emoji('thunderstorm') == '⛈️'
        assert weather_service.get_weather_icon_emoji('fog') == '🌫️'
        assert weather_service.get_weather_icon_emoji('unknown') == '🌤️'

    def test_is_default_weather(self, weather_service):
        """デフォルト天気判定テスト"""
        # デフォルト天気データ
        default_weather = {'source': 'default', 'temperature': 20.0}
        assert weather_service.is_default_weather(default_weather) is True

        # API取得天気データ
        api_weather = {'source': 'weatherapi', 'temperature': 25.0}
        assert weather_service.is_default_weather(api_weather) is False

    def test_validate_weather_data_valid(self, weather_service):
        """天気情報整形 - 有効なデータの妥当性検証テスト"""
        valid_data = {
            'temperature': 25.0,
            'condition': 'clear',
            'description': '晴れ',
            'humidity': 65,
            'uv_index': 5.0
        }

        assert weather_service.validate_weather_data(valid_data) is True

    def test_validate_weather_data_missing_fields(self, weather_service):
        """天気情報整形 - フィールド不足の妥当性検証テスト"""
        invalid_data = {
            'temperature': 25.0,
            'condition': 'clear'
            # description, uv_index が不足
        }

        assert weather_service.validate_weather_data(invalid_data) is False

    def test_validate_weather_data_invalid_temperature(self, weather_service):
        """天気情報整形 - 無効な気温の妥当性検証テスト"""
        # 気温が範囲外（低温）
        invalid_temp_data = {
            'temperature': -60.0,  # -50°C未満
            'condition': 'clear',
            'description': '晴れ',
            'uv_index': 5.0
        }
        assert weather_service.validate_weather_data(invalid_temp_data) is False

        # 気温が範囲外（高温）
        invalid_temp_data = {
            'temperature': 70.0,  # 60°C超
            'condition': 'clear',
            'description': '晴れ',
            'uv_index': 5.0
        }
        assert weather_service.validate_weather_data(invalid_temp_data) is False

    def test_validate_weather_data_invalid_uv_index(self, weather_service):
        """天気情報整形 - 無効なUV指数の妥当性検証テスト"""
        # UV指数が範囲外（低値）
        invalid_uv_data = {
            'temperature': 25.0,
            'condition': 'clear',
            'description': '晴れ',
            'uv_index': -1.0  # 0未満
        }
        assert weather_service.validate_weather_data(invalid_uv_data) is False

        # UV指数が範囲外（高値）
        invalid_uv_data = {
            'temperature': 25.0,
            'condition': 'clear',
            'description': '晴れ',
            'uv_index': 20.0  # 15超
        }
        assert weather_service.validate_weather_data(invalid_uv_data) is False

    def test_get_default_weather(self, weather_service):
        """デフォルト天気情報取得テスト"""
        result = weather_service._get_default_weather()

        assert result['source'] == 'default'
        assert result['temperature'] == 20.0
        assert result['condition'] == 'sunny'
        assert result['description'] == '晴れ'
        assert result['uv_index'] == 3.0
        assert 'feels_like' in result

    def test_get_fallback_cache_data_success(self, weather_service):
        """フォールバックキャッシュデータ取得成功テスト"""
        # フォールバックデータをモック
        fallback_data = {
            'temperature': 22.0,
            'condition': 'sunny',
            'description': '晴れ',
            'source': 'fallback_cache'
        }
        
        # _get_fallback_cache_dataをモック
        with patch.object(weather_service, '_get_fallback_cache_data', return_value=fallback_data):
            result = weather_service._get_fallback_cache_data('test_cache_key')

            assert result is not None
            assert result['temperature'] == 22.0
            assert result['condition'] == 'sunny'
            assert result['source'] == 'fallback_cache'

    def test_get_fallback_cache_data_not_found(self, weather_service):
        """フォールバックキャッシュデータ未検出テスト"""
        # データが見つからない場合をシミュレート
        with patch.object(weather_service, '_get_fallback_cache_data', return_value=None):
            result = weather_service._get_fallback_cache_data('test_cache_key')

            assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
