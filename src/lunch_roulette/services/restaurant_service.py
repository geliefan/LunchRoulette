#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RestaurantService - レストラン情報サービスクラス
Hot Pepper Gourmet APIからレストラン情報を取得する機能を提供

このクラスができること:
1. 指定した場所の近くのレストランを検索（半径1km以内）
2. 予算で絞り込み（ランチ予算1200円以下）
3. レストランの詳細情報を整形
4. キャッシュを使ってAPI呼び出しを節約

使用例:
    service = RestaurantService()
    restaurants = service.search_lunch_restaurants(35.6812, 139.7671)
    print(f"{len(restaurants)}件のランチのお店が見つかりました")
"""

import requests
import os
from typing import Dict, List, Optional
from .cache_service import CacheService


class RestaurantService:
    """
    Hot Pepper Gourmet APIからレストラン情報を取得するサービス

    指定された座標周辺のレストランを検索し、予算でフィルタリングして
    ランチに適したレストランを提供する。
    """

    # ====== 【定数の定義】予算コードとランチ予算の設定 ======
    
    # 予算コードマッピング（Hot Pepper API仕様）
    # Hot Pepper APIでは予算を「B009」「B010」のようなコードで指定します
    # 例: 「B010」は「501〜1000円」を意味する
    # 
    # このマッピングは以下の用途で使われます:
    # 1. APIから返ってきたレストランの予算コードを円に変換
    # 2. 検索時に指定する予算範囲の決定
    # 3. フィルタリング（1200円以下のお店だけ選ぶ）
    BUDGET_CODES = {
        'B009': 500,    # 〜500円（とても安い）
        'B010': 1000,   # 501〜1000円（ワンコイン以上千円以下）
        'B011': 1500,   # 1001〜1500円（普通のランチ価格）
        'B001': 2000,   # 1501〜2000円（ちょっと高めのランチ）
        'B002': 3000,   # 2001〜3000円（高級ランチ）
        'B003': 4000,   # 3001〜4000円
        'B008': 5000,   # 4001〜5000円
        'B004': 7000,   # 5001〜7000円
        'B005': 10000,  # 7001〜10000円
        'B006': 15000,  # 10001〜15000円
        'B012': 20000,  # 15001〜20000円
        'B013': 30000,  # 20001〜30000円
        'B014': 30001   # 30001円以上（超高級店）
    }

    # ランチ予算制限（円）
    # 1200円に設定した理由:
    # - 一般的なサラリーマンの平均ランチ予算が約800-1000円
    # - 少し余裕を持たせて1200円まで許容
    # - これより高いと「ランチ」ではなく「ディナー」扱いになることが多い
    LUNCH_BUDGET_LIMIT = 1200

    def __init__(self, api_key: Optional[str] = None, cache_service: Optional[CacheService] = None):
        """
        RestaurantServiceを初期化
        
        【初期化でやること】
        1. APIキーの取得（引数 > 環境変数の順で確認）
        2. キャッシュサービスの設定
        3. API接続情報の設定（URLとタイムアウト時間）
        4. APIキーがない場合は警告表示

        Args:
            api_key (str, optional): Hot Pepper Gourmet APIキー
                - 指定しない場合は環境変数 HOTPEPPER_API_KEY から取得
            cache_service (CacheService, optional): キャッシュサービス
                - 指定しない場合は新しいCacheServiceインスタンスを作成
        """
        # 1. APIキーの取得（引数で渡されていれば優先、なければ環境変数から）
        self.api_key = api_key or os.getenv('HOTPEPPER_API_KEY')
        
        # 2. キャッシュサービスの設定（API呼び出しを減らして高速化）
        self.cache_service = cache_service or CacheService()
        
        # 3. API接続情報の設定
        self.api_base_url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
        self.timeout = 10  # APIリクエストのタイムアウト（10秒）
        # ※タイムアウトを設定する理由: APIサーバーが応答しない時に永遠に待たないため

        # 4. APIキーの存在確認（ないと検索できないので警告）
        if not self.api_key:
            print("警告: Hot Pepper Gourmet APIキーが設定されていません。")

    def search_restaurants(self, lat: float, lon: float, radius: int = 1, budget_code: str = None, lunch: int = None) -> List[Dict]:
        """
        指定された座標周辺のレストランを検索
        
        【検索処理の流れ - 全10ステップ】
        1. キャッシュキーを生成（同じ検索を繰り返さないため）
        2. キャッシュに保存済みのデータがあれば取得して返す
        3. APIキーがない場合は空のリストを返す
        4. APIリクエストのパラメータを準備
        5. Hot Pepper APIにHTTPリクエストを送信
        6. レスポンスのステータスコードを確認
        7. JSONデータを解析
        8. レストランリストを抽出
        9. データをキャッシュに保存（次回の高速化のため）
        10. レストランリストを返す

        Args:
            lat (float): 緯度（例: 35.6812 = 東京駅付近）
            lon (float): 経度（例: 139.7671 = 東京駅付近）
            radius (int): 検索半径(km)、デフォルトは1km
                - 1km = 徒歩約12〜15分の距離
            budget_code (str, optional): Hot Pepper予算コード（例: "B010"）
                - None の場合は予算フィルタなし
            lunch (int, optional): ランチフィルタ（1=ランチあり、None=指定なし）
                - 1 を指定すると「ランチあり」の店舗のみ検索

        Returns:
            list: レストラン情報のリスト
                - 各レストランは辞書形式で以下の情報を含む:
                  - name: レストラン名
                  - address: 住所
                  - budget: 予算
                  - photo: 写真URL
                  など

        Example:
            >>> restaurant_service = RestaurantService()
            >>> restaurants = restaurant_service.search_restaurants(35.6812, 139.7671)
            >>> print(f"Found {len(restaurants)} restaurants")
            >>> # 予算とランチフィルタ指定
            >>> lunch_restaurants = restaurant_service.search_restaurants(
            ...     35.6812, 139.7671, budget_code="B010", lunch=1
            ... )
        """
        # ====== ステップ1: キャッシュキーを生成 ======
        # 同じ場所・同じ半径の検索結果は再利用できるようにキャッシュキーを作る
        # round(lat, 4) で小数点以下4桁に丸める理由:
        #   - 緯度経度の0.0001度 ≒ 約10m の違いなので、この程度の誤差は許容
        #   - 細かすぎるとキャッシュが効きにくくなる
        cache_key = self.cache_service.generate_cache_key(
            'restaurants',
            lat=round(lat, 4),
            lon=round(lon, 4),
            radius=radius,
            budget_code=budget_code or 'all',
            lunch=lunch or 0
        )

        # ====== ステップ2: キャッシュから取得を試みる ======
        # 過去に同じ検索をしていれば、そのデータを再利用（API呼び出しを節約）
        cached_data = self.cache_service.get_cached_data(cache_key)
        if cached_data:
            print(f"レストラン情報をキャッシュから取得: {len(cached_data)}件")
            return cached_data

        # ====== ステップ3: APIキーが設定されていない場合は空のリストを返す ======
        # APIキーがないとHot Pepper APIを使えないので、検索できない
        if not self.api_key:
            print("APIキーが設定されていないため、レストラン検索をスキップします。")
            return []

        try:
            # ====== ステップ4: APIリクエストのパラメータを準備 ======
            # Hot Pepper APIに送信するパラメータを辞書形式で作成
            params = {
                'key': self.api_key,           # APIキー（認証用）
                'lat': lat,                    # 緯度
                'lng': lon,                    # 経度（Hot Pepper APIでは'lng'と表記）
                'range': self._convert_radius_to_range_code(radius),  # 検索範囲コード（後述）
                'count': 100,                  # 最大取得件数（100件まで一度に取得）
                'format': 'json'               # レスポンス形式（JSON形式で受け取る）
            }
            
            # 予算コードが指定されている場合は追加
            if budget_code:
                params['budget'] = budget_code
            
            # ランチフィルタが指定されている場合は追加
            if lunch is not None:
                params['lunch'] = lunch

            print(f"レストラン検索API呼び出し: lat={lat}, lon={lon}, radius={radius}km, budget={budget_code}, lunch={lunch}")

            # ====== ステップ5: Hot Pepper APIにHTTPリクエストを送信 ======
            # requests.get() でAPIサーバーにアクセス
            # timeout=10秒 を設定してサーバーが応答しない時は諦める
            response = requests.get(self.api_base_url, params=params, timeout=self.timeout)
            
            # ====== ステップ6: レスポンスのステータスコードを確認 ======
            # raise_for_status() でエラーレスポンス（404, 500など）が来たら例外を投げる
            response.raise_for_status()

            # ====== ステップ7: JSONデータを解析 ======
            # APIからのレスポンスはJSON形式なので、Pythonの辞書に変換
            data = response.json()

            # エラーレスポンスをチェック
            # Hot Pepper APIは 'results' キーに検索結果を入れて返すので、これがないとエラー
            if 'results' not in data:
                raise ValueError("APIレスポンスに結果が含まれていません")

            # ====== ステップ8: レストランリストを抽出 ======
            # data['results']['shop'] にレストラン情報の配列が入っている
            # _format_restaurant_data() で使いやすい形式に整形
            restaurants = self._format_restaurant_data(data['results'].get('shop', []))

            # ====== ステップ9: データをキャッシュに保存（次回の高速化のため) ======
            # TTL（Time To Live）= 600秒（10分間）有効
            # 10分後には古いデータになるので、再度APIから取得する
            self.cache_service.set_cached_data(cache_key, restaurants, ttl=600)

            # ====== ステップ10: レストランリストを返す ======
            print(f"レストラン検索成功: {len(restaurants)}件取得")
            return restaurants

        # ====== エラーハンドリング（何か問題が起きた時の処理）======
        except requests.exceptions.HTTPError as e:
            # HTTPエラー（レート制限、認証エラーなど）
            if e.response.status_code == 429:
                # 429 = Too Many Requests（API呼び出し回数の上限を超えた）
                print(f"レストラン検索API レート制限エラー: {e}")
                # レート制限時は古いキャッシュデータを使用を試みる
                fallback_data = self._get_fallback_cache_data(cache_key)
                if fallback_data:
                    return fallback_data
            elif e.response.status_code == 401:
                # 401 = Unauthorized（APIキーが間違っているか、権限がない）
                print(f"レストラン検索API 認証エラー: {e}")
            else:
                print(f"レストラン検索API HTTPエラー: {e}")
            return []

        except requests.exceptions.RequestException as e:
            # ネットワークエラー（インターネット接続が切れた、タイムアウトなど）
            print(f"レストラン検索API リクエストエラー: {e}")
            # ネットワークエラー時は古いキャッシュデータを使用を試みる
            fallback_data = self._get_fallback_cache_data(cache_key)
            if fallback_data:
                return fallback_data
            return []

        except (ValueError, KeyError) as e:
            # データ解析エラー（JSONの形式がおかしい、必要なキーがないなど）
            print(f"レストラン検索データ解析エラー: {e}")
            return []

        except Exception as e:
            # その他の予期しないエラー
            print(f"レストラン検索で予期しないエラー: {e}")
            return []

    def filter_by_budget(self, restaurants: List[Dict], max_budget: int = None) -> List[Dict]:
        """
        予算でレストランをフィルタリング
        
        【フィルタリング処理の流れ】
        1. max_budgetが指定されていなければ、LUNCH_BUDGET_LIMIT（1200円）を使用
        2. レストランリストを一つずつチェック
        3. 予算情報（budget_average）がないレストランはスキップ
        4. 予算が max_budget 以下のレストランだけを抽出
        5. フィルタリング結果を表示して返す

        Args:
            restaurants (list): レストラン情報のリスト
            max_budget (int, optional): 最大予算（円）、デフォルトはLUNCH_BUDGET_LIMIT
                - 例: 1000 を指定すると、1000円以下のお店だけ残る

        Returns:
            list: フィルタリングされたレストラン情報のリスト
                - max_budget以下の予算のレストランのみ含まれる
        """
        # 1. max_budgetが指定されていなければデフォルト値（1200円）を使う
        if max_budget is None:
            max_budget = self.LUNCH_BUDGET_LIMIT

        # 2. フィルタリング結果を格納するリスト
        filtered_restaurants = []

        # 3. レストランを一つずつチェック
        for restaurant in restaurants:
            # 予算情報が存在しない場合はスキップ
            # （稀に予算情報がないお店もあるため）
            if 'budget_average' not in restaurant:
                continue

            # 4. 予算が制限以下の場合に追加
            # 例: max_budget=1200円、restaurant['budget_average']=1000円 → 追加
            # 例: max_budget=1200円、restaurant['budget_average']=1500円 → スキップ
            if restaurant['budget_average'] <= max_budget:
                filtered_restaurants.append(restaurant)

        # 5. フィルタリング結果を表示
        # 例: "予算フィルタリング: 50件 → 30件 (≤¥1200)"
        print(f"予算フィルタリング: {len(restaurants)}件 → {len(filtered_restaurants)}件 (≤¥{max_budget})")
        return filtered_restaurants

    def search_lunch_restaurants(self, lat: float, lon: float, radius: int = 1) -> List[Dict]:
        """
        ランチに適したレストランを検索（予算フィルタリング込み）
        
        【この関数が実行する2ステップ】
        1. search_restaurants() で周辺の全レストランを検索
        2. filter_by_budget() で予算1200円以下のお店だけに絞る
        
        実質的に「近くて安いランチのお店を探す」ための便利関数です。

        Args:
            lat (float): 緯度（例: 35.6812 = 東京駅付近）
            lon (float): 経度（例: 139.7671 = 東京駅付近）
            radius (int): 検索半径(km)、デフォルトは1km
                - 1km = 徒歩約12〜15分の距離

        Returns:
            list: ランチに適したレストラン情報のリスト
                - 予算1200円以下のお店のみ含まれる
        """
        # ステップ1: 全レストランを検索（予算関係なく周辺のお店を全部取得）
        all_restaurants = self.search_restaurants(lat, lon, radius)

        # ステップ2: 予算でフィルタリング（1200円以下だけ残す）
        lunch_restaurants = self.filter_by_budget(all_restaurants, self.LUNCH_BUDGET_LIMIT)

        return lunch_restaurants

    def _convert_radius_to_range_code(self, radius_km: int) -> int:
        """
        半径(km)をHot Pepper APIの範囲コードに変換
        
        【Hot Pepper APIの範囲コードとは】
        Hot Pepper APIでは距離を「1, 2, 3, 4, 5」のコードで指定します:
        - 1 = 300m以内
        - 2 = 500m以内
        - 3 = 1000m以内（1km）
        - 4 = 2000m以内（2km）
        - 5 = 3000m以内（3km）
        
        この関数は「1km以内で検索したい」という要求を「3」に変換します。

        Args:
            radius_km (int): 半径(km)
                - 例: 1 を渡すと、コード3（1000m以内）が返る

        Returns:
            int: Hot Pepper APIの範囲コード（1〜5）
        """
        # 範囲コードの変換ロジック
        if radius_km <= 0.3:
            return 1  # 300m以内（徒歩3〜4分）
        elif radius_km <= 0.5:
            return 2  # 500m以内（徒歩6〜7分）
        elif radius_km <= 1:
            return 3  # 1000m以内（徒歩12〜15分）
        elif radius_km <= 2:
            return 4  # 2000m以内（徒歩24〜30分）
        else:
            return 5  # 3000m以内（徒歩36〜45分）

    def walking_time_to_range(self, minutes: int) -> int:
        """
        徒歩時間（分）をHot Pepper API rangeコードに変換
        
        【変換ロジックの基準】
        徒歩速度: 80m/分（不動産慣例「徒歩1分＝80m」）
        
        Hot Pepper APIの範囲コード:
        - 1 = 300m以内
        - 2 = 500m以内
        - 3 = 1000m以内
        - 4 = 2000m以内
        - 5 = 3000m以内
        
        【変換マッピング】
        | 徒歩時間 | 想定距離（80m/分） | 採用range |
        |---------|------------------|-----------|
        | 〜5分    | 〜400m           | 2 (500m)  |
        | 〜10分   | 〜800m           | 3 (1000m) |
        | 〜20分   | 〜1600m          | 4 (2000m) |
        | 20分超   | 〜2400m以上      | 5 (3000m) |

        Args:
            minutes (int): 徒歩時間（分）
                - 例: 10 を渡すと、コード3（1000m以内）が返る

        Returns:
            int: Hot Pepper APIの範囲コード（1〜5）
            
        Example:
            >>> service = RestaurantService()
            >>> service.walking_time_to_range(5)
            2  # 500m以内
            >>> service.walking_time_to_range(10)
            3  # 1000m以内
        """
        if minutes <= 5:
            return 2  # 500m以内（400m想定 ≈ 5分）
        elif minutes <= 10:
            return 3  # 1000m以内（800m想定 ≈ 10分）
        elif minutes <= 20:
            return 4  # 2000m以内（1600m想定 ≈ 20分）
        else:
            return 5  # 3000m以内（2400m以上）

    def _format_restaurant_data(self, api_restaurants: List[Dict]) -> List[Dict]:
        """
        APIレスポンスを標準形式に整形
        
        【この関数の役割】
        Hot Pepper APIから返ってくるデータは複雑で使いにくいので、
        必要な情報だけを取り出して、わかりやすい形式に整えます。
        
        【整形処理の流れ】
        1. APIから返ってきたレストランリストを一つずつ処理
        2. 各レストランから必要な情報を抽出
        3. 予算情報を「円」に変換（B010 → 1000円 など）
        4. 写真URLを取得
        5. 整形済みのレストラン情報をリストに追加
        6. エラーが起きたレストランはスキップ

        Args:
            api_restaurants (list): Hot Pepper APIからのレストランデータ
                - APIの生データ（辞書のリスト）

        Returns:
            list: 整形されたレストラン情報のリスト
                - 使いやすい形式に変換されたデータ
        """
        # 整形結果を格納するリスト
        formatted_restaurants = []

        # 1. レストランを一つずつ処理
        for restaurant in api_restaurants:
            try:
                # 2. 予算情報を解析（コード → 円に変換）
                # 例: {'code': 'B010', 'name': '〜1000円'} → 1000
                budget_average = self._parse_budget_info(restaurant.get('budget', {}))

                # 3. レストラン情報を標準形式に整形
                # get('キー名', 'デフォルト値') で安全に値を取得
                # ※APIからデータが来ない場合もあるため、デフォルト値を設定
                formatted_restaurant = {
                    # === 基本情報 ===
                    'id': restaurant.get('id', ''),                              # レストランID
                    'name': restaurant.get('name', '不明なレストラン'),           # 店名
                    'name_kana': restaurant.get('name_kana', ''),                # 店名（ふりがな）
                    'address': restaurant.get('address', ''),                    # 住所
                    'lat': float(restaurant.get('lat', 0)),                      # 緯度
                    'lng': float(restaurant.get('lng', 0)),                      # 経度
                    'genre': restaurant.get('genre', {}).get('name', ''),        # ジャンル（例: 居酒屋、イタリアン）
                    
                    # === 予算情報 ===
                    'budget_average': budget_average,                            # 平均予算（円）
                    'budget_name': restaurant.get('budget', {}).get('name', ''), # 予算名（例: 〜1000円）
                    
                    # === お店の特徴 ===
                    'catch': restaurant.get('catch', ''),                        # キャッチコピー
                    'capacity': restaurant.get('capacity', 0),                   # 収容人数
                    'access': restaurant.get('access', ''),                      # アクセス情報
                    'mobile_access': restaurant.get('mobile_access', ''),        # モバイル用アクセス情報
                    
                    # === URL情報 ===
                    'urls': {
                        'pc': restaurant.get('urls', {}).get('pc', ''),          # PC用URL
                        'mobile': restaurant.get('urls', {}).get('mobile', '')   # モバイル用URL
                    },
                    
                    # === 写真情報 ===
                    'photo': self._get_restaurant_photo(restaurant.get('photo', {})),  # 写真URL
                    
                    # === 営業情報 ===
                    'open': restaurant.get('open', ''),                          # 営業時間
                    'close': restaurant.get('close', ''),                        # 定休日
                    
                    # === その他の設備・サービス情報 ===
                    'party_capacity': restaurant.get('party_capacity', 0),       # パーティー収容人数
                    'wifi': restaurant.get('wifi', ''),                          # Wi-Fi有無
                    'wedding': restaurant.get('wedding', ''),                    # ウェディング対応
                    'course': restaurant.get('course', ''),                      # コース料理
                    'free_drink': restaurant.get('free_drink', ''),              # 飲み放題
                    'free_food': restaurant.get('free_food', ''),                # 食べ放題
                    'private_room': restaurant.get('private_room', ''),          # 個室
                    'horigotatsu': restaurant.get('horigotatsu', ''),            # 掘りごたつ
                    'tatami': restaurant.get('tatami', ''),                      # 座敷
                    'card': restaurant.get('card', ''),                          # カード利用可否
                    'non_smoking': restaurant.get('non_smoking', ''),            # 禁煙・喫煙
                    'charter': restaurant.get('charter', ''),                    # 貸切可否
                    'ktai': restaurant.get('ktai', ''),                          # 携帯電話
                    'parking': restaurant.get('parking', ''),                    # 駐車場
                    'barrier_free': restaurant.get('barrier_free', ''),          # バリアフリー
                    'other_memo': restaurant.get('other_memo', ''),              # その他メモ
                    'sommelier': restaurant.get('sommelier', ''),                # ソムリエ
                    'open_air': restaurant.get('open_air', ''),                  # オープンエア
                    'show': restaurant.get('show', ''),                          # ショー
                    'equipment': restaurant.get('equipment', ''),                # 設備
                    'karaoke': restaurant.get('karaoke', ''),                    # カラオケ
                    'band': restaurant.get('band', ''),                          # バンド演奏
                    'tv': restaurant.get('tv', ''),                              # TV
                    'english': restaurant.get('english', ''),                    # 英語対応
                    'pet': restaurant.get('pet', ''),                            # ペット可否
                    'child': restaurant.get('child', ''),                        # お子様連れ
                    'lunch': restaurant.get('lunch', ''),                        # ランチ
                    'midnight': restaurant.get('midnight', ''),                  # 深夜営業
                    'shop_detail_memo': restaurant.get('shop_detail_memo', ''),  # 店舗詳細メモ
                    
                    # === データソース ===
                    'source': 'hotpepper'  # このデータがHot Pepper APIから来たことを示す
                }

                # 4. 整形済みレストランをリストに追加
                formatted_restaurants.append(formatted_restaurant)

            except (ValueError, TypeError, KeyError) as e:
                # 5. エラーが起きたレストランはスキップ（処理を続ける）
                print(f"レストランデータ整形エラー (ID: {restaurant.get('id', 'unknown')}): {e}")
                continue

        return formatted_restaurants

    def _parse_budget_info(self, budget_data: Dict) -> int:
        """
        予算情報を解析して平均予算を算出

        Args:
            budget_data (dict): Hot Pepper APIの予算データ

        Returns:
            int: 平均予算（円）
        """
        try:
            budget_code = budget_data.get('code', '')

            # 予算コードから金額を取得
            if budget_code in self.BUDGET_CODES:
                return self.BUDGET_CODES[budget_code]

            # 予算名から推定（フォールバック）
            budget_name = budget_data.get('name', '').lower()

            if '500' in budget_name:
                return 500
            elif '1000' in budget_name or '1,000' in budget_name:
                return 1000
            elif '1500' in budget_name or '1,500' in budget_name:
                return 1500
            elif '2000' in budget_name or '2,000' in budget_name:
                return 2000
            elif '3000' in budget_name or '3,000' in budget_name:
                return 3000
            else:
                # デフォルト値としてランチ予算制限を適用
                return 2000

        except Exception:
            return 2000  # デフォルト値

    def _get_restaurant_photo(self, photo_data: Dict) -> str:
        """
        レストランの写真URLを取得

        Args:
            photo_data (dict): Hot Pepper APIの写真データ

        Returns:
            str: 写真URL、存在しない場合は空文字列
        """
        try:
            # PCサイズの写真を優先
            if 'pc' in photo_data:
                pc_photos = photo_data['pc']
                if 'l' in pc_photos:  # 大サイズ
                    return pc_photos['l']
                elif 'm' in pc_photos:  # 中サイズ
                    return pc_photos['m']
                elif 's' in pc_photos:  # 小サイズ
                    return pc_photos['s']

            # モバイルサイズの写真をフォールバック
            if 'mobile' in photo_data:
                mobile_photos = photo_data['mobile']
                if 'l' in mobile_photos:
                    return mobile_photos['l']
                elif 's' in mobile_photos:
                    return mobile_photos['s']

            return ''

        except Exception:
            return ''

    def get_restaurant_by_id(self, restaurant_id: str) -> Optional[Dict]:
        """
        レストランIDから詳細情報を取得

        Args:
            restaurant_id (str): レストランID

        Returns:
            dict: レストラン詳細情報、見つからない場合はNone
        """
        # APIキーが設定されていない場合はNoneを返す
        if not self.api_key:
            return None

        try:
            params = {
                'key': self.api_key,
                'id': restaurant_id,
                'format': 'json'
            }

            response = requests.get(self.api_base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if 'results' in data and 'shop' in data['results']:
                shops = data['results']['shop']
                if shops:
                    return self._format_restaurant_data([shops[0]])[0]

            return None

        except Exception as e:
            print(f"レストラン詳細取得エラー (ID: {restaurant_id}): {e}")
            return None

    def _get_fallback_cache_data(self, cache_key: str) -> List[Dict]:
        """
        期限切れでも利用可能なキャッシュデータを取得（フォールバック用）

        Args:
            cache_key (str): キャッシュキー

        Returns:
            list: キャッシュされたレストラン情報、存在しない場合は空リスト
        """
        try:
            from ..models.database import get_db_connection

            with get_db_connection(self.cache_service.db_path) as conn:
                cursor = conn.execute('''
                    SELECT data FROM cache
                    WHERE cache_key = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (cache_key,))

                row = cursor.fetchone()

                if row is None:
                    return []

                # 期限切れでもデータを返す（フォールバック用）
                fallback_data = self.cache_service.deserialize_data(row['data'])

                # ソース情報を更新
                for restaurant in fallback_data:
                    restaurant['source'] = 'fallback_cache'

                print(f"フォールバック用キャッシュデータを使用: {len(fallback_data)}件")
                return fallback_data

        except Exception as e:
            print(f"フォールバックキャッシュ取得エラー: {e}")
            return []

    def validate_restaurant_data(self, restaurant_data: Dict) -> bool:
        """
        レストラン情報データの妥当性を検証

        Args:
            restaurant_data (dict): レストラン情報

        Returns:
            bool: 妥当な場合はTrue
        """
        try:
            # 必須フィールドの存在確認
            required_fields = ['id', 'name', 'lat', 'lng']
            for field in required_fields:
                if field not in restaurant_data or not restaurant_data[field]:
                    return False

            # 座標の範囲確認
            lat = float(restaurant_data['lat'])
            lng = float(restaurant_data['lng'])

            if not (-90 <= lat <= 90):
                return False
            if not (-180 <= lng <= 180):
                return False

            return True

        except (ValueError, TypeError):
            return False


# 使用例とテスト用コード
if __name__ == '__main__':
    """
    RestaurantServiceのテスト実行
    """
    print("RestaurantService テスト実行")
    print("=" * 40)

    # RestaurantServiceインスタンス作成
    restaurant_service = RestaurantService()

    # 東京駅周辺の座標
    tokyo_lat, tokyo_lon = 35.6812, 139.7671

    # レストラン検索テスト
    print("1. レストラン検索:")
    restaurants = restaurant_service.search_restaurants(tokyo_lat, tokyo_lon, radius=1)
    print(f"   検索結果: {len(restaurants)}件")

    if restaurants:
        # 最初のレストラン情報を表示
        first_restaurant = restaurants[0]
        print(f"   店名: {first_restaurant['name']}")
        print(f"       ジャンル: {first_restaurant['genre']}")
        print(f"       予算: ¥{first_restaurant['budget_average']}")
        print(f"       住所: {first_restaurant['address']}")

    # 予算フィルタリングテスト
    print("\n2. 予算フィルタリング:")
    lunch_restaurants = restaurant_service.filter_by_budget(restaurants, 1200)
    print(f"   フィルタリング結果: {len(lunch_restaurants)}件")

    # ランチレストラン検索テスト
    print("\n3. ランチレストラン検索:")
    lunch_only = restaurant_service.search_lunch_restaurants(tokyo_lat, tokyo_lon)
    print(f"   ランチに適したレストラン: {len(lunch_only)}件")

    # データ妥当性検証テスト
    if restaurants:
        print(f"\n4. データ妥当性検証: {restaurant_service.validate_restaurant_data(restaurants[0])}")

    print("\nテスト完了")
