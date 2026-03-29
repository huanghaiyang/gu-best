#!/usr/bin/env python3
"""
自动化测试套件
"""
import os
import sys
import unittest
import sqlite3

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_database import TestDatabaseService
from test_ai import TestAIService
from test_stock import TestStockService
from test_security import TestSecurityService

class ReadOnlyDatabaseMixin:
    """数据库只读测试混合类"""
    def setUp(self):
        """设置测试环境"""
        # 确保数据库连接为只读模式
        self.db_path = 'data/data.db'
        
    def test_database_read_only(self):
        """测试数据库是否为只读模式"""
        # 尝试连接数据库并执行读操作
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 执行读操作
            cursor.execute('SELECT COUNT(*) FROM ai_settings')
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            
            # 尝试执行写操作，应该失败
            try:
                cursor.execute('INSERT INTO ai_settings (modelId, modelName) VALUES (?, ?)', ('test', 'test'))
                conn.commit()
                # 如果执行成功，说明数据库不是只读模式
                self.fail('数据库允许写入操作')
            except sqlite3.OperationalError:
                # 预期的错误，说明数据库是只读模式
                pass

if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试用例
    suite.addTest(unittest.makeSuite(TestDatabaseService))
    suite.addTest(unittest.makeSuite(TestAIService))
    suite.addTest(unittest.makeSuite(TestStockService))
    suite.addTest(unittest.makeSuite(TestSecurityService))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 退出码
    sys.exit(not result.wasSuccessful())
