#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
繧ｭ繝｣繝・す繝･繧ｷ繧ｹ繝・Β邱丞粋繝・せ繝・
繝・・繧ｿ繝吶・繧ｹ縺ｨCacheService縺ｮ蜍穂ｽ懊ｒ讀懆ｨｼ
"""

from database import init_database, get_cache_stats
from cache_service import CacheService


def main():
    print('=== 繧ｭ繝｣繝・す繝･繧ｷ繧ｹ繝・Β邱丞粋繝・せ繝・===')

    # 繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹悶ユ繧ｹ繝・
    print('1. 繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹悶ユ繧ｹ繝・)
    if init_database():
        print('   笨・繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹匁・蜉・)
    else:
        print('   笨・繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹門､ｱ謨・)
        return

    # CacheService繝・せ繝・
    print('2. CacheService繝・せ繝・)
    cache = CacheService()

    # 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ逕滓・繝・せ繝・
    key = cache.generate_cache_key('test', param1='value1', param2=123)
    print(f'   笨・繧ｭ繝｣繝・す繝･繧ｭ繝ｼ逕滓・: {key}')

    # 繝・・繧ｿ菫晏ｭ倥・蜿門ｾ励ユ繧ｹ繝・
    test_data = {'message': 'Hello Cache', 'number': 42, 'list': [1, 2, 3]}
    if cache.set_cached_data(key, test_data, ttl=300):
        print('   笨・繝・・繧ｿ菫晏ｭ俶・蜉・)

        retrieved_data = cache.get_cached_data(key)
        if retrieved_data and retrieved_data['message'] == 'Hello Cache':
            print('   笨・繝・・繧ｿ蜿門ｾ玲・蜉・)
            print(f'     蜿門ｾ励ョ繝ｼ繧ｿ: {retrieved_data}')
        else:
            print('   笨・繝・・繧ｿ蜿門ｾ怜､ｱ謨・)
    else:
        print('   笨・繝・・繧ｿ菫晏ｭ伜､ｱ謨・)

    # 繧ｭ繝｣繝・す繝･諠・ｱ蜿門ｾ励ユ繧ｹ繝・
    cache_info = cache.get_cache_info(key)
    if cache_info:
        ttl_remaining = cache_info['ttl_remaining']
        print(f'   笨・繧ｭ繝｣繝・す繝･諠・ｱ蜿門ｾ玲・蜉・(TTL谿九ｊ: {ttl_remaining:.1f}遘・')
        print(f'     繝・・繧ｿ繧ｵ繧､繧ｺ: {cache_info["data_size"]} bytes')

    # 隍・焚繧ｭ繝ｼ繝・せ繝・
    print('3. 隍・焚繧ｭ繝ｼ繝・せ繝・)
    keys = []
    for i in range(3):
        test_key = cache.generate_cache_key('multi_test', index=i)
        test_value = {'index': i, 'value': f'test_{i}'}
        cache.set_cached_data(test_key, test_value, ttl=60)
        keys.append(test_key)
        print(f'   笨・繧ｭ繝ｼ{i + 1}菫晏ｭ・ {test_key}')

    # 邨ｱ險域ュ蝣ｱ繝・せ繝・
    print('4. 繝・・繧ｿ繝吶・繧ｹ邨ｱ險域ュ蝣ｱ')
    stats = get_cache_stats()
    print(f'   - 邱上Ξ繧ｳ繝ｼ繝画焚: {stats["total_records"]}')
    print(f'   - 譛牙柑繝ｬ繧ｳ繝ｼ繝画焚: {stats["valid_records"]}')
    print(f'   - 譛滄剞蛻・ｌ繝ｬ繧ｳ繝ｼ繝画焚: {stats["expired_records"]}')
    print(f'   - 繝・・繧ｿ繝吶・繧ｹ繧ｵ繧､繧ｺ: {stats["database_size"]} bytes')

    # 繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・繝・せ繝・
    print('5. 繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・繝・せ繝・)
    expired_count = cache.clear_expired_cache()
    print(f'   笨・譛滄剞蛻・ｌ繧ｭ繝｣繝・す繝･繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・: {expired_count}莉ｶ蜑企勁')

    print('=== 繝・せ繝亥ｮ御ｺ・===')


if __name__ == '__main__':
    main()
