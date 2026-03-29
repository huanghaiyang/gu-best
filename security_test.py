#!/usr/bin/env python3
"""
安全测试工具
用于测试系统的安全措施
"""
import sys
import requests
import json
from services.security_service import security_service
from services.privacy_service import privacy_service
from services.csrf_service import csrf_service

class SecurityTester:
    """安全测试类"""
    
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.csrf_token = None
    
    def get_csrf_token(self):
        """获取CSRF令牌"""
        try:
            response = requests.get(f'{self.base_url}/api/csrf-token')
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.csrf_token = data.get('token')
                    print('✅ 获取CSRF令牌成功')
                    return True
            print('❌ 获取CSRF令牌失败')
            return False
        except Exception as e:
            print(f'❌ 获取CSRF令牌异常: {e}')
            return False
    
    def test_csrf_protection(self):
        """测试CSRF保护"""
        print('\n=== 测试CSRF保护 ===')
        
        # 测试没有CSRF令牌的请求
        try:
            response = requests.post(f'{self.base_url}/api/db/settings', json={
                'key': 'test',
                'value': 'test'
            })
            if response.status_code == 403:
                print('✅ CSRF保护生效: 无令牌请求被拒绝')
            else:
                print(f'❌ CSRF保护失效: 无令牌请求被接受 (状态码: {response.status_code})')
        except Exception as e:
            print(f'❌ CSRF测试异常: {e}')
        
        # 测试带有CSRF令牌的请求
        if self.csrf_token:
            try:
                response = requests.post(f'{self.base_url}/api/db/settings', 
                    json={
                        'key': 'test_csrf',
                        'value': 'test_value',
                        'csrf_token': self.csrf_token
                    },
                    headers={
                        'X-CSRF-Token': self.csrf_token,
                        'Content-Type': 'application/json'
                    }
                )
                if response.status_code == 200:
                    print('✅ CSRF保护正常: 带令牌请求被接受')
                else:
                    print(f'❌ CSRF保护异常: 带令牌请求被拒绝 (状态码: {response.status_code})')
            except Exception as e:
                print(f'❌ CSRF测试异常: {e}')
    
    def test_input_validation(self):
        """测试输入验证"""
        print('\n=== 测试输入验证 ===')
        
        # 测试股票代码验证
        test_codes = ['AAPL', '1234', 'INVALID-CODE', 'A', 'ABCDEFGHIJKLMNOP']
        for code in test_codes:
            result = security_service.validate_stock_code(code)
            status = '✅' if result else '❌'
            print(f'{status} 股票代码验证: {code} -> {result}')
        
        # 测试URL验证
        test_urls = ['https://api.openai.com', 'invalid-url', 'http://localhost:8000']
        for url in test_urls:
            result = security_service.validate_url(url)
            status = '✅' if result else '❌'
            print(f'{status} URL验证: {url} -> {result}')
        
        # 测试API Key验证
        test_keys = ['sk-1234567890abcdef', 'invalid', 'a' * 51]
        for key in test_keys:
            result = security_service.validate_api_key(key)
            status = '✅' if result else '❌'
            print(f'{status} API Key验证: {key[:10]}... -> {result}')
    
    def test_privacy_protection(self):
        """测试隐私保护"""
        print('\n=== 测试隐私保护 ===')
        
        # 测试敏感信息脱敏
        test_text = 'API Key: sk-1234567890abcdef, Password: mysecret'
        masked = privacy_service.mask_sensitive_info(test_text)
        print(f'原始文本: {test_text}')
        print(f'脱敏后: {masked}')
        if '***MASKED***' in masked:
            print('✅ 敏感信息脱敏成功')
        else:
            print('❌ 敏感信息脱敏失败')
        
        # 测试字典脱敏
        test_data = {
            'apiKey': 'sk-1234567890',
            'secretKey': 'secret123',
            'normalKey': 'value'
        }
        masked_data = privacy_service.mask_dict_sensitive_info(test_data)
        print(f'原始数据: {test_data}')
        print(f'脱敏后: {masked_data}')
        if masked_data.get('apiKey') == '***MASKED***' and masked_data.get('secretKey') == '***MASKED***':
            print('✅ 字典敏感信息脱敏成功')
        else:
            print('❌ 字典敏感信息脱敏失败')
    
    def test_api_endpoints(self):
        """测试API端点安全"""
        print('\n=== 测试API端点安全 ===')
        
        # 测试搜索API
        try:
            response = requests.get(f'{self.base_url}/api/stocks/search?query=AAPL')
            if response.status_code == 200:
                print('✅ 搜索API正常')
            else:
                print(f'❌ 搜索API异常 (状态码: {response.status_code})')
        except Exception as e:
            print(f'❌ 搜索API测试异常: {e}')
        
        # 测试K线数据API
        try:
            response = requests.get(f'{self.base_url}/api/stocks/kline?code=AAPL')
            if response.status_code == 200:
                print('✅ K线数据API正常')
            else:
                print(f'❌ K线数据API异常 (状态码: {response.status_code})')
        except Exception as e:
            print(f'❌ K线数据API测试异常: {e}')
    
    def run_all_tests(self):
        """运行所有测试"""
        print('开始安全测试...')
        print(f'测试目标: {self.base_url}')
        
        # 获取CSRF令牌
        self.get_csrf_token()
        
        # 运行各项测试
        self.test_csrf_protection()
        self.test_input_validation()
        self.test_privacy_protection()
        self.test_api_endpoints()
        
        print('\n安全测试完成!')

if __name__ == '__main__':
    # 解析命令行参数
    base_url = 'http://localhost:8000'
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    tester = SecurityTester(base_url)
    tester.run_all_tests()
