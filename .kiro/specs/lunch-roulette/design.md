# 設計文書

## 概要

Lunch Rouletteは、Flask Webフレームワークを使用したシンプルなWebアプリケーションです。ユーザーの位置情報と天気データを組み合わせて、近くのレストランをランダムに推薦します。PythonAnywhere無料プランの制約下で動作するよう設計されています。

## 関連技術理論

### 地理情報システム（GIS）

- **ハーバーサイン公式**: 地球上の2点間の距離を計算する数学的手法
- **IPジオロケーション**: IPアドレスから地理的な位置を推定する技術
- **座標系**: 緯度・経度を使用したWGS84座標系を採用

### API統合パターン

- **RESTful API**: Hot Pepper Gourmet APIとOpenWeatherMap APIとの通信
- **レート制限**: 無料プランの制約に対応するためのAPI呼び出し制御
- **エラーハンドリング**: 外部API障害時の適切な処理

### キャッシュ戦略

- **時間ベースキャッシュ**: 10分間のTTL（Time To Live）
- **SQLiteキャッシュ**: ローカルデータベースを使用した高速アクセス
- **キャッシュ無効化**: タイムスタンプベースの自動期限切れ

## アーキテクチャ

### システム構成

```plaintext
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ フロントエンド   │◄──►│ Flaskバックエンド │◄──►│ 外部API         │
│ (HTML/CSS/JS)    │   │ (Python)        │   │ (Hot Pepper,    │
│                  │   │                 │   │  OpenWeather)   │
└───────────────┘   └───────────────┘   └───────────────┘
                              │
                              ▼
                       ┌───────────────┐
                       │ SQLiteキャッシュ │
                       └───────────────┘
```

### レイヤー構成

1. **プレゼンテーション層**: HTML/CSS/JavaScript（バニラJS）

2. **アプリケーション層**: Flask ルーティングとビジネスロジック

3. **データアクセス層**: SQLiteキャッシュとAPI統合

4. **外部サービス層**: Hot Pepper Gourmet API、OpenWeatherMap API

## コンポーネントとインターフェース

### Flaskアプリケーション構造

```plaintext
lunch_roulette/
├── app.py              # メインアプリケーション
├── wsgi.py            # PythonAnywhere用WSGI設定
├── requirements.txt   # 依存関係
├── static/
│   ├── css/
│   │   └── style.css  # モダンUIスタイル
│   └── js/
│       └── main.js    # フロントエンドロジック
├── templates/
│   └── index.html     # メインページテンプレート
└── cache.db           # SQLiteキャッシュデータベース
```

### 主要コンポーネント

#### 1. LocationService

```python
class LocationService:
    """IPアドレスから位置情報を取得するサービス"""
    def get_location_from_ip(self, ip_address: str) -> dict
```

#### 2. WeatherService

```python
class WeatherService:
    """OpenWeatherMap APIから天気情報を取得"""
    def get_current_weather(self, lat: float, lon: float) -> dict
```

#### 3. RestaurantService

```python
class RestaurantService:
    """Hot Pepper Gourmet APIからレストラン情報を取得"""
    def search_restaurants(self, lat: float, lon: float, radius: int) -> list
    def filter_by_budget(self, restaurants: list, max_budget: int) -> list
```

#### 4. CacheService

```python
class CacheService:
    """SQLiteを使用したキャッシング機能"""
    def get_cached_data(self, key: str) -> dict
    def set_cached_data(self, key: str, data: dict, ttl: int) -> None
    def is_cache_valid(self, timestamp: datetime) -> bool
```

#### 5. DistanceCalculator

```python
class DistanceCalculator:
    """ハーバーサイン公式を使用した距離計算"""
    def calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float
```

### APIエンドポイント

#### GET /
- **目的**: メインページの表示
- **レスポンス**: HTML テンプレート
- **処理**: 位置情報検出、天気情報取得、ページレンダリング

#### POST /roulette
- **目的**: レストラン推薦の実行
- **リクエスト**: JSON形式の位置情報
- **レスポンス**: JSON形式のレストラン情報
- **処理**: レストラン検索、距離計算、ランダム選択

## データモデル

### キャッシュテーブル構造
```sql
CREATE TABLE cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT UNIQUE NOT NULL,
    data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);
```

### レストランデータ構造
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

### エラー種類と対処法

#### 1. 外部API エラー
- **Hot Pepper API障害**: キャッシュデータの使用、エラーメッセージ表示
- **OpenWeatherMap API障害**: デフォルト天気情報の表示
- **レート制限超過**: キャッシュデータの優先使用

#### 2. データ処理エラー
- **位置情報取得失敗**: デフォルト位置（東京駅）使用
- **レストラン検索結果なし**: 検索半径拡大または代替提案
- **距離計算エラー**: 概算距離の表示

#### 3. システムエラー
- **データベース接続エラー**: インメモリキャッシュへのフォールバック
- **テンプレートレンダリングエラー**: 最小限のHTMLレスポンス

### エラーレスポンス形式
```json
{
    "error": true,
    "message": "エラーメッセージ",
    "fallback_data": "代替データが可能な場合！"
}
```

## テスト戦略

### テストレベル

#### 1. 単体テスト
- **対象**: サービスクラスの個別メソッド
- **テストツール**: pytest
- **カバレッジ**: 80%以上を目標

#### 2. 統合テスト
- **対象**: API エンドポイントとデータベース操作
- **モック**: 外部API呼び出しをモック
- **シナリオ**: 正常系・異常系の両方

#### 3. E2Eテスト
- **対象**: ブラウザでの完璧なユーザーフロー
- **テストツール**: Selenium（ヘッドレスオプションあり）
- **シナリオ**: ページ読み込み→ボタンクリック→結果表示

### テストデータ
- **モックAPI レスポンス**: 実際のAPI構造に基づく
- **テスト用データベース**: インメモリSQLite
- **位置情報**: 東京都内の固定座標

## UI/UXデザイン

### モダンUIトレンド採用

#### 1. デザインシステム
- **カラーパレット**: Material Design 3.0準拠
- **タイポグラフィ**: システムフォント使用
- **アイコン**: Font Awesome または Material Icons

#### 2. レスポンシブデザイン
- **ブレークポイント**: モバイルファースト
- **グリッドシステム**: CSS Grid / Flexbox
- **タッチターゲット**: 44px以上のタッチターゲット

#### 3. インタラクション
- **ローディング表示**: スピナーとスケルトンUI
- **アニメーション**: CSS transitions（60fps目標）
- **フィードバック**: ホバー・フォーカス時の視覚的フィードバック

### コンポーネント設計

#### 1. ヘッダー
- 位置情報表示
- 天気情報カード
- ルーレットボタン

#### 2. レストランカード
- 画像（アスペクト比: 16:9）
- レストラン名とジャンル
- 距離・予算情報
- マップリンクボタン

#### 3. 状態表示
- ローディング状態
- エラー状態
- 空状態（結果なし）

## セキュリティ対策

### データ保護
- **APIキー**: 環境変数での管理
- **入力検証**: SQLインジェクション対策
- **XSS対策**: テンプレートエスケープ

### プライバシー
- **位置情報**: IPベースのみ、GPS不使用
- **ログ**: 個人情報の非記録
- **キャッシュ**: 個人識別情報の除外

## パフォーマンス最適化

### フロントエンド
- **CSS/JS最小化**: 本番環境での圧縮
- **画像最適化**: WebP形式の使用
- **キャッシュ戦略**: ブラウザキャッシュの活用

### バックエンド
- **データベース**: インデックス最適化
- **API呼び出し**: 並列処理による高速化
- **メモリ使用量**: PythonAnywhere制限内での動作

## デプロイメント設計

### PythonAnywhere設計
- **WSGI設定**: `wsgi.py`での適切な設定
- **静的ファイル**: `/static/`パスの設定
- **環境変数**: PythonAnywhereコンソールでの設定

### 依存関係管理
```
Flask==3.0.0
requests==2.31.0
sqlite3 (標準ライブラリ)
```

### 設定ファイル
- **開発環境**: `config.py`
- **本番環境**: 環境変数での設定上書き