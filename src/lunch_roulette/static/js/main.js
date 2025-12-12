/**
 * Lunch Roulette - メインJavaScript
 * ルーレット機能とレストラン表示のフロントエンド処理
 * 
 * このファイルの役割:
 * 1. 「ルーレットを回す」ボタンが押された時の処理
 * 2. GPS位置情報の取得
 * 3. 検索条件の収集
 * 4. サーバーにレストラン検索をリクエスト
 * 5. 結果を画面に表示
 * 6. エラーが発生した時の処理
 */

// ===== HTML要素の取得 =====
// document.getElementById = HTMLの中から特定のIDを持つ要素を探して取得する関数

// メインボタン
const rouletteBtn = document.getElementById('roulette-btn');  // 「ルーレットを回す」ボタン
const retryBtn = document.getElementById('retry-btn');        // 「もう一度回す」ボタン
const gpsBtn = document.getElementById('gps-btn');            // GPS位置取得ボタン

// 検索条件の入力要素
const walkingTimeSelect = document.getElementById('walking-time-select');  // 徒歩時間選択
const budgetSelect = document.getElementById('budget');                     // 予算選択
const genreSelect = document.getElementById('genre');                       // ジャンル選択
const areaSelect = document.getElementById('area');                         // エリア選択
const gpsStatus = document.getElementById('gps-status');            // GPSステータス表示

// モード切り替えボタン
const modeCurrentBtn = document.getElementById('mode-current');  // 現在地モードボタン
const modeAreaBtn = document.getElementById('mode-area');        // エリアモードボタン

// 条件グループの表示/非表示制御用
const walkingTimeGroup = document.getElementById('walking-time-group');  // 徒歩時間グループ
const areaSelectGroup = document.getElementById('area-select-group');    // エリア選択グループ

// メッセージ表示エリア
const errorMessage = document.getElementById('error-message');          // エラーメッセージ表示エリア
const restaurantSection = document.getElementById('restaurant-section'); // レストラン情報表示エリア

// ボタン内の要素（ボタンの状態を変更するために使用）
const btnText = rouletteBtn.querySelector('.btn-text');       // ボタンのテキスト部分
const btnLoading = rouletteBtn.querySelector('.btn-loading'); // ローディング表示部分

// レストラン情報を表示する要素
// これらの要素にレストランの情報を設定すると、画面に表示されます
const restaurantName = document.getElementById('restaurant-name');       // 店名
const restaurantGenre = document.getElementById('restaurant-genre');     // ジャンル
const restaurantImage = document.getElementById('restaurant-image');     // 写真
const restaurantAddress = document.getElementById('restaurant-address'); // 住所
const restaurantBudget = document.getElementById('restaurant-budget');   // 予算
const walkingTime = document.getElementById('walking-time');             // 徒歩時間
const restaurantHours = document.getElementById('restaurant-hours');     // 営業時間
const restaurantCatch = document.getElementById('restaurant-catch');     // キャッチコピー
const distanceBadge = document.getElementById('distance-badge');         // 距離バッジ
const mapLink = document.getElementById('map-link');                     // 地図リンク
const hotpepperLink = document.getElementById('hotpepper-link');         // ホットペッパーリンク

// ===== グローバル変数 =====
let userLocation = null;  // GPS取得した位置情報を保持する変数
let currentLocationMode = 'current';  // 現在の位置指定モード（'current' or 'area'）

/**
 * ローディング状態の表示/非表示を切り替える関数
 * 
 * レストラン検索中は、ボタンをクリックできないようにし、
 * 「検索中...」という表示に切り替えます。
 * 
 * @param {boolean} isLoading - true=検索中、false=検索完了
 */
function toggleLoading(isLoading) {
    if (isLoading) {
        // 検索中の状態にする
        rouletteBtn.disabled = true;                // ボタンを無効化（クリックできなくする）
        rouletteBtn.classList.add('loading');       // ローディング用のCSSクラスを追加
        btnText.style.display = 'none';             // 通常のテキストを非表示
        btnLoading.style.display = 'flex';          // 「検索中...」を表示
    } else {
        // 検索完了の状態にする
        rouletteBtn.disabled = false;               // ボタンを有効化
        rouletteBtn.classList.remove('loading');    // ローディング用のCSSクラスを削除
        btnText.style.display = 'flex';             // 通常のテキストを表示
        btnLoading.style.display = 'none';          // 「検索中...」を非表示
    }
}

/**
 * エラーメッセージを画面に表示する関数
 * 
 * @param {string} message - 表示するエラーメッセージ
 */
function showError(message) {
    const errorText = errorMessage.querySelector('.error-text');
    
    // 改行を<br>タグに変換して表示
    const formattedMessage = message.replace(/\n/g, '<br>');
    errorText.innerHTML = formattedMessage;       // エラーメッセージのHTMLを設定
    errorMessage.style.display = 'flex';          // エラーメッセージエリアを表示
    
    // 10秒後に自動的に非表示にする（長めのメッセージに対応）
    setTimeout(() => {
        hideError();
    }, 10000);  // 10000ミリ秒 = 10秒
}

/**
 * エラーメッセージを非表示にする関数
 */
function hideError() {
    errorMessage.style.display = 'none';
}

/**
 * GPS位置情報を取得する関数
 * 
 * ブラウザのGeolocation APIを使用してユーザーの現在地を取得します。
 * 取得した位置情報はuserLocation変数に保存され、ルーレット実行時に使用されます。
 */
function getGPSLocation() {
    // Geolocation APIがブラウザでサポートされているか確認
    if (!navigator.geolocation) {
        gpsStatus.textContent = '❌ このブラウザはGPS機能に対応していません';
        gpsStatus.className = 'gps-status error';
        return;
    }
    
    // GPS取得中の表示
    gpsBtn.disabled = true;
    gpsStatus.textContent = '📡 位置情報を取得中...';
    gpsStatus.className = 'gps-status';
    
    // Geolocation APIで位置情報を取得
    navigator.geolocation.getCurrentPosition(
        // 成功時のコールバック
        (position) => {
            userLocation = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            };
            
            gpsStatus.textContent = `✅ GPS位置を取得しました（精度: ${Math.round(position.coords.accuracy)}m）`;
            gpsStatus.className = 'gps-status success';
            gpsBtn.disabled = false;
            
            // GPS位置取得成功後、画面上の位置情報を更新
            updateLocationDisplay(userLocation);
            
            console.log('GPS位置情報取得成功:', userLocation);
        },
        // エラー時のコールバック
        (error) => {
            let errorMsg = '';
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    errorMsg = '❌ 位置情報の使用が拒否されました';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMsg = '❌ 位置情報を取得できません';
                    break;
                case error.TIMEOUT:
                    errorMsg = '❌ 位置情報の取得がタイムアウトしました';
                    break;
                default:
                    errorMsg = '❌ 位置情報の取得に失敗しました';
            }
            
            gpsStatus.textContent = errorMsg;
            gpsStatus.className = 'gps-status error';
            gpsBtn.disabled = false;
            userLocation = null;
            
            console.error('GPS位置情報取得エラー:', error);
        },
        // オプション
        {
            enableHighAccuracy: true,  // 高精度モード
            timeout: 10000,            // タイムアウト: 10秒
            maximumAge: 300000         // キャッシュ有効期限: 5分
        }
    );
}

/**
 * 位置情報表示を更新する関数
 * 
 * GPS位置取得後、画面上の都市名と座標を更新します。
 * 逆ジオコーディング（座標から住所を取得）を行います。
 * 
 * @param {Object} location - 位置情報オブジェクト
 * @param {number} location.latitude - 緯度
 * @param {number} location.longitude - 経度
 */
function updateLocationDisplay(location) {
    // 画面上の座標表示を更新
    const coordinatesElement = document.querySelector('.coordinates');
    if (coordinatesElement) {
        coordinatesElement.textContent = `${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}`;
    }
    
    // デフォルトバッジを削除
    const defaultBadge = document.querySelector('.location-card .default-badge');
    if (defaultBadge) {
        defaultBadge.style.display = 'none';
    }
    
    // 逆ジオコーディングAPIを使って座標から住所を取得
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${location.latitude}&lon=${location.longitude}&accept-language=ja`)
        .then(response => response.json())
        .then(data => {
            console.log('逆ジオコーディング結果:', data);
            
            // 住所情報から都市名と地域名を抽出
            const address = data.address || {};
            const city = address.city || address.town || address.village || address.county || 'GPS位置';
            const region = address.state || address.region || '';
            
            // 画面上の都市名と地域名を更新
            const cityElement = document.querySelector('.location-card .city');
            const regionElement = document.querySelector('.location-card .region');
            
            if (cityElement) {
                cityElement.textContent = city;
            }
            if (regionElement) {
                regionElement.textContent = region;
            }
            
            console.log('位置情報表示を更新しました:', city, region);
        })
        .catch(error => {
            console.error('逆ジオコーディングエラー:', error);
            // エラー時は座標のみ表示
            const cityElement = document.querySelector('.location-card .city');
            const regionElement = document.querySelector('.location-card .region');
            
            if (cityElement) {
                cityElement.textContent = 'GPS位置';
            }
            if (regionElement) {
                regionElement.textContent = '';
            }
        });
}

/**
 * レストラン情報を画面に表示する関数
 * 
 * サーバーから受け取ったレストランデータを解析して、
 * 画面の各要素に情報を設定します。
 * 
 * @param {Object} data - サーバーから返されたレストランデータ
 * @param {Object} data.restaurant - レストラン情報
 * @param {Object} data.distance - 距離情報
 * @param {Object} data.weather - 天気情報
 */
function displayRestaurant(data) {
    // データから必要な情報を取り出す
    // これは「分割代入」というJavaScriptの機能です
    const { restaurant, distance, weather } = data;
    
    // ===== レストランの基本情報を画面に設定 =====
    restaurantName.textContent = restaurant.name;          // 店名
    restaurantGenre.textContent = restaurant.genre;        // ジャンル（例: 和食、イタリアン）
    restaurantAddress.textContent = restaurant.address;    // 住所
    restaurantBudget.textContent = restaurant.budget_display;  // 予算表示
    restaurantHours.textContent = restaurant.hours || '営業時間情報なし';  // 営業時間
    restaurantCatch.textContent = restaurant.catch || restaurant.summary || '';  // キャッチコピー
    
    // 距離情報と徒歩時間（現在地モードの場合のみ）
    if (distance) {
        walkingTime.textContent = distance.time_display;       // 徒歩時間（例: 「徒歩約8分」）
        distanceBadge.textContent = distance.distance_display; // 距離バッジ（例: 「500m」や「1.2km」）
        distanceBadge.style.display = 'inline-block';
    } else {
        // エリアモードの場合は距離情報なし
        walkingTime.textContent = 'アクセス情報は店舗詳細をご確認ください';
        distanceBadge.style.display = 'none';
    }
    
    // ===== レストランの写真を設定 =====
    if (restaurant.photo_url && restaurant.photo_url !== 'no-image') {
        // 写真がある場合
        restaurantImage.src = restaurant.photo_url;           // 画像のURL
        restaurantImage.alt = `${restaurant.name}の写真`;     // 代替テキスト
        restaurantImage.style.display = 'block';              // 画像を表示
    } else {
        // 写真がない場合はデフォルト画像を表示
        // この長い文字列はSVG画像のBase64エンコード版です
        restaurantImage.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXpl';
        restaurantImage.alt = 'レストラン画像なし';
        restaurantImage.style.display = 'block';
    }
    
    // ===== リンクの設定 =====
    mapLink.href = restaurant.map_url;              // Google Mapsへのリンク
    hotpepperLink.href = restaurant.hotpepper_url;  // ホットペッパーへのリンク
    
    // ===== レストラン情報エリアを表示 =====
    restaurantSection.style.display = 'block';
    
    // ===== スムーズスクロール =====
    // レストラン情報が表示されたら、自動的にその位置までスクロール
    restaurantSection.scrollIntoView({ 
        behavior: 'smooth',  // スムーズにスクロール
        block: 'start'       // 要素の上端が画面の上端に来るように
    });
    
    console.log('レストラン表示完了:', restaurant.name);
}

/**
 * レストラン情報エリアを非表示にする関数
 */
function hideRestaurant() {
    restaurantSection.style.display = 'none';
}

/**
 * ルーレットを実行する関数（メイン処理）
 * 
 * この関数が実行される流れ:
 * 1. ローディング状態を表示
 * 2. サーバーに「/roulette」APIをリクエスト
 * 3. サーバーからレストランデータを受け取る
 * 4. データを画面に表示
 * 5. エラーが発生したらエラーメッセージを表示
 * 
 * async/await について:
 * - async = 非同期処理（時間がかかる処理）を扱う関数
 * - await = 処理が完了するまで待つ
 */
async function executeRoulette() {
    try {
        // ===== ステップ1: 準備 =====
        toggleLoading(true);    // ローディング表示を開始
        hideError();            // 前回のエラーメッセージを消す
        hideRestaurant();       // 前回のレストラン情報を消す
        
        console.log('ルーレット開始...');
        
        // ===== ステップ1.5: 検索条件を収集 =====
        const searchParams = {};
        
        // 位置指定モードを追加
        searchParams.location_mode = currentLocationMode;
        
        if (currentLocationMode === 'current') {
            // 現在地モード
            // GPS位置情報があれば追加
            if (userLocation) {
                searchParams.latitude = userLocation.latitude;
                searchParams.longitude = userLocation.longitude;
                console.log('GPS位置情報を使用:', userLocation);
            }
            
            // 徒歩時間を追加
            const walkingTimeValue = parseInt(walkingTimeSelect.value);
            searchParams.max_walking_time_min = walkingTimeValue;
        } else {
            // エリアモード
            const areaValue = areaSelect.value;
            if (!areaValue) {
                // エリアが選択されていない場合はエラー
                throw new Error('エリアを選択してください');
            }
            searchParams.middle_area_code = areaValue;
            console.log('エリアコードを使用:', areaValue);
        }
        
        // 予算コードを追加（空文字列の場合はnull）
        const budgetValue = budgetSelect.value;
        if (budgetValue) {
            searchParams.budget_code = budgetValue;
        }
        
        // ジャンルコードを追加（空文字列の場合はnull）
        const genreValue = genreSelect.value;
        if (genreValue) {
            searchParams.genre_code = genreValue;
        }
        
        // ランチフィルタを追加（デフォルト: 1 = ランチあり）
        searchParams.lunch = 1;
        
        console.log('検索条件:', searchParams);
        
        // ===== ステップ2: サーバーにリクエスト =====
        // fetch = サーバーと通信する関数
        // await = サーバーからの応答を待つ
        const response = await fetch('/roulette', {
            method: 'POST',                              // POSTメソッド（データを送信する形式）
            headers: {
                'Content-Type': 'application/json',      // JSON形式でデータを送る
            },
            body: JSON.stringify(searchParams)           // 検索条件をJSON形式で送信
        });
        
        // ===== ステップ3: レスポンスの確認 =====
        // response.ok = HTTPステータスコードが200番台（成功）かどうか
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // ===== ステップ4: レスポンスのJSON化 =====
        // JSON形式のデータをJavaScriptのオブジェクトに変換
        const data = await response.json();
        
        // ===== ステップ5: エラーレスポンスのチェック =====
        if (data.error || !data.success) {
            // サーバーからエラーが返ってきた場合
            let errorMsg = data.message || 'レストラン検索中にエラーが発生しました';
            
            // サジェスションがある場合は追加
            if (data.suggestion) {
                errorMsg += '\n' + data.suggestion;
            }
            
            throw new Error(errorMsg);
        }
        
        // ===== ステップ6: 成功時の処理 =====
        if (data.success && data.restaurant) {
            console.log('ルーレット成功:', data);
            displayRestaurant(data);  // レストラン情報を画面に表示
        } else {
            // データの形式が正しくない場合
            throw new Error(data.message || 'レストランデータが正しくありません');
        }
        
    } catch (error) {
        // ===== エラーが発生した場合の処理 =====
        console.error('ルーレットエラー:', error);
        
        // エラーの種類に応じて適切なメッセージを表示
        let errorMessage = 'レストラン検索中にエラーが発生しました';
        
        if (error.message.includes('Failed to fetch')) {
            // ネットワークエラー（インターネットに接続できない）
            errorMessage = 'ネットワークエラーが発生しました。インターネット接続を確認してください。';
        } else if (error.message.includes('HTTP 500')) {
            // サーバー内部エラー
            errorMessage = 'サーバーエラーが発生しました。しばらく時間を置いて再度お試しください。';
        } else if (error.message.includes('HTTP 429')) {
            // アクセス制限（リクエストが多すぎる）
            errorMessage = 'アクセスが集中しています。しばらく時間を置いて再度お試しください。';
        } else if (error.message) {
            // その他のエラー（サーバーから返されたメッセージを使用）
            errorMessage = error.message;
        }
        
        showError(errorMessage);  // エラーメッセージを画面に表示
        
    } finally {
        // ===== 最後に必ず実行される処理 =====
        // エラーが発生してもしなくても、ローディング表示を終了
        toggleLoading(false);
    }
}

/**
 * ジャンルマスタデータを取得してセレクトボックスに設定する関数
 * 
 * サーバーからジャンルデータを取得し、ジャンル選択UIに反映します。
 */
async function loadGenres() {
    try {
        console.log('ジャンルマスタを読み込み中...');
        
        // サーバーからジャンルデータを取得
        const response = await fetch('/api/genres');
        
        if (!response.ok) {
            throw new Error('ジャンルマスタの取得に失敗しました');
        }
        
        const data = await response.json();
        
        if (!data.success || !data.genres) {
            throw new Error('ジャンルデータが不正です');
        }
        
        // セレクトボックスをクリア（「指定なし」以外）
        genreSelect.innerHTML = '<option value="">指定なし</option>';
        
        // ジャンルデータをセレクトボックスに追加
        data.genres.forEach(genre => {
            // code が空文字列（「指定なし」）はスキップ
            if (genre.code === '') {
                return;
            }
            
            const option = document.createElement('option');
            option.value = genre.code;
            option.textContent = genre.name;
            genreSelect.appendChild(option);
        });
        
        console.log(`ジャンルマスタを読み込みました: ${data.genres.length}件`);
        
    } catch (error) {
        console.error('ジャンルマスタ読み込みエラー:', error);
        // エラー時もアプリは動作するようにする（ジャンル選択は「指定なし」のまま）
    }
}

/**
 * エリアマスタデータを読み込む関数
 * 
 * サーバーからエリアデータを取得し、エリア選択UIに反映します。
 */
async function loadAreas() {
    try {
        console.log('エリアマスタを読み込み中...');
        
        // サーバーからエリアデータを取得
        const response = await fetch('/api/areas');
        
        if (!response.ok) {
            throw new Error('エリアマスタの取得に失敗しました');
        }
        
        const data = await response.json();
        
        if (!data.success || !data.areas) {
            throw new Error('エリアデータが不正です');
        }
        
        // セレクトボックスをクリア
        areaSelect.innerHTML = '<option value="">エリアを選択してください</option>';
        
        // エリアデータをセレクトボックスに追加
        data.areas.forEach(area => {
            const option = document.createElement('option');
            option.value = area.code;
            option.textContent = area.name;
            areaSelect.appendChild(option);
        });
        
        console.log(`エリアマスタを読み込みました: ${data.areas.length}件`);
        
    } catch (error) {
        console.error('エリアマスタ読み込みエラー:', error);
        // エラー時もアプリは動作するようにする
    }
}

/**
 * 位置指定モードを切り替える関数
 * 
 * @param {string} mode - 'current'（現在地モード） または 'area'（エリアモード）
 */
function switchLocationMode(mode) {
    currentLocationMode = mode;
    
    if (mode === 'current') {
        // 現在地モード
        modeCurrentBtn.classList.add('active');
        modeAreaBtn.classList.remove('active');
        
        // 徒歩時間選択を表示、エリア選択を非表示
        walkingTimeGroup.style.display = 'block';
        areaSelectGroup.style.display = 'none';
        
        console.log('現在地モードに切り替えました');
    } else {
        // エリアモード
        modeAreaBtn.classList.add('active');
        modeCurrentBtn.classList.remove('active');
        
        // エリア選択を表示、徒歩時間選択を非表示
        walkingTimeGroup.style.display = 'none';
        areaSelectGroup.style.display = 'block';
        
        console.log('エリアモードに切り替えました');
    }
}

/**
 * ページ読み込み完了後の初期化処理
 * 
 * DOMContentLoaded = HTMLの読み込みが完了した時に実行されるイベント
 * この時点で、HTMLの要素にアクセスできるようになります
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Lunch Roulette JavaScript 初期化完了');
    
    // ===== 初期化: ジャンルマスタとエリアマスタを読み込む =====
    loadGenres();
    loadAreas();
    
    // ===== イベント0: モード切り替えボタンのクリック =====
    if (modeCurrentBtn) {
        modeCurrentBtn.addEventListener('click', function(e) {
            e.preventDefault();
            switchLocationMode('current');
        });
    }
    
    if (modeAreaBtn) {
        modeAreaBtn.addEventListener('click', function(e) {
            e.preventDefault();
            switchLocationMode('area');
        });
    }
    
    // ===== イベント1: ルーレットボタンのクリック =====
    // ボタンがクリックされた時に executeRoulette() を実行
    rouletteBtn.addEventListener('click', function(e) {
        e.preventDefault();  // デフォルトの動作（ページ遷移など）を防止
        console.log('ルーレットボタンがクリックされました');
        executeRoulette();   // ルーレット実行
    });
    
    // ===== イベント2: 再ルーレットボタンのクリック =====
    // レストラン表示後に「もう一度回す」ボタンを押した時
    if (retryBtn) {
        retryBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('再ルーレットボタンがクリックされました');
            executeRoulette();
        });
    }
    
    // ===== イベント2.5: GPSボタンのクリック =====
    // GPS位置取得ボタンが押された時
    if (gpsBtn) {
        gpsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('GPS取得ボタンがクリックされました');
            getGPSLocation();
        });
    }
    
    // ===== イベント3: エラーメッセージのクリック =====
    // エラーメッセージをクリックすると非表示になる
    errorMessage.addEventListener('click', function() {
        hideError();
    });
    
    // ===== イベント4: キーボードショートカット =====
    // Enterキーを押してもルーレットを実行できるようにする
    document.addEventListener('keydown', function(e) {
        // e.key = 押されたキー
        if (e.key === 'Enter' && !rouletteBtn.disabled) {
            e.preventDefault();
            console.log('Enterキーでルーレットを実行');
            executeRoulette();
        }
    });
    
    console.log('イベントリスナーの設定が完了しました');
});

/**
 * ページを離れる時の警告
 * 
 * ルーレット実行中にページを閉じようとすると、警告を表示します
 */
window.addEventListener('beforeunload', function() {
    // ボタンが無効（disabled=true）= ルーレット実行中
    if (rouletteBtn.disabled) {
        return 'レストラン検索中です。ページを離れますか？';
    }
});

/**
 * JavaScriptのエラーをキャッチして画面に表示
 */
window.addEventListener('error', function(e) {
    // JavaScriptのコードでエラーが発生した場合
    console.error('JavaScript エラー:', e.error);
    showError('予期しないエラーが発生しました。ページを再読み込みしてください。');
});

/**
 * Promiseのエラーをキャッチ
 * 
 * Promise = 非同期処理の結果を扱うオブジェクト
 * fetchなどの非同期処理でエラーが発生した時にキャッチされます
 */
window.addEventListener('unhandledrejection', function(e) {
    console.error('未処理のPromiseエラー:', e.reason);
    showError('通信エラーが発生しました。しばらく時間を置いて再度お試しください。');
    e.preventDefault();  // デフォルトのエラー処理を防止
});
