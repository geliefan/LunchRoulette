#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DistanceCalculatorの単体テスト
ハーバーサイン公式を使用した距離計算機能をテスト
"""

import pytest
from unittest.mock import Mock, patch
from distance_calculator import DistanceCalculator
from error_handler import ErrorHandler


class TestDistanceCalculator:
    """DistanceCalculatorクラスの単体テスト"""

    @pytest.fixture
    def mock_error_handler(self):
        """モックErrorHandlerインスタンス"""
        mock_handler = Mock(spec=ErrorHandler)
        mock_handler.handle_distance_calculation_error.return_value = {
            'message': 'テストエラー',
            'fallback_distance': 0.5
        }
        return mock_handler

    @pytest.fixture
    def distance_calculator(self, mock_error_handler):
        """テスト用DistanceCalculatorインスタンス"""
        return DistanceCalculator(error_handler=mock_error_handler)

    def test_init(self):
        """初期化テスト"""
        calculator = DistanceCalculator()
        assert calculator.EARTH_RADIUS_KM == 6371.0
        assert calculator.error_handler is not None

    def test_calculate_distance_same_point(self, distance_calculator):
        """同一地点間の距離計算テスト"""
        # 東京駅の座標
        lat, lon = 35.6812, 139.7671

        result = distance_calculator.calculate_distance(lat, lon, lat, lon)

        assert result == 0.0

    def test_calculate_distance_known_distance(self, distance_calculator):
        """既知の距離での計算テスト"""
        # 東京駅から新宿駅までの距離：約6.5km
        tokyo_lat, tokyo_lon = 35.6812, 139.7671
        shinjuku_lat, shinjuku_lon = 35.6896, 139.7006

        result = distance_calculator.calculate_distance(
            tokyo_lat, tokyo_lon, shinjuku_lat, shinjuku_lon
        )

        # 実際の距離は約6.5kmなので、±3kmの範囲で確認
        assert 3.0 <= result <= 9.0

    def test_calculate_distance_precision(self, distance_calculator):
        """距離計算精度テスト"""
        # 1度の緯度差は約111km
        lat1, lon1 = 35.0, 139.0
        lat2, lon2 = 36.0, 139.0

        result = distance_calculator.calculate_distance(lat1, lon1, lat2, lon2)

        # 1度の緯度差は約111kmなので、±2kmの範囲で確認
        assert 109.0 <= result <= 113.0

    def test_calculate_distance_invalid_latitude(self, distance_calculator):
        """無効な緯度での距離計算テスト"""
        with pytest.raises(ValueError, match="緯度は-90から90の範囲である必要があります"):
            distance_calculator.calculate_distance(95.0, 139.0, 35.0, 139.0)

        with pytest.raises(ValueError, match="緯度は-90から90の範囲である必要があります"):
            distance_calculator.calculate_distance(-95.0, 139.0, 35.0, 139.0)

    def test_calculate_distance_invalid_longitude(self, distance_calculator):
        """無効な経度での距離計算テスト"""
        with pytest.raises(ValueError, match="経度は-180から180の範囲である必要があります"):
            distance_calculator.calculate_distance(35.0, 185.0, 35.0, 139.0)

        with pytest.raises(ValueError, match="経度は-180から180の範囲である必要があります"):
            distance_calculator.calculate_distance(35.0, -185.0, 35.0, 139.0)

    def test_calculate_distance_invalid_type(self, distance_calculator):
        """無効な型での距離計算テスト"""
        with pytest.raises(ValueError, match="緯度・経度は数値である必要があります"):
            distance_calculator.calculate_distance("invalid", 139.0, 35.0, 139.0)

    def test_calculate_distance_error_handling(self, distance_calculator, mock_error_handler):
        """距離計算エラーハンドリングテスト"""
        # mathモジュールのsin関数でエラーを発生させる
        with patch('math.sin', side_effect=Exception("Math error")):
            result = distance_calculator.calculate_distance(35.0, 139.0, 36.0, 140.0)

            # エラーハンドラーが呼ばれることを確認
            mock_error_handler.handle_distance_calculation_error.assert_called_once()

            # 概算距離が返されることを確認（calculate_approximate_distanceの結果）
            assert isinstance(result, float)
            assert result > 0

    def test_calculate_walking_distance_success(self, distance_calculator):
        """徒歩距離計算成功テスト"""
        # 東京駅から銀座駅までの距離：約2.5km
        tokyo_lat, tokyo_lon = 35.6812, 139.7671
        ginza_lat, ginza_lon = 35.6762, 139.7633

        result = distance_calculator.calculate_walking_distance(
            tokyo_lat, tokyo_lon, ginza_lat, ginza_lon
        )

        # 結果の構造確認
        assert 'distance_km' in result
        assert 'distance_m' in result
        assert 'walking_time_minutes' in result
        assert 'distance_display' in result
        assert 'time_display' in result

        # 値の妥当性確認
        assert result['distance_km'] > 0
        assert result['distance_m'] > 0
        assert result['walking_time_minutes'] > 0
        assert 'm' in result['distance_display'] or 'km' in result['distance_display']
        assert '徒歩' in result['time_display']
        assert '分' in result['time_display']

    def test_calculate_walking_distance_short_distance(self, distance_calculator):
        """短距離の徒歩距離計算テスト"""
        # 非常に近い2点
        lat1, lon1 = 35.6812, 139.7671
        lat2, lon2 = 35.6815, 139.7675  # 約30m程度

        result = distance_calculator.calculate_walking_distance(lat1, lon1, lat2, lon2)

        # 短距離の場合はメートル表示
        assert 'm' in result['distance_display']
        assert result['distance_m'] < 1000
        assert result['walking_time_minutes'] >= 1  # 最低1分

    def test_calculate_walking_distance_long_distance(self, distance_calculator):
        """長距離の徒歩距離計算テスト"""
        # 東京駅から新宿駅まで
        tokyo_lat, tokyo_lon = 35.6812, 139.7671
        shinjuku_lat, shinjuku_lon = 35.6896, 139.7006

        result = distance_calculator.calculate_walking_distance(
            tokyo_lat, tokyo_lon, shinjuku_lat, shinjuku_lon
        )

        # 長距離の場合はキロメートル表示
        assert 'km' in result['distance_display']
        assert result['distance_km'] > 1.0
        assert result['walking_time_minutes'] > 60  # 1時間以上

    def test_calculate_walking_distance_error(self, distance_calculator, mock_error_handler):
        """徒歩距離計算エラーテスト"""
        # calculate_distanceでエラーを発生させる
        with patch.object(distance_calculator, 'calculate_distance', side_effect=Exception("Distance error")):
            result = distance_calculator.calculate_walking_distance(35.0, 139.0, 36.0, 140.0)

            # エラー時はデフォルト値が返されることを確認
            assert result['distance_km'] == 0.5
            assert result['distance_m'] == 500
            assert result['walking_time_minutes'] == 8
            assert result['distance_display'] == "約500m"
            assert result['time_display'] == "徒歩約8分"
            assert 'error_info' in result

    def test_validate_coordinates_valid(self, distance_calculator):
        """座標検証 - 有効な座標テスト"""
        # 有効な座標では例外が発生しないことを確認
        distance_calculator._validate_coordinates(35.6812, 139.7671)
        distance_calculator._validate_coordinates(-90.0, -180.0)
        distance_calculator._validate_coordinates(90.0, 180.0)
        distance_calculator._validate_coordinates(0.0, 0.0)

    def test_validate_coordinates_invalid_latitude(self, distance_calculator):
        """座標検証 - 無効な緯度テスト"""
        with pytest.raises(ValueError, match="緯度は-90から90の範囲である必要があります"):
            distance_calculator._validate_coordinates(91.0, 139.0)

        with pytest.raises(ValueError, match="緯度は-90から90の範囲である必要があります"):
            distance_calculator._validate_coordinates(-91.0, 139.0)

    def test_validate_coordinates_invalid_longitude(self, distance_calculator):
        """座標検証 - 無効な経度テスト"""
        with pytest.raises(ValueError, match="経度は-180から180の範囲である必要があります"):
            distance_calculator._validate_coordinates(35.0, 181.0)

        with pytest.raises(ValueError, match="経度は-180から180の範囲である必要があります"):
            distance_calculator._validate_coordinates(35.0, -181.0)

    def test_validate_coordinates_invalid_type(self, distance_calculator):
        """座標検証 - 無効な型テスト"""
        with pytest.raises(ValueError, match="緯度・経度は数値である必要があります"):
            distance_calculator._validate_coordinates("35.0", 139.0)

        with pytest.raises(ValueError, match="緯度・経度は数値である必要があります"):
            distance_calculator._validate_coordinates(35.0, "139.0")

    def test_calculate_approximate_distance_success(self, distance_calculator):
        """概算距離計算成功テスト"""
        # 東京駅から新宿駅まで
        tokyo_lat, tokyo_lon = 35.6812, 139.7671
        shinjuku_lat, shinjuku_lon = 35.6896, 139.7006

        result = distance_calculator._calculate_approximate_distance(
            tokyo_lat, tokyo_lon, shinjuku_lat, shinjuku_lon
        )

        # 概算距離が妥当な範囲であることを確認
        assert isinstance(result, float)
        assert result > 0
        assert result < 100  # 100km未満であること

    def test_calculate_approximate_distance_same_point(self, distance_calculator):
        """概算距離計算（同一地点）のテスト"""
        lat, lon = 35.6812, 139.7671

        result = distance_calculator._calculate_approximate_distance(lat, lon, lat, lon)

        assert result == 0.0

    def test_calculate_approximate_distance_error_fallback(self, distance_calculator):
        """概算距離計算エラー時フォールバックテスト"""
        # mathモジュールのsqrt関数でエラーを発生させる
        with patch('math.sqrt', side_effect=Exception("Math error")):
            result = distance_calculator._calculate_approximate_distance(35.0, 139.0, 36.0, 140.0)

            # 最終フォールバック値が返されることを確認
            assert result == 0.5

    def test_earth_radius_constant(self, distance_calculator):
        """地球半径定数テスト"""
        assert distance_calculator.EARTH_RADIUS_KM == 6371.0

    def test_walking_speed_calculation(self, distance_calculator):
        """徒歩速度計算テスト"""
        # 1kmの距離での徒歩時間計算
        lat1, lon1 = 35.0, 139.0
        lat2, lon2 = 35.009, 139.0  # 約1km

        result = distance_calculator.calculate_walking_distance(lat1, lon1, lat2, lon2)

        # 1.3kmを時速4kmで歩くと約20分
        expected_time = int(1.3 * 15)  # 15分/km

        # ±5分の誤差を許容
        assert abs(result['walking_time_minutes'] - expected_time) <= 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
