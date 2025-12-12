#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
検索条件機能のユニットテスト

このテストファイルの対象:
1. RestaurantService.walking_time_to_range() - 徒歩時間変換
2. RestaurantService.search_restaurants() - 新しいパラメータの動作確認
3. /roulette エンドポイント - 検索条件パラメータの受け入れ
"""

import pytest
from unittest.mock import MagicMock, patch
from src.lunch_roulette.services.restaurant_service import RestaurantService
from src.lunch_roulette.services.cache_service import CacheService


class TestWalkingTimeToRange:
    """walking_time_to_range メソッドのテスト"""

    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        # モックキャッシュサービスを作成
        self.cache_service = MagicMock(spec=CacheService)
        self.restaurant_service = RestaurantService(
            api_key='test_api_key',
            cache_service=self.cache_service
        )

    def test_walking_time_5min_returns_range_2(self):
        """徒歩5分以内はrange 2（500m）を返す"""
        assert self.restaurant_service.walking_time_to_range(5) == 2
        assert self.restaurant_service.walking_time_to_range(3) == 2
        assert self.restaurant_service.walking_time_to_range(1) == 2

    def test_walking_time_10min_returns_range_3(self):
        """徒歩10分以内はrange 3（1000m）を返す"""
        assert self.restaurant_service.walking_time_to_range(10) == 3
        assert self.restaurant_service.walking_time_to_range(8) == 3
        assert self.restaurant_service.walking_time_to_range(6) == 3

    def test_walking_time_20min_returns_range_4(self):
        """徒歩20分以内はrange 4（2000m）を返す"""
        assert self.restaurant_service.walking_time_to_range(20) == 4
        assert self.restaurant_service.walking_time_to_range(15) == 4
        assert self.restaurant_service.walking_time_to_range(11) == 4

    def test_walking_time_over_20min_returns_range_5(self):
        """徒歩20分超はrange 5（3000m）を返す"""
        assert self.restaurant_service.walking_time_to_range(30) == 5
        assert self.restaurant_service.walking_time_to_range(25) == 5
        assert self.restaurant_service.walking_time_to_range(21) == 5

    def test_walking_time_boundary_values(self):
        """境界値のテスト"""
        # ちょうど境界値
        assert self.restaurant_service.walking_time_to_range(5) == 2
        assert self.restaurant_service.walking_time_to_range(10) == 3
        assert self.restaurant_service.walking_time_to_range(20) == 4


class TestSearchRestaurantsWithConditions:
    """search_restaurants メソッドの新パラメータテスト"""

    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        self.cache_service = MagicMock(spec=CacheService)
        self.restaurant_service = RestaurantService(
            api_key='test_api_key',
            cache_service=self.cache_service
        )

    @patch('src.lunch_roulette.services.restaurant_service.requests.get')
    def test_search_with_budget_code(self, mock_get):
        """予算コード指定時にAPIパラメータに含まれることを確認"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'results': {'shop': []}
        }
        mock_get.return_value = mock_response

        # キャッシュがないことを設定
        self.cache_service.get_cached_data.return_value = None

        # 予算コード指定で検索
        self.restaurant_service.search_restaurants(
            lat=35.6812,
            lon=139.7671,
            radius=1,
            budget_code='B010'
        )

        # requests.get が呼ばれたか確認
        assert mock_get.called
        call_args = mock_get.call_args
        params = call_args[1]['params']

        # budget パラメータが含まれているか確認
        assert 'budget' in params
        assert params['budget'] == 'B010'

    @patch('src.lunch_roulette.services.restaurant_service.requests.get')
    def test_search_with_lunch_filter(self, mock_get):
        """ランチフィルタ指定時にAPIパラメータに含まれることを確認"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'results': {'shop': []}
        }
        mock_get.return_value = mock_response

        # キャッシュがないことを設定
        self.cache_service.get_cached_data.return_value = None

        # ランチフィルタ指定で検索
        self.restaurant_service.search_restaurants(
            lat=35.6812,
            lon=139.7671,
            radius=1,
            lunch=1
        )

        # requests.get が呼ばれたか確認
        assert mock_get.called
        call_args = mock_get.call_args
        params = call_args[1]['params']

        # lunch パラメータが含まれているか確認
        assert 'lunch' in params
        assert params['lunch'] == 1

    @patch('src.lunch_roulette.services.restaurant_service.requests.get')
    def test_search_without_optional_params(self, mock_get):
        """オプションパラメータなしでも動作することを確認"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'results': {'shop': []}
        }
        mock_get.return_value = mock_response

        # キャッシュがないことを設定
        self.cache_service.get_cached_data.return_value = None

        # オプションパラメータなしで検索
        self.restaurant_service.search_restaurants(
            lat=35.6812,
            lon=139.7671,
            radius=1
        )

        # requests.get が呼ばれたか確認
        assert mock_get.called
        call_args = mock_get.call_args
        params = call_args[1]['params']

        # budget と lunch パラメータが含まれていないことを確認
        assert 'budget' not in params
        assert 'lunch' not in params
