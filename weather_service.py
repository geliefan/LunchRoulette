#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeatherService - 天気情報サービスクラス
OpenWeatherMap APIから天気情報を取得する機能を提供

このクラスは以下の機能を提供します:
- OpenWeatherMap One Call 3.0 API統合
- 天気データの取得と整形機能
- キャッシュ機能との統合
- エラーハンドリングとフォールバック機能
"""

import requests
import os
from typing import Dict, Optional
from datetime import datetime
from cache_service import CacheService


class WeatherService:
    """
    OpenWeatherMap APIから天気情報を取得するサービス
    
    One Call 3.0 APIを使用して現在の天気、気温、UV指数などを取得し、
    エラー時にはデフォルト天気情報を提供する。
    """
    
    # デフォルト天気情報
    DEFAULT_WEATHER = {
        'temperature': 20.0,
        'condition': 'clear',
        'description': '晴れ',
        'uv_index': 3.0,
        'humidity': 60,
        'pressure': 1013,
        'visibility': 10000,
        'wind_speed': 2.0,
        'wind_direction': 180,
        'icon': '01d'
    }
    
    # 天気状況の日本語マッピング
    CONDITION_MAPPING = {
        'clear': '晴れ',
        'clouds': '曇り',
        'rain': '雨',
        'drizzle': '小雨',
        'thunderstorm': '雷雨',
        'snow': '雪',
        'mist': '霧',
        'fog': '霧',
        'haze': 'もや',
        'dust': '砂塵',
        'sand': '砂嵐',
        'ash': '火山灰',
        'squall': '突風',
        'tornado': '竜巻'
    }
    
    def __init__(self, api_key: Optional[str] = None, cache_service: Optional[CacheService] = None):
        """
        WeatherServiceを初期化
        
        Args:
            api_key (str, optional): OpenWeatherMap APIキー
            cache_service (CacheService, optional): キャッシュサービス
        """
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.cache_service = cache_service or CacheService()
        self.api_base_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.timeout = 10  # APIリクエストのタイムアウト（秒）
        
        if not self.api_key:
            print("警告: OpenWeatherMap APIキーが設定されていません。デフォルト天気情報を使用します。")
    
    def get_current_weather(self, lat: float, lon: float) -> Dict[str, any]:
        """
        指定された座標の現在の天気情報を取得
        
        Args:
            lat (float): 緯度
            lon (float): 経度
            
        Returns:
            dict: 天気情報（気温、天気状況、UV指数など）
            
        Example:
            >>> weather_service = WeatherService()
            >>> weather = weather_service.get_current_weather(35.6812, 139.7671)
            >>> print(f"Temperature: {weather['temperature']}°C")
        """
        # キャッシュキーを生成
        cache_key = self.cache_service.generate_cache_key(
            'weather',
            lat=round(lat, 4),  # 精度を制限してキャッシュ効率を向上
            lon=round(lon, 4)
        )
        
        # キャッシュから取得を試行
        cached_data = self.cache_service.get_cached_data(cache_key)
        if cached_data:
            print(f"天気情報をキャッシュから取得: {cached_data['description']}")
            return cached_data
        
        # APIキーが設定されていない場合はデフォルト天気情報を返す
        if not self.api_key:
            return self._get_default_weather()
        
        try:
            # APIパラメータを構築
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',  # 摂氏温度
                'lang': 'ja',       # 日本語
                'exclude': 'minutely,hourly,daily,alerts'  # 現在の天気のみ
            }
            
            print(f"天気情報API呼び出し: lat={lat}, lon={lon}")
            
            # APIリクエストを実行
            response = requests.get(self.api_base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # レスポンスを解析
            data = response.json()
            
            # 天気情報を整形
            weather_data = self._format_weather_data(data)
            
            # キャッシュに保存（10分間）
            self.cache_service.set_cached_data(cache_key, weather_data, ttl=600)
            
            print(f"天気情報取得成功: {weather_data['description']}, {weather_data['temperature']}°C")
            return weather_data
            
        except requests.exceptions.HTTPError as e:
            # HTTPエラー（レート制限、認証エラーなど）
            if e.response.status_code == 429:
                print(f"天気情報API レート制限エラー: {e}")
                # レート制限時は古いキャッシュデータを使用を試行
                fallback_data = self._get_fallback_cache_data(cache_key)
                if fallback_data:
                    return fallback_data
            elif e.response.status_code == 401:
                print(f"天気情報API 認証エラー: {e}")
            else:
                print(f"天気情報API HTTPエラー: {e}")
            return self._get_default_weather()
            
        except requests.exceptions.RequestException as e:
            print(f"天気情報API リクエストエラー: {e}")
            # ネットワークエラー時は古いキャッシュデータを使用を試行
            fallback_data = self._get_fallback_cache_data(cache_key)
            if fallback_data:
                return fallback_data
            return self._get_default_weather()
            
        except (ValueError, KeyError) as e:
            print(f"天気情報データ解析エラー: {e}")
            return self._get_default_weather()
            
        except Exception as e:
            print(f"天気情報取得で予期しないエラー: {e}")
            return self._get_default_weather()
    
    def _format_weather_data(self, api_data: Dict) -> Dict[str, any]:
        """
        APIレスポンスを標準形式に整形
        
        Args:
            api_data (dict): OpenWeatherMap APIからのレスポンス
            
        Returns:
            dict: 整形された天気情報
            
        Raises:
            KeyError: 必要なフィールドが不足している場合
        """
        try:
            current = api_data['current']
            weather = current['weather'][0]
            
            # 基本的な天気情報
            condition = weather['main'].lower()
            description = weather.get('description', self.CONDITION_MAPPING.get(condition, '不明'))
            
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
            raise KeyError(f"天気情報データの必須フィールドが不足: {e}")
    
    def _get_fallback_cache_data(self, cache_key: str) -> Optional[Dict[str, any]]:
        """
        期限切れでも利用可能なキャッシュデータを取得（フォールバック用）
        
        Args:
            cache_key (str): キャッシュキー
            
        Returns:
            dict: キャッシュされた天気情報、存在しない場合はNone
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
                
                # 期限切れでもデータを返す（フォールバック用）
                fallback_data = self.cache_service.deserialize_data(row['data'])
                fallback_data['source'] = 'fallback_cache'
                
                print("フォールバック用キャッシュデータを使用（期限切れ）")
                return fallback_data
                
        except Exception as e:
            print(f"フォールバックキャッシュ取得エラー: {e}")
            return None
    
    def _get_default_weather(self) -> Dict[str, any]:
        """
        デフォルト天気情報を返す
        
        Returns:
            dict: デフォルト天気情報
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
        
        print("デフォルト天気情報を使用")
        return default_weather
    
    def get_weather_summary(self, lat: float, lon: float) -> str:
        """
        天気情報の要約文字列を取得
        
        Args:
            lat (float): 緯度
            lon (float): 経度
            
        Returns:
            str: 天気要約（例: "晴れ 25°C UV指数3"）
        """
        weather = self.get_current_weather(lat, lon)
        return f"{weather['description']} {weather['temperature']}°C UV指数{weather['uv_index']}"
    
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
        
        # 雨や雪の場合は徒歩に不適
        bad_conditions = ['rain', 'drizzle', 'thunderstorm', 'snow']
        if weather['condition'] in bad_conditions:
            return False
        
        # 極端な気温の場合は徒歩に不適
        temp = weather['temperature']
        if temp < 0 or temp > 35:
            return False
        
        # 強風の場合は徒歩に不適
        if weather['wind_speed'] > 10:
            return False
        
        return True
    
    def get_weather_icon_url(self, icon_code: str) -> str:
        """
        天気アイコンのURLを取得
        
        Args:
            icon_code (str): アイコンコード
            
        Returns:
            str: アイコンURL
        """
        return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    
    def is_default_weather(self, weather_data: Dict) -> bool:
        """
        天気情報がデフォルト天気かどうかを判定
        
        Args:
            weather_data (dict): 天気情報
            
        Returns:
            bool: デフォルト天気の場合True
        """
        return weather_data.get('source') == 'default'
    
    def validate_weather_data(self, weather_data: Dict) -> bool:
        """
        天気情報データの妥当性を検証
        
        Args:
            weather_data (dict): 天気情報
            
        Returns:
            bool: 妥当な場合True
        """
        try:
            # 必須フィールドの存在確認
            required_fields = ['temperature', 'condition', 'description', 'uv_index']
            for field in required_fields:
                if field not in weather_data:
                    return False
            
            # 気温の範囲確認（-50°C〜60°C）
            temp = float(weather_data['temperature'])
            if not (-50 <= temp <= 60):
                return False
            
            # UV指数の範囲確認（0〜15）
            uv = float(weather_data['uv_index'])
            if not (0 <= uv <= 15):
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False


# 使用例とテスト用コード
if __name__ == '__main__':
    """
    WeatherServiceのテスト実行
    """
    print("WeatherService テスト実行")
    print("=" * 40)
    
    # WeatherServiceインスタンス作成
    weather_service = WeatherService()
    
    # 東京駅の座標
    tokyo_lat, tokyo_lon = 35.6812, 139.7671
    
    # 天気情報取得テスト
    print("1. 現在の天気情報取得:")
    weather = weather_service.get_current_weather(tokyo_lat, tokyo_lon)
    print(f"   天気: {weather['description']}")
    print(f"   気温: {weather['temperature']}°C (体感: {weather['feels_like']}°C)")
    print(f"   UV指数: {weather['uv_index']}")
    print(f"   湿度: {weather['humidity']}%")
    print(f"   ソース: {weather['source']}")
    
    # 天気要約テスト
    print("\n2. 天気要約:")
    summary = weather_service.get_weather_summary(tokyo_lat, tokyo_lon)
    print(f"   要約: {summary}")
    
    # 徒歩適性判定テスト
    print(f"\n3. 徒歩適性判定: {weather_service.is_good_weather_for_walking(tokyo_lat, tokyo_lon)}")
    
    # デフォルト天気判定テスト
    print(f"4. デフォルト天気判定: {weather_service.is_default_weather(weather)}")
    
    # データ妥当性検証テスト
    print(f"5. データ妥当性検証: {weather_service.validate_weather_data(weather)}")
    
    # アイコンURL取得テスト
    print(f"\n6. 天気アイコンURL: {weather_service.get_weather_icon_url(weather['icon'])}")
    
    print("\nテスト完了")