/**
 * Lunch Roulette - メインJavaScript
 * ルーレット機能とレストラン表示のフロントエンド処理
 */

// DOM要素の取得
const rouletteBtn = document.getElementById('roulette-btn');
const retryBtn = document.getElementById('retry-btn');
const errorMessage = document.getElementById('error-message');
const restaurantSection = document.getElementById('restaurant-section');

// ボタン内の要素
const btnText = rouletteBtn.querySelector('.btn-text');
const btnLoading = rouletteBtn.querySelector('.btn-loading');

// レストランカード内の要素
const restaurantName = document.getElementById('restaurant-name');
const restaurantGenre = document.getElementById('restaurant-genre');
const restaurantImage = document.getElementById('restaurant-image');
const restaurantAddress = document.getElementById('restaurant-address');
const restaurantBudget = document.getElementById('restaurant-budget');
const walkingTime = document.getElementById('walking-time');
const restaurantHours = document.getElementById('restaurant-hours');
const restaurantCatch = document.getElementById('restaurant-catch');
const distanceBadge = document.getElementById('distance-badge');
const mapLink = document.getElementById('map-link');
const hotpepperLink = document.getElementById('hotpepper-link');

/**
 * ローディング状態の表示/非表示を切り替える
 * @param {boolean} isLoading - ローディング状態かどうか
 */
function toggleLoading(isLoading) {
    if (isLoading) {
        rouletteBtn.disabled = true;
        rouletteBtn.classList.add('loading');
        btnText.style.display = 'none';
        btnLoading.style.display = 'flex';
    } else {
        rouletteBtn.disabled = false;
        rouletteBtn.classList.remove('loading');
        btnText.style.display = 'flex';
        btnLoading.style.display = 'none';
    }
}

/**
 * エラーメッセージの表示
 * @param {string} message - エラーメッセージ
 */
function showError(message) {
    const errorText = errorMessage.querySelector('.error-text');
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
    
    // 5秒後に自動的に非表示
    setTimeout(() => {
        hideError();
    }, 5000);
}

/**
 * エラーメッセージの非表示
 */
function hideError() {
    errorMessage.style.display = 'none';
}

/**
 * レストランカードの表示
 * @param {Object} data - レストランデータ
 */
function displayRestaurant(data) {
    const { restaurant, distance, weather } = data;
    
    // レストラン基本情報
    restaurantName.textContent = restaurant.name;
    restaurantGenre.textContent = restaurant.genre;
    restaurantAddress.textContent = restaurant.address;
    restaurantBudget.textContent = restaurant.budget_display;
    walkingTime.textContent = distance.time_display;
    restaurantHours.textContent = restaurant.hours || '営業時間情報なし';
    restaurantCatch.textContent = restaurant.catch || restaurant.summary || '';
    
    // 距離バッジ
    distanceBadge.textContent = distance.distance_display;
    
    // レストラン画像
    if (restaurant.photo_url && restaurant.photo_url !== 'no-image') {
        restaurantImage.src = restaurant.photo_url;
        restaurantImage.alt = `${restaurant.name}の写真`;
        restaurantImage.style.display = 'block';
    } else {
        // デフォルト画像
        restaurantImage.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXpl';
        restaurantImage.alt = 'レストラン画像なし';
        restaurantImage.style.display = 'block';
    }
    
    // リンク設定
    mapLink.href = restaurant.map_url;
    hotpepperLink.href = restaurant.hotpepper_url;
    
    // レストランセクションを表示
    restaurantSection.style.display = 'block';
    
    // スムーズスクロール
    restaurantSection.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
    });
    
    console.log('レストラン表示完了', restaurant.name);
}

/**
 * レストランセクションを非表示
 */
function hideRestaurant() {
    restaurantSection.style.display = 'none';
}

/**
 * ルーレット実行
 */
async function executeRoulette() {
    try {
        // ローディング開始
        toggleLoading(true);
        hideError();
        hideRestaurant();
        
        console.log('ルーレット開始..');
        
        // APIリクエスト
        const response = await fetch('/roulette', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        });
        
        // レスポンス処理
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // エラーレスポンスの処理
        if (data.error || !data.success) {
            const errorMsg = data.message || 'レストラン検索中にエラーが発生しました';
            throw new Error(errorMsg);
        }
        
        // 成功時の処理
        if (data.success && data.restaurant) {
            console.log('ルーレット成功:', data);
            displayRestaurant(data);
        } else {
            throw new Error(data.message || 'レストランデータが正しくありません');
        }
        
    } catch (error) {
        console.error('ルーレットエラー:', error);
        
        // エラーメッセージの表示
        let errorMessage = 'レストラン検索中にエラーが発生しました';
        
        if (error.message.includes('Failed to fetch')) {
            errorMessage = 'ネットワークエラーが発生しました。インターネット接続を確認してください。';
        } else if (error.message.includes('HTTP 500')) {
            errorMessage = 'サーバーエラーが発生しました。しばらく時間を置いて再度お試しください。';
        } else if (error.message.includes('HTTP 429')) {
            errorMessage = 'アクセスが集中しています。しばらく時間を置いて再度お試しください。';
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        showError(errorMessage);
        
    } finally {
        // ローディング終了
        toggleLoading(false);
    }
}

/**
 * ページ読み込み完了後の初期化
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Lunch Roulette JavaScript 初期化完了');
    
    // ルーレットボタンのクリックイベント
    rouletteBtn.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('ルーレットボタンクリック');
        executeRoulette();
    });
    
    // 再ルーレットボタンのクリックイベント
    if (retryBtn) {
        retryBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('再ルーレットボタンクリック');
            executeRoulette();
        });
    }
    
    // エラーメッセージのクリックで非表示
    errorMessage.addEventListener('click', function() {
        hideError();
    });
    
    // キーボードショートカット
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !rouletteBtn.disabled) {
            e.preventDefault();
            executeRoulette();
        }
    });
    
    console.log('イベントリスナー設定完了');
});

/**
 * ページ離脱時の処理
 */
window.addEventListener('beforeunload', function() {
    // ルーレット中は警告を表示
    if (rouletteBtn.disabled) {
        return 'レストラン検索中です。ページを離れますか？';
    }
});

/**
 * エラーハンドリング
 */
window.addEventListener('error', function(e) {
    // JavaScriptエラーのキャッチ
    console.error('JavaScript エラー:', e.error);
    showError('予期しないエラーが発生しました。ページを再読み込みしてください。');
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('未処理のPromiseエラー:', e.reason);
    showError('通信エラーが発生しました。しばらく時間を置いて再度お試しください。');
    e.preventDefault();
});
