#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RestaurantSelector - 繝ｬ繧ｹ繝医Λ繝ｳ驕ｸ謚槭Ο繧ｸ繝・け繧ｯ繝ｩ繧ｹ
讀懃ｴ｢邨先棡縺九ｉ繝ｩ繝ｳ繝繝驕ｸ謚樊ｩ溯・縺ｨ繝ｬ繧ｹ繝医Λ繝ｳ繝・・繧ｿ縺ｨ霍晞屬諠・ｱ縺ｮ邨ｱ蜷域ｩ溯・繧呈署萓・

縺薙・繧ｯ繝ｩ繧ｹ縺ｯ莉･荳九・讖溯・繧呈署萓帙＠縺ｾ縺・
- 讀懃ｴ｢邨先棡縺九ｉ繝ｩ繝ｳ繝繝驕ｸ謚樊ｩ溯・
- 繝ｬ繧ｹ繝医Λ繝ｳ繝・・繧ｿ縺ｨ霍晞屬諠・ｱ縺ｮ邨ｱ蜷域ｩ溯・
- 驕ｸ謚樒ｵ先棡縺ｮ謨ｴ蠖｢縺ｨ繝輔か繝ｼ繝槭ャ繝域ｩ溯・
"""

import random
from typing import Dict, List, Optional
from distance_calculator import DistanceCalculator
from error_handler import ErrorHandler


class RestaurantSelector:
    """
    繝ｬ繧ｹ繝医Λ繝ｳ驕ｸ謚槭→繝・・繧ｿ邨ｱ蜷医ｒ陦後≧繝薙ず繝阪せ繝ｭ繧ｸ繝・け繧ｯ繝ｩ繧ｹ

    繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢邨先棡縺九ｉ繝ｩ繝ｳ繝繝縺ｫ驕ｸ謚槭＠縲∬ｷ晞屬諠・ｱ繧堤ｵｱ蜷医＠縺ｦ
    繝ｦ繝ｼ繧ｶ繝ｼ縺ｫ謠蝉ｾ帙☆繧区怙邨ら噪縺ｪ繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ繧堤函謌舌☆繧九・
    """

    def __init__(self, distance_calculator: Optional[DistanceCalculator] = None,
                 error_handler: Optional[ErrorHandler] = None):
        """
        RestaurantSelector繧貞・譛溷喧

        Args:
            distance_calculator (DistanceCalculator, optional): 霍晞屬險育ｮ励し繝ｼ繝薙せ
            error_handler (ErrorHandler, optional): 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ
        """
        self.error_handler = error_handler or ErrorHandler()
        self.distance_calculator = distance_calculator or DistanceCalculator(self.error_handler)
        self.random = random.Random()  # 繝・せ繝亥庄閭ｽ諤ｧ縺ｮ縺溘ａ縺ｮRandom繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ

    def select_random_restaurant(self, restaurants: List[Dict], user_lat: float, user_lon: float) -> Optional[Dict]:
        """
        繝ｬ繧ｹ繝医Λ繝ｳ繝ｪ繧ｹ繝医°繧峨Λ繝ｳ繝繝縺ｫ1縺､繧帝∈謚槭＠縲∬ｷ晞屬諠・ｱ繧堤ｵｱ蜷・

        Args:
            restaurants (list): 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ縺ｮ繝ｪ繧ｹ繝・
            user_lat (float): 繝ｦ繝ｼ繧ｶ繝ｼ縺ｮ邱ｯ蠎ｦ
            user_lon (float): 繝ｦ繝ｼ繧ｶ繝ｼ縺ｮ邨悟ｺｦ

        Returns:
            dict: 霍晞屬諠・ｱ縺檎ｵｱ蜷医＆繧後◆繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ縲・∈謚槭〒縺阪↑縺・ｴ蜷医・None

        Example:
            >>> selector = RestaurantSelector()
            >>> restaurants = [{'id': '1', 'name': 'Test Restaurant', 'lat': 35.6812, 'lng': 139.7671}]
            >>> result = selector.select_random_restaurant(restaurants, 35.6800, 139.7700)
            >>> print(result['name'])  # 'Test Restaurant'
            >>> print(result['distance_info']['distance_display'])  # '邏・00m'
        """
        try:
            # 繝ｬ繧ｹ繝医Λ繝ｳ繝ｪ繧ｹ繝医′遨ｺ縺ｮ蝣ｴ蜷・
            if not restaurants:
                no_restaurant_error = ValueError("驕ｸ謚槫庄閭ｽ縺ｪ繝ｬ繧ｹ繝医Λ繝ｳ縺後≠繧翫∪縺帙ｓ")
                error_info = self.error_handler.handle_restaurant_error(no_restaurant_error, fallback_available=False)
                print(f"繝ｬ繧ｹ繝医Λ繝ｳ驕ｸ謚槭お繝ｩ繝ｼ: {error_info['message']}")
                return None

            # 譛牙柑縺ｪ繝ｬ繧ｹ繝医Λ繝ｳ縺ｮ縺ｿ繧偵ヵ繧｣繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ
            valid_restaurants = self._filter_valid_restaurants(restaurants)

            if not valid_restaurants:
                invalid_data_error = ValueError("譛牙柑縺ｪ繝ｬ繧ｹ繝医Λ繝ｳ繝・・繧ｿ縺後≠繧翫∪縺帙ｓ")
                error_info = self.error_handler.handle_restaurant_error(invalid_data_error, fallback_available=False)
                print(f"繝ｬ繧ｹ繝医Λ繝ｳ驕ｸ謚槭お繝ｩ繝ｼ: {error_info['message']}")
                return None

            # 繝ｩ繝ｳ繝繝縺ｫ1縺､縺ｮ繝ｬ繧ｹ繝医Λ繝ｳ繧帝∈謚・
            selected_restaurant = self.random.choice(valid_restaurants)

            print(f"繝ｬ繧ｹ繝医Λ繝ｳ繧帝∈謚・ {selected_restaurant['name']}")

            # 霍晞屬諠・ｱ繧定ｨ育ｮ励＠縺ｦ邨ｱ蜷・
            restaurant_with_distance = self._integrate_distance_info(
                selected_restaurant, user_lat, user_lon
            )

            return restaurant_with_distance

        except Exception as e:
            error_info = self.error_handler.handle_restaurant_error(e, fallback_available=False)
            print(f"繝ｬ繧ｹ繝医Λ繝ｳ驕ｸ謚槭お繝ｩ繝ｼ: {error_info['message']}")
            return None

    def select_multiple_restaurants(self, restaurants: List[Dict], user_lat: float, user_lon: float, count: int = 3) -> List[Dict]:
        """
        繝ｬ繧ｹ繝医Λ繝ｳ繝ｪ繧ｹ繝医°繧芽､・焚繧偵Λ繝ｳ繝繝縺ｫ驕ｸ謚槭＠縲∬ｷ晞屬諠・ｱ繧堤ｵｱ蜷・

        Args:
            restaurants (list): 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ縺ｮ繝ｪ繧ｹ繝・
            user_lat (float): 繝ｦ繝ｼ繧ｶ繝ｼ縺ｮ邱ｯ蠎ｦ
            user_lon (float): 繝ｦ繝ｼ繧ｶ繝ｼ縺ｮ邨悟ｺｦ
            count (int): 驕ｸ謚槭☆繧倶ｻｶ謨ｰ縲√ョ繝輔か繝ｫ繝医・3莉ｶ

        Returns:
            list: 霍晞屬諠・ｱ縺檎ｵｱ蜷医＆繧後◆繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ縺ｮ繝ｪ繧ｹ繝・
        """
        try:
            # 繝ｬ繧ｹ繝医Λ繝ｳ繝ｪ繧ｹ繝医′遨ｺ縺ｮ蝣ｴ蜷・
            if not restaurants:
                return []

            # 譛牙柑縺ｪ繝ｬ繧ｹ繝医Λ繝ｳ縺ｮ縺ｿ繧偵ヵ繧｣繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ
            valid_restaurants = self._filter_valid_restaurants(restaurants)

            if not valid_restaurants:
                return []

            # 驕ｸ謚樔ｻｶ謨ｰ繧定ｪｿ謨ｴ・亥茜逕ｨ蜿ｯ閭ｽ縺ｪ莉ｶ謨ｰ繧定ｶ・∴縺ｪ縺・ｼ・
            actual_count = min(count, len(valid_restaurants))

            # 繝ｩ繝ｳ繝繝縺ｫ隍・焚縺ｮ繝ｬ繧ｹ繝医Λ繝ｳ繧帝∈謚橸ｼ磯㍾隍・↑縺暦ｼ・
            selected_restaurants = self.random.sample(valid_restaurants, actual_count)

            print(f"{actual_count}莉ｶ縺ｮ繝ｬ繧ｹ繝医Λ繝ｳ繧帝∈謚・)

            # 蜷・Ξ繧ｹ繝医Λ繝ｳ縺ｫ霍晞屬諠・ｱ繧堤ｵｱ蜷・
            restaurants_with_distance = []
            for restaurant in selected_restaurants:
                restaurant_with_distance = self._integrate_distance_info(
                    restaurant, user_lat, user_lon
                )
                if restaurant_with_distance:
                    restaurants_with_distance.append(restaurant_with_distance)

            # 霍晞屬鬆・〒繧ｽ繝ｼ繝茨ｼ郁ｿ代＞鬆・ｼ・
            restaurants_with_distance.sort(key=lambda r: r['distance_info']['distance_km'])

            return restaurants_with_distance

        except Exception as e:
            print(f"隍・焚繝ｬ繧ｹ繝医Λ繝ｳ驕ｸ謚槭お繝ｩ繝ｼ: {e}")
            return []

    def _filter_valid_restaurants(self, restaurants: List[Dict]) -> List[Dict]:
        """
        譛牙柑縺ｪ繝ｬ繧ｹ繝医Λ繝ｳ繝・・繧ｿ縺ｮ縺ｿ繧偵ヵ繧｣繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ

        Args:
            restaurants (list): 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ縺ｮ繝ｪ繧ｹ繝・

        Returns:
            list: 譛牙柑縺ｪ繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ縺ｮ繝ｪ繧ｹ繝・
        """
        valid_restaurants = []

        for restaurant in restaurants:
            if self._is_valid_restaurant(restaurant):
                valid_restaurants.append(restaurant)
            else:
                print(f"辟｡蜉ｹ縺ｪ繝ｬ繧ｹ繝医Λ繝ｳ繝・・繧ｿ繧偵せ繧ｭ繝・・: {restaurant.get('name', 'unknown')}")

        return valid_restaurants

    def _is_valid_restaurant(self, restaurant: Dict) -> bool:
        """
        繝ｬ繧ｹ繝医Λ繝ｳ繝・・繧ｿ縺ｮ螯･蠖捺ｧ繧呈､懆ｨｼ

        Args:
            restaurant (dict): 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ

        Returns:
            bool: 譛牙柑縺ｪ蝣ｴ蜷・rue
        """
        try:
            # 蠢・医ヵ繧｣繝ｼ繝ｫ繝峨・蟄伜惠遒ｺ隱・
            required_fields = ['id', 'name', 'lat', 'lng']
            for field in required_fields:
                if field not in restaurant or not restaurant[field]:
                    return False

            # 蠎ｧ讓吶・螯･蠖捺ｧ遒ｺ隱・
            lat = float(restaurant['lat'])
            lng = float(restaurant['lng'])

            if not (-90 <= lat <= 90):
                return False
            if not (-180 <= lng <= 180):
                return False

            # 蜷榊燕縺檎ｩｺ縺ｧ縺ｪ縺・％縺ｨ繧堤｢ｺ隱・
            if not restaurant['name'].strip():
                return False

            return True

        except (ValueError, TypeError, AttributeError):
            return False

    def _integrate_distance_info(self, restaurant: Dict, user_lat: float, user_lon: float) -> Optional[Dict]:
        """
        繝ｬ繧ｹ繝医Λ繝ｳ繝・・繧ｿ縺ｫ霍晞屬諠・ｱ繧堤ｵｱ蜷・

        Args:
            restaurant (dict): 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ
            user_lat (float): 繝ｦ繝ｼ繧ｶ繝ｼ縺ｮ邱ｯ蠎ｦ
            user_lon (float): 繝ｦ繝ｼ繧ｶ繝ｼ縺ｮ邨悟ｺｦ

        Returns:
            dict: 霍晞屬諠・ｱ縺檎ｵｱ蜷医＆繧後◆繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ縲√お繝ｩ繝ｼ譎ゅ・None
        """
        try:
            # 繝ｬ繧ｹ繝医Λ繝ｳ縺ｮ蠎ｧ讓吶ｒ蜿門ｾ・
            restaurant_lat = float(restaurant['lat'])
            restaurant_lng = float(restaurant['lng'])

            # 霍晞屬諠・ｱ繧定ｨ育ｮ・
            distance_info = self.distance_calculator.calculate_walking_distance(
                user_lat, user_lon, restaurant_lat, restaurant_lng
            )

            # 繝ｬ繧ｹ繝医Λ繝ｳ繝・・繧ｿ繧偵さ繝斐・縺励※霍晞屬諠・ｱ繧定ｿｽ蜉
            restaurant_with_distance = restaurant.copy()
            restaurant_with_distance['distance_info'] = distance_info

            # 霑ｽ蜉縺ｮ陦ｨ遉ｺ逕ｨ諠・ｱ繧堤函謌・
            restaurant_with_distance['display_info'] = self._generate_display_info(
                restaurant_with_distance
            )

            return restaurant_with_distance

        except Exception as e:
            error_info = self.error_handler.handle_distance_calculation_error(e)
            print(f"霍晞屬諠・ｱ邨ｱ蜷医お繝ｩ繝ｼ (繝ｬ繧ｹ繝医Λ繝ｳ: {restaurant.get('name', 'unknown')}): {error_info['message']}")

            # 繧ｨ繝ｩ繝ｼ譎ゅ〒繧ゅΞ繧ｹ繝医Λ繝ｳ諠・ｱ縺ｯ霑斐☆縺後∬ｷ晞屬諠・ｱ縺ｯ繝・ヵ繧ｩ繝ｫ繝亥､繧剃ｽｿ逕ｨ
            restaurant_with_distance = restaurant.copy()
            restaurant_with_distance['distance_info'] = {
                'distance_km': 0.5,
                'distance_m': 500,
                'walking_time_minutes': 8,
                'distance_display': "邏・00m",
                'time_display': "蠕呈ｭｩ邏・蛻・,
                'error_info': error_info
            }
            restaurant_with_distance['display_info'] = self._generate_display_info(restaurant_with_distance)

            return restaurant_with_distance

    def _generate_display_info(self, restaurant: Dict) -> Dict:
        """
        陦ｨ遉ｺ逕ｨ縺ｮ霑ｽ蜉諠・ｱ繧堤函謌・

        Args:
            restaurant (dict): 霍晞屬諠・ｱ縺檎ｵｱ蜷医＆繧後◆繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ

        Returns:
            dict: 陦ｨ遉ｺ逕ｨ諠・ｱ
        """
        try:
            distance_info = restaurant.get('distance_info', {})

            # 莠育ｮ玲ュ蝣ｱ縺ｮ陦ｨ遉ｺ逕ｨ譁・ｭ怜・繧堤函謌・
            budget_display = self._format_budget_display(restaurant.get('budget_average', 0))

            # 繧ｸ繝｣繝ｳ繝ｫ諠・ｱ縺ｮ陦ｨ遉ｺ逕ｨ譁・ｭ怜・繧堤函謌・
            genre_display = restaurant.get('genre', '').strip() or '譁咏炊'

            # 繧｢繧ｯ繧ｻ繧ｹ諠・ｱ縺ｮ陦ｨ遉ｺ逕ｨ譁・ｭ怜・繧堤函謌・
            access_display = self._format_access_display(restaurant.get('access', ''))

            # 蝟ｶ讌ｭ譎る俣縺ｮ陦ｨ遉ｺ逕ｨ譁・ｭ怜・繧堤函謌・
            hours_display = self._format_hours_display(restaurant.get('open', ''))

            display_info = {
                'budget_display': budget_display,
                'genre_display': genre_display,
                'access_display': access_display,
                'hours_display': hours_display,
                'distance_display': distance_info.get('distance_display', '荳肴・'),
                'time_display': distance_info.get('time_display', '蠕呈ｭｩ譎る俣荳肴・'),
                'photo_url': restaurant.get('photo', ''),
                'map_url': self._generate_map_url(restaurant),
                'hotpepper_url': restaurant.get('urls', {}).get('pc', ''),
                'summary': self._generate_summary(restaurant)
            }

            return display_info

        except Exception as e:
            print(f"陦ｨ遉ｺ諠・ｱ逕滓・繧ｨ繝ｩ繝ｼ: {e}")
            return {
                'budget_display': '莠育ｮ嶺ｸ肴・',
                'genre_display': '譁咏炊',
                'access_display': '',
                'hours_display': '',
                'distance_display': '霍晞屬荳肴・',
                'time_display': '蠕呈ｭｩ譎る俣荳肴・',
                'photo_url': '',
                'map_url': '',
                'hotpepper_url': '',
                'summary': ''
            }

    def _format_budget_display(self, budget_average: int) -> str:
        """
        莠育ｮ励・陦ｨ遉ｺ逕ｨ譁・ｭ怜・繧堤函謌・

        Args:
            budget_average (int): 蟷ｳ蝮・ｺ育ｮ暦ｼ亥・・・

        Returns:
            str: 陦ｨ遉ｺ逕ｨ莠育ｮ玲枚蟄怜・
        """
        try:
            if budget_average <= 0:
                return '莠育ｮ嶺ｸ肴・'
            elif budget_average <= 500:
                return '・楪･500'
            elif budget_average <= 1000:
                return 'ﾂ･500・楪･1,000'
            elif budget_average <= 1500:
                return 'ﾂ･1,000・楪･1,500'
            elif budget_average <= 2000:
                return 'ﾂ･1,500・楪･2,000'
            else:
                return f'ﾂ･{budget_average:,}・・
        except Exception:
            return '莠育ｮ嶺ｸ肴・'

    def _format_access_display(self, access: str) -> str:
        """
        繧｢繧ｯ繧ｻ繧ｹ諠・ｱ縺ｮ陦ｨ遉ｺ逕ｨ譁・ｭ怜・繧堤函謌・

        Args:
            access (str): 繧｢繧ｯ繧ｻ繧ｹ諠・ｱ

        Returns:
            str: 陦ｨ遉ｺ逕ｨ繧｢繧ｯ繧ｻ繧ｹ譁・ｭ怜・
        """
        try:
            if not access or not access.strip():
                return ''

            # 髟ｷ縺吶℃繧句ｴ蜷医・逵∫払
            if len(access) > 100:
                return access[:97] + '...'

            return access.strip()

        except Exception:
            return ''

    def _format_hours_display(self, hours: str) -> str:
        """
        蝟ｶ讌ｭ譎る俣縺ｮ陦ｨ遉ｺ逕ｨ譁・ｭ怜・繧堤函謌・

        Args:
            hours (str): 蝟ｶ讌ｭ譎る俣諠・ｱ

        Returns:
            str: 陦ｨ遉ｺ逕ｨ蝟ｶ讌ｭ譎る俣譁・ｭ怜・
        """
        try:
            if not hours or not hours.strip():
                return ''

            # 髟ｷ縺吶℃繧句ｴ蜷医・逵∫払
            if len(hours) > 50:
                return hours[:47] + '...'

            return hours.strip()

        except Exception:
            return ''

    def _generate_map_url(self, restaurant: Dict) -> str:
        """
        蝨ｰ蝗ｳURL繧堤函謌・

        Args:
            restaurant (dict): 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ

        Returns:
            str: Google Maps URL
        """
        try:
            lat = restaurant.get('lat', 0)
            lng = restaurant.get('lng', 0)
            name = restaurant.get('name', '')

            if lat and lng:
                # Google Maps URL繧堤函謌・
                return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}&query_place_id={name}"

            return ''

        except Exception:
            return ''

    def _generate_summary(self, restaurant: Dict) -> str:
        """
        繝ｬ繧ｹ繝医Λ繝ｳ縺ｮ隕∫ｴ・ュ蝣ｱ繧堤函謌・

        Args:
            restaurant (dict): 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ

        Returns:
            str: 隕∫ｴ・枚蟄怜・
        """
        try:
            name = restaurant.get('name', '')
            genre = restaurant.get('genre', '')
            distance_info = restaurant.get('distance_info', {})
            distance_display = distance_info.get('distance_display', '')
            time_display = distance_info.get('time_display', '')

            summary_parts = []

            if genre:
                summary_parts.append(f"{genre}縺ｮ")

            summary_parts.append(f"{name}")

            if distance_display and time_display:
                summary_parts.append(f"・・distance_display}繝ｻ{time_display}・・)

            return ''.join(summary_parts)

        except Exception:
            return restaurant.get('name', '繝ｬ繧ｹ繝医Λ繝ｳ')

    def set_random_seed(self, seed: int) -> None:
        """
        繝ｩ繝ｳ繝繝繧ｷ繝ｼ繝峨ｒ險ｭ螳夲ｼ医ユ繧ｹ繝育畑・・

        Args:
            seed (int): 繝ｩ繝ｳ繝繝繧ｷ繝ｼ繝牙､
        """
        self.random.seed(seed)

    def get_selection_statistics(self, restaurants: List[Dict]) -> Dict:
        """
        驕ｸ謚槫ｯｾ雎｡繝ｬ繧ｹ繝医Λ繝ｳ縺ｮ邨ｱ險域ュ蝣ｱ繧貞叙蠕・

        Args:
            restaurants (list): 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ縺ｮ繝ｪ繧ｹ繝・

        Returns:
            dict: 邨ｱ險域ュ蝣ｱ
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

            # 繧ｸ繝｣繝ｳ繝ｫ蛻･髮・ｨ・
            genres = {}
            budget_ranges = {}

            for restaurant in valid_restaurants:
                # 繧ｸ繝｣繝ｳ繝ｫ髮・ｨ・
                genre = restaurant.get('genre', '荳肴・')
                genres[genre] = genres.get(genre, 0) + 1

                # 莠育ｮ礼ｯ・峇髮・ｨ・
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
            print(f"邨ｱ險域ュ蝣ｱ蜿門ｾ励お繝ｩ繝ｼ: {e}")
            return {
                'total_count': len(restaurants) if restaurants else 0,
                'valid_count': 0,
                'invalid_count': len(restaurants) if restaurants else 0,
                'genres': {},
                'budget_ranges': {}
            }

    def _get_budget_range(self, budget: int) -> str:
        """
        莠育ｮ励°繧我ｺ育ｮ礼ｯ・峇譁・ｭ怜・繧貞叙蠕・

        Args:
            budget (int): 莠育ｮ暦ｼ亥・・・

        Returns:
            str: 莠育ｮ礼ｯ・峇譁・ｭ怜・
        """
        if budget <= 500:
            return '・楪･500'
        elif budget <= 1000:
            return 'ﾂ･500・楪･1,000'
        elif budget <= 1500:
            return 'ﾂ･1,000・楪･1,500'
        elif budget <= 2000:
            return 'ﾂ･1,500・楪･2,000'
        else:
            return 'ﾂ･2,000・・


# 菴ｿ逕ｨ萓九→繝・せ繝育畑繧ｳ繝ｼ繝・
if __name__ == '__main__':
    """
    RestaurantSelector縺ｮ繝・せ繝亥ｮ溯｡・
    """
    print("RestaurantSelector 繝・せ繝亥ｮ溯｡・)
    print("=" * 40)

    # 繝・せ繝育畑繝ｬ繧ｹ繝医Λ繝ｳ繝・・繧ｿ
    test_restaurants = [
        {
            'id': '1',
            'name': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ1',
            'lat': 35.6812,
            'lng': 139.7671,
            'genre': '繧､繧ｿ繝ｪ繧｢繝ｳ',
            'budget_average': 1000,
            'address': '譚ｱ莠ｬ驛ｽ蜊・ｻ｣逕ｰ蛹ｺ荳ｸ縺ｮ蜀・-1-1',
            'photo': 'https://example.com/photo1.jpg',
            'urls': {'pc': 'https://example.com/restaurant1'}
        },
        {
            'id': '2',
            'name': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ2',
            'lat': 35.6820,
            'lng': 139.7680,
            'genre': '蜥碁｣・,
            'budget_average': 800,
            'address': '譚ｱ莠ｬ驛ｽ蜊・ｻ｣逕ｰ蛹ｺ荳ｸ縺ｮ蜀・-2-2',
            'photo': 'https://example.com/photo2.jpg',
            'urls': {'pc': 'https://example.com/restaurant2'}
        },
        {
            'id': '3',
            'name': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ3',
            'lat': 35.6800,
            'lng': 139.7650,
            'genre': '荳ｭ闖ｯ',
            'budget_average': 1200,
            'address': '譚ｱ莠ｬ驛ｽ蜊・ｻ｣逕ｰ蛹ｺ荳ｸ縺ｮ蜀・-3-3',
            'photo': '',
            'urls': {'pc': 'https://example.com/restaurant3'}
        }
    ]

    # RestaurantSelector繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ菴懈・
    selector = RestaurantSelector()

    # 繝ｦ繝ｼ繧ｶ繝ｼ菴咲ｽｮ・域擲莠ｬ鬧・ｻ倩ｿ托ｼ・
    user_lat, user_lon = 35.6812, 139.7671

    # 繝ｩ繝ｳ繝繝繧ｷ繝ｼ繝峨ｒ險ｭ螳夲ｼ医ユ繧ｹ繝育ｵ先棡縺ｮ蜀咲樟諤ｧ縺ｮ縺溘ａ・・
    selector.set_random_seed(42)

    # 1. 蜊倅ｸ繝ｬ繧ｹ繝医Λ繝ｳ驕ｸ謚槭ユ繧ｹ繝・
    print("1. 蜊倅ｸ繝ｬ繧ｹ繝医Λ繝ｳ驕ｸ謚・")
    selected = selector.select_random_restaurant(test_restaurants, user_lat, user_lon)
    if selected:
        print(f"   驕ｸ謚槭＆繧後◆繝ｬ繧ｹ繝医Λ繝ｳ: {selected['name']}")
        print(f"   繧ｸ繝｣繝ｳ繝ｫ: {selected['genre']}")
        print(f"   霍晞屬: {selected['distance_info']['distance_display']}")
        print(f"   蠕呈ｭｩ譎る俣: {selected['distance_info']['time_display']}")
        print(f"   隕∫ｴ・ {selected['display_info']['summary']}")

    # 2. 隍・焚繝ｬ繧ｹ繝医Λ繝ｳ驕ｸ謚槭ユ繧ｹ繝・
    print("\n2. 隍・焚繝ｬ繧ｹ繝医Λ繝ｳ驕ｸ謚・")
    multiple_selected = selector.select_multiple_restaurants(test_restaurants, user_lat, user_lon, 2)
    for i, restaurant in enumerate(multiple_selected, 1):
        print(f"   {i}. {restaurant['name']} - {restaurant['distance_info']['distance_display']}")

    # 3. 邨ｱ險域ュ蝣ｱ繝・せ繝・
    print("\n3. 邨ｱ險域ュ蝣ｱ:")
    stats = selector.get_selection_statistics(test_restaurants)
    print(f"   邱丈ｻｶ謨ｰ: {stats['total_count']}")
    print(f"   譛牙柑莉ｶ謨ｰ: {stats['valid_count']}")
    print(f"   繧ｸ繝｣繝ｳ繝ｫ蛻･: {stats['genres']}")
    print(f"   莠育ｮ礼ｯ・峇蛻･: {stats['budget_ranges']}")

    # 4. 遨ｺ繝ｪ繧ｹ繝医ユ繧ｹ繝・
    print("\n4. 遨ｺ繝ｪ繧ｹ繝亥・逅・")
    empty_result = selector.select_random_restaurant([], user_lat, user_lon)
    print(f"   遨ｺ繝ｪ繧ｹ繝医・邨先棡: {empty_result}")

    print("\n繝・せ繝亥ｮ御ｺ・)
