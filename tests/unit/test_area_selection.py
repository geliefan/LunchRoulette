"""
エリア選択機能のユニットテスト

issue#10の実装に対するテスト
- /api/areasエンドポイント
- エリアモードでのレストラン検索
- middle_areaパラメータの処理
"""

import pytest
import json
from pathlib import Path


def test_areas_endpoint_success(client):
    """
    /api/areasエンドポイントが正常にエリアリストを返すことを確認
    """
    response = client.get('/api/areas')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['success'] is True
    assert 'areas' in data
    assert isinstance(data['areas'], list)
    assert len(data['areas']) > 0
    
    # 各エリアにcodeとnameが含まれることを確認
    for area in data['areas']:
        assert 'code' in area
        assert 'name' in area
        assert isinstance(area['code'], str)
        assert isinstance(area['name'], str)


def test_areas_endpoint_contains_tokyo_areas(client):
    """
    /api/areasが東京の主要エリアを含むことを確認
    """
    response = client.get('/api/areas')
    data = response.get_json()
    
    area_codes = [area['code'] for area in data['areas']]
    area_names = [area['name'] for area in data['areas']]
    
    # 新宿、渋谷、東京などの主要エリアが含まれることを確認
    assert 'Y005' in area_codes  # 新宿
    assert 'Y010' in area_codes  # 渋谷
    assert 'Y030' in area_codes  # 東京・丸の内
    
    assert '新宿・代々木' in area_names
    assert '渋谷・恵比寿・代官山' in area_names


def test_roulette_with_area_mode(client, mocker):
    """
    エリアモードでのルーレット実行が正常に動作することを確認
    """
    # RestaurantServiceのモック
    mock_restaurants = [
        {
            'id': 'test001',
            'name': 'テストレストラン新宿',
            'genre': '和食',
            'address': '東京都新宿区',
            'display_info': {
                'budget_display': '〜1000円',
                'photo_url': 'http://example.com/photo.jpg',
                'hotpepper_url': 'http://example.com',
                'map_url': 'http://maps.example.com',
                'summary': 'テスト店舗',
                'access_display': '新宿駅徒歩5分',
                'hours_display': '11:00〜14:00'
            }
        }
    ]
    
    mocker.patch(
        'lunch_roulette.services.restaurant_service.RestaurantService.search_restaurants',
        return_value=mock_restaurants
    )
    
    # エリアモードでのリクエスト
    request_data = {
        'location_mode': 'area',
        'middle_area_code': 'Y005',  # 新宿
        'budget_code': 'B010',
        'genre_code': '',
        'lunch': 1
    }
    
    response = client.post(
        '/roulette',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['success'] is True
    assert 'restaurant' in data
    assert data['restaurant']['name'] == 'テストレストラン新宿'
    
    # エリアモードでは距離情報が含まれないことを確認
    assert 'distance' not in data
    
    # エリアモードでは天気情報が含まれないことを確認
    assert 'weather' not in data


def test_roulette_with_area_mode_missing_area_code(client):
    """
    エリアモードでmiddle_area_codeが指定されていない場合のエラーハンドリング
    """
    request_data = {
        'location_mode': 'area',
        # middle_area_code が未指定
        'budget_code': 'B010',
        'lunch': 1
    }
    
    response = client.post(
        '/roulette',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert data['success'] is False
    # エラーメッセージに「エリア」が含まれることを確認
    assert 'エリア' in data['message']


def test_roulette_current_mode_still_works(client, mocker):
    """
    現在地モードが引き続き動作することを確認（後方互換性）
    """
    # モックを設定
    mock_restaurants = [
        {
            'id': 'test002',
            'name': 'テストレストラン',
            'genre': 'イタリアン',
            'address': '東京都渋谷区',
            'display_info': {
                'budget_display': '〜1500円',
                'photo_url': 'http://example.com/photo.jpg',
                'hotpepper_url': 'http://example.com',
                'map_url': 'http://maps.example.com',
                'summary': 'テスト店舗',
                'access_display': '渋谷駅徒歩3分',
                'hours_display': '11:00〜15:00'
            },
            'distance_info': {
                'distance_km': 0.5,
                'distance_display': '500m',
                'walking_time_minutes': 6,
                'time_display': '徒歩約6分'
            }
        }
    ]
    
    mocker.patch(
        'lunch_roulette.services.restaurant_service.RestaurantService.search_restaurants',
        return_value=mock_restaurants
    )
    
    mocker.patch(
        'lunch_roulette.services.weather_service.WeatherService.get_current_weather',
        return_value={
            'description': '晴れ',
            'temperature': 20.0,
            'uv_index': 5.0,
            'icon': 'sunny'
        }
    )
    
    mocker.patch(
        'lunch_roulette.services.weather_service.WeatherService.is_good_weather_for_walking',
        return_value=True
    )
    
    mocker.patch(
        'lunch_roulette.utils.restaurant_selector.RestaurantSelector.select_random_restaurant',
        return_value=mock_restaurants[0]
    )
    
    # 現在地モードでのリクエスト
    request_data = {
        'location_mode': 'current',
        'latitude': 35.6812,
        'longitude': 139.7671,
        'max_walking_time_min': 10,
        'budget_code': 'B011',
        'lunch': 1
    }
    
    response = client.post(
        '/roulette',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['success'] is True
    assert 'restaurant' in data
    assert 'distance' in data  # 現在地モードでは距離情報が含まれる
    assert 'weather' in data   # 現在地モードでは天気情報が含まれる
    assert data['distance']['distance_km'] == 0.5


def test_restaurant_service_search_with_middle_area(mocker):
    """
    RestaurantService.search_restaurants()がmiddle_areaパラメータを正しく処理することを確認
    
    このテストはHot Pepper API呼び出しをモックして、middle_areaパラメータが
    正しく渡されることを確認します。
    """
    # Hot Pepper APIのレスポンスをモック
    mock_api_response = {
        'results': {
            'shop': [
                {
                    'id': 'test001',
                    'name': 'テスト店舗',
                    'genre': {'name': '和食'},
                    'address': '東京都新宿区',
                    'lat': 35.6895,
                    'lng': 139.6917,
                    'budget': {'average': '1000円'},
                    'urls': {'pc': 'http://example.com'},
                    'photo': {'mobile': {'l': 'http://example.com/photo.jpg'}},
                    'open': '11:00-14:00',
                    'access': '新宿駅徒歩5分',
                    'catch': 'テストキャッチコピー'
                }
            ]
        }
    }
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response
    
    mock_get = mocker.patch('requests.get', return_value=mock_response)
    
    # RestaurantServiceインスタンスを作成（実際のインスタンス）
    from lunch_roulette.services.restaurant_service import RestaurantService
    from lunch_roulette.services.cache_service import CacheService
    
    cache_service = CacheService(':memory:')
    service = RestaurantService(api_key='test_key', cache_service=cache_service)
    
    # middle_areaパラメータでレストラン検索
    restaurants = service.search_restaurants(
        middle_area='Y005',  # 新宿
        budget_code='B010',
        lunch=1
    )
    
    # 結果の検証
    assert len(restaurants) > 0
    assert restaurants[0]['name'] == 'テスト店舗'
    
    # APIが正しいパラメータで呼ばれたことを確認
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    params = call_args[1]['params']
    
    # middle_areaがパラメータに含まれることを確認
    assert 'middle_area' in params
    assert params['middle_area'] == 'Y005'
    
    # lat/lonがパラメータに含まれないことを確認（エリア指定の場合）
    assert 'lat' not in params
    assert 'lng' not in params
