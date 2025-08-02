#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CacheService - 繧ｭ繝｣繝・す繝･繧ｵ繝ｼ繝薙せ繧ｯ繝ｩ繧ｹ
SQLite繧剃ｽｿ逕ｨ縺励◆繧ｭ繝｣繝・す繝ｳ繧ｰ讖溯・繧呈署萓・

縺薙・繧ｯ繝ｩ繧ｹ縺ｯ莉･荳九・讖溯・繧呈署萓帙＠縺ｾ縺・
- 繧ｭ繝｣繝・す繝･繝・・繧ｿ縺ｮ菫晏ｭ倥・蜿門ｾ・
- TTL・・ime To Live・峨・繝ｼ繧ｹ縺ｮ譛牙柑譛滄剞繝√ぉ繝・け
- 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ縺ｮ逕滓・縺ｨ繝・・繧ｿ繧ｷ繝ｪ繧｢繝ｩ繧､繧ｼ繝ｼ繧ｷ繝ｧ繝ｳ
- 閾ｪ蜍慕噪縺ｪ譛滄剞蛻・ｌ繝・・繧ｿ繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from database import get_db_connection, cleanup_expired_cache


class CacheService:
    """
    SQLite繧剃ｽｿ逕ｨ縺励◆繧ｭ繝｣繝・す繝ｳ繧ｰ繧ｵ繝ｼ繝薙せ

    螟夜ΚAPI蜻ｼ縺ｳ蜃ｺ縺励・邨先棡繧偵く繝｣繝・す繝･縺励√Ξ繝ｼ繝亥宛髯仙ｯｾ遲悶→
    繝代ヵ繧ｩ繝ｼ繝槭Φ繧ｹ蜷台ｸ翫ｒ螳溽樟縺吶ｋ縲・
    """

    def __init__(self, db_path: str = 'cache.db', default_ttl: int = 600):
        """
        CacheService繧貞・譛溷喧

        Args:
            db_path (str): SQLite繝・・繧ｿ繝吶・繧ｹ繝輔ぃ繧､繝ｫ縺ｮ繝代せ
            default_ttl (int): 繝・ヵ繧ｩ繝ｫ繝・TL・育ｧ抵ｼ峨√ョ繝輔か繝ｫ繝医・10蛻・
        """
        self.db_path = db_path
        self.default_ttl = default_ttl

    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """
        繧ｭ繝｣繝・す繝･繧ｭ繝ｼ繧堤函謌・

        繝励Ξ繝輔ぅ繝・け繧ｹ縺ｨ繧ｭ繝ｼ繝ｯ繝ｼ繝牙ｼ墓焚縺九ｉ繝ｦ繝九・繧ｯ縺ｪ繧ｭ繝｣繝・す繝･繧ｭ繝ｼ繧堤函謌舌☆繧九・
        蜷後§繝代Λ繝｡繝ｼ繧ｿ縺ｫ蟇ｾ縺励※縺ｯ蟶ｸ縺ｫ蜷後§繧ｭ繝ｼ縺檎函謌舌＆繧後ｋ縲・

        Args:
            prefix (str): 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ縺ｮ繝励Ξ繝輔ぅ繝・け繧ｹ・井ｾ・ "weather", "restaurant"・・
            **kwargs: 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ逕滓・縺ｫ菴ｿ逕ｨ縺吶ｋ繝代Λ繝｡繝ｼ繧ｿ

        Returns:
            str: 逕滓・縺輔ｌ縺溘く繝｣繝・す繝･繧ｭ繝ｼ

        Example:
            >>> cache = CacheService()
            >>> key = cache.generate_cache_key("weather", lat=35.6762, lon=139.6503)
            >>> print(key)  # "weather_a1b2c3d4e5f6..."
        """
        # 繝代Λ繝｡繝ｼ繧ｿ繧呈枚蟄怜・縺ｫ螟画鋤縺励※繧ｽ繝ｼ繝茨ｼ井ｸ雋ｫ諤ｧ縺ｮ縺溘ａ・・
        params_str = json.dumps(kwargs, sort_keys=True, ensure_ascii=False)

        # SHA256繝上ャ繧ｷ繝･繧堤函謌・
        hash_object = hashlib.sha256(params_str.encode('utf-8'))
        hash_hex = hash_object.hexdigest()[:16]  # 16譁・ｭ励↓遏ｭ邵ｮ

        return f"{prefix}_{hash_hex}"

    def serialize_data(self, data: Any) -> str:
        """
        繝・・繧ｿ繧谷SON譁・ｭ怜・縺ｫ繧ｷ繝ｪ繧｢繝ｩ繧､繧ｺ

        Args:
            data (Any): 繧ｷ繝ｪ繧｢繝ｩ繧､繧ｺ縺吶ｋ繝・・繧ｿ

        Returns:
            str: JSON譁・ｭ怜・

        Raises:
            ValueError: 繧ｷ繝ｪ繧｢繝ｩ繧､繧ｺ縺ｧ縺阪↑縺・ョ繝ｼ繧ｿ縺ｮ蝣ｴ蜷・
        """
        try:
            return json.dumps(data, ensure_ascii=False, default=str)
        except (TypeError, ValueError) as e:
            raise ValueError(f"繝・・繧ｿ縺ｮ繧ｷ繝ｪ繧｢繝ｩ繧､繧ｺ縺ｫ螟ｱ謨・ {e}")

    def deserialize_data(self, data_str: str) -> Any:
        """
        JSON譁・ｭ怜・繧偵ョ繝ｼ繧ｿ縺ｫ繝・す繝ｪ繧｢繝ｩ繧､繧ｺ

        Args:
            data_str (str): JSON譁・ｭ怜・

        Returns:
            Any: 繝・す繝ｪ繧｢繝ｩ繧､繧ｺ縺輔ｌ縺溘ョ繝ｼ繧ｿ

        Raises:
            ValueError: 繝・す繝ｪ繧｢繝ｩ繧､繧ｺ縺ｧ縺阪↑縺・枚蟄怜・縺ｮ蝣ｴ蜷・
        """
        try:
            return json.loads(data_str)
        except (TypeError, ValueError) as e:
            raise ValueError(f"繝・・繧ｿ縺ｮ繝・す繝ｪ繧｢繝ｩ繧､繧ｺ縺ｫ螟ｱ謨・ {e}")

    def is_cache_valid(self, expires_at: datetime) -> bool:
        """
        繧ｭ繝｣繝・す繝･縺ｮ譛牙柑諤ｧ繧偵メ繧ｧ繝・け

        Args:
            expires_at (datetime): 繧ｭ繝｣繝・す繝･縺ｮ譛牙柑譛滄剞

        Returns:
            bool: 譛牙柑縺ｪ蝣ｴ蜷・rue縲∵悄髯仙・繧後・蝣ｴ蜷・alse
        """
        return datetime.now() < expires_at

    def set_cached_data(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        繧ｭ繝｣繝・す繝･繝・・繧ｿ繧剃ｿ晏ｭ・

        Args:
            key (str): 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ
            data (Any): 菫晏ｭ倥☆繧九ョ繝ｼ繧ｿ
            ttl (int, optional): TTL・育ｧ抵ｼ峨・one縺ｮ蝣ｴ蜷医・default_ttl繧剃ｽｿ逕ｨ

        Returns:
            bool: 菫晏ｭ倥′謌仙粥縺励◆蝣ｴ蜷・rue

        Example:
            >>> cache = CacheService()
            >>> success = cache.set_cached_data("weather_tokyo", {"temp": 25}, 600)
            >>> print(success)  # True
        """
        try:
            # TTL縺梧欠螳壹＆繧後※縺・↑縺・ｴ蜷医・繝・ヵ繧ｩ繝ｫ繝亥､繧剃ｽｿ逕ｨ
            if ttl is None:
                ttl = self.default_ttl

            # 譛牙柑譛滄剞繧定ｨ育ｮ・
            expires_at = datetime.now() + timedelta(seconds=ttl)

            # 繝・・繧ｿ繧偵す繝ｪ繧｢繝ｩ繧､繧ｺ
            serialized_data = self.serialize_data(data)

            # 繝・・繧ｿ繝吶・繧ｹ縺ｫ菫晏ｭ・
            with get_db_connection(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO cache
                    (cache_key, data, expires_at)
                    VALUES (?, ?, ?)
                ''', (key, serialized_data, expires_at))
                conn.commit()

            return True

        except Exception as e:
            print(f"繧ｭ繝｣繝・す繝･菫晏ｭ倥お繝ｩ繝ｼ (key: {key}): {e}")
            return False

    def get_cached_data(self, key: str) -> Optional[Any]:
        """
        繧ｭ繝｣繝・す繝･繝・・繧ｿ繧貞叙蠕・

        Args:
            key (str): 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ

        Returns:
            Any: 繧ｭ繝｣繝・す繝･縺輔ｌ縺溘ョ繝ｼ繧ｿ縲ょｭ伜惠縺励↑縺・°譛滄剞蛻・ｌ縺ｮ蝣ｴ蜷医・None

        Example:
            >>> cache = CacheService()
            >>> data = cache.get_cached_data("weather_tokyo")
            >>> if data:
            ...     print(f"Temperature: {data['temp']}")
        """
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT data, expires_at FROM cache
                    WHERE cache_key = ?
                ''', (key,))

                row = cursor.fetchone()

                if row is None:
                    return None

                # 譛牙柑譛滄剞繧偵メ繧ｧ繝・け
                expires_at = datetime.fromisoformat(row['expires_at'])
                if not self.is_cache_valid(expires_at):
                    # 譛滄剞蛻・ｌ縺ｮ蝣ｴ蜷医・蜑企勁
                    self._delete_cache_entry(key)
                    return None

                # 繝・・繧ｿ繧偵ョ繧ｷ繝ｪ繧｢繝ｩ繧､繧ｺ縺励※霑斐☆
                return self.deserialize_data(row['data'])

        except Exception as e:
            print(f"繧ｭ繝｣繝・す繝･蜿門ｾ励お繝ｩ繝ｼ (key: {key}): {e}")
            return None

    def _delete_cache_entry(self, key: str) -> bool:
        """
        謖・ｮ壹＆繧後◆繧ｭ繝｣繝・す繝･繧ｨ繝ｳ繝医Μ繧貞炎髯､・亥・驛ｨ繝｡繧ｽ繝・ラ・・

        Args:
            key (str): 蜑企勁縺吶ｋ繧ｭ繝｣繝・す繝･繧ｭ繝ｼ

        Returns:
            bool: 蜑企勁縺梧・蜉溘＠縺溷ｴ蜷・rue
        """
        try:
            with get_db_connection(self.db_path) as conn:
                conn.execute('DELETE FROM cache WHERE cache_key = ?', (key,))
                conn.commit()
            return True
        except Exception as e:
            print(f"繧ｭ繝｣繝・す繝･蜑企勁繧ｨ繝ｩ繝ｼ (key: {key}): {e}")
            return False

    def delete_cached_data(self, key: str) -> bool:
        """
        繧ｭ繝｣繝・す繝･繝・・繧ｿ繧貞炎髯､

        Args:
            key (str): 蜑企勁縺吶ｋ繧ｭ繝｣繝・す繝･繧ｭ繝ｼ

        Returns:
            bool: 蜑企勁縺梧・蜉溘＠縺溷ｴ蜷・rue
        """
        return self._delete_cache_entry(key)

    def clear_expired_cache(self) -> int:
        """
        譛滄剞蛻・ｌ縺ｮ繧ｭ繝｣繝・す繝･繝・・繧ｿ繧偵☆縺ｹ縺ｦ蜑企勁

        Returns:
            int: 蜑企勁縺輔ｌ縺溘Ξ繧ｳ繝ｼ繝画焚
        """
        return cleanup_expired_cache(self.db_path)

    def clear_all_cache(self) -> bool:
        """
        縺吶∋縺ｦ縺ｮ繧ｭ繝｣繝・す繝･繝・・繧ｿ繧貞炎髯､

        Returns:
            bool: 蜑企勁縺梧・蜉溘＠縺溷ｴ蜷・rue
        """
        try:
            with get_db_connection(self.db_path) as conn:
                conn.execute('DELETE FROM cache')
                conn.commit()
            return True
        except Exception as e:
            print(f"蜈ｨ繧ｭ繝｣繝・す繝･蜑企勁繧ｨ繝ｩ繝ｼ: {e}")
            return False

    def get_cache_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        繧ｭ繝｣繝・す繝･縺ｮ隧ｳ邏ｰ諠・ｱ繧貞叙蠕・

        Args:
            key (str): 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ

        Returns:
            dict: 繧ｭ繝｣繝・す繝･諠・ｱ・井ｽ懈・譌･譎ゅ∵怏蜉ｹ譛滄剞縲√ョ繝ｼ繧ｿ繧ｵ繧､繧ｺ縺ｪ縺ｩ・・
        """
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT created_at, expires_at, LENGTH(data) as data_size
                    FROM cache WHERE cache_key = ?
                ''', (key,))

                row = cursor.fetchone()

                if row is None:
                    return None

                expires_at = datetime.fromisoformat(row['expires_at'])
                created_at = datetime.fromisoformat(row['created_at'])

                return {
                    'key': key,
                    'created_at': created_at,
                    'expires_at': expires_at,
                    'is_valid': self.is_cache_valid(expires_at),
                    'data_size': row['data_size'],
                    'ttl_remaining': max(0, (expires_at - datetime.now()).total_seconds())
                }

        except Exception as e:
            print(f"繧ｭ繝｣繝・す繝･諠・ｱ蜿門ｾ励お繝ｩ繝ｼ (key: {key}): {e}")
            return None


# 菴ｿ逕ｨ萓九→繝・せ繝育畑繧ｳ繝ｼ繝・
if __name__ == '__main__':
    """
    CacheService縺ｮ繝・せ繝亥ｮ溯｡・
    """
    print("CacheService 繝・せ繝亥ｮ溯｡・)
    print("=" * 40)

    # CacheService繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ菴懈・
    cache = CacheService()

    # 繝・せ繝医ョ繝ｼ繧ｿ
    test_data = {
        'temperature': 25.5,
        'condition': 'sunny',
        'location': '譚ｱ莠ｬ',
        'timestamp': datetime.now().isoformat()
    }

    # 繧ｭ繝｣繝・す繝･繧ｭ繝ｼ逕滓・繝・せ繝・
    cache_key = cache.generate_cache_key('weather', lat=35.6762, lon=139.6503)
    print(f"笨・繧ｭ繝｣繝・す繝･繧ｭ繝ｼ逕滓・: {cache_key}")

    # 繝・・繧ｿ菫晏ｭ倥ユ繧ｹ繝・
    if cache.set_cached_data(cache_key, test_data, ttl=60):
        print("笨・繧ｭ繝｣繝・す繝･繝・・繧ｿ菫晏ｭ俶・蜉・)
    else:
        print("笨・繧ｭ繝｣繝・す繝･繝・・繧ｿ菫晏ｭ伜､ｱ謨・)

    # 繝・・繧ｿ蜿門ｾ励ユ繧ｹ繝・
    cached_data = cache.get_cached_data(cache_key)
    if cached_data:
        print(f"笨・繧ｭ繝｣繝・す繝･繝・・繧ｿ蜿門ｾ玲・蜉・ {cached_data['condition']}")
    else:
        print("笨・繧ｭ繝｣繝・す繝･繝・・繧ｿ蜿門ｾ怜､ｱ謨・)

    # 繧ｭ繝｣繝・す繝･諠・ｱ蜿門ｾ励ユ繧ｹ繝・
    cache_info = cache.get_cache_info(cache_key)
    if cache_info:
        print(f"笨・繧ｭ繝｣繝・す繝･諠・ｱ: TTL谿九ｊ {cache_info['ttl_remaining']:.1f}遘・)

    # 譛滄剞蛻・ｌ繧ｭ繝｣繝・す繝･繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・繝・せ繝・
    expired_count = cache.clear_expired_cache()
    print(f"笨・譛滄剞蛻・ｌ繧ｭ繝｣繝・す繝･繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・: {expired_count}莉ｶ蜑企勁")

    print("繝・せ繝亥ｮ御ｺ・)
