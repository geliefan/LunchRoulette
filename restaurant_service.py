#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RestaurantService - レストラン情報サービスクラス
Hot Pepper Gourmet APIからレストラン情報を取得する機能を提供

このクラスは以下の機能を提供します:
- Hot Pepper Gourmet Web API統合
- 半径1km以内のレストラン検索機能
- ランチ予算≤¥1,200のフィルタリング機能
- キャッシュ機能との統合
"""

import requests
import os
from typing import Dict, List, Optional
from cache_service import CacheService


class RestaurantService:
    """
    Hot Pepper Gourmet APIからレストラン情報を取得するサービス
    
    指定された座標周辺のレストランを検索し、予算でフィルタリングして
    ランチに適したレストランを提供する。
    """
    
    # 予算コードマッピング（Hot Pepper API仕様）
    BUDGET_CODES = {
        'B009': 500,    # ～500円
        'B010': 1000,   # 501～1000円
        'B011': 1500,   # 1001～1500円
        'B001': 2000,   # 1501～2000円
        'B002': 3000,   # 2001～3000円
        'B003': 4000,   # 3001～4000円
        'B008': 5000,   # 4001～5000円
        'B004': 7000,   # 5001～7000円
        'B005': 10000,  # 7001～10000円
        'B006': 15000,  # 10001～15000円
        'B012': 20000,  # 15001～20000円
        'B013': 30000,  # 20001～30000円
        'B014': 30001   # 30001円～
    }
    
    # ランチ予算制限（円）
    LUNCH_BUDGET_LIMIT = 1200
    
    def __init__(self, api_key: Optional[str] = None, cache_service: Optional[CacheService] = None):
        """
        RestaurantServiceを初期化
        
        Args:
            api_key (str, optional): Hot Pepper Gourmet APIキー
            cache_service (CacheService, optional): キャッシュサービス
        """
        self.api_key = api_key or os.getenv('HOTPEPPER_API_KEY')
        self.cache_service = cache_service or CacheService()
        self.api_base_url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
        self.timeout = 10  # APIリクエストのタイムアウト（秒）
        
        if not self.api_key:
            print("警告: Hot Pepper Gourmet APIキーが設定されていません。")
    
    def search_restaurants(self, lat: float, lon: float, radius: int = 1) -> List[Dict]:
        """
        指定された座標周辺のレストランを検索
        
        Args:
            lat (float): 緯度
            lon (float): 経度
            radius (int): 検索半径（km）、デフォルトは1km
            
        Returns:
            list: レストラン情報のリスト
            
        Example:
            >>> restaurant_service = RestaurantService()
            >>> restaurants = restaurant_service.search_restaurants(35.6812, 139.7671)
            >>> print(f"Found {len(restaurants)} restaurants")
        """
        # キャッシュキーを生成
        cache_key = self.cache_service.generate_cache_key(
            'restaurants',
            lat=round(lat, 4),
            lon=round(lon, 4),
            radius=radius
        )
        
        # キャッシュから取得を試行
        cached_data = self.cache_service.get_cached_data(cache_key)
        if cached_data:
            print(f"レストラン情報をキャッシュから取得: {len(cached_data)}件")
            return cached_data
        
        # APIキーが設定されていない場合は空のリストを返す
        if not self.api_key:
            print("APIキーが設定されていないため、レストラン検索をスキップ")
            return []
        
        try:
            # APIパラメータを構築
            params = {
                'key': self.api_key,
                'lat': lat,
                'lng': lon,
                'range': self._convert_radius_to_range_code(radius),
                'count': 100,  # 最大取得件数
                'format': 'json'
            }
            
            print(f"レストラン検索API呼び出し: lat={lat}, lon={lon}, radius={radius}km")
            
            # APIリクエストを実行
            response = requests.get(self.api_base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # レスポンスを解析
            data = response.json()
            
            # エラーレスポンスをチェック
            if 'results' not in data:
                raise ValueError("APIレスポンスに結果が含まれていません")
            
            # レストラン情報を整形
            restaurants = self._format_restaurant_data(data['results'].get('shop', []))
            
            # キャッシュに保存（10分間）
            self.cache_service.set_cached_data(cache_key, restaurants, ttl=600)
            
            print(f"レストラン検索成功: {len(restaurants)}件取得")
            return restaurants
            
        except requests.exceptions.HTTPError as e:
            # HTTPエラー（レート制限、認証エラーなど）
            if e.response.status_code == 429:
                print(f"レストラン検索API レート制限エラー: {e}")
                # レート制限時は古いキャッシュデータを使用を試行
                fallback_data = self._get_fallback_cache_data(cache_key)
                if fallback_data:
                    return fallback_data
            elif e.response.status_code == 401:
                print(f"レストラン検索API 認証エラー: {e}")
            else:
                print(f"レストラン検索API HTTPエラー: {e}")
            return []
            
        except requests.exceptions.RequestException as e:
            print(f"レストラン検索API リクエストエラー: {e}")
            # ネットワークエラー時は古いキャッシュデータを使用を試行
            fallback_data = self._get_fallback_cache_data(cache_key)
            if fallback_data:
                return fallback_data
            return []
            
        except (ValueError, KeyError) as e:
            print(f"レストラン検索データ解析エラー: {e}")
            return []
            
        except Exception as e:
            print(f"レストラン検索で予期しないエラー: {e}")
            return []
    
    def filter_by_budget(self, restaurants: List[Dict], max_budget: int = None) -> List[Dict]:
        """
        予算でレストランをフィルタリング
        
        Args:
            restaurants (list): レストラン情報のリスト
            max_budget (int, optional): 最大予算（円）、デフォルトはLUNCH_BUDGET_LIMIT
            
        Returns:
            list: フィルタリングされたレストラン情報のリスト
        """
        if max_budget is None:
            max_budget = self.LUNCH_BUDGET_LIMIT
        
        filtered_restaurants = []
        
        for restaurant in restaurants:
            # 予算情報が存在しない場合はスキップ
            if 'budget_average' not in restaurant:
                continue
            
            # 予算が制限以下の場合のみ追加
            if restaurant['budget_average'] <= max_budget:
                filtered_restaurants.append(restaurant)
        
        print(f"予算フィルタリング: {len(restaurants)}件 → {len(filtered_restaurants)}件 (≤¥{max_budget})")
        return filtered_restaurants
    
    def search_lunch_restaurants(self, lat: float, lon: float, radius: int = 1) -> List[Dict]:
        """
        ランチに適したレストランを検索（予算フィルタリング込み）
        
        Args:
            lat (float): 緯度
            lon (float): 経度
            radius (int): 検索半径（km）
            
        Returns:
            list: ランチに適したレストラン情報のリスト
        """
        # 全レストランを検索
        all_restaurants = self.search_restaurants(lat, lon, radius)
        
        # 予算でフィルタリング
        lunch_restaurants = self.filter_by_budget(all_restaurants, self.LUNCH_BUDGET_LIMIT)
        
        return lunch_restaurants
    
    def _convert_radius_to_range_code(self, radius_km: int) -> int:
        """
        半径（km）をHot Pepper APIの範囲コードに変換
        
        Args:
            radius_km (int): 半径（km）
            
        Returns:
            int: Hot Pepper APIの範囲コード
        """
        # Hot Pepper APIの範囲コード
        # 1: 300m, 2: 500m, 3: 1000m, 4: 2000m, 5: 3000m
        if radius_km <= 0.3:
            return 1
        elif radius_km <= 0.5:
            return 2
        elif radius_km <= 1:
            return 3
        elif radius_km <= 2:
            return 4
        else:
            return 5
    
    def _format_restaurant_data(self, api_restaurants: List[Dict]) -> List[Dict]:
        """
        APIレスポンスを標準形式に整形
        
        Args:
            api_restaurants (list): Hot Pepper APIからのレストランデータ
            
        Returns:
            list: 整形されたレストラン情報のリスト
        """
        formatted_restaurants = []
        
        for restaurant in api_restaurants:
            try:
                # 予算情報を解析
                budget_average = self._parse_budget_info(restaurant.get('budget', {}))
                
                formatted_restaurant = {
                    'id': restaurant.get('id', ''),
                    'name': restaurant.get('name', '不明なレストラン'),
                    'name_kana': restaurant.get('name_kana', ''),
                    'address': restaurant.get('address', ''),
                    'lat': float(restaurant.get('lat', 0)),
                    'lng': float(restaurant.get('lng', 0)),
                    'genre': restaurant.get('genre', {}).get('name', ''),
                    'budget_average': budget_average,
                    'budget_name': restaurant.get('budget', {}).get('name', ''),
                    'catch': restaurant.get('catch', ''),
                    'capacity': restaurant.get('capacity', 0),
                    'access': restaurant.get('access', ''),
                    'mobile_access': restaurant.get('mobile_access', ''),
                    'urls': {
                        'pc': restaurant.get('urls', {}).get('pc', ''),
                        'mobile': restaurant.get('urls', {}).get('mobile', '')
                    },
                    'photo': self._get_restaurant_photo(restaurant.get('photo', {})),
                    'open': restaurant.get('open', ''),
                    'close': restaurant.get('close', ''),
                    'party_capacity': restaurant.get('party_capacity', 0),
                    'wifi': restaurant.get('wifi', ''),
                    'wedding': restaurant.get('wedding', ''),
                    'course': restaurant.get('course', ''),
                    'free_drink': restaurant.get('free_drink', ''),
                    'free_food': restaurant.get('free_food', ''),
                    'private_room': restaurant.get('private_room', ''),
                    'horigotatsu': restaurant.get('horigotatsu', ''),
                    'tatami': restaurant.get('tatami', ''),
                    'card': restaurant.get('card', ''),
                    'non_smoking': restaurant.get('non_smoking', ''),
                    'charter': restaurant.get('charter', ''),
                    'ktai': restaurant.get('ktai', ''),
                    'parking': restaurant.get('parking', ''),
                    'barrier_free': restaurant.get('barrier_free', ''),
                    'other_memo': restaurant.get('other_memo', ''),
                    'sommelier': restaurant.get('sommelier', ''),
                    'open_air': restaurant.get('open_air', ''),
                    'show': restaurant.get('show', ''),
                    'equipment': restaurant.get('equipment', ''),
                    'karaoke': restaurant.get('karaoke', ''),
                    'band': restaurant.get('band', ''),
                    'tv': restaurant.get('tv', ''),
                    'english': restaurant.get('english', ''),
                    'pet': restaurant.get('pet', ''),
                    'child': restaurant.get('child', ''),
                    'lunch': restaurant.get('lunch', ''),
                    'midnight': restaurant.get('midnight', ''),
                    'shop_detail_memo': restaurant.get('shop_detail_memo', ''),
                    'source': 'hotpepper'
                }
                
                formatted_restaurants.append(formatted_restaurant)
                
            except (ValueError, TypeError, KeyError) as e:
                print(f"レストランデータ整形エラー (ID: {restaurant.get('id', 'unknown')}): {e}")
                continue
        
        return formatted_restaurants
    
    def _parse_budget_info(self, budget_data: Dict) -> int:
        """
        予算情報を解析して平均予算を算出
        
        Args:
            budget_data (dict): Hot Pepper APIの予算データ
            
        Returns:
            int: 平均予算（円）
        """
        try:
            budget_code = budget_data.get('code', '')
            
            # 予算コードから金額を取得
            if budget_code in self.BUDGET_CODES:
                return self.BUDGET_CODES[budget_code]
            
            # 予算名から推定（フォールバック）
            budget_name = budget_data.get('name', '').lower()
            
            if '500' in budget_name:
                return 500
            elif '1000' in budget_name or '1,000' in budget_name:
                return 1000
            elif '1500' in budget_name or '1,500' in budget_name:
                return 1500
            elif '2000' in budget_name or '2,000' in budget_name:
                return 2000
            elif '3000' in budget_name or '3,000' in budget_name:
                return 3000
            else:
                # デフォルト値（ランチ予算制限を超える値）
                return 2000
                
        except Exception:
            return 2000  # デフォルト値
    
    def _get_restaurant_photo(self, photo_data: Dict) -> str:
        """
        レストランの写真URLを取得
        
        Args:
            photo_data (dict): Hot Pepper APIの写真データ
            
        Returns:
            str: 写真URL（存在しない場合は空文字列）
        """
        try:
            # PCサイズの写真を優先
            if 'pc' in photo_data:
                pc_photos = photo_data['pc']
                if 'l' in pc_photos:  # 大サイズ
                    return pc_photos['l']
                elif 'm' in pc_photos:  # 中サイズ
                    return pc_photos['m']
                elif 's' in pc_photos:  # 小サイズ
                    return pc_photos['s']
            
            # モバイルサイズの写真をフォールバック
            if 'mobile' in photo_data:
                mobile_photos = photo_data['mobile']
                if 'l' in mobile_photos:
                    return mobile_photos['l']
                elif 's' in mobile_photos:
                    return mobile_photos['s']
            
            return ''
            
        except Exception:
            return ''
    
    def get_restaurant_by_id(self, restaurant_id: str) -> Optional[Dict]:
        """
        レストランIDから詳細情報を取得
        
        Args:
            restaurant_id (str): レストランID
            
        Returns:
            dict: レストラン詳細情報、見つからない場合はNone
        """
        # APIキーが設定されていない場合はNoneを返す
        if not self.api_key:
            return None
        
        try:
            params = {
                'key': self.api_key,
                'id': restaurant_id,
                'format': 'json'
            }
            
            response = requests.get(self.api_base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data and 'shop' in data['results']:
                shops = data['results']['shop']
                if shops:
                    return self._format_restaurant_data([shops[0]])[0]
            
            return None
            
        except Exception as e:
            print(f"レストラン詳細取得エラー (ID: {restaurant_id}): {e}")
            return None
    
    def _get_fallback_cache_data(self, cache_key: str) -> List[Dict]:
        """
        期限切れでも利用可能なキャッシュデータを取得（フォールバック用）
        
        Args:
            cache_key (str): キャッシュキー
            
        Returns:
            list: キャッシュされたレストラン情報、存在しない場合は空リスト
        """
        try:
            from database import get_db_connection
            
            with get_db_connection(self.cache_service.db_path) as conn:
                cursor = conn.execute('''
                    SELECT data FROM cache 
                    WHERE cache_key = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (cache_key,))
                
                row = cursor.fetchone()
                
                if row is None:
                    return []
                
                # 期限切れでもデータを返す（フォールバック用）
                fallback_data = self.cache_service.deserialize_data(row['data'])
                
                # ソース情報を更新
                for restaurant in fallback_data:
                    restaurant['source'] = 'fallback_cache'
                
                print(f"フォールバック用キャッシュデータを使用（期限切れ）: {len(fallback_data)}件")
                return fallback_data
                
        except Exception as e:
            print(f"フォールバックキャッシュ取得エラー: {e}")
            return []
    
    def validate_restaurant_data(self, restaurant_data: Dict) -> bool:
        """
        レストラン情報データの妥当性を検証
        
        Args:
            restaurant_data (dict): レストラン情報
            
        Returns:
            bool: 妥当な場合True
        """
        try:
            # 必須フィールドの存在確認
            required_fields = ['id', 'name', 'lat', 'lng']
            for field in required_fields:
                if field not in restaurant_data or not restaurant_data[field]:
                    return False
            
            # 座標の範囲確認
            lat = float(restaurant_data['lat'])
            lng = float(restaurant_data['lng'])
            
            if not (-90 <= lat <= 90):
                return False
            if not (-180 <= lng <= 180):
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False


# 使用例とテスト用コード
if __name__ == '__main__':
    """
    RestaurantServiceのテスト実行
    """
    print("RestaurantService テスト実行")
    print("=" * 40)
    
    # RestaurantServiceインスタンス作成
    restaurant_service = RestaurantService()
    
    # 東京駅の座標
    tokyo_lat, tokyo_lon = 35.6812, 139.7671
    
    # レストラン検索テスト
    print("1. レストラン検索:")
    restaurants = restaurant_service.search_restaurants(tokyo_lat, tokyo_lon, radius=1)
    print(f"   検索結果: {len(restaurants)}件")
    
    if restaurants:
        # 最初のレストラン情報を表示
        first_restaurant = restaurants[0]
        print(f"   例: {first_restaurant['name']}")
        print(f"       ジャンル: {first_restaurant['genre']}")
        print(f"       予算: ¥{first_restaurant['budget_average']}")
        print(f"       住所: {first_restaurant['address']}")
    
    # 予算フィルタリングテスト
    print("\n2. 予算フィルタリング:")
    lunch_restaurants = restaurant_service.filter_by_budget(restaurants, 1200)
    print(f"   フィルタリング後: {len(lunch_restaurants)}件")
    
    # ランチレストラン検索テスト
    print("\n3. ランチレストラン検索:")
    lunch_only = restaurant_service.search_lunch_restaurants(tokyo_lat, tokyo_lon)
    print(f"   ランチ適合: {len(lunch_only)}件")
    
    # データ妥当性検証テスト
    if restaurants:
        print(f"\n4. データ妥当性検証: {restaurant_service.validate_restaurant_data(restaurants[0])}")
    
    print("\nテスト完了")