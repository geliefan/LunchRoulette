#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RestaurantService縺ｮ蜊倅ｽ薙ユ繧ｹ繝・
Hot Pepper Gourmet API縺九ｉ繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ繧貞叙蠕励☆繧区ｩ溯・繧偵ユ繧ｹ繝・
"""

import pytest
import os
from unittest.mock import Mock, patch
from restaurant_service import RestaurantService
from cache_service import CacheService


class TestRestaurantService:
    """RestaurantService繧ｯ繝ｩ繧ｹ縺ｮ蜊倅ｽ薙ユ繧ｹ繝・""

    @pytest.fixture
    def mock_cache_service(self):
        """繝｢繝・けCacheService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ"""
        mock_cache = Mock(spec=CacheService)
        mock_cache.generate_cache_key.return_value = "restaurant_test_key"
        mock_cache.get_cached_data.return_value = None
        mock_cache.set_cached_data.return_value = True
        return mock_cache

    @pytest.fixture
    def restaurant_service(self, mock_cache_service):
        """繝・せ繝育畑RestaurantService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ"""
        return RestaurantService(api_key="test_api_key", cache_service=mock_cache_service)

    @pytest.fixture
    def restaurant_service_no_key(self, mock_cache_service):
        """API繧ｭ繝ｼ縺ｪ縺励・RestaurantService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ"""
        return RestaurantService(api_key=None, cache_service=mock_cache_service)

    def test_init_with_api_key(self, mock_cache_service):
        """API繧ｭ繝ｼ縺ゅｊ縺ｮ蛻晄悄蛹悶ユ繧ｹ繝・""
        service = RestaurantService(api_key="test_key", cache_service=mock_cache_service)
        assert service.api_key == "test_key"
        assert service.api_base_url == "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
        assert service.timeout == 10
        assert service.cache_service is not None

    def test_init_without_api_key(self, mock_cache_service):
        """API繧ｭ繝ｼ縺ｪ縺励・蛻晄悄蛹悶ユ繧ｹ繝・""
        with patch.dict(os.environ, {}, clear=True):
            service = RestaurantService(api_key=None, cache_service=mock_cache_service)
            assert service.api_key is None

    def test_budget_codes_constant(self):
        """莠育ｮ励さ繝ｼ繝牙ｮ壽焚繝・せ繝・""
        codes = RestaurantService.BUDGET_CODES
        assert codes['B009'] == 500
        assert codes['B010'] == 1000
        assert codes['B011'] == 1500
        assert codes['B001'] == 2000

    def test_lunch_budget_limit(self):
        """繝ｩ繝ｳ繝∽ｺ育ｮ怜宛髯仙ｮ壽焚繝・せ繝・""
        assert RestaurantService.LUNCH_BUDGET_LIMIT == 1200

    def test_filter_by_budget_success(self, restaurant_service):
        """莠育ｮ励ヵ繧｣繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ謌仙粥繝・せ繝・""
        restaurants = [
            {'id': '1', 'name': '繝ｬ繧ｹ繝医Λ繝ｳ1', 'budget_average': 800},
            {'id': '2', 'name': '繝ｬ繧ｹ繝医Λ繝ｳ2', 'budget_average': 1500},
            {'id': '3', 'name': '繝ｬ繧ｹ繝医Λ繝ｳ3', 'budget_average': 1000},
            {'id': '4', 'name': '繝ｬ繧ｹ繝医Λ繝ｳ4', 'budget_average': 2000}
        ]

        result = restaurant_service.filter_by_budget(restaurants, max_budget=1200)

        # 莠育ｮ・200蜀・ｻ･荳九・繝ｬ繧ｹ繝医Λ繝ｳ縺ｮ縺ｿ縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
        assert len(result) == 2
        assert result[0]['id'] == '1'
        assert result[1]['id'] == '3'

    def test_filter_by_budget_default_limit(self, restaurant_service):
        """莠育ｮ励ヵ繧｣繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ・医ョ繝輔か繝ｫ繝亥宛髯撰ｼ峨ユ繧ｹ繝・""
        restaurants = [
            {'id': '1', 'name': '繝ｬ繧ｹ繝医Λ繝ｳ1', 'budget_average': 800},
            {'id': '2', 'name': '繝ｬ繧ｹ繝医Λ繝ｳ2', 'budget_average': 1500}
        ]

        result = restaurant_service.filter_by_budget(restaurants)

        # 繝・ヵ繧ｩ繝ｫ繝亥宛髯撰ｼ・200蜀・ｼ峨′驕ｩ逕ｨ縺輔ｌ繧九％縺ｨ繧堤｢ｺ隱・
        assert len(result) == 1
        assert result[0]['id'] == '1'

    def test_convert_radius_to_range_code(self, restaurant_service):
        """蜊雁ｾ・°繧臥ｯ・峇繧ｳ繝ｼ繝牙､画鋤繝・せ繝・""
        assert restaurant_service._convert_radius_to_range_code(0.2) == 1  # 300m
        assert restaurant_service._convert_radius_to_range_code(0.4) == 2  # 500m
        assert restaurant_service._convert_radius_to_range_code(0.8) == 3  # 1000m
        assert restaurant_service._convert_radius_to_range_code(1.5) == 4  # 2000m
        assert restaurant_service._convert_radius_to_range_code(5.0) == 5  # 3000m

    def test_parse_budget_info_with_code(self, restaurant_service):
        """莠育ｮ玲ュ蝣ｱ隗｣譫撰ｼ医さ繝ｼ繝峨≠繧奇ｼ峨ユ繧ｹ繝・""
        budget_data = {'code': 'B010', 'name': '501・・000蜀・}

        result = restaurant_service._parse_budget_info(budget_data)

        assert result == 1000

    def test_validate_restaurant_data_valid(self, restaurant_service):
        """繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ繝・・繧ｿ螯･蠖捺ｧ讀懆ｨｼ・域怏蜉ｹ・峨ユ繧ｹ繝・""
        valid_data = {
            'id': 'J001234567',
            'name': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ',
            'lat': 35.6812,
            'lng': 139.7671
        }

        assert restaurant_service.validate_restaurant_data(valid_data) is True

    def test_validate_restaurant_data_missing_fields(self, restaurant_service):
        """繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ繝・・繧ｿ螯･蠖捺ｧ讀懆ｨｼ・医ヵ繧｣繝ｼ繝ｫ繝我ｸ崎ｶｳ・峨ユ繧ｹ繝・""
        invalid_data = {
            'id': 'J001234567',
            'name': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ'
            # lat, lng 縺御ｸ崎ｶｳ
        }

        assert restaurant_service.validate_restaurant_data(invalid_data) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
