import sqlite3
import json
from typing import Optional, List, Dict, Any

class DatabaseService:
    def __init__(self, db_path: str = 'data.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建设置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL
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
            
            # 创建用户表（如果需要）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def get_setting(self, key: str) -> Optional[Any]:
        """获取设置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
    
    def set_setting(self, key: str, value: Any) -> bool:
        """设置设置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value) 
                    VALUES (?, ?)
                ''', (key, json.dumps(value)))
                conn.commit()
                return True
            except Exception as e:
                print(f"设置设置失败: {e}")
                return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """获取所有设置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT key, value FROM settings')
            results = cursor.fetchall()
            settings = {}
            for key, value in results:
                settings[key] = json.loads(value)
            return settings
    
    def add_to_watchlist(self, code: str, name: str) -> bool:
        """添加自选股"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO watchlist (code, name) 
                    VALUES (?, ?)
                ''', (code, name))
                conn.commit()
                return True
            except Exception as e:
                print(f"添加自选股失败: {e}")
                return False
    
    def remove_from_watchlist(self, code: str) -> bool:
        """移除自选股"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM watchlist WHERE code = ?', (code,))
                conn.commit()
                return True
            except Exception as e:
                print(f"移除自选股失败: {e}")
                return False
    
    def get_watchlist(self) -> List[Dict[str, Any]]:
        """获取自选股列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT code, name, added_at FROM watchlist ORDER BY added_at DESC')
            results = cursor.fetchall()
            watchlist = []
            for code, name, added_at in results:
                watchlist.append({
                    'code': code,
                    'name': name,
                    'added_at': added_at
                })
            return watchlist
    
    def clear_watchlist(self) -> bool:
        """清空自选股"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM watchlist')
                conn.commit()
                return True
            except Exception as e:
                print(f"清空自选股失败: {e}")
                return False
    
    def close(self):
        """关闭数据库连接"""
        # SQLite3的连接在with语句结束后会自动关闭
        pass