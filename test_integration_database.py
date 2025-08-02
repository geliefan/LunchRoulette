#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
繝・・繧ｿ繝吶・繧ｹ謫堺ｽ懊・邨ｱ蜷医ユ繧ｹ繝・
螳滄圀縺ｮSQLite繝・・繧ｿ繝吶・繧ｹ縺ｨ縺ｮ邨ｱ蜷医ｒ繝・せ繝・
"""

import pytest
import tempfile
import os
import sqlite3
from datetime import datetime, timedelta
from database import (
    init_database, get_db_connection, cleanup_expired_cache,
    get_cache_stats
)
from cache_service import CacheService


class TestDatabaseIntegration:
    """繝・・繧ｿ繝吶・繧ｹ謫堺ｽ懊・邨ｱ蜷医ユ繧ｹ繝・""

    @pytest.fixture
    def temp_db_path(self):
        """繝・せ繝育畑縺ｮ荳譎ゅョ繝ｼ繧ｿ繝吶・繧ｹ繝輔ぃ繧､繝ｫ繝代せ"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            temp_path = temp_file.name
        yield temp_path
        # 繝・せ繝亥ｾ後↓繝輔ぃ繧､繝ｫ繧貞炎髯､・・indows縺ｧ縺ｮ讓ｩ髯舌お繝ｩ繝ｼ蟇ｾ遲厄ｼ・
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        except (PermissionError, OSError):
            # Windows迺ｰ蠅・〒繝輔ぃ繧､繝ｫ縺御ｽｿ逕ｨ荳ｭ縺ｮ蝣ｴ蜷医・辟｡隕・
            pass

    def test_init_database_success(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹匁・蜉溘ユ繧ｹ繝・""
        result = init_database(temp_db_path)

        assert result is True
        assert os.path.exists(temp_db_path)

        # 繝・・繝悶Ν縺御ｽ懈・縺輔ｌ縺ｦ縺・ｋ縺薙→繧堤｢ｺ隱・
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='cache'
            """)
            table_exists = cursor.fetchone() is not None
            assert table_exists is True

    def test_init_database_existing_file(self, temp_db_path):
        """譌｢蟄倥ョ繝ｼ繧ｿ繝吶・繧ｹ繝輔ぃ繧､繝ｫ縺ｮ蛻晄悄蛹悶ユ繧ｹ繝・""
        # 譛蛻昴・蛻晄悄蛹・
        init_database(temp_db_path)

        # 譌｢蟄倥ヵ繧｡繧､繝ｫ縺ｫ蟇ｾ縺吶ｋ蜀榊・譛溷喧
        result = init_database(temp_db_path)

        assert result is True
        assert os.path.exists(temp_db_path)

    def test_get_db_connection_success(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ謗･邯壼叙蠕玲・蜉溘ユ繧ｹ繝・""
        init_database(temp_db_path)

        with get_db_connection(temp_db_path) as conn:
            assert conn is not None

            # 蝓ｺ譛ｬ逧・↑繧ｯ繧ｨ繝ｪ螳溯｡後ユ繧ｹ繝・
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            count = cursor.fetchone()[0]
            assert count == 0

    def test_get_db_connection_row_factory(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ謗･邯壹・Row Factory繝・せ繝・""
        init_database(temp_db_path)

        with get_db_connection(temp_db_path) as conn:
            # 繝・せ繝医ョ繝ｼ繧ｿ繧呈諺蜈･
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('test_key', '{"test": "data"}', datetime.now() + timedelta(hours=1)))
            conn.commit()

            # Row Factory縺瑚ｨｭ螳壹＆繧後※縺・ｋ縺薙→繧堤｢ｺ隱・
            cursor = conn.execute("SELECT cache_key, data FROM cache WHERE cache_key = ?", ('test_key',))
            row = cursor.fetchone()

            # 霎樊嶌蠖｢蠑上〒繧｢繧ｯ繧ｻ繧ｹ縺ｧ縺阪ｋ縺薙→繧堤｢ｺ隱・
            assert row['cache_key'] == 'test_key'
            assert row['data'] == '{"test": "data"}'

    def test_cache_table_structure(self, temp_db_path):
        """繧ｭ繝｣繝・す繝･繝・・繝悶Ν讒矩遒ｺ隱阪ユ繧ｹ繝・""
        init_database(temp_db_path)

        # 繝・・繝悶Ν讒矩繧堤｢ｺ隱・
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
        """譛滄剞蛻・ｌ繧ｭ繝｣繝・す繝･繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・謌仙粥繝・せ繝・""
        init_database(temp_db_path)

        # 繝・せ繝医ョ繝ｼ繧ｿ繧呈諺蜈･・域怏蜉ｹ繝ｻ譛滄剞蛻・ｌ豺ｷ蝨ｨ・・
        with sqlite3.connect(temp_db_path) as conn:
            # 譛牙柑縺ｪ繧ｭ繝｣繝・す繝･
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key', '{"test": "valid"}', datetime.now() + timedelta(hours=1)))

            # 譛滄剞蛻・ｌ繧ｭ繝｣繝・す繝･
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('expired_key1', '{"test": "expired1"}', datetime.now() - timedelta(hours=1)))

            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('expired_key2', '{"test": "expired2"}', datetime.now() - timedelta(minutes=30)))

            conn.commit()

        # 繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・螳溯｡・
        deleted_count = cleanup_expired_cache(temp_db_path)

        assert deleted_count == 2

        # 譛牙柑縺ｪ繧ｭ繝｣繝・す繝･縺ｮ縺ｿ谿九▲縺ｦ縺・ｋ縺薙→繧堤｢ｺ隱・
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            remaining_count = cursor.fetchone()[0]
            assert remaining_count == 1

            cursor = conn.execute("SELECT cache_key FROM cache")
            remaining_key = cursor.fetchone()[0]
            assert remaining_key == 'valid_key'

    def test_cleanup_expired_cache_no_expired(self, temp_db_path):
        """譛滄剞蛻・ｌ繧ｭ繝｣繝・す繝･縺ｪ縺励・繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・繝・せ繝・""
        init_database(temp_db_path)

        # 譛牙柑縺ｪ繧ｭ繝｣繝・す繝･縺ｮ縺ｿ謖ｿ蜈･
        with sqlite3.connect(temp_db_path) as conn:
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key', '{"test": "valid"}', datetime.now() + timedelta(hours=1)))
            conn.commit()

        deleted_count = cleanup_expired_cache(temp_db_path)

        assert deleted_count == 0

    def test_get_cache_stats_success(self, temp_db_path):
        """繧ｭ繝｣繝・す繝･邨ｱ險亥叙蠕玲・蜉溘ユ繧ｹ繝・""
        init_database(temp_db_path)

        # 繝・せ繝医ョ繝ｼ繧ｿ繧呈諺蜈･
        with sqlite3.connect(temp_db_path) as conn:
            # 譛牙柑縺ｪ繧ｭ繝｣繝・す繝･
            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key1', '{"test": "valid1"}', datetime.now() + timedelta(hours=1)))

            conn.execute("""
                INSERT INTO cache (cache_key, data, expires_at)
                VALUES (?, ?, ?)
            """, ('valid_key2', '{"test": "valid2"}', datetime.now() + timedelta(hours=2)))

            # 譛滄剞蛻・ｌ繧ｭ繝｣繝・す繝･
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
        """遨ｺ繝・・繧ｿ繝吶・繧ｹ縺ｮ邨ｱ險亥叙蠕励ユ繧ｹ繝・""
        init_database(temp_db_path)

        stats = get_cache_stats(temp_db_path)

        assert stats['total_records'] == 0
        assert stats['valid_records'] == 0
        assert stats['expired_records'] == 0
        assert stats['database_size'] > 0  # 繝輔ぃ繧､繝ｫ繧ｵ繧､繧ｺ縺ｯ0繧医ｊ螟ｧ縺阪＞

    def test_cache_service_database_integration(self, temp_db_path):
        """CacheService縺ｨ繝・・繧ｿ繝吶・繧ｹ縺ｮ邨ｱ蜷医ユ繧ｹ繝・""
        init_database(temp_db_path)
        cache_service = CacheService(db_path=temp_db_path)

        # 繝・・繧ｿ菫晏ｭ・
        test_data = {'message': 'Hello Integration', 'number': 42}
        cache_key = cache_service.generate_cache_key('integration_test', param='value')

        result = cache_service.set_cached_data(cache_key, test_data, ttl=300)
        assert result is True

        # 繝・・繧ｿ繝吶・繧ｹ縺ｫ逶ｴ謗･繧｢繧ｯ繧ｻ繧ｹ縺励※遒ｺ隱・
        with sqlite3.connect(temp_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM cache WHERE cache_key = ?", (cache_key,))
            row = cursor.fetchone()

            assert row is not None
            assert row['cache_key'] == cache_key
            assert '"message": "Hello Integration"' in row['data']

        # CacheService邨檎罰縺ｧ繝・・繧ｿ蜿門ｾ・
        retrieved_data = cache_service.get_cached_data(cache_key)
        assert retrieved_data == test_data

    def test_database_transaction_rollback(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ繝医Λ繝ｳ繧ｶ繧ｯ繧ｷ繝ｧ繝ｳ繝ｭ繝ｼ繝ｫ繝舌ャ繧ｯ繝・せ繝・""
        init_database(temp_db_path)

        try:
            with get_db_connection(temp_db_path) as conn:
                # 豁｣蟶ｸ縺ｪ繝・・繧ｿ謖ｿ蜈･
                conn.execute("""
                    INSERT INTO cache (cache_key, data, expires_at)
                    VALUES (?, ?, ?)
                """, ('test_key', '{"test": "data"}', datetime.now() + timedelta(hours=1)))

                # 諢丞峙逧・↓繧ｨ繝ｩ繝ｼ繧堤匱逕溘＆縺帙ｋ・育┌蜉ｹ縺ｪSQL・・
                conn.execute("INVALID SQL STATEMENT")

        except sqlite3.Error:
            # 繧ｨ繝ｩ繝ｼ縺檎匱逕溘☆繧九％縺ｨ繧呈悄蠕・
            pass

        # 繝医Λ繝ｳ繧ｶ繧ｯ繧ｷ繝ｧ繝ｳ縺後Ο繝ｼ繝ｫ繝舌ャ繧ｯ縺輔ｌ縺ｦ縺・ｋ縺薙→繧堤｢ｺ隱・
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            count = cursor.fetchone()[0]
            assert count == 0

    def test_database_concurrent_access_simulation(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ蜷梧凾繧｢繧ｯ繧ｻ繧ｹ繧ｷ繝溘Η繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ繝・せ繝・""
        init_database(temp_db_path)

        # 隍・焚縺ｮCacheService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ縺ｧ蜷後§繝・・繧ｿ繝吶・繧ｹ縺ｫ繧｢繧ｯ繧ｻ繧ｹ
        cache_service1 = CacheService(db_path=temp_db_path)
        cache_service2 = CacheService(db_path=temp_db_path)

        # 逡ｰ縺ｪ繧九く繝ｼ縺ｧ繝・・繧ｿ繧剃ｿ晏ｭ・
        key1 = cache_service1.generate_cache_key('test1', param='value1')
        key2 = cache_service2.generate_cache_key('test2', param='value2')

        data1 = {'service': 1, 'data': 'test1'}
        data2 = {'service': 2, 'data': 'test2'}

        result1 = cache_service1.set_cached_data(key1, data1)
        result2 = cache_service2.set_cached_data(key2, data2)

        assert result1 is True
        assert result2 is True

        # 荳｡譁ｹ縺ｮ繝・・繧ｿ縺梧ｭ｣縺励￥菫晏ｭ倥＆繧後※縺・ｋ縺薙→繧堤｢ｺ隱・
        retrieved_data1 = cache_service1.get_cached_data(key1)
        retrieved_data2 = cache_service2.get_cached_data(key2)

        assert retrieved_data1 == data1
        assert retrieved_data2 == data2

    def test_database_file_permissions(self, temp_db_path):
        """繝・・繧ｿ繝吶・繧ｹ繝輔ぃ繧､繝ｫ讓ｩ髯舌ユ繧ｹ繝・""
        init_database(temp_db_path)

        # 繝輔ぃ繧､繝ｫ縺悟ｭ伜惠縺励∬ｪｭ縺ｿ譖ｸ縺榊庄閭ｽ縺ｧ縺ゅｋ縺薙→繧堤｢ｺ隱・
        assert os.path.exists(temp_db_path)
        assert os.access(temp_db_path, os.R_OK)
        assert os.access(temp_db_path, os.W_OK)

        # 繝輔ぃ繧､繝ｫ繧ｵ繧､繧ｺ縺・繧医ｊ螟ｧ縺阪＞縺薙→繧堤｢ｺ隱・
        file_size = os.path.getsize(temp_db_path)
        assert file_size > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
