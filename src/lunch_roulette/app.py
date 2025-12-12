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
    
    【このエンドポイントがやること】
    「ルーレットを回す」ボタンが押された時に実行されます。
    まるでルーレットを回すように、条件に合ったお店の中から
    ランダムに1つのお店を選んで、詳細情報を返します。
    
    【処理の流れ（全体像）】
    ┌─────────────┐
    │1. 現在地を確認  │
    └────┬────────┘
         ↓
    ┌─────────────┐
    │2. お店を検索   │（半径1km、予算1200円以下など）
    └────┬────────┘
         ↓
    ┌─────────────┐
    │3. ランダムに選ぶ│（ルーレット！）
    └────┬────────┘
         ↓
    ┌─────────────┐
    │4. 距離を計算   │（徒歩〇分）
    └────┬────────┘
         ↓
    ┌─────────────┐
    │5. 結果を返す   │（JSON形式でブラウザへ）
    └─────────────┘
    
    【返すデータ】
    - 成功時: お店の情報（名前、住所、予算、写真、距離、徒歩時間など）
    - 失敗時: エラーメッセージ（お店が見つからない、など）
    
    Returns:
        JSON形式のデータ（JavaScriptが受け取ってブラウザに表示）
    """
    try:
        # ========================================
        # ステップ1: 必要な部品（サービスクラス）を準備
        # ========================================
        # それぞれの部品（モジュール）を読み込む
        from .services.location_service import LocationService      # 位置情報取得部品
        from .services.weather_service import WeatherService        # 天気情報取得部品
        from .services.restaurant_service import RestaurantService  # レストラン検索部品
        from .utils.restaurant_selector import RestaurantSelector   # レストラン選択部品（ルーレット）
        from .utils.distance_calculator import DistanceCalculator   # 距離計算部品

        # 各部品のインスタンスを作成（実際に使えるようにする）
        # インスタンス = クラスを実際に使える状態にしたもの
        location_service = LocationService(cache_service)
        weather_service = WeatherService(cache_service=cache_service)
        restaurant_service = RestaurantService(cache_service=cache_service)
        distance_calculator = DistanceCalculator(error_handler)
        restaurant_selector = RestaurantSelector(distance_calculator, error_handler)

        # ========================================
        # ステップ2: ブラウザから送られてきたデータを取得
        # ========================================
        # ユーザーがブラウザで指定した条件（位置、予算、ジャンルなど）を受け取る
        # JavaScriptから送られてくるJSON形式のデータを辞書型に変換
        request_data = request.get_json() or {}

        # ========================================
        # ステップ3: 検索条件を整理する
        # ========================================
        # 【検索条件の種類】
        # 1. location_mode: 現在地モード or エリア指定モード
        # 2. budget_code: 予算（例: B010 = 1000円以下）
        # 3. lunch_filter: ランチ営業しているか（1=Yes, 0=No）
        # 4. genre_code: ジャンル（例: G001 = 居酒屋）
        
        location_mode = request_data.get('location_mode', 'current')  # デフォルトは現在地モード
        budget_code = request_data.get('budget_code', None)  # Noneなら予算制限なし
        lunch_filter = request_data.get('lunch', 1)  # デフォルトはランチ営業中のみ
        genre_code = request_data.get('genre_code', None)  # Noneなら全ジャンル
        
        # 空文字列が送られてきた場合はNoneに変換
        if genre_code == '':
            genre_code = None
        
        # ========================================
        # ステップ4: 検索モードに応じて処理を分岐
        # ========================================
        # location_mode に応じて2つの処理に分かれます
        
        if location_mode == 'area':
            # ===== パターンA: エリア指定モード =====
            # 「渋谷周辺」「新宿周辺」のようにエリアで検索
            # 現在地が不明な場合や、別のエリアを探したい時に使います
            
            middle_area_code = request_data.get('middle_area_code')
            
            # エリアコードが指定されていない場合はエラー
            if not middle_area_code:
                return jsonify({
                    'success': False,
                    'message': 'エリアを選択してください。',
                    'suggestion': 'エリア選択から検索したいエリアを指定してください。'
                }), 400
            
            print(f"エリア指定モード: middle_area={middle_area_code}, 予算={budget_code or 'すべて'}, ランチ={lunch_filter}, ジャンル={genre_code or 'すべて'}")
            
            # エリアモードでは天気情報は取得しない
            # 理由: エリアが広すぎて、どの地点の天気か特定できないため
            # デフォルトの天気情報（晴れ、20度）を使用
            weather_data = {
                'temperature': 20.0,
                'description': '晴れ',
                'uv_index': 3.0,
                'condition': 'sunny',
                'source': 'default'
            }
            
            # エリアベースでレストランを検索
            restaurants = restaurant_service.search_restaurants(
                middle_area=middle_area_code,  # エリアコード（例: Y055 = 渋谷）
                budget_code=budget_code,       # 予算コード
                lunch=lunch_filter,            # ランチ営業フィルタ
                genre_code=genre_code          # ジャンルコード
            )
            
            # エリアモードでは距離計算ができない
            # 理由: ユーザーの正確な位置がわからないため
            user_lat = None
            user_lon = None
            
        elif location_mode == 'current':
            # ===== パターンB: 現在地モード（GPSや位置情報を使う）=====
            # 「今いる場所の近く」を探す場合に使います
            
            # 徒歩時間の上限（分）を取得（デフォルト: 10分）
            # 例: 10分なら徒歩10分以内のお店だけを検索
            max_walking_time = request_data.get('max_walking_time_min', 10)
            
            # ユーザーの現在位置（緯度・経度）を取得する
            # 2つの方法があります:
            #   方法1: ブラウザのGPS機能から取得（精度が高い）
            #   方法2: IPアドレスから推測（精度は低いが、GPSなしでも使える）
            
            if 'latitude' in request_data and 'longitude' in request_data:
                # 方法1: ブラウザのGPS機能から送られてきた位置情報を使用
                # JavaScriptのgeolocation APIで取得した座標
                user_lat = float(request_data['latitude'])   # 緯度（北緯35度など）
                user_lon = float(request_data['longitude'])  # 経度（東経139度など）
                print(f"ブラウザのGPSから位置情報を取得: 緯度{user_lat}, 経度{user_lon}")
            else:
                # 方法2: IPアドレスから位置情報を推測
                # GPS機能が使えない場合の代替手段
                # 精度は低い（市区町村レベル）が、おおよその位置はわかる
                client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
                # プロキシ経由の場合、複数のIPが含まれるので最初のものを使用
                if client_ip and ',' in client_ip:
                    client_ip = client_ip.split(',')[0].strip()

                location_data = location_service.get_location_from_ip(client_ip)
                user_lat = location_data['latitude']
                user_lon = location_data['longitude']
                print(f"IPアドレスから位置情報を取得: 緯度{user_lat}, 経度{user_lon}")
            
            print(f"現在地モード: 徒歩{max_walking_time}分以内, 予算={budget_code or 'すべて'}, ランチ={lunch_filter}, ジャンル={genre_code or 'すべて'}")
            
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
            # - ジャンルコード指定（ある場合）
            restaurants = restaurant_service.search_restaurants(
                user_lat, 
                user_lon, 
                radius=search_range,
                budget_code=budget_code,
                lunch=lunch_filter,
                genre_code=genre_code
            )
        
        print(f"検索結果: {len(restaurants)}件のレストランが見つかりました")

        # ===== ステップ6: レストランが見つからなかった場合の処理 =====
        if not restaurants:
            # 検索条件に応じたメッセージを作成
            conditions = []
            if genre_code:
                # ジャンル名を取得（genres.jsonから）
                import json
                genres_file = package_dir / 'data' / 'genres.json'
                try:
                    with open(genres_file, 'r', encoding='utf-8') as f:
                        genres_data = json.load(f)
                    genre_name = next((g['name'] for g in genres_data['genres'] if g['code'] == genre_code), 'ジャンル指定')
                    conditions.append(f'「{genre_name}」')
                except:
                    conditions.append('指定されたジャンル')
            
            if budget_code:
                budget_names = {
                    'B009': '〜500円',
                    'B010': '〜1000円',
                    'B011': '〜1500円',
                    'B001': '〜2000円',
                    'B002': '〜3000円'
                }
                budget_name = budget_names.get(budget_code, '指定された予算')
                conditions.append(f'予算{budget_name}')
            
            # 現在地モードの場合のみ徒歩時間を追加
            if location_mode == 'current':
                conditions.append(f'徒歩{max_walking_time}分以内')
            
            conditions_text = '、'.join(conditions)
            message = f'{conditions_text}の条件に該当するお店が見つかりませんでした。'
            suggestion = '条件を緩めて再度お試しください。'

            # エラーメッセージをJSON形式で返す
            response = {
                'success': False,
                'message': message,
                'suggestion': suggestion
            }
            
            # 現在地モードの場合は天気情報も含める
            if location_mode == 'current':
                response['weather'] = {
                    'description': weather_data['description'],
                    'temperature': weather_data['temperature'],
                    'is_good_walking_weather': weather_service.is_good_weather_for_walking(user_lat, user_lon)
                }
            
            return jsonify(response)

        # ===== ステップ7: 見つかったレストランの中からランダムに1つ選ぶ =====
        # エリアモードと現在地モードで処理を分岐
        if location_mode == 'area':
            # エリアモード: 距離計算なしでランダム選択
            import random
            selected = random.choice(restaurants)
            
            # display_info を生成（距離情報なし）
            budget_avg = selected.get('budget_average', 0)
            if budget_avg <= 0:
                budget_display = '予算不明'
            elif budget_avg <= 500:
                budget_display = '〜500円'
            elif budget_avg <= 1000:
                budget_display = '〜1000円'
            elif budget_avg <= 1500:
                budget_display = '〜1500円'
            elif budget_avg <= 2000:
                budget_display = '〜2000円'
            else:
                budget_display = f'{budget_avg}円〜'
            
            selected_restaurant = selected.copy()
            selected_restaurant['display_info'] = {
                'budget_display': budget_display,
                'photo_url': selected.get('photo', ''),
                'hotpepper_url': selected.get('urls', {}).get('pc', ''),
                'map_url': f"https://www.google.com/maps/search/?api=1&query={selected.get('lat', 0)},{selected.get('lng', 0)}",
                'summary': selected.get('catch', selected.get('name', '')),
                'access_display': selected.get('access', '').strip() or 'アクセス情報なし',
                'hours_display': selected.get('open', '').strip() or '営業時間情報なし'
            }
        else:
            # 現在地モード: 距離計算ありでランダム選択
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

            response = {
                'success': False,
                'error_info': error_info,
                'message': error_info['message'],
                'suggestion': error_info['suggestion']
            }
            
            # 現在地モードの場合は天気情報も含める
            if location_mode == 'current':
                response['weather'] = {
                    'description': weather_data['description'],
                    'temperature': weather_data['temperature'],
                    'is_good_walking_weather': weather_service.is_good_weather_for_walking(user_lat, user_lon)
                }
            
            return jsonify(response)

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
            
            # 検索情報（参考データ）
            'search_info': {
                'total_restaurants_found': len(restaurants),   # 見つかったレストランの総数
                'max_budget': restaurant_service.LUNCH_BUDGET_LIMIT  # 最大予算（1200円）
            }
        }
        
        # 現在地モードの場合のみ距離情報と天気情報を追加
        if location_mode == 'current':
            response_data['distance'] = {
                'distance_km': selected_restaurant['distance_info']['distance_km'],              # 距離（km）
                'distance_display': selected_restaurant['distance_info']['distance_display'],    # 距離表示用
                'walking_time_minutes': selected_restaurant['distance_info']['walking_time_minutes'],  # 徒歩時間（分）
                'time_display': selected_restaurant['distance_info']['time_display']             # 時間表示用
            }
            
            response_data['weather'] = {
                'description': weather_data['description'],    # 天気の説明
                'temperature': weather_data['temperature'],    # 気温
                'uv_index': weather_data['uv_index'],          # UV指数
                'is_good_walking_weather': weather_service.is_good_weather_for_walking(user_lat, user_lon),  # 歩くのに良い天気か
                'icon': weather_data['icon']                   # 天気アイコン
            }
            
            response_data['search_info']['search_radius_km'] = 1  # 検索半径（1km）
            response_data['search_info']['user_location'] = {
                'latitude': user_lat,                      # ユーザーの緯度
                'longitude': user_lon                      # ユーザーの経度
            }
            
            print(f"ルーレット成功（現在地モード）: {selected_restaurant['name']} ({selected_restaurant['distance_info']['distance_display']})")
        else:
            print(f"ルーレット成功（エリアモード）: {selected_restaurant['name']}")


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


@app.route('/api/genres', methods=['GET'])
def get_genres():
    """
    ジャンルマスタデータを取得するAPIエンドポイント
    
    フロントエンドでジャンル選択UIを表示するために使用します。
    genres.jsonファイルからジャンルデータを読み込んで返します。
    
    Returns:
        JSON形式のデータ:
        - success: 成功フラグ
        - genres: ジャンルリスト
    """
    try:
        import json
        
        # ジャンルマスタファイルのパスを取得
        genres_file = package_dir / 'data' / 'genres.json'
        
        # ファイルが存在しない場合はエラー
        if not genres_file.exists():
            return jsonify({
                'success': False,
                'error': 'ジャンルマスタファイルが見つかりません'
            }), 404
        
        # ジャンルマスタファイルを読み込み
        with open(genres_file, 'r', encoding='utf-8') as f:
            genres_data = json.load(f)
        
        return jsonify({
            'success': True,
            'genres': genres_data['genres']
        })
    
    except Exception as e:
        app.logger.error(f'ジャンルマスタ取得でエラー: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'ジャンルマスタの取得に失敗しました'
        }), 500


@app.route('/api/areas', methods=['GET'])
def get_areas():
    """
    エリアマスタデータを取得するAPIエンドポイント
    
    フロントエンドでエリア選択UIを表示するために使用します。
    areas_tokyo.jsonファイルからエリアデータを読み込んで返します。
    
    Returns:
        JSON形式のデータ:
        - success: 成功フラグ
        - areas: エリアリスト（large_area配下のmiddle_areas）
    """
    try:
        import json
        
        # エリアマスタファイルのパスを取得
        areas_file = package_dir / 'data' / 'areas_tokyo.json'
        
        # ファイルが存在しない場合はエラー
        if not areas_file.exists():
            return jsonify({
                'success': False,
                'error': 'エリアマスタファイルが見つかりません'
            }), 404
        
        # エリアマスタファイルを読み込み
        with open(areas_file, 'r', encoding='utf-8') as f:
            areas_data = json.load(f)
        
        # middle_areasを取得（データ構造: { "large_area_code": "Z011", "large_area_name": "東京", "middle_areas": [...] }）
        middle_areas = areas_data['middle_areas']
        
        return jsonify({
            'success': True,
            'areas': middle_areas
        })
    
    except Exception as e:
        app.logger.error(f'エリアマスタ取得でエラー: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'エリアマスタの取得に失敗しました'
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
