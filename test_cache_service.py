#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CacheService縺ｮ蜊倅ｽ薙ユ繧ｹ繝・
蜷・Γ繧ｽ繝・ラ縺ｮ蜍穂ｽ懊ｒ讀懆ｨｼ縺励√Δ繝・け繧剃ｽｿ逕ｨ縺励※螟夜Κ萓晏ｭ倬未菫ゅｒ繝・せ繝・
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from cache_service import CacheService


class TestCacheService:
    """CacheService繧ｯ繝ｩ繧ｹ縺ｮ蜊倅ｽ薙ユ繧ｹ繝・""

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

    @pytest.fixture
    def cache_service(self, temp_db_path):
        """繝・せ繝育畑CacheService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ"""
        return CacheService(db_path=temp_db_path, default_ttl=300)

    def test_init(self, temp_db_path):
        """蛻晄悄蛹悶ユ繧ｹ繝・""
        cache = CacheService(db_path=temp_db_path, default_ttl=600)
        assert cache.db_path == temp_db_path
        assert cache.default_ttl == 600

    def test_generate_cache_key(self, cache_service):
        """繧ｭ繝｣繝・す繝･繧ｭ繝ｼ逕滓・繝・せ繝・""
        # 蝓ｺ譛ｬ逧・↑繧ｭ繝ｼ逕滓・
        key1 = cache_service.generate_cache_key("weather", lat=35.6762, lon=139.6503)
        assert key1.startswith("weather_")
        assert len(key1) > 8  # 繝励Ξ繝輔ぅ繝・け繧ｹ + 繝上ャ繧ｷ繝･

        # 蜷後§繝代Λ繝｡繝ｼ繧ｿ縺ｧ蜷後§繧ｭ繝ｼ縺檎函謌舌＆繧後ｋ縺薙→繧堤｢ｺ隱・
        key2 = cache_service.generate_cache_key("weather", lat=35.6762, lon=139.6503)
        assert key1 == key2

        # 逡ｰ縺ｪ繧九ヱ繝ｩ繝｡繝ｼ繧ｿ縺ｧ逡ｰ縺ｪ繧九く繝ｼ縺檎函謌舌＆繧後ｋ縺薙→繧堤｢ｺ隱・
        key3 = cache_service.generate_cache_key("weather", lat=35.6762, lon=139.6504)
        assert key1 != key3

        # 繝代Λ繝｡繝ｼ繧ｿ縺ｮ鬆・ｺ上′逡ｰ縺ｪ縺｣縺ｦ繧ょ酔縺倥く繝ｼ縺檎函謌舌＆繧後ｋ縺薙→繧堤｢ｺ隱・
        key4 = cache_service.generate_cache_key("weather", lon=139.6503, lat=35.6762)
        assert key1 == key4

    def test_serialize_deserialize_data(self, cache_service):
        """繝・・繧ｿ繧ｷ繝ｪ繧｢繝ｩ繧､繧ｼ繝ｼ繧ｷ繝ｧ繝ｳ繝ｻ繝・す繝ｪ繧｢繝ｩ繧､繧ｼ繝ｼ繧ｷ繝ｧ繝ｳ繝・せ繝・""
        # 蝓ｺ譛ｬ逧・↑繝・・繧ｿ蝙・
        test_data = {
            'string': '繝・せ繝域枚蟄怜・',
            'number': 123,
            'float': 45.67,
            'boolean': True,
            'list': [1, 2, 3],
            'dict': {'nested': 'value'}
        }

        # 繧ｷ繝ｪ繧｢繝ｩ繧､繧ｺ
        serialized = cache_service.serialize_data(test_data)
        assert isinstance(serialized, str)

        # 繝・す繝ｪ繧｢繝ｩ繧､繧ｺ
        deserialized = cache_service.deserialize_data(serialized)
        assert deserialized == test_data

        # 辟｡蜉ｹ縺ｪ繝・・繧ｿ縺ｮ繧ｷ繝ｪ繧｢繝ｩ繧､繧ｺ繧ｨ繝ｩ繝ｼ
        with pytest.raises(ValueError):
            cache_service.serialize_data(lambda x: x)  # 髢｢謨ｰ縺ｯ繧ｷ繝ｪ繧｢繝ｩ繧､繧ｺ縺ｧ縺阪↑縺・

        # 辟｡蜉ｹ縺ｪJSON縺ｮ繝・す繝ｪ繧｢繝ｩ繧､繧ｺ繧ｨ繝ｩ繝ｼ
        with pytest.raises(ValueError):
            cache_service.deserialize_data("invalid json")

    def test_is_cache_valid(self, cache_service):
        """繧ｭ繝｣繝・す繝･譛牙柑諤ｧ繝√ぉ繝・け繝・せ繝・""
        # 譛ｪ譚･縺ｮ譎ょ綾・域怏蜉ｹ・・
        future_time = datetime.now() + timedelta(minutes=5)
        assert cache_service.is_cache_valid(future_time) is True

        # 驕主悉縺ｮ譎ょ綾・育┌蜉ｹ・・
        past_time = datetime.now() - timedelta(minutes=5)
        assert cache_service.is_cache_valid(past_time) is False

        # 迴ｾ蝨ｨ譎ょ綾・亥｢・阜蛟､・・
        current_time = datetime.now()
        # 螳溯｡梧凾髢薙ｒ閠・・縺励※蟆代＠菴呵｣輔ｒ謖√◆縺帙ｋ
        result = cache_service.is_cache_valid(current_time + timedelta(seconds=1))
        assert result is True

    @patch('cache_service.get_db_connection')
    def test_set_cached_data_success(self, mock_get_db_connection, cache_service):
        """繧ｭ繝｣繝・す繝･繝・・繧ｿ菫晏ｭ俶・蜉溘ユ繧ｹ繝・""
        # 繝｢繝・け繝・・繧ｿ繝吶・繧ｹ謗･邯壹ｒ險ｭ螳・
        mock_conn = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn

        test_data = {'test': 'data'}
        result = cache_service.set_cached_data('test_key', test_data, ttl=300)

        assert result is True
        mock_conn.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('cache_service.get_db_connection')
    def test_set_cached_data_failure(self, mock_get_db_connection, cache_service):
        """繧ｭ繝｣繝・す繝･繝・・繧ｿ菫晏ｭ伜､ｱ謨励ユ繧ｹ繝・""
        # 繝・・繧ｿ繝吶・繧ｹ繧ｨ繝ｩ繝ｼ繧偵す繝溘Η繝ｬ繝ｼ繝・
        mock_get_db_connection.side_effect = Exception("Database error")

        test_data = {'test': 'data'}
        result = cache_service.set_cached_data('test_key', test_data)

        assert result is False

    @patch('cache_service.get_db_connection')
    def test_get_cached_data_success(self, mock_get_db_connection, cache_service):
        """繧ｭ繝｣繝・す繝･繝・・繧ｿ蜿門ｾ玲・蜉溘ユ繧ｹ繝・""
        # 繝｢繝・け繝・・繧ｿ繝吶・繧ｹ謗･邯壹ｒ險ｭ螳・
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # 譛牙柑縺ｪ繧ｭ繝｣繝・す繝･繝・・繧ｿ繧偵Δ繝・け
        future_time = datetime.now() + timedelta(minutes=5)
        test_data = {'test': 'data'}
        mock_cursor.fetchone.return_value = {
            'data': json.dumps(test_data),
            'expires_at': future_time.isoformat()
        }

        result = cache_service.get_cached_data('test_key')

        assert result == test_data
        mock_conn.execute.assert_called_once()

    @patch('cache_service.get_db_connection')
    def test_get_cached_data_expired(self, mock_get_db_connection, cache_service):
        """譛滄剞蛻・ｌ繧ｭ繝｣繝・す繝･繝・・繧ｿ蜿門ｾ励ユ繧ｹ繝・""
        # 繝｢繝・け繝・・繧ｿ繝吶・繧ｹ謗･邯壹ｒ險ｭ螳・
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # 譛滄剞蛻・ｌ縺ｮ繧ｭ繝｣繝・す繝･繝・・繧ｿ繧偵Δ繝・け
        past_time = datetime.now() - timedelta(minutes=5)
        test_data = {'test': 'data'}
        mock_cursor.fetchone.return_value = {
            'data': json.dumps(test_data),
            'expires_at': past_time.isoformat()
        }

        result = cache_service.get_cached_data('test_key')

        assert result is None
        # 譛滄剞蛻・ｌ繝・・繧ｿ縺ｮ蜑企勁縺悟他縺ｰ繧後ｋ縺薙→繧堤｢ｺ隱・
        assert mock_conn.execute.call_count >= 1

    @patch('cache_service.get_db_connection')
    def test_get_cached_data_not_found(self, mock_get_db_connection, cache_service):
        """蟄伜惠縺励↑縺・く繝｣繝・す繝･繝・・繧ｿ蜿門ｾ励ユ繧ｹ繝・""
        # 繝｢繝・け繝・・繧ｿ繝吶・繧ｹ謗･邯壹ｒ險ｭ螳・
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # 繝・・繧ｿ縺瑚ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷医ｒ繝｢繝・け
        mock_cursor.fetchone.return_value = None

        result = cache_service.get_cached_data('nonexistent_key')

        assert result is None

    @patch('cache_service.get_db_connection')
    def test_get_cached_data_error(self, mock_get_db_connection, cache_service):
        """繧ｭ繝｣繝・す繝･繝・・繧ｿ蜿門ｾ励お繝ｩ繝ｼ繝・せ繝・""
        # 繝・・繧ｿ繝吶・繧ｹ繧ｨ繝ｩ繝ｼ繧偵す繝溘Η繝ｬ繝ｼ繝・
        mock_get_db_connection.side_effect = Exception("Database error")

        result = cache_service.get_cached_data('test_key')

        assert result is None

    @patch('cache_service.get_db_connection')
    def test_delete_cached_data(self, mock_get_db_connection, cache_service):
        """繧ｭ繝｣繝・す繝･繝・・繧ｿ蜑企勁繝・せ繝・""
        # 繝｢繝・け繝・・繧ｿ繝吶・繧ｹ謗･邯壹ｒ險ｭ螳・
        mock_conn = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn

        result = cache_service.delete_cached_data('test_key')

        assert result is True
        mock_conn.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('cache_service.cleanup_expired_cache')
    def test_clear_expired_cache(self, mock_cleanup, cache_service):
        """譛滄剞蛻・ｌ繧ｭ繝｣繝・す繝･繧ｯ繝ｪ繧｢繝・せ繝・""
        mock_cleanup.return_value = 5

        result = cache_service.clear_expired_cache()

        assert result == 5
        mock_cleanup.assert_called_once_with(cache_service.db_path)

    @patch('cache_service.get_db_connection')
    def test_clear_all_cache(self, mock_get_db_connection, cache_service):
        """蜈ｨ繧ｭ繝｣繝・す繝･繧ｯ繝ｪ繧｢繝・せ繝・""
        # 繝｢繝・け繝・・繧ｿ繝吶・繧ｹ謗･邯壹ｒ險ｭ螳・
        mock_conn = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn

        result = cache_service.clear_all_cache()

        assert result is True
        mock_conn.execute.assert_called_once_with('DELETE FROM cache')
        mock_conn.commit.assert_called_once()

    @patch('cache_service.get_db_connection')
    def test_get_cache_info(self, mock_get_db_connection, cache_service):
        """繧ｭ繝｣繝・す繝･諠・ｱ蜿門ｾ励ユ繧ｹ繝・""
        # 繝｢繝・け繝・・繧ｿ繝吶・繧ｹ謗･邯壹ｒ險ｭ螳・
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # 繧ｭ繝｣繝・す繝･諠・ｱ繧偵Δ繝・け
        created_time = datetime.now() - timedelta(minutes=2)
        expires_time = datetime.now() + timedelta(minutes=8)
        mock_cursor.fetchone.return_value = {
            'created_at': created_time.isoformat(),
            'expires_at': expires_time.isoformat(),
            'data_size': 100
        }

        result = cache_service.get_cache_info('test_key')

        assert result is not None
        assert result['key'] == 'test_key'
        assert result['data_size'] == 100
        assert result['is_valid'] is True
        assert result['ttl_remaining'] > 0

    def test_default_ttl_usage(self, cache_service):
        """繝・ヵ繧ｩ繝ｫ繝・TL菴ｿ逕ｨ繝・せ繝・""
        with patch('cache_service.get_db_connection') as mock_get_db_connection:
            mock_conn = MagicMock()
            mock_get_db_connection.return_value.__enter__.return_value = mock_conn

            # TTL繧呈欠螳壹○縺壹↓繝・・繧ｿ繧剃ｿ晏ｭ・
            cache_service.set_cached_data('test_key', {'data': 'test'})

            # 繝・ヵ繧ｩ繝ｫ繝・TL・・00遘抵ｼ峨′菴ｿ逕ｨ縺輔ｌ繧九％縺ｨ繧堤｢ｺ隱・
            call_args = mock_conn.execute.call_args[0]
            # 譛牙柑譛滄剞縺檎樟蝨ｨ譎ょ綾 + 300遘堤ｨ句ｺｦ縺ｫ縺ｪ縺｣縺ｦ縺・ｋ縺薙→繧堤｢ｺ隱・
            expires_at_str = call_args[1][2]  # expires_at 繝代Λ繝｡繝ｼ繧ｿ
            expires_at = datetime.fromisoformat(expires_at_str)
            expected_expires = datetime.now() + timedelta(seconds=300)

            # 螳溯｡梧凾髢薙・隱､蟾ｮ繧定・・縺励※ﾂｱ10遘偵・遽・峇縺ｧ遒ｺ隱・
            time_diff = abs((expires_at - expected_expires).total_seconds())
            assert time_diff < 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
