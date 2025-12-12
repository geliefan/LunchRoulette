# 案7: ルーレットアニメーション強化

## ねらい
「ルーレットを回す」ボタンを押した時に、複数のレストランが次々に切り替わるアニメーションを表示し、最後に選ばれたレストランで止まるようにすることで、ルーレット感を演出し、ユーザ体験を向上させる。

## 短時間で改修可能な理由
- レストラン検索結果のリストは既に取得できている
- JavaScriptの`setTimeout`や`setInterval`で簡単にアニメーション実装可能
- CSS transitionを活用することで滑らかな表示切替ができる
- 既存のレストラン表示処理を再利用できる
- **改修時間目安: 2〜3時間**

## 改修に必要なビジネスロジック

### 1. ルーレットアニメーションロジック（JavaScript）
```javascript
/**
 * ルーレットアニメーションを実行
 * @param {array} restaurants - レストランリスト
 * @param {object} finalRestaurant - 最終的に選ばれるレストラン
 * @param {function} callback - アニメーション完了時のコールバック
 */
function playRouletteAnimation(restaurants, finalRestaurant, callback) {
    // アニメーション設定
    const TOTAL_DURATION = 3000; // 総アニメーション時間（ミリ秒）
    const INITIAL_INTERVAL = 100; // 初期切替間隔（速い）
    const FINAL_INTERVAL = 500;   // 最終切替間隔（遅い）
    const SLOW_DOWN_START = 2000; // スローダウン開始時刻
    
    // レストラン選択用のランダムインデックス配列を生成
    const displaySequence = generateDisplaySequence(restaurants.length, 20);
    
    let currentIndex = 0;
    let elapsedTime = 0;
    let lastUpdateTime = Date.now();
    
    // ルーレット表示エリアを表示
    const rouletteDisplay = document.getElementById('roulette-display');
    rouletteDisplay.style.display = 'block';
    rouletteDisplay.classList.add('spinning');
    
    /**
     * レストランを切り替えて表示
     */
    function updateDisplay() {
        const now = Date.now();
        elapsedTime += now - lastUpdateTime;
        lastUpdateTime = now;
        
        // 進行度に応じて切替間隔を調整（だんだん遅くなる）
        const progress = elapsedTime / TOTAL_DURATION;
        let interval = INITIAL_INTERVAL;
        
        if (elapsedTime > SLOW_DOWN_START) {
            // スローダウンフェーズ: 徐々に遅くする
            const slowDownProgress = (elapsedTime - SLOW_DOWN_START) / (TOTAL_DURATION - SLOW_DOWN_START);
            interval = INITIAL_INTERVAL + (FINAL_INTERVAL - INITIAL_INTERVAL) * slowDownProgress;
        }
        
        // アニメーション終了判定
        if (elapsedTime >= TOTAL_DURATION) {
            // 最終レストランを表示
            displayRouletteCard(finalRestaurant, true);
            rouletteDisplay.classList.remove('spinning');
            rouletteDisplay.classList.add('stopped');
            
            // コールバック実行（完了処理）
            if (callback) callback();
            return;
        }
        
        // ランダムなレストランを表示
        const restaurant = restaurants[displaySequence[currentIndex % displaySequence.length]];
        displayRouletteCard(restaurant, false);
        
        currentIndex++;
        
        // 次の更新をスケジュール
        setTimeout(updateDisplay, interval);
    }
    
    // アニメーション開始
    updateDisplay();
}

/**
 * 表示順序の配列を生成（ランダムだが偏りなく）
 * @param {number} poolSize - レストラン総数
 * @param {number} count - 生成する表示回数
 * @return {array} インデックスの配列
 */
function generateDisplaySequence(poolSize, count) {
    const sequence = [];
    for (let i = 0; i < count; i++) {
        sequence.push(Math.floor(Math.random() * poolSize));
    }
    return sequence;
}

/**
 * ルーレット用のカード表示
 * @param {object} restaurant - レストラン情報
 * @param {boolean} isFinal - 最終選択かどうか
 */
function displayRouletteCard(restaurant, isFinal) {
    const card = document.getElementById('roulette-card');
    
    // フェードアウト
    card.classList.add('fade-out');
    
    setTimeout(() => {
        // 内容を更新
        document.getElementById('roulette-restaurant-name').textContent = restaurant.name;
        document.getElementById('roulette-restaurant-genre').textContent = restaurant.genre;
        document.getElementById('roulette-restaurant-budget').textContent = restaurant.budget_name || '予算不明';
        
        // 写真がある場合は表示
        const photoElement = document.getElementById('roulette-restaurant-photo');
        if (restaurant.photo) {
            photoElement.src = restaurant.photo;
            photoElement.style.display = 'block';
        } else {
            photoElement.style.display = 'none';
        }
        
        // 最終選択の場合はハイライト
        if (isFinal) {
            card.classList.add('final-selection');
        } else {
            card.classList.remove('final-selection');
        }
        
        // フェードイン
        card.classList.remove('fade-out');
        card.classList.add('fade-in');
        
        setTimeout(() => {
            card.classList.remove('fade-in');
        }, 300);
    }, 150);
}
```

### 2. 既存ルーレット処理の改修
`/roulette` APIのレスポンス受信後の処理を変更:
```javascript
// ルーレットボタンのクリックイベント
document.getElementById('roulette-btn').addEventListener('click', async function() {
    // ... 既存の検索条件収集処理 ...
    
    try {
        const response = await fetch('/roulette', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 検索結果の全レストランと最終選択を取得
            // （サーバー側で全レストランリストも返すように改修が必要）
            const allRestaurants = data.all_restaurants || [data.restaurant];
            const finalRestaurant = data.restaurant;
            
            // アニメーション実行
            playRouletteAnimation(allRestaurants, finalRestaurant, () => {
                // アニメーション完了後、詳細カードを表示
                displayRestaurantDetail(finalRestaurant);
            });
        } else {
            // エラー処理
            showError(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('検索中にエラーが発生しました');
    }
});
```

### 3. サーバー側の改修（`app.py`）
レスポンスに全レストランリストを追加:
```python
@app.route('/roulette', methods=['POST'])
def roulette():
    # ... 既存の検索処理 ...
    
    # 成功時のレスポンスに全レストランリストを追加
    response_data = {
        'success': True,
        'restaurant': selected_restaurant,
        'all_restaurants': [
            {
                'id': r['id'],
                'name': r['name'],
                'genre': r['genre'],
                'budget_name': r['budget_name'],
                'photo': r.get('photo', '')
            }
            for r in restaurants[:20]  # 最大20件を返す（アニメーション用）
        ],
        # ... その他の既存フィールド ...
    }
    
    return jsonify(response_data)
```

### 4. HTML追加箇所
ルーレット表示用のカードを追加:
```html
<!-- ルーレットアニメーション表示エリア -->
<div id="roulette-display" class="roulette-display" style="display: none;">
    <div id="roulette-card" class="roulette-card">
        <div class="roulette-card-content">
            <img id="roulette-restaurant-photo" src="" alt="" class="roulette-photo">
            <h3 id="roulette-restaurant-name" class="roulette-name"></h3>
            <p id="roulette-restaurant-genre" class="roulette-genre"></p>
            <p id="roulette-restaurant-budget" class="roulette-budget"></p>
        </div>
    </div>
    <div class="roulette-spinner">
        <div class="spinner-icon">🎲</div>
    </div>
</div>
```

### 5. CSS追加
```css
/* ルーレット表示エリア */
.roulette-display {
    position: relative;
    margin: 30px auto;
    max-width: 500px;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.roulette-display.spinning {
    animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

/* ルーレットカード */
.roulette-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    min-height: 200px;
    position: relative;
    overflow: hidden;
}

.roulette-card.fade-out {
    opacity: 0;
    transform: translateY(-10px);
    transition: opacity 0.15s, transform 0.15s;
}

.roulette-card.fade-in {
    opacity: 1;
    transform: translateY(0);
    transition: opacity 0.3s, transform 0.3s;
}

.roulette-card.final-selection {
    border: 3px solid #ffd700;
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
    animation: finalGlow 0.5s ease-in-out;
}

@keyframes finalGlow {
    0%, 100% { box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
    50% { box-shadow: 0 0 40px rgba(255, 215, 0, 0.8); }
}

/* ルーレットカードの内容 */
.roulette-photo {
    width: 100%;
    height: 150px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 10px;
}

.roulette-name {
    font-size: 1.3rem;
    font-weight: bold;
    color: #333;
    margin: 10px 0;
}

.roulette-genre {
    color: #666;
    margin: 5px 0;
}

.roulette-budget {
    color: #ff6b6b;
    font-weight: bold;
}

/* スピナーアイコン */
.roulette-spinner {
    text-align: center;
    margin-top: 15px;
}

.spinner-icon {
    font-size: 2rem;
    animation: spin 0.8s linear infinite;
}

.roulette-display.stopped .spinner-icon {
    animation: none;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
```

## 学習ポイント
- JavaScriptのタイマー関数（`setTimeout`, `setInterval`）
- アニメーションの制御（進行度計算、イージング）
- CSS transitionとanimationの使い分け
- 非同期処理とコールバック
- DOM操作とクラス制御（`classList.add/remove`）

## 発展課題（余力があれば）
1. 効果音の追加（ルーレット回転音、決定音）
2. スロットマシン風の演出（3列のレストランが順番に止まる）
3. アニメーション速度の設定機能（速い/普通/遅い）
4. 背景エフェクト（紙吹雪が舞うなど）
