# 案4: お気に入りレストラン機能

## ねらい
ユーザがルーレットで見つけたレストランを「お気に入り」として保存できる機能を追加し、後で簡単にアクセスできるようにする。

## 短時間で改修可能な理由
- ブラウザの`localStorage`を使用することで、データベース設計やサーバー側の変更が不要
- 既存のレストラン情報構造をそのまま活用できる
- UI側はボタンとリスト表示を追加するだけで済む
- JavaScriptの基本的な配列操作とJSON変換のみで実装可能
- **改修時間目安: 2〜3時間**

## 改修に必要なビジネスロジック

### 1. データ保存ロジック（JavaScript）
```javascript
// お気に入りに追加
function addToFavorites(restaurant) {
    // localStorageから既存のお気に入りを取得
    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    
    // 重複チェック（同じIDがあれば追加しない）
    if (!favorites.find(r => r.id === restaurant.id)) {
        favorites.push(restaurant);
        localStorage.setItem('favorites', JSON.stringify(favorites));
        return true;
    }
    return false; // 既に登録済み
}

// お気に入りから削除
function removeFromFavorites(restaurantId) {
    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    favorites = favorites.filter(r => r.id !== restaurantId);
    localStorage.setItem('favorites', JSON.stringify(favorites));
}

// お気に入り一覧を取得
function getFavorites() {
    return JSON.parse(localStorage.getItem('favorites') || '[]');
}
```

### 2. UI追加箇所

#### 2.1 レストランカードに「お気に入り」ボタンを追加
`templates/index.html`の`<div class="action-buttons">`内に以下を追加:
```html
<button id="favorite-btn" class="btn btn-favorite">
    <span class="btn-icon">⭐</span>
    お気に入りに追加
</button>
```

#### 2.2 お気に入り一覧表示セクションを追加
ヘッダー下部に新しいセクションを追加:
```html
<section class="favorites-section">
    <h2 class="section-title">
        <span class="title-icon">⭐</span>
        お気に入りのお店
    </h2>
    <div id="favorites-list" class="favorites-grid">
        <!-- お気に入りカードが動的に追加される -->
    </div>
</section>
```

### 3. イベントハンドラの実装
```javascript
// お気に入りボタンのクリックイベント
document.getElementById('favorite-btn').addEventListener('click', function() {
    const currentRestaurant = getCurrentRestaurantData(); // 現在表示中のレストラン情報
    
    if (addToFavorites(currentRestaurant)) {
        alert('お気に入りに追加しました！');
        this.disabled = true;
        this.innerHTML = '<span class="btn-icon">✅</span>追加済み';
    } else {
        alert('このお店は既にお気に入りに登録されています。');
    }
    
    renderFavoritesList(); // 一覧を再描画
});

// お気に入り一覧を描画
function renderFavoritesList() {
    const favorites = getFavorites();
    const listElement = document.getElementById('favorites-list');
    
    if (favorites.length === 0) {
        listElement.innerHTML = '<p class="empty-message">まだお気に入りがありません</p>';
        return;
    }
    
    listElement.innerHTML = favorites.map(restaurant => `
        <div class="favorite-card">
            <h3>${restaurant.name}</h3>
            <p>${restaurant.genre}</p>
            <p>💰 ${restaurant.budget_display}</p>
            <div class="favorite-actions">
                <a href="${restaurant.map_url}" target="_blank" class="btn-mini">地図</a>
                <button onclick="removeFromFavorites('${restaurant.id}')" class="btn-mini btn-remove">削除</button>
            </div>
        </div>
    `).join('');
}
```

### 4. CSS追加
```css
.favorites-section {
    margin: 20px 0;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 8px;
}

.favorites-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
    margin-top: 15px;
}

.favorite-card {
    background: white;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-favorite {
    background-color: #ffd700;
    color: #333;
}

.btn-favorite:hover {
    background-color: #ffed4e;
}
```

## 学習ポイント
- ブラウザのlocalStorageの使い方
- JSONデータの保存と取得（`JSON.stringify` / `JSON.parse`）
- 配列操作（`filter`, `find`, `map`）
- DOM操作とイベントハンドリング
- シンプルなステート管理の考え方

## 発展課題（余力があれば）
1. お気に入りの件数上限を設定（例: 10件まで）
2. お気に入りに追加した日時を記録
3. お気に入りをエクスポート（JSONファイルダウンロード）
4. お気に入りをインポート（JSONファイルアップロード）
