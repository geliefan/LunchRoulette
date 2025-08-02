#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask 繧ｨ繝ｳ繝峨・繧､繝ｳ繝医・邁｡蜊倥↑繝・せ繝・
Task 5縺ｮ螳溯｣・ｒ讀懆ｨｼ縺吶ｋ
"""


from app import app
import sys
import os

# 繝励Ο繧ｸ繧ｧ繧ｯ繝医Ν繝ｼ繝医ｒ繝代せ縺ｫ霑ｽ蜉
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_main_page_endpoint():
    """繝｡繧､繝ｳ繝壹・繧ｸ繧ｨ繝ｳ繝峨・繧､繝ｳ繝茨ｼ・ET /・峨・繝・せ繝・""
    print("=" * 50)
    print("繝｡繧､繝ｳ繝壹・繧ｸ繧ｨ繝ｳ繝峨・繧､繝ｳ繝茨ｼ・ET /・峨・繝・せ繝・)
    print("=" * 50)

    with app.test_client() as client:
        try:
            response = client.get('/')
            print(f"繧ｹ繝・・繧ｿ繧ｹ繧ｳ繝ｼ繝・ {response.status_code}")
            print(f"Content-Type: {response.content_type}")

            if response.status_code == 200:
                print("笨・繝｡繧､繝ｳ繝壹・繧ｸ繧ｨ繝ｳ繝峨・繧､繝ｳ繝医′豁｣蟶ｸ縺ｫ蜍穂ｽ懊＠縺ｦ縺・∪縺・)
                # HTML繝ｬ繧ｹ繝昴Φ繧ｹ縺ｮ蝓ｺ譛ｬ逧・↑遒ｺ隱・
                if b'html' in response.data.lower():
                    print("笨・HTML繝ｬ繧ｹ繝昴Φ繧ｹ縺瑚ｿ斐＆繧後※縺・∪縺・)
                else:
                    print("笞 HTML繝ｬ繧ｹ繝昴Φ繧ｹ縺ｧ縺ｯ縺ｪ縺・庄閭ｽ諤ｧ縺後≠繧翫∪縺・)
            else:
                print(f"笨・繧ｨ繝ｩ繝ｼ: 繧ｹ繝・・繧ｿ繧ｹ繧ｳ繝ｼ繝・{response.status_code}")
                print(f"繝ｬ繧ｹ繝昴Φ繧ｹ: {response.data.decode('utf-8')[:200]}...")

        except Exception as e:
            print(f"笨・繝・せ繝亥ｮ溯｡後お繝ｩ繝ｼ: {e}")


def test_roulette_endpoint():
    """繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝茨ｼ・OST /roulette・峨・繝・せ繝・""
    print("\n" + "=" * 50)
    print("繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝茨ｼ・OST /roulette・峨・繝・せ繝・)
    print("=" * 50)

    with app.test_client() as client:
        try:
            # 菴咲ｽｮ諠・ｱ縺ｪ縺励〒縺ｮ繝・せ繝・
            print("\n1. 菴咲ｽｮ諠・ｱ縺ｪ縺励〒縺ｮ繝・せ繝・")
            response = client.post('/roulette',
                                   json={},
                                   content_type='application/json')

            print(f"繧ｹ繝・・繧ｿ繧ｹ繧ｳ繝ｼ繝・ {response.status_code}")

            if response.status_code in [200, 400, 500]:
                try:
                    data = response.get_json()
                    print("繝ｬ繧ｹ繝昴Φ繧ｹ蠖｢蠑・ JSON")

                    if data.get('success'):
                        print("笨・謌仙粥繝ｬ繧ｹ繝昴Φ繧ｹ")
                        if 'restaurant' in data:
                            print(f"  繝ｬ繧ｹ繝医Λ繝ｳ蜷・ {data['restaurant'].get('name', 'N/A')}")
                            print(f"  霍晞屬: {data.get('distance', {}).get('distance_display', 'N/A')}")
                    elif data.get('error') or not data.get('success'):
                        print("笞 繧ｨ繝ｩ繝ｼ繝ｬ繧ｹ繝昴Φ繧ｹ・域ｭ｣蟶ｸ縺ｪ蜍穂ｽ懶ｼ・)
                        print(f"  繝｡繝・そ繝ｼ繧ｸ: {data.get('message', 'N/A')}")

                except Exception as e:
                    print(f"笨・JSON繝ｬ繧ｹ繝昴Φ繧ｹ隗｣譫舌お繝ｩ繝ｼ: {e}")
                    print(f"繝ｬ繧ｹ繝昴Φ繧ｹ: {response.data.decode('utf-8')[:200]}...")
            else:
                print(f"笨・莠域悄縺励↑縺・せ繝・・繧ｿ繧ｹ繧ｳ繝ｼ繝・ {response.status_code}")

            # 菴咲ｽｮ諠・ｱ縺ゅｊ縺ｧ縺ｮ繝・せ繝・
            print("\n2. 菴咲ｽｮ諠・ｱ縺ゅｊ縺ｧ縺ｮ繝・せ繝・")
            test_data = {
                'latitude': 35.6812,  # 譚ｱ莠ｬ鬧・
                'longitude': 139.7671
            }

            response = client.post('/roulette',
                                   json=test_data,
                                   content_type='application/json')

            print(f"繧ｹ繝・・繧ｿ繧ｹ繧ｳ繝ｼ繝・ {response.status_code}")

            if response.status_code in [200, 400, 500]:
                try:
                    data = response.get_json()
                    print("繝ｬ繧ｹ繝昴Φ繧ｹ蠖｢蠑・ JSON")

                    if data.get('success'):
                        print("笨・謌仙粥繝ｬ繧ｹ繝昴Φ繧ｹ")
                        if 'restaurant' in data:
                            print(f"  繝ｬ繧ｹ繝医Λ繝ｳ蜷・ {data['restaurant'].get('name', 'N/A')}")
                            print(f"  繧ｸ繝｣繝ｳ繝ｫ: {data['restaurant'].get('genre', 'N/A')}")
                            print(f"  霍晞屬: {data.get('distance', {}).get('distance_display', 'N/A')}")
                            print(f"  蠕呈ｭｩ譎る俣: {data.get('distance', {}).get('time_display', 'N/A')}")
                    elif data.get('error') or not data.get('success'):
                        print("笞 繧ｨ繝ｩ繝ｼ繝ｬ繧ｹ繝昴Φ繧ｹ")
                        print(f"  繝｡繝・そ繝ｼ繧ｸ: {data.get('message', 'N/A')}")
                        # API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺・↑縺・ｴ蜷医・豁｣蟶ｸ縺ｪ蜍穂ｽ・
                        if 'API繧ｭ繝ｼ' in data.get('message', '') or '繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ' in data.get('message', ''):
                            print("  ・・PI繧ｭ繝ｼ譛ｪ險ｭ螳壹∪縺溘・繝ｬ繧ｹ繝医Λ繝ｳ譛ｪ逋ｺ隕九・縺溘ａ豁｣蟶ｸ・・)

                except Exception as e:
                    print(f"笨・JSON繝ｬ繧ｹ繝昴Φ繧ｹ隗｣譫舌お繝ｩ繝ｼ: {e}")
                    print(f"繝ｬ繧ｹ繝昴Φ繧ｹ: {response.data.decode('utf-8')[:200]}...")
            else:
                print(f"笨・莠域悄縺励↑縺・せ繝・・繧ｿ繧ｹ繧ｳ繝ｼ繝・ {response.status_code}")

        except Exception as e:
            print(f"笨・繝・せ繝亥ｮ溯｡後お繝ｩ繝ｼ: {e}")


def test_error_handlers():
    """繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ縺ｮ繝・せ繝・""
    print("\n" + "=" * 50)
    print("繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ縺ｮ繝・せ繝・)
    print("=" * 50)

    with app.test_client() as client:
        try:
            # 404繧ｨ繝ｩ繝ｼ繝・せ繝・
            print("\n1. 404繧ｨ繝ｩ繝ｼ繝・せ繝・")
            response = client.get('/nonexistent-page')
            print(f"繧ｹ繝・・繧ｿ繧ｹ繧ｳ繝ｼ繝・ {response.status_code}")

            if response.status_code == 404:
                print("笨・404繧ｨ繝ｩ繝ｼ繝上Φ繝峨Λ繝ｼ縺悟虚菴懊＠縺ｦ縺・∪縺・)
                try:
                    data = response.get_json()
                    if data and data.get('error'):
                        print(f"  繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ: {data.get('message', 'N/A')}")
                except BaseException:
                    print("  繝ｬ繧ｹ繝昴Φ繧ｹ蠖｢蠑・ HTML")
            else:
                print(f"笨・莠域悄縺励↑縺・せ繝・・繧ｿ繧ｹ繧ｳ繝ｼ繝・ {response.status_code}")

        except Exception as e:
            print(f"笨・繝・せ繝亥ｮ溯｡後お繝ｩ繝ｼ: {e}")


if __name__ == '__main__':
    print("Flask 繧ｨ繝ｳ繝峨・繧､繝ｳ繝医ユ繧ｹ繝磯幕蟋・)
    print("Task 5: Flask繝ｫ繝ｼ繝・ぅ繝ｳ繧ｰ縺ｨ繧ｨ繝ｳ繝峨・繧､繝ｳ繝医・螳溯｣・- 讀懆ｨｼ")

    # 繝・せ繝亥ｮ溯｡・
    test_main_page_endpoint()
    test_roulette_endpoint()
    test_error_handlers()

    print("\n" + "=" * 50)
    print("繝・せ繝亥ｮ御ｺ・)
    print("=" * 50)
    print("\n豕ｨ諢・")
    print("- API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺・↑縺・ｴ蜷医∽ｸ驛ｨ縺ｮ讖溯・縺ｯ蛻ｶ髯舌＆繧後∪縺・)
    print("- 螳滄圀縺ｮAPI蜻ｼ縺ｳ蜃ｺ縺励・螟夜Κ繧ｵ繝ｼ繝薙せ縺ｮ蜿ｯ逕ｨ諤ｧ縺ｫ萓晏ｭ倥＠縺ｾ縺・)
    print("- 繧ｭ繝｣繝・す繝･讖溯・縺ｫ繧医ｊ縲・蝗樒岼莉･髯阪・繝・せ繝医・鬮倬溷喧縺輔ｌ縺ｾ縺・)
