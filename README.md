# lunch-roulette

東京エリアのランチスポット発見Webサービス

## 概要

Lunch Rouletteは、東京エリアのユーザーがリアルタイムの天気データと徒歩距離計算を組み合わせてランチスポットを発見できる低コストWebサービスです。PythonAnywhere無料プランで動作し、予算制限下で近くのレストランを見つけるためのシンプルで効率的なインターフェースを提供します。

## 主な機能

- **自動位置検出**: IPアドレスベースの位置情報検出
- **リアルタイム天気情報**: WeatherAPI.com APIを使用した現在の天気表示
- **レストラン検索**: Hot Pepper Gourmet APIを使用した半径1km以内のレストラン検索
- **予算フィルタリング**: ランチ予算≤¥1,200での絞り込み
- **距離計算**: ハーバーサイン公式を使用した正確な徒歩距離計算
- **キャッシング**: SQLiteを使用した10分間のAPIレスポンスキャッシュ
- **モダンUI**: レスポンシブデザインとモダンなユーザーインターフェース

## 技術スタック

- **バックエンド**: Python 3.11, Flask 3.x
- **データベース**: SQLite（キャッシュ用）
- **フロントエンド**: HTML5, CSS3, バニラJavaScript
- **外部API**: 
  - WeatherAPI.com Current Weather API
  - Hot Pepper Gourmet Web API
  - ipapi.co（位置情報検出用）
- **デプロイメント**: PythonAnywhere無料プラン

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

   以下の環境変数を設定してください。

   ```bash
   # Windows (コマンドプロンプト)
   set WEATHERAPI_KEY=your_weatherapi_key
   set HOTPEPPER_API_KEY=your_hotpepper_api_key
   set FLASK_DEBUG=True
   
   # Windows (PowerShell)
   $env:WEATHERAPI_KEY="your_weatherapi_key"
   $env:HOTPEPPER_API_KEY="your_hotpepper_api_key"
   $env:FLASK_DEBUG="True"
   
   # macOS/Linux
   export WEATHERAPI_KEY=your_weatherapi_key
   export HOTPEPPER_API_KEY=your_hotpepper_api_key
   export FLASK_DEBUG=True
   ```

5. **データベースの初期化**

   ```bash
   python -c "from src.lunch_roulette.models.database import init_database; init_database('cache.db')"
   ```

6. **アプリケーションの起動**

   ```bash
   # 新しい方法（推奨）
   python run.py
   
   # または直接実行
   python -m lunch_roulette.app
   ```

7. **ブラウザでアクセス**

   [http://localhost:5000](http://localhost:5000) にアクセスしてアプリケーションを確認

### APIキーの取得

#### WeatherAPI.com API

1. [WeatherAPI.com](https://www.weatherapi.com/)にアカウント登録

2. Current Weather APIのAPIキーを取得

3. 無料プランでは1日100万回まで利用可能

**Note**: 現在、テスト用APIキー `weather_api_key` がデフォルトで設定されています。

#### Hot Pepper Gourmet API


1. [リクルートWebサービス](https://webservice.recruit.co.jp/)にアカウント登録

2. Hot Pepper Gourmet APIのAPIキーを取得

3. 無料プランでは1日3,000回まで利用可能

## テスト

### 単体テスト実行

```bash
# 全テストを実行
pytest

# 特定テストファイルを実行
pytest test_cache_service.py

# カバレッジレポート付きで実行
pytest --cov=. --cov-report=html
```

### 統合テスト実行

```bash
# 統合テストを実行
pytest test_integration_*.py

# エンドポイントテスト
python test_endpoints.py
```

### コード品質チェック

```bash
# flake8によるリンティング
flake8 .

# 自動フォーマット（オプション）
autopep8 --in-place --aggressive --aggressive *.py
```

## プロジェクト構造

```plaintext
lunch-roulette/
├── src/                             # ソースコード
│   └── lunch_roulette/              # メインパッケージ
│       ├── __init__.py              # パッケージ初期化
│       ├── app.py                   # メインFlaskアプリケーション
│       ├── config.py                # 設定管理
│       ├── wsgi.py                  # PythonAnywhere用WSGI設定
│       ├── api/                     # API関連モジュール
│       │   └── __init__.py
│       ├── models/                  # データモデル
│       │   ├── __init__.py
│       │   └── database.py          # データベース管理
│       ├── services/                # ビジネスロジック
│       │   ├── __init__.py
│       │   ├── cache_service.py     # キャッシュサービス
│       │   ├── location_service.py  # 位置情報サービス
│       │   ├── weather_service.py   # 天気情報サービス
│       │   └── restaurant_service.py # レストラン検索サービス
│       └── utils/                   # ユーティリティ
│           ├── __init__.py
│           ├── distance_calculator.py # 距離計算サービス
│           ├── restaurant_selector.py # レストラン選択ロジック
│           └── error_handler.py      # エラーハンドリング
│       ├── static/                   # 静的ファイル
│       │   ├── css/
│       │   │   └── style.css         # メインスタイルシート
│       │   └── js/
│       │       └── main.js           # メインJavaScript
│       └── templates/                # HTMLテンプレート
│           └── index.html            # メインページテンプレート
├── tests/                           # テスト
│   ├── __init__.py
│   ├── conftest.py                  # pytest設定
│   ├── pytest.ini                   # pytest設定
│   ├── unit/                        # 単体テスト
│   │   ├── __init__.py
│   │   └── test_*.py                # 各種テストファイル
│   └── integration/                 # 統合テスト
│       └── __init__.py
├── docs/                           # ドキュメント
├── config/                         # 設定ファイル
├── run.py                          # 開発用エントリーポイント
├── pyproject.toml                  # プロジェクト設定
├── requirements.txt                # Python依存関係
├── requirements-dev.txt            # 開発用依存関係
├── README.md                       # このファイル
├── DEPLOYMENT.md                   # デプロイメントガイド
├── .flake8                        # flake8設定
├── .gitignore                     # Git無視ファイル
└── cache.db                       # SQLiteキャッシュデータベース
```

## 技術理論概要

### 地理情報システム (GIS)

#### ハーバーサイン公式

地理上の2点間距離を計算する数学的手法。球面三角法を使用して、緯度・経度から直線距離を算出します。

```python
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # 地球の半径 (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c
```

#### IPジオロケーション

IPアドレスから地理的な位置を推定する技術。ISPのデータベースとIPアドレス割り当て情報を基に、おおよその位置を特定します。

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
# アプリケーションログの確認
tail -f /var/log/pythonanywhere.log

# エラーログの確認
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
# アプリケーションを実行
"
```

## 貢献

1. こリポジトリをフォーク
2. 機ブランチを作 (`git chckout -b fatur/amazing-fatur`)
3. 変更をコミッチ(`git commit -m 'Add amazing fatur'`)
4. ブランチにプッシュ (`git push origin fatur/amazing-fatur`)
5. プルリクエストを作

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は`LICENSE`ファイルを参照してください。

## 作成者

- 開発者: [Your Name]
- メール: [your.email@example.com]
- GitHub: [your-github-username]

## 謝辞

- WeatherAPI.com API
- Hot Pepper Gourmet API
- PythonAnywhere
- Flask コミュニティ

---

**注記**: このアプリケーションは教育目的で作成されました。商用利用の際、各APIの利用規約を確認してください。
