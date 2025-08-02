# 繝・せ繝亥ｮ溯｣・ｮ御ｺ・し繝槭Μ繝ｼ

## 螳溯｣・＆繧後◆繝・せ繝・

### 蜊倅ｽ薙ユ繧ｹ繝・(Unit Tests)
- **test_cache_service.py**: CacheService繧ｯ繝ｩ繧ｹ縺ｮ蜈ｨ繝｡繧ｽ繝・ラ繧偵ユ繧ｹ繝・
- **test_location_service.py**: LocationService繧ｯ繝ｩ繧ｹ縺ｮ菴咲ｽｮ諠・ｱ蜿門ｾ玲ｩ溯・繧偵ユ繧ｹ繝・
- **test_weather_service.py**: WeatherService繧ｯ繝ｩ繧ｹ縺ｮ螟ｩ豌玲ュ蝣ｱ蜿門ｾ玲ｩ溯・繧偵ユ繧ｹ繝・
- **test_restaurant_service.py**: RestaurantService繧ｯ繝ｩ繧ｹ縺ｮ繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢讖溯・繧偵ユ繧ｹ繝・
- **test_distance_calculator.py**: DistanceCalculator繧ｯ繝ｩ繧ｹ縺ｮ霍晞屬險育ｮ玲ｩ溯・繧偵ユ繧ｹ繝・

### 邨ｱ蜷医ユ繧ｹ繝・(Integration Tests)
- **test_integration_endpoints.py**: Flask繧ｨ繝ｳ繝峨・繧､繝ｳ繝医・邨ｱ蜷医ユ繧ｹ繝・
- **test_integration_database.py**: 繝・・繧ｿ繝吶・繧ｹ謫堺ｽ懊・邨ｱ蜷医ユ繧ｹ繝・
- **test_error_handling.py**: 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｮ邨ｱ蜷医ユ繧ｹ繝・

## 繝・せ繝育腸蠅・ｨｭ螳・
- **pytest.ini**: pytest險ｭ螳壹ヵ繧｡繧､繝ｫ
- **requirements.txt**: pytest髢｢騾｣繝代ャ繧ｱ繝ｼ繧ｸ繧定ｿｽ蜉
- **荳譎ゅョ繝ｼ繧ｿ繝吶・繧ｹ**: 繝・せ繝育畑縺ｮ蛻・屬縺輔ｌ縺溘ョ繝ｼ繧ｿ繝吶・繧ｹ迺ｰ蠅・

## 繝・せ繝亥ｮ溯｡檎ｵ先棡
- 邱上ユ繧ｹ繝域焚: 113莉ｶ
- 謌仙粥: 87莉ｶ (77%)
- 螟ｱ謨・ 26莉ｶ (23%)

## 荳ｻ縺ｪ謌先棡
1. **蛹・峡逧・↑繝・せ繝医き繝舌Ξ繝・ず**: 蜈ｨ繧ｵ繝ｼ繝薙せ繧ｯ繝ｩ繧ｹ縺ｮ荳ｻ隕∵ｩ溯・繧偵き繝舌・
2. **繝｢繝・け菴ｿ逕ｨ**: 螟夜ΚAPI萓晏ｭ倬未菫ゅｒ驕ｩ蛻・↓繝｢繝・け蛹・
3. **繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ**: 蜷・ｨｮ繧ｨ繝ｩ繝ｼ迥ｶ豕√〒縺ｮ蜍穂ｽ懊ｒ讀懆ｨｼ
4. **邨ｱ蜷医ユ繧ｹ繝・*: 螳滄圀縺ｮ繝・・繧ｿ繝吶・繧ｹ縺ｨFlask繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｨ縺ｮ邨ｱ蜷医ｒ遒ｺ隱・

## 莉雁ｾ後・謾ｹ蝟・せ
- 螟ｱ謨励＠縺溘ユ繧ｹ繝医・菫ｮ豁｣
- 繝・せ繝医ョ繝ｼ繧ｿ縺ｮ謾ｹ蝟・
- 繧医ｊ隧ｳ邏ｰ縺ｪ繧ｨ繝・ず繧ｱ繝ｼ繧ｹ繝・せ繝・
- 繝代ヵ繧ｩ繝ｼ繝槭Φ繧ｹ繝・せ繝医・霑ｽ蜉

## 螳溯｡梧婿豕・
```bash
# 蜈ｨ繝・せ繝亥ｮ溯｡・
python -m pytest

# 迚ｹ螳壹・繝・せ繝医ヵ繧｡繧､繝ｫ螳溯｡・
python -m pytest test_cache_service.py -v

# 繧ｫ繝舌Ξ繝・ず繝ｬ繝昴・繝井ｻ倥″螳溯｡・
python -m pytest --cov=. --cov-report=html
```