#!/bin/bash
# テストファイルのインポート修正スクリプト

cd /home/ope/LunchRoulette/tests/unit

# 他のテストファイルのpatch修正
for file in test_*.py; do
    if [[ "$file" != "test_cache_service.py" && "$file" != "test_distance_calculator.py" ]]; then
        echo "Fixing $file..."
        
        # patchの修正
        sed -i 's/@patch("app\./@patch("lunch_roulette.app./g' "$file"
        sed -i 's/@patch("database\./@patch("lunch_roulette.models.database./g' "$file"
        sed -i 's/@patch("cache_service\./@patch("lunch_roulette.services.cache_service./g' "$file"
        sed -i 's/@patch("location_service\./@patch("lunch_roulette.services.location_service./g' "$file"
        sed -i 's/@patch("weather_service\./@patch("lunch_roulette.services.weather_service./g' "$file"
        sed -i 's/@patch("restaurant_service\./@patch("lunch_roulette.services.restaurant_service./g' "$file"
        sed -i 's/@patch("distance_calculator\./@patch("lunch_roulette.utils.distance_calculator./g' "$file"
        sed -i 's/@patch("error_handler\./@patch("lunch_roulette.utils.error_handler./g' "$file"
        
        # with patch文の修正
        sed -i "s/with patch('app\./with patch('lunch_roulette.app./g" "$file"
        sed -i "s/with patch('database\./with patch('lunch_roulette.models.database./g" "$file"
        sed -i "s/with patch('cache_service\./with patch('lunch_roulette.services.cache_service./g" "$file"
        sed -i "s/with patch('location_service\./with patch('lunch_roulette.services.location_service./g" "$file"
        sed -i "s/with patch('weather_service\./with patch('lunch_roulette.services.weather_service./g" "$file"
        sed -i "s/with patch('restaurant_service\./with patch('lunch_roulette.services.restaurant_service./g" "$file"
        sed -i "s/with patch('distance_calculator\./with patch('lunch_roulette.utils.distance_calculator./g" "$file"
        sed -i "s/with patch('error_handler\./with patch('lunch_roulette.utils.error_handler./g" "$file"
        
        # MockやMagicMockの修正（モジュール内の関数参照）
        sed -i 's/patch\.object(app,/patch.object(lunch_roulette.app,/g' "$file"
        sed -i 's/patch\.object(database,/patch.object(lunch_roulette.models.database,/g' "$file"
    fi
done

echo "テストファイルのpatch修正完了"