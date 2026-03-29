#!/usr/bin/env python3
"""
数据库服务测试
"""
import unittest
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_service import DatabaseService

class TestDatabaseService(unittest.TestCase):
    """数据库服务测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.db_service = DatabaseService()
    
    def test_get_all_ai_settings(self):
        """测试获取所有AI模型配置"""
        settings = self.db_service.get_all_ai_settings()
        self.assertIsInstance(settings, list)
        # 至少应该有一个默认模型配置
        self.assertGreaterEqual(len(settings), 1)
    
    def test_get_ai_setting(self):
        """测试获取特定AI模型配置"""
        # 测试获取默认模型配置
        setting = self.db_service.get_ai_setting('volcengine')
        self.assertIsInstance(setting, dict)
        self.assertEqual(setting.get('modelId'), 'volcengine')
    
    def test_get_active_ai_setting(self):
        """测试获取激活的AI模型配置"""
        setting = self.db_service.get_active_ai_setting()
        if setting:
            self.assertIsInstance(setting, dict)
            self.assertEqual(setting.get('isActive'), 1)
    
    def test_get_all_settings(self):
        """测试获取所有设置"""
        settings = self.db_service.get_all_settings()
        self.assertIsInstance(settings, dict)
    
    def test_get_watchlist(self):
        """测试获取自选股列表"""
        watchlist = self.db_service.get_watchlist()
        self.assertIsInstance(watchlist, list)

if __name__ == '__main__':
    unittest.main()
