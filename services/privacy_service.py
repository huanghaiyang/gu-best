"""敏感信息保护服务"""
import re
import os
from typing import Dict, Any, Optional

class PrivacyService:
    """敏感信息保护服务"""
    
    # 敏感信息模式
    SENSITIVE_PATTERNS = {
        'api_key': r'(?i)(api[_\s-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{10,50})["\']?',
        'secret_key': r'(?i)(secret[_\s-]?key|secretkey)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{10,50})["\']?',
        'password': r'(?i)(password|passwd)\s*[:=]\s*["\']?([^"\']+)"\']?',
        'token': r'(?i)(token|auth[_\s-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{10,50})["\']?',
        'credit_card': r'(?i)(credit[_\s-]?card|cc)\s*[:=]\s*["\']?([0-9]{13,16})["\']?',
        'phone': r'(?i)(phone|mobile)\s*[:=]\s*["\']?([0-9]{10,15})["\']?',
        'email': r'(?i)(email)\s*[:=]\s*["\']?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})["\']?',
    }
    
    @staticmethod
    def mask_sensitive_info(text: str) -> str:
        """脱敏敏感信息
        
        Args:
            text: 要处理的文本
        
        Returns:
            脱敏后的文本
        """
        if not text or not isinstance(text, str):
            return text
        
        masked_text = text
        for pattern_name, pattern in PrivacyService.SENSITIVE_PATTERNS.items():
            # 替换敏感信息
            masked_text = re.sub(
                pattern,
                lambda m: f"{m.group(1)}='***MASKED***'",
                masked_text
            )
        
        return masked_text
    
    @staticmethod
    def mask_dict_sensitive_info(data: Dict[str, Any]) -> Dict[str, Any]:
        """递归脱敏字典中的敏感信息
        
        Args:
            data: 要处理的字典
        
        Returns:
            脱敏后的字典
        """
        if not data or not isinstance(data, dict):
            return data
        
        masked_data = {}
        for key, value in data.items():
            # 检查键名是否包含敏感信息
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in ['api', 'secret', 'password', 'token']):
                masked_data[key] = '***MASKED***'
            elif isinstance(value, str):
                masked_data[key] = PrivacyService.mask_sensitive_info(value)
            elif isinstance(value, dict):
                masked_data[key] = PrivacyService.mask_dict_sensitive_info(value)
            elif isinstance(value, list):
                masked_data[key] = [
                    PrivacyService.mask_dict_sensitive_info(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                masked_data[key] = value
        
        return masked_data
    
    @staticmethod
    def sanitize_log_message(message: str) -> str:
        """清理日志消息中的敏感信息
        
        Args:
            message: 日志消息
        
        Returns:
            清理后的日志消息
        """
        return PrivacyService.mask_sensitive_info(message)
    
    @staticmethod
    def sanitize_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """清理请求数据中的敏感信息
        
        Args:
            data: 请求数据
        
        Returns:
            清理后的请求数据
        """
        return PrivacyService.mask_dict_sensitive_info(data)
    
    @staticmethod
    def is_sensitive_key(key: str) -> bool:
        """检查键名是否包含敏感信息
        
        Args:
            key: 键名
        
        Returns:
            是否为敏感键
        """
        sensitive_keys = [
            'api', 'secret', 'password', 'token', 
            'key', 'credential', 'auth', 'pass'
        ]
        key_lower = key.lower()
        return any(sensitive in key_lower for sensitive in sensitive_keys)
    
    @staticmethod
    def get_env_variable(name: str, default: Optional[str] = None) -> Optional[str]:
        """获取环境变量，防止泄露
        
        Args:
            name: 环境变量名称
            default: 默认值
        
        Returns:
            环境变量值
        """
        value = os.environ.get(name, default)
        if value and PrivacyService.is_sensitive_key(name):
            # 不记录敏感环境变量的值
            return value
        return value
    
    @staticmethod
    def redact_sensitive_headers(headers: Dict[str, str]) -> Dict[str, str]:
        """脱敏请求头中的敏感信息
        
        Args:
            headers: 请求头
        
        Returns:
            脱敏后的请求头
        """
        if not headers or not isinstance(headers, dict):
            return headers
        
        redacted_headers = {}
        for key, value in headers.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in ['authorization', 'token', 'api', 'secret']):
                redacted_headers[key] = '***MASKED***'
            else:
                redacted_headers[key] = value
        
        return redacted_headers


# 全局隐私服务实例
privacy_service = PrivacyService()
