#!/usr/bin/python3

"""
WSGI設定ファイル - PythonAnywhere用
Lunch Rouletteアプリケーションのデプロイメント設定
"""

import sys
import os

# プロジェクトディレクトリをPythonパスに追加
project_home = '/home/yourusername/lunch-roulette'  # PythonAnywhereでの実際のパスに変更してください
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Flaskアプリケーションをインポート
from app import app as application

if __name__ == "__main__":
    application.run()