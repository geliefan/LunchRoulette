#!/usr/bin/python3

"""
WSGI設定ファイル - PythonAnywhere用
Lunch Rouletteアプリケーションのデプロイメント設定

このファイルはPythonAnywhereのWebアプリケーション設定で使用されます。
PythonAnywhereのWebタブで以下の設定を行ってください:
1. Source code: /home/yourusername/lunch-roulette
2. Working directory: /home/yourusername/lunch-roulette  
3. WSGI configuration file: /home/yourusername/lunch-roulette/wsgi.py

注意: 'yourusername'を実際のPythonAnywhereユーザー名に変更してください。
"""

import sys
import os

# プロジェクトディレクトリをPythonパスに追加
# PythonAnywhereでの実際のパスに変更してください
project_home = '/home/yourusername/lunch-roulette'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# 作業ディレクトリを設定
os.chdir(project_home)

# データベース初期化（初回デプロイ時）
try:
    from database import init_database
    init_database('cache.db')
    print("データベース初期化完了")
except Exception as e:
    print(f"データベース初期化エラー: 既に存在する可能性があります。 {e}")

# Flaskアプリケーションをインポート
from app import app as application

# 本番環境設定を確認
if not os.environ.get('SECRET_KEY'):
    print("警告: SECRET_KEYが設定されていません")
if not os.environ.get('OPENWEATHER_API_KEY'):
    print("警告: OPENWEATHER_API_KEYが設定されていません")
if not os.environ.get('HOTPEPPER_API_KEY'):
    print("警告: HOTPEPPER_API_KEYが設定されていません")

# デバッグモードを本番環境では無効化
application.config['DEBUG'] = False

if __name__ == "__main__":
    application.run()
