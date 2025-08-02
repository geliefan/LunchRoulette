#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ErrorHandler - 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｨ繝｡繝・そ繝ｼ繧ｸ邂｡逅・け繝ｩ繧ｹ
繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ蜈ｨ菴薙・繧ｨ繝ｩ繝ｼ蜃ｦ逅・→繝ｦ繝ｼ繧ｶ繝ｼ繝輔Ξ繝ｳ繝峨Μ繝ｼ縺ｪ繝｡繝・そ繝ｼ繧ｸ陦ｨ遉ｺ繧呈署萓・

縺薙・繧ｯ繝ｩ繧ｹ縺ｯ莉･荳九・讖溯・繧呈署萓帙＠縺ｾ縺・
- API 繧ｨ繝ｩ繝ｼ縺ｮ蛻・｡槭→驕ｩ蛻・↑繝｡繝・そ繝ｼ繧ｸ逕滓・
- 繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ讖溯・縺ｮ邂｡逅・
- 繧ｨ繝ｩ繝ｼ繝ｭ繧ｰ縺ｮ險倬鹸
- 繝ｦ繝ｼ繧ｶ繝ｼ蜷代￠繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ縺ｮ蝗ｽ髫帛喧蟇ｾ蠢・
"""

import logging
from typing import Dict, Any, Tuple
from enum import Enum
from datetime import datetime


class ErrorType(Enum):
    """繧ｨ繝ｩ繝ｼ繧ｿ繧､繝励・螳夂ｾｩ"""
    API_RATE_LIMIT = "api_rate_limit"
    API_AUTH_ERROR = "api_auth_error"
    API_NETWORK_ERROR = "api_network_error"
    API_TIMEOUT = "api_timeout"
    DATA_PARSING_ERROR = "data_parsing_error"
    LOCATION_NOT_FOUND = "location_not_found"
    RESTAURANT_NOT_FOUND = "restaurant_not_found"
    DISTANCE_CALCULATION_ERROR = "distance_calculation_error"
    CACHE_ERROR = "cache_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorHandler:
    """
    繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ蜈ｨ菴薙・繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ繧堤ｮ｡逅・☆繧九け繝ｩ繧ｹ

    繧ｨ繝ｩ繝ｼ縺ｮ蛻・｡槭√Ο繧ｰ險倬鹸縲√Θ繝ｼ繧ｶ繝ｼ繝輔Ξ繝ｳ繝峨Μ繝ｼ縺ｪ繝｡繝・そ繝ｼ繧ｸ逕滓・縲・
    繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ讖溯・縺ｮ謠蝉ｾ帙ｒ陦後≧縲・
    """

    # 繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ縺ｮ繝槭ャ繝斐Φ繧ｰ
    ERROR_MESSAGES = {
        ErrorType.API_RATE_LIMIT: {
            'user_message': 'API縺ｮ蛻ｩ逕ｨ蛻ｶ髯舌↓驕斐＠縺ｾ縺励◆縲ゅく繝｣繝・す繝･縺輔ｌ縺溘ョ繝ｼ繧ｿ繧剃ｽｿ逕ｨ縺励∪縺吶・,
            'suggestion': '縺励・繧峨￥譎る俣繧堤ｽｮ縺・※縺九ｉ蜀榊ｺｦ縺願ｩｦ縺励￥縺縺輔＞縲・,
            'severity': 'warning'
        },
        ErrorType.API_AUTH_ERROR: {
            'user_message': 'API隱崎ｨｼ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆縲・,
            'suggestion': '繧ｷ繧ｹ繝・Β邂｡逅・・↓縺雁撫縺・粋繧上○縺上□縺輔＞縲・,
            'severity': 'error'
        },
        ErrorType.API_NETWORK_ERROR: {
            'user_message': '繝阪ャ繝医Ρ繝ｼ繧ｯ謗･邯壹お繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆縲・,
            'suggestion': '繧､繝ｳ繧ｿ繝ｼ繝阪ャ繝域磁邯壹ｒ遒ｺ隱阪＠縺ｦ縺上□縺輔＞縲・,
            'severity': 'warning'
        },
        ErrorType.API_TIMEOUT: {
            'user_message': 'API縺ｮ蠢懃ｭ斐′繧ｿ繧､繝繧｢繧ｦ繝医＠縺ｾ縺励◆縲・,
            'suggestion': '縺励・繧峨￥譎る俣繧堤ｽｮ縺・※縺九ｉ蜀榊ｺｦ縺願ｩｦ縺励￥縺縺輔＞縲・,
            'severity': 'warning'
        },
        ErrorType.DATA_PARSING_ERROR: {
            'user_message': '繝・・繧ｿ縺ｮ蜃ｦ逅・ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆縲・,
            'suggestion': '繝・ヵ繧ｩ繝ｫ繝医ョ繝ｼ繧ｿ繧剃ｽｿ逕ｨ縺励∪縺吶・,
            'severity': 'warning'
        },
        ErrorType.LOCATION_NOT_FOUND: {
            'user_message': '菴咲ｽｮ諠・ｱ繧貞叙蠕励〒縺阪∪縺帙ｓ縺ｧ縺励◆縲・,
            'suggestion': '譚ｱ莠ｬ鬧・ｒ蝓ｺ貅悶↓讀懃ｴ｢縺励∪縺吶・,
            'severity': 'info'
        },
        ErrorType.RESTAURANT_NOT_FOUND: {
            'user_message': '霑代￥縺ｫ繝ｬ繧ｹ繝医Λ繝ｳ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ縺ｧ縺励◆縲・,
            'suggestion': '讀懃ｴ｢遽・峇繧貞ｺ・￡繧九°縲∵擅莉ｶ繧貞､画峩縺励※縺願ｩｦ縺励￥縺縺輔＞縲・,
            'severity': 'info'
        },
        ErrorType.DISTANCE_CALCULATION_ERROR: {
            'user_message': '霍晞屬縺ｮ險育ｮ嶺ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆縲・,
            'suggestion': '讎らｮ苓ｷ晞屬繧定｡ｨ遉ｺ縺励∪縺吶・,
            'severity': 'warning'
        },
        ErrorType.CACHE_ERROR: {
            'user_message': '繧ｭ繝｣繝・す繝･繧ｷ繧ｹ繝・Β縺ｧ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆縲・,
            'suggestion': '繝・・繧ｿ縺ｮ蜿門ｾ励↓譎る俣縺後°縺九ｋ蝣ｴ蜷医′縺ゅｊ縺ｾ縺吶・,
            'severity': 'warning'
        },
        ErrorType.UNKNOWN_ERROR: {
            'user_message': '莠域悄縺励↑縺・お繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆縲・,
            'suggestion': '縺励・繧峨￥譎る俣繧堤ｽｮ縺・※縺九ｉ蜀榊ｺｦ縺願ｩｦ縺励￥縺縺輔＞縲・,
            'severity': 'error'
        }
    }

    def __init__(self, logger_name: str = 'lunch_roulette'):
        """
        ErrorHandler繧貞・譛溷喧

        Args:
            logger_name (str): 繝ｭ繧ｬ繝ｼ蜷・
        """
        self.logger = logging.getLogger(logger_name)
        self.error_count = {}  # 繧ｨ繝ｩ繝ｼ逋ｺ逕溷屓謨ｰ縺ｮ險倬鹸

    def handle_api_error(self, service_name: str, error: Exception,
                         fallback_available: bool = False) -> Tuple[ErrorType, Dict[str, Any]]:
        """
        API 繧ｨ繝ｩ繝ｼ繧貞・逅・＠縲・←蛻・↑繧ｨ繝ｩ繝ｼ繧ｿ繧､繝励→繝｡繝・そ繝ｼ繧ｸ繧定ｿ斐☆

        Args:
            service_name (str): 繧ｵ繝ｼ繝薙せ蜷搾ｼ井ｾ・ "weather", "restaurant", "location"・・
            error (Exception): 逋ｺ逕溘＠縺溘お繝ｩ繝ｼ
            fallback_available (bool): 繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繝・・繧ｿ縺悟茜逕ｨ蜿ｯ閭ｽ縺九←縺・°

        Returns:
            tuple: (繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・ 繧ｨ繝ｩ繝ｼ諠・ｱ霎樊嶌)
        """
        error_type = self._classify_error(error)
        error_info = self._create_error_info(service_name, error_type, error, fallback_available)

        # 繧ｨ繝ｩ繝ｼ繝ｭ繧ｰ繧定ｨ倬鹸
        self._log_error(service_name, error_type, error, fallback_available)

        # 繧ｨ繝ｩ繝ｼ逋ｺ逕溷屓謨ｰ繧定ｨ倬鹸
        self._increment_error_count(error_type)

        return error_type, error_info

    def _classify_error(self, error: Exception) -> ErrorType:
        """
        繧ｨ繝ｩ繝ｼ繧貞・鬘槭＠縺ｦErrorType繧定ｿ斐☆

        Args:
            error (Exception): 逋ｺ逕溘＠縺溘お繝ｩ繝ｼ

        Returns:
            ErrorType: 蛻・｡槭＆繧後◆繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・
        """
        import requests

        if isinstance(error, requests.exceptions.HTTPError):
            if hasattr(error, 'response') and error.response.status_code == 429:
                return ErrorType.API_RATE_LIMIT
            elif hasattr(error, 'response') and error.response.status_code == 401:
                return ErrorType.API_AUTH_ERROR
            else:
                return ErrorType.API_NETWORK_ERROR
        elif isinstance(error, requests.exceptions.Timeout):
            return ErrorType.API_TIMEOUT
        elif isinstance(error, requests.exceptions.RequestException):
            return ErrorType.API_NETWORK_ERROR
        elif isinstance(error, (ValueError, KeyError)):
            return ErrorType.DATA_PARSING_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR

    def _create_error_info(self, service_name: str, error_type: ErrorType,
                           error: Exception, fallback_available: bool) -> Dict[str, Any]:
        """
        繧ｨ繝ｩ繝ｼ諠・ｱ霎樊嶌繧剃ｽ懈・

        Args:
            service_name (str): 繧ｵ繝ｼ繝薙せ蜷・
            error_type (ErrorType): 繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・
            error (Exception): 逋ｺ逕溘＠縺溘お繝ｩ繝ｼ
            fallback_available (bool): 繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繝・・繧ｿ縺悟茜逕ｨ蜿ｯ閭ｽ縺九←縺・°

        Returns:
            dict: 繧ｨ繝ｩ繝ｼ諠・ｱ霎樊嶌
        """
        error_config = self.ERROR_MESSAGES.get(error_type, self.ERROR_MESSAGES[ErrorType.UNKNOWN_ERROR])

        return {
            'error_type': error_type.value,
            'service_name': service_name,
            'user_message': error_config['user_message'],
            'suggestion': error_config['suggestion'],
            'severity': error_config['severity'],
            'fallback_available': fallback_available,
            'timestamp': datetime.now().isoformat(),
            'technical_details': str(error)
        }

    def _log_error(self, service_name: str, error_type: ErrorType,
                   error: Exception, fallback_available: bool) -> None:
        """
        繧ｨ繝ｩ繝ｼ繝ｭ繧ｰ繧定ｨ倬鹸

        Args:
            service_name (str): 繧ｵ繝ｼ繝薙せ蜷・
            error_type (ErrorType): 繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・
            error (Exception): 逋ｺ逕溘＠縺溘お繝ｩ繝ｼ
            fallback_available (bool): 繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繝・・繧ｿ縺悟茜逕ｨ蜿ｯ閭ｽ縺九←縺・°
        """
        log_message = (
            f"[{service_name}] {error_type.value}: {str(error)} "
            f"(繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ蛻ｩ逕ｨ蜿ｯ閭ｽ: {fallback_available})"
        )

        if error_type in [ErrorType.API_AUTH_ERROR, ErrorType.UNKNOWN_ERROR]:
            self.logger.error(log_message)
        elif error_type in [ErrorType.API_RATE_LIMIT, ErrorType.API_NETWORK_ERROR,
                            ErrorType.API_TIMEOUT, ErrorType.DATA_PARSING_ERROR]:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def _increment_error_count(self, error_type: ErrorType) -> None:
        """
        繧ｨ繝ｩ繝ｼ逋ｺ逕溷屓謨ｰ繧偵き繧ｦ繝ｳ繝・

        Args:
            error_type (ErrorType): 繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・
        """
        if error_type not in self.error_count:
            self.error_count[error_type] = 0
        self.error_count[error_type] += 1

    def get_error_statistics(self) -> Dict[str, int]:
        """
        繧ｨ繝ｩ繝ｼ邨ｱ險域ュ蝣ｱ繧貞叙蠕・

        Returns:
            dict: 繧ｨ繝ｩ繝ｼ繧ｿ繧､繝怜挨縺ｮ逋ｺ逕溷屓謨ｰ
        """
        return {error_type.value: count for error_type, count in self.error_count.items()}

    def create_user_friendly_message(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        繝ｦ繝ｼ繧ｶ繝ｼ繝輔Ξ繝ｳ繝峨Μ繝ｼ縺ｪ繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ繧剃ｽ懈・

        Args:
            error_info (dict): 繧ｨ繝ｩ繝ｼ諠・ｱ霎樊嶌

        Returns:
            dict: 繝ｦ繝ｼ繧ｶ繝ｼ蜷代￠繝｡繝・そ繝ｼ繧ｸ
        """
        return {
            'message': error_info['user_message'],
            'suggestion': error_info['suggestion'],
            'severity': error_info['severity'],
            'fallback_used': error_info['fallback_available'],
            'service_affected': error_info['service_name']
        }

    def handle_location_error(self, error: Exception, fallback_available: bool = True) -> Dict[str, Any]:
        """
        菴咲ｽｮ諠・ｱ繧ｨ繝ｩ繝ｼ繧貞・逅・

        Args:
            error (Exception): 逋ｺ逕溘＠縺溘お繝ｩ繝ｼ
            fallback_available (bool): 繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繝・・繧ｿ縺悟茜逕ｨ蜿ｯ閭ｽ縺九←縺・°

        Returns:
            dict: 繧ｨ繝ｩ繝ｼ蜃ｦ逅・ｵ先棡
        """
        error_type, error_info = self.handle_api_error('location', error, fallback_available)

        # 菴咲ｽｮ諠・ｱ迚ｹ譛峨・蜃ｦ逅・
        if not fallback_available:
            error_info['user_message'] = '菴咲ｽｮ諠・ｱ繧貞叙蠕励〒縺阪∪縺帙ｓ縺ｧ縺励◆縲よ擲莠ｬ鬧・ｒ蝓ｺ貅悶↓讀懃ｴ｢縺励∪縺吶・
            error_info['suggestion'] = '繧医ｊ豁｣遒ｺ縺ｪ邨先棡繧貞ｾ励ｋ縺ｫ縺ｯ縲∽ｽ咲ｽｮ諠・ｱ縺ｮ險ｱ蜿ｯ繧呈怏蜉ｹ縺ｫ縺励※縺上□縺輔＞縲・

        return self.create_user_friendly_message(error_info)

    def handle_restaurant_error(self, error: Exception, fallback_available: bool = False) -> Dict[str, Any]:
        """
        繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢繧ｨ繝ｩ繝ｼ繧貞・逅・

        Args:
            error (Exception): 逋ｺ逕溘＠縺溘お繝ｩ繝ｼ
            fallback_available (bool): 繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繝・・繧ｿ縺悟茜逕ｨ蜿ｯ閭ｽ縺九←縺・°

        Returns:
            dict: 繧ｨ繝ｩ繝ｼ蜃ｦ逅・ｵ先棡
        """
        error_type, error_info = self.handle_api_error('restaurant', error, fallback_available)

        # 繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢迚ｹ譛峨・蜃ｦ逅・
        if error_type == ErrorType.API_RATE_LIMIT and fallback_available:
            error_info['user_message'] = 'API蛻ｶ髯舌・縺溘ａ縲∽ｻ･蜑阪・讀懃ｴ｢邨先棡繧定｡ｨ遉ｺ縺励※縺・∪縺吶・
            error_info['suggestion'] = '譛譁ｰ縺ｮ諠・ｱ繧貞叙蠕励☆繧九↓縺ｯ縲√＠縺ｰ繧峨￥譎る俣繧堤ｽｮ縺・※縺上□縺輔＞縲・

        return self.create_user_friendly_message(error_info)

    def handle_weather_error(self, error: Exception, fallback_available: bool = True) -> Dict[str, Any]:
        """
        螟ｩ豌玲ュ蝣ｱ繧ｨ繝ｩ繝ｼ繧貞・逅・

        Args:
            error (Exception): 逋ｺ逕溘＠縺溘お繝ｩ繝ｼ
            fallback_available (bool): 繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ繝・・繧ｿ縺悟茜逕ｨ蜿ｯ閭ｽ縺九←縺・°

        Returns:
            dict: 繧ｨ繝ｩ繝ｼ蜃ｦ逅・ｵ先棡
        """
        error_type, error_info = self.handle_api_error('weather', error, fallback_available)

        # 螟ｩ豌玲ュ蝣ｱ迚ｹ譛峨・蜃ｦ逅・
        if not fallback_available:
            error_info['user_message'] = '螟ｩ豌玲ュ蝣ｱ繧貞叙蠕励〒縺阪∪縺帙ｓ縺ｧ縺励◆縲よｨ呎ｺ也噪縺ｪ螟ｩ豌玲ュ蝣ｱ繧定｡ｨ遉ｺ縺励∪縺吶・
            error_info['suggestion'] = '螳滄圀縺ｮ螟ｩ豌励・逡ｰ縺ｪ繧句ｴ蜷医′縺ゅｊ縺ｾ縺吶・

        return self.create_user_friendly_message(error_info)

    def handle_distance_calculation_error(self, error: Exception) -> Dict[str, Any]:
        """
        霍晞屬險育ｮ励お繝ｩ繝ｼ繧貞・逅・

        Args:
            error (Exception): 逋ｺ逕溘＠縺溘お繝ｩ繝ｼ

        Returns:
            dict: 繧ｨ繝ｩ繝ｼ蜃ｦ逅・ｵ先棡
        """
        error_info = {
            'error_type': ErrorType.DISTANCE_CALCULATION_ERROR.value,
            'service_name': 'distance_calculator',
            'user_message': '霍晞屬縺ｮ險育ｮ嶺ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆縲・,
            'suggestion': '讎らｮ苓ｷ晞屬繧定｡ｨ遉ｺ縺励∪縺吶・,
            'severity': 'warning',
            'fallback_available': True,
            'timestamp': datetime.now().isoformat(),
            'technical_details': str(error)
        }

        self._log_error('distance_calculator', ErrorType.DISTANCE_CALCULATION_ERROR, error, True)
        self._increment_error_count(ErrorType.DISTANCE_CALCULATION_ERROR)

        return self.create_user_friendly_message(error_info)

    def is_critical_error(self, error_type: ErrorType) -> bool:
        """
        繧ｯ繝ｪ繝・ぅ繧ｫ繝ｫ繧ｨ繝ｩ繝ｼ縺九←縺・°繧貞愛螳・

        Args:
            error_type (ErrorType): 繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・

        Returns:
            bool: 繧ｯ繝ｪ繝・ぅ繧ｫ繝ｫ繧ｨ繝ｩ繝ｼ縺ｮ蝣ｴ蜷・rue
        """
        critical_errors = [ErrorType.API_AUTH_ERROR, ErrorType.UNKNOWN_ERROR]
        return error_type in critical_errors

    def should_retry(self, error_type: ErrorType) -> bool:
        """
        繝ｪ繝医Λ繧､縺吶∋縺阪お繝ｩ繝ｼ縺九←縺・°繧貞愛螳・

        Args:
            error_type (ErrorType): 繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・

        Returns:
            bool: 繝ｪ繝医Λ繧､縺吶∋縺榊ｴ蜷・rue
        """
        retry_errors = [ErrorType.API_NETWORK_ERROR, ErrorType.API_TIMEOUT]
        return error_type in retry_errors

    def get_retry_delay(self, error_type: ErrorType, attempt_count: int) -> int:
        """
        繝ｪ繝医Λ繧､驕・ｻｶ譎る俣繧貞叙蠕・

        Args:
            error_type (ErrorType): 繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・
            attempt_count (int): 隧ｦ陦悟屓謨ｰ

        Returns:
            int: 驕・ｻｶ譎る俣・育ｧ抵ｼ・
        """
        base_delays = {
            ErrorType.API_NETWORK_ERROR: 5,
            ErrorType.API_TIMEOUT: 10,
            ErrorType.API_RATE_LIMIT: 60
        }

        base_delay = base_delays.get(error_type, 5)
        # 謖・焚繝舌ャ繧ｯ繧ｪ繝・
        return min(base_delay * (2 ** (attempt_count - 1)), 300)  # 譛螟ｧ5蛻・


# 菴ｿ逕ｨ萓九→繝・せ繝育畑繧ｳ繝ｼ繝・
if __name__ == '__main__':
    """
    ErrorHandler縺ｮ繝・せ繝亥ｮ溯｡・
    """
    print("ErrorHandler 繝・せ繝亥ｮ溯｡・)
    print("=" * 40)

    # ErrorHandler繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ菴懈・
    error_handler = ErrorHandler()

    # 繝・せ繝育畑繧ｨ繝ｩ繝ｼ
    import requests

    # 繝ｬ繝ｼ繝亥宛髯舌お繝ｩ繝ｼ縺ｮ繝・せ繝・
    print("1. 繝ｬ繝ｼ繝亥宛髯舌お繝ｩ繝ｼ繝・せ繝・")
    rate_limit_error = requests.exceptions.HTTPError()
    rate_limit_error.response = type('Response', (), {'status_code': 429})()

    error_type, error_info = error_handler.handle_api_error('weather', rate_limit_error, True)
    user_message = error_handler.create_user_friendly_message(error_info)
    print(f"   繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・ {error_type.value}")
    print(f"   繝ｦ繝ｼ繧ｶ繝ｼ繝｡繝・そ繝ｼ繧ｸ: {user_message['message']}")
    print(f"   謠先｡・ {user_message['suggestion']}")

    # 繝阪ャ繝医Ρ繝ｼ繧ｯ繧ｨ繝ｩ繝ｼ縺ｮ繝・せ繝・
    print("\n2. 繝阪ャ繝医Ρ繝ｼ繧ｯ繧ｨ繝ｩ繝ｼ繝・せ繝・")
    network_error = requests.exceptions.ConnectionError("Connection failed")

    location_error = error_handler.handle_location_error(network_error, False)
    print(f"   繝｡繝・そ繝ｼ繧ｸ: {location_error['message']}")
    print(f"   謠先｡・ {location_error['suggestion']}")

    # 繧ｨ繝ｩ繝ｼ邨ｱ險医・陦ｨ遉ｺ
    print("\n3. 繧ｨ繝ｩ繝ｼ邨ｱ險・")
    stats = error_handler.get_error_statistics()
    for error_type, count in stats.items():
        print(f"   {error_type}: {count}蝗・)

    print("\n繝・せ繝亥ｮ御ｺ・)
