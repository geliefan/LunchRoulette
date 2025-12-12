# lunch-roulette

東京エリアのランチスポット発見Webサービス

## 概要

Lunch Rouletteは、東京エリアのユーザーがリアルタイムの天気データと徒歩距離計算を組み合わせてランチスポットを発見できるWebサービスです。予算制限下で近くのレストランを見つけるためのシンプルで効率的なインターフェースを提供します。

## 主な機能

- **自動位置検出**: IPアドレスベースの位置情報検出（ipapi.co）
- **GPS位置取得**: ブラウザのGeolocation APIによる正確な現在地取得
- **リアルタイム天気情報**: WeatherAPI.com APIを使用した現在の天気表示
- **レストラン検索**: Hot Pepper Gourmet APIを使用したレストラン検索
- **カスタマイズ可能な検索条件**:
  - 徒歩時間指定（5分/10分/15分/20分/20分超）
  - 予算カテゴリ選択（すべて/〜500円/〜1000円/〜1500円/〜2000円/〜3000円）
  - ジャンル選択（複数ジャンル対応）
  - ランチフィルタ（ランチ営業ありの店舗に絞り込み）
- **距離計算**: ハバーサイン公式を使用した正確な徒歩距離計算
- **APIレスポンスキャッシング**: SQLiteを使用した10分間のキャッシング機能
- **モダンUI**: レスポンシブデザインとモダンなユーザーインターフェース

## 技術スタック

- **バックエンド**: Python 3.11+, Flask 3.x
- **データベース**: SQLite（キャッシュ用、標準ライブラリ）
- **フロントエンド**: HTML5, CSS3, バニラJavaScript
- **外部API**: 
  - WeatherAPI.com Current Weather API
  - Hot Pepper Gourmet Web API
  - ipapi.co（位置情報検出用）
- **開発・テスト**: pytest, pytest-cov, flake8, autopep8
- **コンテナ**: Docker, Docker Compose

## 技術理論概要

Lunch Rouletteの技術的な基盤は、以下の理論とアルゴリズムに基づいています：

1. **ハーバーサイン公式**: 地球上の2点間の最短距離を計算するための公式。
2. **キャッシュ最適化**: SQLiteを使用してAPIレスポンスをキャッシュし、リクエスト頻度を削減。
3. **リアルタイムAPI統合**: WeatherAPI.comとHot Pepper Gourmet APIを統合し、リアルタイムデータを提供。
4. **レスポンシブデザイン**: モバイルデバイスとデスクトップの両方で最適に動作するUI設計。

## セットアップ手順

### 前提条件

- Python 3.11以上
- pip（Pythonパッケージマネージャー）
- インターネット接続（外部API使用のため）

### ローカル開発環境セットアップ

1. **リポジトリのクローン**

   ```bash
   git clone <repository-url>
   cd lunch-roulette
   ```

2. **仮想環境作成と有効化**

   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **依存関係インストール**

   ```bash
   pip install -r requirements.txt
   ```

4. **環境変数の設定**

   必須環境変数：

   ```bash
   # APIキー（必須）
   export WEATHERAPI_KEY=your_weatherapi_key
   export HOTPEPPER_API_KEY=your_hotpepper_api_key
   
   # 任意の環境変数
   export FLASK_DEBUG=True                    # デバッグモード（開発時）
   export SECRET_KEY=your_secret_key          # セッション暗号化キー
   export CACHE_TTL_MINUTES=10                # キャッシュ有効期限（分）
   export DATABASE_PATH=cache.db              # データベースファイルパス
   export DEFAULT_LATITUDE=35.6812            # デフォルト緯度（東京駅）
   export DEFAULT_LONGITUDE=139.7671          # デフォルト経度（東京駅）
   export FLASK_ENV=development               # Flask実行環境
   export HOST=127.0.0.1                      # バインドするホストアドレス
   export PORT=5000                           # バインドするポート
   ```

5. **アプリケーションの起動**

   ```bash
   # 推奨方法: run.pyを使用
   python run.py
   
   # または、Flaskアプリケーションを直接実行
   python -m lunch_roulette.app
   
   # または、モジュールエントリーポイントから実行
   python -m lunch_roulette
   ```

   キャッシュデータベースは初回起動時に自動作成されます。

### APIキーの取得

#### WeatherAPI.com

1. [WeatherAPI.com](https://www.weatherapi.com/) でアカウント登録
2. APIキー（API Key）を取得
3. 無料プランでは1日100万回まで利用可能

#### Hot Pepper Gourmet API

1. [リクルートWebサービス](https://webservice.recruit.co.jp/) でアカウント登録
2. Hot Pepper Gourmet APIのAPIキー（API Key）を取得
3. 無料プランでは1日3,000回まで利用可能

## テスト

### テスト実行

開発環境では`requirements-dev.txt`で追加依存関係をインストール後、テストを実行します。

```bash
# 開発環境の依存関係をインストール
pip install -r requirements-dev.txt

# 全テストを実行
pytest

# 特定テストファイルを実行
pytest tests/unit/test_cache_service.py

# カバレッジレポート付きで実行
pytest --cov=src --cov-report=html

# flake8によるリンティング
flake8 src/

# 自動フォーマット（オプション）
autopep8 --in-place --aggressive --aggressive src/
```

## プロジェクト構造

```plaintext
lunch-roulette/
├── src/                             # ソースコード
│   └── lunch_roulette/              # メインパッケージ
│       ├── __init__.py              # パッケージ初期化
│       ├── __main__.py              # モジュール実行エントリーポイント
│       ├── app.py                   # メインFlaskアプリケーション
│       ├── config.py                # 設定管理
│       ├── wsgi.py                  # WSGI設定（本番環境用）
│       ├── api/                     # API関連モジュール
│       │   └── __init__.py
│       ├── data/                    # マスタデータ
│       │   ├── areas_tokyo.json     # 東京エリアマスタデータ
│       │   └── genres.json          # ジャンルマスタデータ
│       ├── models/                  # データモデル
│       │   ├── __init__.py
│       │   └── database.py          # データベース管理
│       ├── services/                # ビジネスロジック
│       │   ├── __init__.py
│       │   ├── cache_service.py     # キャッシュサービス
│       │   ├── location_service.py  # 位置情報サービス
│       │   ├── weather_service.py   # 天気情報サービス
│       │   └── restaurant_service.py # レストラン検索サービス
│       ├── static/                   # 静的ファイル
│       │   ├── css/
│       │   │   └── style.css         # メインスタイルシート
│       │   └── js/
│       │       └── main.js           # メインJavaScript
│       ├── templates/                # HTMLテンプレート
│       │   └── index.html            # メインページテンプレート
│       └── utils/                    # ユーティリティ
│           ├── __init__.py
│           ├── distance_calculator.py # 距離計算サービス
│           ├── restaurant_selector.py # レストラン選択ロジック
│           └── error_handler.py       # エラーハンドリング
├── tests/                           # テスト
│   ├── __init__.py
│   ├── conftest.py                  # pytest設定
│   ├── pytest.ini                   # pytest設定
│   ├── unit/                        # 単体テスト
│   │   ├── __init__.py
│   │   ├── test_cache_service.py
│   │   ├── test_cache_system.py
│   │   ├── test_distance_calculator.py
│   │   ├── test_endpoints.py
│   │   ├── test_error_handling.py
│   │   ├── test_location_service.py
│   │   ├── test_restaurant_service.py
│   │   ├── test_weather_service.py
│   │   └── その他テストファイル
│   └── integration/                 # 統合テスト
│       └── __init__.py
├── docs/                           # ドキュメント
│   ├── 01_要求定義書_学生用.md
│   ├── 01_要求定義書_講師用.md
│   ├── 02_設計.md
│   └── 03_デプロイ手順.md
├── internship/                     # インターンシップ課題
│   ├── 01_budget_filter.md
│   ├── 02_weather_message.md
│   ├── 03_distance_display.md
│   ├── 04_favorite_restaurants.md
│   ├── 05_opening_hours_validation.md
│   ├── 06_search_history.md
│   ├── 07_random_animation.md
│   └── 08_private_room_filter.md
├── run.py                          # 開発用エントリーポイント
├── pyproject.toml                  # プロジェクト設定
├── requirements.txt                # Python依存関係
├── requirements-dev.txt            # 開発用依存関係
├── docker-compose.yml              # Docker Compose設定
├── Dockerfile                      # Docker設定
├── README.md                       # このファイル
├── .flake8                        # flake8設定
├── .gitignore                     # Git無視ファイル
└── cache.db                       # SQLiteキャッシュデータベース（実行時に生成）
```

## 技術理論概要

### 地理情報システム (GIS)

#### ハバーサイン公式

地球上の2点間距離を計算する数学的手法。球面三角法を使用して、緯度・経度から最短距離を算出します。

```python
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    ハバーサイン公式を使用して2地点間の距離を計算
    
    Args:
        lat1, lon1: 地点1の緯度・経度
        lat2, lon2: 地点2の緯度・経度
    
    Returns:
        距離（km）
    """
    R = 6371  # 地球の平均半径 (km)
    
    # ラジアンに変換
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    # ハバーサイン公式
    a = (math.sin(dlat/2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c
```

#### IPジオロケーション

IPアドレスから地理的な位置を推定する技術。IPv4/IPv6アドレスをGeoIPデータベースで照合し、おおよその緯度・経度を取得します。本アプリケーションではipapi.coサービスを使用しています。

### API統合パターン

#### RESTful API設計

- **統一インターフェース**: HTTP動詞 (GET, POSTなど) を適切に使用
- **ステートレス**: サーバはクライアント状態を保持しない
- **キャッシュ可能**: レスポンスにキャッシュ情報を含める

#### レート制限対策

- **指数バックオフ**: 失敗時の再試行間隔を指数的に増加
- **キャッシング**: 同一リクエスト結果を一定時間保持
- **バッチ処理**: 複数のリクエストをまとめて処理

### キャッシング戦略

#### 時間ベースキャッシング (TTL)

```python
# 10分間のキャッシュ
cache_duration = timedelta(minutes=10)
expires_at = datetime.now() + cache_duration
```

#### キャッシュ無効化戦略

- **タイムスタンプ方式**: 作成時刻と現在時刻を比較
- **自動クリーンアップ**: 期限切れデータの定期削除
- **LRU (Least Recently Used)**: 使用頻度の低いデータから削除

### パフォーマンス最適化

#### フロントエンド最適化

- **CSS/JS最小化**: ファイルサイズの削減
- **画像最適化**: WebP形式使用、適切なサイズ設定
- **ブラウザキャッシュ**: Cache-Controlヘッダーの設定

#### バックエンド最適化

- **データベースインデックス**: 検索性能の向上
- **並列処理**: 複数API呼び出しの同時実行
- **メモリ管理**: 不要なオブジェクトを適切に解放

## トラブルシューティング

### よくある問題と解決方法

#### 1. APIキーエラー

```plaintext
エラー: Invalid API key
解決: 環境変数が正しく設定されているか確認
```

#### 2. データベース接続エラー

```plaintext
エラー: database is locked
解決: アプリケーションを再起動し、データベースファイルの権限を確認
```

#### 3. 位置情報取得失敗

```plaintext
エラー: Location detection failed
解決: デフォルト位置 (東京駅) が使用されます。正常な動作です。
```

#### 4. レストラン検索結果なし

```plaintext
エラー: No restaurants found
解決: 検索範囲を拡大するか、予算制限を緩和してください
```

### ログの確認

```bash
# デバッグモードでアプリケーションを起動
FLASK_DEBUG=true python run.py
```

デバッグモードではコンソールに詳細なログが出力されます。

## 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は`LICENSE`ファイルを参照してください。

## 作成者

- 開発者: [Your Name]
- メール: [your.email@example.com]
- GitHub: [your-github-username]

## 謝辞

- WeatherAPI.com API
- Hot Pepper Gourmet API
- Flask コミュニティ

---

**注記**: このアプリケーションは教育目的で作成されました。商用利用の際、各APIの利用規約を確認してください。
