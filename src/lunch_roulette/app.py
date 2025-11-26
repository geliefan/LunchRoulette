#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lunch Roulette - メインアプリケーション
東京エリアのランチスポット発見Webサービス

このアプリケーションの主な機能:
1. IPアドレスから現在地を自動検出
2. 現在地の天気情報をリアルタイムで表示
3. 半径1km以内のランチ店（予算1200円以内）を検索
4. ランダムにお店を選んで推薦（ルーレット機能）
5. 徒歩での距離と所要時間を表示

利用シーン:
- 「今日のランチ、どこにしようかな？」と迷った時
- 新しいお店を開拓したい時
- 天気を考慮してお店を選びたい時
"""

# ===== 必要なライブラリの読み込み =====
from flask import Flask, render_template, request, jsonify  # Webアプリケーションフレームワーク
import os       # 環境変数の取得など、OS関連の機能
import logging  # ログ（記録）を残すための機能
from pathlib import Path  # ファイルパスを扱いやすくする機能

# 自作のモジュールを読み込み
from .models.database import init_database          # データベース初期化機能
from .services.cache_service import CacheService    # キャッシュ（一時保存）機能
from .utils.error_handler import ErrorHandler       # エラー処理機能

# ===== アプリケーションの初期設定 =====

# このファイルがあるディレクトリ（フォルダ）のパスを取得
package_dir = Path(__file__).parent

# Flaskアプリケーションを作成
# Flask = Pythonで簡単にWebサイトを作れるフレームワーク
app = Flask(__name__,
           static_folder=str(package_dir / 'static'),      # CSS、JavaScriptなどのファイルの場所
           template_folder=str(package_dir / 'templates'))  # HTMLファイルの場所

# アプリケーションの設定
# SECRET_KEY = セッション情報を暗号化するための秘密の鍵
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
# DATABASE = キャッシュデータを保存するデータベースファイル名
app.config['DATABASE'] = 'cache.db'

# デバッグモード（開発中はTrue、本番環境ではFalse）
# デバッグモード = エラーの詳細情報を画面に表示する開発者向けモード
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# ===== 共通サービスの初期化 =====

# キャッシュサービス = 同じデータを何度もAPIから取得しないよう、一時的に保存する仕組み
# 例: 5分以内に同じ場所の天気を調べた場合、前回の結果を再利用
cache_service = CacheService(db_path=app.config['DATABASE'])

# エラーハンドラー = エラーが発生した時に適切な対処をする仕組み
error_handler = ErrorHandler()

# ログ設定 = アプリケーションの動作を記録する設定
# ログレベル INFO = 通常の動作情報を記録（デバッグ情報よりは少なめ）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # ログの表示形式
)


def init_db():
    """
    データベースを初期化する関数
    
    アプリケーション起動時に1回だけ実行されます。
    キャッシュデータを保存するためのデータベースファイル（cache.db）を作成します。
    
    データベースとは:
        データを整理して保存するための仕組み。
        このアプリでは、APIから取得したデータを一時的に保存するために使用。
    """
    return init_database(app.config['DATABASE'])


@app.route('/')
def index():
    """
    メインページを表示する関数（トップページ）
    
    このページでは:
    1. ユーザーの現在地を自動検出
    2. その場所の天気情報を取得
    3. 画面に位置情報と天気を表示
    4. 「ルーレットを回す」ボタンを表示
    
    処理の流れ:
    1. ユーザーのIPアドレスから位置情報を取得
    2. 位置情報（緯度・経度）を使って天気APIを呼び出し
    3. 取得したデータをHTMLテンプレートに渡して画面を表示
    
    エラーが発生した場合:
    - 東京のデフォルト情報を表示
    
    Returns:
        HTMLページ（ユーザーのブラウザに表示される画面）
    """
    try:
        # ===== ステップ1: 必要なサービスクラスを準備 =====
        # サービスクラス = 特定の機能をまとめたプログラムの部品
        from .services.location_service import LocationService    # 位置情報を取得する部品
        from .services.weather_service import WeatherService      # 天気情報を取得する部品

        # サービスクラスのインスタンスを作成（実際に使えるようにする）
        location_service = LocationService(cache_service)
        weather_service = WeatherService(cache_service=cache_service)

        # ===== ステップ2: ユーザーのIPアドレスを取得 =====
        # IPアドレス = インターネット上の住所のようなもの
        # これを使って、ユーザーが今どこにいるかを推測します
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        # プロキシ経由の場合、複数のIPが含まれるので最初のものを使用
        if client_ip and ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()

        print(f"クライアントIP: {client_ip}")

        # ===== ステップ3: IPアドレスから位置情報を取得 =====
        # 位置情報 = 緯度、経度、都市名など
        location_data = location_service.get_location_from_ip(client_ip)

        # ===== ステップ4: 位置情報から天気情報を取得 =====
        # 緯度・経度を使って、その場所の現在の天気を調べます
        weather_data = weather_service.get_current_weather(
            location_data['latitude'],   # 緯度
            location_data['longitude']   # 経度
        )

        # ===== ステップ5: 画面に表示するデータを整理 =====
        # HTMLテンプレートに渡すデータをまとめます
        template_data = {
            'location': location_data,  # 位置情報（都市名、緯度・経度など）
            'weather': weather_data,    # 天気情報（気温、天気状況など）
            'weather_icon_emoji': weather_service.get_weather_icon_emoji(weather_data['condition']),  # 天気アイコン
            'is_default_location': location_service.is_default_location(location_data),  # デフォルト位置か
            'is_default_weather': weather_service.is_default_weather(weather_data),      # デフォルト天気か
            'weather_summary': weather_service.get_weather_summary(                       # 天気の要約文
                location_data['latitude'],
                location_data['longitude']
            ),
            'is_good_walking_weather': weather_service.is_good_weather_for_walking(      # 歩くのに良い天気か
                location_data['latitude'],
                location_data['longitude']
            )
        }

        print(f"メインページ表示: {location_data['city']}, {weather_data['description']}")

        # ===== ステップ6: HTMLページを生成して返す =====
        return render_template('index.html', **template_data)

    except Exception as e:
        # ===== エラーが発生した場合の処理 =====
        # 何か問題が起きても、アプリが止まらないようにデフォルトの情報を表示します
        
        app.logger.error(f'メインページ表示でエラーが発生: {str(e)}')

        # エラーハンドラーでエラー情報を整理
        error_info = error_handler.handle_location_error(e, fallback_available=True)

        # デフォルトデータ（東京の標準的な情報）を準備
        default_data = {
            'location': {
                'city': '東京',
                'region': '東京都',
                'latitude': 35.6812,    # 東京駅の緯度
                'longitude': 139.7671,  # 東京駅の経度
                'source': 'default'     # デフォルト値であることを示す
            },
            'weather': {
                'temperature': 20.0,     # 20度
                'description': '晴れ',
                'uv_index': 3.0,         # UV指数
                'condition': 'sunny',
                'source': 'default'
            },
            'weather_icon_emoji': '☀️',
            'is_default_location': True,
            'is_default_weather': True,
            'weather_summary': '晴れ 20°C UV指数3',
            'is_good_walking_weather': True,
            'error_message': error_info
        }

        # デフォルトデータでページを表示
        return render_template('index.html', **default_data)


@app.route('/roulette', methods=['POST'])
def roulette():
    """
    ランチルーレット機能（レストランをランダムに選ぶ機能）
    
    「ルーレットを回す」ボタンが押された時に実行されます。
    
    処理の流れ:
    1. ユーザーの現在地を確認
    2. 現在地から半径1km以内のレストランを検索
    3. 予算1200円以下のお店に絞り込み
    4. その中からランダムに1つのお店を選ぶ
    5. お店までの距離と徒歩時間を計算
    6. 結果をJSON形式で返す（JavaScriptが受け取る）
    
    Returns:
        JSON形式のデータ:
        - 成功時: レストラン情報、距離、天気情報
        - 失敗時: エラーメッセージ
    """
    try:
        # ===== ステップ1: 必要な部品（サービスクラス）を準備 =====
        from .services.location_service import LocationService      # 位置情報取得
        from .services.weather_service import WeatherService        # 天気情報取得
        from .services.restaurant_service import RestaurantService  # レストラン検索
        from .utils.restaurant_selector import RestaurantSelector   # レストラン選択
        from .utils.distance_calculator import DistanceCalculator   # 距離計算

        # 各サービスのインスタンスを作成（実際に使えるようにする）
        location_service = LocationService(cache_service)
        weather_service = WeatherService(cache_service=cache_service)
        restaurant_service = RestaurantService(cache_service=cache_service)
        distance_calculator = DistanceCalculator(error_handler)
        restaurant_selector = RestaurantSelector(distance_calculator, error_handler)

        # ===== ステップ2: ブラウザから送られてきたデータを取得 =====
        # JavaScriptから送られてくるJSON形式のデータを受け取る
        request_data = request.get_json() or {}

        # ===== ステップ3: ユーザーの位置情報を取得 =====
        # 2つの方法で位置情報を取得できます
        if 'latitude' in request_data and 'longitude' in request_data:
            # 方法1: ブラウザのGPS機能から送られてきた位置情報を使用
            user_lat = float(request_data['latitude'])   # 緯度
            user_lon = float(request_data['longitude'])  # 経度
            print(f"ブラウザのGPSから位置情報を取得: 緯度{user_lat}, 経度{user_lon}")
        else:
            # 方法2: IPアドレスから位置情報を推測
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            if client_ip and ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()

            location_data = location_service.get_location_from_ip(client_ip)
            user_lat = location_data['latitude']
            user_lon = location_data['longitude']
            print(f"IPアドレスから位置情報を取得: 緯度{user_lat}, 経度{user_lon}")

        # ===== ステップ3.5: 検索条件パラメータを取得 =====
        # 徒歩時間（分）を取得（デフォルト: 10分）
        max_walking_time = request_data.get('max_walking_time_min', 10)
        
        # 予算コードを取得（デフォルト: None = すべての予算）
        budget_code = request_data.get('budget_code', None)
        
        # ランチフィルタを取得（デフォルト: 1 = ランチあり）
        lunch_filter = request_data.get('lunch', 1)
        
        print(f"検索条件: 徒歩{max_walking_time}分以内, 予算={budget_code or 'すべて'}, ランチ={lunch_filter}")

        # ===== ステップ4: 現在の天気情報を取得 =====
        # 結果に天気情報も含めるため、天気APIを呼び出す
        weather_data = weather_service.get_current_weather(user_lat, user_lon)

        # ===== ステップ5: 近くのレストランを検索 =====
        # 徒歩時間をrangeコードに変換
        search_range = restaurant_service.walking_time_to_range(max_walking_time)
        
        # 条件:
        # - 徒歩時間内（rangeコードに変換）
        # - 予算コード指定（ある場合）
        # - ランチフィルタ
        restaurants = restaurant_service.search_restaurants(
            user_lat, 
            user_lon, 
            radius=search_range,
            budget_code=budget_code,
            lunch=lunch_filter
        )
        
        print(f"検索結果: {len(restaurants)}件のレストランが見つかりました")

        # ===== ステップ6: レストランが見つからなかった場合の処理 =====
        if not restaurants:
            # エラー情報を作成
            no_restaurant_error = ValueError("近くにレストランが見つかりませんでした")
            error_info = error_handler.handle_restaurant_error(no_restaurant_error, fallback_available=False)

            # エラーメッセージをJSON形式で返す
            # JSON = JavaScript Object Notation = データをやり取りする標準的な形式
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

        # ===== ステップ7: 見つかったレストランの中からランダムに1つ選ぶ =====
        # restaurant_selector.select_random_restaurant が以下を実行:
        # 1. リストからランダムに1つのレストランを選択
        # 2. そのレストランまでの距離と徒歩時間を計算
        # 3. 距離情報をレストラン情報に追加
        selected_restaurant = restaurant_selector.select_random_restaurant(restaurants, user_lat, user_lon)

        # ===== ステップ8: レストラン選択に失敗した場合の処理 =====
        if not selected_restaurant:
            # 何らかの理由で選択に失敗した場合のエラー処理
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

        # ===== ステップ9: 成功時のレスポンスデータを作成 =====
        # ブラウザのJavaScriptに返すデータを整理
        # このデータが画面に表示されます
        response_data = {
            'success': True,  # 成功フラグ
            
            # レストラン情報
            'restaurant': {
                'id': selected_restaurant['id'],              # レストランID
                'name': selected_restaurant['name'],          # 店名
                'genre': selected_restaurant['genre'],        # ジャンル（例: 和食、イタリアン）
                'address': selected_restaurant['address'],    # 住所
                'budget_display': selected_restaurant['display_info']['budget_display'],  # 予算表示
                'photo_url': selected_restaurant['display_info']['photo_url'],            # 写真URL
                'hotpepper_url': selected_restaurant['display_info']['hotpepper_url'],    # ホットペッパーのURL
                'map_url': selected_restaurant['display_info']['map_url'],                # 地図URL
                'summary': selected_restaurant['display_info']['summary'],                # 概要
                'catch': selected_restaurant.get('catch', ''),                            # キャッチコピー
                'access': selected_restaurant['display_info']['access_display'],          # アクセス情報
                'hours': selected_restaurant['display_info']['hours_display']             # 営業時間
            },
            
            # 距離情報
            'distance': {
                'distance_km': selected_restaurant['distance_info']['distance_km'],              # 距離（km）
                'distance_display': selected_restaurant['distance_info']['distance_display'],    # 距離表示用
                'walking_time_minutes': selected_restaurant['distance_info']['walking_time_minutes'],  # 徒歩時間（分）
                'time_display': selected_restaurant['distance_info']['time_display']             # 時間表示用
            },
            
            # 天気情報
            'weather': {
                'description': weather_data['description'],    # 天気の説明
                'temperature': weather_data['temperature'],    # 気温
                'uv_index': weather_data['uv_index'],          # UV指数
                'is_good_walking_weather': weather_service.is_good_weather_for_walking(user_lat, user_lon),  # 歩くのに良い天気か
                'icon': weather_data['icon']                   # 天気アイコン
            },
            
            # 検索情報（参考データ）
            'search_info': {
                'total_restaurants_found': len(restaurants),   # 見つかったレストランの総数
                'search_radius_km': 1,                         # 検索半径（1km）
                'max_budget': restaurant_service.LUNCH_BUDGET_LIMIT,  # 最大予算（1200円）
                'user_location': {
                    'latitude': user_lat,                      # ユーザーの緯度
                    'longitude': user_lon                      # ユーザーの経度
                }
            }
        }

        print(f"ルーレット成功: {selected_restaurant['name']} ({selected_restaurant['distance_info']['distance_display']})")

        # ===== ステップ10: 結果をJSON形式で返す =====
        # このデータがブラウザのJavaScriptに送られ、画面に表示されます
        return jsonify(response_data)

    except ValueError as e:
        # ===== エラー処理1: 入力値エラー =====
        # 緯度・経度の値が不正な場合など
        app.logger.error(f'ルーレット処理で入力値エラー: {str(e)}')
        error_info = error_handler.handle_location_error(e, fallback_available=False)

        # エラーメッセージをJSON形式で返す（HTTPステータスコード400 = Bad Request）
        return jsonify({
            'error': True,
            'error_info': error_info,
            'message': error_info['message'],
            'suggestion': error_info['suggestion']
        }), 400

    except Exception as e:
        # ===== エラー処理2: その他の予期しないエラー =====
        # システムエラーなど、想定外のエラーが発生した場合
        app.logger.error(f'ルーレット処理で予期しないエラー: {str(e)}')

        # 汎用エラーハンドリング
        error_type, error_info = error_handler.handle_api_error('roulette', e, fallback_available=False)
        user_message = error_handler.create_user_friendly_message(error_info)

        # エラーメッセージをJSON形式で返す（HTTPステータスコード500 = Internal Server Error）
        return jsonify({
            'error': True,
            'error_info': user_message,
            'message': user_message['message'],
            'suggestion': user_message['suggestion']
        }), 500


@app.errorhandler(404)
def not_found_error(error):
    """
    404エラー（ページが見つからない）の処理
    
    存在しないURLにアクセスした時に表示されます
    """
    return jsonify({'error': True, 'message': 'ページが見つかりません'}), 404


@app.errorhandler(500)
def internal_error(error):
    """
    500エラー（サーバー内部エラー）の処理
    
    サーバー側で予期しないエラーが発生した時に表示されます
    """
    return jsonify({'error': True, 'message': 'サーバー内部エラーが発生しました'}), 500


# ===== アプリケーション起動処理 =====
if __name__ == '__main__':
    # このファイルを直接実行した時だけ、以下のコードが実行されます
    
    # データベース初期化（キャッシュ用のテーブルを作成）
    init_db()

    # 開発サーバーを起動
    # host='0.0.0.0' = すべてのネットワークインターフェースで待ち受け
    # port = サーバーが使用するポート番号（デフォルトは5000番）
    # debug = デバッグモード（エラーの詳細を表示）
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )
