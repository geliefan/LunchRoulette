#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeatherService - 天気情報サービスクラス
WeatherAPI.com APIから天気情報を取得する機能を提供

このクラスができること:
1. 指定した場所の現在の天気を取得
2. 天気データを日本語に変換（例: "sunny" → "晴れ"）
3. キャッシュを使ってAPI呼び出し回数を節約
4. エラー時には標準的な天気情報を返す

使用例:
    service = WeatherService()
    weather = service.get_current_weather(35.6812, 139.7671)  # 東京駅の天気
    print(f"気温: {weather['temperature']}°C, 天気: {weather['description']}")
"""

import requests
import os
from typing import Dict, Optional
from datetime import datetime
from .cache_service import CacheService


class WeatherService:
    """
    天気情報を取得するサービスクラス
    
    WeatherAPI.comという外部サービスから天気データを取得します。
    APIが使えない時は、標準的な天気情報（晴れ、20度）を返します。
    """

    # ===== デフォルト天気情報 =====
    # APIが使えない時やエラー時に使用する標準的な天気データ
    # 東京の平均的な春秋の天気をイメージして設定
    DEFAULT_WEATHER = {
        'temperature': 20.0,       # 気温（摂氏） - 20度は過ごしやすい気温
        'condition': 'sunny',      # 天気状況（英語）
        'description': '晴れ',     # 天気状況（日本語）
        'uv_index': 3.0,           # UV指数 - 3は「中程度」
        'humidity': 60,            # 湿度（%） - 60%は快適な範囲
        'pressure': 1013,          # 気圧（hPa） - 標準大気圧
        'visibility': 10.0,        # 視界（km） - 10kmは良好
        'wind_speed': 2.0,         # 風速（m/s） - 微風
        'wind_direction': 180,     # 風向（度） - 180度は南風
        'icon': 1000,              # 天気アイコンコード（1000 = 晴れ）
        'feels_like': 20.0,        # 体感温度 - 気温と同じ
        'source': 'default'        # データソース - デフォルト値であることを明示
    }

    # ===== 天気状況の英語→日本語変換テーブル =====
    # WeatherAPI.comから返ってくる英語の天気表現を日本語に変換するための辞書
    # 例: 'sunny' → '晴れ', 'rainy' → '雨'
    CONDITION_MAPPING = {
        'sunny': '晴れ',
        'clear': '快晴', 
        'partly cloudy': '部分的に曇り',
        'cloudy': '曇り',
        'overcast': '曇天',
        'mist': '霧',
        'patchy rain possible': '所により雨の可能性',
        'patchy snow possible': '所により雪の可能性',
        'patchy sleet possible': 'みぞれの可能性',
        'patchy freezing drizzle possible': '氷雨の可能性',
        'thundery outbreaks possible': '雷雨の可能性',
        'blowing snow': '地吹雪',
        'blizzard': '吹雪',
        'fog': '霧',
        'freezing fog': '氷霧',
        'patchy light drizzle': '所により小雨',
        'light drizzle': '小雨',
        'freezing drizzle': '氷雨',
        'heavy freezing drizzle': '激しい氷雨',
        'patchy light rain': '所により小雨',
        'light rain': '小雨',
        'moderate rain at times': '時々中程度の雨',
        'moderate rain': '中程度の雨',
        'heavy rain at times': '時々激しい雨',
        'heavy rain': '激しい雨',
        'light freezing rain': '軽い氷雨',
        'moderate or heavy freezing rain': '中程度から激しい氷雨',
        'light sleet': '軽いみぞれ',
        'moderate or heavy sleet': '中程度から激しいみぞれ',
        'patchy light snow': '所により軽い雪',
        'light snow': '軽い雪',
        'patchy moderate snow': '所により中程度の雪',
        'moderate snow': '中程度の雪',
        'patchy heavy snow': '所により激しい雪',
        'heavy snow': '激しい雪',
        'ice pellets': '氷粒',
        'light rain shower': '軽いにわか雨',
        'moderate or heavy rain shower': '中程度から激しいにわか雨',
        'torrential rain shower': '激流のようなにわか雨',
        'light sleet showers': '軽いみぞれのにわか雨',
        'moderate or heavy sleet showers': '中程度から激しいみぞれのにわか雨',
        'light snow showers': '軽い雪のにわか雨',
        'moderate or heavy snow showers': '中程度から激しい雪のにわか雨',
        'patchy light rain with thunder': '雷を伴う所により軽い雨',
        'moderate or heavy rain with thunder': '雷を伴う中程度から激しい雨',
        'patchy light snow with thunder': '雷を伴う所により軽い雪',
        'moderate or heavy snow with thunder': '雷を伴う中程度から激しい雪',
        'patchy rain nearby': '近くで雨',  # 新しく追加
        'patchy snow nearby': '近くで雪',  # 新しく追加
        'patchy sleet nearby': '近くでみぞれ',  # 新しく追加
        'patchy freezing drizzle nearby': '近くで氷雨',  # 新しく追加
        'thundery outbreaks nearby': '近くで雷雨'  # 新しく追加
    }

    def __init__(self, api_key: Optional[str] = None, cache_service: Optional[CacheService] = None):
        """
        天気サービスを初期化します
        
        初期化時に以下を設定:
        - WeatherAPI.comのAPIキー（外部サービスへのアクセスに必要）
        - キャッシュサービス（同じデータを何度も取得しないため）
        - APIのURLとタイムアウト設定

        Args:
            api_key: WeatherAPI.comのAPIキー（省略可、環境変数から取得）
            cache_service: キャッシュサービス（省略可、自動作成）
        """
        # APIキーの取得（2つの方法を試す）
        # 1. 引数で渡されたAPIキーを使用
        # 2. 環境変数 WEATHERAPI_KEY から取得
        # ※どちらもなければNone（デフォルト天気を返す）
        self.api_key = api_key or os.getenv('WEATHERAPI_KEY')
        
        # キャッシュサービスの設定（同じデータを繰り返し取得しないため）
        self.cache_service = cache_service or CacheService()
        
        # WeatherAPI.comのAPIエンドポイント（URL）
        self.api_base_url = "http://api.weatherapi.com/v1/current.json"
        
        # APIリクエストのタイムアウト設定（10秒）
        # タイムアウト = サーバーからの応答を待つ最大時間
        self.timeout = 10

        # APIキーが設定されていない場合は警告を表示
        if not self.api_key:
            print("警告: WeatherAPI.com APIキーが設定されていません。デフォルト天気情報を使用します。")

    def get_current_weather(self, lat: float, lon: float) -> Dict[str, any]:
        """
        指定された場所の現在の天気情報を取得します
        
        処理の流れ:
        1. キャッシュに同じ場所の天気データがあるか確認
        2. キャッシュにあればそれを返す（APIを呼ばない）
        3. なければWeatherAPI.comに問い合わせ
        4. 取得した天気データをキャッシュに保存（10分間）
        5. エラーが発生したらデフォルトの天気情報を返す

        Args:
            lat: 緯度（例: 東京駅は 35.6812）
            lon: 経度（例: 東京駅は 139.7671）

        Returns:
            dict: 天気情報の辞書
                - temperature: 気温（摂氏）
                - description: 天気の説明（日本語）
                - humidity: 湿度（%）
                - uv_index: UV指数
                など

        使用例:
            >>> service = WeatherService()
            >>> weather = service.get_current_weather(35.6812, 139.7671)
            >>> print(f"気温: {weather['temperature']}°C, 天気: {weather['description']}")
        """
        # ===== ステップ1: キャッシュキーを生成 =====
        # キャッシュキー = データを識別するための文字列
        # 同じ場所の天気は、少しの時間（10分）なら同じデータを使い回す
        cache_key = self.cache_service.generate_cache_key(
            'weather',
            lat=round(lat, 4),  # 小数点以下4桁に丸める（例: 35.681234 → 35.6812）
            lon=round(lon, 4)   # これにより、ほぼ同じ場所の天気は同じキャッシュを使える
        )

        # ===== ステップ2: キャッシュからデータ取得を試みる =====
        cached_data = self.cache_service.get_cached_data(cache_key)
        if cached_data:
            # キャッシュにデータがあった → APIを呼ばずに済む
            desc = cached_data.get('description', cached_data.get('condition', '天気'))
            print(f"天気情報をキャッシュから取得: {desc}")
            return cached_data

        # ===== ステップ3: APIキーの確認 =====
        # APIキーがないと外部サービスを使えないので、デフォルト値を返す
        if not self.api_key:
            print("APIキーが未設定のため、デフォルト天気情報を返します")
            return self._get_default_weather()

        try:
            # ===== ステップ4: APIリクエストのパラメータを準備 =====
            params = {
                'key': self.api_key,        # 認証用のAPIキー
                'q': f"{lat},{lon}",        # 緯度・経度を「35.6812,139.7671」の形式で指定
                'aqi': 'no'                 # 大気質データは不要（aqi = Air Quality Index）
            }

            print(f"天気情報APIを呼び出します: 緯度={lat}, 経度={lon}")

            # ===== ステップ5: APIリクエストを実行 =====
            # requests.get = HTTPのGETリクエストを送信する関数
            response = requests.get(self.api_base_url, params=params, timeout=self.timeout)
            response.raise_for_status()  # エラーがあれば例外を発生させる

            # ===== ステップ6: レスポンスをJSON形式で解析 =====
            data = response.json()

            # ===== ステップ7: データを使いやすい形式に整形 =====
            weather_data = self._format_weather_data(data)

            # ===== ステップ8: データをキャッシュに保存 =====
            # ttl=600 → 600秒（10分）間キャッシュを保持
            self.cache_service.set_cached_data(cache_key, weather_data, ttl=600)

            print(f"天気情報取得成功: {weather_data['description']}, {weather_data['temperature']}°C")
            return weather_data

        except requests.exceptions.HTTPError as e:
            # ===== エラー処理1: HTTPエラー =====
            # HTTPエラー = サーバーから400番台または500番台のエラーが返ってきた
            
            if e.response.status_code == 429:
                # 429エラー = レート制限（APIの呼び出し回数制限に達した）
                print(f"天気情報API: リクエスト回数制限に達しました: {e}")
                # 古いキャッシュがあればそれを使う
                fallback_data = self._get_fallback_cache_data(cache_key)
                if fallback_data:
                    return fallback_data
                    
            elif e.response.status_code == 401:
                # 401エラー = 認証エラー（APIキーが間違っている）
                print(f"天気情報API: APIキーが無効です: {e}")
            else:
                # その他のHTTPエラー
                print(f"天気情報API: HTTPエラーが発生しました: {e}")

            # エラー時はデフォルトの天気情報を返す
            return self._get_default_weather()

        except requests.exceptions.RequestException as e:
            # ===== エラー処理2: ネットワークエラー =====
            # ネットワークエラー = インターネット接続の問題、タイムアウトなど
            print(f"天気情報API: 通信エラーが発生しました: {e}")
            
            # 古いキャッシュデータがあれば使用
            fallback_data = self._get_fallback_cache_data(cache_key)
            if fallback_data:
                return fallback_data

            return self._get_default_weather()

        except (ValueError, KeyError) as e:
            # JSONパースエラー、レスポンス形式エラーなど
            print(f"天気情報API レスポンス解析エラー: {e}")
            return self._get_default_weather()

    def _format_weather_data(self, raw_data: Dict) -> Dict[str, any]:
        """
        WeatherAPI.comからのレスポンスを内部形式に整形

        Args:
            raw_data (dict): WeatherAPI.comからの生レスポンス

        Returns:
            dict: 整形された天気情報
        """
        try:
            current = raw_data.get('current', {})
            condition = current.get('condition', {})
            
            # 天気状況の英語名を取得し、日本語に変換
            condition_text = condition.get('text', '').lower()
            description = self.CONDITION_MAPPING.get(condition_text, condition_text)

            weather_data = {
                'temperature': float(current.get('temp_c', 20.0)),
                'condition': condition_text,
                'description': description,
                'humidity': int(current.get('humidity', 60)),
                'pressure': float(current.get('pressure_mb', 1013)),
                'visibility': float(current.get('vis_km', 10.0)),
                'wind_speed': float(current.get('wind_kph', 0.0)) / 3.6,  # kph to m/s
                'wind_direction': int(current.get('wind_degree', 0)),
                'uv_index': float(current.get('uv', 0.0)),
                'icon': condition.get('code', 1000),  # WeatherAPI.comのアイコンコード
                'feels_like': float(current.get('feelslike_c', current.get('temp_c', 20.0))),
                'last_updated': current.get('last_updated', datetime.now().strftime('%Y-%m-%d %H:%M')),
                'source': 'weatherapi'
            }

            return weather_data

        except Exception as e:
            print(f"天気データ整形エラー: {e}")
            return self._get_default_weather()

    def _get_default_weather(self) -> Dict[str, any]:
        """
        デフォルト天気情報を返す

        Returns:
            dict: デフォルト天気情報
        """
        print("デフォルト天気情報を使用")
        return self.DEFAULT_WEATHER.copy()

    def _get_fallback_cache_data(self, cache_key: str) -> Optional[Dict]:
        """
        期限切れでも古いキャッシュデータを取得

        Args:
            cache_key (str): キャッシュキー

        Returns:
            dict or None: 古いキャッシュデータ（存在する場合）
        """
        try:
            from ..models.database import get_db_connection

            with get_db_connection(self.cache_service.db_path) as conn:
                cursor = conn.execute('''
                    SELECT data FROM cache WHERE cache_key = ?
                    ORDER BY created_at DESC LIMIT 1
                ''', (cache_key,))
                result = cursor.fetchone()

                if result:
                    data = self.cache_service.deserialize_data(result[0])
                    print(f"期限切れキャッシュデータを使用: {data.get('description', '不明')}")
                    return data

        except Exception as e:
            print(f"フォールバックキャッシュデータ取得エラー: {e}")

        return None

    def get_weather_summary(self, lat: float, lon: float) -> str:
        """
        天気の簡潔な要約を取得

        Args:
            lat (float): 緯度
            lon (float): 経度

        Returns:
            str: 天気の要約文
        """
        weather = self.get_current_weather(lat, lon)
        
        temp = weather['temperature']
        description = weather['description']
        feels_like = weather['feels_like']
        
        if abs(temp - feels_like) > 3:
            return f"{description}、気温{temp}°C（体感{feels_like}°C）"
        else:
            return f"{description}、気温{temp}°C"

    def is_good_weather_for_walking(self, lat: float, lon: float) -> bool:
        """
        徒歩に適した天気かどうかを判定

        Args:
            lat (float): 緯度
            lon (float): 経度

        Returns:
            bool: 徒歩に適している場合True
        """
        weather = self.get_current_weather(lat, lon)
        
        # 雨や雪が降っている場合は適さない
        condition = weather['condition'].lower()
        if any(word in condition for word in ['rain', 'snow', 'storm', 'drizzle']):
            return False
            
        # 極端な気温の場合は適さない
        temp = weather['temperature']
        if temp < 0 or temp > 35:
            return False
            
        # 強風の場合は適さない（風速10m/s以上）
        if weather['wind_speed'] > 10:
            return False
            
        return True

    def is_default_weather(self, weather_data: Dict) -> bool:
        """
        デフォルト天気情報かどうかを判定

        Args:
            weather_data (dict): 天気データ

        Returns:
            bool: デフォルト天気の場合True
        """
        return weather_data.get('source') == 'default'

    def validate_weather_data(self, weather_data: Dict) -> bool:
        """
        天気データの妥当性を検証

        Args:
            weather_data (dict): 検証する天気データ

        Returns:
            bool: データが妥当な場合True
        """
        try:
            # 必須フィールドの存在確認
            required_fields = ['temperature', 'description', 'humidity']
            for field in required_fields:
                if field not in weather_data:
                    return False

            # 数値範囲の妥当性確認
            temp = float(weather_data['temperature'])
            if not (-100 <= temp <= 60):  # 地球上の気温範囲
                return False

            humidity = int(weather_data['humidity'])
            if not (0 <= humidity <= 100):
                return False

            uv = float(weather_data.get('uv_index', 0))
            if not (0 <= uv <= 15):
                return False

            return True

        except (ValueError, TypeError):
            return False

    def get_weather_icon_emoji(self, condition: str) -> str:
        """
        天気状態に応じた絵文字を返す

        Args:
            condition (str): 天気状態（英語）

        Returns:
            str: 天気を表す絵文字
        """
        condition_lower = condition.lower()
        
        if 'clear' in condition_lower or 'sunny' in condition_lower:
            return '☀️'
        elif 'cloud' in condition_lower:
            return '☁️'
        elif 'rain' in condition_lower or 'drizzle' in condition_lower:
            return '🌧️'
        elif 'snow' in condition_lower:
            return '❄️'
        elif 'thunder' in condition_lower or 'storm' in condition_lower:
            return '⛈️'
        elif 'fog' in condition_lower or 'mist' in condition_lower:
            return '🌫️'
        else:
            return '🌤️'
