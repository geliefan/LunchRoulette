#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
キャッシュシステム総合テスト
データベースとCacheServiceの動作を検証
"""

from database import init_database, get_cache_stats
from cache_service import CacheService


def main():
    print('=== キャッシュシステム総合テスト ===')

    # データベース初期化テスト
    print('1. データベース初期化テスト')
    if init_database():
        print('   ✅ データベース初期化成功')
    else:
        print('   ❌ データベース初期化失敗')
        return

    # CacheServiceテスト
    print('2. CacheServiceテスト')
    cache = CacheService()

    # キャッシュキー生成テスト
    key = cache.generate_cache_key('test', param1='value1', param2=123)
    print(f'   ✅ キャッシュキー生成: {key}')

    # データ保存と取得テスト
    test_data = {'message': 'Hello Cache', 'number': 42, 'list': [1, 2, 3]}
    if cache.set_cached_data(key, test_data, ttl=300):
        print('   ✅ データ保存成功')

        retrieved_data = cache.get_cached_data(key)
        if retrieved_data and retrieved_data['message'] == 'Hello Cache':
            print('   ✅ データ取得成功')
            print(f'     取得データ: {retrieved_data}')
        else:
            print('   ❌ データ取得失敗')
    else:
        print('   ❌ データ保存失敗')

    # キャッシュ情報取得テスト
    cache_info = cache.get_cache_info(key)
    if cache_info:
        ttl_remaining = cache_info['ttl_remaining']
        print(f'   ✅ キャッシュ情報取得成功 (TTL残り: {ttl_remaining:.1f}秒)')
        print(f'     データサイズ: {cache_info["data_size"]} bytes')

    # 複数キー操作テスト
    print('3. 複数キー操作テスト')
    keys = []
    for i in range(3):
        test_key = cache.generate_cache_key('multi_test', index=i)
        test_value = {'index': i, 'value': f'test_{i}'}
        cache.set_cached_data(test_key, test_value, ttl=60)
        keys.append(test_key)
        print(f'   ✅ キー{i + 1}保存: {test_key}')

    # 統計情報テスト
    print('4. データベース統計情報')
    stats = get_cache_stats()
    print(f'   - 総レコード数: {stats["total_records"]}')
    print(f'   - 有効レコード数: {stats["valid_records"]}')
    print(f'   - 期限切れレコード数: {stats["expired_records"]}')
    print(f'   - データベースサイズ: {stats["database_size"]} bytes')

    # クリーンアップテスト
    print('5. クリーンアップテスト')
    expired_count = cache.clear_expired_cache()
    print(f'   ✅ 期限切れキャッシュクリーンアップ: {expired_count}件削除')

    print('=== テスト完了 ===')


if __name__ == '__main__':
    main()
