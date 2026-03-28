#!/usr/bin/env python3
"""
数据库管理脚本
用于清除和初始化数据库
"""
import os
import sys
import sqlite3
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import db_path, default_ai_config_file, default_model_id

def clear_database():
    """清除数据库文件"""
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"✓ 数据库文件 '{db_path}' 已清除")
            return True
        except Exception as e:
            print(f"✗ 清除数据库失败: {e}")
            return False
    else:
        print(f"! 数据库文件 '{db_path}' 不存在")
        return True


def create_tables(conn):
    """创建数据库表结构"""
    cursor = conn.cursor()
    
    # 创建设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL
        )
    ''')
    
    # 创建AI设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelId TEXT NOT NULL,
            modelName TEXT NOT NULL,
            apiUrl TEXT NOT NULL,
            apiKey TEXT,
            secretKey TEXT,
            temperature REAL DEFAULT 0.7,
            maxTokens INTEGER DEFAULT 2048,
            isActive INTEGER DEFAULT 0,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建自选股表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()


def init_ai_settings(conn):
    """初始化AI模型配置"""
    cursor = conn.cursor()
    
    # 检查是否已存在配置
    cursor.execute('SELECT COUNT(*) FROM ai_settings')
    if cursor.fetchone()[0] > 0:
        print("AI配置已存在，跳过初始化")
        return
    
    # 从defaultAIConfig.json读取配置
    try:
        with open(default_ai_config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 获取默认模型ID
        default_model = config.get('defaultModel')

        if not default_model:
            default_model = default_model_id
        
        # 插入所有模型配置
        for model in config.get('models', []):
            model_id = model.get('id', '')
            model_name = model.get('model', '')
            api_url = model.get('apiUrl', '')
            api_key = model.get('apiKey', '')
            secret_key = model.get('secretKey', '')
            
            # 插入到ai_settings表
            is_active = 1 if model_id == default_model else 0
            cursor.execute('''
                INSERT OR IGNORE INTO ai_settings 
                (modelId, modelName, apiUrl, apiKey, secretKey, temperature, maxTokens, isActive)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                model_id,
                model_name,
                api_url,
                api_key,
                secret_key,
                0.7,
                2048,
                is_active
            ))
        
        # 设置默认AI模型（只存储模型ID）
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value) 
            VALUES (?, ?)
        ''', ('currentAiModel', default_model))
        
        conn.commit()
        print("已从defaultAIConfig.json初始化AI模型配置")
    except Exception as e:
        print(f"读取defaultAIConfig.json失败: {e}")
        print("无法初始化AI配置，请检查defaultAIConfig.json文件是否存在且格式正确")


def init_database():
    """初始化数据库"""
    try:
        # 创建数据库连接
        with sqlite3.connect(db_path) as conn:
            # 创建表结构
            create_tables(conn)
            
            # 初始化AI配置
            init_ai_settings(conn)
        
        print(f"✓ 数据库已初始化: '{db_path}'")
        
        # 显示已创建的表
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"\n已创建的表 ({len(tables)}个):")
            for table in tables:
                print(f"  - {table[0]}")
            
            # 显示AI设置
            cursor.execute("SELECT modelId, modelName, isActive FROM ai_settings;")
            ai_settings = cursor.fetchall()
            if ai_settings:
                print(f"\nAI模型配置 ({len(ai_settings)}个):")
                for setting in ai_settings:
                    active_mark = " [激活]" if setting[2] else ""
                    print(f"  - {setting[0]}: {setting[1]}{active_mark}")
        
        return True
    except Exception as e:
        print(f"✗ 初始化数据库失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_database():
    """检查数据库是否存在，不存在则初始化"""
    if os.path.exists(db_path):
        print(f"✓ 数据库已存在: '{db_path}'")
        return True
    else:
        print(f"! 数据库不存在，正在初始化...")
        return init_database()


def dump_table(table_name=None):
    """打印指定数据库表的数据"""
    if not os.path.exists(db_path):
        print(f"✗ 数据库文件不存在: '{db_path}'")
        return False
    
    # 如果没有指定表名，显示所有可用表
    if table_name is None:
        if len(sys.argv) >= 3:
            table_name = sys.argv[2]
        else:
            # 显示所有表
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
                tables = cursor.fetchall()
                print(f"\n数据库中的表 ({len(tables)}个):")
                print("-" * 40)
                for table in tables:
                    # 获取每表的记录数
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"  {table[0]:<20} ({count} 条记录)")
                print("-" * 40)
                print(f"\n使用: npm run db:dump -- <表名>")
                print(f"示例: npm run db:dump -- ai_settings")
            return True
    
    # 打印指定表的数据
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
            if not cursor.fetchone():
                print(f"✗ 表不存在: '{table_name}'")
                return False
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # 获取数据
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            print(f"\n表: {table_name}")
            print("=" * 80)
            
            if not rows:
                print("(空表)")
            else:
                # 打印表头
                header = " | ".join(f"{name:<15}" for name in column_names)
                print(header)
                print("-" * len(header))
                
                # 打印数据行
                for row in rows:
                    row_str = " | ".join(f"{str(val)[:15]:<15}" for val in row)
                    print(row_str)
                
                print(f"\n共 {len(rows)} 条记录")
            
            print("=" * 80)
            return True
            
    except Exception as e:
        print(f"✗ 读取表数据失败: {e}")
        return False


def show_help():
    """显示帮助信息"""
    print("""
数据库管理工具

用法:
  python scripts/db_manage.py <命令>

命令:
  check   检查数据库是否存在，不存在则初始化
  clear   清除数据库文件
  init    初始化数据库（创建表和默认数据）
  reset   清除并重新初始化数据库
  dump    打印指定表的数据（不指定表名则列出所有表）

示例:
  npm run db:check              # 检查数据库
  npm run db:clear              # 清除数据库
  npm run db:init               # 初始化数据库
  npm run db:reset              # 重置数据库
  npm run db:dump               # 列出所有表
  npm run db:dump -- ai_settings # 打印ai_settings表数据
""")


def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'check':
        check_database()
    elif command == 'clear':
        clear_database()
    elif command == 'init':
        init_database()
    elif command == 'reset':
        if clear_database():
            print()
            init_database()
    elif command == 'dump':
        dump_table()
    else:
        print(f"未知命令: {command}")
        show_help()


if __name__ == '__main__':
    main()
