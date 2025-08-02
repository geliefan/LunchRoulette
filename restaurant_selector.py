#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RestaurantSelector - レストラン選択ロジッククラス
検索結果からランダム選択機能とレストランデータと距離情報の統合機能を提供

このクラスは以下の機能を提供します:
- 検索結果からランダム選択機能
- レストランデータと距離情報の統合機能
- 選択結果の整形とフォーマット機能
"""

import random
from typing import Dict, List, Optional, Tuple
from distance_calculator import DistanceCalculator
from error_handler import ErrorHandler


class RestaurantSelector:
    """
    レストラン選択とデータ統合を行うビジネスロジッククラス
    
    レストラン検索結果からランダムに選択し、距離情報を統合して
    ユーザーに提供する最終的なレストラン情報を生成する。
    """
    
    def __init__(self, distance_calculator: Optional[DistanceCalculator] = None, 
                 error_handler: Optional[ErrorHandler] = None):
        """
        RestaurantSelectorを初期化
        
        Args:
            distance_calculator (DistanceCalculator, optional): 距離計算サービス
            error_handler (ErrorHandler, optional): エラーハンドラー
        """
        self.error_handler = error_handler or ErrorHandler()
        self.distance_calculator = distance_calculator or DistanceCalculator(self.error_handler)
        self.random = random.Random()  # テスト可能性のためのRandomインスタンス
    
    def select_random_restaurant(self, restaurants: List[Dict], user_lat: float, user_lon: float) -> Optional[Dict]:
        """
        レストランリストからランダムに1つを選択し、距離情報を統合
        
        Args:
            restaurants (list): レストラン情報のリスト
            user_lat (float): ユーザーの緯度
            user_lon (float): ユーザーの経度
            
        Returns:
            dict: 距離情報が統合されたレストラン情報、選択できない場合はNone
            
        Example:
            >>> selector = RestaurantSelector()
            >>> restaurants = [{'id': '1', 'name': 'Test Restaurant', 'lat': 35.6812, 'lng': 139.7671}]
            >>> result = selector.select_random_restaurant(restaurants, 35.6800, 139.7700)
            >>> print(result['name'])  # 'Test Restaurant'
            >>> print(result['distance_info']['distance_display'])  # '約200m'
        """
        try:
            # レストランリストが空の場合
            if not restaurants:
                no_restaurant_error = ValueError("選択可能なレストランがありません")
                error_info = self.error_handler.handle_restaurant_error(no_restaurant_error, fallback_available=False)
                print(f"レストラン選択エラー: {error_info['message']}")
                return None
            
            # 有効なレストランのみをフィルタリング
            valid_restaurants = self._filter_valid_restaurants(restaurants)
            
            if not valid_restaurants:
                invalid_data_error = ValueError("有効なレストランデータがありません")
                error_info = self.error_handler.handle_restaurant_error(invalid_data_error, fallback_available=False)
                print(f"レストラン選択エラー: {error_info['message']}")
                return None
            
            # ランダムに1つのレストランを選択
            selected_restaurant = self.random.choice(valid_restaurants)
            
            print(f"レストランを選択: {selected_restaurant['name']}")
            
            # 距離情報を計算して統合
            restaurant_with_distance = self._integrate_distance_info(
                selected_restaurant, user_lat, user_lon
            )
            
            return restaurant_with_distance
            
        except Exception as e:
            error_info = self.error_handler.handle_restaurant_error(e, fallback_available=False)
            print(f"レストラン選択エラー: {error_info['message']}")
            return None
    
    def select_multiple_restaurants(self, restaurants: List[Dict], user_lat: float, user_lon: float, count: int = 3) -> List[Dict]:
        """
        レストランリストから複数をランダムに選択し、距離情報を統合
        
        Args:
            restaurants (list): レストラン情報のリスト
            user_lat (float): ユーザーの緯度
            user_lon (float): ユーザーの経度
            count (int): 選択する件数、デフォルトは3件
            
        Returns:
            list: 距離情報が統合されたレストラン情報のリスト
        """
        try:
            # レストランリストが空の場合
            if not restaurants:
                return []
            
            # 有効なレストランのみをフィルタリング
            valid_restaurants = self._filter_valid_restaurants(restaurants)
            
            if not valid_restaurants:
                return []
            
            # 選択件数を調整（利用可能な件数を超えない）
            actual_count = min(count, len(valid_restaurants))
            
            # ランダムに複数のレストランを選択（重複なし）
            selected_restaurants = self.random.sample(valid_restaurants, actual_count)
            
            print(f"{actual_count}件のレストランを選択")
            
            # 各レストランに距離情報を統合
            restaurants_with_distance = []
            for restaurant in selected_restaurants:
                restaurant_with_distance = self._integrate_distance_info(
                    restaurant, user_lat, user_lon
                )
                if restaurant_with_distance:
                    restaurants_with_distance.append(restaurant_with_distance)
            
            # 距離順でソート（近い順）
            restaurants_with_distance.sort(key=lambda r: r['distance_info']['distance_km'])
            
            return restaurants_with_distance
            
        except Exception as e:
            print(f"複数レストラン選択エラー: {e}")
            return []
    
    def _filter_valid_restaurants(self, restaurants: List[Dict]) -> List[Dict]:
        """
        有効なレストランデータのみをフィルタリング
        
        Args:
            restaurants (list): レストラン情報のリスト
            
        Returns:
            list: 有効なレストラン情報のリスト
        """
        valid_restaurants = []
        
        for restaurant in restaurants:
            if self._is_valid_restaurant(restaurant):
                valid_restaurants.append(restaurant)
            else:
                print(f"無効なレストランデータをスキップ: {restaurant.get('name', 'unknown')}")
        
        return valid_restaurants
    
    def _is_valid_restaurant(self, restaurant: Dict) -> bool:
        """
        レストランデータの妥当性を検証
        
        Args:
            restaurant (dict): レストラン情報
            
        Returns:
            bool: 有効な場合True
        """
        try:
            # 必須フィールドの存在確認
            required_fields = ['id', 'name', 'lat', 'lng']
            for field in required_fields:
                if field not in restaurant or not restaurant[field]:
                    return False
            
            # 座標の妥当性確認
            lat = float(restaurant['lat'])
            lng = float(restaurant['lng'])
            
            if not (-90 <= lat <= 90):
                return False
            if not (-180 <= lng <= 180):
                return False
            
            # 名前が空でないことを確認
            if not restaurant['name'].strip():
                return False
            
            return True
            
        except (ValueError, TypeError, AttributeError):
            return False
    
    def _integrate_distance_info(self, restaurant: Dict, user_lat: float, user_lon: float) -> Optional[Dict]:
        """
        レストランデータに距離情報を統合
        
        Args:
            restaurant (dict): レストラン情報
            user_lat (float): ユーザーの緯度
            user_lon (float): ユーザーの経度
            
        Returns:
            dict: 距離情報が統合されたレストラン情報、エラー時はNone
        """
        try:
            # レストランの座標を取得
            restaurant_lat = float(restaurant['lat'])
            restaurant_lng = float(restaurant['lng'])
            
            # 距離情報を計算
            distance_info = self.distance_calculator.calculate_walking_distance(
                user_lat, user_lon, restaurant_lat, restaurant_lng
            )
            
            # レストランデータをコピーして距離情報を追加
            restaurant_with_distance = restaurant.copy()
            restaurant_with_distance['distance_info'] = distance_info
            
            # 追加の表示用情報を生成
            restaurant_with_distance['display_info'] = self._generate_display_info(
                restaurant_with_distance
            )
            
            return restaurant_with_distance
            
        except Exception as e:
            error_info = self.error_handler.handle_distance_calculation_error(e)
            print(f"距離情報統合エラー (レストラン: {restaurant.get('name', 'unknown')}): {error_info['message']}")
            
            # エラー時でもレストラン情報は返すが、距離情報はデフォルト値を使用
            restaurant_with_distance = restaurant.copy()
            restaurant_with_distance['distance_info'] = {
                'distance_km': 0.5,
                'distance_m': 500,
                'walking_time_minutes': 8,
                'distance_display': "約500m",
                'time_display': "徒歩約8分",
                'error_info': error_info
            }
            restaurant_with_distance['display_info'] = self._generate_display_info(restaurant_with_distance)
            
            return restaurant_with_distance
    
    def _generate_display_info(self, restaurant: Dict) -> Dict:
        """
        表示用の追加情報を生成
        
        Args:
            restaurant (dict): 距離情報が統合されたレストラン情報
            
        Returns:
            dict: 表示用情報
        """
        try:
            distance_info = restaurant.get('distance_info', {})
            
            # 予算情報の表示用文字列を生成
            budget_display = self._format_budget_display(restaurant.get('budget_average', 0))
            
            # ジャンル情報の表示用文字列を生成
            genre_display = restaurant.get('genre', '').strip() or '料理'
            
            # アクセス情報の表示用文字列を生成
            access_display = self._format_access_display(restaurant.get('access', ''))
            
            # 営業時間の表示用文字列を生成
            hours_display = self._format_hours_display(restaurant.get('open', ''))
            
            display_info = {
                'budget_display': budget_display,
                'genre_display': genre_display,
                'access_display': access_display,
                'hours_display': hours_display,
                'distance_display': distance_info.get('distance_display', '不明'),
                'time_display': distance_info.get('time_display', '徒歩時間不明'),
                'photo_url': restaurant.get('photo', ''),
                'map_url': self._generate_map_url(restaurant),
                'hotpepper_url': restaurant.get('urls', {}).get('pc', ''),
                'summary': self._generate_summary(restaurant)
            }
            
            return display_info
            
        except Exception as e:
            print(f"表示情報生成エラー: {e}")
            return {
                'budget_display': '予算不明',
                'genre_display': '料理',
                'access_display': '',
                'hours_display': '',
                'distance_display': '距離不明',
                'time_display': '徒歩時間不明',
                'photo_url': '',
                'map_url': '',
                'hotpepper_url': '',
                'summary': ''
            }
    
    def _format_budget_display(self, budget_average: int) -> str:
        """
        予算の表示用文字列を生成
        
        Args:
            budget_average (int): 平均予算（円）
            
        Returns:
            str: 表示用予算文字列
        """
        try:
            if budget_average <= 0:
                return '予算不明'
            elif budget_average <= 500:
                return '～¥500'
            elif budget_average <= 1000:
                return '¥500～¥1,000'
            elif budget_average <= 1500:
                return '¥1,000～¥1,500'
            elif budget_average <= 2000:
                return '¥1,500～¥2,000'
            else:
                return f'¥{budget_average:,}～'
        except Exception:
            return '予算不明'
    
    def _format_access_display(self, access: str) -> str:
        """
        アクセス情報の表示用文字列を生成
        
        Args:
            access (str): アクセス情報
            
        Returns:
            str: 表示用アクセス文字列
        """
        try:
            if not access or not access.strip():
                return ''
            
            # 長すぎる場合は省略
            if len(access) > 100:
                return access[:97] + '...'
            
            return access.strip()
            
        except Exception:
            return ''
    
    def _format_hours_display(self, hours: str) -> str:
        """
        営業時間の表示用文字列を生成
        
        Args:
            hours (str): 営業時間情報
            
        Returns:
            str: 表示用営業時間文字列
        """
        try:
            if not hours or not hours.strip():
                return ''
            
            # 長すぎる場合は省略
            if len(hours) > 50:
                return hours[:47] + '...'
            
            return hours.strip()
            
        except Exception:
            return ''
    
    def _generate_map_url(self, restaurant: Dict) -> str:
        """
        地図URLを生成
        
        Args:
            restaurant (dict): レストラン情報
            
        Returns:
            str: Google Maps URL
        """
        try:
            lat = restaurant.get('lat', 0)
            lng = restaurant.get('lng', 0)
            name = restaurant.get('name', '')
            
            if lat and lng:
                # Google Maps URLを生成
                return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}&query_place_id={name}"
            
            return ''
            
        except Exception:
            return ''
    
    def _generate_summary(self, restaurant: Dict) -> str:
        """
        レストランの要約情報を生成
        
        Args:
            restaurant (dict): レストラン情報
            
        Returns:
            str: 要約文字列
        """
        try:
            name = restaurant.get('name', '')
            genre = restaurant.get('genre', '')
            distance_info = restaurant.get('distance_info', {})
            distance_display = distance_info.get('distance_display', '')
            time_display = distance_info.get('time_display', '')
            
            summary_parts = []
            
            if genre:
                summary_parts.append(f"{genre}の")
            
            summary_parts.append(f"{name}")
            
            if distance_display and time_display:
                summary_parts.append(f"（{distance_display}・{time_display}）")
            
            return ''.join(summary_parts)
            
        except Exception:
            return restaurant.get('name', 'レストラン')
    
    def set_random_seed(self, seed: int) -> None:
        """
        ランダムシードを設定（テスト用）
        
        Args:
            seed (int): ランダムシード値
        """
        self.random.seed(seed)
    
    def get_selection_statistics(self, restaurants: List[Dict]) -> Dict:
        """
        選択対象レストランの統計情報を取得
        
        Args:
            restaurants (list): レストラン情報のリスト
            
        Returns:
            dict: 統計情報
        """
        try:
            valid_restaurants = self._filter_valid_restaurants(restaurants)
            
            if not valid_restaurants:
                return {
                    'total_count': 0,
                    'valid_count': 0,
                    'invalid_count': len(restaurants),
                    'genres': {},
                    'budget_ranges': {}
                }
            
            # ジャンル別集計
            genres = {}
            budget_ranges = {}
            
            for restaurant in valid_restaurants:
                # ジャンル集計
                genre = restaurant.get('genre', '不明')
                genres[genre] = genres.get(genre, 0) + 1
                
                # 予算範囲集計
                budget = restaurant.get('budget_average', 0)
                budget_range = self._get_budget_range(budget)
                budget_ranges[budget_range] = budget_ranges.get(budget_range, 0) + 1
            
            return {
                'total_count': len(restaurants),
                'valid_count': len(valid_restaurants),
                'invalid_count': len(restaurants) - len(valid_restaurants),
                'genres': genres,
                'budget_ranges': budget_ranges
            }
            
        except Exception as e:
            print(f"統計情報取得エラー: {e}")
            return {
                'total_count': len(restaurants) if restaurants else 0,
                'valid_count': 0,
                'invalid_count': len(restaurants) if restaurants else 0,
                'genres': {},
                'budget_ranges': {}
            }
    
    def _get_budget_range(self, budget: int) -> str:
        """
        予算から予算範囲文字列を取得
        
        Args:
            budget (int): 予算（円）
            
        Returns:
            str: 予算範囲文字列
        """
        if budget <= 500:
            return '～¥500'
        elif budget <= 1000:
            return '¥500～¥1,000'
        elif budget <= 1500:
            return '¥1,000～¥1,500'
        elif budget <= 2000:
            return '¥1,500～¥2,000'
        else:
            return '¥2,000～'


# 使用例とテスト用コード
if __name__ == '__main__':
    """
    RestaurantSelectorのテスト実行
    """
    print("RestaurantSelector テスト実行")
    print("=" * 40)
    
    # テスト用レストランデータ
    test_restaurants = [
        {
            'id': '1',
            'name': 'テストレストラン1',
            'lat': 35.6812,
            'lng': 139.7671,
            'genre': 'イタリアン',
            'budget_average': 1000,
            'address': '東京都千代田区丸の内1-1-1',
            'photo': 'https://example.com/photo1.jpg',
            'urls': {'pc': 'https://example.com/restaurant1'}
        },
        {
            'id': '2',
            'name': 'テストレストラン2',
            'lat': 35.6820,
            'lng': 139.7680,
            'genre': '和食',
            'budget_average': 800,
            'address': '東京都千代田区丸の内1-2-2',
            'photo': 'https://example.com/photo2.jpg',
            'urls': {'pc': 'https://example.com/restaurant2'}
        },
        {
            'id': '3',
            'name': 'テストレストラン3',
            'lat': 35.6800,
            'lng': 139.7650,
            'genre': '中華',
            'budget_average': 1200,
            'address': '東京都千代田区丸の内1-3-3',
            'photo': '',
            'urls': {'pc': 'https://example.com/restaurant3'}
        }
    ]
    
    # RestaurantSelectorインスタンス作成
    selector = RestaurantSelector()
    
    # ユーザー位置（東京駅付近）
    user_lat, user_lon = 35.6812, 139.7671
    
    # ランダムシードを設定（テスト結果の再現性のため）
    selector.set_random_seed(42)
    
    # 1. 単一レストラン選択テスト
    print("1. 単一レストラン選択:")
    selected = selector.select_random_restaurant(test_restaurants, user_lat, user_lon)
    if selected:
        print(f"   選択されたレストラン: {selected['name']}")
        print(f"   ジャンル: {selected['genre']}")
        print(f"   距離: {selected['distance_info']['distance_display']}")
        print(f"   徒歩時間: {selected['distance_info']['time_display']}")
        print(f"   要約: {selected['display_info']['summary']}")
    
    # 2. 複数レストラン選択テスト
    print("\n2. 複数レストラン選択:")
    multiple_selected = selector.select_multiple_restaurants(test_restaurants, user_lat, user_lon, 2)
    for i, restaurant in enumerate(multiple_selected, 1):
        print(f"   {i}. {restaurant['name']} - {restaurant['distance_info']['distance_display']}")
    
    # 3. 統計情報テスト
    print("\n3. 統計情報:")
    stats = selector.get_selection_statistics(test_restaurants)
    print(f"   総件数: {stats['total_count']}")
    print(f"   有効件数: {stats['valid_count']}")
    print(f"   ジャンル別: {stats['genres']}")
    print(f"   予算範囲別: {stats['budget_ranges']}")
    
    # 4. 空リストテスト
    print("\n4. 空リスト処理:")
    empty_result = selector.select_random_restaurant([], user_lat, user_lon)
    print(f"   空リストの結果: {empty_result}")
    
    print("\nテスト完了")