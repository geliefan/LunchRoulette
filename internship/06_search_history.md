# 案6: 検索履歴機能

## ねらい
ユーザが過去に検索した条件（位置、予算、ジャンルなど）を履歴として保存し、「前回と同じ条件で検索」や「よく使う条件で検索」を簡単に実行できるようにする。

## 短時間で改修可能な理由
- ブラウザの`localStorage`を使用することで、サーバー側の変更が不要
- 検索条件はすでにJavaScriptで管理されている
- 履歴の保存・取得は配列操作とJSON変換のみ
- UI側はドロップダウンまたは履歴リストを追加するだけで済む
- **改修時間目安: 2〜3時間**

## 改修に必要なビジネスロジック

### 1. 検索履歴管理ロジック（JavaScript）
```javascript
// 検索履歴の最大保存件数
const MAX_HISTORY = 10;

/**
 * 検索条件を履歴に保存
 * @param {object} searchConditions - 検索条件オブジェクト
 */
function saveSearchHistory(searchConditions) {
    // 現在時刻をタイムスタンプとして追加
    const historyItem = {
        ...searchConditions,
        timestamp: new Date().toISOString(),
        displayName: generateHistoryDisplayName(searchConditions)
    };
    
    // 既存の履歴を取得
    let history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
    
    // 同じ条件が既にある場合は削除（重複防止）
    history = history.filter(item => 
        !isSameConditions(item, searchConditions)
    );
    
    // 新しい履歴を先頭に追加
    history.unshift(historyItem);
    
    // 最大件数を超えた場合は古いものを削除
    if (history.length > MAX_HISTORY) {
        history = history.slice(0, MAX_HISTORY);
    }
    
    // localStorageに保存
    localStorage.setItem('searchHistory', JSON.stringify(history));
}

/**
 * 検索履歴を取得
 * @return {array} 検索履歴の配列
 */
function getSearchHistory() {
    return JSON.parse(localStorage.getItem('searchHistory') || '[]');
}

/**
 * 検索条件が同じかどうかを判定
 * @param {object} a - 検索条件A
 * @param {object} b - 検索条件B
 * @return {boolean} 同じ条件ならtrue
 */
function isSameConditions(a, b) {
    return (
        a.location_mode === b.location_mode &&
        a.budget_code === b.budget_code &&
        a.genre_code === b.genre_code &&
        a.max_walking_time_min === b.max_walking_time_min &&
        a.middle_area_code === b.middle_area_code
    );
}

/**
 * 検索条件から表示用の名前を生成
 * @param {object} conditions - 検索条件オブジェクト
 * @return {string} 表示用の名前
 */
function generateHistoryDisplayName(conditions) {
    let parts = [];
    
    // 位置情報
    if (conditions.location_mode === 'area' && conditions.middle_area_code) {
        const areaName = getAreaName(conditions.middle_area_code);
        parts.push(areaName);
    } else {
        parts.push('現在地');
    }
    
    // 徒歩時間（現在地モードのみ）
    if (conditions.location_mode === 'current') {
        parts.push(`徒歩${conditions.max_walking_time_min}分`);
    }
    
    // 予算
    if (conditions.budget_code) {
        const budgetNames = {
            'B009': '〜500円',
            'B010': '〜1000円',
            'B011': '〜1500円',
            'B001': '〜2000円',
            'B002': '〜3000円'
        };
        parts.push(budgetNames[conditions.budget_code]);
    }
    
    // ジャンル
    if (conditions.genre_code) {
        const genreName = getGenreName(conditions.genre_code);
        parts.push(genreName);
    }
    
    return parts.join(' / ');
}

/**
 * 検索履歴から条件を復元
 * @param {object} historyItem - 履歴アイテム
 */
function restoreSearchConditions(historyItem) {
    // 位置モード選択
    if (historyItem.location_mode === 'area') {
        document.getElementById('mode-area').click();
        document.getElementById('area').value = historyItem.middle_area_code || '';
    } else {
        document.getElementById('mode-current').click();
        document.getElementById('walking-time-select').value = historyItem.max_walking_time_min || 10;
    }
    
    // 予算選択
    document.getElementById('budget').value = historyItem.budget_code || '';
    
    // ジャンル選択
    document.getElementById('genre').value = historyItem.genre_code || '';
    
    // 検索実行（オプション）
    // document.getElementById('roulette-btn').click();
}

/**
 * 検索履歴を削除
 */
function clearSearchHistory() {
    if (confirm('検索履歴をすべて削除しますか？')) {
        localStorage.removeItem('searchHistory');
        renderSearchHistory();
    }
}
```

### 2. UI表示処理
```javascript
/**
 * 検索履歴を画面に描画
 */
function renderSearchHistory() {
    const history = getSearchHistory();
    const historyContainer = document.getElementById('search-history-list');
    
    if (history.length === 0) {
        historyContainer.innerHTML = '<p class="empty-message">検索履歴はありません</p>';
        return;
    }
    
    historyContainer.innerHTML = history.map((item, index) => `
        <div class="history-item" onclick="restoreSearchConditions(${JSON.stringify(item).replace(/"/g, '&quot;')})">
            <div class="history-info">
                <span class="history-name">${item.displayName}</span>
                <span class="history-date">${formatDate(item.timestamp)}</span>
            </div>
            <button class="history-delete-btn" onclick="event.stopPropagation(); deleteHistoryItem(${index})">
                ✕
            </button>
        </div>
    `).join('');
}

/**
 * タイムスタンプを読みやすい形式に変換
 * @param {string} isoString - ISO形式の日時文字列
 * @return {string} 表示用の日時文字列
 */
function formatDate(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMinutes = Math.floor(diffMs / 60000);
    
    if (diffMinutes < 1) return 'たった今';
    if (diffMinutes < 60) return `${diffMinutes}分前`;
    
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours}時間前`;
    
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, '0');
    
    return `${month}/${day} ${hours}:${minutes}`;
}

/**
 * 履歴アイテムを削除
 * @param {number} index - 削除する履歴のインデックス
 */
function deleteHistoryItem(index) {
    let history = getSearchHistory();
    history.splice(index, 1);
    localStorage.setItem('searchHistory', JSON.stringify(history));
    renderSearchHistory();
}
```

### 3. 検索実行時の履歴保存処理
既存の`roulette`ボタンのクリックイベントに追加:
```javascript
document.getElementById('roulette-btn').addEventListener('click', function() {
    // 検索条件を収集
    const searchConditions = {
        location_mode: currentLocationMode,
        budget_code: document.getElementById('budget').value,
        genre_code: document.getElementById('genre').value,
        max_walking_time_min: parseInt(document.getElementById('walking-time-select').value),
        middle_area_code: document.getElementById('area').value,
        lunch: 1
    };
    
    // 履歴に保存
    saveSearchHistory(searchConditions);
    
    // 既存のルーレット処理を実行...
});
```

### 4. HTML追加箇所
検索条件セクションの下に履歴セクションを追加:
```html
<!-- 検索履歴セクション -->
<section class="search-history-section">
    <div class="search-history-box">
        <div class="history-header">
            <h2 class="box-title">
                <span class="title-icon">🕒</span>
                検索履歴
            </h2>
            <button class="history-clear-btn" onclick="clearSearchHistory()">
                すべて削除
            </button>
        </div>
        <div id="search-history-list" class="history-list">
            <!-- 履歴アイテムが動的に追加される -->
        </div>
    </div>
</section>
```

### 5. CSS追加
```css
/* 検索履歴セクション */
.search-history-section {
    margin: 20px 0;
}

.search-history-box {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.history-clear-btn {
    background: #f44336;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
}

.history-clear-btn:hover {
    background: #d32f2f;
}

.history-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.history-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: #f5f5f5;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s;
}

.history-item:hover {
    background: #e0e0e0;
}

.history-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.history-name {
    font-weight: 500;
    color: #333;
}

.history-date {
    font-size: 0.85rem;
    color: #666;
}

.history-delete-btn {
    background: none;
    border: none;
    color: #999;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 4px 8px;
}

.history-delete-btn:hover {
    color: #f44336;
}

.empty-message {
    text-align: center;
    color: #999;
    padding: 20px;
}
```

## 学習ポイント
- localStorageを使ったデータの永続化
- 配列操作（`filter`, `slice`, `unshift`）
- オブジェクトの比較とコピー（スプレッド構文`...`）
- 日時の扱い方（`Date`オブジェクト、ISO形式）
- 相対時刻表示（「○分前」「○時間前」）
- イベント伝播の制御（`event.stopPropagation()`）

## 発展課題（余力があれば）
1. 履歴にニックネーム（別名）を付ける機能
2. 頻度の高い条件を「よく使う検索」として別表示
3. 履歴のエクスポート/インポート機能
4. 検索履歴から統計情報を表示（よく使う予算帯、ジャンルなど）
