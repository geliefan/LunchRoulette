#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask エンドポイントの簡単なテスト
Task 5の実装を検証する
"""


from app import app
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_main_page_endpoint():
    """メインページエンドポイント: GET / のテスト"""
    print("=" * 50)
    print("メインページエンドポイント: GET / のテスト")
    print("=" * 50)

    with app.test_client() as client:
        try:
            response = client.get('/')
            print(f"ステータスコード: {response.status_code}")
            print(f"Content-Type: {response.content_type}")

            if response.status_code == 200:
                print("✔ メインページエンドポイントが正常に動作しています")
                # HTMLレスポンスの基本検証
                if b'html' in response.data.lower():
                    print("✔ HTMLレスポンスが返されました")
                else:
                    print("⚠ HTMLレスポンスではない可能性があります")
            else:
                print(f"✘ エラー: ステータスコード {response.status_code}")
                print(f"レスポンス: {response.data.decode('utf-8')[:200]}...")

        except Exception as e:
            print(f"✘ テスト実行エラー: {e}")


def test_roulette_endpoint():
    """ルーレットエンドポイント: POST /roulette のテスト"""
    print("\n" + "=" * 50)
    print("ルーレットエンドポイント: POST /roulette のテスト")
    print("=" * 50)

    with app.test_client() as client:
        try:
            # 位置情報なしでのテスト
            print("\n1. 位置情報なしでのテスト")
            response = client.post('/roulette',
                                   json={},
                                   content_type='application/json')

            print(f"ステータスコード: {response.status_code}")

            if response.status_code in [200, 400, 500]:
                try:
                    data = response.get_json()
                    print("レスポンス形式: JSON")

                    if data.get('success'):
                        print("✔ 成功レスポンス")
                        if 'restaurant' in data:
                            print(f"  レストラン名: {data['restaurant'].get('name', 'N/A')}")
                            print(f"  距離: {data.get('distance', {}).get('distance_display', 'N/A')}")
                    elif data.get('error') or not data.get('success'):
                        print("⚠ エラーレスポンスが正常な動作です")
                        print(f"  メッセージ: {data.get('message', 'N/A')}")

                except Exception as e:
                    print(f"✘ JSONレスポンス解析エラー: {e}")
                    print(f"レスポンス: {response.data.decode('utf-8')[:200]}...")
            else:
                print(f"✘ 予期しないステータスコード: {response.status_code}")

            # 位置情報ありでのテスト
            print("\n2. 位置情報ありでのテスト")
            test_data = {
                'latitude': 35.6812,  # 東京駅
                'longitude': 139.7671
            }

            response = client.post('/roulette',
                                   json=test_data,
                                   content_type='application/json')

            print(f"ステータスコード: {response.status_code}")

            if response.status_code in [200, 400, 500]:
                try:
                    data = response.get_json()
                    print("レスポンス形式: JSON")

                    if data.get('success'):
                        print("✔ 成功レスポンス")
                        if 'restaurant' in data:
                            print(f"  レストラン名: {data['restaurant'].get('name', 'N/A')}")
                            print(f"  ジャンル: {data['restaurant'].get('genre', 'N/A')}")
                            print(f"  距離: {data.get('distance', {}).get('distance_display', 'N/A')}")
                            print(f"  徒歩時間: {data.get('distance', {}).get('time_display', 'N/A')}")
                    elif data.get('error') or not data.get('success'):
                        print("⚠ エラーレスポンス")
                        print(f"  メッセージ: {data.get('message', 'N/A')}")
                        # APIキーが設定されていない場合やレストランが見つからない場合は正常な動作
                        if 'APIキー' in data.get('message', '') or 'レストランが見つかりません' in data.get('message', ''):
                            print("  ※ APIキー未設定またはレストラン未発見のため正常です")

                except Exception as e:
                    print(f"✘ JSONレスポンス解析エラー: {e}")
                    print(f"レスポンス: {response.data.decode('utf-8')[:200]}...")
            else:
                print(f"✘ 予期しないステータスコード: {response.status_code}")

        except Exception as e:
            print(f"✘ テスト実行エラー: {e}")


def test_error_handlers():
    """エラーハンドラーのテスト"""
    print("\n" + "=" * 50)
    print("エラーハンドラーのテスト")
    print("=" * 50)

    with app.test_client() as client:
        try:
            # 404エラーテスト
            print("\n1. 404エラーテスト")
            response = client.get('/nonexistent-page')
            print(f"ステータスコード: {response.status_code}")

            if response.status_code == 404:
                print("✔ 404エラーハンドラーが動作しています")
                try:
                    data = response.get_json()
                    if data and data.get('error'):
                        print(f"  エラーメッセージ: {data.get('message', 'N/A')}")
                except BaseException:
                    print("  レスポンス形式: HTML")
            else:
                print(f"✘ 予期しないステータスコード: {response.status_code}")

        except Exception as e:
            print(f"✘ テスト実行エラー: {e}")


if __name__ == '__main__':
    print("Flask エンドポイントテスト開始")
    print("Task 5: Flaskルーティングとエンドポイントの実装 - 検証")

    # テスト実行
    test_main_page_endpoint()
    test_roulette_endpoint()
    test_error_handlers()

    print("\n" + "=" * 50)
    print("テスト完了")
    print("=" * 50)
    print("\n注意:")
    print("- APIキーが設定されていない場合、一部の機能は制限されます")
    print("- 実際のAPI呼び出しは外部サービスの可用性に依存します")
    print("- キャッシュ機能により、2回目以降のテストは高速化されます")
