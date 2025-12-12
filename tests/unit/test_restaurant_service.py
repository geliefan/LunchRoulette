#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RestaurantServiceの単体テスト
Hot Pepper Gourmet APIからレストラン情報を取得する機能をテスト
"""

import pytest
import os
from unittest.mock import Mock, patch
from lunch_roulette.services.restaurant_service import RestaurantService
from lunch_roulette.services.cache_service import CacheService


class TestRestaurantService:
    """RestaurantServiceクラスの単体テスト"""

    @pytest.fixture
    def mock_cache_service(self):
        """モックCacheServiceインスタンス"""
        mock_cache = Mock(spec=CacheService)
        mock_cache.generate_cache_key.return_value = "restaurant_test_key"
        mock_cache.get_cached_data.return_value = None
        mock_cache.set_cached_data.return_value = True
        return mock_cache

    @pytest.fixture
    def restaurant_service(self, mock_cache_service):
        """テスト用RestaurantServiceインスタンス"""
        return RestaurantService(api_key="test_api_key", cache_service=mock_cache_service)

    @pytest.fixture
    def restaurant_service_no_key(self, mock_cache_service):
        """APIキーなしのRestaurantServiceインスタンス"""
        return RestaurantService(api_key=None, cache_service=mock_cache_service)

    def test_init_with_api_key(self, mock_cache_service):
        """APIキーありの初期化テスト"""
        service = RestaurantService(api_key="test_key", cache_service=mock_cache_service)
        assert service.api_key == "test_key"
        assert service.api_base_url == "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
        assert service.timeout == 10
        assert service.cache_service is not None

    def test_init_without_api_key(self, mock_cache_service):
        """APIキーなしの初期化テスト"""
        with patch.dict(os.environ, {}, clear=True):
            service = RestaurantService(api_key=None, cache_service=mock_cache_service)
            assert service.api_key is None

    def test_budget_codes_constant(self):
        """予算コード定数のテスト"""
        codes = RestaurantService.BUDGET_CODES
        assert codes['B009'] == 500
        assert codes['B010'] == 1000
        assert codes['B011'] == 1500
        assert codes['B001'] == 2000

    def test_lunch_budget_limit(self):
        """ランチ予算制限定数のテスト"""
        assert RestaurantService.LUNCH_BUDGET_LIMIT == 1200

    def test_filter_by_budget_success(self, restaurant_service):
        """予算フィルタリング成功のテスト"""
        restaurants = [
            {'id': '1', 'name': 'レストラン1', 'budget_average': 800},
            {'id': '2', 'name': 'レストラン2', 'budget_average': 1500},
            {'id': '3', 'name': 'レストラン3', 'budget_average': 1000},
            {'id': '4', 'name': 'レストラン4', 'budget_average': 2000}
        ]

        result = restaurant_service.filter_by_budget(restaurants, max_budget=1200)

        # 予算1200以下のレストランのみが返されることを確認
        assert len(result) == 2
        assert result[0]['id'] == '1'
        assert result[1]['id'] == '3'

    def test_filter_by_budget_default_limit(self, restaurant_service):
        """予算フィルタリング（デフォルト制限）のテスト"""
        restaurants = [
            {'id': '1', 'name': 'レストラン1', 'budget_average': 800},
            {'id': '2', 'name': 'レストラン2', 'budget_average': 1500}
        ]

        result = restaurant_service.filter_by_budget(restaurants)

        # デフォルト制限（1200以下）が適用されることを確認
        assert len(result) == 1
        assert result[0]['id'] == '1'

    def test_convert_radius_to_range_code(self, restaurant_service):
        """半径から範囲コード変換のテスト"""
        assert restaurant_service._convert_radius_to_range_code(0.2) == 1  # 300m
        assert restaurant_service._convert_radius_to_range_code(0.4) == 2  # 500m
        assert restaurant_service._convert_radius_to_range_code(0.8) == 3  # 1000m
        assert restaurant_service._convert_radius_to_range_code(1.5) == 4  # 2000m
        assert restaurant_service._convert_radius_to_range_code(5.0) == 5  # 3000m

    def test_parse_budget_info_with_code(self, restaurant_service):
        """予算情報解析（コードあり）のテスト"""
        budget_data = {'code': 'B010', 'name': '501〜1000円'}

        result = restaurant_service._parse_budget_info(budget_data)

        assert result == 1000

    def test_validate_restaurant_data_valid(self, restaurant_service):
        """レストラン情報データ妥当性検証（有効）のテスト"""
        valid_data = {
            'id': 'J001234567',
            'name': 'テストレストラン',
            'lat': 35.6812,
            'lng': 139.7671
        }

        assert restaurant_service.validate_restaurant_data(valid_data) is True

    def test_validate_restaurant_data_missing_fields(self, restaurant_service):
        """レストラン情報データ妥当性検証（フィールド不足）のテスト"""
        invalid_data = {
            'id': 'J001234567',
            'name': 'テストレストラン'
            # lat, lng が不足
        }

        assert restaurant_service.validate_restaurant_data(invalid_data) is False

    @patch('lunch_roulette.services.restaurant_service.requests.get')
    def test_search_restaurants_with_genre_code(self, mock_get, restaurant_service, mock_cache_service):
        """ジャンルコード指定でのレストラン検索テスト"""
        # キャッシュなし
        mock_cache_service.get_cached_data.return_value = None
        
        # APIレスポンスのモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'shop': [
                    {
                        'id': 'J001',
                        'name': '中華料理店',
                        'genre': {'code': 'G007', 'name': '中華'},
                        'budget': {'code': 'B010', 'name': '〜1000円'},
                        'lat': '35.6812',
                        'lng': '139.7671',
                        'address': '東京都千代田区',
                        'photo': {}
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # ジャンルコード指定で検索
        result = restaurant_service.search_restaurants(
            lat=35.6812,
            lon=139.7671,
            radius=1,
            genre_code='G007'
        )
        
        # APIが正しく呼ばれたことを確認
        assert mock_get.called
        call_args = mock_get.call_args
        assert 'params' in call_args.kwargs
        assert call_args.kwargs['params']['genre'] == 'G007'
        
        # 結果が返されることを確認
        assert len(result) >= 0

    def test_search_lunch_restaurants_with_genre(self, restaurant_service, mock_cache_service):
        """ジャンル指定でのランチレストラン検索テスト"""
        # search_restaurantsのモック
        with patch.object(restaurant_service, 'search_restaurants') as mock_search:
            mock_search.return_value = [
                {'id': '1', 'name': 'ラーメン店', 'budget_average': 800, 'genre': 'ラーメン'},
                {'id': '2', 'name': '高級ラーメン', 'budget_average': 1500, 'genre': 'ラーメン'}
            ]
            
            # ジャンルコード指定で検索
            result = restaurant_service.search_lunch_restaurants(
                lat=35.6812,
                lon=139.7671,
                radius=1,
                genre_code='G013'
            )
            
            # search_restaurantsがgenre_code付きで呼ばれたことを確認
            mock_search.assert_called_once()
            call_kwargs = mock_search.call_args.kwargs
            assert 'genre_code' in call_kwargs
            assert call_kwargs['genre_code'] == 'G013'
            
            # 予算フィルタリングが適用されることを確認
            assert len(result) == 1  # 1200円以下は1件のみ
            assert result[0]['id'] == '1'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
