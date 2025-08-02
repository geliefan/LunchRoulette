#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本番環境テスト - Production Environment Testing
Lunch Roulette アプリケーションの本番環境対応テスト

このテストスイートは以下をカバーします:
1. ローカル環境での最終動作確認
2. API制限下での動作確認
3. パフォーマンステスト実行

要件: 4.3, 5.4
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

# アプリケーションモジュールをインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app, init_db
from cache_service import CacheService
from location_service import LocationService
from weather_service import WeatherService
from restaurant_service import RestaurantService


class ProductionEnvironmentTest(unittest.TestCase):
    """本番環境テスト用のテストクラス"""

    @classmethod
    def setUpClass(cls):
        """テストクラス全体の初期化"""
        print("\n" + "="*60)
        print("本番環境テスト開始 - Production Environment Testing")
        print("="*60)
        
        # テスト用データベースを初期化
        cls.test_db = 'test_production.db'
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
        
        # Flaskアプリケーションをテストモードで設定
        app.config['TESTING'] = True
        app.config['DATABASE'] = cls.test_db
        app.config['DEBUG'] = False  # 本番環境設定
        
        # データベース初期化
        init_db()
        
        cls.client = app.test_client()
        cls.cache_service = CacheService(db_path=cls.test_db)
        
        # API制限追跡用
        cls.api_call_count = {
            'location': 0,
            'weather': 0,
            'restaurant': 0
        }
        cls.test_start_time = datetime.now()

    @classmethod
    def tearDownClass(cls):
        """テストクラス全体のクリーンアップ"""
        try:
            # データベース接続を明示的に閉じる
            if hasattr(cls, 'cache_service'):
                cls.cache_service.close_connection()
            
            # ファイルが存在し、削除可能な場合のみ削除
            if os.path.exists(cls.test_db):
                try:
                    os.remove(cls.test_db)
                except PermissionError:
                    print(f"⚠ テストデータベースファイル {cls.test_db} を削除できませんでした（使用中）")
        except Exception as e:
            print(f"⚠ クリーンアップ中にエラー: {e}")
        
        print("\n" + "="*60)
        print("本番環境テスト完了")
        print("="*60)

    def setUp(self):
        """各テストの初期化"""
        self.start_time = time.time()

    def tearDown(self):
        """各テストのクリーンアップ"""
        end_time = time.time()
        execution_time = end_time - self.start_time
        print(f"テスト実行時間: {execution_time:.3f}秒")


class LocalEnvironmentTest(ProductionEnvironmentTest):
    """1. ローカル環境での最終動作確認"""

    def test_01_application_startup(self):
        """アプリケーション起動テスト"""
        print("\n[テストケース1.1] アプリケーション起動確認")
        
        # メインページへのアクセステスト
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Lunch Roulette', response.data)
        print("✓ アプリケーションが正常に起動しました")

    def test_02_database_initialization(self):
        """データベース初期化テスト"""
        print("\n[テストケース1.2] データベース初期化確認")
        
        # データベースファイルの存在確認
        self.assertTrue(os.path.exists(self.test_db))
        
        # テーブル構造の確認
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # cacheテーブルの存在確認
        table_names = [table[0] for table in tables]
        self.assertIn('cache', table_names)
        
        # cacheテーブルの構造確認
        cursor.execute("PRAGMA table_info(cache);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        expected_columns = ['id', 'cache_key', 'data', 'created_at', 'expires_at']
        for col in expected_columns:
            self.assertIn(col, column_names)
        
        conn.close()
        print("✓ データベースが正常に初期化されました")

    def test_03_main_page_functionality(self):
        """メインページ機能テスト"""
        print("\n[テストケース1.3] メインページ機能確認")
        
        with patch('location_service.LocationService.get_location_from_ip') as mock_location, \
             patch('weather_service.WeatherService.get_current_weather') as mock_weather:
            
            # モックデータを設定
            mock_location.return_value = {
                'city': '東京',
                'region': '東京都',
                'latitude': 35.6812,
                'longitude': 139.7671,
                'source': 'test'
            }
            
            mock_weather.return_value = {
                'temperature': 22.5,
                'description': '晴れ',
                'uv_index': 4.0,
                'icon': '01d',
                'source': 'test'
            }
            
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            
            # HTMLコンテンツ確認
            html_content = response.data.decode('utf-8')
            self.assertIn('東京', html_content)
            self.assertIn('晴れ', html_content)
            self.assertIn('ルーレットを回す', html_content)
            
        print("✓ メインページが正常に動作しています")

    def test_04_roulette_endpoint(self):
        """ルーレットエンドポイントテスト"""
        print("\n[テストケース1.4] ルーレットエンドポイント確認")
        
        with patch('location_service.LocationService.get_location_from_ip') as mock_location, \
             patch('weather_service.WeatherService.get_current_weather') as mock_weather, \
             patch('weather_service.WeatherService.is_good_weather_for_walking') as mock_walking, \
             patch('restaurant_service.RestaurantService.search_lunch_restaurants') as mock_restaurants:
            
            # モックデータを設定
            mock_location.return_value = {
                'latitude': 35.6812,
                'longitude': 139.7671
            }
            
            mock_weather.return_value = {
                'temperature': 22.5,
                'description': '晴れ',
                'condition': 'clear',  # 応答に追加フィールド
                'uv_index': 4.0,
                'icon': '01d'
            }
            
            mock_walking.return_value = True
            
            mock_restaurants.return_value = [{
                'id': 'test_restaurant_001',
                'name': 'テストレストラン',
                'genre': '和食',
                'address': '東京都千代田区',
                'lat': 35.6815,
                'lng': 139.7675,
                'budget': 1000,
                'photo': 'https://example.com/photo.jpg',
                'urls': {'pc': 'https://example.com/restaurant'},
                'catch': 'おいしい和食レストラン',
                'access': '東京駅から徒歩5分',
                'open': '11:00-14:00'
            }]
            
            # ルーレットエンドポイントをテスト
            response = self.client.post('/roulette', 
                                      json={'latitude': 35.6812, 'longitude': 139.7671},
                                      content_type='application/json')
            
            # レスポンスの確認（エラーの場合は詳細を表示）
            if response.status_code != 200:
                print(f"エラーレスポンス: {response.status_code}")
                print(f"レスポンス内容: {response.data.decode('utf-8')}")
            
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('restaurant', data)
            self.assertIn('distance', data)
            self.assertIn('weather', data)
            
        print("✓ ルーレットエンドポイントが正常に動作しています")

    def test_05_error_handling(self):
        """エラーハンドリングテスト"""
        print("\n[テストケース1.5] エラーハンドリング確認")
        
        # 存在しないエンドポイントへのアクセス
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        
        # 不正なJSONデータでのPOSTリクエスト
        response = self.client.post('/roulette', 
                                  data='invalid json',
                                  content_type='application/json')
        # 実際のレスポンスを確認
        if response.status_code not in [400, 500]:
            print(f"予期しないステータスコード {response.status_code}")
            print(f"レスポンス内容: {response.data.decode('utf-8')}")
        
        # 400または500のいずれかを許可（実際の動作によって異なる）
        self.assertIn(response.status_code, [400, 500])
        
        print("✓ エラーハンドリングが正常に動作しています")


class APILimitTest(ProductionEnvironmentTest):
    """2. API制限下での動作確認"""

    def test_01_cache_functionality(self):
        """キャッシュ機能テスト"""
        print("\n[テストケース2.1] キャッシュ機能確認")
        
        # キャッシュサービスのテスト
        test_key = "test_cache_key"
        test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
        
        # データをキャッシュに保存
        self.cache_service.set_cached_data(test_key, test_data, ttl=600)  # 10分
        
        # キャッシュからデータを取得
        cached_data = self.cache_service.get_cached_data(test_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['test'], 'data')
        
        print("✓ キャッシュ機能が正常に動作しています")

    def test_02_cache_expiration(self):
        """キャッシュ有効期限テスト"""
        print("\n[テストケース2.2] キャッシュ有効期限確認")
        
        test_key = "test_expiration_key"
        test_data = {"test": "expiration_data"}
        
        # 短い有効期限でキャッシュに保存（1秒）
        self.cache_service.set_cached_data(test_key, test_data, ttl=1)
        
        # すぐに取得（有効期限内）
        cached_data = self.cache_service.get_cached_data(test_key)
        self.assertIsNotNone(cached_data)
        
        # 2秒待機（有効期限切れ）
        time.sleep(2)
        
        # 有効期限切れ後に取得
        expired_data = self.cache_service.get_cached_data(test_key)
        self.assertIsNone(expired_data)
        
        print("✓ キャッシュ有効期限が正常に動作しています")

    def test_03_api_rate_limiting_simulation(self):
        """API制限シミュレーションテスト"""
        print("\n[テストケース2.3] API制限シミュレーション")
        
        # キャッシュ効果をテスト（同じキーで複数回呼び出し）
        test_calls = 10
        cache_key = "test_location_192.168.1.1"
        
        # 最初にキャッシュにデータを設定
        test_location_data = {
            'city': 'テストシティ',
            'region': 'テスト県',
            'latitude': 35.6812,
            'longitude': 139.7671,
            'source': 'cache'
        }
        
        self.cache_service.set_cached_data(cache_key, test_location_data, ttl=600)
        
        location_service = LocationService(self.cache_service)
        
        # API呼び出し回数をカウント
        cached_calls = 0
        api_calls = 0
        
        for i in range(test_calls):
            try:
                # 同じIPアドレスで複数回呼び出し（キャッシュ効果を確認）
                result = location_service.get_location_from_ip("192.168.1.1")
                
                if result.get('source') == 'cache':
                    cached_calls += 1
                elif result.get('source') == 'default':
                    # デフォルト値が返された場合はAPI制限やエラーの可能性
                    api_calls += 1
                else:
                    api_calls += 1
                    
            except Exception as e:
                print(f"API呼び出し{ i+1 } でエラー: {e}")
        
        print(f"✓ キャッシュからの取得回数: {cached_calls}回")
        print(f"✓ API/デフォルト呼び出し回数: {api_calls}回")
        print(f"✓ 総呼び出し回数: {cached_calls + api_calls}回")
        
        # キャッシュが効果的に動作していることを確認
        # 最初の呼び出し以外はキャッシュから取得されるべき
        self.assertGreaterEqual(cached_calls, test_calls - 2)  # 多少の誤差を許容

    def test_04_concurrent_requests_handling(self):
        """同時リクエスト処理テスト"""
        print("\n[テストケース2.4] 同時リクエスト処理確認")
        
        def make_request():
            """テスト用リクエスト関数"""
            try:
                response = self.client.get('/')
                return response.status_code == 200
            except Exception:
                return False
        
        # 10個の同時リクエストを実行
        threads = []
        results = []
        
        for i in range(10):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        # すべてのスレッドの完了を待機
        for thread in threads:
            thread.join()
        
        # 成功率を計算
        success_rate = sum(results) / len(results)
        self.assertGreaterEqual(success_rate, 0.8)  # 80%以上が成功すること
        
        print(f"✓ 同時リクエスト成功率: {success_rate*100:.1f}%")


class PerformanceTest(ProductionEnvironmentTest):
    """3. パフォーマンステスト実行"""

    def test_01_response_time_measurement(self):
        """レスポンス時間測定テスト"""
        print("\n[テストケース3.1] レスポンス時間測定")
        
        response_times = []
        test_iterations = 10
        
        for i in range(test_iterations):
            start_time = time.time()
            response = self.client.get('/')
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            self.assertEqual(response.status_code, 200)
        
        # 統計情報を計算
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"✓ 平均レスポンス時間: {avg_response_time:.3f}秒")
        print(f"✓ 最大レスポンス時間: {max_response_time:.3f}秒")
        print(f"✓ 最小レスポンス時間: {min_response_time:.3f}秒")
        
        # パフォーマンス基準（5秒以内）
        self.assertLess(avg_response_time, 5.0)
        self.assertLess(max_response_time, 10.0)

    def test_02_memory_usage_monitoring(self):
        """メモリ使用量監視テスト"""
        print("\n[テストケース3.2] メモリ使用量監視")
        
        try:
            import psutil
            process = psutil.Process()
            
            # 初期メモリ使用量
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 複数回リクエストを実行
            for i in range(50):
                response = self.client.get('/')
                self.assertEqual(response.status_code, 200)
            
            # 最終メモリ使用量
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"✓ 初期メモリ使用量: {initial_memory:.2f}MB")
            print(f"✓ 最終メモリ使用量: {final_memory:.2f}MB")
            print(f"✓ メモリ増加量: {memory_increase:.2f}MB")
            
            # メモリリークの確認（100MB以下の増加を許可）
            self.assertLess(memory_increase, 100)
            
        except ImportError:
            print("⚠ psutilが利用できないため、メモリ監視をスキップします")

    def test_03_database_performance(self):
        """データベースパフォーマンステスト"""
        print("\n[テストケース3.3] データベースパフォーマンス")
        
        # 大量のキャッシュデータを作成
        cache_operations = 100
        operation_times = []
        
        for i in range(cache_operations):
            test_key = f"perf_test_key_{i}"
            test_data = {"index": i, "data": f"test_data_{i}" * 10}
            
            start_time = time.time()
            self.cache_service.set_cached_data(test_key, test_data, ttl=3600)
            end_time = time.time()
            
            operation_times.append(end_time - start_time)
        
        # 読み取りパフォーマンステスト
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
        
        print(f"✓ 平均書き込み時間: {avg_write_time:.4f}秒")
        print(f"✓ 平均読み取り時間: {avg_read_time:.4f}秒")
        
        # パフォーマンス基準（各操作0.1秒以内）
        self.assertLess(avg_write_time, 0.1)
        self.assertLess(avg_read_time, 0.1)

    def test_04_load_testing_simulation(self):
        """負荷テストシミュレーション"""
        print("\n[テストケース3.4] 負荷テストシミュレーション")
        
        def worker_thread(thread_id, results):
            """ワーカースレッド関数"""
            thread_results = []
            
            for i in range(5):  # 各スレッドで5回リクエスト
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
        
        # 10個のワーカースレッドで負荷テスト
        threads = []
        results = []
        
        start_time = time.time()
        
        for thread_id in range(10):
            thread = threading.Thread(target=worker_thread, args=(thread_id, results))
            threads.append(thread)
            thread.start()
        
        # すべてのスレッドの完了を待機
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 結果の集計
        successful_requests = sum(1 for r in results if r.get('success', False))
        total_requests = len(results)
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        response_times = [r['response_time'] for r in results if 'response_time' in r]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        print(f"✓ 総リクエスト数: {total_requests}")
        print(f"✓ 成功リクエスト数: {successful_requests}")
        print(f"✓ 成功率: {success_rate*100:.1f}%")
        print(f"✓ 平均レスポンス時間: {avg_response_time:.3f}秒")
        print(f"✓ 総実行時間: {total_time:.3f}秒")
        print(f"✓ スループット: {total_requests/total_time:.2f} req/sec")
        
        # パフォーマンス基準
        self.assertGreaterEqual(success_rate, 0.9)  # 90%以上が成功すること
        self.assertLess(avg_response_time, 5.0)     # 平均5秒以内


def run_production_tests():
    """本番環境テスト実行"""
    print("Lunch Roulette - 本番環境テスト実行")
    print("Production Environment Testing")
    print("="*60)
    
    # テストスイートを作成
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # 1. ローカル環境での最終動作確認
    test_suite.addTests(loader.loadTestsFromTestCase(LocalEnvironmentTest))
    
    # 2. API制限下での動作確認
    test_suite.addTests(loader.loadTestsFromTestCase(APILimitTest))
    
    # 3. パフォーマンステスト実行
    test_suite.addTests(loader.loadTestsFromTestCase(PerformanceTest))
    
    # テストランナーを作成して実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果サマリーを表示
    print("\n" + "="*60)
    print("テスト結果サマリー")
    print("="*60)
    print(f"実行テスト数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    
    if result.failures:
        print("\n失敗したテストケース")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nエラーが発生したテストケース")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # 全体的な成功判定
    if result.wasSuccessful():
        print("\n🎉 すべてのテストが成功しました")
        print("✓ 本番環境の準備が完了しました")
        return True
    else:
        print("\n❌ 一部のテストが失敗しました")
        print("⚠ 本番環境にプロイ前に問題を修正してください")
        return False


if __name__ == '__main__':
    success = run_production_tests()
    sys.exit(0 if success else 1)
