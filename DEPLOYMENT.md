# PythonAnywhere 繝・・繝ｭ繧､繝｡繝ｳ繝域焔鬆・

## 讎りｦ・

縺薙・繝峨く繝･繝｡繝ｳ繝医・縲´unch Roulette繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧単ythonAnywhere辟｡譁吶・繝ｩ繝ｳ縺ｫ繝・・繝ｭ繧､縺吶ｋ縺溘ａ縺ｮ隧ｳ邏ｰ縺ｪ謇矩・ｒ隱ｬ譏弱＠縺ｾ縺吶・

## 蜑肴署譚｡莉ｶ

- PythonAnywhere繧｢繧ｫ繧ｦ繝ｳ繝茨ｼ育┌譁吶・繝ｩ繝ｳ・・
- OpenWeatherMap API繧ｭ繝ｼ
- Hot Pepper Gourmet API繧ｭ繝ｼ
- Git繝ｪ繝昴ず繝医Μ・・itHub縲；itLab遲会ｼ・

## 1. PythonAnywhere縺ｧ縺ｮ繝励Ο繧ｸ繧ｧ繧ｯ繝医そ繝・ヨ繧｢繝・・

### 1.1 繝輔ぃ繧､繝ｫ縺ｮ繧｢繝・・繝ｭ繝ｼ繝・

1. PythonAnywhere縺ｮDashboard縺ｫ繝ｭ繧ｰ繧､繝ｳ
2. "Files" 繧ｿ繝悶ｒ髢九￥
3. 莉･荳九・縺・★繧後°縺ｮ譁ｹ豕輔〒繝励Ο繧ｸ繧ｧ繧ｯ繝医ｒ繧｢繝・・繝ｭ繝ｼ繝会ｼ・

**譁ｹ豕柊: Git繧ｯ繝ｭ繝ｼ繝ｳ・域耳螂ｨ・・*
```bash
# Bash繧ｳ繝ｳ繧ｽ繝ｼ繝ｫ縺ｧ螳溯｡・
cd ~
git clone https://github.com/yourusername/lunch-roulette.git
cd lunch-roulette
```

**譁ｹ豕稗: 繝輔ぃ繧､繝ｫ逶ｴ謗･繧｢繝・・繝ｭ繝ｼ繝・*
- 繝励Ο繧ｸ繧ｧ繧ｯ繝医ヵ繧｡繧､繝ｫ繧呈焔蜍輔〒繧｢繝・・繝ｭ繝ｼ繝・
- 繝・ぅ繝ｬ繧ｯ繝医Μ讒矩繧堤ｶｭ謖・

### 1.2 莉ｮ諠ｳ迺ｰ蠅・・菴懈・

```bash
# Bash繧ｳ繝ｳ繧ｽ繝ｼ繝ｫ縺ｧ螳溯｡・
cd ~/lunch-roulette
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. 迺ｰ蠅・､画焚縺ｮ險ｭ螳・

### 2.1 蠢・育腸蠅・､画焚

PythonAnywhere縺ｮWeb繧ｿ繝悶〒莉･荳九・迺ｰ蠅・､画焚繧定ｨｭ螳壹＠縺ｦ縺上□縺輔＞・・

| 螟画焚蜷・| 隱ｬ譏・| 萓・|
|--------|------|-----|
| `SECRET_KEY` | Flask繧ｻ繝・す繝ｧ繝ｳ證怜捷蛹悶く繝ｼ | `your-secret-key-here-change-in-production` |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API繧ｭ繝ｼ | `abcd1234efgh5678ijkl9012mnop3456` |
| `HOTPEPPER_API_KEY` | Hot Pepper Gourmet API繧ｭ繝ｼ | `1234567890abcdef1234567890abcdef` |
| `FLASK_DEBUG` | 繝・ヰ繝・げ繝｢繝ｼ繝会ｼ域悽逡ｪ縺ｧ縺ｯ`False`・・| `False` |

### 2.2 迺ｰ蠅・､画焚險ｭ螳壽焔鬆・

1. PythonAnywhere縺ｮWeb繧ｿ繝悶ｒ髢九￥
2. "Environment variables" 繧ｻ繧ｯ繧ｷ繝ｧ繝ｳ繧定ｦ九▽縺代ｋ
3. 蜷・腸蠅・､画焚繧定ｿｽ蜉・・
   - Name: 螟画焚蜷阪ｒ蜈･蜉・
   - Value: 蟇ｾ蠢懊☆繧句､繧貞・蜉・
   - "Set" 繝懊ち繝ｳ繧偵け繝ｪ繝・け

### 2.3 API繧ｭ繝ｼ縺ｮ蜿門ｾ玲婿豕・

**OpenWeatherMap API繧ｭ繝ｼ:**
1. https://openweathermap.org/ 縺ｫ繧｢繧ｯ繧ｻ繧ｹ
2. 繧｢繧ｫ繧ｦ繝ｳ繝井ｽ懈・繝ｻ繝ｭ繧ｰ繧､繝ｳ
3. API Keys 繧ｻ繧ｯ繧ｷ繝ｧ繝ｳ縺ｧ繧ｭ繝ｼ繧堤函謌・
4. One Call API 3.0縺ｮ蛻ｩ逕ｨ繧堤｢ｺ隱・

**Hot Pepper Gourmet API繧ｭ繝ｼ:**
1. https://webservice.recruit.co.jp/ 縺ｫ繧｢繧ｯ繧ｻ繧ｹ
2. 繧｢繧ｫ繧ｦ繝ｳ繝井ｽ懈・繝ｻ繝ｭ繧ｰ繧､繝ｳ
3. Hot Pepper Gourmet API v1縺ｮ繧ｭ繝ｼ繧貞叙蠕・

## 3. Web繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｮ險ｭ螳・

### 3.1 蝓ｺ譛ｬ險ｭ螳・

1. PythonAnywhere縺ｮWeb繧ｿ繝悶ｒ髢九￥
2. "Add a new web app" 繧偵け繝ｪ繝・け
3. 莉･荳九・險ｭ螳壹ｒ陦後≧・・

| 鬆・岼 | 險ｭ螳壼､ |
|------|--------|
| Python version | Python 3.11 |
| Framework | Manual configuration |
| Source code | `/home/yourusername/lunch-roulette` |
| Working directory | `/home/yourusername/lunch-roulette` |
| WSGI configuration file | `/home/yourusername/lunch-roulette/wsgi.py` |

### 3.2 wsgi.py縺ｮ邱ｨ髮・

`wsgi.py`繝輔ぃ繧､繝ｫ蜀・・莉･荳九・陦後ｒ邱ｨ髮・ｼ・

```python
# 螟画峩蜑・
project_home = '/home/yourusername/lunch-roulette'

# 螟画峩蠕鯉ｼ亥ｮ滄圀縺ｮ繝ｦ繝ｼ繧ｶ繝ｼ蜷阪↓鄂ｮ謠幢ｼ・
project_home = '/home/actual_username/lunch-roulette'
```

### 3.3 髱咏噪繝輔ぃ繧､繝ｫ縺ｮ險ｭ螳・

Web繧ｿ繝悶・ "Static files" 繧ｻ繧ｯ繧ｷ繝ｧ繝ｳ縺ｧ莉･荳九ｒ險ｭ螳夲ｼ・

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/lunch-roulette/static/` |

## 4. 繝・・繧ｿ繝吶・繧ｹ縺ｮ蛻晄悄蛹・

### 4.1 閾ｪ蜍募・譛溷喧

`wsgi.py`繝輔ぃ繧､繝ｫ縺ｫ繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹悶さ繝ｼ繝峨′蜷ｫ縺ｾ繧後※縺・ｋ縺溘ａ縲∝・蝗槭い繧ｯ繧ｻ繧ｹ譎ゅ↓閾ｪ蜍慕噪縺ｫ菴懈・縺輔ｌ縺ｾ縺吶・

### 4.2 謇句虚蛻晄悄蛹厄ｼ亥ｿ・ｦ√↓蠢懊§縺ｦ・・

```bash
# Bash繧ｳ繝ｳ繧ｽ繝ｼ繝ｫ縺ｧ螳溯｡・
cd ~/lunch-roulette
source venv/bin/activate
python3 -c "from database import init_database; init_database('cache.db')"
```

## 5. 繝・・繝ｭ繧､繝｡繝ｳ繝育｢ｺ隱・

### 5.1 險ｭ螳夂｢ｺ隱阪メ繧ｧ繝・け繝ｪ繧ｹ繝・

- [ ] 繝励Ο繧ｸ繧ｧ繧ｯ繝医ヵ繧｡繧､繝ｫ縺後い繝・・繝ｭ繝ｼ繝画ｸ医∩
- [ ] 莉ｮ諠ｳ迺ｰ蠅・′菴懈・縺輔ｌ縲∽ｾ晏ｭ倬未菫ゅ′繧､繝ｳ繧ｹ繝医・繝ｫ貂医∩
- [ ] 蜈ｨ縺ｦ縺ｮ迺ｰ蠅・､画焚縺瑚ｨｭ螳壽ｸ医∩
- [ ] wsgi.py縺ｮ繝代せ縺梧ｭ｣縺励￥險ｭ螳壽ｸ医∩
- [ ] 髱咏噪繝輔ぃ繧､繝ｫ縺ｮ繝槭ャ繝斐Φ繧ｰ縺瑚ｨｭ螳壽ｸ医∩
- [ ] Web繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺梧怏蜉ｹ蛹匁ｸ医∩

### 5.2 蜍穂ｽ懃｢ｺ隱・

1. PythonAnywhere縺ｮWeb繧ｿ繝悶〒 "Reload" 繝懊ち繝ｳ繧偵け繝ｪ繝・け
2. 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳURL縺ｫ繧｢繧ｯ繧ｻ繧ｹ
3. 莉･荳九・讖溯・繧堤｢ｺ隱搾ｼ・
   - [ ] 繝壹・繧ｸ縺梧ｭ｣蟶ｸ縺ｫ陦ｨ遉ｺ縺輔ｌ繧・
   - [ ] 菴咲ｽｮ諠・ｱ縺瑚｡ｨ遉ｺ縺輔ｌ繧・
   - [ ] 螟ｩ豌玲ュ蝣ｱ縺瑚｡ｨ遉ｺ縺輔ｌ繧・
   - [ ] 繝ｫ繝ｼ繝ｬ繝・ヨ繝懊ち繝ｳ縺悟虚菴懊☆繧・
   - [ ] 繝ｬ繧ｹ繝医Λ繝ｳ諠・ｱ縺瑚｡ｨ遉ｺ縺輔ｌ繧・

### 5.3 繝ｭ繧ｰ縺ｮ遒ｺ隱・

繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺溷ｴ蜷医・縲∽ｻ･荳九・繝ｭ繧ｰ繧堤｢ｺ隱搾ｼ・

1. PythonAnywhere縺ｮWeb繧ｿ繝・竊・"Log files"
2. Error log: `/var/log/yourusername.pythonanywhere.com.error.log`
3. Server log: `/var/log/yourusername.pythonanywhere.com.server.log`

## 6. 繝医Λ繝悶Ν繧ｷ繝･繝ｼ繝・ぅ繝ｳ繧ｰ

### 6.1 繧医￥縺ゅｋ蝠城｡後→隗｣豎ｺ譁ｹ豕・

**蝠城｡・ "ImportError: No module named 'app'"**
- 隗｣豎ｺ: wsgi.py縺ｮproject_home繝代せ繧堤｢ｺ隱・
- Working directory縺梧ｭ｣縺励￥險ｭ螳壹＆繧後※縺・ｋ縺狗｢ｺ隱・

**蝠城｡・ "API key not found"**
- 隗｣豎ｺ: 迺ｰ蠅・､画焚縺梧ｭ｣縺励￥險ｭ螳壹＆繧後※縺・ｋ縺狗｢ｺ隱・
- 螟画焚蜷阪・繧ｹ繝壹Ν繝溘せ縺後↑縺・°遒ｺ隱・

**蝠城｡・ "Database is locked"**
- 隗｣豎ｺ: Bash繧ｳ繝ｳ繧ｽ繝ｼ繝ｫ縺ｧ繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繝励Ο繧ｻ繧ｹ繧堤｢ｺ隱・
- 蠢・ｦ√↓蠢懊§縺ｦWeb繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧偵Μ繝ｭ繝ｼ繝・

**蝠城｡・ 髱咏噪繝輔ぃ繧､繝ｫ・・SS/JS・峨′隱ｭ縺ｿ霎ｼ縺ｾ繧後↑縺・*
- 隗｣豎ｺ: Static files縺ｮ險ｭ螳壹ｒ遒ｺ隱・
- 繝輔ぃ繧､繝ｫ繝代せ縺梧ｭ｣縺励＞縺狗｢ｺ隱・

### 6.2 繝代ヵ繧ｩ繝ｼ繝槭Φ繧ｹ譛驕ｩ蛹・

**辟｡譁吶・繝ｩ繝ｳ縺ｮ蛻ｶ髯仙・縺ｧ縺ｮ驕狗畑:**
- API繧ｭ繝｣繝・す繝･讖溯・縺ｫ繧医ｊ螟夜ΚAPI蜻ｼ縺ｳ蜃ｺ縺励ｒ譛蟆丞喧
- 1譎る俣縺ゅ◆繧・0蝗樊悴貅縺ｮAPI蜻ｼ縺ｳ蜃ｺ縺怜宛髯舌ｒ驕ｵ螳・
- SQLite繧ｭ繝｣繝・す繝･縺ｫ繧医ｋ鬮倬溘Ξ繧ｹ繝昴Φ繧ｹ

**繝｡繝｢繝ｪ菴ｿ逕ｨ驥上・譛驕ｩ蛹・**
- 荳崎ｦ√↑繝ｩ繧､繝悶Λ繝ｪ縺ｮ繧､繝ｳ繝昴・繝医ｒ驕ｿ縺代ｋ
- 繧ｭ繝｣繝・す繝･繧ｵ繧､繧ｺ繧帝←蛻・↓邂｡逅・
- 螳壽悄逧・↑繧ｭ繝｣繝・す繝･繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・

## 7. 繝｡繝ｳ繝・リ繝ｳ繧ｹ

### 7.1 螳壽悄逧・↑菴懈･ｭ

**譛域ｬ｡:**
- [ ] API繧ｭ繝ｼ縺ｮ譛牙柑譛滄剞遒ｺ隱・
- [ ] 繝ｭ繧ｰ繝輔ぃ繧､繝ｫ縺ｮ繧ｵ繧､繧ｺ遒ｺ隱・
- [ ] 繧ｭ繝｣繝・す繝･繝・・繧ｿ繝吶・繧ｹ縺ｮ繧ｵ繧､繧ｺ遒ｺ隱・

**蠢・ｦ√↓蠢懊§縺ｦ:**
- [ ] 萓晏ｭ倬未菫ゅ・繧｢繝・・繝・・繝・
- [ ] 繧ｻ繧ｭ繝･繝ｪ繝・ぅ繝代ャ繝√・驕ｩ逕ｨ
- [ ] 繧ｭ繝｣繝・す繝･繝・・繧ｿ繝吶・繧ｹ縺ｮ譛驕ｩ蛹・

### 7.2 繧｢繝・・繝・・繝域焔鬆・

```bash
# Bash繧ｳ繝ｳ繧ｽ繝ｼ繝ｫ縺ｧ螳溯｡・
cd ~/lunch-roulette
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
```

縺昴・蠕後仝eb繧ｿ繝悶〒Reload繧貞ｮ溯｡後・

## 8. 繧ｻ繧ｭ繝･繝ｪ繝・ぅ閠・・莠矩・

### 8.1 譛ｬ逡ｪ迺ｰ蠅・〒縺ｮ豕ｨ諢冗せ

- [ ] `SECRET_KEY`繧呈悽逡ｪ逕ｨ縺ｮ蠑ｷ蜉帙↑繧ｭ繝ｼ縺ｫ螟画峩
- [ ] `FLASK_DEBUG`繧蛋False`縺ｫ險ｭ螳・
- [ ] API繧ｭ繝ｼ繧堤腸蠅・､画焚縺ｧ邂｡逅・ｼ医さ繝ｼ繝峨↓逶ｴ謗･險倩ｿｰ縺励↑縺・ｼ・
- [ ] 螳壽悄逧・↑繧ｻ繧ｭ繝･繝ｪ繝・ぅ繧｢繝・・繝・・繝・

### 8.2 繝・・繧ｿ菫晁ｭｷ

- 菴咲ｽｮ諠・ｱ縺ｯIP繝吶・繧ｹ縺ｮ縺ｿ・・PS荳堺ｽｿ逕ｨ・・
- 蛟倶ｺｺ隴伜挨諠・ｱ縺ｯ繝ｭ繧ｰ縺ｫ險倬鹸縺励↑縺・
- 繧ｭ繝｣繝・す繝･繝・・繧ｿ縺ｫ蛟倶ｺｺ諠・ｱ繧貞性繧√↑縺・

## 9. 繧ｵ繝昴・繝域ュ蝣ｱ

### 9.1 髢｢騾｣繝ｪ繝ｳ繧ｯ

- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Hot Pepper Gourmet API](https://webservice.recruit.co.jp/doc/hotpepper/)

### 9.2 繝励Ο繧ｸ繧ｧ繧ｯ繝域ュ蝣ｱ

- GitHub: [繝励Ο繧ｸ繧ｧ繧ｯ繝・RL]
- 謚陦薙せ繧ｿ繝・け: Python 3.11, Flask 3.0, SQLite
- 蟇ｾ蠢懊・繝ｩ繝・ヨ繝輔か繝ｼ繝: PythonAnywhere辟｡譁吶・繝ｩ繝ｳ