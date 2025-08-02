#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lunch Roulette - 繝｡繧､繝ｳ繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ
譚ｱ莠ｬ繧ｨ繝ｪ繧｢縺ｮ繝ｩ繝ｳ繝√せ繝昴ャ繝育匱隕妓eb繧ｵ繝ｼ繝薙せ

縺薙・繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｯ莉･荳九・讖溯・繧呈署萓帙＠縺ｾ縺・
- IP繧｢繝峨Ξ繧ｹ繝吶・繧ｹ縺ｮ菴咲ｽｮ諠・ｱ讀懷・
- 繝ｪ繧｢繝ｫ繧ｿ繧､繝螟ｩ豌玲ュ蝣ｱ縺ｮ蜿門ｾ・
- 霑代￥縺ｮ繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢縺ｨ繝ｩ繝ｳ繝繝謗ｨ阮ｦ
- PythonAnywhere辟｡譁吶・繝ｩ繝ｳ蟇ｾ蠢・
"""

from flask import Flask, render_template, request, jsonify
import os
import logging
from database import init_database
from cache_service import CacheService
from error_handler import ErrorHandler

# Flask繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｮ蛻晄悄蛹・
app = Flask(__name__)

# 險ｭ螳・
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DATABASE'] = 'cache.db'

# 繝・ヰ繝・げ繝｢繝ｼ繝会ｼ域悽逡ｪ迺ｰ蠅・〒縺ｯ辟｡蜉ｹ縺ｫ縺吶ｋ・・
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# 繧ｭ繝｣繝・す繝･繧ｵ繝ｼ繝薙せ縺ｮ蛻晄悄蛹・
cache_service = CacheService(db_path=app.config['DATABASE'])

# 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ縺ｮ蛻晄悄蛹・
error_handler = ErrorHandler()

# 繝ｭ繧ｰ險ｭ螳・
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def init_db():
    """
    SQLite繧ｭ繝｣繝・す繝･繝・・繧ｿ繝吶・繧ｹ繧貞・譛溷喧
    繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ襍ｷ蜍墓凾縺ｫ螳溯｡後＆繧後ｋ
    """
    return init_database(app.config['DATABASE'])


@app.route('/')
def index():
    """
    繝｡繧､繝ｳ繝壹・繧ｸ縺ｮ繝ｫ繝ｼ繝・
    菴咲ｽｮ諠・ｱ縺ｨ螟ｩ豌玲ュ蝣ｱ繧定｡ｨ遉ｺ縺励√Ν繝ｼ繝ｬ繝・ヨ讖溯・繧呈署萓・

    Returns:
        str: 繝ｬ繝ｳ繝繝ｪ繝ｳ繧ｰ縺輔ｌ縺櫞TML繝・Φ繝励Ξ繝ｼ繝・
    """
    try:
        # 蠢・ｦ√↑繧ｵ繝ｼ繝薙せ繧ｯ繝ｩ繧ｹ繧偵う繝ｳ繝昴・繝・
        from location_service import LocationService
        from weather_service import WeatherService

        # 繧ｵ繝ｼ繝薙せ繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ繧剃ｽ懈・
        location_service = LocationService(cache_service)
        weather_service = WeatherService(cache_service=cache_service)

        # 繧ｯ繝ｩ繧､繧｢繝ｳ繝医・IP繧｢繝峨Ξ繧ｹ繧貞叙蠕・
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if client_ip and ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()

        print(f"繧ｯ繝ｩ繧､繧｢繝ｳ繝・P: {client_ip}")

        # 菴咲ｽｮ諠・ｱ繧貞叙蠕・
        location_data = location_service.get_location_from_ip(client_ip)

        # 螟ｩ豌玲ュ蝣ｱ繧貞叙蠕・
        weather_data = weather_service.get_current_weather(
            location_data['latitude'],
            location_data['longitude']
        )

        # 繝・Φ繝励Ξ繝ｼ繝医↓貂｡縺吶ョ繝ｼ繧ｿ繧呈ｺ門ｙ
        template_data = {
            'location': location_data,
            'weather': weather_data,
            'weather_icon_url': weather_service.get_weather_icon_url(weather_data['icon']),
            'is_default_location': location_service.is_default_location(location_data),
            'is_default_weather': weather_service.is_default_weather(weather_data),
            'weather_summary': weather_service.get_weather_summary(
                location_data['latitude'],
                location_data['longitude']
            ),
            'is_good_walking_weather': weather_service.is_good_weather_for_walking(
                location_data['latitude'],
                location_data['longitude']
            )
        }

        print(f"繝｡繧､繝ｳ繝壹・繧ｸ陦ｨ遉ｺ: {location_data['city']}, {weather_data['description']}")

        return render_template('index.html', **template_data)

    except Exception as e:
        # 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ・壹お繝ｩ繝ｼ譎ゅ・繝・ヵ繧ｩ繝ｫ繝域ュ蝣ｱ縺ｧ繝壹・繧ｸ繧定｡ｨ遉ｺ
        app.logger.error(f'繝｡繧､繝ｳ繝壹・繧ｸ陦ｨ遉ｺ縺ｧ繧ｨ繝ｩ繝ｼ縺檎匱逕・ {str(e)}')

        # 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ縺ｧ繧ｨ繝ｩ繝ｼ諠・ｱ繧貞・逅・
        error_info = error_handler.handle_location_error(e, fallback_available=True)

        # 繝・ヵ繧ｩ繝ｫ繝医ョ繝ｼ繧ｿ縺ｧ繝壹・繧ｸ繧定｡ｨ遉ｺ
        default_data = {
            'location': {
                'city': '譚ｱ莠ｬ',
                'region': '譚ｱ莠ｬ驛ｽ',
                'latitude': 35.6812,
                'longitude': 139.7671,
                'source': 'default'
            },
            'weather': {
                'temperature': 20.0,
                'description': '譎ｴ繧・,
                'uv_index': 3.0,
                'icon': '01d',
                'source': 'default'
            },
            'weather_icon_url': 'https://openweathermap.org/img/wn/01d@2x.png',
            'is_default_location': True,
            'is_default_weather': True,
            'weather_summary': '譎ｴ繧・20ﾂｰC UV謖・焚3',
            'is_good_walking_weather': True,
            'error_message': error_info  # 繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ繧定ｿｽ蜉
        }

        return render_template('index.html', **default_data)


@app.route('/roulette', methods=['POST'])
def roulette():
    """
    繝ｬ繧ｹ繝医Λ繝ｳ繝ｫ繝ｼ繝ｬ繝・ヨ縺ｮ繧ｨ繝ｳ繝峨・繧､繝ｳ繝・
    繝ｩ繝ｳ繝繝縺ｪ繝ｬ繧ｹ繝医Λ繝ｳ謗ｨ阮ｦ繧定ｿ斐☆

    Returns:
        dict: 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ縺ｮJSON繝ｬ繧ｹ繝昴Φ繧ｹ
    """
    try:
        # 蠢・ｦ√↑繧ｵ繝ｼ繝薙せ繧ｯ繝ｩ繧ｹ繧偵う繝ｳ繝昴・繝・
        from location_service import LocationService
        from weather_service import WeatherService
        from restaurant_service import RestaurantService
        from restaurant_selector import RestaurantSelector
        from distance_calculator import DistanceCalculator

        # 繧ｵ繝ｼ繝薙せ繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ繧剃ｽ懈・
        location_service = LocationService(cache_service)
        weather_service = WeatherService(cache_service=cache_service)
        restaurant_service = RestaurantService(cache_service=cache_service)
        distance_calculator = DistanceCalculator(error_handler)
        restaurant_selector = RestaurantSelector(distance_calculator, error_handler)

        # 繝ｪ繧ｯ繧ｨ繧ｹ繝医ョ繝ｼ繧ｿ繧貞叙蠕・
        request_data = request.get_json() or {}

        # 菴咲ｽｮ諠・ｱ繧貞叙蠕暦ｼ医Μ繧ｯ繧ｨ繧ｹ繝医°繧峨√∪縺溘・IP繧｢繝峨Ξ繧ｹ縺九ｉ・・
        if 'latitude' in request_data and 'longitude' in request_data:
            # 繝ｪ繧ｯ繧ｨ繧ｹ繝医↓菴咲ｽｮ諠・ｱ縺悟性縺ｾ繧後※縺・ｋ蝣ｴ蜷・
            user_lat = float(request_data['latitude'])
            user_lon = float(request_data['longitude'])
            print(f"繝ｪ繧ｯ繧ｨ繧ｹ繝医°繧我ｽ咲ｽｮ諠・ｱ繧貞叙蠕・ {user_lat}, {user_lon}")
        else:
            # IP繧｢繝峨Ξ繧ｹ縺九ｉ菴咲ｽｮ諠・ｱ繧貞叙蠕・
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            if client_ip and ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()

            location_data = location_service.get_location_from_ip(client_ip)
            user_lat = location_data['latitude']
            user_lon = location_data['longitude']
            print(f"IP繧｢繝峨Ξ繧ｹ縺九ｉ菴咲ｽｮ諠・ｱ繧貞叙蠕・ {user_lat}, {user_lon}")

        # 螟ｩ豌玲ュ蝣ｱ繧貞叙蠕暦ｼ医Ξ繧ｹ繝昴Φ繧ｹ縺ｫ蜷ｫ繧√ｋ縺溘ａ・・
        weather_data = weather_service.get_current_weather(user_lat, user_lon)

        # 繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢繧貞ｮ溯｡鯉ｼ亥濠蠕・km縲√Λ繝ｳ繝∽ｺ育ｮ冷王ﾂ･1,200・・
        restaurants = restaurant_service.search_lunch_restaurants(user_lat, user_lon, radius=1)

        # 繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷・
        if not restaurants:
            # 繝ｬ繧ｹ繝医Λ繝ｳ譛ｪ逋ｺ隕九お繝ｩ繝ｼ繧貞・逅・
            no_restaurant_error = ValueError("霑代￥縺ｫ繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ縺ｧ縺励◆")
            error_info = error_handler.handle_restaurant_error(no_restaurant_error, fallback_available=False)

            return jsonify({
                'success': False,
                'error_info': error_info,
                'message': error_info['message'],
                'suggestion': error_info['suggestion'],
                'weather': {
                    'description': weather_data['description'],
                    'temperature': weather_data['temperature'],
                    'is_good_walking_weather': weather_service.is_good_weather_for_walking(user_lat, user_lon)
                }
            })

        # 繝ｩ繝ｳ繝繝縺ｫ繝ｬ繧ｹ繝医Λ繝ｳ繧帝∈謚槭＠縲∬ｷ晞屬諠・ｱ繧堤ｵｱ蜷・
        selected_restaurant = restaurant_selector.select_random_restaurant(restaurants, user_lat, user_lon)

        if not selected_restaurant:
            # 繝ｬ繧ｹ繝医Λ繝ｳ驕ｸ謚槭お繝ｩ繝ｼ繧貞・逅・
            selection_error = ValueError("繝ｬ繧ｹ繝医Λ繝ｳ驕ｸ謚樔ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆")
            error_info = error_handler.handle_restaurant_error(selection_error, fallback_available=False)

            return jsonify({
                'success': False,
                'error_info': error_info,
                'message': error_info['message'],
                'suggestion': error_info['suggestion'],
                'weather': {
                    'description': weather_data['description'],
                    'temperature': weather_data['temperature'],
                    'is_good_walking_weather': weather_service.is_good_weather_for_walking(user_lat, user_lon)
                }
            })

        # 謌仙粥繝ｬ繧ｹ繝昴Φ繧ｹ繧堤函謌・
        response_data = {
            'success': True,
            'restaurant': {
                'id': selected_restaurant['id'],
                'name': selected_restaurant['name'],
                'genre': selected_restaurant['genre'],
                'address': selected_restaurant['address'],
                'budget_display': selected_restaurant['display_info']['budget_display'],
                'photo_url': selected_restaurant['display_info']['photo_url'],
                'hotpepper_url': selected_restaurant['display_info']['hotpepper_url'],
                'map_url': selected_restaurant['display_info']['map_url'],
                'summary': selected_restaurant['display_info']['summary'],
                'catch': selected_restaurant.get('catch', ''),
                'access': selected_restaurant['display_info']['access_display'],
                'hours': selected_restaurant['display_info']['hours_display']
            },
            'distance': {
                'distance_km': selected_restaurant['distance_info']['distance_km'],
                'distance_display': selected_restaurant['distance_info']['distance_display'],
                'walking_time_minutes': selected_restaurant['distance_info']['walking_time_minutes'],
                'time_display': selected_restaurant['distance_info']['time_display']
            },
            'weather': {
                'description': weather_data['description'],
                'temperature': weather_data['temperature'],
                'uv_index': weather_data['uv_index'],
                'is_good_walking_weather': weather_service.is_good_weather_for_walking(user_lat, user_lon),
                'icon': weather_data['icon']
            },
            'search_info': {
                'total_restaurants_found': len(restaurants),
                'search_radius_km': 1,
                'max_budget': restaurant_service.LUNCH_BUDGET_LIMIT,
                'user_location': {
                    'latitude': user_lat,
                    'longitude': user_lon
                }
            }
        }

        print(f"繝ｫ繝ｼ繝ｬ繝・ヨ謌仙粥: {selected_restaurant['name']} ({selected_restaurant['distance_info']['distance_display']})")

        return jsonify(response_data)

    except ValueError as e:
        # 蜈･蜉帛､繧ｨ繝ｩ繝ｼ
        app.logger.error(f'繝ｫ繝ｼ繝ｬ繝・ヨ蜃ｦ逅・〒蜈･蜉帛､繧ｨ繝ｩ繝ｼ: {str(e)}')
        error_info = error_handler.handle_location_error(e, fallback_available=False)

        return jsonify({
            'error': True,
            'error_info': error_info,
            'message': error_info['message'],
            'suggestion': error_info['suggestion']
        }), 400

    except Exception as e:
        # 縺昴・莉悶・繧ｨ繝ｩ繝ｼ
        app.logger.error(f'繝ｫ繝ｼ繝ｬ繝・ヨ蜃ｦ逅・〒莠域悄縺励↑縺・お繝ｩ繝ｼ: {str(e)}')

        # 豎守畑繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ
        error_type, error_info = error_handler.handle_api_error('roulette', e, fallback_available=False)
        user_message = error_handler.create_user_friendly_message(error_info)

        return jsonify({
            'error': True,
            'error_info': user_message,
            'message': user_message['message'],
            'suggestion': user_message['suggestion']
        }), 500


@app.errorhandler(404)
def not_found_error(error):
    """404繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ"""
    return jsonify({'error': True, 'message': '繝壹・繧ｸ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ"""
    return jsonify({'error': True, 'message': '繧ｵ繝ｼ繝舌・蜀・Κ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆'}), 500


# 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ襍ｷ蜍墓凾縺ｮ蛻晄悄蛹・
if __name__ == '__main__':
    # 繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹・
    init_db()

    # 髢狗匱繧ｵ繝ｼ繝舌・襍ｷ蜍・
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )
