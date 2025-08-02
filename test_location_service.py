#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LocationServiceの単体テスト
IPアドレスから位置情報を取得する機能をテスト
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from location_service import LocationService
from cache_service import CacheService


class TestLocationService:
    """LocationServiceクラスの単体テスト"""
    
    @pytest.fixture
    def mock_cache_service(self):
        """モックCacheServiceインスタンス"""
        mock_cache = Mock(spec=CacheService)
        mock_cache.generate_cache_key.return_value = "location_test_key"
        mock_cache.get_cached_data.return_value = None
        mock_cache.set_cached_data.return_value = True
        return mock_cache
    
    @pytest.fixture
    def location_service(self, mock_cache_service):
        """テスト用LocationServiceインスタンス"""
        return LocationService(cache_service=mock_cache_service)
    
    def test_init(self):
        """初期化テスト"""
        service = LocationService()
        assert service.api_base_url == "https://ipapi.co"
        assert service.timeout == 10
        assert service.cache_service is not None
    
    def test_default_location_constant(self):
        """デフォルト位置定数テスト"""
        assert LocationService.DEFAULT_LOCATION['latitude'] == 35.6812
        assert LocationService.DEFAULT_LOCATION['longitude'] == 139.7671
        assert LocationService.DEFAULT_LOCATION['city'] == '東京'
        assert LocationService.DEFAULT_LOCATION['country'] == '日本'
    
    @patch('location_service.requests.get')
    def test_get_location_from_ip_success(self, mock_get, location_service, mock_cache_service):
        """位置情報取得成功テスト"""
        # モックAPIレスポンス
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '千代田区',
            'region': '東京都',
            'country_name': '日本',
            'country_code': 'JP',
            'postal': '100-0001',
            'timezone': 'Asia/Tokyo'
        }
        mock_get.return_value = mock_response
        
        result = location_service.get_location_from_ip('192.168.1.1')
        
        # 結果の検証
        assert result['latitude'] == 35.6762
        assert result['longitude'] == 139.6503
        assert result['city'] == '千代田区'
        assert result['region'] == '東京都'
        assert result['country'] == '日本'
        assert result['country_code'] == 'JP'
        assert result['source'] == 'ipapi.co'
        
        # APIが正しく呼ばれたことを確認
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'https://ipapi.co/192.168.1.1/json/' in call_args[0][0]
        
        # キャッシュに保存されたことを確認
        mock_cache_service.set_cached_data.assert_called_once()
    
    @patch('location_service.requests.get')
    def test_get_location_from_ip_auto_detect(self, mock_get, location_service):
        """自動IP検出テスト"""
        # モックAPIレスポンス
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '東京',
            'region': '東京都',
            'country_name': '日本',
            'country_code': 'JP'
        }
        mock_get.return_value = mock_response
        
        result = location_service.get_location_from_ip()
        
        # 自動検出用URLが呼ばれたことを確認
        call_args = mock_get.call_args
        assert call_args[0][0] == 'https://ipapi.co/json/'
    
    def test_get_location_from_ip_cached(self, location_service, mock_cache_service):
        """キャッシュされた位置情報取得テスト"""
        # キャッシュデータを設定
        cached_data = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '東京',
            'source': 'ipapi.co'
        }
        mock_cache_service.get_cached_data.return_value = cached_data
        
        result = location_service.get_location_from_ip('192.168.1.1')
        
        # キャッシュデータが返されることを確認
        assert result == cached_data
        
        # APIが呼ばれないことを確認
        mock_cache_service.get_cached_data.assert_called_once()
    
    @patch('location_service.requests.get')
    def test_get_location_from_ip_http_error(self, mock_get, location_service):
        """HTTP エラー時のテスト"""
        # HTTPエラーをシミュレート
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        result = location_service.get_location_from_ip('invalid.ip')
        
        # デフォルト位置が返されることを確認
        assert result['source'] == 'default'
        assert result['city'] == '東京'
        assert result['latitude'] == 35.6812
        assert result['longitude'] == 139.7671
    
    @patch('location_service.requests.get')
    def test_get_location_from_ip_rate_limit(self, mock_get, location_service, mock_cache_service):
        """レート制限エラー時のテスト"""
        # レート制限エラーをシミュレート
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")
        mock_get.return_value = mock_response
        
        # フォールバックキャッシュデータを設定
        fallback_data = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '東京',
            'source': 'fallback_cache'
        }
        
        with patch.object(location_service, '_get_fallback_cache_data', return_value=fallback_data):
            result = location_service.get_location_from_ip('192.168.1.1')
            
            # フォールバックデータが返されることを確認
            assert result == fallback_data
    
    @patch('location_service.requests.get')
    def test_get_location_from_ip_network_error(self, mock_get, location_service):
        """ネットワークエラー時のテスト"""
        # ネットワークエラーをシミュレート
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        result = location_service.get_location_from_ip('192.168.1.1')
        
        # デフォルト位置が返されることを確認
        assert result['source'] == 'default'
        assert result['city'] == '東京'
    
    @patch('location_service.requests.get')
    def test_get_location_from_ip_api_error_response(self, mock_get, location_service):
        """API エラーレスポンス時のテスト"""
        # APIエラーレスポンスをシミュレート
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'error': True,
            'reason': 'Invalid IP address'
        }
        mock_get.return_value = mock_response
        
        result = location_service.get_location_from_ip('invalid.ip')
        
        # デフォルト位置が返されることを確認
        assert result['source'] == 'default'
    
    def test_format_location_data_success(self, location_service):
        """位置情報データ整形成功テスト"""
        api_data = {
            'latitude': '35.6762',
            'longitude': '139.6503',
            'city': '千代田区',
            'region': '東京都',
            'country_name': '日本',
            'country_code': 'JP',
            'postal': '100-0001',
            'timezone': 'Asia/Tokyo'
        }
        
        result = location_service._format_location_data(api_data)
        
        assert result['latitude'] == 35.6762
        assert result['longitude'] == 139.6503
        assert result['city'] == '千代田区'
        assert result['region'] == '東京都'
        assert result['country'] == '日本'
        assert result['country_code'] == 'JP'
        assert result['postal'] == '100-0001'
        assert result['timezone'] == 'Asia/Tokyo'
        assert result['source'] == 'ipapi.co'
    
    def test_format_location_data_missing_fields(self, location_service):
        """位置情報データ整形（フィールド不足）テスト"""
        api_data = {
            'latitude': '35.6762',
            'longitude': '139.6503'
            # 他のフィールドは不足
        }
        
        result = location_service._format_location_data(api_data)
        
        assert result['latitude'] == 35.6762
        assert result['longitude'] == 139.6503
        assert result['city'] == '不明'
        assert result['region'] == '不明'
        assert result['country'] == '不明'
        assert result['country_code'] == 'XX'
    
    def test_format_location_data_invalid_coordinates(self, location_service):
        """位置情報データ整形（無効な座標）テスト"""
        api_data = {
            'latitude': 'invalid',
            'longitude': 'invalid',
            'city': '東京'
        }
        
        with pytest.raises(KeyError):
            location_service._format_location_data(api_data)
    
    def test_get_coordinates(self, location_service, mock_cache_service):
        """座標取得テスト"""
        # キャッシュデータを設定
        cached_data = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '東京'
        }
        mock_cache_service.get_cached_data.return_value = cached_data
        
        lat, lon = location_service.get_coordinates('192.168.1.1')
        
        assert lat == 35.6762
        assert lon == 139.6503
    
    def test_is_default_location(self, location_service):
        """デフォルト位置判定テスト"""
        # デフォルト位置
        default_location = {'source': 'default', 'city': '東京'}
        assert location_service.is_default_location(default_location) is True
        
        # API取得位置
        api_location = {'source': 'ipapi.co', 'city': '大阪'}
        assert location_service.is_default_location(api_location) is False
    
    def test_validate_location_data_valid(self, location_service):
        """位置情報データ妥当性検証（有効）テスト"""
        valid_data = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '東京',
            'region': '東京都',
            'country': '日本'
        }
        
        assert location_service.validate_location_data(valid_data) is True
    
    def test_validate_location_data_missing_fields(self, location_service):
        """位置情報データ妥当性検証（フィールド不足）テスト"""
        invalid_data = {
            'latitude': 35.6762,
            'longitude': 139.6503
            # city, region, country が不足
        }
        
        assert location_service.validate_location_data(invalid_data) is False
    
    def test_validate_location_data_invalid_coordinates(self, location_service):
        """位置情報データ妥当性検証（無効な座標）テスト"""
        # 緯度が範囲外
        invalid_lat_data = {
            'latitude': 95.0,  # 90度を超える
            'longitude': 139.6503,
            'city': '東京',
            'region': '東京都',
            'country': '日本'
        }
        assert location_service.validate_location_data(invalid_lat_data) is False
        
        # 経度が範囲外
        invalid_lon_data = {
            'latitude': 35.6762,
            'longitude': 185.0,  # 180度を超える
            'city': '東京',
            'region': '東京都',
            'country': '日本'
        }
        assert location_service.validate_location_data(invalid_lon_data) is False
    
    def test_validate_location_data_invalid_types(self, location_service):
        """位置情報データ妥当性検証（無効な型）テスト"""
        invalid_type_data = {
            'latitude': 'invalid',  # 文字列
            'longitude': 139.6503,
            'city': '東京',
            'region': '東京都',
            'country': '日本'
        }
        
        assert location_service.validate_location_data(invalid_type_data) is False
    
    @patch('location_service.get_db_connection')
    def test_get_fallback_cache_data_success(self, mock_get_db_connection, location_service):
        """フォールバックキャッシュデータ取得成功テスト"""
        # モックデータベース接続を設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        
        # フォールバックデータをモック
        fallback_data = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'city': '東京'
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
        """フォールバックキャッシュデータ取得（データなし）テスト"""
        # モックデータベース接続を設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        
        # データが見つからない場合をモック
        mock_cursor.fetchone.return_value = None
        
        result = location_service._get_fallback_cache_data('test_key')
        
        assert result is None
    
    def test_get_default_location(self, location_service):
        """デフォルト位置取得テスト"""
        result = location_service._get_default_location()
        
        assert result['source'] == 'default'
        assert result['city'] == '東京'
        assert result['latitude'] == 35.6812
        assert result['longitude'] == 139.7671
        assert result['country'] == '日本'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])