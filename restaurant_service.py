#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RestaurantService - 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ繧ｵ繝ｼ繝薙せ繧ｯ繝ｩ繧ｹ
Hot Pepper Gourmet API縺九ｉ繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ繧貞叙蠕励☆繧区ｩ溯・繧呈署萓・

縺薙・繧ｯ繝ｩ繧ｹ縺ｯ莉･荳九・讖溯・繧呈署萓帙＠縺ｾ縺・
- Hot Pepper Gourmet Web API邨ｱ蜷・
- 蜊雁ｾ・km莉･蜀・・繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢讖溯・
- 繝ｩ繝ｳ繝∽ｺ育ｮ冷王ﾂ･1,200縺ｮ繝輔ぅ繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ讖溯・
- 繧ｭ繝｣繝・す繝･讖溯・縺ｨ縺ｮ邨ｱ蜷・
"""

import requests
import os
from typing import Dict, List, Optional
from cache_service import CacheService


class RestaurantService:
    """
    Hot Pepper Gourmet API縺九ｉ繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ繧貞叙蠕励☆繧九し繝ｼ繝薙せ

    謖・ｮ壹＆繧後◆蠎ｧ讓吝捉霎ｺ縺ｮ繝ｬ繧ｹ繝医Λ繝ｳ繧呈､懃ｴ｢縺励∽ｺ育ｮ励〒繝輔ぅ繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ縺励※
    繝ｩ繝ｳ繝√↓驕ｩ縺励◆繝ｬ繧ｹ繝医Λ繝ｳ繧呈署萓帙☆繧九・
    """

    # 莠育ｮ励さ繝ｼ繝峨・繝・ヴ繝ｳ繧ｰ・・ot Pepper API莉墓ｧ假ｼ・
    BUDGET_CODES = {
        'B009': 500,    # ・・00蜀・
        'B010': 1000,   # 501・・000蜀・
        'B011': 1500,   # 1001・・500蜀・
        'B001': 2000,   # 1501・・000蜀・
        'B002': 3000,   # 2001・・000蜀・
        'B003': 4000,   # 3001・・000蜀・
        'B008': 5000,   # 4001・・000蜀・
        'B004': 7000,   # 5001・・000蜀・
        'B005': 10000,  # 7001・・0000蜀・
        'B006': 15000,  # 10001・・5000蜀・
        'B012': 20000,  # 15001・・0000蜀・
        'B013': 30000,  # 20001・・0000蜀・
        'B014': 30001   # 30001蜀・ｽ・
    }

    # 繝ｩ繝ｳ繝∽ｺ育ｮ怜宛髯撰ｼ亥・・・
    LUNCH_BUDGET_LIMIT = 1200

    def __init__(self, api_key: Optional[str] = None, cache_service: Optional[CacheService] = None):
        """
        RestaurantService繧貞・譛溷喧

        Args:
            api_key (str, optional): Hot Pepper Gourmet API繧ｭ繝ｼ
            cache_service (CacheService, optional): 繧ｭ繝｣繝・す繝･繧ｵ繝ｼ繝薙せ
        """
        self.api_key = api_key or os.getenv('HOTPEPPER_API_KEY')
        self.cache_service = cache_service or CacheService()
        self.api_base_url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
        self.timeout = 10  # API繝ｪ繧ｯ繧ｨ繧ｹ繝医・繧ｿ繧､繝繧｢繧ｦ繝茨ｼ育ｧ抵ｼ・

        if not self.api_key:
            print("隴ｦ蜻・ Hot Pepper Gourmet API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺・∪縺帙ｓ縲・)

    def search_restaurants(self, lat: float, lon: float, radius: int = 1) -> List[Dict]:
        """
        謖・ｮ壹＆繧後◆蠎ｧ讓吝捉霎ｺ縺ｮ繝ｬ繧ｹ繝医Λ繝ｳ繧呈､懃ｴ｢

        Args:
            lat (float): 邱ｯ蠎ｦ
            lon (float): 邨悟ｺｦ
            radius (int): 讀懃ｴ｢蜊雁ｾ・ｼ・m・峨√ョ繝輔か繝ｫ繝医・1km

        Returns:
            list: 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ縺ｮ繝ｪ繧ｹ繝・

        Example:
            >>> restaurant_service = RestaurantService()
            >>> restaurants = restaurant_service.search_restaurants(35.6812, 139.7671)
            >>> print(f"Found {len(restaurants)} restaurants")
        """
        # 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ繧堤函謌・
        cache_key = self.cache_service.generate_cache_key(
            'restaurants',
            lat=round(lat, 4),
            lon=round(lon, 4),
            radius=radius
        )

        # 繧ｭ繝｣繝・す繝･縺九ｉ蜿門ｾ励ｒ隧ｦ陦・
        cached_data = self.cache_service.get_cached_data(cache_key)
        if cached_data:
            print(f"繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ繧偵く繝｣繝・す繝･縺九ｉ蜿門ｾ・ {len(cached_data)}莉ｶ")
            return cached_data

        # API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺・↑縺・ｴ蜷医・遨ｺ縺ｮ繝ｪ繧ｹ繝医ｒ霑斐☆
        if not self.api_key:
            print("API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺・↑縺・◆繧√√Ξ繧ｹ繝医Λ繝ｳ讀懃ｴ｢繧偵せ繧ｭ繝・・")
            return []

        try:
            # API繝代Λ繝｡繝ｼ繧ｿ繧呈ｧ狗ｯ・
            params = {
                'key': self.api_key,
                'lat': lat,
                'lng': lon,
                'range': self._convert_radius_to_range_code(radius),
                'count': 100,  # 譛螟ｧ蜿門ｾ嶺ｻｶ謨ｰ
                'format': 'json'
            }

            print(f"繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢API蜻ｼ縺ｳ蜃ｺ縺・ lat={lat}, lon={lon}, radius={radius}km")

            # API繝ｪ繧ｯ繧ｨ繧ｹ繝医ｒ螳溯｡・
            response = requests.get(self.api_base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            # 繝ｬ繧ｹ繝昴Φ繧ｹ繧定ｧ｣譫・
            data = response.json()

            # 繧ｨ繝ｩ繝ｼ繝ｬ繧ｹ繝昴Φ繧ｹ繧偵メ繧ｧ繝・け
            if 'results' not in data:
                raise ValueError("API繝ｬ繧ｹ繝昴Φ繧ｹ縺ｫ邨先棡縺悟性縺ｾ繧後※縺・∪縺帙ｓ")

            # 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ繧呈紛蠖｢
            restaurants = self._format_restaurant_data(data['results'].get('shop', []))

            # 繧ｭ繝｣繝・す繝･縺ｫ菫晏ｭ假ｼ・0蛻・俣・・
            self.cache_service.set_cached_data(cache_key, restaurants, ttl=600)

            print(f"繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢謌仙粥: {len(restaurants)}莉ｶ蜿門ｾ・)
            return restaurants

        except requests.exceptions.HTTPError as e:
            # HTTP繧ｨ繝ｩ繝ｼ・医Ξ繝ｼ繝亥宛髯舌∬ｪ崎ｨｼ繧ｨ繝ｩ繝ｼ縺ｪ縺ｩ・・
            if e.response.status_code == 429:
                print(f"繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢API 繝ｬ繝ｼ繝亥宛髯舌お繝ｩ繝ｼ: {e}")
                # 繝ｬ繝ｼ繝亥宛髯先凾縺ｯ蜿､縺・く繝｣繝・す繝･繝・・繧ｿ繧剃ｽｿ逕ｨ繧定ｩｦ陦・
                fallback_data = self._get_fallback_cache_data(cache_key)
                if fallback_data:
                    return fallback_data
            elif e.response.status_code == 401:
                print(f"繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢API 隱崎ｨｼ繧ｨ繝ｩ繝ｼ: {e}")
            else:
                print(f"繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢API HTTP繧ｨ繝ｩ繝ｼ: {e}")
            return []

        except requests.exceptions.RequestException as e:
            print(f"繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢API 繝ｪ繧ｯ繧ｨ繧ｹ繝医お繝ｩ繝ｼ: {e}")
            # 繝阪ャ繝医Ρ繝ｼ繧ｯ繧ｨ繝ｩ繝ｼ譎ゅ・蜿､縺・く繝｣繝・す繝･繝・・繧ｿ繧剃ｽｿ逕ｨ繧定ｩｦ陦・
            fallback_data = self._get_fallback_cache_data(cache_key)
            if fallback_data:
                return fallback_data
            return []

        except (ValueError, KeyError) as e:
            print(f"繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢繝・・繧ｿ隗｣譫舌お繝ｩ繝ｼ: {e}")
            return []

        except Exception as e:
            print(f"繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢縺ｧ莠域悄縺励↑縺・お繝ｩ繝ｼ: {e}")
            return []

    def filter_by_budget(self, restaurants: List[Dict], max_budget: int = None) -> List[Dict]:
        """
        莠育ｮ励〒繝ｬ繧ｹ繝医Λ繝ｳ繧偵ヵ繧｣繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ

        Args:
            restaurants (list): 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ縺ｮ繝ｪ繧ｹ繝・
            max_budget (int, optional): 譛螟ｧ莠育ｮ暦ｼ亥・・峨√ョ繝輔か繝ｫ繝医・LUNCH_BUDGET_LIMIT

        Returns:
            list: 繝輔ぅ繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ縺輔ｌ縺溘Ξ繧ｹ繝医Λ繝ｳ諠・ｱ縺ｮ繝ｪ繧ｹ繝・
        """
        if max_budget is None:
            max_budget = self.LUNCH_BUDGET_LIMIT

        filtered_restaurants = []

        for restaurant in restaurants:
            # 莠育ｮ玲ュ蝣ｱ縺悟ｭ伜惠縺励↑縺・ｴ蜷医・繧ｹ繧ｭ繝・・
            if 'budget_average' not in restaurant:
                continue

            # 莠育ｮ励′蛻ｶ髯蝉ｻ･荳九・蝣ｴ蜷医・縺ｿ霑ｽ蜉
            if restaurant['budget_average'] <= max_budget:
                filtered_restaurants.append(restaurant)

        print(f"莠育ｮ励ヵ繧｣繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ: {len(restaurants)}莉ｶ 竊・{len(filtered_restaurants)}莉ｶ (竕､ﾂ･{max_budget})")
        return filtered_restaurants

    def search_lunch_restaurants(self, lat: float, lon: float, radius: int = 1) -> List[Dict]:
        """
        繝ｩ繝ｳ繝√↓驕ｩ縺励◆繝ｬ繧ｹ繝医Λ繝ｳ繧呈､懃ｴ｢・井ｺ育ｮ励ヵ繧｣繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ霎ｼ縺ｿ・・

        Args:
            lat (float): 邱ｯ蠎ｦ
            lon (float): 邨悟ｺｦ
            radius (int): 讀懃ｴ｢蜊雁ｾ・ｼ・m・・

        Returns:
            list: 繝ｩ繝ｳ繝√↓驕ｩ縺励◆繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ縺ｮ繝ｪ繧ｹ繝・
        """
        # 蜈ｨ繝ｬ繧ｹ繝医Λ繝ｳ繧呈､懃ｴ｢
        all_restaurants = self.search_restaurants(lat, lon, radius)

        # 莠育ｮ励〒繝輔ぅ繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ
        lunch_restaurants = self.filter_by_budget(all_restaurants, self.LUNCH_BUDGET_LIMIT)

        return lunch_restaurants

    def _convert_radius_to_range_code(self, radius_km: int) -> int:
        """
        蜊雁ｾ・ｼ・m・峨ｒHot Pepper API縺ｮ遽・峇繧ｳ繝ｼ繝峨↓螟画鋤

        Args:
            radius_km (int): 蜊雁ｾ・ｼ・m・・

        Returns:
            int: Hot Pepper API縺ｮ遽・峇繧ｳ繝ｼ繝・
        """
        # Hot Pepper API縺ｮ遽・峇繧ｳ繝ｼ繝・
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
        API繝ｬ繧ｹ繝昴Φ繧ｹ繧呈ｨ呎ｺ門ｽ｢蠑上↓謨ｴ蠖｢

        Args:
            api_restaurants (list): Hot Pepper API縺九ｉ縺ｮ繝ｬ繧ｹ繝医Λ繝ｳ繝・・繧ｿ

        Returns:
            list: 謨ｴ蠖｢縺輔ｌ縺溘Ξ繧ｹ繝医Λ繝ｳ諠・ｱ縺ｮ繝ｪ繧ｹ繝・
        """
        formatted_restaurants = []

        for restaurant in api_restaurants:
            try:
                # 莠育ｮ玲ュ蝣ｱ繧定ｧ｣譫・
                budget_average = self._parse_budget_info(restaurant.get('budget', {}))

                formatted_restaurant = {
                    'id': restaurant.get('id', ''),
                    'name': restaurant.get('name', '荳肴・縺ｪ繝ｬ繧ｹ繝医Λ繝ｳ'),
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
                print(f"繝ｬ繧ｹ繝医Λ繝ｳ繝・・繧ｿ謨ｴ蠖｢繧ｨ繝ｩ繝ｼ (ID: {restaurant.get('id', 'unknown')}): {e}")
                continue

        return formatted_restaurants

    def _parse_budget_info(self, budget_data: Dict) -> int:
        """
        莠育ｮ玲ュ蝣ｱ繧定ｧ｣譫舌＠縺ｦ蟷ｳ蝮・ｺ育ｮ励ｒ邂怜・

        Args:
            budget_data (dict): Hot Pepper API縺ｮ莠育ｮ励ョ繝ｼ繧ｿ

        Returns:
            int: 蟷ｳ蝮・ｺ育ｮ暦ｼ亥・・・
        """
        try:
            budget_code = budget_data.get('code', '')

            # 莠育ｮ励さ繝ｼ繝峨°繧蛾≡鬘阪ｒ蜿門ｾ・
            if budget_code in self.BUDGET_CODES:
                return self.BUDGET_CODES[budget_code]

            # 莠育ｮ怜錐縺九ｉ謗ｨ螳夲ｼ医ヵ繧ｩ繝ｼ繝ｫ繝舌ャ繧ｯ・・
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
                # 繝・ヵ繧ｩ繝ｫ繝亥､・医Λ繝ｳ繝∽ｺ育ｮ怜宛髯舌ｒ雜・∴繧句､・・
                return 2000

        except Exception:
            return 2000  # 繝・ヵ繧ｩ繝ｫ繝亥､

    def _get_restaurant_photo(self, photo_data: Dict) -> str:
        """
        繝ｬ繧ｹ繝医Λ繝ｳ縺ｮ蜀咏悄URL繧貞叙蠕・

        Args:
            photo_data (dict): Hot Pepper API縺ｮ蜀咏悄繝・・繧ｿ

        Returns:
            str: 蜀咏悄URL・亥ｭ伜惠縺励↑縺・ｴ蜷医・遨ｺ譁・ｭ怜・・・
        """
        try:
            # PC繧ｵ繧､繧ｺ縺ｮ蜀咏悄繧貞━蜈・
            if 'pc' in photo_data:
                pc_photos = photo_data['pc']
                if 'l' in pc_photos:  # 螟ｧ繧ｵ繧､繧ｺ
                    return pc_photos['l']
                elif 'm' in pc_photos:  # 荳ｭ繧ｵ繧､繧ｺ
                    return pc_photos['m']
                elif 's' in pc_photos:  # 蟆上し繧､繧ｺ
                    return pc_photos['s']

            # 繝｢繝舌う繝ｫ繧ｵ繧､繧ｺ縺ｮ蜀咏悄繧偵ヵ繧ｩ繝ｼ繝ｫ繝舌ャ繧ｯ
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
        繝ｬ繧ｹ繝医Λ繝ｳID縺九ｉ隧ｳ邏ｰ諠・ｱ繧貞叙蠕・

        Args:
            restaurant_id (str): 繝ｬ繧ｹ繝医Λ繝ｳID

        Returns:
            dict: 繝ｬ繧ｹ繝医Λ繝ｳ隧ｳ邏ｰ諠・ｱ縲∬ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷医・None
        """
        # API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺・↑縺・ｴ蜷医・None繧定ｿ斐☆
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
            print(f"繝ｬ繧ｹ繝医Λ繝ｳ隧ｳ邏ｰ蜿門ｾ励お繝ｩ繝ｼ (ID: {restaurant_id}): {e}")
            return None

    def _get_fallback_cache_data(self, cache_key: str) -> List[Dict]:
        """
        譛滄剞蛻・ｌ縺ｧ繧ょ茜逕ｨ蜿ｯ閭ｽ縺ｪ繧ｭ繝｣繝・す繝･繝・・繧ｿ繧貞叙蠕暦ｼ医ヵ繧ｩ繝ｼ繝ｫ繝舌ャ繧ｯ逕ｨ・・

        Args:
            cache_key (str): 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ

        Returns:
            list: 繧ｭ繝｣繝・す繝･縺輔ｌ縺溘Ξ繧ｹ繝医Λ繝ｳ諠・ｱ縲∝ｭ伜惠縺励↑縺・ｴ蜷医・遨ｺ繝ｪ繧ｹ繝・
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

                # 譛滄剞蛻・ｌ縺ｧ繧ゅョ繝ｼ繧ｿ繧定ｿ斐☆・医ヵ繧ｩ繝ｼ繝ｫ繝舌ャ繧ｯ逕ｨ・・
                fallback_data = self.cache_service.deserialize_data(row['data'])

                # 繧ｽ繝ｼ繧ｹ諠・ｱ繧呈峩譁ｰ
                for restaurant in fallback_data:
                    restaurant['source'] = 'fallback_cache'

                print(f"繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ逕ｨ繧ｭ繝｣繝・す繝･繝・・繧ｿ繧剃ｽｿ逕ｨ・域悄髯仙・繧鯉ｼ・ {len(fallback_data)}莉ｶ")
                return fallback_data

        except Exception as e:
            print(f"繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繧ｭ繝｣繝・す繝･蜿門ｾ励お繝ｩ繝ｼ: {e}")
            return []

    def validate_restaurant_data(self, restaurant_data: Dict) -> bool:
        """
        繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ繝・・繧ｿ縺ｮ螯･蠖捺ｧ繧呈､懆ｨｼ

        Args:
            restaurant_data (dict): 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ

        Returns:
            bool: 螯･蠖薙↑蝣ｴ蜷・rue
        """
        try:
            # 蠢・医ヵ繧｣繝ｼ繝ｫ繝峨・蟄伜惠遒ｺ隱・
            required_fields = ['id', 'name', 'lat', 'lng']
            for field in required_fields:
                if field not in restaurant_data or not restaurant_data[field]:
                    return False

            # 蠎ｧ讓吶・遽・峇遒ｺ隱・
            lat = float(restaurant_data['lat'])
            lng = float(restaurant_data['lng'])

            if not (-90 <= lat <= 90):
                return False
            if not (-180 <= lng <= 180):
                return False

            return True

        except (ValueError, TypeError):
            return False


# 菴ｿ逕ｨ萓九→繝・せ繝育畑繧ｳ繝ｼ繝・
if __name__ == '__main__':
    """
    RestaurantService縺ｮ繝・せ繝亥ｮ溯｡・
    """
    print("RestaurantService 繝・せ繝亥ｮ溯｡・)
    print("=" * 40)

    # RestaurantService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ菴懈・
    restaurant_service = RestaurantService()

    # 譚ｱ莠ｬ鬧・・蠎ｧ讓・
    tokyo_lat, tokyo_lon = 35.6812, 139.7671

    # 繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢繝・せ繝・
    print("1. 繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢:")
    restaurants = restaurant_service.search_restaurants(tokyo_lat, tokyo_lon, radius=1)
    print(f"   讀懃ｴ｢邨先棡: {len(restaurants)}莉ｶ")

    if restaurants:
        # 譛蛻昴・繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ繧定｡ｨ遉ｺ
        first_restaurant = restaurants[0]
        print(f"   萓・ {first_restaurant['name']}")
        print(f"       繧ｸ繝｣繝ｳ繝ｫ: {first_restaurant['genre']}")
        print(f"       莠育ｮ・ ﾂ･{first_restaurant['budget_average']}")
        print(f"       菴乗園: {first_restaurant['address']}")

    # 莠育ｮ励ヵ繧｣繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ繝・せ繝・
    print("\n2. 莠育ｮ励ヵ繧｣繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ:")
    lunch_restaurants = restaurant_service.filter_by_budget(restaurants, 1200)
    print(f"   繝輔ぅ繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ蠕・ {len(lunch_restaurants)}莉ｶ")

    # 繝ｩ繝ｳ繝√Ξ繧ｹ繝医Λ繝ｳ讀懃ｴ｢繝・せ繝・
    print("\n3. 繝ｩ繝ｳ繝√Ξ繧ｹ繝医Λ繝ｳ讀懃ｴ｢:")
    lunch_only = restaurant_service.search_lunch_restaurants(tokyo_lat, tokyo_lon)
    print(f"   繝ｩ繝ｳ繝・←蜷・ {len(lunch_only)}莉ｶ")

    # 繝・・繧ｿ螯･蠖捺ｧ讀懆ｨｼ繝・せ繝・
    if restaurants:
        print(f"\n4. 繝・・繧ｿ螯･蠖捺ｧ讀懆ｨｼ: {restaurant_service.validate_restaurant_data(restaurants[0])}")

    print("\n繝・せ繝亥ｮ御ｺ・)
