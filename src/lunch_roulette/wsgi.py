#!/usr/bin/python3

"""
WSGI設定ファイル - PythonAnywhere用
Lunch Rouletteアプリケーションのデプロイメント設定

このファイルはPythonAnywhereのWebアプリケーション設定で使用されます。
PythonAnywhereのWebタブで以下の設定を行ってください:
1. Source code: /home/yourusername/lunch-roulette
2. Working directory: /home/yourusername/lunch-roulette  
3. WSGI configuration file: /home/yourusername/lunch-roulette/src/lunch_roulette/wsgi.py

注意: 'yourusername'を実際のPythonAnywhereユーザー名に変更してください。
"""

import sys
import os
from pathlib import Path

# プロジェクトディレクトリをPythonパスに追加
project_home = str(Path(__file__).parent.parent.parent)
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# srcディレクトリもPythonパスに追加  
src_path = os.path.join(project_home, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 作業ディレクトリを設定
os.chdir(project_home)

# データベース初期化（初回デプロイ時）
try:
    from lunch_roulette.models.database import init_database
    init_database(os.path.join(project_home, 'cache.db'))
    print("データベース初期化完了")
except Exception as e:
    print(f"データベース初期化エラー: 既に存在する可能性があります。 {e}")

# Flaskアプリケーションをインポート
from lunch_roulette.app import app as application

# 本番環境設定を確認
if not os.environ.get('SECRET_KEY'):
    print("警告: SECRET_KEYが設定されていません")
if not os.environ.get('WEATHERAPI_KEY'):
    print("警告: WEATHERAPI_KEYが設定されていません")
if not os.environ.get('HOTPEPPER_API_KEY'):
    print("警告: HOTPEPPER_API_KEYが設定されていません")

# デバッグモードを本番環境では無効化
application.config['DEBUG'] = False

if __name__ == "__main__":
    application.run()
