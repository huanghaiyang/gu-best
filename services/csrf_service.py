"""CSRF（跨站请求伪造）防护服务"""
import os
import hmac
import hashlib
import time
from typing import Optional

class CSRFService:
    """CSRF防护服务"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or self._get_default_secret()
        self.token_ttl = 3600  # 令牌有效期（秒）
    
    def _get_default_secret(self) -> str:
        """获取默认密钥"""
        env_secret = os.environ.get('CSRF_SECRET_KEY')
        if env_secret:
            return env_secret
        return "stock_analysis_csrf_secret_2024"
    
    def generate_token(self, user_identifier: str = "anonymous") -> str:
        """生成CSRF令牌
        
        Args:
            user_identifier: 用户标识符，用于增加令牌的唯一性
        
        Returns:
            生成的CSRF令牌
        """
        timestamp = int(time.time())
        data = f"{user_identifier}:{timestamp}"
        
        # 使用HMAC-SHA256生成签名
        signature = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # 组合令牌：签名:时间戳:用户标识符
        token = f"{signature}:{timestamp}:{user_identifier}"
        return token
    
    def validate_token(self, token: str, user_identifier: str = None) -> bool:
        """验证CSRF令牌
        
        Args:
            token: 要验证的CSRF令牌
            user_identifier: 用户标识符，用于验证令牌的用户关联性
        
        Returns:
            令牌是否有效
        """
        if not token:
            return False
        
        try:
            parts = token.split(":")
            if len(parts) != 3:
                return False
            
            signature, timestamp_str, token_user_id = parts
            timestamp = int(timestamp_str)
            
            # 检查令牌是否过期
            current_time = int(time.time())
            if current_time - timestamp > self.token_ttl:
                return False
            
            # 如果提供了用户标识符，验证令牌是否属于该用户
            if user_identifier and token_user_id != user_identifier:
                return False
            
            # 重新生成签名并验证
            data = f"{token_user_id}:{timestamp}"
            expected_signature = hmac.new(
                self.secret_key.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False
    
    def get_token_for_request(self) -> str:
        """为当前请求生成CSRF令牌"""
        return self.generate_token()


# 全局CSRF服务实例
csrf_service = CSRFService()
