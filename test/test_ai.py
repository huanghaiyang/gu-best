#!/usr/bin/env python3
"""
AI服务测试
"""
import unittest
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_service import AIService
from services.database_service import DatabaseService

class TestAIService(unittest.TestCase):
    """AI服务测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.ai_service = AIService()
        self.db_service = DatabaseService()
    
    def test_analyze_stock(self):
        """测试股票分析功能"""
        # 测试数据
        stock_code = '600000'
        stock_name = '浦发银行'
        stock_data = {
            'code': stock_code,
            'name': stock_name,
            'price': 10.5,
            'change_pct': 1.2,
            'volume': 1000000,
            'market_cap': 300000000000,
            'volume_ratio': 1.5,
            'turnover_rate': 5.0,
            'score': 85.5
        }
        
        # 测试分析功能
        result = self.ai_service.analyze_stock(stock_code, stock_name, stock_data)
        self.assertIsInstance(result, dict)
        self.assertIn('stock_code', result)
        self.assertIn('stock_name', result)
        self.assertIn('analysis', result)
        self.assertIn('recommendation', result)
        self.assertIn('confidence', result)
    
    def test_batch_analyze_stocks(self):
        """测试批量分析股票功能"""
        # 测试数据
        stocks = [
            {
                'code': '600000',
                'name': '浦发银行',
                'price': 10.5,
                'change_pct': 1.2,
                'volume': 1000000,
                'market_cap': 300000000000,
                'volume_ratio': 1.5,
                'turnover_rate': 5.0,
                'score': 85.5
            },
            {
                'code': '000001',
                'name': '平安银行',
                'price': 15.8,
                'change_pct': 0.8,
                'volume': 800000,
                'market_cap': 250000000000,
                'volume_ratio': 1.2,
                'turnover_rate': 3.5,
                'score': 75.0
            }
        ]
        
        # 测试批量分析功能
        results = self.ai_service.batch_analyze_stocks(stocks)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), len(stocks))
    
    def test_test_model(self):
        """测试模型测试功能"""
        # 从数据库获取豆包配置
        all_settings = self.db_service.get_all_ai_settings()
        doubao_config = None
        for setting in all_settings:
            if setting['modelId'] == 'volcengine':
                doubao_config = setting
                break
        
        if doubao_config:
            # 构建测试配置
            model = 'volcengine'
            params = {
                'temperature': doubao_config.get('temperature', 0.7),
                'maxTokens': doubao_config.get('maxTokens', 2048)
            }
            api_config = {
                'apiUrl': doubao_config.get('apiUrl', ''),
                'apiKey': doubao_config.get('apiKey', ''),
                'secretKey': doubao_config.get('secretKey', None),
                'model': doubao_config.get('modelName', '')
            }
            
            # 测试模型
            result = self.ai_service.test_model(model, params, api_config)
            self.assertIsInstance(result, dict)
            self.assertIn('status', result)

if __name__ == '__main__':
    unittest.main()
