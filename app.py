#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lunch Roulette - メインアプリケーション
東京エリアのランチスポット発見Webサービス

このアプリケーションは以下の機能を提供します:
- IPアドレスベースの位置情報検出
- リアルタイム天気情報の取得
- 近くのレストラン検索とランダム推薦
- PythonAnywhere無料プラン対応
"""

from flask import Flask, render_template, request, jsonify
import os
import logging
from database import init_database
from cache_service import CacheService
from error_handler import ErrorHandler

# Flaskアプリケーションの初期化
app = Flask(__name__)

# 設定
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DATABASE'] = 'cache.db'

# デバッグモード（本番環境では無効にする）
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# キャッシュサービスの初期化
cache_service = CacheService(db_path=app.config['DATABASE'])

# エラーハンドラーの初期化
error_handler = ErrorHandler()

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def init_db():
    """
    SQLiteキャッシュデータベースを初期化
    アプリケーション起動時に実行される
    """
    return init_database(app.config['DATABASE'])


@app.route('/')
def index():
    """
    メインページのルート
    位置情報と天気情報を表示し、ルーレット機能を提供
    
    Returns:
        str: レンダリングされたHTMLテンプレート
    """
    try:
        # 必要なサービスクラスをインポート
        from location_service import LocationService
        from weather_service import WeatherService
        
        # サービスインスタンスを作成
        location_service = LocationService(cache_service)
        weather_service = WeatherService(cache_service=cache_service)
        
        # クライアントのIPアドレスを取得
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if client_ip and ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()
        
        print(f"クライアントIP: {client_ip}")
        
        # 位置情報を取得
        location_data = location_service.get_location_from_ip(client_ip)
        
        # 天気情報を取得
        weather_data = weather_service.get_current_weather(
            location_data['latitude'], 
            location_data['longitude']
        )
        
        # テンプレートに渡すデータを準備
        template_data = {
            'location': location_data,
            'weather': weather_data,
            'weather_icon_url': weather_service.get_weather_icon_url(weather_data['icon']),
            'is_default_location': location_service.is_default_location(location_data),
            'is_default_weather': weather_service.is_default_weather(weather_data),
            'weather_summary': weather_service.get_weather_summary(
                location_data['latitude'], 
                location_data['longitude']
            ),
            'is_good_walking_weather': weather_service.is_good_weather_for_walking(
                location_data['latitude'], 
                location_data['longitude']
            )
        }
        
        print(f"メインページ表示: {location_data['city']}, {weather_data['description']}")
        
        return render_template('index.html', **template_data)
        
    except Exception as e:
        # エラーハンドリング：エラー時はデフォルト情報でページを表示
        app.logger.error(f'メインページ表示でエラーが発生: {str(e)}')
        
        # エラーハンドラーでエラー情報を処理
        error_info = error_handler.handle_location_error(e, fallback_available=True)
        
        # デフォルトデータでページを表示
        default_data = {
            'location': {
                'city': '東京',
                'region': '東京都',
                'latitude': 35.6812,
                'longitude': 139.7671,
                'source': 'default'
            },
            'weather': {
                'temperature': 20.0,
                'description': '晴れ',
                'uv_index': 3.0,
                'icon': '01d',
                'source': 'default'
            },
            'weather_icon_url': 'https://openweathermap.org/img/wn/01d@2x.png',
            'is_default_location': True,
            'is_default_weather': True,
            'weather_summary': '晴れ 20°C UV指数3',
            'is_good_walking_weather': True,
            'error_message': error_info  # エラーメッセージを追加
        }
        
        return render_template('index.html', **default_data)


@app.route('/roulette', methods=['POST'])
def roulette():
    """
    レストランルーレットのエンドポイント
    ランダムなレストラン推薦を返す
    
    Returns:
        dict: レストラン情報のJSONレスポンス
    """
    try:
        # 必要なサービスクラスをインポート
        from location_service import LocationService
        from weather_service import WeatherService
        from restaurant_service import RestaurantService
        from restaurant_selector import RestaurantSelector
        from distance_calculator import DistanceCalculator
        
        # サービスインスタンスを作成
        location_service = LocationService(cache_service)
        weather_service = WeatherService(cache_service=cache_service)
        restaurant_service = RestaurantService(cache_service=cache_service)
        distance_calculator = DistanceCalculator(error_handler)
        restaurant_selector = RestaurantSelector(distance_calculator, error_handler)
        
        # リクエストデータを取得
        request_data = request.get_json() or {}
        
        # 位置情報を取得（リクエストから、またはIPアドレスから）
        if 'latitude' in request_data and 'longitude' in request_data:
            # リクエストに位置情報が含まれている場合
            user_lat = float(request_data['latitude'])
            user_lon = float(request_data['longitude'])
            print(f"リクエストから位置情報を取得: {user_lat}, {user_lon}")
        else:
            # IPアドレスから位置情報を取得
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            if client_ip and ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            location_data = location_service.get_location_from_ip(client_ip)
            user_lat = location_data['latitude']
            user_lon = location_data['longitude']
            print(f"IPアドレスから位置情報を取得: {user_lat}, {user_lon}")
        
        # 天気情報を取得（レスポンスに含めるため）
        weather_data = weather_service.get_current_weather(user_lat, user_lon)
        
        # レストラン検索を実行（半径1km、ランチ予算≤¥1,200）
        restaurants = restaurant_service.search_lunch_restaurants(user_lat, user_lon, radius=1)
        
        # レストランが見つからない場合
        if not restaurants:
            # レストラン未発見エラーを処理
            no_restaurant_error = ValueError("近くにレストランが見つかりませんでした")
            error_info = error_handler.handle_restaurant_error(no_restaurant_error, fallback_available=False)
            
            return jsonify({
                'success': False,
                'error_info': error_info,
                'message': error_info['message'],
                'suggestion': error_info['suggestion'],
                'weather': {
                    'description': weather_data['description'],
                    'temperature': weather_data['temperature'],
                    'is_good_walking_weather': weather_service.is_good_weather_for_walking(user_lat, user_lon)
                }
            })
        
        # ランダムにレストランを選択し、距離情報を統合
        selected_restaurant = restaurant_selector.select_random_restaurant(restaurants, user_lat, user_lon)
        
        if not selected_restaurant:
            # レストラン選択エラーを処理
            selection_error = ValueError("レストラン選択中にエラーが発生しました")
            error_info = error_handler.handle_restaurant_error(selection_error, fallback_available=False)
            
            return jsonify({
                'success': False,
                'error_info': error_info,
                'message': error_info['message'],
                'suggestion': error_info['suggestion'],
                'weather': {
                    'description': weather_data['description'],
                    'temperature': weather_data['temperature'],
                    'is_good_walking_weather': weather_service.is_good_weather_for_walking(user_lat, user_lon)
                }
            })
        
        # 成功レスポンスを生成
        response_data = {
            'success': True,
            'restaurant': {
                'id': selected_restaurant['id'],
                'name': selected_restaurant['name'],
                'genre': selected_restaurant['genre'],
                'address': selected_restaurant['address'],
                'budget_display': selected_restaurant['display_info']['budget_display'],
                'photo_url': selected_restaurant['display_info']['photo_url'],
                'hotpepper_url': selected_restaurant['display_info']['hotpepper_url'],
                'map_url': selected_restaurant['display_info']['map_url'],
                'summary': selected_restaurant['display_info']['summary'],
                'catch': selected_restaurant.get('catch', ''),
                'access': selected_restaurant['display_info']['access_display'],
                'hours': selected_restaurant['display_info']['hours_display']
            },
            'distance': {
                'distance_km': selected_restaurant['distance_info']['distance_km'],
                'distance_display': selected_restaurant['distance_info']['distance_display'],
                'walking_time_minutes': selected_restaurant['distance_info']['walking_time_minutes'],
                'time_display': selected_restaurant['distance_info']['time_display']
            },
            'weather': {
                'description': weather_data['description'],
                'temperature': weather_data['temperature'],
                'uv_index': weather_data['uv_index'],
                'is_good_walking_weather': weather_service.is_good_weather_for_walking(user_lat, user_lon),
                'icon': weather_data['icon']
            },
            'search_info': {
                'total_restaurants_found': len(restaurants),
                'search_radius_km': 1,
                'max_budget': restaurant_service.LUNCH_BUDGET_LIMIT,
                'user_location': {
                    'latitude': user_lat,
                    'longitude': user_lon
                }
            }
        }
        
        print(f"ルーレット成功: {selected_restaurant['name']} ({selected_restaurant['distance_info']['distance_display']})")
        
        return jsonify(response_data)
        
    except ValueError as e:
        # 入力値エラー
        app.logger.error(f'ルーレット処理で入力値エラー: {str(e)}')
        error_info = error_handler.handle_location_error(e, fallback_available=False)
        
        return jsonify({
            'error': True,
            'error_info': error_info,
            'message': error_info['message'],
            'suggestion': error_info['suggestion']
        }), 400
        
    except Exception as e:
        # その他のエラー
        app.logger.error(f'ルーレット処理で予期しないエラー: {str(e)}')
        
        # 汎用エラーハンドリング
        from error_handler import ErrorType
        error_type, error_info = error_handler.handle_api_error('roulette', e, fallback_available=False)
        user_message = error_handler.create_user_friendly_message(error_info)
        
        return jsonify({
            'error': True,
            'error_info': user_message,
            'message': user_message['message'],
            'suggestion': user_message['suggestion']
        }), 500


@app.errorhandler(404)
def not_found_error(error):
    """404エラーハンドラー"""
    return jsonify({'error': True, 'message': 'ページが見つかりません'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500エラーハンドラー"""
    return jsonify({'error': True, 'message': 'サーバー内部エラーが発生しました'}), 500


# アプリケーション起動時の初期化
if __name__ == '__main__':
    # データベース初期化
    init_db()
    
    # 開発サーバー起動
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )