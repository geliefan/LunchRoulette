# 案5: 営業時間の判定機能

## ねらい
現在時刻が営業時間内かどうかを判定し、「今営業中」「営業時間外」などのバッジを表示することで、ユーザがすぐに利用できるかどうかを把握しやすくする。

## 短時間で改修可能な理由
- 既存のレストラン情報に営業時間（`open`フィールド）が含まれている
- JavaScriptの`Date`オブジェクトで現在時刻を取得できる
- 簡単な文字列解析とif文で営業時間を判定できる
- UI側はバッジを追加するだけで済む
- **改修時間目安: 2〜3時間**

## 改修に必要なビジネスロジック

### 1. 営業時間解析ロジック（JavaScript）
```javascript
/**
 * 営業時間文字列を解析して、現在営業中かどうかを判定
 * @param {string} openingHours - 営業時間文字列（例: "11:00～14:00、17:00～23:00"）
 * @return {object} { isOpen: boolean, message: string }
 */
function checkOpeningStatus(openingHours) {
    // 現在時刻を取得
    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const currentTime = currentHour * 60 + currentMinute; // 分単位に変換
    
    // 営業時間が不明な場合
    if (!openingHours || openingHours.trim() === '') {
        return {
            isOpen: null,
            message: '営業時間不明',
            badgeClass: 'badge-unknown'
        };
    }
    
    // 24時間営業の場合
    if (openingHours.includes('24時間') || openingHours.includes('24時間営業')) {
        return {
            isOpen: true,
            message: '24時間営業中',
            badgeClass: 'badge-open'
        };
    }
    
    // 定休日の場合
    if (openingHours.includes('定休日') || openingHours.includes('休業日')) {
        return {
            isOpen: false,
            message: '定休日',
            badgeClass: 'badge-closed'
        };
    }
    
    // 時間帯を抽出（例: "11:00～14:00" または "11:00-14:00"）
    const timePattern = /(\d{1,2}):(\d{2})[～~-](\d{1,2}):(\d{2})/g;
    const matches = [...openingHours.matchAll(timePattern)];
    
    if (matches.length === 0) {
        return {
            isOpen: null,
            message: '営業時間不明',
            badgeClass: 'badge-unknown'
        };
    }
    
    // 各営業時間帯をチェック
    for (const match of matches) {
        const openHour = parseInt(match[1]);
        const openMinute = parseInt(match[2]);
        const closeHour = parseInt(match[3]);
        const closeMinute = parseInt(match[4]);
        
        const openTime = openHour * 60 + openMinute;
        let closeTime = closeHour * 60 + closeMinute;
        
        // 深夜営業対応（例: 23:00～02:00）
        if (closeTime < openTime) {
            closeTime += 24 * 60; // 翌日扱い
            if (currentTime < openTime) {
                // 深夜帯の判定用に現在時刻も翌日扱い
                const adjustedCurrentTime = currentTime + 24 * 60;
                if (adjustedCurrentTime >= openTime && adjustedCurrentTime <= closeTime) {
                    return {
                        isOpen: true,
                        message: '営業中（深夜営業）',
                        badgeClass: 'badge-open'
                    };
                }
            }
        }
        
        // 通常の営業時間チェック
        if (currentTime >= openTime && currentTime <= closeTime) {
            // 閉店30分前の場合は「まもなく閉店」
            if (closeTime - currentTime <= 30) {
                return {
                    isOpen: true,
                    message: '営業中（まもなく閉店）',
                    badgeClass: 'badge-closing-soon'
                };
            }
            
            return {
                isOpen: true,
                message: '営業中',
                badgeClass: 'badge-open'
            };
        }
    }
    
    // 営業時間外
    return {
        isOpen: false,
        message: '営業時間外',
        badgeClass: 'badge-closed'
    };
}
```

### 2. UI表示処理
```javascript
// レストランカードに営業状況バッジを追加
function displayRestaurant(restaurant) {
    // 既存のレストラン表示処理...
    
    // 営業状況を判定
    const openingStatus = checkOpeningStatus(restaurant.hours);
    
    // バッジHTML生成
    const statusBadgeHTML = `
        <span class="opening-status-badge ${openingStatus.badgeClass}">
            ${openingStatus.message}
        </span>
    `;
    
    // レストラン名の横にバッジを追加
    document.getElementById('restaurant-name').insertAdjacentHTML('afterend', statusBadgeHTML);
}
```

### 3. HTML修正箇所
`templates/index.html`のレストラン名表示部分を修正:
```html
<div class="card-header">
    <div class="header-top">
        <h3 class="restaurant-name" id="restaurant-name"></h3>
        <!-- 営業状況バッジがここに動的に追加される -->
    </div>
    <span class="restaurant-genre" id="restaurant-genre"></span>
</div>
```

### 4. CSS追加
```css
/* 営業状況バッジの共通スタイル */
.opening-status-badge {
    display: inline-block;
    padding: 4px 12px;
    margin-left: 10px;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: bold;
    vertical-align: middle;
}

/* 営業中（緑） */
.badge-open {
    background-color: #4caf50;
    color: white;
}

/* 営業時間外（グレー） */
.badge-closed {
    background-color: #9e9e9e;
    color: white;
}

/* まもなく閉店（オレンジ） */
.badge-closing-soon {
    background-color: #ff9800;
    color: white;
}

/* 営業時間不明（薄いグレー） */
.badge-unknown {
    background-color: #e0e0e0;
    color: #666;
}

/* ヘッダーのレイアウト調整 */
.header-top {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
}
```

## テストケース例
以下のケースで正しく動作することを確認:

1. **通常営業時間内**
   - 営業時間: "11:00～14:00、17:00～23:00"
   - 現在時刻: 12:30 → "営業中"

2. **営業時間外**
   - 営業時間: "11:00～14:00、17:00～23:00"
   - 現在時刻: 15:00 → "営業時間外"

3. **24時間営業**
   - 営業時間: "24時間営業"
   - 現在時刻: いつでも → "24時間営業中"

4. **深夜営業**
   - 営業時間: "17:00～02:00"
   - 現在時刻: 01:00 → "営業中（深夜営業）"

5. **閉店間際**
   - 営業時間: "11:00～14:00"
   - 現在時刻: 13:45 → "営業中（まもなく閉店）"

## 学習ポイント
- JavaScriptの`Date`オブジェクトの使い方
- 正規表現による文字列パターンマッチング（`matchAll`）
- 時刻の比較ロジック（分単位への変換）
- 条件分岐（if-else）の組み立て方
- CSS クラスによる動的スタイル変更

## 発展課題（余力があれば）
1. 曜日別の営業時間に対応（例: 月〜金と土日で営業時間が異なる）
2. 定休日情報（`close`フィールド）も考慮した判定
3. 「あと○分で閉店」のようなカウントダウン表示
4. 次回の営業開始時刻を表示（例: 「17:00から営業開始」）
