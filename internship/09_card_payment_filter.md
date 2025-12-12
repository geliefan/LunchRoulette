# 案9: カード利用可フィルター機能

## ねらい
「カード利用可」のレストランに絞り込めるフィルター機能を追加し、現金を持ち合わせていない場合やキャッシュレス決済を希望するユーザーのニーズに応える。

## 短時間で改修可能な理由
- Hot Pepper APIの`card`パラメータを使用するだけで実装可能
- APIパラメータ: `card=1`（カード利用可）
- 既存のレストランデータに`card`フィールドが含まれている
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
    
    <!-- カード利用可フィルター -->
    <div class="condition-group">
        <label class="condition-label">
            <span class="label-icon">💳</span>
            支払い方法
        </label>
        <div class="checkbox-group">
            <label class="checkbox-label">
                <input type="checkbox" id="card-payment" class="condition-checkbox">
                <span class="checkbox-text">カード利用可</span>
            </label>
        </div>
    </div>
</div>
```

### 2. JavaScript修正（`static/js/main.js`）
検索条件にカード利用フィルタを追加:
```javascript
// HTML要素の取得に追加
const cardPaymentCheckbox = document.getElementById('card-payment');

// executeRoulette関数内の検索条件収集部分に追加
async function executeRoulette() {
    try {
        // ... 既存のコード ...
        
        // カード利用フィルタを追加
        if (cardPaymentCheckbox && cardPaymentCheckbox.checked) {
            searchParams.card = 1;  // カード利用可
        }
        
        console.log('検索条件:', searchParams);
        
        // ... 既存のサーバーへのリクエスト処理 ...
    } catch (error) {
        // ... エラー処理 ...
    }
}
```

### 3. サーバー側修正（`src/lunch_roulette/app.py`）
ルーレットエンドポイントでカード利用パラメータを受け取る:
```python
@app.route('/roulette', methods=['POST'])
def roulette():
    try:
        # ... 既存のコード ...
        
        # カード利用フィルタを取得
        card = request_data.get('card', None)
        
        # ... 既存の検索条件収集 ...
        
        if location_mode == 'area':
            # エリアモード
            restaurants = restaurant_service.search_restaurants(
                middle_area=middle_area_code,
                budget_code=budget_code,
                lunch=lunch_filter,
                genre_code=genre_code,
                card=card  # 追加
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
                card=card  # 追加
            )
        
        # ... 既存のレスポンス処理 ...
        
    except Exception as e:
        # ... エラー処理 ...
```

### 4. RestaurantService修正（`src/lunch_roulette/services/restaurant_service.py`）
search_restaurants関数にcardパラメータを追加:
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
    card: int = None  # 追加
) -> List[Dict]:
    """
    レストランを検索
    
    Args:
        ... 既存のパラメータ ...
        card (int, optional): カード利用可フィルタ（1=カード利用可、None=指定なし）
    """
    
    # キャッシュキー生成にカード利用フィルタを追加
    if middle_area:
        cache_key = self.cache_service.generate_cache_key(
            'restaurants',
            middle_area=middle_area,
            budget_code=budget_code or 'all',
            lunch=lunch or 0,
            genre_code=genre_code or 'all',
            card=card or 0  # 追加
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
            card=card or 0  # 追加
        )
    
    # ... キャッシュチェック処理 ...
    
    try:
        # APIパラメータにカード利用フィルタを追加
        params = {
            'key': self.api_key,
            'count': 100,
            'format': 'json'
        }
        
        # ... 既存のパラメータ設定 ...
        
        # カード利用フィルタが指定されている場合は追加
        if card is not None:
            params['card'] = card
        
        print(f"レストラン検索API呼び出し: ... card={card}")
        
        # ... 既存のAPI呼び出し処理 ...
        
    except Exception as e:
        # ... エラー処理 ...
```

### 5. レストラン詳細表示への追加（オプション）
レストランカードにカード利用可の情報を表示:
```javascript
// displayRestaurant関数に追加
function displayRestaurant(data) {
    const { restaurant, distance, weather } = data;
    
    // ... 既存の表示処理 ...
    
    // カード利用可情報を表示（レストランデータに含まれている場合）
    if (restaurant.card) {
        const cardInfo = document.createElement('div');
        cardInfo.className = 'payment-info';
        cardInfo.innerHTML = '<span class="info-icon">💳</span> カード利用可';
        
        // 店舗情報エリアに追加
        const infoSection = document.querySelector('.restaurant-info');
        infoSection.appendChild(cardInfo);
    }
}
```

### 6. CSS追加（`static/css/style.css`）
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

/* 支払い情報表示 */
.payment-info {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    background-color: #e3f2fd;
    border-radius: 6px;
    margin-top: 10px;
    color: #1976d2;
    font-size: 0.9rem;
}

.payment-info .info-icon {
    margin-right: 6px;
    font-size: 1.1rem;
}
```

## 動作確認方法

### テストケース
1. **カード利用可のみで検索**
   - 「カード利用可」にチェック
   - ルーレット実行
   - 結果のレストランがカード利用可か確認

2. **他の条件と組み合わせ**
   - 予算「〜1000円」+ カード利用可
   - ジャンル「イタリアン」+ カード利用可
   - 複合条件で正しく絞り込まれるか確認

3. **カード不要（チェックなし）**
   - チェックなしで検索
   - カード利用の有無に関わらず検索されることを確認

### 確認ポイント
- コンソールログで`card`パラメータが送信されているか確認
- API呼び出し時のパラメータに`card=1`が含まれているか確認
- レストラン詳細にカード利用可情報が表示されているか確認

## Hot Pepper APIのカード利用フィルタ仕様
- パラメータ名: `card`
- 値: `1`（カード利用可）
- 未指定の場合: カード利用の有無に関わらず検索

## 学習ポイント
- チェックボックスの状態管理（`checked`プロパティ）
- 条件付きパラメータの追加（真偽値を数値に変換）
- APIリクエストへのパラメータ追加
- レスポンスデータの表示処理
- ユーザビリティを考慮したフィルタ設計

## 発展課題（余力があれば）
1. 複数の支払い方法フィルタを追加:
   - 電子マネー対応
   - QRコード決済対応
   - ※Hot Pepper APIには個別のパラメータがないため、`card`フィールドのテキスト解析が必要

2. 支払い方法アイコンをレストランカードに表示
   - カード💳、電子マネー📱などのアイコン

3. 支払い方法の詳細情報を表示
   - 利用可能なカードブランド（VISA、JCBなど）

4. フィルタのプリセット機能
   - 「完全キャッシュレス対応店」など
