"""后端安全服务"""
import re
import json
from typing import Optional, Dict, Any, List

class SecurityService:
    """安全服务类"""
    
    @staticmethod
    def is_empty(value) -> bool:
        """检查值是否为空"""
        if value is None:
            return True
        if isinstance(value, str):
            return value.strip() == ''
        if isinstance(value, (list, dict)):
            return len(value) == 0
        return False
    
    @staticmethod
    def validate_stock_code(code: str) -> bool:
        """验证股票代码格式"""
        if SecurityService.is_empty(code):
            return False
        # 股票代码格式：字母或数字，长度1-10
        # 支持纯数字（如A股代码）、纯字母（如美股代码）或字母数字组合
        pattern = r'^[A-Z0-9]{1,10}$'
        return bool(re.match(pattern, code, re.IGNORECASE))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """验证URL格式"""
        if SecurityService.is_empty(url):
            return False
        # 简单的URL验证，支持本地URL
        pattern = r'^https?://(localhost|127\.0\.0\.1|[\w\-]+(\.[\w\-]+)+)(:[0-9]+)?([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """验证API密钥格式"""
        if SecurityService.is_empty(api_key):
            return False
        # API密钥通常是字母数字组合，长度10-50
        pattern = r'^[A-Za-z0-9_-]{10,50}$'
        return bool(re.match(pattern, api_key))
    
    @staticmethod
    def validate_temperature(temperature: float) -> bool:
        """验证温度值（0-1之间）"""
        try:
            temp = float(temperature)
            return 0 <= temp <= 1
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_max_tokens(max_tokens: int) -> bool:
        """验证最大tokens值"""
        try:
            tokens = int(max_tokens)
            return tokens > 0 and tokens <= 100000
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_model_id(model_id: str) -> bool:
        """验证模型ID"""
        if SecurityService.is_empty(model_id):
            return False
        # 模型ID格式：字母、数字、下划线，长度3-30
        pattern = r'^[A-Za-z0-9_]{3,30}$'
        return bool(re.match(pattern, model_id))
    
    @staticmethod
    def validate_model_name(model_name: str) -> bool:
        """验证模型名称"""
        if SecurityService.is_empty(model_name):
            return False
        # 模型名称长度限制：1-50个字符
        length = len(model_name.strip())
        return 1 <= length <= 50
    
    @staticmethod
    def validate_search_query(query: str) -> bool:
        """验证搜索查询"""
        if SecurityService.is_empty(query):
            return False
        # 搜索查询长度限制：1-50个字符
        length = len(query.strip())
        return 1 <= length <= 50
    
    @staticmethod
    def validate_integer(value) -> bool:
        """验证是否为整数"""
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_positive_integer(value) -> bool:
        """验证是否为正整数"""
        try:
            num = int(value)
            return num > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_length(value: str, min_length: int, max_length: int) -> bool:
        """验证字符串长度"""
        if not isinstance(value, str):
            return False
        length = len(value.strip())
        return min_length <= length <= max_length
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """清理输入，防止SQL注入和XSS"""
        if not input_str or not isinstance(input_str, str):
            return ''
        # 移除潜在的危险字符
        dangerous_chars = [';', '--', '/*', '*/', '\'', '"', '<', '>']
        for char in dangerous_chars:
            input_str = input_str.replace(char, '')
        return input_str.strip()
    
    @staticmethod
    def sanitize_object(obj: Any) -> Any:
        """递归清理对象中的所有字符串属性"""
        if not obj or not isinstance(obj, dict):
            return obj
        
        sanitized = {}
        for key, value in obj.items():
            if isinstance(value, str):
                sanitized[key] = SecurityService.sanitize_input(value)
            elif isinstance(value, dict):
                sanitized[key] = SecurityService.sanitize_object(value)
            elif isinstance(value, list):
                sanitized[key] = [SecurityService.sanitize_object(item) if isinstance(item, dict) else item for item in value]
            else:
                sanitized[key] = value
        return sanitized
    
    @staticmethod
    def validate_request_data(data: Dict[str, Any], required_fields: List[str]) -> Optional[str]:
        """验证请求数据是否包含所有必需字段"""
        if not data or not isinstance(data, dict):
            return '请求数据格式不正确'
        
        for field in required_fields:
            if field not in data or SecurityService.is_empty(data[field]):
                return f'缺少必需字段: {field}'
        
        return None
    
    @staticmethod
    def validate_stock_data(stock_data: Dict[str, Any]) -> Optional[str]:
        """验证股票数据"""
        if not stock_data or not isinstance(stock_data, dict):
            return '股票数据格式不正确'
        
        # 验证股票代码
        if 'code' in stock_data:
            if not SecurityService.validate_stock_code(stock_data['code']):
                return '股票代码格式不正确'
        
        # 验证股票名称
        if 'name' in stock_data:
            if not SecurityService.validate_length(stock_data['name'], 1, 50):
                return '股票名称长度不正确'
        
        return None


# 全局安全服务实例
security_service = SecurityService()
