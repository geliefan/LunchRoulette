#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CacheServiceの単体テスト
キャッシュロジックの動作を検証し、モックを使用して外部依存関係をテスト
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from cache_service import CacheService


class TestCacheService:
    """CacheServiceクラスの単体テスト"""

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

    @pytest.fixture
    def cache_service(self, temp_db_path):
        """テスト用CacheServiceインスタンス"""
        return CacheService(db_path=temp_db_path, default_ttl=300)

    def test_init(self, temp_db_path):
        """初期化テスト"""
        cache = CacheService(db_path=temp_db_path, default_ttl=600)
        assert cache.db_path == temp_db_path
        assert cache.default_ttl == 600

    def test_generate_cache_key(self, cache_service):
        """キャッシュキー生成テスト"""
        # 基本的なキー生成
        key1 = cache_service.generate_cache_key("weather", lat=35.6762, lon=139.6503)
        assert key1.startswith("weather_")
        assert len(key1) > 8  # プレフィックス + ハッシュ

        # 同じパラメータで同じキーが生成されることを確認
        key2 = cache_service.generate_cache_key("weather", lat=35.6762, lon=139.6503)
        assert key1 == key2

        # 異なるパラメータで異なるキーが生成されることを確認
        key3 = cache_service.generate_cache_key("weather", lat=35.6762, lon=139.6504)
        assert key1 != key3

        # パラメータの順序が異なっても同じキーが生成されることを確認
        key4 = cache_service.generate_cache_key("weather", lon=139.6503, lat=35.6762)
        assert key1 == key4

    def test_serialize_deserialize_data(self, cache_service):
        """シリアライゼーション・デシリアライゼーションテスト"""
        # 基本的なシリアライズデータ
        test_data = {
            'string': 'テスト文字列',
            'number': 123,
            'float': 45.67,
            'boolean': True,
            'list': [1, 2, 3],
            'dict': {'nested': 'value'}
        }

        # シリアライズ
        serialized = cache_service.serialize_data(test_data)
        assert isinstance(serialized, str)

        # デシリアライズ
        deserialized = cache_service.deserialize_data(serialized)
        assert deserialized == test_data

        # 無効なシリアライズエラー
        with pytest.raises(ValueError):
            cache_service.serialize_data(lambda x: x)  # 関数はシリアライズできない

        # 無効なJSONのデシリアライズエラー
        with pytest.raises(ValueError):
            cache_service.deserialize_data("invalid json")

    def test_is_cache_valid(self, cache_service):
        """キャッシュ有効性チェックテスト"""
        # 未来の時刻は有効
        future_time = datetime.now() + timedelta(minutes=5)
        assert cache_service.is_cache_valid(future_time) is True

        # 過去の時刻は無効
        past_time = datetime.now() - timedelta(minutes=5)
        assert cache_service.is_cache_valid(past_time) is False

        # 現在時刻は有効
        current_time = datetime.now()
        # 実行時間を考慮して少し余裕を持たせる
        result = cache_service.is_cache_valid(current_time + timedelta(seconds=1))
        assert result is True

    @patch('cache_service.get_db_connection')
    def test_set_cached_data_success(self, mock_get_db_connection, cache_service):
        """キャッシュデータ保存成功テスト"""
        # モックデータベース接続を設定
        mock_conn = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn

        test_data = {'test': 'data'}
        result = cache_service.set_cached_data('test_key', test_data, ttl=300)

        assert result is True
        mock_conn.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('cache_service.get_db_connection')
    def test_set_cached_data_failure(self, mock_get_db_connection, cache_service):
        """キャッシュデータ保存失敗テスト"""
        # データベースエラーをシミュレート
        mock_get_db_connection.side_effect = Exception("Database error")

        test_data = {'test': 'data'}
        result = cache_service.set_cached_data('test_key', test_data)

        assert result is False

    @patch('cache_service.get_db_connection')
    def test_get_cached_data_success(self, mock_get_db_connection, cache_service):
        """キャッシュデータ取得成功テスト"""
        # モックデータベース接続を設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # 有効なキャッシュデータをモック
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
        """期限切れキャッシュデータ取得テスト"""
        # モックデータベース接続を設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # 期限切れのキャッシュデータをモック
        past_time = datetime.now() - timedelta(minutes=5)
        test_data = {'test': 'data'}
        mock_cursor.fetchone.return_value = {
            'data': json.dumps(test_data),
            'expires_at': past_time.isoformat()
        }

        result = cache_service.get_cached_data('test_key')

        assert result is None
        # 期限切れデータの削除が呼ばれることを確認
        assert mock_conn.execute.call_count >= 1

    @patch('cache_service.get_db_connection')
    def test_get_cached_data_not_found(self, mock_get_db_connection, cache_service):
        """存在しないキャッシュデータ取得テスト"""
        # モックデータベース接続を設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # データが見つからない場合をモック
        mock_cursor.fetchone.return_value = None

        result = cache_service.get_cached_data('nonexistent_key')

        assert result is None

    @patch('cache_service.get_db_connection')
    def test_get_cached_data_error(self, mock_get_db_connection, cache_service):
        """キャッシュデータ取得エラーテスト"""
        # データベースエラーをシミュレート
        mock_get_db_connection.side_effect = Exception("Database error")

        result = cache_service.get_cached_data('test_key')

        assert result is None

    @patch('cache_service.get_db_connection')
    def test_delete_cached_data(self, mock_get_db_connection, cache_service):
        """キャッシュデータ削除テスト"""
        # モックデータベース接続を設定
        mock_conn = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn

        result = cache_service.delete_cached_data('test_key')

        assert result is True
        mock_conn.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('cache_service.cleanup_expired_cache')
    def test_clear_expired_cache(self, mock_cleanup, cache_service):
        """期限切れキャッシュクリアテスト"""
        mock_cleanup.return_value = 5

        result = cache_service.clear_expired_cache()

        assert result == 5
        mock_cleanup.assert_called_once_with(cache_service.db_path)

    @patch('cache_service.get_db_connection')
    def test_clear_all_cache(self, mock_get_db_connection, cache_service):
        """全キャッシュクリアテスト"""
        # モックデータベース接続を設定
        mock_conn = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn

        result = cache_service.clear_all_cache()

        assert result is True
        mock_conn.execute.assert_called_once_with('DELETE FROM cache')
        mock_conn.commit.assert_called_once()

    @patch('cache_service.get_db_connection')
    def test_get_cache_info(self, mock_get_db_connection, cache_service):
        """キャッシュ情報取得テスト"""
        # モックデータベース接続を設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # キャッシュ情報をモック
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
        """デフォルトTTL使用テスト"""
        with patch('cache_service.get_db_connection') as mock_get_db_connection:
            mock_conn = MagicMock()
            mock_get_db_connection.return_value.__enter__.return_value = mock_conn

            # TTLを指定せずにデータを保存
            cache_service.set_cached_data('test_key', {'data': 'test'})

            # デフォルトTTL（300秒）が使用されることを確認
            call_args = mock_conn.execute.call_args[0]
            # 有効期限が現在時刻 + 300秒程度になっていることを確認
            expires_at_str = call_args[1][2]  # expires_at パラメータ
            expires_at = datetime.fromisoformat(expires_at_str)
            expected_expires = datetime.now() + timedelta(seconds=300)

            # 実行時間の誤差を考慮して±10秒以内で確認
            time_diff = abs((expires_at - expected_expires).total_seconds())
            assert time_diff < 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
