# 案8: 個室ありフィルター機能

## ねらい
「個室あり」のレストランに絞り込めるフィルター機能を追加し、プライベートな食事や接待、少人数の打ち合わせなどに適したレストランを簡単に探せるようにする。

## 短時間で改修可能な理由
- Hot Pepper APIの`private_room`パラメータを使用するだけで実装可能
- APIパラメータ: `private_room=1`（個室あり）
- 既存のレストランデータに`private_room`フィールドが含まれている
- UIはチェックボックス1つを追加するだけで済む
- サーバー側は既存の検索処理にパラメータを1つ追加するだけ
- **改修時間目安: 1〜2時間**

## 改修に必要なビジネスロジック

### 1. HTML修正（`templates/index.html`）
検索条件セクションにチェックボックスを追加:
```html
<!-- 検索条件セクション内に追加 -->
<div class="conditions-grid">
    <!-- 既存の条件... -->
    
    <!-- 個室フィルター -->
    <div class="condition-group">
        <label class="condition-label">
            <span class="label-icon">🚪</span>
            個室
        </label>
        <div class="checkbox-group">
            <label class="checkbox-label">
                <input type="checkbox" id="private-room" class="condition-checkbox">
                <span class="checkbox-text">個室あり</span>
            </label>
        </div>
    </div>
</div>
```

### 2. JavaScript修正（`static/js/main.js`）
検索条件に個室フィルタを追加:
```javascript
// HTML要素の取得に追加
const privateRoomCheckbox = document.getElementById('private-room');

// executeRoulette関数内の検索条件収集部分に追加
async function executeRoulette() {
    try {
        // ... 既存のコード ...
        
        // 個室フィルタを追加
        if (privateRoomCheckbox && privateRoomCheckbox.checked) {
            searchParams.private_room = 1;  // 個室あり
        }
        
        console.log('検索条件:', searchParams);
        
        // ... 既存のサーバーへのリクエスト処理 ...
    } catch (error) {
        // ... エラー処理 ...
    }
}
```

### 3. サーバー側修正（`src/lunch_roulette/app.py`）
ルーレットエンドポイントで個室パラメータを受け取る:
```python
@app.route('/roulette', methods=['POST'])
def roulette():
    try:
        # ... 既存のコード ...
        
        # 個室フィルタを取得
        private_room = request_data.get('private_room', None)
        
        # ... 既存の検索条件収集 ...
        
        if location_mode == 'area':
            # エリアモード
            restaurants = restaurant_service.search_restaurants(
                middle_area=middle_area_code,
                budget_code=budget_code,
                lunch=lunch_filter,
                genre_code=genre_code,
                private_room=private_room  # 追加
            )
        else:
            # 現在地モード
            restaurants = restaurant_service.search_restaurants(
                user_lat, 
                user_lon, 
                radius=search_range,
                budget_code=budget_code,
                lunch=lunch_filter,
                genre_code=genre_code,
                private_room=private_room  # 追加
            )
        
        # ... 既存のレスポンス処理 ...
        
    except Exception as e:
        # ... エラー処理 ...
```

### 4. RestaurantService修正（`src/lunch_roulette/services/restaurant_service.py`）
search_restaurants関数にprivate_roomパラメータを追加:
```python
def search_restaurants(
    self, 
    lat: float = None, 
    lon: float = None, 
    radius: int = 1, 
    budget_code: str = None, 
    lunch: int = None, 
    genre_code: str = None, 
    middle_area: str = None,
    private_room: int = None  # 追加
) -> List[Dict]:
    """
    レストランを検索
    
    Args:
        ... 既存のパラメータ ...
        private_room (int, optional): 個室フィルタ（1=個室あり、None=指定なし）
    """
    
    # キャッシュキー生成に個室フィルタを追加
    if middle_area:
        cache_key = self.cache_service.generate_cache_key(
            'restaurants',
            middle_area=middle_area,
            budget_code=budget_code or 'all',
            lunch=lunch or 0,
            genre_code=genre_code or 'all',
            private_room=private_room or 0  # 追加
        )
    else:
        cache_key = self.cache_service.generate_cache_key(
            'restaurants',
            lat=round(lat, 4) if lat else 0,
            lon=round(lon, 4) if lon else 0,
            radius=radius,
            budget_code=budget_code or 'all',
            lunch=lunch or 0,
            genre_code=genre_code or 'all',
            private_room=private_room or 0  # 追加
        )
    
    # ... キャッシュチェック処理 ...
    
    try:
        # APIパラメータに個室フィルタを追加
        params = {
            'key': self.api_key,
            'count': 100,
            'format': 'json'
        }
        
        # ... 既存のパラメータ設定 ...
        
        # 個室フィルタが指定されている場合は追加
        if private_room is not None:
            params['private_room'] = private_room
        
        print(f"レストラン検索API呼び出し: ... private_room={private_room}")
        
        # ... 既存のAPI呼び出し処理 ...
        
    except Exception as e:
        # ... エラー処理 ...
```

### 5. CSS追加（`static/css/style.css`）
```css
/* チェックボックスグループ */
.checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 8px 0;
}

/* チェックボックスラベル */
.checkbox-label {
    display: flex;
    align-items: center;
    cursor: pointer;
    user-select: none;
    padding: 6px 10px;
    border-radius: 6px;
    transition: background-color 0.2s;
}

.checkbox-label:hover {
    background-color: #f5f5f5;
}

/* チェックボックス */
.condition-checkbox {
    width: 18px;
    height: 18px;
    margin-right: 8px;
    cursor: pointer;
    accent-color: #667eea;
}

/* チェックボックステキスト */
.checkbox-text {
    font-size: 0.95rem;
    color: #333;
}
```

## 動作確認方法

### テストケース
1. **個室ありのみで検索**
   - 「個室あり」にチェック
   - ルーレット実行
   - 結果に個室情報が表示されることを確認

2. **他の条件と組み合わせ**
   - 予算「〜1000円」+ 個室あり
   - ジャンル「和食」+ 個室あり
   - 複合条件で正しく絞り込まれるか確認

3. **個室なし（チェックなし）**
   - チェックなしで検索
   - 個室の有無に関わらず検索されることを確認

### 確認ポイント
- コンソールログで`private_room`パラメータが送信されているか確認
- API呼び出し時のパラメータに`private_room=1`が含まれているか確認
- レストラン詳細に個室情報が表示されているか確認

## Hot Pepper APIの個室フィルタ仕様
- パラメータ名: `private_room`
- 値: `1`（個室あり）
- 未指定の場合: 個室の有無に関わらず検索

## 学習ポイント
- チェックボックスの扱い方（`checked`プロパティ）
- 条件付きパラメータの追加（値がある場合のみ送信）
- APIパラメータの追加方法
- キャッシュキーの生成ロジック
- ユーザーニーズに応じた絞り込み機能の実装

## 発展課題（余力があれば）
1. 「個室」以外の設備フィルタも追加:
   - `free_drink=1`: 飲み放題あり
   - `free_food=1`: 食べ放題あり
   - `card=1`: カード利用可
   - `non_smoking=1`: 禁煙席あり
   - `parking=1`: 駐車場あり
   - `wifi=1`: Wi-Fiあり

2. 複数の設備を同時に指定できるUI（チェックボックス複数）

3. レストランカードに設備アイコンを表示（個室🚪、Wi-Fi📶など）

4. 設備フィルタのプリセット機能（「接待向け」「家族向け」など）
