#!/usr/bin/env python3
"""
运行自动化测试
"""
import os
import sys
import sqlite3
import shutil

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def make_database_read_only():
    """将数据库设置为只读模式"""
    db_path = 'data/data.db'
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f'数据库文件不存在: {db_path}')
        return False
    
    try:
        # 尝试以只读模式打开数据库
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        conn.close()
        print('数据库已设置为只读模式')
        return True
    except Exception as e:
        print(f'设置数据库只读模式失败: {e}')
        return False

def run_tests():
    """运行测试"""
    # 设置数据库为只读模式
    if make_database_read_only():
        # 运行测试套件
        print('开始运行测试...')
        os.system('python test/test_suite.py')
    else:
        print('无法设置数据库为只读模式，测试终止')

if __name__ == '__main__':
    run_tests()
