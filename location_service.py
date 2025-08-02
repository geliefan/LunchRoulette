#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LocationService - 菴咲ｽｮ諠・ｱ繧ｵ繝ｼ繝薙せ繧ｯ繝ｩ繧ｹ
IP繧｢繝峨Ξ繧ｹ縺九ｉ菴咲ｽｮ諠・ｱ繧貞叙蠕励☆繧区ｩ溯・繧呈署萓・

縺薙・繧ｯ繝ｩ繧ｹ縺ｯ莉･荳九・讖溯・繧呈署萓帙＠縺ｾ縺・
- IP繧｢繝峨Ξ繧ｹ縺九ｉ菴咲ｽｮ諠・ｱ縺ｮ蜿門ｾ・
- 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｨ繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ・域擲莠ｬ鬧・ｼ芽ｨｭ螳・
- 繧ｭ繝｣繝・す繝･讖溯・縺ｨ縺ｮ邨ｱ蜷・
"""

import requests
from typing import Dict, Optional, Tuple
from cache_service import CacheService


class LocationService:
    """
    IP繧｢繝峨Ξ繧ｹ縺九ｉ菴咲ｽｮ諠・ｱ繧貞叙蠕励☆繧九し繝ｼ繝薙せ

    ipapi.co API繧剃ｽｿ逕ｨ縺励※IP繧｢繝峨Ξ繧ｹ縺九ｉ菴咲ｽｮ諠・ｱ繧貞叙蠕励＠縲・
    繧ｨ繝ｩ繝ｼ譎ゅ↓縺ｯ譚ｱ莠ｬ鬧・ｒ繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ縺ｨ縺励※菴ｿ逕ｨ縺吶ｋ縲・
    """

    # 繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ・域擲莠ｬ鬧・ｼ・
    DEFAULT_LOCATION = {
        'latitude': 35.6812,
        'longitude': 139.7671,
        'city': '譚ｱ莠ｬ',
        'region': '譚ｱ莠ｬ驛ｽ',
        'country': '譌･譛ｬ',
        'country_code': 'JP'
    }

    def __init__(self, cache_service: Optional[CacheService] = None):
        """
        LocationService繧貞・譛溷喧

        Args:
            cache_service (CacheService, optional): 繧ｭ繝｣繝・す繝･繧ｵ繝ｼ繝薙せ
        """
        self.cache_service = cache_service or CacheService()
        self.api_base_url = "https://ipapi.co"
        self.timeout = 10  # API繝ｪ繧ｯ繧ｨ繧ｹ繝医・繧ｿ繧､繝繧｢繧ｦ繝茨ｼ育ｧ抵ｼ・

    def get_location_from_ip(self, ip_address: Optional[str] = None) -> Dict[str, any]:
        """
        IP繧｢繝峨Ξ繧ｹ縺九ｉ菴咲ｽｮ諠・ｱ繧貞叙蠕・

        Args:
            ip_address (str, optional): IP繧｢繝峨Ξ繧ｹ縲・one縺ｮ蝣ｴ蜷医・閾ｪ蜍墓､懷・

        Returns:
            dict: 菴咲ｽｮ諠・ｱ・育ｷｯ蠎ｦ縲∫ｵ悟ｺｦ縲・・蟶ょ錐縺ｪ縺ｩ・・

        Example:
            >>> location_service = LocationService()
            >>> location = location_service.get_location_from_ip()
            >>> print(f"Location: {location['city']}, {location['region']}")
        """
        # 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ繧堤函謌・
        cache_key = self.cache_service.generate_cache_key(
            'location',
            ip=ip_address or 'auto'
        )

        # 繧ｭ繝｣繝・す繝･縺九ｉ蜿門ｾ励ｒ隧ｦ陦・
        cached_data = self.cache_service.get_cached_data(cache_key)
        if cached_data:
            print(f"菴咲ｽｮ諠・ｱ繧偵く繝｣繝・す繝･縺九ｉ蜿門ｾ・ {cached_data['city']}")
            return cached_data

        try:
            # API URL繧呈ｧ狗ｯ・
            if ip_address:
                url = f"{self.api_base_url}/{ip_address}/json/"
            else:
                url = f"{self.api_base_url}/json/"

            print(f"菴咲ｽｮ諠・ｱAPI蜻ｼ縺ｳ蜃ｺ縺・ {url}")

            # API繝ｪ繧ｯ繧ｨ繧ｹ繝医ｒ螳溯｡・
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            # 繝ｬ繧ｹ繝昴Φ繧ｹ繧定ｧ｣譫・
            data = response.json()

            # 繧ｨ繝ｩ繝ｼ繝ｬ繧ｹ繝昴Φ繧ｹ繧偵メ繧ｧ繝・け
            if 'error' in data and data['error']:
                raise ValueError(f"API 繧ｨ繝ｩ繝ｼ: {data.get('reason', 'Unknown error')}")

            # 菴咲ｽｮ諠・ｱ繧呈紛蠖｢
            location_data = self._format_location_data(data)

            # 繧ｭ繝｣繝・す繝･縺ｫ菫晏ｭ假ｼ・0蛻・俣・・
            self.cache_service.set_cached_data(cache_key, location_data, ttl=600)

            print(f"菴咲ｽｮ諠・ｱ蜿門ｾ玲・蜉・ {location_data['city']}, {location_data['region']}")
            return location_data

        except requests.exceptions.HTTPError as e:
            # HTTP繧ｨ繝ｩ繝ｼ・医Ξ繝ｼ繝亥宛髯舌∬ｪ崎ｨｼ繧ｨ繝ｩ繝ｼ縺ｪ縺ｩ・・
            if e.response.status_code == 429:
                print(f"菴咲ｽｮ諠・ｱAPI 繝ｬ繝ｼ繝亥宛髯舌お繝ｩ繝ｼ: {e}")
                # 繝ｬ繝ｼ繝亥宛髯先凾縺ｯ蜿､縺・く繝｣繝・す繝･繝・・繧ｿ繧剃ｽｿ逕ｨ繧定ｩｦ陦・
                fallback_data = self._get_fallback_cache_data(cache_key)
                if fallback_data:
                    return fallback_data
            else:
                print(f"菴咲ｽｮ諠・ｱAPI HTTP繧ｨ繝ｩ繝ｼ: {e}")
            return self._get_default_location()

        except requests.exceptions.RequestException as e:
            print(f"菴咲ｽｮ諠・ｱAPI 繝ｪ繧ｯ繧ｨ繧ｹ繝医お繝ｩ繝ｼ: {e}")
            # 繝阪ャ繝医Ρ繝ｼ繧ｯ繧ｨ繝ｩ繝ｼ譎ゅ・蜿､縺・く繝｣繝・す繝･繝・・繧ｿ繧剃ｽｿ逕ｨ繧定ｩｦ陦・
            fallback_data = self._get_fallback_cache_data(cache_key)
            if fallback_data:
                return fallback_data
            return self._get_default_location()

        except (ValueError, KeyError) as e:
            print(f"菴咲ｽｮ諠・ｱ繝・・繧ｿ隗｣譫舌お繝ｩ繝ｼ: {e}")
            return self._get_default_location()

        except Exception as e:
            print(f"菴咲ｽｮ諠・ｱ蜿門ｾ励〒莠域悄縺励↑縺・お繝ｩ繝ｼ: {e}")
            return self._get_default_location()

    def _format_location_data(self, api_data: Dict) -> Dict[str, any]:
        """
        API繝ｬ繧ｹ繝昴Φ繧ｹ繧呈ｨ呎ｺ門ｽ｢蠑上↓謨ｴ蠖｢

        Args:
            api_data (dict): ipapi.co API縺九ｉ縺ｮ繝ｬ繧ｹ繝昴Φ繧ｹ

        Returns:
            dict: 謨ｴ蠖｢縺輔ｌ縺滉ｽ咲ｽｮ諠・ｱ

        Raises:
            KeyError: 蠢・ｦ√↑繝輔ぅ繝ｼ繝ｫ繝峨′荳崎ｶｳ縺励※縺・ｋ蝣ｴ蜷・
        """
        try:
            return {
                'latitude': float(api_data['latitude']),
                'longitude': float(api_data['longitude']),
                'city': api_data.get('city', '荳肴・'),
                'region': api_data.get('region', '荳肴・'),
                'country': api_data.get('country_name', '荳肴・'),
                'country_code': api_data.get('country_code', 'XX'),
                'postal': api_data.get('postal', ''),
                'timezone': api_data.get('timezone', 'Asia/Tokyo'),
                'source': 'ipapi.co'
            }
        except (KeyError, ValueError, TypeError) as e:
            raise KeyError(f"菴咲ｽｮ諠・ｱ繝・・繧ｿ縺ｮ蠢・医ヵ繧｣繝ｼ繝ｫ繝峨′荳崎ｶｳ: {e}")

    def _get_fallback_cache_data(self, cache_key: str) -> Optional[Dict[str, any]]:
        """
        譛滄剞蛻・ｌ縺ｧ繧ょ茜逕ｨ蜿ｯ閭ｽ縺ｪ繧ｭ繝｣繝・す繝･繝・・繧ｿ繧貞叙蠕暦ｼ医ヵ繧ｩ繝ｼ繝ｫ繝舌ャ繧ｯ逕ｨ・・

        Args:
            cache_key (str): 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ

        Returns:
            dict: 繧ｭ繝｣繝・す繝･縺輔ｌ縺滉ｽ咲ｽｮ諠・ｱ縲∝ｭ伜惠縺励↑縺・ｴ蜷医・None
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
                    return None

                # 譛滄剞蛻・ｌ縺ｧ繧ゅョ繝ｼ繧ｿ繧定ｿ斐☆・医ヵ繧ｩ繝ｼ繝ｫ繝舌ャ繧ｯ逕ｨ・・
                fallback_data = self.cache_service.deserialize_data(row['data'])
                fallback_data['source'] = 'fallback_cache'

                print("繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ逕ｨ繧ｭ繝｣繝・す繝･繝・・繧ｿ繧剃ｽｿ逕ｨ・域悄髯仙・繧鯉ｼ・)
                return fallback_data

        except Exception as e:
            print(f"繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繧ｭ繝｣繝・す繝･蜿門ｾ励お繝ｩ繝ｼ: {e}")
            return None

    def _get_default_location(self) -> Dict[str, any]:
        """
        繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ・域擲莠ｬ鬧・ｼ峨ｒ霑斐☆

        Returns:
            dict: 繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ諠・ｱ
        """
        default_location = self.DEFAULT_LOCATION.copy()
        default_location['source'] = 'default'

        print("繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ・域擲莠ｬ鬧・ｼ峨ｒ菴ｿ逕ｨ")
        return default_location

    def get_coordinates(self, ip_address: Optional[str] = None) -> Tuple[float, float]:
        """
        IP繧｢繝峨Ξ繧ｹ縺九ｉ邱ｯ蠎ｦ繝ｻ邨悟ｺｦ縺ｮ繧ｿ繝励Ν繧貞叙蠕・

        Args:
            ip_address (str, optional): IP繧｢繝峨Ξ繧ｹ

        Returns:
            tuple: (邱ｯ蠎ｦ, 邨悟ｺｦ)

        Example:
            >>> location_service = LocationService()
            >>> lat, lon = location_service.get_coordinates()
            >>> print(f"Coordinates: {lat}, {lon}")
        """
        location = self.get_location_from_ip(ip_address)
        return location['latitude'], location['longitude']

    def is_default_location(self, location_data: Dict) -> bool:
        """
        菴咲ｽｮ諠・ｱ縺後ョ繝輔か繝ｫ繝井ｽ咲ｽｮ縺九←縺・°繧貞愛螳・

        Args:
            location_data (dict): 菴咲ｽｮ諠・ｱ

        Returns:
            bool: 繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ縺ｮ蝣ｴ蜷・rue
        """
        return location_data.get('source') == 'default'

    def validate_location_data(self, location_data: Dict) -> bool:
        """
        菴咲ｽｮ諠・ｱ繝・・繧ｿ縺ｮ螯･蠖捺ｧ繧呈､懆ｨｼ

        Args:
            location_data (dict): 菴咲ｽｮ諠・ｱ

        Returns:
            bool: 螯･蠖薙↑蝣ｴ蜷・rue
        """
        try:
            # 蠢・医ヵ繧｣繝ｼ繝ｫ繝峨・蟄伜惠遒ｺ隱・
            required_fields = ['latitude', 'longitude', 'city', 'region', 'country']
            for field in required_fields:
                if field not in location_data:
                    return False

            # 邱ｯ蠎ｦ繝ｻ邨悟ｺｦ縺ｮ遽・峇遒ｺ隱・
            lat = float(location_data['latitude'])
            lon = float(location_data['longitude'])

            if not (-90 <= lat <= 90):
                return False
            if not (-180 <= lon <= 180):
                return False

            return True

        except (ValueError, TypeError):
            return False


# 菴ｿ逕ｨ萓九→繝・せ繝育畑繧ｳ繝ｼ繝・
if __name__ == '__main__':
    """
    LocationService縺ｮ繝・せ繝亥ｮ溯｡・
    """
    print("LocationService 繝・せ繝亥ｮ溯｡・)
    print("=" * 40)

    # LocationService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ菴懈・
    location_service = LocationService()

    # 菴咲ｽｮ諠・ｱ蜿門ｾ励ユ繧ｹ繝・
    print("1. 閾ｪ蜍肘P讀懷・縺ｫ繧医ｋ菴咲ｽｮ諠・ｱ蜿門ｾ・")
    location = location_service.get_location_from_ip()
    print(f"   菴咲ｽｮ: {location['city']}, {location['region']}")
    print(f"   蠎ｧ讓・ {location['latitude']}, {location['longitude']}")
    print(f"   繧ｽ繝ｼ繧ｹ: {location['source']}")

    # 蠎ｧ讓吝叙蠕励ユ繧ｹ繝・
    print("\n2. 蠎ｧ讓吶・縺ｿ蜿門ｾ・")
    lat, lon = location_service.get_coordinates()
    print(f"   邱ｯ蠎ｦ: {lat}, 邨悟ｺｦ: {lon}")

    # 繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ蛻､螳壹ユ繧ｹ繝・
    print(f"\n3. 繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ蛻､螳・ {location_service.is_default_location(location)}")

    # 繝・・繧ｿ螯･蠖捺ｧ讀懆ｨｼ繝・せ繝・
    print(f"4. 繝・・繧ｿ螯･蠖捺ｧ讀懆ｨｼ: {location_service.validate_location_data(location)}")

    # 辟｡蜉ｹ縺ｪIP繧｢繝峨Ξ繧ｹ繝・せ繝・
    print("\n5. 辟｡蜉ｹ縺ｪIP繧｢繝峨Ξ繧ｹ繝・せ繝・")
    invalid_location = location_service.get_location_from_ip("invalid.ip")
    print(f"   菴咲ｽｮ: {invalid_location['city']}, {invalid_location['region']}")
    print(f"   繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ: {location_service.is_default_location(invalid_location)}")

    print("\n繝・せ繝亥ｮ御ｺ・)
