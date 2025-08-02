#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeatherService - 螟ｩ豌玲ュ蝣ｱ繧ｵ繝ｼ繝薙せ繧ｯ繝ｩ繧ｹ
OpenWeatherMap API縺九ｉ螟ｩ豌玲ュ蝣ｱ繧貞叙蠕励☆繧区ｩ溯・繧呈署萓・

縺薙・繧ｯ繝ｩ繧ｹ縺ｯ莉･荳九・讖溯・繧呈署萓帙＠縺ｾ縺・
- OpenWeatherMap One Call 3.0 API邨ｱ蜷・
- 螟ｩ豌励ョ繝ｼ繧ｿ縺ｮ蜿門ｾ励→謨ｴ蠖｢讖溯・
- 繧ｭ繝｣繝・す繝･讖溯・縺ｨ縺ｮ邨ｱ蜷・
- 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｨ繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ讖溯・
"""

import requests
import os
from typing import Dict, Optional
from datetime import datetime
from cache_service import CacheService


class WeatherService:
    """
    OpenWeatherMap API縺九ｉ螟ｩ豌玲ュ蝣ｱ繧貞叙蠕励☆繧九し繝ｼ繝薙せ

    One Call 3.0 API繧剃ｽｿ逕ｨ縺励※迴ｾ蝨ｨ縺ｮ螟ｩ豌励∵ｰ玲ｸｩ縲ゞV謖・焚縺ｪ縺ｩ繧貞叙蠕励＠縲・
    繧ｨ繝ｩ繝ｼ譎ゅ↓縺ｯ繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌玲ュ蝣ｱ繧呈署萓帙☆繧九・
    """

    # 繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌玲ュ蝣ｱ
    DEFAULT_WEATHER = {
        'temperature': 20.0,
        'condition': 'clear',
        'description': '譎ｴ繧・,
        'uv_index': 3.0,
        'humidity': 60,
        'pressure': 1013,
        'visibility': 10000,
        'wind_speed': 2.0,
        'wind_direction': 180,
        'icon': '01d'
    }

    # 螟ｩ豌礼憾豕√・譌･譛ｬ隱槭・繝・ヴ繝ｳ繧ｰ
    CONDITION_MAPPING = {
        'clear': '譎ｴ繧・,
        'clouds': '譖・ｊ',
        'rain': '髮ｨ',
        'drizzle': '蟆城岑',
        'thunderstorm': '髮ｷ髮ｨ',
        'snow': '髮ｪ',
        'mist': '髴ｧ',
        'fog': '髴ｧ',
        'haze': '繧ゅｄ',
        'dust': '遐ょ｡ｵ',
        'sand': '遐ょｵ・,
        'ash': '轣ｫ螻ｱ轣ｰ',
        'squall': '遯・｢ｨ',
        'tornado': '遶懷ｷｻ'
    }

    def __init__(self, api_key: Optional[str] = None, cache_service: Optional[CacheService] = None):
        """
        WeatherService繧貞・譛溷喧

        Args:
            api_key (str, optional): OpenWeatherMap API繧ｭ繝ｼ
            cache_service (CacheService, optional): 繧ｭ繝｣繝・す繝･繧ｵ繝ｼ繝薙せ
        """
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.cache_service = cache_service or CacheService()
        self.api_base_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.timeout = 10  # API繝ｪ繧ｯ繧ｨ繧ｹ繝医・繧ｿ繧､繝繧｢繧ｦ繝茨ｼ育ｧ抵ｼ・

        if not self.api_key:
            print("隴ｦ蜻・ OpenWeatherMap API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺・∪縺帙ｓ縲ゅョ繝輔か繝ｫ繝亥､ｩ豌玲ュ蝣ｱ繧剃ｽｿ逕ｨ縺励∪縺吶・)

    def get_current_weather(self, lat: float, lon: float) -> Dict[str, any]:
        """
        謖・ｮ壹＆繧後◆蠎ｧ讓吶・迴ｾ蝨ｨ縺ｮ螟ｩ豌玲ュ蝣ｱ繧貞叙蠕・

        Args:
            lat (float): 邱ｯ蠎ｦ
            lon (float): 邨悟ｺｦ

        Returns:
            dict: 螟ｩ豌玲ュ蝣ｱ・域ｰ玲ｸｩ縲∝､ｩ豌礼憾豕√ゞV謖・焚縺ｪ縺ｩ・・

        Example:
            >>> weather_service = WeatherService()
            >>> weather = weather_service.get_current_weather(35.6812, 139.7671)
            >>> print(f"Temperature: {weather['temperature']}ﾂｰC")
        """
        # 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ繧堤函謌・
        cache_key = self.cache_service.generate_cache_key(
            'weather',
            lat=round(lat, 4),  # 邊ｾ蠎ｦ繧貞宛髯舌＠縺ｦ繧ｭ繝｣繝・す繝･蜉ｹ邇・ｒ蜷台ｸ・
            lon=round(lon, 4)
        )

        # 繧ｭ繝｣繝・す繝･縺九ｉ蜿門ｾ励ｒ隧ｦ陦・
        cached_data = self.cache_service.get_cached_data(cache_key)
        if cached_data:
            print(f"螟ｩ豌玲ュ蝣ｱ繧偵く繝｣繝・す繝･縺九ｉ蜿門ｾ・ {cached_data['description']}")
            return cached_data

        # API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺・↑縺・ｴ蜷医・繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌玲ュ蝣ｱ繧定ｿ斐☆
        if not self.api_key:
            return self._get_default_weather()

        try:
            # API繝代Λ繝｡繝ｼ繧ｿ繧呈ｧ狗ｯ・
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',  # 鞫よｰ乗ｸｩ蠎ｦ
                'lang': 'ja',       # 譌･譛ｬ隱・
                'exclude': 'minutely,hourly,daily,alerts'  # 迴ｾ蝨ｨ縺ｮ螟ｩ豌励・縺ｿ
            }

            print(f"螟ｩ豌玲ュ蝣ｱAPI蜻ｼ縺ｳ蜃ｺ縺・ lat={lat}, lon={lon}")

            # API繝ｪ繧ｯ繧ｨ繧ｹ繝医ｒ螳溯｡・
            response = requests.get(self.api_base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            # 繝ｬ繧ｹ繝昴Φ繧ｹ繧定ｧ｣譫・
            data = response.json()

            # 螟ｩ豌玲ュ蝣ｱ繧呈紛蠖｢
            weather_data = self._format_weather_data(data)

            # 繧ｭ繝｣繝・す繝･縺ｫ菫晏ｭ假ｼ・0蛻・俣・・
            self.cache_service.set_cached_data(cache_key, weather_data, ttl=600)

            print(f"螟ｩ豌玲ュ蝣ｱ蜿門ｾ玲・蜉・ {weather_data['description']}, {weather_data['temperature']}ﾂｰC")
            return weather_data

        except requests.exceptions.HTTPError as e:
            # HTTP繧ｨ繝ｩ繝ｼ・医Ξ繝ｼ繝亥宛髯舌∬ｪ崎ｨｼ繧ｨ繝ｩ繝ｼ縺ｪ縺ｩ・・
            if e.response.status_code == 429:
                print(f"螟ｩ豌玲ュ蝣ｱAPI 繝ｬ繝ｼ繝亥宛髯舌お繝ｩ繝ｼ: {e}")
                # 繝ｬ繝ｼ繝亥宛髯先凾縺ｯ蜿､縺・く繝｣繝・す繝･繝・・繧ｿ繧剃ｽｿ逕ｨ繧定ｩｦ陦・
                fallback_data = self._get_fallback_cache_data(cache_key)
                if fallback_data:
                    return fallback_data
            elif e.response.status_code == 401:
                print(f"螟ｩ豌玲ュ蝣ｱAPI 隱崎ｨｼ繧ｨ繝ｩ繝ｼ: {e}")
            else:
                print(f"螟ｩ豌玲ュ蝣ｱAPI HTTP繧ｨ繝ｩ繝ｼ: {e}")
            return self._get_default_weather()

        except requests.exceptions.RequestException as e:
            print(f"螟ｩ豌玲ュ蝣ｱAPI 繝ｪ繧ｯ繧ｨ繧ｹ繝医お繝ｩ繝ｼ: {e}")
            # 繝阪ャ繝医Ρ繝ｼ繧ｯ繧ｨ繝ｩ繝ｼ譎ゅ・蜿､縺・く繝｣繝・す繝･繝・・繧ｿ繧剃ｽｿ逕ｨ繧定ｩｦ陦・
            fallback_data = self._get_fallback_cache_data(cache_key)
            if fallback_data:
                return fallback_data
            return self._get_default_weather()

        except (ValueError, KeyError) as e:
            print(f"螟ｩ豌玲ュ蝣ｱ繝・・繧ｿ隗｣譫舌お繝ｩ繝ｼ: {e}")
            return self._get_default_weather()

        except Exception as e:
            print(f"螟ｩ豌玲ュ蝣ｱ蜿門ｾ励〒莠域悄縺励↑縺・お繝ｩ繝ｼ: {e}")
            return self._get_default_weather()

    def _format_weather_data(self, api_data: Dict) -> Dict[str, any]:
        """
        API繝ｬ繧ｹ繝昴Φ繧ｹ繧呈ｨ呎ｺ門ｽ｢蠑上↓謨ｴ蠖｢

        Args:
            api_data (dict): OpenWeatherMap API縺九ｉ縺ｮ繝ｬ繧ｹ繝昴Φ繧ｹ

        Returns:
            dict: 謨ｴ蠖｢縺輔ｌ縺溷､ｩ豌玲ュ蝣ｱ

        Raises:
            KeyError: 蠢・ｦ√↑繝輔ぅ繝ｼ繝ｫ繝峨′荳崎ｶｳ縺励※縺・ｋ蝣ｴ蜷・
        """
        try:
            current = api_data['current']
            weather = current['weather'][0]

            # 蝓ｺ譛ｬ逧・↑螟ｩ豌玲ュ蝣ｱ
            condition = weather['main'].lower()
            description = weather.get('description', self.CONDITION_MAPPING.get(condition, '荳肴・'))

            return {
                'temperature': round(current['temp'], 1),
                'feels_like': round(current['feels_like'], 1),
                'condition': condition,
                'description': description,
                'uv_index': round(current.get('uvi', 0), 1),
                'humidity': current.get('humidity', 0),
                'pressure': current.get('pressure', 1013),
                'visibility': current.get('visibility', 10000),
                'wind_speed': round(current.get('wind_speed', 0), 1),
                'wind_direction': current.get('wind_deg', 0),
                'clouds': current.get('clouds', 0),
                'icon': weather.get('icon', '01d'),
                'sunrise': datetime.fromtimestamp(current.get('sunrise', 0)).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(current.get('sunset', 0)).strftime('%H:%M'),
                'timestamp': datetime.fromtimestamp(current['dt']).isoformat(),
                'source': 'openweathermap'
            }

        except (KeyError, ValueError, TypeError, IndexError) as e:
            raise KeyError(f"螟ｩ豌玲ュ蝣ｱ繝・・繧ｿ縺ｮ蠢・医ヵ繧｣繝ｼ繝ｫ繝峨′荳崎ｶｳ: {e}")

    def _get_fallback_cache_data(self, cache_key: str) -> Optional[Dict[str, any]]:
        """
        譛滄剞蛻・ｌ縺ｧ繧ょ茜逕ｨ蜿ｯ閭ｽ縺ｪ繧ｭ繝｣繝・す繝･繝・・繧ｿ繧貞叙蠕暦ｼ医ヵ繧ｩ繝ｼ繝ｫ繝舌ャ繧ｯ逕ｨ・・

        Args:
            cache_key (str): 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ

        Returns:
            dict: 繧ｭ繝｣繝・す繝･縺輔ｌ縺溷､ｩ豌玲ュ蝣ｱ縲∝ｭ伜惠縺励↑縺・ｴ蜷医・None
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

    def _get_default_weather(self) -> Dict[str, any]:
        """
        繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌玲ュ蝣ｱ繧定ｿ斐☆

        Returns:
            dict: 繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌玲ュ蝣ｱ
        """
        default_weather = self.DEFAULT_WEATHER.copy()
        default_weather.update({
            'feels_like': default_weather['temperature'],
            'clouds': 20,
            'sunrise': '06:00',
            'sunset': '18:00',
            'timestamp': datetime.now().isoformat(),
            'source': 'default'
        })

        print("繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌玲ュ蝣ｱ繧剃ｽｿ逕ｨ")
        return default_weather

    def get_weather_summary(self, lat: float, lon: float) -> str:
        """
        螟ｩ豌玲ュ蝣ｱ縺ｮ隕∫ｴ・枚蟄怜・繧貞叙蠕・

        Args:
            lat (float): 邱ｯ蠎ｦ
            lon (float): 邨悟ｺｦ

        Returns:
            str: 螟ｩ豌苓ｦ∫ｴ・ｼ井ｾ・ "譎ｴ繧・25ﾂｰC UV謖・焚3"・・
        """
        weather = self.get_current_weather(lat, lon)
        return f"{weather['description']} {weather['temperature']}ﾂｰC UV謖・焚{weather['uv_index']}"

    def is_good_weather_for_walking(self, lat: float, lon: float) -> bool:
        """
        蠕呈ｭｩ縺ｫ驕ｩ縺励◆螟ｩ豌励°縺ｩ縺・°繧貞愛螳・

        Args:
            lat (float): 邱ｯ蠎ｦ
            lon (float): 邨悟ｺｦ

        Returns:
            bool: 蠕呈ｭｩ縺ｫ驕ｩ縺励※縺・ｋ蝣ｴ蜷・rue
        """
        weather = self.get_current_weather(lat, lon)

        # 髮ｨ繧・妛縺ｮ蝣ｴ蜷医・蠕呈ｭｩ縺ｫ荳埼←
        bad_conditions = ['rain', 'drizzle', 'thunderstorm', 'snow']
        if weather['condition'] in bad_conditions:
            return False

        # 讌ｵ遶ｯ縺ｪ豌玲ｸｩ縺ｮ蝣ｴ蜷医・蠕呈ｭｩ縺ｫ荳埼←
        temp = weather['temperature']
        if temp < 0 or temp > 35:
            return False

        # 蠑ｷ鬚ｨ縺ｮ蝣ｴ蜷医・蠕呈ｭｩ縺ｫ荳埼←
        if weather['wind_speed'] > 10:
            return False

        return True

    def get_weather_icon_url(self, icon_code: str) -> str:
        """
        螟ｩ豌励い繧､繧ｳ繝ｳ縺ｮURL繧貞叙蠕・

        Args:
            icon_code (str): 繧｢繧､繧ｳ繝ｳ繧ｳ繝ｼ繝・

        Returns:
            str: 繧｢繧､繧ｳ繝ｳURL
        """
        return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

    def is_default_weather(self, weather_data: Dict) -> bool:
        """
        螟ｩ豌玲ュ蝣ｱ縺後ョ繝輔か繝ｫ繝亥､ｩ豌励°縺ｩ縺・°繧貞愛螳・

        Args:
            weather_data (dict): 螟ｩ豌玲ュ蝣ｱ

        Returns:
            bool: 繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌励・蝣ｴ蜷・rue
        """
        return weather_data.get('source') == 'default'

    def validate_weather_data(self, weather_data: Dict) -> bool:
        """
        螟ｩ豌玲ュ蝣ｱ繝・・繧ｿ縺ｮ螯･蠖捺ｧ繧呈､懆ｨｼ

        Args:
            weather_data (dict): 螟ｩ豌玲ュ蝣ｱ

        Returns:
            bool: 螯･蠖薙↑蝣ｴ蜷・rue
        """
        try:
            # 蠢・医ヵ繧｣繝ｼ繝ｫ繝峨・蟄伜惠遒ｺ隱・
            required_fields = ['temperature', 'condition', 'description', 'uv_index']
            for field in required_fields:
                if field not in weather_data:
                    return False

            # 豌玲ｸｩ縺ｮ遽・峇遒ｺ隱搾ｼ・50ﾂｰC縲・0ﾂｰC・・
            temp = float(weather_data['temperature'])
            if not (-50 <= temp <= 60):
                return False

            # UV謖・焚縺ｮ遽・峇遒ｺ隱搾ｼ・縲・5・・
            uv = float(weather_data['uv_index'])
            if not (0 <= uv <= 15):
                return False

            return True

        except (ValueError, TypeError):
            return False


# 菴ｿ逕ｨ萓九→繝・せ繝育畑繧ｳ繝ｼ繝・
if __name__ == '__main__':
    """
    WeatherService縺ｮ繝・せ繝亥ｮ溯｡・
    """
    print("WeatherService 繝・せ繝亥ｮ溯｡・)
    print("=" * 40)

    # WeatherService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ菴懈・
    weather_service = WeatherService()

    # 譚ｱ莠ｬ鬧・・蠎ｧ讓・
    tokyo_lat, tokyo_lon = 35.6812, 139.7671

    # 螟ｩ豌玲ュ蝣ｱ蜿門ｾ励ユ繧ｹ繝・
    print("1. 迴ｾ蝨ｨ縺ｮ螟ｩ豌玲ュ蝣ｱ蜿門ｾ・")
    weather = weather_service.get_current_weather(tokyo_lat, tokyo_lon)
    print(f"   螟ｩ豌・ {weather['description']}")
    print(f"   豌玲ｸｩ: {weather['temperature']}ﾂｰC (菴捺─: {weather['feels_like']}ﾂｰC)")
    print(f"   UV謖・焚: {weather['uv_index']}")
    print(f"   貉ｿ蠎ｦ: {weather['humidity']}%")
    print(f"   繧ｽ繝ｼ繧ｹ: {weather['source']}")

    # 螟ｩ豌苓ｦ∫ｴ・ユ繧ｹ繝・
    print("\n2. 螟ｩ豌苓ｦ∫ｴ・")
    summary = weather_service.get_weather_summary(tokyo_lat, tokyo_lon)
    print(f"   隕∫ｴ・ {summary}")

    # 蠕呈ｭｩ驕ｩ諤ｧ蛻､螳壹ユ繧ｹ繝・
    print(f"\n3. 蠕呈ｭｩ驕ｩ諤ｧ蛻､螳・ {weather_service.is_good_weather_for_walking(tokyo_lat, tokyo_lon)}")

    # 繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌怜愛螳壹ユ繧ｹ繝・
    print(f"4. 繝・ヵ繧ｩ繝ｫ繝亥､ｩ豌怜愛螳・ {weather_service.is_default_weather(weather)}")

    # 繝・・繧ｿ螯･蠖捺ｧ讀懆ｨｼ繝・せ繝・
    print(f"5. 繝・・繧ｿ螯･蠖捺ｧ讀懆ｨｼ: {weather_service.validate_weather_data(weather)}")

    # 繧｢繧､繧ｳ繝ｳURL蜿門ｾ励ユ繧ｹ繝・
    print(f"\n6. 螟ｩ豌励い繧､繧ｳ繝ｳURL: {weather_service.get_weather_icon_url(weather['icon'])}")

    print("\n繝・せ繝亥ｮ御ｺ・)
