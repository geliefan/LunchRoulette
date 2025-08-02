#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lunch Roulette - メインアプリケーション
東京エリアのランチスポット発見Webサービス

このアプリケーションは以下の機能を提供します:
- IPアドレスベースの位置情報検出
- リアルタイム天気情報の取得
- 近くのレストラン検索とランダム推薦
- PythonAnywhere無料プラン対応
"""

from flask import Flask, render_template, request, jsonify
import os
from database import init_database
from cache_service import CacheService

# Flaskアプリケーションの初期化
app = Flask(__name__)

# 設定
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DATABASE'] = 'cache.db'

# デバッグモード（本番環境では無効にする）
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# キャッシュサービスの初期化
cache_service = CacheService(db_path=app.config['DATABASE'])


def init_db():
    """
    SQLiteキャッシュデータベースを初期化
    アプリケーション起動時に実行される
    """
    return init_database(app.config['DATABASE'])


@app.route('/')
def index():
    """
    メインページのルート
    位置情報と天気情報を表示し、ルーレット機能を提供
    
    Returns:
        str: レンダリングされたHTMLテンプレート
    """
    # 後のタスクで実装される機能:
    # - IPアドレスから位置情報を取得
    # - 天気情報を取得
    # - テンプレートに情報を渡す
    
    return render_template('index.html')


@app.route('/roulette', methods=['POST'])
def roulette():
    """
    レストランルーレットのエンドポイント
    ランダムなレストラン推薦を返す
    
    Returns:
        dict: レストラン情報のJSONレスポンス
    """
    try:
        # 後のタスクで実装される機能:
        # - リクエストから位置情報を取得
        # - レストラン検索を実行
        # - 距離計算を実行
        # - ランダム選択を実行
        
        # 現在は基本的なレスポンス構造のみ
        return jsonify({
            'success': True,
            'message': 'ルーレット機能は後のタスクで実装されます'
        })
        
    except Exception as e:
        # エラーハンドリング
        app.logger.error(f'ルーレット処理でエラーが発生: {str(e)}')
        return jsonify({
            'error': True,
            'message': 'レストラン検索中にエラーが発生しました'
        }), 500


@app.errorhandler(404)
def not_found_error(error):
    """404エラーハンドラー"""
    return jsonify({'error': True, 'message': 'ページが見つかりません'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500エラーハンドラー"""
    return jsonify({'error': True, 'message': 'サーバー内部エラーが発生しました'}), 500


# アプリケーション起動時の初期化
if __name__ == '__main__':
    # データベース初期化
    init_db()
    
    # 開発サーバー起動
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )