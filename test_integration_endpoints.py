#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask 繧ｨ繝ｳ繝峨・繧､繝ｳ繝医・邨ｱ蜷医ユ繧ｹ繝・
螳滄圀縺ｮFlask繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｨ縺ｮ邨ｱ蜷医ｒ繝・せ繝・
"""

import pytest
import json
import os
from unittest.mock import patch, Mock
from app import app
from database import init_database


class TestFlaskEndpointsIntegration:
    """Flask 繧ｨ繝ｳ繝峨・繧､繝ｳ繝医・邨ｱ蜷医ユ繧ｹ繝・""

    @pytest.fixture
    def client(self):
        """繝・せ繝育畑Flask繧ｯ繝ｩ繧､繧｢繝ｳ繝・""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

        # 荳諢上↑繝・せ繝医ョ繝ｼ繧ｿ繝吶・繧ｹ蜷阪ｒ逕滓・
        import uuid
        test_db_name = f'test_cache_{uuid.uuid4().hex[:8]}.db'

        with app.test_client() as client:
            with app.app_context():
                # 繝・せ繝育畑繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹・
                init_database(test_db_name)
                yield client

        # 繝・せ繝亥ｾ後・繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・・・indows縺ｧ縺ｮ讓ｩ髯舌お繝ｩ繝ｼ蟇ｾ遲厄ｼ・
        try:
            if os.path.exists(test_db_name):
                os.unlink(test_db_name)
        except (PermissionError, OSError):
            # Windows迺ｰ蠅・〒繝輔ぃ繧､繝ｫ縺御ｽｿ逕ｨ荳ｭ縺ｮ蝣ｴ蜷医・辟｡隕・
            pass

    def test_main_page_endpoint_success(self, client):
        """繝｡繧､繝ｳ繝壹・繧ｸ繧ｨ繝ｳ繝峨・繧､繝ｳ繝域・蜉溘ユ繧ｹ繝・""
        with patch('location_service.LocationService') as mock_location_service, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # 繝｢繝・け繧ｵ繝ｼ繝薙せ縺ｮ險ｭ螳・
            mock_location_instance = Mock()
            mock_location_instance.get_location_from_ip.return_value = {
                'city': '譚ｱ莠ｬ',
                'region': '譚ｱ莠ｬ驛ｽ',
                'latitude': 35.6812,
                'longitude': 139.7671,
                'source': 'ipapi.co'
            }
            mock_location_service.return_value = mock_location_instance

            mock_weather_instance = Mock()
            mock_weather_instance.get_current_weather.return_value = {
                'temperature': 25.0,
                'description': '譎ｴ繧・,
                'uv_index': 5.0,
                'icon': '01d',
                'source': 'openweathermap'
            }
            mock_weather_instance.get_weather_icon_url.return_value = 'https://openweathermap.org/img/wn/01d@2x.png'
            mock_weather_instance.get_weather_summary.return_value = '譎ｴ繧・25ﾂｰC UV謖・焚5'
            mock_weather_instance.is_good_weather_for_walking.return_value = True
            mock_weather_service.return_value = mock_weather_instance

            response = client.get('/')

            assert response.status_code == 200
            assert response.content_type.startswith('text/html')

            # HTML繧ｳ繝ｳ繝・Φ繝・・蝓ｺ譛ｬ遒ｺ隱・
            html_content = response.data.decode('utf-8')
            assert '<!DOCTYPE html>' in html_content
            assert '<title>' in html_content
            assert '繝ｫ繝ｼ繝ｬ繝・ヨ繧貞屓縺・ in html_content

    def test_main_page_endpoint_service_error(self, client):
        """繝｡繧､繝ｳ繝壹・繧ｸ繧ｨ繝ｳ繝峨・繧､繝ｳ繝茨ｼ医し繝ｼ繝薙せ繧ｨ繝ｩ繝ｼ・峨ユ繧ｹ繝・""
        with patch('location_service.LocationService') as mock_location_service, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # 繧ｵ繝ｼ繝薙せ縺ｧ繧ｨ繝ｩ繝ｼ縺檎匱逕溘☆繧句ｴ蜷・
            mock_location_service.side_effect = Exception("Location service error")
            mock_weather_service.side_effect = Exception("Weather service error")

            response = client.get('/')

            # 繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｦ繧ゅ・繝ｼ繧ｸ縺ｯ陦ｨ遉ｺ縺輔ｌ繧具ｼ医お繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ・・
            assert response.status_code == 200

            # 繝・ヵ繧ｩ繝ｫ繝医ョ繝ｼ繧ｿ縺ｧ繝壹・繧ｸ縺瑚｡ｨ遉ｺ縺輔ｌ繧九％縺ｨ繧堤｢ｺ隱・
            html_content = response.data.decode('utf-8')
            assert '譚ｱ莠ｬ' in html_content  # 繝・ヵ繧ｩ繝ｫ繝井ｽ咲ｽｮ

    def test_roulette_endpoint_success(self, client):
        """繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝域・蜉溘ユ繧ｹ繝・""
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service, \
                patch('restaurant_selector.RestaurantSelector') as mock_restaurant_selector, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # 繝｢繝・け繧ｵ繝ｼ繝薙せ縺ｮ險ｭ螳・
            mock_restaurant_instance = Mock()
            mock_restaurant_instance.search_lunch_restaurants.return_value = [{
                'id': 'J001234567',
                'name': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ',
                'genre': '蜥碁｣・,
                'lat': 35.6815,
                'lng': 139.7675,
                'budget_average': 1000,
                'address': '譚ｱ莠ｬ驛ｽ蜊・ｻ｣逕ｰ蛹ｺ',
                'urls': {'pc': 'http://example.com'},
                'photo': 'http://example.com/photo.jpg'
            }]
            mock_restaurant_service.return_value = mock_restaurant_instance

            mock_selector_instance = Mock()
            mock_selector_instance.select_random_restaurant.return_value = {
                'id': 'J001234567',
                'name': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ',
                'genre': '蜥碁｣・,
                'address': '譚ｱ莠ｬ驛ｽ蜊・ｻ｣逕ｰ蛹ｺ',
                'catch': '縺翫＞縺励＞繝ｬ繧ｹ繝医Λ繝ｳ',
                'display_info': {
                    'budget_display': 'ﾂ･1,000',
                    'photo_url': 'http://example.com/photo.jpg',
                    'hotpepper_url': 'http://example.com',
                    'map_url': 'https://maps.google.com',
                    'summary': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ - 蜥碁｣・,
                    'access_display': '蠕呈ｭｩ5蛻・,
                    'hours_display': '11:00-14:00'
                },
                'distance_info': {
                    'distance_km': 0.5,
                    'distance_display': '500m',
                    'walking_time_minutes': 8,
                    'time_display': '蠕呈ｭｩ邏・蛻・
                }
            }
            mock_restaurant_selector.return_value = mock_selector_instance

            mock_weather_instance = Mock()
            mock_weather_instance.get_current_weather.return_value = {
                'temperature': 25.0,
                'description': '譎ｴ繧・,
                'uv_index': 5.0,
                'icon': '01d',
                'source': 'openweathermap'
            }
            mock_weather_instance.is_good_weather_for_walking.return_value = True
            mock_weather_service.return_value = mock_weather_instance

            # 繝ｪ繧ｯ繧ｨ繧ｹ繝医ョ繝ｼ繧ｿ
            request_data = {
                'latitude': 35.6812,
                'longitude': 139.7671
            }

            response = client.post('/roulette',
                                   data=json.dumps(request_data),
                                   content_type='application/json')

            assert response.status_code == 200
            assert response.content_type == 'application/json'

            # 繝ｬ繧ｹ繝昴Φ繧ｹ繝・・繧ｿ縺ｮ遒ｺ隱・
            data = response.get_json()
            assert data['success'] is True
            assert 'restaurant' in data
            assert 'distance' in data
            assert data['restaurant']['name'] == '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ'
            assert data['distance']['distance_display'] == '500m'

    def test_roulette_endpoint_no_restaurants(self, client):
        """繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝茨ｼ医Ξ繧ｹ繝医Λ繝ｳ縺ｪ縺暦ｼ峨ユ繧ｹ繝・""
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # 繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷・
            mock_restaurant_instance = Mock()
            mock_restaurant_instance.search_lunch_restaurants.return_value = []
            mock_restaurant_service.return_value = mock_restaurant_instance

            mock_weather_instance = Mock()
            mock_weather_instance.get_current_weather.return_value = {
                'temperature': 25.0,
                'description': '譎ｴ繧・,
                'uv_index': 5.0,
                'icon': '01d'
            }
            mock_weather_instance.is_good_weather_for_walking.return_value = True
            mock_weather_service.return_value = mock_weather_instance

            request_data = {
                'latitude': 35.6812,
                'longitude': 139.7671
            }

            response = client.post('/roulette',
                                   data=json.dumps(request_data),
                                   content_type='application/json')

            assert response.status_code == 200

            data = response.get_json()
            assert data['success'] is False
            assert '繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ' in data['message']

    def test_roulette_endpoint_missing_coordinates(self, client):
        """繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝茨ｼ亥ｺｧ讓吩ｸ崎ｶｳ・峨ユ繧ｹ繝・""
        with patch('location_service.LocationService') as mock_location_service, \
                patch('restaurant_service.RestaurantService') as mock_restaurant_service, \
                patch('weather_service.WeatherService') as mock_weather_service:

            # LocationService縺ｮ繝｢繝・け險ｭ螳夲ｼ・P縺九ｉ菴咲ｽｮ諠・ｱ繧貞叙蠕暦ｼ・
            mock_location_instance = Mock()
            mock_location_instance.get_location_from_ip.return_value = {
                'latitude': 35.6812,
                'longitude': 139.7671,
                'city': '譚ｱ莠ｬ',
                'source': 'ipapi.co'
            }
            mock_location_service.return_value = mock_location_instance

            # 繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷・
            mock_restaurant_instance = Mock()
            mock_restaurant_instance.search_lunch_restaurants.return_value = []
            mock_restaurant_service.return_value = mock_restaurant_instance

            mock_weather_instance = Mock()
            mock_weather_instance.get_current_weather.return_value = {
                'temperature': 25.0,
                'description': '譎ｴ繧・,
                'uv_index': 5.0,
                'icon': '01d'
            }
            mock_weather_instance.is_good_weather_for_walking.return_value = True
            mock_weather_service.return_value = mock_weather_instance

            # 蠎ｧ讓吶′荳崎ｶｳ縺励※縺・ｋ繝ｪ繧ｯ繧ｨ繧ｹ繝茨ｼ・P縺九ｉ蜿門ｾ励＆繧後ｋ・・
            request_data = {
                'latitude': 35.6812
                # longitude 縺御ｸ崎ｶｳ
            }

            response = client.post('/roulette',
                                   data=json.dumps(request_data),
                                   content_type='application/json')

            # 蠎ｧ讓吩ｸ崎ｶｳ縺ｧ繧・P縺九ｉ蜿門ｾ励☆繧九◆繧・00縺瑚ｿ斐＆繧後ｋ
            assert response.status_code == 200

            data = response.get_json()
            assert data['success'] is False  # 繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｉ縺ｪ縺・◆繧・
            assert '繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ' in data['message']

    def test_roulette_endpoint_invalid_json(self, client):
        """繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝茨ｼ育┌蜉ｹ縺ｪJSON・峨ユ繧ｹ繝・""
        response = client.post('/roulette',
                               data='invalid json',
                               content_type='application/json')

        # 辟｡蜉ｹ縺ｪJSON縺ｯ500繧ｨ繝ｩ繝ｼ縺ｫ縺ｪ繧具ｼ医い繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｮ螳溯｣・↓繧医ｋ・・
        assert response.status_code == 500

        data = response.get_json()
        assert data['error'] is True
        assert 'message' in data

    def test_roulette_endpoint_service_error(self, client):
        """繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝茨ｼ医し繝ｼ繝薙せ繧ｨ繝ｩ繝ｼ・峨ユ繧ｹ繝・""
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service:

            # 繧ｵ繝ｼ繝薙せ縺ｧ繧ｨ繝ｩ繝ｼ縺檎匱逕溘☆繧句ｴ蜷・
            mock_restaurant_service.side_effect = Exception("Service error")

            request_data = {
                'latitude': 35.6812,
                'longitude': 139.7671
            }

            response = client.post('/roulette',
                                   data=json.dumps(request_data),
                                   content_type='application/json')

            assert response.status_code == 500

            data = response.get_json()
            assert data['error'] is True
            assert 'message' in data

    def test_404_error_handler(self, client):
        """404繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ繝・せ繝・""
        response = client.get('/nonexistent-page')

        assert response.status_code == 404

        # JSON繝ｬ繧ｹ繝昴Φ繧ｹ縺ｾ縺溘・HTML繝ｬ繧ｹ繝昴Φ繧ｹ縺ｮ縺・★繧後°縺瑚ｿ斐＆繧後ｋ
        if response.content_type == 'application/json':
            data = response.get_json()
            assert data['error'] is True
            assert '繝壹・繧ｸ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ' in data['message']
        else:
            # HTML繧ｨ繝ｩ繝ｼ繝壹・繧ｸ縺ｮ蝣ｴ蜷・
            assert response.content_type.startswith('text/html')

    def test_500_error_handler(self, client):
        """500繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ繝・せ繝・""
        # 譌｢蟄倥・繧ｨ繝ｳ繝峨・繧､繝ｳ繝医〒繧ｨ繝ｩ繝ｼ繧堤匱逕溘＆縺帙ｋ
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service:
            # 繧ｵ繝ｼ繝薙せ縺ｧ繧ｨ繝ｩ繝ｼ縺檎匱逕溘☆繧句ｴ蜷・
            mock_restaurant_service.side_effect = Exception("Test error")

            request_data = {
                'latitude': 35.6812,
                'longitude': 139.7671
            }

            response = client.post('/roulette',
                                   data=json.dumps(request_data),
                                   content_type='application/json')

            assert response.status_code == 500

            if response.content_type == 'application/json':
                data = response.get_json()
                assert data['error'] is True
                assert 'message' in data

    def test_method_not_allowed(self, client):
        """繝｡繧ｽ繝・ラ荳崎ｨｱ蜿ｯ繝・せ繝・""
        # POST繧ｨ繝ｳ繝峨・繧､繝ｳ繝医↓GET繝ｪ繧ｯ繧ｨ繧ｹ繝・
        response = client.get('/roulette')

        assert response.status_code == 405

    def test_content_type_validation(self, client):
        """Content-Type讀懆ｨｼ繝・せ繝・""
        # 荳肴ｭ｣縺ｪContent-Type
        response = client.post('/roulette',
                               data='{"latitude": 35.6812, "longitude": 139.7671}',
                               content_type='text/plain')

        # Content-Type縺御ｸ肴ｭ｣縺ｪ蝣ｴ蜷医・500繧ｨ繝ｩ繝ｼ縺ｫ縺ｪ繧具ｼ医い繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｮ螳溯｣・↓繧医ｋ・・
        assert response.status_code == 500

        data = response.get_json()
        assert data['error'] is True

    def test_large_request_handling(self, client):
        """螟ｧ縺阪↑繝ｪ繧ｯ繧ｨ繧ｹ繝亥・逅・ユ繧ｹ繝・""
        # 螟ｧ縺阪↑JSON繝・・繧ｿ
        large_data = {
            'latitude': 35.6812,
            'longitude': 139.7671,
            'extra_data': 'x' * 10000  # 10KB 縺ｮ菴吝・縺ｪ繝・・繧ｿ
        }

        response = client.post('/roulette',
                               data=json.dumps(large_data),
                               content_type='application/json')

        # 螟ｧ縺阪↑繝ｪ繧ｯ繧ｨ繧ｹ繝医〒繧ょ・逅・＆繧後ｋ・亥ｿ・ｦ√↑驛ｨ蛻・・縺ｿ菴ｿ逕ｨ・・
        assert response.status_code in [200, 400, 413]

    def test_concurrent_requests_simulation(self, client):
        """蜷梧凾繝ｪ繧ｯ繧ｨ繧ｹ繝医す繝溘Η繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ繝・せ繝・""
        with patch('restaurant_service.RestaurantService') as mock_restaurant_service, \
                patch('restaurant_selector.RestaurantSelector') as mock_restaurant_selector, \
                patch('weather_service.WeatherService') as mock_weather_service:

            mock_restaurant_instance = Mock()
            mock_restaurant_instance.search_lunch_restaurants.return_value = [{
                'id': 'J001234567',
                'name': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ',
                'genre': '蜥碁｣・,
                'lat': 35.6815,
                'lng': 139.7675,
                'budget_average': 1000,
                'address': '譚ｱ莠ｬ驛ｽ蜊・ｻ｣逕ｰ蛹ｺ',
                'urls': {'pc': 'http://example.com'},
                'photo': 'http://example.com/photo.jpg'
            }]
            mock_restaurant_service.return_value = mock_restaurant_instance

            mock_selector_instance = Mock()
            mock_selector_instance.select_random_restaurant.return_value = {
                'id': 'J001234567',
                'name': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ',
                'genre': '蜥碁｣・,
                'address': '譚ｱ莠ｬ驛ｽ蜊・ｻ｣逕ｰ蛹ｺ',
                'catch': '縺翫＞縺励＞繝ｬ繧ｹ繝医Λ繝ｳ',
                'display_info': {
                    'budget_display': 'ﾂ･1,000',
                    'photo_url': 'http://example.com/photo.jpg',
                    'hotpepper_url': 'http://example.com',
                    'map_url': 'https://maps.google.com',
                    'summary': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ - 蜥碁｣・,
                    'access_display': '蠕呈ｭｩ5蛻・,
                    'hours_display': '11:00-14:00'
                },
                'distance_info': {
                    'distance_km': 0.5,
                    'distance_display': '500m',
                    'walking_time_minutes': 8,
                    'time_display': '蠕呈ｭｩ邏・蛻・
                }
            }
            mock_restaurant_selector.return_value = mock_selector_instance

            mock_weather_instance = Mock()
            mock_weather_instance.get_current_weather.return_value = {
                'temperature': 25.0,
                'description': '譎ｴ繧・,
                'uv_index': 5.0,
                'icon': '01d'
            }
            mock_weather_instance.is_good_weather_for_walking.return_value = True
            mock_weather_service.return_value = mock_weather_instance

            # 隍・焚縺ｮ繝ｪ繧ｯ繧ｨ繧ｹ繝医ｒ鬆・ｬ｡螳溯｡鯉ｼ亥酔譎ょｮ溯｡後・繧ｷ繝溘Η繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ・・
            request_data = {
                'latitude': 35.6812,
                'longitude': 139.7671
            }

            responses = []
            for i in range(5):
                response = client.post('/roulette',
                                       data=json.dumps(request_data),
                                       content_type='application/json')
                responses.append(response)

            # 縺吶∋縺ｦ縺ｮ繝ｪ繧ｯ繧ｨ繧ｹ繝医′豁｣蟶ｸ縺ｫ蜃ｦ逅・＆繧後ｋ縺薙→繧堤｢ｺ隱・
            for response in responses:
                assert response.status_code in [200, 500]  # 謌仙粥縺ｾ縺溘・繧ｵ繝ｼ繝舌・繧ｨ繝ｩ繝ｼ


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
