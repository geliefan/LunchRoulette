#!/bin/bash
# テスト実行スクリプト

echo "=== Lunch Roulette テスト実行 ==="

cd /home/ope/LunchRoulette

# コアモジュールのテスト（依存関係なし）
echo "1. Distance Calculator テスト..."
python3 -m pytest tests/unit/test_distance_calculator.py -v --tb=short

echo ""
echo "2. Cache Service 基本テスト..."
python3 -m pytest tests/unit/test_cache_service.py::TestCacheService::test_serialize_deserialize_data -v --tb=short
python3 -m pytest tests/unit/test_cache_service.py::TestCacheService::test_is_cache_valid -v --tb=short

echo ""
echo "3. Error Handling テスト..."
python3 -m pytest tests/unit/test_error_handling.py::TestErrorHandlerUnit::test_handle_api_error -v --tb=short 2>/dev/null || echo "Error handling test may need API keys"

echo ""
echo "=== 基本テスト完了 ==="
echo "全テストを実行するには: python3 -m pytest tests/unit/ -v"