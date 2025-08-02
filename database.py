#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database - SQLiteキャチE��ュチE�Eタベ�Eス管琁E��ジュール
Lunch Roulette用のキャチE��ュチE�Eタベ�Eスの初期化と管琁E��行う

こ�Eモジュールは以下�E機�Eを提供しまぁE
- キャチE��ュチE�Eブルのスキーマ定義
- チE�Eタベ�Eス初期化�E琁E
- インチE��クス作�Eによる最適匁E
"""

import sqlite3
import os
from datetime import datetime


def get_db_connection(db_path='cache.db'):
    """
    チE�Eタベ�Eス接続を取征E

    Args:
        db_path (str): チE�Eタベ�Eスファイルのパス

    Returns:
        sqlite3.Connection: チE�Eタベ�Eス接続オブジェクチE
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 辞書形式でのアクセスを可能にする
    return conn


def init_database(db_path='cache.db'):
    """
    SQLiteキャチE��ュチE�Eタベ�Eスを�E期化

    キャチE��ュチE�Eブルを作�Eし、忁E��なインチE��クスを設定する、E
    既存�EチE�Eブルがある場合�E何もしなぁE��EREATE TABLE IF NOT EXISTS�E�、E

    Args:
        db_path (str): チE�Eタベ�Eスファイルのパス

    Returns:
        bool: 初期化が成功した場吁Erue
    """
    try:
        with get_db_connection(db_path) as conn:
            # キャチE��ュチE�Eブルの作�E
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            ''')

            # パフォーマンス向上�EためのインチE��クス作�E
            # cache_keyでの検索を高速化
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_cache_key
                ON cache(cache_key)
            ''')

            # expires_atでの検索を高速化�E�期限�Eれデータの削除用�E�E
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_expires_at
                ON cache(expires_at)
            ''')

            # created_atでの検索を高速化�E�統計情報取得用�E�E
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON cache(created_at)
            ''')

            conn.commit()
            print(f"チE�Eタベ�Eス初期化完亁E {db_path}")
            return True

    except sqlite3.Error as e:
        print(f"チE�Eタベ�Eス初期化エラー: {e}")
        return False


def cleanup_expired_cache(db_path='cache.db'):
    """
    期限刁E��のキャチE��ュチE�Eタを削除

    現在時刻よりもexpires_atが古ぁE��コードを削除する、E
    定期皁E��実行することでチE�Eタベ�Eスサイズを最適化する、E

    Args:
        db_path (str): チE�Eタベ�Eスファイルのパス

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
                print(f"期限刁E��キャチE��ュを削除: {deleted_count}件")

            return deleted_count

    except sqlite3.Error as e:
        print(f"キャチE��ュクリーンアチE�Eエラー: {e}")
        return 0


def get_cache_stats(db_path='cache.db'):
    """
    キャチE��ュチE�Eタベ�Eスの統計情報を取征E

    Args:
        db_path (str): チE�Eタベ�Eスファイルのパス

    Returns:
        dict: 統計情報�E�総レコード数、有効レコード数、期限�Eれレコード数�E�E
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

            # 期限刁E��レコード数
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
    スクリプトとして直接実行された場合�E処琁E
    チE�Eタベ�Eスの初期化とチE��ト用チE�Eタの挿入を行う
    """
    print("SQLiteキャチE��ュチE�Eタベ�Eス初期化スクリプト")
    print("=" * 50)

    # チE�Eタベ�Eス初期匁E
    if init_database():
        print("✁EチE�Eタベ�Eス初期化�E劁E)

        # 統計情報表示
        stats = get_cache_stats()
        print("✁E統計情報:")
        print(f"  - 総レコード数: {stats['total_records']}")
        print(f"  - 有効レコード数: {stats['valid_records']}")
        print(f"  - 期限刁E��レコード数: {stats['expired_records']}")
        print(f"  - チE�Eタベ�Eスサイズ: {stats['database_size']} bytes")

        # 期限刁E��チE�EタのクリーンアチE�E
        cleanup_expired_cache()

    else:
        print("✁EチE�Eタベ�Eス初期化失敁E)
