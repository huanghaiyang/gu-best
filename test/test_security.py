#!/usr/bin/env python3
"""
安全服务测试
"""
import unittest
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.security_service import SecurityService
from services.encryption_service import encryption_service
from services.csrf_service import csrf_service

class TestSecurityService(unittest.TestCase):
    """安全服务测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.security_service = SecurityService()
    
    def test_validate_stock_code(self):
        """测试股票代码验证"""
        # 测试有效的股票代码
        self.assertTrue(self.security_service.validate_stock_code('600000'))
        self.assertTrue(self.security_service.validate_stock_code('000001'))
        self.assertTrue(self.security_service.validate_stock_code('AAPL'))
        self.assertTrue(self.security_service.validate_stock_code('MSFT'))
        self.assertTrue(self.security_service.validate_stock_code('BABA'))
        
        # 测试无效的股票代码
        self.assertFalse(self.security_service.validate_stock_code('invalid@'))
        self.assertFalse(self.security_service.validate_stock_code(''))
    
    def test_validate_url(self):
        """测试URL验证"""
        # 测试有效的URL
        self.assertTrue(self.security_service.validate_url('https://api.openai.com/v1'))
        self.assertTrue(self.security_service.validate_url('http://localhost:8000'))
        
        # 测试无效的URL
        self.assertFalse(self.security_service.validate_url('invalid'))
        self.assertFalse(self.security_service.validate_url(''))
    
    def test_validate_api_key(self):
        """测试API密钥验证"""
        # 测试有效的API密钥
        self.assertTrue(self.security_service.validate_api_key('sk-1234567890abcdef1234567890abcdef'))
        
        # 测试无效的API密钥
        self.assertFalse(self.security_service.validate_api_key('invalid'))
        self.assertFalse(self.security_service.validate_api_key(''))
    
    def test_validate_temperature(self):
        """测试温度值验证"""
        # 测试有效的温度值
        self.assertTrue(self.security_service.validate_temperature(0.0))
        self.assertTrue(self.security_service.validate_temperature(0.7))
        self.assertTrue(self.security_service.validate_temperature(1.0))
        
        # 测试无效的温度值
        self.assertFalse(self.security_service.validate_temperature(-0.1))
        self.assertFalse(self.security_service.validate_temperature(1.1))
        self.assertFalse(self.security_service.validate_temperature('invalid'))
    
    def test_validate_max_tokens(self):
        """测试最大tokens值验证"""
        # 测试有效的最大tokens值
        self.assertTrue(self.security_service.validate_max_tokens(100))
        self.assertTrue(self.security_service.validate_max_tokens(2048))
        
        # 测试无效的最大tokens值
        self.assertFalse(self.security_service.validate_max_tokens(0))
        self.assertFalse(self.security_service.validate_max_tokens(-1))
        self.assertFalse(self.security_service.validate_max_tokens('invalid'))
    
    def test_sanitize_input(self):
        """测试输入 sanitize"""
        # 测试需要 sanitize 的输入
        unsanitized_input = '<script>alert("XSS")</script>'
        sanitized = self.security_service.sanitize_input(unsanitized_input)
        self.assertNotIn('<script>', sanitized)
        self.assertNotIn('</script>', sanitized)
    
    def test_sanitize_object(self):
        """测试对象 sanitize"""
        # 测试需要 sanitize 的对象
        unsanitized_obj = {
            'code': '600000',
            'name': '<script>alert("XSS")</script>',
            'description': '测试<script>标签</script>'
        }
        sanitized = self.security_service.sanitize_object(unsanitized_obj)
        self.assertNotIn('<script>', sanitized.get('name', ''))
        self.assertNotIn('</script>', sanitized.get('description', ''))
    
    def test_validate_request_data(self):
        """测试请求数据验证"""
        # 测试有效的请求数据
        valid_data = {
            'modelId': 'volcengine',
            'modelName': 'doubao'
        }
        result = self.security_service.validate_request_data(valid_data, ['modelId', 'modelName'])
        self.assertIsNone(result)
        
        # 测试无效的请求数据
        invalid_data = {
            'modelId': 'volcengine'
        }
        result = self.security_service.validate_request_data(invalid_data, ['modelId', 'modelName'])
        self.assertIsInstance(result, str)
    
    def test_encryption_service(self):
        """测试加密服务"""
        # 测试加密和解密
        test_string = 'test string'
        encrypted = encryption_service.encrypt(test_string)
        decrypted = encryption_service.decrypt(encrypted)
        self.assertEqual(test_string, decrypted)
    
    def test_csrf_service(self):
        """测试CSRF服务"""
        # 测试生成和验证CSRF令牌
        user_identifier = 'test_user'
        token = csrf_service.generate_token(user_identifier)
        self.assertTrue(csrf_service.validate_token(token, user_identifier))
        # 测试无效的令牌
        self.assertFalse(csrf_service.validate_token('invalid_token', user_identifier))

if __name__ == '__main__':
    unittest.main()
