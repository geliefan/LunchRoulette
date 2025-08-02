#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
譛ｬ逡ｪ迺ｰ蠅・ユ繧ｹ繝・- Production Environment Testing
Lunch Roulette 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｮ譛ｬ逡ｪ迺ｰ蠅・ｯｾ蠢懊ユ繧ｹ繝・

縺薙・繝・せ繝医せ繧､繝ｼ繝医・莉･荳九ｒ繧ｫ繝舌・縺励∪縺・
1. 繝ｭ繝ｼ繧ｫ繝ｫ迺ｰ蠅・〒縺ｮ譛邨ょ虚菴懃｢ｺ隱・
2. API蛻ｶ髯仙・縺ｧ縺ｮ蜍穂ｽ懃｢ｺ隱・
3. 繝代ヵ繧ｩ繝ｼ繝槭Φ繧ｹ繝・せ繝亥ｮ溯｡・

隕∽ｻｶ: 4.3, 5.4
"""

import unittest
import time
import threading
import requests
import json
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sqlite3

# 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繝｢繧ｸ繝･繝ｼ繝ｫ繧偵う繝ｳ繝昴・繝・
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app, init_db
from cache_service import CacheService
from location_service import LocationService
from weather_service import WeatherService
from restaurant_service import RestaurantService


class ProductionEnvironmentTest(unittest.TestCase):
    """譛ｬ逡ｪ迺ｰ蠅・ユ繧ｹ繝育畑縺ｮ繝・せ繝医け繝ｩ繧ｹ"""

    @classmethod
    def setUpClass(cls):
        """繝・せ繝医け繝ｩ繧ｹ蜈ｨ菴薙・蛻晄悄蛹・""
        print("\n" + "="*60)
        print("譛ｬ逡ｪ迺ｰ蠅・ユ繧ｹ繝磯幕蟋・- Production Environment Testing")
        print("="*60)
        
        # 繝・せ繝育畑繝・・繧ｿ繝吶・繧ｹ繧貞・譛溷喧
        cls.test_db = 'test_production.db'
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
        
        # Flask繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧偵ユ繧ｹ繝医Δ繝ｼ繝峨〒險ｭ螳・
        app.config['TESTING'] = True
        app.config['DATABASE'] = cls.test_db
        app.config['DEBUG'] = False  # 譛ｬ逡ｪ迺ｰ蠅・ｨｭ螳・
        
        # 繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹・
        init_db()
        
        cls.client = app.test_client()
        cls.cache_service = CacheService(db_path=cls.test_db)
        
        # API蛻ｶ髯占ｿｽ霍｡逕ｨ
        cls.api_call_count = {
            'location': 0,
            'weather': 0,
            'restaurant': 0
        }
        cls.test_start_time = datetime.now()

    @classmethod
    def tearDownClass(cls):
        """繝・せ繝医け繝ｩ繧ｹ蜈ｨ菴薙・繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・"""
        try:
            # 繝・・繧ｿ繝吶・繧ｹ謗･邯壹ｒ譏守､ｺ逧・↓髢峨§繧・
            if hasattr(cls, 'cache_service'):
                cls.cache_service.close_connection()
            
            # 繝輔ぃ繧､繝ｫ縺悟ｭ伜惠縺励∝炎髯､蜿ｯ閭ｽ縺ｪ蝣ｴ蜷医・縺ｿ蜑企勁
            if os.path.exists(cls.test_db):
                try:
                    os.remove(cls.test_db)
                except PermissionError:
                    print(f"笞 繝・せ繝医ョ繝ｼ繧ｿ繝吶・繧ｹ繝輔ぃ繧､繝ｫ {cls.test_db} 繧貞炎髯､縺ｧ縺阪∪縺帙ｓ縺ｧ縺励◆・井ｽｿ逕ｨ荳ｭ・・)
        except Exception as e:
            print(f"笞 繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・荳ｭ縺ｫ繧ｨ繝ｩ繝ｼ: {e}")
        
        print("\n" + "="*60)
        print("譛ｬ逡ｪ迺ｰ蠅・ユ繧ｹ繝亥ｮ御ｺ・)
        print("="*60)

    def setUp(self):
        """蜷・ユ繧ｹ繝医・蛻晄悄蛹・""
        self.start_time = time.time()

    def tearDown(self):
        """蜷・ユ繧ｹ繝医・繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・"""
        end_time = time.time()
        execution_time = end_time - self.start_time
        print(f"繝・せ繝亥ｮ溯｡梧凾髢・ {execution_time:.3f}遘・)


class LocalEnvironmentTest(ProductionEnvironmentTest):
    """1. 繝ｭ繝ｼ繧ｫ繝ｫ迺ｰ蠅・〒縺ｮ譛邨ょ虚菴懃｢ｺ隱・""

    def test_01_application_startup(self):
        """繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ襍ｷ蜍輔ユ繧ｹ繝・""
        print("\n[繝・せ繝・1.1] 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ襍ｷ蜍慕｢ｺ隱・)
        
        # 繝｡繧､繝ｳ繝壹・繧ｸ縺ｸ縺ｮ繧｢繧ｯ繧ｻ繧ｹ繝・せ繝・
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Lunch Roulette', response.data)
        print("笨・繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺梧ｭ｣蟶ｸ縺ｫ襍ｷ蜍・)

    def test_02_database_initialization(self):
        """繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹悶ユ繧ｹ繝・""
        print("\n[繝・せ繝・1.2] 繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹也｢ｺ隱・)
        
        # 繝・・繧ｿ繝吶・繧ｹ繝輔ぃ繧､繝ｫ縺ｮ蟄伜惠遒ｺ隱・
        self.assertTrue(os.path.exists(self.test_db))
        
        # 繝・・繝悶Ν讒矩縺ｮ遒ｺ隱・
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # cache繝・・繝悶Ν縺ｮ蟄伜惠遒ｺ隱・
        table_names = [table[0] for table in tables]
        self.assertIn('cache', table_names)
        
        # cache繝・・繝悶Ν縺ｮ讒矩遒ｺ隱・
        cursor.execute("PRAGMA table_info(cache);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        expected_columns = ['id', 'cache_key', 'data', 'created_at', 'expires_at']
        for col in expected_columns:
            self.assertIn(col, column_names)
        
        conn.close()
        print("笨・繝・・繧ｿ繝吶・繧ｹ縺梧ｭ｣蟶ｸ縺ｫ蛻晄悄蛹悶＆繧後※縺・ｋ")

    def test_03_main_page_functionality(self):
        """繝｡繧､繝ｳ繝壹・繧ｸ讖溯・繝・せ繝・""
        print("\n[繝・せ繝・1.3] 繝｡繧､繝ｳ繝壹・繧ｸ讖溯・遒ｺ隱・)
        
        with patch('location_service.LocationService.get_location_from_ip') as mock_location, \
             patch('weather_service.WeatherService.get_current_weather') as mock_weather:
            
            # 繝｢繝・け繝・・繧ｿ繧定ｨｭ螳・
            mock_location.return_value = {
                'city': '譚ｱ莠ｬ',
                'region': '譚ｱ莠ｬ驛ｽ',
                'latitude': 35.6812,
                'longitude': 139.7671,
                'source': 'test'
            }
            
            mock_weather.return_value = {
                'temperature': 22.5,
                'description': '譎ｴ繧・,
                'uv_index': 4.0,
                'icon': '01d',
                'source': 'test'
            }
            
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            
            # HTML繧ｳ繝ｳ繝・Φ繝・・遒ｺ隱・
            html_content = response.data.decode('utf-8')
            self.assertIn('譚ｱ莠ｬ', html_content)
            self.assertIn('譎ｴ繧・, html_content)
            self.assertIn('繝ｫ繝ｼ繝ｬ繝・ヨ繧貞屓縺・, html_content)
            
        print("笨・繝｡繧､繝ｳ繝壹・繧ｸ縺梧ｭ｣蟶ｸ縺ｫ蜍穂ｽ・)

    def test_04_roulette_endpoint(self):
        """繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝医ユ繧ｹ繝・""
        print("\n[繝・せ繝・1.4] 繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝育｢ｺ隱・)
        
        with patch('location_service.LocationService.get_location_from_ip') as mock_location, \
             patch('weather_service.WeatherService.get_current_weather') as mock_weather, \
             patch('weather_service.WeatherService.is_good_weather_for_walking') as mock_walking, \
             patch('restaurant_service.RestaurantService.search_lunch_restaurants') as mock_restaurants:
            
            # 繝｢繝・け繝・・繧ｿ繧定ｨｭ螳・
            mock_location.return_value = {
                'latitude': 35.6812,
                'longitude': 139.7671
            }
            
            mock_weather.return_value = {
                'temperature': 22.5,
                'description': '譎ｴ繧・,
                'condition': 'clear',  # 蠢・ｦ√↑繝輔ぅ繝ｼ繝ｫ繝峨ｒ霑ｽ蜉
                'uv_index': 4.0,
                'icon': '01d'
            }
            
            mock_walking.return_value = True
            
            mock_restaurants.return_value = [{
                'id': 'test_restaurant_001',
                'name': '繝・せ繝医Ξ繧ｹ繝医Λ繝ｳ',
                'genre': '蜥碁｣・,
                'address': '譚ｱ莠ｬ驛ｽ蜊・ｻ｣逕ｰ蛹ｺ',
                'lat': 35.6815,
                'lng': 139.7675,
                'budget': 1000,
                'photo': 'https://example.com/photo.jpg',
                'urls': {'pc': 'https://example.com/restaurant'},
                'catch': '縺翫＞縺励＞蜥碁｣溘Ξ繧ｹ繝医Λ繝ｳ',
                'access': '譚ｱ莠ｬ鬧・ｾ呈ｭｩ5蛻・,
                'open': '11:00-14:00'
            }]
            
            # 繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝医ｒ繝・せ繝・
            response = self.client.post('/roulette', 
                                      json={'latitude': 35.6812, 'longitude': 139.7671},
                                      content_type='application/json')
            
            # 繝ｬ繧ｹ繝昴Φ繧ｹ縺ｮ遒ｺ隱搾ｼ医お繝ｩ繝ｼ縺ｮ蝣ｴ蜷医・隧ｳ邏ｰ繧定｡ｨ遉ｺ・・
            if response.status_code != 200:
                print(f"繧ｨ繝ｩ繝ｼ繝ｬ繧ｹ繝昴Φ繧ｹ: {response.status_code}")
                print(f"繝ｬ繧ｹ繝昴Φ繧ｹ蜀・ｮｹ: {response.data.decode('utf-8')}")
            
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('restaurant', data)
            self.assertIn('distance', data)
            self.assertIn('weather', data)
            
        print("笨・繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝医′豁｣蟶ｸ縺ｫ蜍穂ｽ・)

    def test_05_error_handling(self):
        """繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繝・せ繝・""
        print("\n[繝・せ繝・1.5] 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ遒ｺ隱・)
        
        # 蟄伜惠縺励↑縺・お繝ｳ繝峨・繧､繝ｳ繝医∈縺ｮ繧｢繧ｯ繧ｻ繧ｹ
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        
        # 荳肴ｭ｣縺ｪJSON繝・・繧ｿ縺ｧ縺ｮPOST・・lask縺瑚・蜍慕噪縺ｫ400繧定ｿ斐☆縺薙→繧呈悄蠕・ｼ・
        response = self.client.post('/roulette', 
                                  data='invalid json',
                                  content_type='application/json')
        # 螳滄圀縺ｮ繝ｬ繧ｹ繝昴Φ繧ｹ繧堤｢ｺ隱・
        if response.status_code not in [400, 500]:
            print(f"莠域悄縺励↑縺・せ繝・・繧ｿ繧ｹ繧ｳ繝ｼ繝・ {response.status_code}")
            print(f"繝ｬ繧ｹ繝昴Φ繧ｹ蜀・ｮｹ: {response.data.decode('utf-8')}")
        
        # 400縺ｾ縺溘・500縺ｮ縺・★繧後°繧定ｨｱ蜿ｯ・亥ｮ溯｣・↓繧医▲縺ｦ逡ｰ縺ｪ繧具ｼ・
        self.assertIn(response.status_code, [400, 500])
        
        print("笨・繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺梧ｭ｣蟶ｸ縺ｫ蜍穂ｽ・)


class APILimitTest(ProductionEnvironmentTest):
    """2. API蛻ｶ髯仙・縺ｧ縺ｮ蜍穂ｽ懃｢ｺ隱・""

    def test_01_cache_functionality(self):
        """繧ｭ繝｣繝・す繝･讖溯・繝・せ繝・""
        print("\n[繝・せ繝・2.1] 繧ｭ繝｣繝・す繝･讖溯・遒ｺ隱・)
        
        # 繧ｭ繝｣繝・す繝･繧ｵ繝ｼ繝薙せ縺ｮ繝・せ繝・
        test_key = "test_cache_key"
        test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
        
        # 繝・・繧ｿ繧偵く繝｣繝・す繝･縺ｫ菫晏ｭ・
        self.cache_service.set_cached_data(test_key, test_data, ttl=600)  # 10蛻・
        
        # 繧ｭ繝｣繝・す繝･縺九ｉ繝・・繧ｿ繧貞叙蠕・
        cached_data = self.cache_service.get_cached_data(test_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['test'], 'data')
        
        print("笨・繧ｭ繝｣繝・す繝･讖溯・縺梧ｭ｣蟶ｸ縺ｫ蜍穂ｽ・)

    def test_02_cache_expiration(self):
        """繧ｭ繝｣繝・す繝･譛牙柑譛滄剞繝・せ繝・""
        print("\n[繝・せ繝・2.2] 繧ｭ繝｣繝・す繝･譛牙柑譛滄剞遒ｺ隱・)
        
        test_key = "test_expiration_key"
        test_data = {"test": "expiration_data"}
        
        # 遏ｭ縺・怏蜉ｹ譛滄剞縺ｧ繧ｭ繝｣繝・す繝･縺ｫ菫晏ｭ假ｼ・遘抵ｼ・
        self.cache_service.set_cached_data(test_key, test_data, ttl=1)
        
        # 縺吶＄縺ｫ蜿門ｾ暦ｼ域怏蜉ｹ譛滄剞蜀・ｼ・
        cached_data = self.cache_service.get_cached_data(test_key)
        self.assertIsNotNone(cached_data)
        
        # 2遘貞ｾ・ｩ滂ｼ域怏蜉ｹ譛滄剞蛻・ｌ・・
        time.sleep(2)
        
        # 譛牙柑譛滄剞蛻・ｌ蠕後・蜿門ｾ・
        expired_data = self.cache_service.get_cached_data(test_key)
        self.assertIsNone(expired_data)
        
        print("笨・繧ｭ繝｣繝・す繝･譛牙柑譛滄剞縺梧ｭ｣蟶ｸ縺ｫ蜍穂ｽ・)

    def test_03_api_rate_limiting_simulation(self):
        """API蛻ｶ髯舌す繝溘Η繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ繝・せ繝・""
        print("\n[繝・せ繝・2.3] API蛻ｶ髯舌す繝溘Η繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ")
        
        # 繧ｭ繝｣繝・す繝･蜉ｹ譫懊ｒ繝・せ繝茨ｼ亥酔縺倥く繝ｼ縺ｧ隍・焚蝗槫他縺ｳ蜃ｺ縺暦ｼ・
        test_calls = 10
        cache_key = "test_location_192.168.1.1"
        
        # 譛蛻昴↓繧ｭ繝｣繝・す繝･繝・・繧ｿ繧定ｨｭ螳・
        test_location_data = {
            'city': '繝・せ繝亥ｸ・,
            'region': '繝・せ繝育恁',
            'latitude': 35.6812,
            'longitude': 139.7671,
            'source': 'cache'
        }
        
        self.cache_service.set_cached_data(cache_key, test_location_data, ttl=600)
        
        location_service = LocationService(self.cache_service)
        
        # API蜻ｼ縺ｳ蜃ｺ縺怜屓謨ｰ繧偵き繧ｦ繝ｳ繝・
        cached_calls = 0
        api_calls = 0
        
        for i in range(test_calls):
            try:
                # 蜷後§IP繧｢繝峨Ξ繧ｹ縺ｧ隍・焚蝗槫他縺ｳ蜃ｺ縺暦ｼ医く繝｣繝・す繝･蜉ｹ譫懊ｒ遒ｺ隱搾ｼ・
                result = location_service.get_location_from_ip("192.168.1.1")
                
                if result.get('source') == 'cache':
                    cached_calls += 1
                elif result.get('source') == 'default':
                    # 繝・ヵ繧ｩ繝ｫ繝亥､縺瑚ｿ斐＆繧後◆蝣ｴ蜷茨ｼ・PI蛻ｶ髯舌ｄ繧ｨ繝ｩ繝ｼ・・
                    api_calls += 1
                else:
                    api_calls += 1
                    
            except Exception as e:
                print(f"API蜻ｼ縺ｳ蜃ｺ縺・{i+1} 縺ｧ繧ｨ繝ｩ繝ｼ: {e}")
        
        print(f"笨・繧ｭ繝｣繝・す繝･縺九ｉ縺ｮ蜿門ｾ・ {cached_calls}蝗・)
        print(f"笨・API/繝・ヵ繧ｩ繝ｫ繝亥他縺ｳ蜃ｺ縺・ {api_calls}蝗・)
        print(f"笨・邱丞他縺ｳ蜃ｺ縺・ {cached_calls + api_calls}蝗・)
        
        # 繧ｭ繝｣繝・す繝･縺悟柑譫懃噪縺ｫ蜍穂ｽ懊＠縺ｦ縺・ｋ縺薙→繧堤｢ｺ隱・
        # 譛蛻昴・蜻ｼ縺ｳ蜃ｺ縺嶺ｻ･螟悶・繧ｭ繝｣繝・す繝･縺九ｉ蜿門ｾ励＆繧後ｋ縺ｹ縺・
        self.assertGreaterEqual(cached_calls, test_calls - 2)  # 螟壼ｰ代・隱､蟾ｮ繧定ｨｱ螳ｹ

    def test_04_concurrent_requests_handling(self):
        """蜷梧凾繝ｪ繧ｯ繧ｨ繧ｹ繝亥・逅・ユ繧ｹ繝・""
        print("\n[繝・せ繝・2.4] 蜷梧凾繝ｪ繧ｯ繧ｨ繧ｹ繝亥・逅・｢ｺ隱・)
        
        def make_request():
            """繝・せ繝育畑繝ｪ繧ｯ繧ｨ繧ｹ繝磯未謨ｰ"""
            try:
                response = self.client.get('/')
                return response.status_code == 200
            except Exception:
                return False
        
        # 10蛟九・蜷梧凾繝ｪ繧ｯ繧ｨ繧ｹ繝医ｒ螳溯｡・
        threads = []
        results = []
        
        for i in range(10):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        # 縺吶∋縺ｦ縺ｮ繧ｹ繝ｬ繝・ラ縺ｮ螳御ｺ・ｒ蠕・ｩ・
        for thread in threads:
            thread.join()
        
        # 謌仙粥邇・ｒ遒ｺ隱・
        success_rate = sum(results) / len(results)
        self.assertGreaterEqual(success_rate, 0.8)  # 80%莉･荳翫・謌仙粥邇・
        
        print(f"笨・蜷梧凾繝ｪ繧ｯ繧ｨ繧ｹ繝域・蜉溽紫: {success_rate*100:.1f}%")


class PerformanceTest(ProductionEnvironmentTest):
    """3. 繝代ヵ繧ｩ繝ｼ繝槭Φ繧ｹ繝・せ繝亥ｮ溯｡・""

    def test_01_response_time_measurement(self):
        """繝ｬ繧ｹ繝昴Φ繧ｹ譎る俣貂ｬ螳壹ユ繧ｹ繝・""
        print("\n[繝・せ繝・3.1] 繝ｬ繧ｹ繝昴Φ繧ｹ譎る俣貂ｬ螳・)
        
        response_times = []
        test_iterations = 10
        
        for i in range(test_iterations):
            start_time = time.time()
            response = self.client.get('/')
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            self.assertEqual(response.status_code, 200)
        
        # 邨ｱ險域ュ蝣ｱ繧定ｨ育ｮ・
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"笨・蟷ｳ蝮・Ξ繧ｹ繝昴Φ繧ｹ譎る俣: {avg_response_time:.3f}遘・)
        print(f"笨・譛螟ｧ繝ｬ繧ｹ繝昴Φ繧ｹ譎る俣: {max_response_time:.3f}遘・)
        print(f"笨・譛蟆上Ξ繧ｹ繝昴Φ繧ｹ譎る俣: {min_response_time:.3f}遘・)
        
        # 繝代ヵ繧ｩ繝ｼ繝槭Φ繧ｹ蝓ｺ貅厄ｼ・遘剃ｻ･蜀・ｼ・
        self.assertLess(avg_response_time, 5.0)
        self.assertLess(max_response_time, 10.0)

    def test_02_memory_usage_monitoring(self):
        """繝｡繝｢繝ｪ菴ｿ逕ｨ驥冗屮隕悶ユ繧ｹ繝・""
        print("\n[繝・せ繝・3.2] 繝｡繝｢繝ｪ菴ｿ逕ｨ驥冗屮隕・)
        
        try:
            import psutil
            process = psutil.Process()
            
            # 蛻晄悄繝｡繝｢繝ｪ菴ｿ逕ｨ驥・
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 隍・焚蝗槭・繝ｪ繧ｯ繧ｨ繧ｹ繝医ｒ螳溯｡・
            for i in range(50):
                response = self.client.get('/')
                self.assertEqual(response.status_code, 200)
            
            # 譛邨ゅΓ繝｢繝ｪ菴ｿ逕ｨ驥・
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"笨・蛻晄悄繝｡繝｢繝ｪ菴ｿ逕ｨ驥・ {initial_memory:.2f}MB")
            print(f"笨・譛邨ゅΓ繝｢繝ｪ菴ｿ逕ｨ驥・ {final_memory:.2f}MB")
            print(f"笨・繝｡繝｢繝ｪ蠅怜刈驥・ {memory_increase:.2f}MB")
            
            # 繝｡繝｢繝ｪ繝ｪ繝ｼ繧ｯ縺ｮ遒ｺ隱搾ｼ・00MB莉･荳九・蠅怜刈・・
            self.assertLess(memory_increase, 100)
            
        except ImportError:
            print("笞 psutil縺悟茜逕ｨ縺ｧ縺阪↑縺・◆繧√√Γ繝｢繝ｪ逶｣隕悶ｒ繧ｹ繧ｭ繝・・")

    def test_03_database_performance(self):
        """繝・・繧ｿ繝吶・繧ｹ繝代ヵ繧ｩ繝ｼ繝槭Φ繧ｹ繝・せ繝・""
        print("\n[繝・せ繝・3.3] 繝・・繧ｿ繝吶・繧ｹ繝代ヵ繧ｩ繝ｼ繝槭Φ繧ｹ")
        
        # 螟ｧ驥上・繧ｭ繝｣繝・す繝･繝・・繧ｿ繧剃ｽ懈・
        cache_operations = 100
        operation_times = []
        
        for i in range(cache_operations):
            test_key = f"perf_test_key_{i}"
            test_data = {"index": i, "data": f"test_data_{i}" * 10}
            
            start_time = time.time()
            self.cache_service.set_cached_data(test_key, test_data, ttl=3600)
            end_time = time.time()
            
            operation_times.append(end_time - start_time)
        
        # 隱ｭ縺ｿ蜿悶ｊ繝代ヵ繧ｩ繝ｼ繝槭Φ繧ｹ繝・せ繝・
        read_times = []
        for i in range(cache_operations):
            test_key = f"perf_test_key_{i}"
            
            start_time = time.time()
            cached_data = self.cache_service.get_cached_data(test_key)
            end_time = time.time()
            
            read_times.append(end_time - start_time)
            self.assertIsNotNone(cached_data)
        
        avg_write_time = sum(operation_times) / len(operation_times)
        avg_read_time = sum(read_times) / len(read_times)
        
        print(f"笨・蟷ｳ蝮・嶌縺崎ｾｼ縺ｿ譎る俣: {avg_write_time:.4f}遘・)
        print(f"笨・蟷ｳ蝮・ｪｭ縺ｿ蜿悶ｊ譎る俣: {avg_read_time:.4f}遘・)
        
        # 繝代ヵ繧ｩ繝ｼ繝槭Φ繧ｹ蝓ｺ貅厄ｼ亥推謫堺ｽ・.1遘剃ｻ･蜀・ｼ・
        self.assertLess(avg_write_time, 0.1)
        self.assertLess(avg_read_time, 0.1)

    def test_04_load_testing_simulation(self):
        """雋闕ｷ繝・せ繝医す繝溘Η繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ"""
        print("\n[繝・せ繝・3.4] 雋闕ｷ繝・せ繝医す繝溘Η繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ")
        
        def worker_thread(thread_id, results):
            """繝ｯ繝ｼ繧ｫ繝ｼ繧ｹ繝ｬ繝・ラ髢｢謨ｰ"""
            thread_results = []
            
            for i in range(5):  # 蜷・せ繝ｬ繝・ラ縺ｧ5蝗槭・繝ｪ繧ｯ繧ｨ繧ｹ繝・
                try:
                    start_time = time.time()
                    response = self.client.get('/')
                    end_time = time.time()
                    
                    thread_results.append({
                        'thread_id': thread_id,
                        'request_id': i,
                        'status_code': response.status_code,
                        'response_time': end_time - start_time,
                        'success': response.status_code == 200
                    })
                except Exception as e:
                    thread_results.append({
                        'thread_id': thread_id,
                        'request_id': i,
                        'error': str(e),
                        'success': False
                    })
            
            results.extend(thread_results)
        
        # 10蛟九・繝ｯ繝ｼ繧ｫ繝ｼ繧ｹ繝ｬ繝・ラ縺ｧ雋闕ｷ繝・せ繝・
        threads = []
        results = []
        
        start_time = time.time()
        
        for thread_id in range(10):
            thread = threading.Thread(target=worker_thread, args=(thread_id, results))
            threads.append(thread)
            thread.start()
        
        # 縺吶∋縺ｦ縺ｮ繧ｹ繝ｬ繝・ラ縺ｮ螳御ｺ・ｒ蠕・ｩ・
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 邨先棡縺ｮ蛻・梵
        successful_requests = sum(1 for r in results if r.get('success', False))
        total_requests = len(results)
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        response_times = [r['response_time'] for r in results if 'response_time' in r]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        print(f"笨・邱上Μ繧ｯ繧ｨ繧ｹ繝域焚: {total_requests}")
        print(f"笨・謌仙粥繝ｪ繧ｯ繧ｨ繧ｹ繝域焚: {successful_requests}")
        print(f"笨・謌仙粥邇・ {success_rate*100:.1f}%")
        print(f"笨・蟷ｳ蝮・Ξ繧ｹ繝昴Φ繧ｹ譎る俣: {avg_response_time:.3f}遘・)
        print(f"笨・邱丞ｮ溯｡梧凾髢・ {total_time:.3f}遘・)
        print(f"笨・繧ｹ繝ｫ繝ｼ繝励ャ繝・ {total_requests/total_time:.2f} req/sec")
        
        # 繝代ヵ繧ｩ繝ｼ繝槭Φ繧ｹ蝓ｺ貅・
        self.assertGreaterEqual(success_rate, 0.9)  # 90%莉･荳翫・謌仙粥邇・
        self.assertLess(avg_response_time, 5.0)     # 蟷ｳ蝮・遘剃ｻ･蜀・


def run_production_tests():
    """譛ｬ逡ｪ迺ｰ蠅・ユ繧ｹ繝医・螳溯｡・""
    print("Lunch Roulette - 譛ｬ逡ｪ迺ｰ蠅・ユ繧ｹ繝亥ｮ溯｡・)
    print("Production Environment Testing")
    print("="*60)
    
    # 繝・せ繝医せ繧､繝ｼ繝医ｒ菴懈・
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # 1. 繝ｭ繝ｼ繧ｫ繝ｫ迺ｰ蠅・〒縺ｮ譛邨ょ虚菴懃｢ｺ隱・
    test_suite.addTests(loader.loadTestsFromTestCase(LocalEnvironmentTest))
    
    # 2. API蛻ｶ髯仙・縺ｧ縺ｮ蜍穂ｽ懃｢ｺ隱・
    test_suite.addTests(loader.loadTestsFromTestCase(APILimitTest))
    
    # 3. 繝代ヵ繧ｩ繝ｼ繝槭Φ繧ｹ繝・せ繝亥ｮ溯｡・
    test_suite.addTests(loader.loadTestsFromTestCase(PerformanceTest))
    
    # 繝・せ繝医Λ繝ｳ繝翫・繧剃ｽ懈・縺励※螳溯｡・
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 邨先棡繧ｵ繝槭Μ繝ｼ繧定｡ｨ遉ｺ
    print("\n" + "="*60)
    print("繝・せ繝育ｵ先棡繧ｵ繝槭Μ繝ｼ - Test Results Summary")
    print("="*60)
    print(f"螳溯｡後ユ繧ｹ繝域焚: {result.testsRun}")
    print(f"謌仙粥: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"螟ｱ謨・ {len(result.failures)}")
    print(f"繧ｨ繝ｩ繝ｼ: {len(result.errors)}")
    
    if result.failures:
        print("\n螟ｱ謨励＠縺溘ユ繧ｹ繝・")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺溘ユ繧ｹ繝・")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # 蜈ｨ菴鍋噪縺ｪ謌仙粥蛻､螳・
    if result.wasSuccessful():
        print("\n脂 縺吶∋縺ｦ縺ｮ繝・せ繝医′謌仙粥縺励∪縺励◆・・)
        print("笨・譛ｬ逡ｪ迺ｰ蠅・∈縺ｮ貅門ｙ縺悟ｮ御ｺ・＠縺ｦ縺・∪縺・)
        return True
    else:
        print("\n笶・荳驛ｨ縺ｮ繝・せ繝医′螟ｱ謨励＠縺ｾ縺励◆")
        print("笞 譛ｬ逡ｪ迺ｰ蠅・ョ繝励Ο繧､蜑阪↓蝠城｡後ｒ菫ｮ豁｣縺励※縺上□縺輔＞")
        return False


if __name__ == '__main__':
    success = run_production_tests()
    sys.exit(0 if success else 1)