#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
データベース操作の統合テスト
実際のSQLiteデータベースとの統合をテスト
"""

import pytest
import tempfile
import os
import sqlite3
from datetime import datetime, timedelta
from lunch_roulette.models.database import (
    init_database, get_db_connection, cleanup_expired_cache,
    get_cache_stats
)
from lunch_roulette.services.cache_service import CacheService


class TestDatabaseIntegration:
    """データベース操作の統合テスト"""

    @pytest.fixture
    def temp_db_path(self):
        """テスト用の一時データベースファイルパス"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            temp_path = temp_file.name
        yield temp_path
        # テスト後にファイルを削除（Windowsでの権限エラー対策）
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        except (PermissionError, OSError):
            # Windows環境でファイルが使用中の場合は無視
            pass

    def test_init_database_success(self, temp_db_path):
        """データベース初期化成功テスト"""
        result = init_database(temp_db_path)

        assert result is True
        assert os.path.exists(temp_db_path)

        # テーブルが作成されていることを確認
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='cache'
            """)
            table_exists = cursor.fetchone() is not None
            assert table_exists is True

    def test_init_database_existing_file(self, temp_db_path):
        """既存データベースファイルの初期化テスト"""
        # 最初に初期化
        init_database(temp_db_path)

        # 既存ファイルに対する再初期化
        result = init_database(temp_db_path)

        assert result is True
        assert os.path.exists(temp_db_path)

    def test_get_db_connection_success(self, temp_db_path):
        """データベース接続取得成功テスト"""
        init_database(temp_db_path)

        with get_db_connection(temp_db_path) as conn:
            assert conn is not None

            # 基本的なクエリ実行テスト
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            count = cursor.fetchone()[0]
            assert count == 0

    def test_get_db_connection_row_factory(self, temp_db_path):
        """データベース接続のRow Factoryテスト"""
        init_database(temp_db_path)

        with get_db_connection(temp_db_path) as conn:
            # テストデータを挿入
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('test_key', '{"test": "data"}', datetime.now() + timedelta(hours=1)))
            conn.commit()

            # Row Factoryが設定されていることを確認
            cursor = conn.execute("SELECT cache_key, data FROM cache WHERE cache_key = ?", ('test_key',))
            row = cursor.fetchone()

            # 辞書形式でアクセスできることを確認
            assert row['cache_key'] == 'test_key'
            assert row['data'] == '{"test": "data"}'

    def test_cache_table_structure(self, temp_db_path):
        """キャッシュテーブル構造確認テスト"""
        init_database(temp_db_path)

        # テーブル構造を確認
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute("PRAGMA table_info(cache)")
            columns = cursor.fetchall()

            column_names = [col[1] for col in columns]
            assert 'id' in column_names
            assert 'cache_key' in column_names
            assert 'data' in column_names
            assert 'created_at' in column_names
            assert 'expires_at' in column_names

    def test_cleanup_expired_cache_success(self, temp_db_path):
        """期限切れキャッシュクリーンアップ成功テスト"""
        init_database(temp_db_path)

        # テストデータを挿入（有効・期限切れ混在）
        with sqlite3.connect(temp_db_path) as conn:
            # 有効なキャッシュ
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key', '{"test": "valid"}', datetime.now() + timedelta(hours=1)))

            # 期限切れキャッシュ
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('expired_key1', '{"test": "expired1"}', datetime.now() - timedelta(hours=1)))

            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('expired_key2', '{"test": "expired2"}', datetime.now() - timedelta(minutes=30)))

            conn.commit()

        # クリーンアップ実行
        deleted_count = cleanup_expired_cache(temp_db_path)

        assert deleted_count == 2

        # 有効なキャッシュのみ残っていることを確認
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            remaining_count = cursor.fetchone()[0]
            assert remaining_count == 1

            cursor = conn.execute("SELECT cache_key FROM cache")
            remaining_key = cursor.fetchone()[0]
            assert remaining_key == 'valid_key'

    def test_cleanup_expired_cache_no_expired(self, temp_db_path):
        """期限切れキャッシュなしのクリーンアップテスト"""
        init_database(temp_db_path)

        # 有効なキャッシュのみ挿入
        with sqlite3.connect(temp_db_path) as conn:
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key', '{"test": "valid"}', datetime.now() + timedelta(hours=1)))
            conn.commit()

        deleted_count = cleanup_expired_cache(temp_db_path)

        assert deleted_count == 0

    def test_get_cache_stats_success(self, temp_db_path):
        """キャッシュ統計取得成功テスト"""
        init_database(temp_db_path)

        # テストデータを挿入
        with sqlite3.connect(temp_db_path) as conn:
            # 有効なキャッシュ
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key1', '{"test": "valid1"}', datetime.now() + timedelta(hours=1)))

            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key2', '{"test": "valid2"}', datetime.now() + timedelta(hours=2)))

            # 期限切れキャッシュ
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('expired_key', '{"test": "expired"}', datetime.now() - timedelta(hours=1)))

            conn.commit()

        stats = get_cache_stats(temp_db_path)

        assert stats['total_records'] == 3
        assert stats['valid_records'] == 2
        assert stats['expired_records'] == 1
        assert stats['database_size'] > 0

    def test_get_cache_stats_empty_database(self, temp_db_path):
        """空データベースの統計取得テスト"""
        init_database(temp_db_path)

        stats = get_cache_stats(temp_db_path)

        assert stats['total_records'] == 0
        assert stats['valid_records'] == 0
        assert stats['expired_records'] == 0
        assert stats['database_size'] > 0  # ファイルサイズは0より大きい

    def test_cache_service_database_integration(self, temp_db_path):
        """CacheServiceとデータベースの統合テスト"""
        init_database(temp_db_path)
        cache_service = CacheService(db_path=temp_db_path)

        # データ保存
        test_data = {'message': 'Hello Integration', 'number': 42}
        cache_key = cache_service.generate_cache_key('integration_test', param='value')

        result = cache_service.set_cached_data(cache_key, test_data, ttl=300)
        assert result is True

        # データベースに直接アクセスして確認
        with sqlite3.connect(temp_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM cache WHERE cache_key = ?", (cache_key,))
            row = cursor.fetchone()

            assert row is not None
            assert row['cache_key'] == cache_key
            assert '"message": "Hello Integration"' in row['data']

        # CacheService経由でデータ取得
        retrieved_data = cache_service.get_cached_data(cache_key)
        assert retrieved_data == test_data

    def test_database_transaction_rollback(self, temp_db_path):
        """データベーストランザクションロールバックテスト"""
        init_database(temp_db_path)

        try:
            with get_db_connection(temp_db_path) as conn:
                # 正常なデータ挿入
                conn.execute("""
                    INSERT INTO cache (cache_key, data, expires_at)
                    VALUES (?, ?, ?)
                """, ('test_key', '{"test": "data"}', datetime.now() + timedelta(hours=1)))

                # 意図的なエラーを発生させる（無効なSQL）
                conn.execute("INVALID SQL STATEMENT")

        except sqlite3.Error:
            # エラーが発生することを期待
            pass

        # トランザクションがロールバックされていることを確認
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            count = cursor.fetchone()[0]
            assert count == 0

    def test_database_concurrent_access_simulation(self, temp_db_path):
        """データベース同時アクセスシミュレーションテスト"""
        init_database(temp_db_path)

        # 複数のCacheServiceインスタンスで同じデータベースにアクセス
        cache_service1 = CacheService(db_path=temp_db_path)
        cache_service2 = CacheService(db_path=temp_db_path)

        # 異なるキーでデータを保存
        key1 = cache_service1.generate_cache_key('test1', param='value1')
        key2 = cache_service2.generate_cache_key('test2', param='value2')

        data1 = {'service': 1, 'data': 'test1'}
        data2 = {'service': 2, 'data': 'test2'}

        result1 = cache_service1.set_cached_data(key1, data1)
        result2 = cache_service2.set_cached_data(key2, data2)

        assert result1 is True
        assert result2 is True

        # 両方のデータが正しく保存されていることを確認
        retrieved_data1 = cache_service1.get_cached_data(key1)
        retrieved_data2 = cache_service2.get_cached_data(key2)

        assert retrieved_data1 == data1
        assert retrieved_data2 == data2

    def test_database_file_permissions(self, temp_db_path):
        """データベースファイル権限テスト"""
        init_database(temp_db_path)

        # ファイルが存在し、読み書き可能であることを確認
        assert os.path.exists(temp_db_path)
        assert os.access(temp_db_path, os.R_OK)
        assert os.access(temp_db_path, os.W_OK)

        # ファイルサイズが0より大きいことを確認
        file_size = os.path.getsize(temp_db_path)
        assert file_size > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
