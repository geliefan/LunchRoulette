#!/usr/bin/env python3
"""
Lunch Roulette パッケージのメインエントリーポイント

このファイルにより、以下のコマンドでアプリケーションを実行できます：
python -m lunch_roulette
"""

from .app import app, init_db
import os

if __name__ == '__main__':
    # データベース初期化
    init_db()

    # 開発サーバー起動
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )