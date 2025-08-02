#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LocationService - 位置情報サービスクラス
IPアドレスから位置情報を取得する機能を提供

このクラスは以下の機能を提供します:
- IPアドレスから位置情報の取得
- エラーハンドリングとデフォルト位置（東京駅）設定
- キャッシュ機能との統合
"""

import requests
from typing import Dict, Optional, Tuple
from cache_service import CacheService


class LocationService:
    """
    IPアドレスから位置情報を取得するサービス
    
    ipapi.co APIを使用してIPアドレスから位置情報を取得し、
    エラー時には東京駅をデフォルト位置として使用する。
    """
    
    # デフォルト位置（東京駅）
    DEFAULT_LOCATION = {
        'latitude': 35.6812,
        'longitude': 139.7671,
        'city': '東京',
        'region': '東京都',
        'country': '日本',
        'country_code': 'JP'
    }
    
    def __init__(self, cache_service: Optional[CacheService] = None):
        """
        LocationServiceを初期化
        
        Args:
            cache_service (CacheService, optional): キャッシュサービス
        """
        self.cache_service = cache_service or CacheService()
        self.api_base_url = "https://ipapi.co"
        self.timeout = 10  # APIリクエストのタイムアウト（秒）
    
    def get_location_from_ip(self, ip_address: Optional[str] = None) -> Dict[str, any]:
        """
        IPアドレスから位置情報を取得
        
        Args:
            ip_address (str, optional): IPアドレス。Noneの場合は自動検出
            
        Returns:
            dict: 位置情報（緯度、経度、都市名など）
            
        Example:
            >>> location_service = LocationService()
            >>> location = location_service.get_location_from_ip()
            >>> print(f"Location: {location['city']}, {location['region']}")
        """
        # キャッシュキーを生成
        cache_key = self.cache_service.generate_cache_key(
            'location', 
            ip=ip_address or 'auto'
        )
        
        # キャッシュから取得を試行
        cached_data = self.cache_service.get_cached_data(cache_key)
        if cached_data:
            print(f"位置情報をキャッシュから取得: {cached_data['city']}")
            return cached_data
        
        try:
            # API URLを構築
            if ip_address:
                url = f"{self.api_base_url}/{ip_address}/json/"
            else:
                url = f"{self.api_base_url}/json/"
            
            print(f"位置情報API呼び出し: {url}")
            
            # APIリクエストを実行
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # レスポンスを解析
            data = response.json()
            
            # エラーレスポンスをチェック
            if 'error' in data and data['error']:
                raise ValueError(f"API エラー: {data.get('reason', 'Unknown error')}")
            
            # 位置情報を整形
            location_data = self._format_location_data(data)
            
            # キャッシュに保存（10分間）
            self.cache_service.set_cached_data(cache_key, location_data, ttl=600)
            
            print(f"位置情報取得成功: {location_data['city']}, {location_data['region']}")
            return location_data
            
        except requests.exceptions.RequestException as e:
            print(f"位置情報API リクエストエラー: {e}")
            return self._get_default_location()
            
        except (ValueError, KeyError) as e:
            print(f"位置情報データ解析エラー: {e}")
            return self._get_default_location()
            
        except Exception as e:
            print(f"位置情報取得で予期しないエラー: {e}")
            return self._get_default_location()
    
    def _format_location_data(self, api_data: Dict) -> Dict[str, any]:
        """
        APIレスポンスを標準形式に整形
        
        Args:
            api_data (dict): ipapi.co APIからのレスポンス
            
        Returns:
            dict: 整形された位置情報
            
        Raises:
            KeyError: 必要なフィールドが不足している場合
        """
        try:
            return {
                'latitude': float(api_data['latitude']),
                'longitude': float(api_data['longitude']),
                'city': api_data.get('city', '不明'),
                'region': api_data.get('region', '不明'),
                'country': api_data.get('country_name', '不明'),
                'country_code': api_data.get('country_code', 'XX'),
                'postal': api_data.get('postal', ''),
                'timezone': api_data.get('timezone', 'Asia/Tokyo'),
                'source': 'ipapi.co'
            }
        except (KeyError, ValueError, TypeError) as e:
            raise KeyError(f"位置情報データの必須フィールドが不足: {e}")
    
    def _get_default_location(self) -> Dict[str, any]:
        """
        デフォルト位置（東京駅）を返す
        
        Returns:
            dict: デフォルト位置情報
        """
        default_location = self.DEFAULT_LOCATION.copy()
        default_location['source'] = 'default'
        
        print("デフォルト位置（東京駅）を使用")
        return default_location
    
    def get_coordinates(self, ip_address: Optional[str] = None) -> Tuple[float, float]:
        """
        IPアドレスから緯度・経度のタプルを取得
        
        Args:
            ip_address (str, optional): IPアドレス
            
        Returns:
            tuple: (緯度, 経度)
            
        Example:
            >>> location_service = LocationService()
            >>> lat, lon = location_service.get_coordinates()
            >>> print(f"Coordinates: {lat}, {lon}")
        """
        location = self.get_location_from_ip(ip_address)
        return location['latitude'], location['longitude']
    
    def is_default_location(self, location_data: Dict) -> bool:
        """
        位置情報がデフォルト位置かどうかを判定
        
        Args:
            location_data (dict): 位置情報
            
        Returns:
            bool: デフォルト位置の場合True
        """
        return location_data.get('source') == 'default'
    
    def validate_location_data(self, location_data: Dict) -> bool:
        """
        位置情報データの妥当性を検証
        
        Args:
            location_data (dict): 位置情報
            
        Returns:
            bool: 妥当な場合True
        """
        try:
            # 必須フィールドの存在確認
            required_fields = ['latitude', 'longitude', 'city', 'region', 'country']
            for field in required_fields:
                if field not in location_data:
                    return False
            
            # 緯度・経度の範囲確認
            lat = float(location_data['latitude'])
            lon = float(location_data['longitude'])
            
            if not (-90 <= lat <= 90):
                return False
            if not (-180 <= lon <= 180):
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False


# 使用例とテスト用コード
if __name__ == '__main__':
    """
    LocationServiceのテスト実行
    """
    print("LocationService テスト実行")
    print("=" * 40)
    
    # LocationServiceインスタンス作成
    location_service = LocationService()
    
    # 位置情報取得テスト
    print("1. 自動IP検出による位置情報取得:")
    location = location_service.get_location_from_ip()
    print(f"   位置: {location['city']}, {location['region']}")
    print(f"   座標: {location['latitude']}, {location['longitude']}")
    print(f"   ソース: {location['source']}")
    
    # 座標取得テスト
    print("\n2. 座標のみ取得:")
    lat, lon = location_service.get_coordinates()
    print(f"   緯度: {lat}, 経度: {lon}")
    
    # デフォルト位置判定テスト
    print(f"\n3. デフォルト位置判定: {location_service.is_default_location(location)}")
    
    # データ妥当性検証テスト
    print(f"4. データ妥当性検証: {location_service.validate_location_data(location)}")
    
    # 無効なIPアドレステスト
    print("\n5. 無効なIPアドレステスト:")
    invalid_location = location_service.get_location_from_ip("invalid.ip")
    print(f"   位置: {invalid_location['city']}, {invalid_location['region']}")
    print(f"   デフォルト位置: {location_service.is_default_location(invalid_location)}")
    
    print("\nテスト完了")