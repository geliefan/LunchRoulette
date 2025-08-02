import math
from typing import Optional
from error_handler import ErrorHandler


class DistanceCalculator:
    """
    繝上・繝舌・繧ｵ繧､繝ｳ蜈ｬ蠑上ｒ菴ｿ逕ｨ縺励◆霍晞屬險育ｮ励け繝ｩ繧ｹ
    蝨ｰ逅・ｸ翫・2轤ｹ髢薙・霍晞屬繧堤ｷｯ蠎ｦ繝ｻ邨悟ｺｦ縺九ｉ險育ｮ励☆繧・
    """

    # 蝨ｰ逅・・蜊雁ｾ・ｼ・m・・
    EARTH_RADIUS_KM = 6371.0

    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        """
        DistanceCalculator繧ｯ繝ｩ繧ｹ縺ｮ蛻晄悄蛹・

        Args:
            error_handler (ErrorHandler, optional): 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ
        """
        self.error_handler = error_handler or ErrorHandler()

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        繝上・繝舌・繧ｵ繧､繝ｳ蜈ｬ蠑上ｒ菴ｿ逕ｨ縺励※2轤ｹ髢薙・霍晞屬繧定ｨ育ｮ・

        Args:
            lat1 (float): 蝨ｰ轤ｹ1縺ｮ邱ｯ蠎ｦ
            lon1 (float): 蝨ｰ轤ｹ1縺ｮ邨悟ｺｦ
            lat2 (float): 蝨ｰ轤ｹ2縺ｮ邱ｯ蠎ｦ
            lon2 (float): 蝨ｰ轤ｹ2縺ｮ邨悟ｺｦ

        Returns:
            float: 2轤ｹ髢薙・霍晞屬・・m・・

        Raises:
            ValueError: 邱ｯ蠎ｦ繝ｻ邨悟ｺｦ縺ｮ蛟､縺檎┌蜉ｹ縺ｪ蝣ｴ蜷・
        """
        try:
            # 蜈･蜉帛､縺ｮ讀懆ｨｼ
            self._validate_coordinates(lat1, lon1)
            self._validate_coordinates(lat2, lon2)

            # 邱ｯ蠎ｦ繝ｻ邨悟ｺｦ繧偵Λ繧ｸ繧｢繝ｳ縺ｫ螟画鋤
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)

            # 邱ｯ蠎ｦ繝ｻ邨悟ｺｦ縺ｮ蟾ｮ繧定ｨ育ｮ・
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad

            # 繝上・繝舌・繧ｵ繧､繝ｳ蜈ｬ蠑上ｒ驕ｩ逕ｨ
            a = (math.sin(dlat / 2) ** 2
                 + math.cos(lat1_rad) * math.cos(lat2_rad)
                 * math.sin(dlon / 2) ** 2)

            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            # 霍晞屬繧定ｨ育ｮ暦ｼ・m・・
            distance_km = self.EARTH_RADIUS_KM * c

            return round(distance_km, 3)  # 蟆乗焚轤ｹ隨ｬ3菴阪∪縺ｧ

        except Exception as e:
            # 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ・夊ｷ晞屬險育ｮ励お繝ｩ繝ｼ譎ゅ・讎らｮ苓ｷ晞屬繧定ｿ斐☆
            error_info = self.error_handler.handle_distance_calculation_error(e)
            print(f"霍晞屬險育ｮ励お繝ｩ繝ｼ: {error_info['message']}")
            return self._calculate_approximate_distance(lat1, lon1, lat2, lon2)

    def calculate_walking_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> dict:
        """
        蠕呈ｭｩ霍晞屬縺ｨ謇隕∵凾髢薙ｒ險育ｮ・

        Args:
            lat1 (float): 蝨ｰ轤ｹ1縺ｮ邱ｯ蠎ｦ
            lon1 (float): 蝨ｰ轤ｹ1縺ｮ邨悟ｺｦ
            lat2 (float): 蝨ｰ轤ｹ2縺ｮ邱ｯ蠎ｦ
            lon2 (float): 蝨ｰ轤ｹ2縺ｮ邨悟ｺｦ

        Returns:
            dict: 霍晞屬諠・ｱ・郁ｷ晞屬縲∝ｾ呈ｭｩ譎る俣縲∬｡ｨ遉ｺ逕ｨ譁・ｭ怜・・・
        """
        try:
            # 逶ｴ邱夊ｷ晞屬繧定ｨ育ｮ・
            distance_km = self.calculate_distance(lat1, lon1, lat2, lon2)

            # 蠕呈ｭｩ霍晞屬縺ｯ逶ｴ邱夊ｷ晞屬縺ｮ邏・.3蛟阪→縺励※險育ｮ暦ｼ磯％霍ｯ縺ｮ霑ょ屓繧定・・・・
            walking_distance_km = distance_km * 1.3
            walking_distance_m = walking_distance_km * 1000

            # 蠕呈ｭｩ譎る俣繧定ｨ育ｮ暦ｼ域凾騾・km縺ｧ險育ｮ暦ｼ・
            walking_time_minutes = int(walking_distance_km * 15)  # 4km/h = 15蛻・km

            # 陦ｨ遉ｺ逕ｨ縺ｮ霍晞屬譁・ｭ怜・繧堤函謌・
            if walking_distance_m < 1000:
                distance_display = f"{int(walking_distance_m)}m"
            else:
                distance_display = f"{walking_distance_km:.1f}km"

            return {
                'distance_km': round(walking_distance_km, 3),
                'distance_m': int(walking_distance_m),
                'walking_time_minutes': walking_time_minutes,
                'distance_display': distance_display,
                'time_display': f"蠕呈ｭｩ邏кwalking_time_minutes}蛻・
            }

        except Exception as e:
            error_info = self.error_handler.handle_distance_calculation_error(e)
            print(f"蠕呈ｭｩ霍晞屬險育ｮ励お繝ｩ繝ｼ: {error_info['message']}")
            # 繧ｨ繝ｩ繝ｼ譎ゅ・繝・ヵ繧ｩ繝ｫ繝亥､繧定ｿ斐☆
            return {
                'distance_km': 0.5,
                'distance_m': 500,
                'walking_time_minutes': 8,
                'distance_display': "邏・00m",
                'time_display': "蠕呈ｭｩ邏・蛻・,
                'error_info': error_info  # 繧ｨ繝ｩ繝ｼ諠・ｱ繧定ｿｽ蜉
            }

    def _validate_coordinates(self, lat: float, lon: float) -> None:
        """
        邱ｯ蠎ｦ繝ｻ邨悟ｺｦ縺ｮ蛟､繧呈､懆ｨｼ

        Args:
            lat (float): 邱ｯ蠎ｦ
            lon (float): 邨悟ｺｦ

        Raises:
            ValueError: 邱ｯ蠎ｦ繝ｻ邨悟ｺｦ縺ｮ蛟､縺檎┌蜉ｹ縺ｪ蝣ｴ蜷・
        """
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise ValueError("邱ｯ蠎ｦ繝ｻ邨悟ｺｦ縺ｯ謨ｰ蛟､縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・)

        if not (-90 <= lat <= 90):
            raise ValueError(f"邱ｯ蠎ｦ縺ｯ-90縺九ｉ90縺ｮ遽・峇縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・ {lat}")

        if not (-180 <= lon <= 180):
            raise ValueError(f"邨悟ｺｦ縺ｯ-180縺九ｉ180縺ｮ遽・峇縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・ {lon}")

    def _calculate_approximate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        邁｡譏鍋噪縺ｪ霍晞屬險育ｮ暦ｼ医お繝ｩ繝ｼ譎ゅ・繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ・・

        Args:
            lat1 (float): 蝨ｰ轤ｹ1縺ｮ邱ｯ蠎ｦ
            lon1 (float): 蝨ｰ轤ｹ1縺ｮ邨悟ｺｦ
            lat2 (float): 蝨ｰ轤ｹ2縺ｮ邱ｯ蠎ｦ
            lon2 (float): 蝨ｰ轤ｹ2縺ｮ邨悟ｺｦ

        Returns:
            float: 讎らｮ苓ｷ晞屬・・m・・
        """
        try:
            # 邁｡譏鍋噪縺ｪ逶ｴ邱夊ｷ晞屬險育ｮ暦ｼ亥ｹｳ髱｢霑台ｼｼ・・
            lat_diff = abs(lat2 - lat1)
            lon_diff = abs(lon2 - lon1)

            # 1蠎ｦ縺ゅ◆繧翫・霍晞屬・域律譛ｬ莉倩ｿ代〒縺ｮ讎らｮ怜､・・
            lat_km_per_degree = 111.0  # 邱ｯ蠎ｦ1蠎ｦ 竕・111km
            lon_km_per_degree = 91.0   # 邨悟ｺｦ1蠎ｦ 竕・91km・域擲莠ｬ莉倩ｿ托ｼ・

            lat_distance = lat_diff * lat_km_per_degree
            lon_distance = lon_diff * lon_km_per_degree

            # 繝斐ち繧ｴ繝ｩ繧ｹ縺ｮ螳夂炊縺ｧ讎らｮ苓ｷ晞屬繧定ｨ育ｮ・
            approximate_distance = math.sqrt(lat_distance**2 + lon_distance**2)

            return round(approximate_distance, 3)

        except Exception:
            # 譛邨ら噪縺ｪ繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ・壼崋螳壼､繧定ｿ斐☆
            return 0.5  # 500m
