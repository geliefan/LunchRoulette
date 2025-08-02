#!/usr/bin/python3

"""
WSGI險ｭ螳壹ヵ繧｡繧､繝ｫ - PythonAnywhere逕ｨ
Lunch Roulette繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｮ繝・・繝ｭ繧､繝｡繝ｳ繝郁ｨｭ螳・

縺薙・繝輔ぃ繧､繝ｫ縺ｯPythonAnywhere縺ｮWeb繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ險ｭ螳壹〒菴ｿ逕ｨ縺輔ｌ縺ｾ縺吶・
PythonAnywhere縺ｮWeb繧ｿ繝悶〒莉･荳九・險ｭ螳壹ｒ陦後▲縺ｦ縺上□縺輔＞・・
1. Source code: /home/yourusername/lunch-roulette
2. Working directory: /home/yourusername/lunch-roulette  
3. WSGI configuration file: /home/yourusername/lunch-roulette/wsgi.py

豕ｨ諢・ 'yourusername'繧貞ｮ滄圀縺ｮPythonAnywhere繝ｦ繝ｼ繧ｶ繝ｼ蜷阪↓螟画峩縺励※縺上□縺輔＞
"""

import sys
import os

# 繝励Ο繧ｸ繧ｧ繧ｯ繝医ョ繧｣繝ｬ繧ｯ繝医Μ繧単ython繝代せ縺ｫ霑ｽ蜉
# PythonAnywhere縺ｧ縺ｮ螳滄圀縺ｮ繝代せ縺ｫ螟画峩縺励※縺上□縺輔＞
project_home = '/home/yourusername/lunch-roulette'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# 菴懈･ｭ繝・ぅ繝ｬ繧ｯ繝医Μ繧定ｨｭ螳・
os.chdir(project_home)

# 繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹厄ｼ亥・蝗槭ョ繝励Ο繧､譎ゑｼ・
try:
    from database import init_database
    init_database('cache.db')
    print("繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹門ｮ御ｺ・)
except Exception as e:
    print(f"繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹悶お繝ｩ繝ｼ・域里縺ｫ蟄伜惠縺吶ｋ蜿ｯ閭ｽ諤ｧ縺後≠繧翫∪縺呻ｼ・ {e}")

# Flask繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧偵う繝ｳ繝昴・繝・
from app import app as application

# 譛ｬ逡ｪ迺ｰ蠅・ｨｭ螳壹・遒ｺ隱・
if not os.environ.get('SECRET_KEY'):
    print("隴ｦ蜻・ SECRET_KEY縺瑚ｨｭ螳壹＆繧後※縺・∪縺帙ｓ")
if not os.environ.get('OPENWEATHER_API_KEY'):
    print("隴ｦ蜻・ OPENWEATHER_API_KEY縺瑚ｨｭ螳壹＆繧後※縺・∪縺帙ｓ")
if not os.environ.get('HOTPEPPER_API_KEY'):
    print("隴ｦ蜻・ HOTPEPPER_API_KEY縺瑚ｨｭ螳壹＆繧後※縺・∪縺帙ｓ")

# 繝・ヰ繝・げ繝｢繝ｼ繝峨ｒ譛ｬ逡ｪ迺ｰ蠅・〒縺ｯ辟｡蜉ｹ蛹・
application.config['DEBUG'] = False

if __name__ == "__main__":
    application.run()
