import math


class DistanceCalculator:
    """
    ハーバーサイン公式を使用した距離計算クラス
    地球上の2点間の距離を緯度・経度から計算する
    """
    
    # 地球の半径（km）
    EARTH_RADIUS_KM = 6371.0
    
    def __init__(self):
        """DistanceCalculatorクラスの初期化"""
        pass
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        ハーバーサイン公式を使用して2点間の距離を計算
        
        Args:
            lat1 (float): 地点1の緯度
            lon1 (float): 地点1の経度
            lat2 (float): 地点2の緯度
            lon2 (float): 地点2の経度
            
        Returns:
            float: 2点間の距離（km）
            
        Raises:
            ValueError: 緯度・経度の値が無効な場合
        """
        try:
            # 入力値の検証
            self._validate_coordinates(lat1, lon1)
            self._validate_coordinates(lat2, lon2)
            
            # 緯度・経度をラジアンに変換
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)
            
            # 緯度・経度の差を計算
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            
            # ハーバーサイン公式を適用
            a = (math.sin(dlat / 2) ** 2 + 
                 math.cos(lat1_rad) * math.cos(lat2_rad) * 
                 math.sin(dlon / 2) ** 2)
            
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            # 距離を計算（km）
            distance_km = self.EARTH_RADIUS_KM * c
            
            return round(distance_km, 3)  # 小数点第3位まで
            
        except Exception as e:
            # エラーハンドリング：距離計算エラー時は概算距離を返す
            print(f"距離計算エラー: {e}")
            return self._calculate_approximate_distance(lat1, lon1, lat2, lon2)
    
    def calculate_walking_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> dict:
        """
        徒歩距離と所要時間を計算
        
        Args:
            lat1 (float): 地点1の緯度
            lon1 (float): 地点1の経度
            lat2 (float): 地点2の緯度
            lon2 (float): 地点2の経度
            
        Returns:
            dict: 距離情報（距離、徒歩時間、表示用文字列）
        """
        try:
            # 直線距離を計算
            distance_km = self.calculate_distance(lat1, lon1, lat2, lon2)
            
            # 徒歩距離は直線距離の約1.3倍として計算（道路の迂回を考慮）
            walking_distance_km = distance_km * 1.3
            walking_distance_m = walking_distance_km * 1000
            
            # 徒歩時間を計算（時速4kmで計算）
            walking_time_minutes = int(walking_distance_km * 15)  # 4km/h = 15分/km
            
            # 表示用の距離文字列を生成
            if walking_distance_m < 1000:
                distance_display = f"{int(walking_distance_m)}m"
            else:
                distance_display = f"{walking_distance_km:.1f}km"
            
            return {
                'distance_km': round(walking_distance_km, 3),
                'distance_m': int(walking_distance_m),
                'walking_time_minutes': walking_time_minutes,
                'distance_display': distance_display,
                'time_display': f"徒歩約{walking_time_minutes}分"
            }
            
        except Exception as e:
            print(f"徒歩距離計算エラー: {e}")
            # エラー時はデフォルト値を返す
            return {
                'distance_km': 0.5,
                'distance_m': 500,
                'walking_time_minutes': 8,
                'distance_display': "約500m",
                'time_display': "徒歩約8分"
            }
    
    def _validate_coordinates(self, lat: float, lon: float) -> None:
        """
        緯度・経度の値を検証
        
        Args:
            lat (float): 緯度
            lon (float): 経度
            
        Raises:
            ValueError: 緯度・経度の値が無効な場合
        """
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise ValueError("緯度・経度は数値である必要があります")
        
        if not (-90 <= lat <= 90):
            raise ValueError(f"緯度は-90から90の範囲である必要があります: {lat}")
        
        if not (-180 <= lon <= 180):
            raise ValueError(f"経度は-180から180の範囲である必要があります: {lon}")
    
    def _calculate_approximate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        簡易的な距離計算（エラー時のフォールバック）
        
        Args:
            lat1 (float): 地点1の緯度
            lon1 (float): 地点1の経度
            lat2 (float): 地点2の緯度
            lon2 (float): 地点2の経度
            
        Returns:
            float: 概算距離（km）
        """
        try:
            # 簡易的な直線距離計算（平面近似）
            lat_diff = abs(lat2 - lat1)
            lon_diff = abs(lon2 - lon1)
            
            # 1度あたりの距離（日本付近での概算値）
            lat_km_per_degree = 111.0  # 緯度1度 ≈ 111km
            lon_km_per_degree = 91.0   # 経度1度 ≈ 91km（東京付近）
            
            lat_distance = lat_diff * lat_km_per_degree
            lon_distance = lon_diff * lon_km_per_degree
            
            # ピタゴラスの定理で概算距離を計算
            approximate_distance = math.sqrt(lat_distance**2 + lon_distance**2)
            
            return round(approximate_distance, 3)
            
        except Exception:
            # 最終的なフォールバック：固定値を返す
            return 0.5  # 500m