# Lunch Roulette

東京エリアのランチスポット発見Webサービス

## 概要E

Lunch Rouletteは、東京エリアのユーザーがリアルタイムの天気データと徒歩距離計算を絁E��合わせてランチスポットを発見できる低コスチEebサービスです。PythonAnywhere無料�Eランで動作し、予算制紁E�Eで近くのレストランを見つけるためのシンプルで魁E��皁E��インターフェースを提供します、E

## 主な機�E

- **自動位置検�E**: IPアドレスベ�Eスの位置惁E��検�E
- **リアルタイム天気情報**: OpenWeatherMap APIを使用した現在の天気表示
- **レストラン検索**: Hot Pepper Gourmet APIを使用した半征Ekm以冁E�Eレストラン検索
- **予算フィルタリング**: ランチ予算≤¥1,200での絞り込み
- **距離計箁E*: ハ�Eバ�Eサイン公式を使用した正確な徒歩距離計箁E
- **キャチE��ング**: SQLiteを使用した10刁E��のAPIレスポンスキャチE��ュ
- **モダンUI**: レスポンシブデザインとモダンなユーザーインターフェース

## 技術スタチE��

- **バックエンチE*: Python 3.11, Flask 3.x
- **チE�Eタベ�Eス**: SQLite�E�キャチE��ュ用�E�E
- **フロントエンチE*: HTML5, CSS3, バニラJavaScript
- **外部API**: 
  - OpenWeatherMap One Call 3.0 API
  - Hot Pepper Gourmet Web API
  - ipapi.co�E�位置惁E��検�E�E�E
- **チE�EロイメンチE*: PythonAnywhere無料�Eラン

## セチE��アチE�E手頁E

### 前提条件

- Python 3.11以丁E
- pip�E�Eythonパッケージマネージャー�E�E
- インターネット接続（外部API使用のため�E�E

### ローカル開発環墁E�EセチE��アチE�E

1. **リポジトリのクローン**
   ```bash
   git clone <repository-url>
   cd lunch-roulette
   ```

2. **仮想環墁E�E作�Eと有効匁E*
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **依存関係�Eインスト�Eル**
   ```bash
   pip install -r requirements.txt
   ```

4. **環墁E��数の設宁E*
   
   以下�E環墁E��数を設定してください�E�E
   
   ```bash
   # Windows (コマンド�Eロンプト)
   set OPENWEATHER_API_KEY=your_openweather_api_key
   set HOTPEPPER_API_KEY=your_hotpepper_api_key
   set FLASK_DEBUG=True
   
   # Windows (PowerShell)
   $env:OPENWEATHER_API_KEY="your_openweather_api_key"
   $env:HOTPEPPER_API_KEY="your_hotpepper_api_key"
   $env:FLASK_DEBUG="True"
   
   # macOS/Linux
   export OPENWEATHER_API_KEY=your_openweather_api_key
   export HOTPEPPER_API_KEY=your_hotpepper_api_key
   export FLASK_DEBUG=True
   ```

5. **チE�Eタベ�Eスの初期匁E*
   ```bash
   python database.py
   ```

6. **アプリケーションの起勁E*
   ```bash
   python app.py
   ```

7. **ブラウザでアクセス**
   
   http://localhost:5000 にアクセスしてアプリケーションを確誁E

### APIキーの取征E

#### OpenWeatherMap API
1. [OpenWeatherMap](https://openweathermap.org/api)にアカウント登録
2. One Call API 3.0のAPIキーを取征E
3. 無料�Eランでは1日1,000回まで利用可能

#### Hot Pepper Gourmet API
1. [リクルーチEebサービス](https://webservice.recruit.co.jp/)にアカウント登録
2. Hot Pepper Gourmet APIのAPIキーを取征E
3. 無料�Eランでは1日3,000回まで利用可能

## PythonAnywhereチE�Eロイメント手頁E

> **📋 詳細なチE�Eロイメント手頁E��トラブルシューチE��ングは [DEPLOYMENT.md](DEPLOYMENT.md) を参照してください、E*

### クイチE��スターチE

1. **PythonAnywhereアカウント�E準備**
   - [PythonAnywhere](https://www.pythonanywhere.com/)で無料アカウントを作�E
   - Bashコンソールを開ぁE

2. **プロジェクト�EアチE�EローチE*
   ```bash
   cd ~
   git clone <your-repository-url> lunch-roulette
   cd lunch-roulette
   ```

3. **仮想環墁E�EセチE��アチE�E**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **環墁E��数の設宁E*
   PythonAnywhereのWebタブで以下�E環墁E��数を設定！E
   - `SECRET_KEY`: FlaskセチE��ョン暗号化キー�E�本番用の強力なキー�E�E
   - `OPENWEATHER_API_KEY`: OpenWeatherMap APIキー
   - `HOTPEPPER_API_KEY`: Hot Pepper Gourmet APIキー
   - `FLASK_DEBUG`: `False`�E�本番環墁E��E

### 5. WSGIファイルの設宁E

PythonAnywhereのWebタブでWSGIファイルを編雁E��E

```python
#!/usr/bin/python3

import sys
import os

# プロジェクトディレクトリをPythonパスに追加
project_home = '/home/yourusername/lunch-roulette'  # 実際のパスに変更
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# 仮想環墁E�Eパスを設宁E
activate_this = '/home/yourusername/lunch-roulette/.venv/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), dict(__file__=activate_this))

# Flaskアプリケーションをインポ�EチE
from app import app as application

if __name__ == "__main__":
    application.run()
```

### 6. 静的ファイルの設宁E

PythonAnywhereのWebタブで静的ファイルマッピングを設定！E

- URL: `/static/`
- Directory: `/home/yourusername/lunch-roulette/static/`

### 7. チE�Eタベ�Eスの初期匁E

```bash
cd ~/lunch-roulette
source .venv/bin/activate
python database.py
```

### 8. アプリケーションの起勁E

PythonAnywhereのWebタブで「Reload」�EタンをクリチE��してアプリケーションを起勁E

## チE��チE

### 単体テスト実衁E

```bash
# 全チE��トを実衁E
pytest

# 特定�EチE��トファイルを実衁E
pytest test_cache_service.py

# カバレチE��レポ�Eト付きで実衁E
pytest --cov=. --cov-report=html
```

### 統合テスト実衁E

```bash
# 統合テストを実衁E
pytest test_integration_*.py

# エンド�EイントテスチE
python test_endpoints.py
```

### コード品質チェチE��

```bash
# flake8によるリンチE��ング
flake8 .

# 自動フォーマット（オプション�E�E
autopep8 --in-place --aggressive --aggressive *.py
```

## プロジェクト構造

```
lunch-roulette/
├── app.py                          # メインFlaskアプリケーション
├── wsgi.py                         # PythonAnywhere用WSGI設宁E
├── requirements.txt                # Python依存関俁E
├── .flake8                        # flake8設宁E
├── pytest.ini                     # pytest設宁E
├── README.md                       # こ�Eファイル
├── cache.db                        # SQLiteキャチE��ュチE�Eタベ�Eス
├── database.py                     # チE�Eタベ�Eス初期化�E管琁E
├── cache_service.py                # キャチE��ュサービス
├── location_service.py             # 位置惁E��サービス
├── weather_service.py              # 天気情報サービス
├── restaurant_service.py           # レストラン検索サービス
├── distance_calculator.py          # 距離計算サービス
├── restaurant_selector.py          # レストラン選択ロジチE��
├── error_handler.py                # エラーハンドリング
├── static/                         # 静的ファイル
━E  ├── css/
━E  ━E  └── style.css              # メインスタイルシーチE
━E  └── js/
━E      └── main.js                # メインJavaScript
├── templates/                      # HTMLチE��プレーチE
━E  └── index.html                 # メインペ�EジチE��プレーチE
└── test_*.py                      # チE��トファイル群
```

## 技術理論概要E

### 地琁E��報シスチE���E�EIS�E�E

#### ハ�Eバ�Eサイン公弁E
地琁E���E2点間�E距離を計算する数学皁E��法。球面三角法を使用して、緯度・経度から直線距離を算�Eします、E

```python
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # 地琁E�E半征E��Em�E�E
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c
```

#### IPジオロケーション
IPアドレスから地琁E��位置を推定する技術、ESPのチE�Eタベ�EスとIPアドレス割り当て惁E��を基に、おおよそ�E位置を特定します、E

### API統合パターン

#### RESTful API設訁E
- **統一インターフェース**: HTTP動詞！EET, POST�E��E適刁E��使用
- **スチE�Eトレス**: サーバ�Eはクライアント�E状態を保持しなぁE
- **キャチE��ュ可能**: レスポンスにキャチE��ュ惁E��を含める

#### レート制限対筁E
- **持E��バックオチE*: 失敗時の再試行間隔を持E��皁E��増加
- **キャチE��ング**: 同一リクエスト�E結果を一定時間保孁E
- **バッチ�E琁E*: 褁E��のリクエストをまとめて処琁E

### キャチE��ング戦略

#### 時間ベ�EスキャチE��ュ�E�ETL�E�E
```python
# 10刁E��のキャチE��ュ
cache_duration = timedelta(minutes=10)
expires_at = datetime.now() + cache_duration
```

#### キャチE��ュ無効化戦略
- **タイムスタンプ�Eース**: 作�E時刻と現在時刻を比輁E
- **自動クリーンアチE�E**: 期限刁E��チE�Eタの定期削除
- **LRU�E�Eeast Recently Used�E�E*: 使用頻度の低いチE�Eタから削除

### パフォーマンス最適匁E

#### フロントエンド最適匁E
- **CSS/JS最小化**: ファイルサイズの削渁E
- **画像最適匁E*: WebP形式�E使用、E��刁E��サイズ設宁E
- **ブラウザキャチE��ュ**: Cache-Controlヘッダーの設宁E

#### バックエンド最適匁E
- **チE�Eタベ�EスインチE��クス**: 検索性能の向丁E
- **並列�E琁E*: 褁E��API呼び出し�E同時実衁E
- **メモリ管琁E*: 不要なオブジェクト�E適刁E��解放

## トラブルシューチE��ング

### よくある問題と解決方況E

#### 1. APIキーエラー
```
エラー: Invalid API key
解決: 環墁E��数が正しく設定されてぁE��か確誁E
```

#### 2. チE�Eタベ�Eス接続エラー
```
エラー: database is locked
解決: アプリケーションを�E起動し、データベ�Eスファイルの権限を確誁E
```

#### 3. 位置惁E��取得失敁E
```
エラー: Location detection failed
解決: チE��ォルト位置�E�東京駁E��が使用されます。正常な動作です、E
```

#### 4. レストラン検索結果なぁE
```
エラー: No restaurants found
解決: 検索篁E��を拡大するか、予算制限を緩和してください
```

### ログの確誁E

```bash
# アプリケーションログの確誁E
tail -f /var/log/pythonanywhere.log

# エラーログの確誁E
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
# アプリケーションを実衁E
"
```

## 貢献

1. こ�Eリポジトリをフォーク
2. 機�Eブランチを作�E (`git checkout -b feature/amazing-feature`)
3. 変更をコミッチE(`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作�E

## ライセンス

こ�Eプロジェクト�EMITライセンスの下で公開されてぁE��す。詳細は`LICENSE`ファイルを参照してください、E

## 作老E

- 開発老E [Your Name]
- Email: [your.email@example.com]
- GitHub: [your-github-username]

## 謝辁E

- OpenWeatherMap API
- Hot Pepper Gourmet API
- PythonAnywhere
- Flask コミュニティ

---

**注愁E*: こ�Eアプリケーションは教育目皁E��作�Eされました。商用利用の際�E、各APIの利用規紁E��確認してください�