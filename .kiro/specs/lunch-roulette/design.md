# 設計文書

## 概要E

Lunch Rouletteは、Flask Webフレームワークを使用したシンプルなWebアプリケーションです。ユーザーの位置惁E��と天気データを絁E��合わせて、近くのレストランをランダムに推薦します。PythonAnywhere無料�Eランの制紁E�Eで動作するよぁE��計されてぁE��す、E

## 関連技術理諁E

### 地琁E��報シスチE���E�EIS�E�E
- **ハ�Eバ�Eサイン公弁E*: 地琁E���E2点間�E距離を計算する数学皁E��況E
- **IPジオロケーション**: IPアドレスから地琁E��位置を推定する技衁E
- **座標系**: 緯度・経度を使用したWGS84座標系を採用

### API統合パターン
- **RESTful API**: Hot Pepper Gourmet APIとOpenWeatherMap APIとの通信
- **レート制陁E*: 無料�Eランの制紁E��対応するため�EAPI呼び出し制御
- **エラーハンドリング**: 外部API障害時�E適刁E��処琁E

### キャチE��ング戦略
- **時間ベ�EスキャチE��ュ**: 10刁E��のTTL�E�Eime To Live�E�E
- **SQLiteキャチE��ュ**: ローカルチE�Eタベ�Eスを使用した高速アクセス
- **キャチE��ュ無効匁E*: タイムスタンプ�Eースの自動期限�EめE

## アーキチE��チャ

### シスチE��構�E
```
┌─────────────────━E   ┌─────────────────━E   ┌─────────────────━E
━E  フロントエンチE  ━E   ━E  FlaskバックエンチE ━E   ━E  外部API        ━E
━E  (HTML/CSS/JS)  │◄──►━E  (Python)      │◄──►━E  (Hot Pepper,   ━E
━E                ━E   ━E                ━E   ━E  OpenWeather)  ━E
└─────────────────━E   └─────────────────━E   └─────────────────━E
                              ━E
                              ▼
                       ┌─────────────────━E
                       ━E  SQLiteキャチE��ュ ━E
                       ━E                ━E
                       └─────────────────━E
```

### レイヤー構�E
1. **プレゼンチE�Eション層**: HTML/CSS/JavaScript�E�バニラJS�E�E
2. **アプリケーション層**: Flask ルーチE��ングとビジネスロジチE��
3. **チE�Eタアクセス層**: SQLiteキャチE��ュとAPI統吁E
4. **外部サービス層**: Hot Pepper Gourmet API、OpenWeatherMap API

## コンポ�Eネントと インターフェース

### Flaskアプリケーション構造
```
lunch_roulette/
├── app.py              # メインアプリケーション
├── wsgi.py            # PythonAnywhere用WSGI設宁E
├── requirements.txt   # 依存関俁E
├── static/
━E  ├── css/
━E  ━E  └── style.css  # モダンUIスタイル
━E  └── js/
━E      └── main.js    # フロントエンドロジチE��
├── templates/
━E  └── index.html     # メインペ�EジチE��プレーチE
└── cache.db           # SQLiteキャチE��ュチE�Eタベ�Eス
```

### 主要コンポ�EネンチE

#### 1. LocationService
```python
class LocationService:
    """IPアドレスから位置惁E��を取得するサービス"""
    def get_location_from_ip(self, ip_address: str) -> dict
```

#### 2. WeatherService
```python
class WeatherService:
    """OpenWeatherMap APIから天気情報を取征E""
    def get_current_weather(self, lat: float, lon: float) -> dict
```

#### 3. RestaurantService
```python
class RestaurantService:
    """Hot Pepper Gourmet APIからレストラン惁E��を取征E""
    def search_restaurants(self, lat: float, lon: float, radius: int) -> list
    def filter_by_budget(self, restaurants: list, max_budget: int) -> list
```

#### 4. CacheService
```python
class CacheService:
    """SQLiteを使用したキャチE��ング機�E"""
    def get_cached_data(self, key: str) -> dict
    def set_cached_data(self, key: str, data: dict, ttl: int) -> None
    def is_cache_valid(self, timestamp: datetime) -> bool
```

#### 5. DistanceCalculator
```python
class DistanceCalculator:
    """ハ�Eバ�Eサイン公式を使用した距離計箁E""
    def calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float
```

### APIエンド�EインチE

#### GET /
- **目皁E*: メインペ�Eジの表示
- **レスポンス**: HTML チE��プレーチE
- **処琁E*: 位置惁E��検�E、天気情報取得、�Eージレンダリング

#### POST /roulette
- **目皁E*: レストラン推薦の実衁E
- **リクエスチE*: JSON�E�位置惁E���E�E
- **レスポンス**: JSON�E�レストラン惁E���E�E
- **処琁E*: レストラン検索、距離計算、ランダム選抁E

## チE�EタモチE��

### キャチE��ュチE�Eブル構造
```sql
CREATE TABLE cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT UNIQUE NOT NULL,
    data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);
```

### レストランチE�Eタ構造
```json
{
    "id": "string",
    "name": "string",
    "photo": "string",
    "lat": "float",
    "lng": "float",
    "address": "string",
    "budget": "integer",
    "genre": "string",
    "urls": {
        "pc": "string"
    }
}
```

### 天気データ構造
```json
{
    "temperature": "float",
    "condition": "string",
    "uv_index": "float",
    "description": "string"
}
```

## エラーハンドリング

### エラー刁E��と対忁E

#### 1. 外部API エラー
- **Hot Pepper API障害**: キャチE��ュチE�Eタの使用、エラーメチE��ージ表示
- **OpenWeatherMap API障害**: チE��ォルト天気情報の表示
- **レート制限趁E��**: キャチE��ュチE�Eタの優先使用

#### 2. チE�Eタ処琁E��ラー
- **位置惁E��取得失敁E*: チE��ォルト位置�E�東京駁E���E使用
- **レストラン検索結果なぁE*: 篁E��拡大また�E代替提桁E
- **距離計算エラー**: 概算距離の表示

#### 3. シスチE��エラー
- **チE�Eタベ�Eス接続エラー**: インメモリキャチE��ュへのフォールバック
- **チE��プレートエラー**: 最小限のHTMLレスポンス

### エラーレスポンス形弁E
```json
{
    "error": true,
    "message": "エラーメチE��ージ",
    "fallback_data": "代替チE�Eタ�E�可能な場合！E
}
```

## チE��ト戦略

### チE��トレベル

#### 1. 単体テスチE
- **対象**: 吁E��ービスクラスの個別メソチE��
- **チE�Eル**: pytest
- **カバレチE��**: 80%以上を目樁E

#### 2. 統合テスチE
- **対象**: API エンド�EイントとチE�Eタベ�Eス操佁E
- **モチE��**: 外部API呼び出し�EモチE��匁E
- **シナリオ**: 正常系・異常系の両方

#### 3. E2EチE��チE
- **対象**: ブラウザでの完�Eなユーザーフロー
- **チE�Eル**: Selenium�E�オプション�E�E
- **シナリオ**: ペ�Eジ読み込み→�EタンクリチE��→結果表示

### チE��トデータ
- **モチE��API レスポンス**: 実際のAPI構造に基づぁE
- **チE��ト用チE�Eタベ�Eス**: インメモリSQLite
- **位置惁E��**: 東京都冁E�E固定座樁E

## UI/UXチE��イン

### モダンUIトレンド採用

#### 1. チE��インシスチE��
- **カラーパレチE��**: Material Design 3.0準拠
- **タイポグラフィ**: シスチE��フォント使用
- **アイコン**: Font Awesome また�E Material Icons

#### 2. レスポンシブデザイン
- **ブレークポインチE*: モバイルファースチE
- **グリチE��シスチE��**: CSS Grid / Flexbox
- **タチE��対忁E*: 44px以上�EタチE�EターゲチE��

#### 3. インタラクション
- **ローチE��ング状慁E*: スピナーとスケルトンUI
- **アニメーション**: CSS transitions�E�E0fps�E�E
- **フィードバチE��**: ホバー・フォーカス状慁E

### コンポ�Eネント設訁E

#### 1. ヘッダー
- 位置惁E��表示
- 天気情報カーチE
- ルーレチE��ボタン

#### 2. レストランカーチE
- 画像！Espect-ratio: 16:9�E�E
- レストラン名�Eジャンル
- 距離・予算情報
- マップリンクボタン

#### 3. 状態管琁E
- ローチE��ング状慁E
- エラー状慁E
- 空状態（結果なし！E

## セキュリチE��老E�E事頁E

### チE�Eタ保護
- **APIキー**: 環墁E��数での管琁E
- **入力検証**: SQLインジェクション対筁E
- **XSS対筁E*: チE��プレートエスケーチE

### プライバシー
- **位置惁E��**: IPベ�Eスのみ、GPS不使用
- **ログ**: 個人惁E��の非記録
- **キャチE��ュ**: 個人識別惁E��の除夁E

## パフォーマンス最適匁E

### フロントエンチE
- **CSS/JS最小化**: 本番環墁E��の圧縮
- **画像最適匁E*: WebP形式�E使用
- **キャチE��ュ戦略**: ブラウザキャチE��ュの活用

### バックエンチE
- **チE�Eタベ�Eス**: インチE��クス最適匁E
- **API呼び出ぁE*: 並列�E琁E�E実裁E
- **メモリ使用釁E*: PythonAnywhere制限�Eでの動佁E

## チE�Eロイメント設訁E

### PythonAnywhere設宁E
- **WSGI設宁E*: `wsgi.py`での適刁E��設宁E
- **静的ファイル**: `/static/`パスの設宁E
- **環墁E��数**: PythonAnywhereコンソールでの設宁E

### 依存関係管琁E
```
Flask==3.0.0
requests==2.31.0
sqlite3 (標準ライブラリ)
```

### 設定ファイル
- **開発環墁E*: `config.py`
- **本番環墁E*: 環墁E��数での設定上書�