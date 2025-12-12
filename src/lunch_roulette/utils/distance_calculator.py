"""距離計算モジュール - 2地点間の距離を計算する

【このモジュールがやること】
地図上の2つの場所（レストランとあなたの現在地など）の間の距離を計算します。

【なぜ必要か】
「近くのレストラン」を探すには、今いる場所からお店までの距離を知る必要があります。
Googleマップで「ここから〇〇まで何km」と表示されるのと同じ計算をします。

【ポイント】
・地球は丸い（球体）ので、特別な計算式を使います
・直線距離だけでなく、実際に歩く距離も計算します
・緯度・経度という座標から距離を求めます
"""

import math  # 数学の計算に使うライブラリ（sin, cos, 平方根など）
from typing import Optional  # 型ヒント用（プログラムをわかりやすくするため）
from .error_handler import ErrorHandler  # エラー処理用


class DistanceCalculator:
    """
    2地点間の距離を計算するクラス
    
    【何をするクラス?】
    地図上の2つの場所の距離を計算します。
    例：「東京駅から新宿駅まで何km?」を計算できます。
    
    【なぜ特別な計算が必要?】
    地球は平らではなく丸い（球体）ので、
    単純な三平方の定理（a²+b²=c²）では正確な距離が出ません。
    球面上の最短距離を求める「ハバースイン公式」という
    特別な計算式を使います。
    
    【使い方の例】
        calculator = DistanceCalculator()
        # 東京駅（緯度35.6812, 経度139.7671）から
        # 新宿駅（緯度35.6896, 経度139.7006）までの距離を計算
        distance_km = calculator.calculate_distance(
            35.6812, 139.7671,  # 東京駅の座標
            35.6896, 139.7006   # 新宿駅の座標
        )
        print(f"距離: {distance_km}km")  # → 「距離: 6.5km」のように表示
    
    【このクラスで計算できること】
    1. 2地点間の直線距離（鳥が飛ぶ距離）
    2. 実際に歩く距離（道は曲がっているので直線距離×1.3倍）
    3. 歩いて何分かかるか（時速4kmで計算）
    """

    # ===== 定数の定義（プログラム中で変わらない値） =====
    
    # 【定数1】地球の半径
    # 地球の赤道半径は約6378km、極半径は約6357kmですが、
    # 平均半径6371kmを使うのが一般的です。
    # この値は、国際的な標準として使われています。
    EARTH_RADIUS_KM = 6371.0  # 単位: キロメートル
    
    # 【定数2】徒歩距離の補正係数（直線距離→実際の歩行距離に変換）
    # 理由: 実際の道は真っすぐではなく、曲がったり迂回したりします
    # 例: 直線距離が1kmでも、実際に歩くと1.3km程度になります
    # この1.3という値は、都市部の道路網を考慮した経験値です
    WALKING_DISTANCE_MULTIPLIER = 1.3  # 1.3倍 = 30%増し
    
    # 【定数3】平均的な歩行速度
    # 一般的な大人がゆっくり歩く速度 = 時速4km
    # （速く歩く人は時速5〜6km、高齢者は時速3km程度）
    # この値を使って「徒歩〇分」を計算します
    WALKING_SPEED_KM_PER_HOUR = 4.0  # 単位: 時速km（1時間で4km進む）

    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        """
        距離計算機を初期化します
        
        Args:
            error_handler: エラーが発生した時の処理を行うオブジェクト（省略可能）
        """
        self.error_handler = error_handler or ErrorHandler()

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        2地点間の距離を計算します
        
        地球は球体なので、球面上の最短距離（大圏距離）を計算します。
        これは「ハバースイン公式」という数学の公式を使って求めます。
        
        Args:
            lat1: 出発地点の緯度（例: 東京駅は 35.6812）
            lon1: 出発地点の経度（例: 東京駅は 139.7671）
            lat2: 到着地点の緯度（例: 新宿駅は 35.6896）
            lon2: 到着地点の経度（例: 新宿駅は 139.7006）
        
        Returns:
            2地点間の距離（キロメートル）
            例: 6.5 なら 6.5km の距離
        
        Raises:
            ValueError: 緯度や経度の値が正しくない場合
            
        使用例:
            distance = calculator.calculate_distance(35.6812, 139.7671, 35.6896, 139.7006)
            print(f"{distance}km")  # 例: 6.5km
        """
        try:
            # ステップ1: 入力された緯度・経度が正しい値か確認
            self._validate_coordinates(lat1, lon1)
            self._validate_coordinates(lat2, lon2)

            # ========================================
            # ステップ2: 角度の単位を変換する
            # ========================================
            # 【なぜ変換が必要?】
            # 緯度・経度は普通「度」（degree）で表されます（例: 35度）
            # でも、数学の計算では「ラジアン」（radian）という単位を使います
            # 
            # 【度とラジアンの関係】
            #   360度 = 2π ラジアン （円1周分）
            #   180度 = π ラジアン  （半円）
            #    90度 = π/2 ラジアン ≒ 1.57ラジアン（直角）
            # 
            # Pythonのmath.radians()が自動で変換してくれます
            lat1_rad = math.radians(lat1)  # 出発地点の緯度を度→ラジアンに変換
            lon1_rad = math.radians(lon1)  # 出発地点の経度を度→ラジアンに変換
            lat2_rad = math.radians(lat2)  # 到着地点の緯度を度→ラジアンに変換
            lon2_rad = math.radians(lon2)  # 到着地点の経度を度→ラジアンに変換

            # ========================================
            # ステップ3: 2地点間の「ズレ」を計算
            # ========================================
            # 【何を計算している?】
            # 出発地点と到着地点が、どれだけ離れているかを計算します
            # ・緯度の差 = 南北方向のズレ
            # ・経度の差 = 東西方向のズレ
            dlat = lat2_rad - lat1_rad  # 緯度の差（南北のズレ）
            dlon = lon2_rad - lon1_rad  # 経度の差（東西のズレ）

            # ========================================
            # ステップ4: ハバースイン公式で距離を計算
            # ========================================
            # 【ハバースイン公式とは?】
            # 球面上の2点間の最短距離を求める数学の公式です。
            # 飛行機が最短ルートで飛ぶ時や、GPSで距離を測る時に使われます。
            # 
            # 【公式の流れ】
            # 1. 緯度・経度の差から中間値 a を計算
            # 2. a から中心角 c を計算（地球の中心から見た角度）
            # 3. 中心角に地球の半径をかけて距離を求める
            # 
            # 【イメージ】
            #        地点A ●
            #              /  \
            #             /    \
            #            / 角度c \
            #           /   ↓   \
            #          ●---------● 地点B
            #        地球の中心
            
            # 4-1: 中間値 a を計算（数学的な計算の途中段階）
            # この値自体に物理的な意味はありませんが、次の計算に必要です
            a = (math.sin(dlat / 2) ** 2  # 緯度の差の半分のsin²
                 + math.cos(lat1_rad) * math.cos(lat2_rad)  # 緯度の補正
                 * math.sin(dlon / 2) ** 2)  # 経度の差の半分のsin²

            # 4-2: 中心角 c を計算
            # 中心角 = 地球の中心から見た2地点間の角度（ラジアン）
            # 例: 中心角が0.001ラジアンなら、とても近い距離
            #     中心角が3.14ラジアン（π）なら、地球の裏側
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            # ========================================
            # ステップ5: 角度から実際の距離を計算
            # ========================================
            # 【公式】距離 = 地球の半径 × 中心角
            # 例: 半径6371km × 0.001ラジアン = 約6.4km
            distance_km = self.EARTH_RADIUS_KM * c

            # 小数点以下3桁で四捨五入して返す
            # 例: 6.543210 km → 6.543 km
            # （これ以上細かくしても意味がないため）
            return round(distance_km, 3)

        except Exception as e:
            # エラーが発生した場合は、簡易的な方法で距離を計算
            error_info = self.error_handler.handle_distance_calculation_error(e)
            print(f"距離計算でエラーが発生しました: {error_info['message']}")
            print("簡易的な方法で距離を計算します")
            return self._calculate_approximate_distance(lat1, lon1, lat2, lon2)

    def calculate_walking_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> dict:
        """
        徒歩での移動距離と所要時間を計算します
        
        直線距離だけでなく、実際に道路を歩く場合の距離と時間を計算します。
        道路は直線ではなく曲がっているので、直線距離より長くなります。
        
        Args:
            lat1: 出発地点の緯度
            lon1: 出発地点の経度
            lat2: 到着地点の緯度
            lon2: 到着地点の経度
        
        Returns:
            dict: 以下の情報を含む辞書
                - distance_km: 徒歩距離（キロメートル）
                - distance_m: 徒歩距離（メートル）
                - walking_time_minutes: 徒歩所要時間（分）
                - distance_display: 画面表示用の距離（例: "500m" や "1.2km"）
                - time_display: 画面表示用の時間（例: "徒歩約8分"）
        
        使用例:
            result = calculator.calculate_walking_distance(35.6812, 139.7671, 35.6896, 139.7006)
            print(result['time_display'])  # 例: "徒歩約24分"
        """
        try:
            # ステップ1: 2地点間の直線距離を計算
            straight_distance_km = self.calculate_distance(lat1, lon1, lat2, lon2)

            # ステップ2: 実際の徒歩距離を計算
            # 道路は曲がっているので、直線距離の1.3倍を実際の歩行距離とします
            # （例: 直線で1kmなら、実際には1.3km歩くことになる）
            walking_distance_km = straight_distance_km * self.WALKING_DISTANCE_MULTIPLIER
            
            # キロメートルをメートルに変換（1km = 1000m）
            walking_distance_m = walking_distance_km * 1000

            # ステップ3: 徒歩所要時間を計算
            # 平均的な歩行速度は時速4kmなので:
            # 時間（時間）= 距離（km）÷ 速度（km/時）
            # 時間（分）= 時間（時間）× 60
            # つまり、距離（km）× 15 = 時間（分）
            walking_time_hours = walking_distance_km / self.WALKING_SPEED_KM_PER_HOUR
            walking_time_minutes = int(walking_time_hours * 60)

            # ステップ4: 画面に表示しやすい形式に整形
            # 1km未満なら「○○m」、1km以上なら「○.○km」と表示
            if walking_distance_m < 1000:
                distance_display = f"{int(walking_distance_m)}m"
            else:
                distance_display = f"{walking_distance_km:.1f}km"

            # 計算結果をまとめて返す
            return {
                'distance_km': round(walking_distance_km, 3),      # 例: 1.234
                'distance_m': int(walking_distance_m),              # 例: 1234
                'walking_time_minutes': walking_time_minutes,       # 例: 18
                'distance_display': distance_display,               # 例: "1.2km"
                'time_display': f"徒歩約{walking_time_minutes}分"  # 例: "徒歩約18分"
            }

        except Exception as e:
            # エラーが発生した場合は、標準的な値を返す
            error_info = self.error_handler.handle_distance_calculation_error(e)
            print(f"徒歩距離計算でエラーが発生しました: {error_info['message']}")
            print("標準的な値（500m、徒歩8分）を返します")
            
            return {
                'distance_km': 0.5,
                'distance_m': 500,
                'walking_time_minutes': 8,
                'distance_display': "約500m",
                'time_display': "徒歩約8分",
                'error_info': error_info
            }

    def _validate_coordinates(self, lat: float, lon: float) -> None:
        """
        緯度・経度の値が正しいかチェックします
        
        緯度は-90度〜90度、経度は-180度〜180度の範囲でなければなりません。
        また、数値でなければなりません。
        
        Args:
            lat: 緯度（-90〜90の数値）
            lon: 経度（-180〜180の数値）
        
        Raises:
            ValueError: 緯度・経度の値が正しくない場合にエラーを発生させます
        """
        # 数値かどうかをチェック
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise ValueError("緯度・経度は数値である必要があります（文字列などは使えません）")

        # 緯度の範囲をチェック（北極が90度、南極が-90度）
        if not (-90 <= lat <= 90):
            raise ValueError(f"緯度は-90から90の範囲である必要があります（入力された値: {lat}）")

        # 経度の範囲をチェック（東経が正、西経が負、-180〜180度）
        if not (-180 <= lon <= 180):
            raise ValueError(f"経度は-180から180の範囲である必要があります（入力された値: {lon}）")

    def _calculate_approximate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        簡易的な方法で距離を計算します（エラー時の予備手段）
        
        正確な計算ができない場合に使用する、簡易的な距離計算方法です。
        地球を平面として扱い、ピタゴラスの定理（三平方の定理）を使って計算します。
        
        計算方法:
        1. 緯度1度 = 約111km、経度1度 = 約91km（東京付近）として換算
        2. 緯度の差と経度の差をそれぞれkmに変換
        3. 直角三角形の斜辺の長さ = √(縦^2 + 横^2) で計算
        
        Args:
            lat1: 出発地点の緯度
            lon1: 出発地点の経度
            lat2: 到着地点の緯度
            lon2: 到着地点の経度
        
        Returns:
            概算の距離（キロメートル）
        """
        try:
            # ステップ1: 緯度と経度の差を計算（絶対値で取得）
            lat_diff = abs(lat2 - lat1)  # 緯度の差
            lon_diff = abs(lon2 - lon1)  # 経度の差

            # ステップ2: 「度」を「キロメートル」に変換
            # 日本付近での概算値を使用
            lat_km_per_degree = 111.0  # 緯度1度 ≈ 111km（地球のどこでもほぼ同じ）
            lon_km_per_degree = 91.0   # 経度1度 ≈ 91km（東京付近の値、緯度によって変わる）

            # 緯度・経度の差をkmに変換
            lat_distance = lat_diff * lat_km_per_degree  # 南北方向の距離
            lon_distance = lon_diff * lon_km_per_degree  # 東西方向の距離

            # ステップ3: ピタゴラスの定理で距離を計算
            # 直角三角形の斜辺 = √(縦^2 + 横^2)
            approximate_distance = math.sqrt(lat_distance**2 + lon_distance**2)

            return round(approximate_distance, 3)

        except Exception:
            # それでもエラーが発生したら、固定値（500m）を返す
            print("簡易計算でもエラーが発生したため、固定値500mを返します")
            return 0.5  # 0.5km = 500m
