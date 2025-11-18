#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database - SQLiteキャッシュデータベース管理モジュール
Lunch Roulette用のキャッシュデータベースの初期化と管理を行う

このモジュールは以下の機能を提供します:
- キャッシュテーブルのスキーマ定義
- データベース初期化処理
- インデックス作成による最適化
"""

import sqlite3
import os
from datetime import datetime


def get_db_connection(db_path='cache.db'):
    """
    データベース接続を取得

    Args:
        db_path (str): データベースファイルのパス

    Returns:
        sqlite3.Connection: データベース接続オブジェクト
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 辞書形式でのアクセスを可能にする
    return conn


def init_database(db_path='cache.db'):
    """
    SQLiteキャッシュデータベースを初期化

    キャッシュテーブルを作成し、必要なインデックスを設定する。
    既存のテーブルがある場合は何もしない（CREATE TABLE IF NOT EXISTSを使用）。

    Args:
        db_path (str): データベースファイルのパス

    Returns:
        bool: 初期化が成功した場合True
    """
    try:
        with get_db_connection(db_path) as conn:
            # キャッシュテーブルの作成
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            ''')

            # パフォーマンス向上のためのインデックス作成
            # cache_keyでの検索を高速化
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_cache_key
                ON cache(cache_key)
            ''')

            # expires_atでの検索を高速化（期限切れデータの削除用）
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_expires_at
                ON cache(expires_at)
            ''')

            # created_atでの検索を高速化（統計情報取得用）
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON cache(created_at)
            ''')

            conn.commit()
            print(f"データベース初期化完了: {db_path}")
            return True

    except sqlite3.Error as e:
        print(f"データベース初期化エラー: {e}")
        return False


def cleanup_expired_cache(db_path='cache.db'):
    """
    期限切れのキャッシュデータを削除

    現在時刻よりもexpires_atが古いレコードを削除する。
    定期的に実行することでデータベースサイズを最適化する。

    Args:
        db_path (str): データベースファイルのパス

    Returns:
        int: 削除されたレコード数
    """
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.execute('''
                DELETE FROM cache
                WHERE expires_at < ?
            ''', (datetime.now(),))

            deleted_count = cursor.rowcount
            conn.commit()

            if deleted_count > 0:
                print(f"期限切れキャッシュを削除: {deleted_count}件")

            return deleted_count

    except sqlite3.Error as e:
        print(f"キャッシュクリーンアップエラー: {e}")
        return 0


def get_cache_stats(db_path='cache.db'):
    """
    キャッシュデータベースの統計情報を取得

    Args:
        db_path (str): データベースファイルのパス

    Returns:
        dict: 統計情報（総レコード数、有効レコード数、期限切れレコード数など）
    """
    try:
        with get_db_connection(db_path) as conn:
            # 総レコード数
            total_count = conn.execute('SELECT COUNT(*) FROM cache').fetchone()[0]

            # 有効レコード数
            valid_count = conn.execute('''
                SELECT COUNT(*) FROM cache
                WHERE expires_at > ?
            ''', (datetime.now(),)).fetchone()[0]

            # 期限切れレコード数
            expired_count = total_count - valid_count

            return {
                'total_records': total_count,
                'valid_records': valid_count,
                'expired_records': expired_count,
                'database_size': os.path.getsize(db_path) if os.path.exists(db_path) else 0
            }

    except sqlite3.Error as e:
        print(f"統計情報取得エラー: {e}")
        return {
            'total_records': 0,
            'valid_records': 0,
            'expired_records': 0,
            'database_size': 0
        }


if __name__ == '__main__':
    """
    スクリプトとして直接実行された場合の処理
    データベースの初期化とテスト用データの挿入を行う
    """
    print("SQLiteキャッシュデータベース初期化スクリプト")
    print("=" * 50)

    # データベース初期化
    if init_database():
        print("✔ データベース初期化成功")

        # 統計情報表示
        stats = get_cache_stats()
        print("✔ 統計情報:")
        print(f"  - 総レコード数: {stats['total_records']}")
        print(f"  - 有効レコード数: {stats['valid_records']}")
        print(f"  - 期限切れレコード数: {stats['expired_records']}")
        print(f"  - データベースサイズ: {stats['database_size']} bytes")

        # 期限切れデータのクリーンアップ
        cleanup_expired_cache()

    else:
        print("✘ データベース初期化失敗")
