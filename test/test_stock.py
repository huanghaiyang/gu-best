#!/usr/bin/env python3
"""
股票服务测试
"""
import unittest
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.stock_service import StockService

class TestStockService(unittest.TestCase):
    """股票服务测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.stock_service = StockService()
    
    def test_search_stocks(self):
        """测试搜索股票"""
        # 测试代码搜索
        result = self.stock_service.search_stocks('600519')
        self.assertIsInstance(result, list)
        
        # 测试名称搜索
        result = self.stock_service.search_stocks('浦发')
        self.assertIsInstance(result, list)
    
    def test_get_hot_sectors(self):
        """测试获取热门板块"""
        result = self.stock_service.get_sectors()
        self.assertIsInstance(result, list)
    
    def test_get_sector_stocks(self):
        """测试获取板块成分股"""
        # 测试获取板块成分股
        sectors = self.stock_service.get_sectors()
        if sectors:
            sector_code = sectors[0].get('code')
            if sector_code:
                result = self.stock_service.get_sector_stocks(sector_code)
                self.assertIsInstance(result, list)
    
    def test_screen_leader_stocks(self):
        """测试筛选龙头股"""
        # 测试默认参数
        result = self.stock_service.screen_leader_stocks()
        self.assertIsInstance(result, list)
        
        # 测试自定义参数
        result = self.stock_service.screen_leader_stocks(top_n=10)
        self.assertIsInstance(result, list)
    
    def test_get_stock_detail(self):
        """测试获取股票详情"""
        result = self.stock_service.get_stock_detail('600519')
        self.assertIsInstance(result, dict)
        self.assertIn('code', result)
        self.assertIn('name', result)
    
    def test_get_stock_history(self):
        """测试获取股票历史数据"""
        result = self.stock_service.get_stock_history('600519', days=7)
        self.assertIsInstance(result, list)
    
    def test_get_index_data(self):
        """测试获取指数数据"""
        result = self.stock_service.get_index_data()
        self.assertIsInstance(result, dict)
        self.assertIn('sh', result)
        self.assertIn('sz', result)
        self.assertIn('cy', result)
        self.assertIn('kc', result)
    
    def test_get_quote(self):
        """测试获取股票实时行情"""
        result = self.stock_service.get_quote('600519')
        self.assertIsInstance(result, dict)
        self.assertIn('code', result)
        self.assertIn('name', result)
        self.assertIn('price', result)

if __name__ == '__main__':
    unittest.main()
