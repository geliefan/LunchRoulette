#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DistanceCalculator縺ｮ蜊倅ｽ薙ユ繧ｹ繝・
繝上・繝舌・繧ｵ繧､繝ｳ蜈ｬ蠑上ｒ菴ｿ逕ｨ縺励◆霍晞屬險育ｮ玲ｩ溯・繧偵ユ繧ｹ繝・
"""

import pytest
from unittest.mock import Mock, patch
from distance_calculator import DistanceCalculator
from error_handler import ErrorHandler


class TestDistanceCalculator:
    """DistanceCalculator繧ｯ繝ｩ繧ｹ縺ｮ蜊倅ｽ薙ユ繧ｹ繝・""

    @pytest.fixture
    def mock_error_handler(self):
        """繝｢繝・けErrorHandler繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ"""
        mock_handler = Mock(spec=ErrorHandler)
        mock_handler.handle_distance_calculation_error.return_value = {
            'message': '繝・せ繝医お繝ｩ繝ｼ',
            'fallback_distance': 0.5
        }
        return mock_handler

    @pytest.fixture
    def distance_calculator(self, mock_error_handler):
        """繝・せ繝育畑DistanceCalculator繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ"""
        return DistanceCalculator(error_handler=mock_error_handler)

    def test_init(self):
        """蛻晄悄蛹悶ユ繧ｹ繝・""
        calculator = DistanceCalculator()
        assert calculator.EARTH_RADIUS_KM == 6371.0
        assert calculator.error_handler is not None

    def test_calculate_distance_same_point(self, distance_calculator):
        """蜷御ｸ蝨ｰ轤ｹ髢薙・霍晞屬險育ｮ励ユ繧ｹ繝・""
        # 譚ｱ莠ｬ鬧・・蠎ｧ讓・
        lat, lon = 35.6812, 139.7671

        result = distance_calculator.calculate_distance(lat, lon, lat, lon)

        assert result == 0.0

    def test_calculate_distance_known_distance(self, distance_calculator):
        """譌｢遏･縺ｮ霍晞屬縺ｧ縺ｮ險育ｮ励ユ繧ｹ繝・""
        # 譚ｱ莠ｬ鬧・°繧画眠螳ｿ鬧・∪縺ｧ縺ｮ霍晞屬・育ｴ・.5km・・
        tokyo_lat, tokyo_lon = 35.6812, 139.7671
        shinjuku_lat, shinjuku_lon = 35.6896, 139.7006

        result = distance_calculator.calculate_distance(
            tokyo_lat, tokyo_lon, shinjuku_lat, shinjuku_lon
        )

        # 螳滄圀縺ｮ霍晞屬縺ｯ邏・.5km縺ｪ縺ｮ縺ｧ縲・-9km縺ｮ遽・峇縺ｧ遒ｺ隱・
        assert 6.0 <= result <= 9.0

    def test_calculate_distance_precision(self, distance_calculator):
        """霍晞屬險育ｮ礼ｲｾ蠎ｦ繝・せ繝・""
        # 1蠎ｦ縺ｮ邱ｯ蠎ｦ蟾ｮ・育ｴ・11km・・
        lat1, lon1 = 35.0, 139.0
        lat2, lon2 = 36.0, 139.0

        result = distance_calculator.calculate_distance(lat1, lon1, lat2, lon2)

        # 1蠎ｦ縺ｮ邱ｯ蠎ｦ蟾ｮ縺ｯ邏・11km縺ｪ縺ｮ縺ｧ縲・10-112km縺ｮ遽・峇縺ｧ遒ｺ隱・
        assert 110.0 <= result <= 112.0

    def test_calculate_distance_invalid_latitude(self, distance_calculator):
        """辟｡蜉ｹ縺ｪ邱ｯ蠎ｦ縺ｧ縺ｮ霍晞屬險育ｮ励ユ繧ｹ繝・""
        with pytest.raises(ValueError, match="邱ｯ蠎ｦ縺ｯ-90縺九ｉ90縺ｮ遽・峇縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・):
            distance_calculator.calculate_distance(95.0, 139.0, 35.0, 139.0)

        with pytest.raises(ValueError, match="邱ｯ蠎ｦ縺ｯ-90縺九ｉ90縺ｮ遽・峇縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・):
            distance_calculator.calculate_distance(-95.0, 139.0, 35.0, 139.0)

    def test_calculate_distance_invalid_longitude(self, distance_calculator):
        """辟｡蜉ｹ縺ｪ邨悟ｺｦ縺ｧ縺ｮ霍晞屬險育ｮ励ユ繧ｹ繝・""
        with pytest.raises(ValueError, match="邨悟ｺｦ縺ｯ-180縺九ｉ180縺ｮ遽・峇縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・):
            distance_calculator.calculate_distance(35.0, 185.0, 35.0, 139.0)

        with pytest.raises(ValueError, match="邨悟ｺｦ縺ｯ-180縺九ｉ180縺ｮ遽・峇縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・):
            distance_calculator.calculate_distance(35.0, -185.0, 35.0, 139.0)

    def test_calculate_distance_invalid_type(self, distance_calculator):
        """辟｡蜉ｹ縺ｪ蝙九〒縺ｮ霍晞屬險育ｮ励ユ繧ｹ繝・""
        with pytest.raises(ValueError, match="邱ｯ蠎ｦ繝ｻ邨悟ｺｦ縺ｯ謨ｰ蛟､縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・):
            distance_calculator.calculate_distance("invalid", 139.0, 35.0, 139.0)

    def test_calculate_distance_error_handling(self, distance_calculator, mock_error_handler):
        """霍晞屬險育ｮ励お繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        # math繝｢繧ｸ繝･繝ｼ繝ｫ縺ｮsin髢｢謨ｰ縺ｧ繧ｨ繝ｩ繝ｼ繧堤匱逕溘＆縺帙ｋ
        with patch('math.sin', side_effect=Exception("Math error")):
            result = distance_calculator.calculate_distance(35.0, 139.0, 36.0, 140.0)

            # 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ縺悟他縺ｰ繧後ｋ縺薙→繧堤｢ｺ隱・
            mock_error_handler.handle_distance_calculation_error.assert_called_once()

            # 讎らｮ苓ｷ晞屬縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱搾ｼ・calculate_approximate_distance縺ｮ邨先棡・・
            assert isinstance(result, float)
            assert result > 0

    def test_calculate_walking_distance_success(self, distance_calculator):
        """蠕呈ｭｩ霍晞屬險育ｮ玲・蜉溘ユ繧ｹ繝・""
        # 譚ｱ莠ｬ鬧・°繧蛾橿蠎ｧ鬧・∪縺ｧ縺ｮ霍晞屬・育ｴ・km・・
        tokyo_lat, tokyo_lon = 35.6812, 139.7671
        ginza_lat, ginza_lon = 35.6762, 139.7633

        result = distance_calculator.calculate_walking_distance(
            tokyo_lat, tokyo_lon, ginza_lat, ginza_lon
        )

        # 邨先棡縺ｮ讒矩遒ｺ隱・
        assert 'distance_km' in result
        assert 'distance_m' in result
        assert 'walking_time_minutes' in result
        assert 'distance_display' in result
        assert 'time_display' in result

        # 蛟､縺ｮ螯･蠖捺ｧ遒ｺ隱・
        assert result['distance_km'] > 0
        assert result['distance_m'] > 0
        assert result['walking_time_minutes'] > 0
        assert 'm' in result['distance_display'] or 'km' in result['distance_display']
        assert '蠕呈ｭｩ邏・ in result['time_display']
        assert '蛻・ in result['time_display']

    def test_calculate_walking_distance_short_distance(self, distance_calculator):
        """遏ｭ霍晞屬縺ｮ蠕呈ｭｩ霍晞屬險育ｮ励ユ繧ｹ繝・""
        # 髱槫ｸｸ縺ｫ霑代＞2轤ｹ
        lat1, lon1 = 35.6812, 139.7671
        lat2, lon2 = 35.6815, 139.7675  # 邏・0m遞句ｺｦ

        result = distance_calculator.calculate_walking_distance(lat1, lon1, lat2, lon2)

        # 遏ｭ霍晞屬縺ｮ蝣ｴ蜷医・繝｡繝ｼ繝医Ν陦ｨ遉ｺ
        assert 'm' in result['distance_display']
        assert result['distance_m'] < 1000
        assert result['walking_time_minutes'] >= 1  # 譛菴・蛻・

    def test_calculate_walking_distance_long_distance(self, distance_calculator):
        """髟ｷ霍晞屬縺ｮ蠕呈ｭｩ霍晞屬險育ｮ励ユ繧ｹ繝・""
        # 譚ｱ莠ｬ鬧・°繧画眠螳ｿ鬧・∪縺ｧ
        tokyo_lat, tokyo_lon = 35.6812, 139.7671
        shinjuku_lat, shinjuku_lon = 35.6896, 139.7006

        result = distance_calculator.calculate_walking_distance(
            tokyo_lat, tokyo_lon, shinjuku_lat, shinjuku_lon
        )

        # 髟ｷ霍晞屬縺ｮ蝣ｴ蜷医・繧ｭ繝ｭ繝｡繝ｼ繝医Ν陦ｨ遉ｺ
        assert 'km' in result['distance_display']
        assert result['distance_km'] > 1.0
        assert result['walking_time_minutes'] > 60  # 1譎る俣莉･荳・

    def test_calculate_walking_distance_error(self, distance_calculator, mock_error_handler):
        """蠕呈ｭｩ霍晞屬險育ｮ励お繝ｩ繝ｼ繝・せ繝・""
        # calculate_distance縺ｧ繧ｨ繝ｩ繝ｼ繧堤匱逕溘＆縺帙ｋ
        with patch.object(distance_calculator, 'calculate_distance', side_effect=Exception("Distance error")):
            result = distance_calculator.calculate_walking_distance(35.0, 139.0, 36.0, 140.0)

            # 繧ｨ繝ｩ繝ｼ譎ゅ・繝・ヵ繧ｩ繝ｫ繝亥､縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
            assert result['distance_km'] == 0.5
            assert result['distance_m'] == 500
            assert result['walking_time_minutes'] == 8
            assert result['distance_display'] == "邏・00m"
            assert result['time_display'] == "蠕呈ｭｩ邏・蛻・
            assert 'error_info' in result

    def test_validate_coordinates_valid(self, distance_calculator):
        """蠎ｧ讓呎､懆ｨｼ・域怏蜉ｹ・峨ユ繧ｹ繝・""
        # 譛牙柑縺ｪ蠎ｧ讓吶〒縺ｯ萓句､悶′逋ｺ逕溘＠縺ｪ縺・
        distance_calculator._validate_coordinates(35.6812, 139.7671)
        distance_calculator._validate_coordinates(-90.0, -180.0)
        distance_calculator._validate_coordinates(90.0, 180.0)
        distance_calculator._validate_coordinates(0.0, 0.0)

    def test_validate_coordinates_invalid_latitude(self, distance_calculator):
        """蠎ｧ讓呎､懆ｨｼ・育┌蜉ｹ縺ｪ邱ｯ蠎ｦ・峨ユ繧ｹ繝・""
        with pytest.raises(ValueError, match="邱ｯ蠎ｦ縺ｯ-90縺九ｉ90縺ｮ遽・峇縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・):
            distance_calculator._validate_coordinates(91.0, 139.0)

        with pytest.raises(ValueError, match="邱ｯ蠎ｦ縺ｯ-90縺九ｉ90縺ｮ遽・峇縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・):
            distance_calculator._validate_coordinates(-91.0, 139.0)

    def test_validate_coordinates_invalid_longitude(self, distance_calculator):
        """蠎ｧ讓呎､懆ｨｼ・育┌蜉ｹ縺ｪ邨悟ｺｦ・峨ユ繧ｹ繝・""
        with pytest.raises(ValueError, match="邨悟ｺｦ縺ｯ-180縺九ｉ180縺ｮ遽・峇縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・):
            distance_calculator._validate_coordinates(35.0, 181.0)

        with pytest.raises(ValueError, match="邨悟ｺｦ縺ｯ-180縺九ｉ180縺ｮ遽・峇縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・):
            distance_calculator._validate_coordinates(35.0, -181.0)

    def test_validate_coordinates_invalid_type(self, distance_calculator):
        """蠎ｧ讓呎､懆ｨｼ・育┌蜉ｹ縺ｪ蝙具ｼ峨ユ繧ｹ繝・""
        with pytest.raises(ValueError, match="邱ｯ蠎ｦ繝ｻ邨悟ｺｦ縺ｯ謨ｰ蛟､縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・):
            distance_calculator._validate_coordinates("35.0", 139.0)

        with pytest.raises(ValueError, match="邱ｯ蠎ｦ繝ｻ邨悟ｺｦ縺ｯ謨ｰ蛟､縺ｧ縺ゅｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・):
            distance_calculator._validate_coordinates(35.0, "139.0")

    def test_calculate_approximate_distance_success(self, distance_calculator):
        """讎らｮ苓ｷ晞屬險育ｮ玲・蜉溘ユ繧ｹ繝・""
        # 譚ｱ莠ｬ鬧・°繧画眠螳ｿ鬧・∪縺ｧ
        tokyo_lat, tokyo_lon = 35.6812, 139.7671
        shinjuku_lat, shinjuku_lon = 35.6896, 139.7006

        result = distance_calculator._calculate_approximate_distance(
            tokyo_lat, tokyo_lon, shinjuku_lat, shinjuku_lon
        )

        # 讎らｮ苓ｷ晞屬縺悟ｦ･蠖薙↑遽・峇蜀・〒縺ゅｋ縺薙→繧堤｢ｺ隱・
        assert isinstance(result, float)
        assert result > 0
        assert result < 100  # 100km譛ｪ貅・域擲莠ｬ驛ｽ蜀・↑縺ｮ縺ｧ・・

    def test_calculate_approximate_distance_same_point(self, distance_calculator):
        """讎らｮ苓ｷ晞屬險育ｮ暦ｼ亥酔荳蝨ｰ轤ｹ・峨ユ繧ｹ繝・""
        lat, lon = 35.6812, 139.7671

        result = distance_calculator._calculate_approximate_distance(lat, lon, lat, lon)

        assert result == 0.0

    def test_calculate_approximate_distance_error_fallback(self, distance_calculator):
        """讎らｮ苓ｷ晞屬險育ｮ励お繝ｩ繝ｼ譎ゅ・繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繝・せ繝・""
        # math繝｢繧ｸ繝･繝ｼ繝ｫ縺ｮsqrt髢｢謨ｰ縺ｧ繧ｨ繝ｩ繝ｼ繧堤匱逕溘＆縺帙ｋ
        with patch('math.sqrt', side_effect=Exception("Math error")):
            result = distance_calculator._calculate_approximate_distance(35.0, 139.0, 36.0, 140.0)

            # 譛邨ゅヵ繧ｩ繝ｼ繝ｫ繝舌ャ繧ｯ蛟､縺瑚ｿ斐＆繧後ｋ縺薙→繧堤｢ｺ隱・
            assert result == 0.5

    def test_earth_radius_constant(self, distance_calculator):
        """蝨ｰ逅・濠蠕・ｮ壽焚繝・せ繝・""
        assert distance_calculator.EARTH_RADIUS_KM == 6371.0

    def test_walking_speed_calculation(self, distance_calculator):
        """蠕呈ｭｩ騾溷ｺｦ險育ｮ励ユ繧ｹ繝・""
        # 1km縺ｮ霍晞屬縺ｧ縺ｮ蠕呈ｭｩ譎る俣險育ｮ・
        lat1, lon1 = 35.0, 139.0
        lat2, lon2 = 35.009, 139.0  # 邏・km

        result = distance_calculator.calculate_walking_distance(lat1, lon1, lat2, lon2)

        # 1.3km・郁ｿょ屓閠・・・峨ｒ譎る・km縺ｧ豁ｩ縺上→邏・0蛻・
        expected_time = int(1.3 * 15)  # 15蛻・km

        # ﾂｱ5蛻・・隱､蟾ｮ繧定ｨｱ螳ｹ
        assert abs(result['walking_time_minutes'] - expected_time) <= 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
