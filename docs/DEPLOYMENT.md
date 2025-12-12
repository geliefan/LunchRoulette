# PythonAnywhere デプロイメント手順

## 概要

このドキュメントは、Lunch RouletteアプリケーションをPythonAnywhere無料プランにデプロイするための詳細な手順を説明します。

## 前提条件

- PythonAnywhereアカウント（無料プラン）
- WeatherAPI.com APIキー
- Hot Pepper Gourmet APIキー
- Gitリポジトリ（GitHub、Gitea等）

## 1. PythonAnywhereでのプロジェクトセットアップ

### 1.1 ファイルのアップロード

1. PythonAnywhereのDashboardにログイン
2. "Files" タブを開く
3. 以下のいずれかの方法でプロジェクトをアップロード

#### 方法A: Gitクローン（推奨）

```bash
# Bashコンソールで実行
cd ~
git clone <your-git-repository-url>
cd lunch-roulette
```

#### 方法B: ファイル直接アップロード

- プロジェクトファイルを手動でアップロード
- ディレクトリ構造を維持

### 1.2 仮想環境の作成

```bash
# Bashコンソールで実行
cd ~/lunch-roulette
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. 環境変数の設定

### 2.1 必須環境変数

PythonAnywhereのWebタブで以下の環境変数を設定してください。

| 変数名 | 説明 | 値 | デフォルト |
|--------|------|-----|-----------|
| `SECRET_KEY` | Flaskセッション暗号化キー | 強力なランダム文字列を設定 | `dev-secret-key-change-in-production` |
| `WEATHERAPI_KEY` | WeatherAPI.com APIキー | 取得したAPIキーを設定 | `weather_api_key` |
| `HOTPEPPER_API_KEY` | Hot Pepper Gourmet APIキー | 取得したAPIキーを設定 | なし（必須） |
| `FLASK_DEBUG` | デバッグモード（本番では`False`推奨） | `False` | `False` |

### 2.2 オプション環境変数

以下の環境変数はデフォルト値があるため、必須ではありません。必要に応じて設定してください。

| 変数名 | 説明 | デフォルト値 |
|--------|------|------------|
| `DEFAULT_BUDGET_CODE` | デフォルト予算カテゴリ（Hot Pepper予算コード） | `None`（すべて） |
| `DEFAULT_MAX_WALKING_TIME_MIN` | デフォルト最大徒歩時間（分） | `10` |
| `DATABASE_PATH` | SQLiteキャッシュDBパス | `cache.db` |
| `CACHE_TTL_MINUTES` | キャッシュ有効期限（分） | `10` |
| `DEFAULT_LATITUDE` | デフォルト緯度（東京駅） | `35.6812` |
| `DEFAULT_LONGITUDE` | デフォルト経度（東京駅） | `139.7671` |
| `SEARCH_RADIUS_KM` | レストラン検索半径（km） | `1.0` |
| `MAX_BUDGET_YEN` | 最大予算（円） | `1200` |

### 2.2 環境変数設定手順

1. PythonAnywhereのWebタブを開く
2. "Environment variables" セクションを見つける
3. 環境変数を追加

   - Name: 変数名を入力
   - Value: 対応する値を入力
   - "Set" ボタンをクリック

### 2.3 APIキーの取得方法

**WeatherAPI.com APIキー:**

1. [WeatherAPI.com](https://www.weatherapi.com/) にアクセス
2. アカウント作成（Sign Up）
3. ダッシュボードでAPIキーを確認
4. 無料プランで十分（月100万リクエストまで）

**Hot Pepper Gourmet APIキー:**

1. [リクルートWebサービス](https://webservice.recruit.co.jp/) にアクセス
2. アカウント作成・ログイン
3. Hot Pepper Gourmet Search API のAPIキーを取得

## 3. Webアプリケーションの設定

### 3.1 基本設定

1. PythonAnywhereのWebタブを開く
2. "Add a new web app" をクリック
3. 以下の設定を行う

| 項目 | 設定値 |
|------|--------|
| Python version | Python 3.11 |
| Framework | Manual configuration |
| Source code | `/home/yourusername/lunch-roulette` |
| Working directory | `/home/yourusername/lunch-roulette` |
| WSGI configuration file | `/home/yourusername/lunch-roulette/src/lunch_roulette/wsgi.py` |

### 3.2 wsgi.pyの設定確認

`src/lunch_roulette/wsgi.py`は自動的にプロジェクトパスを設定します。
特に編集は不要ですが、以下の警告メッセージが表示されないことを確認してください:

```
警告: SECRET_KEYが設定されていません
警告: WEATHERAPI_KEYが設定されていません
警告: HOTPEPPER_API_KEYが設定されていません
```

警告が表示される場合は、環境変数の設定を確認してください。

### 3.3 静的ファイルの設定

Webタブの "Static files" セクションで以下を設定

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/lunch-roulette/src/lunch_roulette/static/` |

## 4. データベースの初期化

### 4.1 自動初期化

`wsgi.py`ファイルにデータベース初期化コードが含まれているため、初回アクセス時に自動的に作成されます。

### 4.2 手動初期化（必要に応じて）

```bash
# Bashコンソールで実行
cd ~/lunch-roulette
source venv/bin/activate
python3 -c "from src.lunch_roulette.models.database import init_database; init_database('cache.db')"
```

## 5. デプロイメント確認

### 5.1 設定確認チェックリスト

- [ ] プロジェクトファイルがアップロード済み
- [ ] 仮想環境が作成され、依存関係がインストール済み
- [ ] 全ての環境変数が設定済み
- [ ] wsgi.pyのパスが正しく設定済み
- [ ] 静的ファイルのマッピングが設定済み
- [ ] Webアプリケーションが有効化済み

### 5.2 動作確認

1. PythonAnywhereのWebタブで "Reload" ボタンをクリック
2. アプリケーションURLにアクセス
3. 以下の機能を確認

   - [ ] ページが正常に表示される
   - [ ] 位置情報が表示される
   - [ ] 天気情報が表示される
   - [ ] ルーレットボタンが動作する
   - [ ] レストラン情報が表示される

### 5.3 ログの確認

エラーが発生した場合は、以下のログを確認

1. PythonAnywhereのWebタブで "Log files"
2. Error log: `/var/log/yourusername.pythonanywhere.com.error.log`
3. Server log: `/var/log/yourusername.pythonanywhere.com.server.log`

## 6. トラブルシューティング

### 6.1 よくある問題と解決方法

#### 問題 "ImportError: No module named 'lunch_roulette'"

- 解決: WSGI configuration fileが `/home/yourusername/lunch-roulette/src/lunch_roulette/wsgi.py` に設定されているか確認
- Working directoryが `/home/yourusername/lunch-roulette` に設定されているか確認
- sys.pathにsrcディレクトリが含まれているか確認（wsgi.pyで自動設定されます）

#### 問題 "API key not found"

- 解決: 環境変数が正しく設定されているか確認
- 変数名にスペルミスがないか確認

#### 問題 "Database is locked"

- 解決: Bashコンソールでアプリケーションプロセスを確認
- 必要に応じてWebアプリケーションをリロード

#### 問題 静的ファイル（CSS/JS）が読み込まれない

- 解決: Static filesの設定を確認
- ファイルパスが正しいか確認

### 6.2 パフォーマンス最適化

#### 無料プランの制限下での運用

- APIキャッシュ機能により外部API呼び出しを最小化
- 1時間あたり50回未満のAPI呼び出し制限を遵守
- SQLiteキャッシュによる高速レスポンス

#### メモリ使用量の最適化

- 不要なライブラリのインポートを避ける
- キャッシュサイズを適切に管理
- 定期的にキャッシュクリーンアップ

## 7. メンテナンス

### 7.1 定期的な作業

**月次:**

- [ ] APIキーの有効期限確認
- [ ] ログファイルのサイズ確認
- [ ] キャッシュデータベースのサイズ確認

**必要に応じて:**

- [ ] 依存関係のアップデート
- [ ] セキュリティパッチの適用
- [ ] キャッシュデータベースの最適化

### 7.2 アップデート手順

```bash
# Bashコンソールで実行
cd ~/lunch-roulette
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
```

その後、WebタブでReloadを実行。

## 8. セキュリティ考慮事項

### 8.1 本番環境の注意点

- [ ] `SECRET_KEY`を本番用の強力なキーに変更
- [ ] `FLASK_DEBUG`を`False`に設定
- [ ] APIキーを環境変数で管理し、コードに直接記述しない
- [ ] 定期的にセキュリティアップデートを適用

### 8.2 データ保護

- 位置情報はIPベースのみ（HTTPS不使用）
- 個人識別情報はログに記録しない
- キャッシュデータに個人情報を含めない

## 9. サポート情報

### 9.1 関連リンク

- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [WeatherAPI.com Documentation](https://www.weatherapi.com/docs/)
- [Hot Pepper Gourmet API](https://webservice.recruit.co.jp/doc/hotpepper/)

### 9.2 プロジェクト情報

- 技術スタック: Python 3.11, Flask 3.0, SQLite
- 外部API: WeatherAPI.com (天気情報), Hot Pepper Gourmet Search API (レストラン情報)
- 対応プラットフォーム: PythonAnywhere無料プラン