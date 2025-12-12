# 案10: 飲み放題ありフィルター機能

## ねらい
「飲み放題あり」のレストランに絞り込めるフィルター機能を追加し、歓送迎会や懇親会などの宴会シーンでレストランを探しやすくする。

## 短時間で改修可能な理由
- Hot Pepper APIの`free_drink`パラメータを使用するだけで実装可能
- APIパラメータ: `free_drink=1`（飲み放題あり）
- 既存のレストランデータに`free_drink`フィールドが含まれている
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
    
    <!-- 飲み放題フィルター -->
    <div class="condition-group">
        <label class="condition-label">
            <span class="label-icon">🍺</span>
            飲み放題
        </label>
        <div class="checkbox-group">
            <label class="checkbox-label">
                <input type="checkbox" id="free-drink" class="condition-checkbox">
                <span class="checkbox-text">飲み放題あり</span>
            </label>
        </div>
    </div>
</div>
```

### 2. JavaScript修正（`static/js/main.js`）
検索条件に飲み放題フィルタを追加:
```javascript
// HTML要素の取得に追加
const freeDrinkCheckbox = document.getElementById('free-drink');

// executeRoulette関数内の検索条件収集部分に追加
async function executeRoulette() {
    try {
        // ... 既存のコード ...
        
        // 飲み放題フィルタを追加
        if (freeDrinkCheckbox && freeDrinkCheckbox.checked) {
            searchParams.free_drink = 1;  // 飲み放題あり
        }
        
        console.log('検索条件:', searchParams);
        
        // ... 既存のサーバーへのリクエスト処理 ...
    } catch (error) {
        // ... エラー処理 ...
    }
}
```

### 3. サーバー側修正（`src/lunch_roulette/app.py`）
ルーレットエンドポイントで飲み放題パラメータを受け取る:
```python
@app.route('/roulette', methods=['POST'])
def roulette():
    try:
        # ... 既存のコード ...
        
        # 飲み放題フィルタを取得
        free_drink = request_data.get('free_drink', None)
        
        # ... 既存の検索条件収集 ...
        
        if location_mode == 'area':
            # エリアモード
            restaurants = restaurant_service.search_restaurants(
                middle_area=middle_area_code,
                budget_code=budget_code,
                lunch=lunch_filter,
                genre_code=genre_code,
                free_drink=free_drink  # 追加
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
                free_drink=free_drink  # 追加
            )
        
        # ... 既存のレスポンス処理 ...
        
    except Exception as e:
        # ... エラー処理 ...
```

### 4. RestaurantService修正（`src/lunch_roulette/services/restaurant_service.py`）
search_restaurants関数にfree_drinkパラメータを追加:
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
    free_drink: int = None  # 追加
) -> List[Dict]:
    """
    レストランを検索
    
    Args:
        ... 既存のパラメータ ...
        free_drink (int, optional): 飲み放題フィルタ（1=飲み放題あり、None=指定なし）
    """
    
    # キャッシュキー生成に飲み放題フィルタを追加
    if middle_area:
        cache_key = self.cache_service.generate_cache_key(
            'restaurants',
            middle_area=middle_area,
            budget_code=budget_code or 'all',
            lunch=lunch or 0,
            genre_code=genre_code or 'all',
            free_drink=free_drink or 0  # 追加
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
            free_drink=free_drink or 0  # 追加
        )
    
    # ... キャッシュチェック処理 ...
    
    try:
        # APIパラメータに飲み放題フィルタを追加
        params = {
            'key': self.api_key,
            'count': 100,
            'format': 'json'
        }
        
        # ... 既存のパラメータ設定 ...
        
        # 飲み放題フィルタが指定されている場合は追加
        if free_drink is not None:
            params['free_drink'] = free_drink
        
        print(f"レストラン検索API呼び出し: ... free_drink={free_drink}")
        
        # ... 既存のAPI呼び出し処理 ...
        
    except Exception as e:
        # ... エラー処理 ...
```

### 5. レストラン詳細表示への追加（オプション）
レストランカードに飲み放題情報を表示:
```javascript
// displayRestaurant関数に追加
function displayRestaurant(data) {
    const { restaurant, distance, weather } = data;
    
    // ... 既存の表示処理 ...
    
    // 飲み放題情報を表示（レストランデータに含まれている場合）
    if (restaurant.free_drink && restaurant.free_drink !== 'なし') {
        const drinkInfo = document.createElement('div');
        drinkInfo.className = 'feature-badge';
        drinkInfo.innerHTML = '<span class="badge-icon">🍺</span> 飲み放題あり';
        
        // 店舗情報エリアに追加
        const infoSection = document.querySelector('.restaurant-info');
        infoSection.appendChild(drinkInfo);
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

/* 特徴バッジ */
.feature-badge {
    display: inline-flex;
    align-items: center;
    padding: 6px 12px;
    background-color: #fff3e0;
    border-radius: 6px;
    margin-top: 10px;
    color: #e65100;
    font-size: 0.9rem;
    font-weight: 500;
}

.feature-badge .badge-icon {
    margin-right: 6px;
    font-size: 1.1rem;
}
```

## 動作確認方法

### テストケース
1. **飲み放題ありのみで検索**
   - 「飲み放題あり」にチェック
   - ルーレット実行
   - 結果のレストランが飲み放題対応か確認

2. **他の条件と組み合わせ**
   - 予算「〜3000円」+ 飲み放題あり
   - ジャンル「居酒屋」+ 飲み放題あり
   - 複合条件で正しく絞り込まれるか確認

3. **飲み放題不要（チェックなし）**
   - チェックなしで検索
   - 飲み放題の有無に関わらず検索されることを確認

### 確認ポイント
- コンソールログで`free_drink`パラメータが送信されているか確認
- API呼び出し時のパラメータに`free_drink=1`が含まれているか確認
- レストラン詳細に飲み放題情報が表示されているか確認

## Hot Pepper APIの飲み放題フィルタ仕様
- パラメータ名: `free_drink`
- 値: `1`（飲み放題あり）
- 未指定の場合: 飲み放題の有無に関わらず検索

## 活用シーン
- 会社の歓送迎会・忘年会・新年会
- サークルや友人グループの懇親会
- 同窓会などのイベント
- 長時間の飲み会を予定している場合

## 学習ポイント
- チェックボックスによる条件フィルタの実装
- APIパラメータの動的な追加
- レストランデータの属性表示
- ユーザーシーンに応じた機能設計
- 宴会向けサービスの理解

## 発展課題（余力があれば）
1. 食べ放題フィルタも追加（`free_food=1`）
   - 「飲み放題」と「食べ放題」の両方をチェックボックスで選択可能に

2. コースフィルタの追加（`course=1`）
   - 宴会コースがあるお店に絞り込み

3. 宴会向けプリセット機能
   - 「宴会向け」ボタン一つで「飲み放題」「コース」「個室」を同時選択

4. 収容人数フィルタの追加（`party_capacity`）
   - 「20名以上収容可」などの条件を追加

5. 飲み放題の詳細情報を表示
   - 時間制限、料金、対象ドリンクなどの情報表示
