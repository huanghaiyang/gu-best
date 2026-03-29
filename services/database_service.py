import sqlite3
import json
from typing import Optional, List, Dict, Any
from config import db_path
from services.encryption_service import encryption_service

class DatabaseService:
    def __init__(self, db_path: str = db_path):
        self.db_path = db_path
    
    def get_setting(self, key: str) -> Optional[Any]:
        """获取设置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            if result:
                try:
                    return json.loads(result[0])
                except json.JSONDecodeError:
                    return result[0]
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
                try:
                    settings[key] = json.loads(value)
                except json.JSONDecodeError:
                    settings[key] = value
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
        pass
    
    def add_ai_setting(self, model_id: str, model_name: str, api_url: str, 
                     api_key: str = None, secret_key: str = None, 
                     temperature: float = 0.7, max_tokens: int = 2048, 
                     is_active: int = 0) -> bool:
        """添加AI模型配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                # 加密敏感信息
                encrypted_api_key = encryption_service.encrypt(api_key) if api_key else None
                encrypted_secret_key = encryption_service.encrypt(secret_key) if secret_key else None
                
                cursor.execute('''
                    INSERT OR REPLACE INTO ai_settings 
                    (modelId, modelName, apiUrl, apiKey, secretKey, temperature, maxTokens, isActive, updatedAt)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (model_id, model_name, api_url, encrypted_api_key, encrypted_secret_key, temperature, max_tokens, is_active))
                conn.commit()
                return True
            except Exception as e:
                print(f"添加AI设置失败: {e}")
                return False
    
    def update_ai_setting(self, model_id: str, model_name: str = None, api_url: str = None,
                       api_key: str = None, secret_key: str = None,
                       temperature: float = None, max_tokens: int = None,
                       is_active: int = None) -> bool:
        """更新AI模型配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                update_fields = []
                update_values = []
                
                if model_name is not None:
                    update_fields.append('modelName = ?')
                    update_values.append(model_name)
                if api_url is not None:
                    update_fields.append('apiUrl = ?')
                    update_values.append(api_url)
                if api_key is not None:
                    # 加密 API Key
                    encrypted_api_key = encryption_service.encrypt(api_key) if api_key else None
                    update_fields.append('apiKey = ?')
                    update_values.append(encrypted_api_key)
                if secret_key is not None:
                    # 加密 Secret Key
                    encrypted_secret_key = encryption_service.encrypt(secret_key) if secret_key else None
                    update_fields.append('secretKey = ?')
                    update_values.append(encrypted_secret_key)
                if temperature is not None:
                    update_fields.append('temperature = ?')
                    update_values.append(temperature)
                if max_tokens is not None:
                    update_fields.append('maxTokens = ?')
                    update_values.append(max_tokens)
                if is_active is not None:
                    update_fields.append('isActive = ?')
                    update_values.append(is_active)
                
                if update_fields:
                    update_fields.append('updatedAt = CURRENT_TIMESTAMP')
                    update_values.append(model_id)
                    
                    cursor.execute(f'''
                        UPDATE ai_settings 
                        SET {', '.join(update_fields)}
                        WHERE modelId = ?
                    ''', update_values)
                    conn.commit()
                    return True
                return False
            except Exception as e:
                print(f"更新AI设置失败: {e}")
                return False
    
    def get_ai_setting(self, model_id: str) -> Optional[Dict[str, Any]]:
        """获取指定AI模型配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT modelId, modelName, apiUrl, apiKey, secretKey, temperature, maxTokens, isActive, createdAt, updatedAt
                FROM ai_settings 
                WHERE modelId = ?
            ''', (model_id,))
            result = cursor.fetchone()
            if result:
                # 解密敏感信息
                decrypted_api_key = encryption_service.decrypt(result[3]) if result[3] else None
                decrypted_secret_key = encryption_service.decrypt(result[4]) if result[4] else None
                
                return {
                    'modelId': result[0],
                    'modelName': result[1],
                    'apiUrl': result[2],
                    'apiKey': decrypted_api_key,
                    'secretKey': decrypted_secret_key,
                    'temperature': result[5],
                    'maxTokens': result[6],
                    'isActive': result[7],
                    'createdAt': result[8],
                    'updatedAt': result[9]
                }
            return None
    
    def get_all_ai_settings(self) -> List[Dict[str, Any]]:
        """获取所有AI模型配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT modelId, modelName, apiUrl, apiKey, secretKey, temperature, maxTokens, isActive, createdAt, updatedAt
                FROM ai_settings 
                ORDER BY createdAt DESC
            ''')
            results = cursor.fetchall()
            ai_settings = []
            for result in results:
                # 解密敏感信息
                decrypted_api_key = encryption_service.decrypt(result[3]) if result[3] else None
                decrypted_secret_key = encryption_service.decrypt(result[4]) if result[4] else None
                
                ai_settings.append({
                    'modelId': result[0],
                    'modelName': result[1],
                    'apiUrl': result[2],
                    'apiKey': decrypted_api_key,
                    'secretKey': decrypted_secret_key,
                    'temperature': result[5],
                    'maxTokens': result[6],
                    'isActive': result[7],
                    'createdAt': result[8],
                    'updatedAt': result[9]
                })
            return ai_settings
    
    def get_active_ai_setting(self) -> Optional[Dict[str, Any]]:
        """获取当前激活的AI模型配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT modelId, modelName, apiUrl, apiKey, secretKey, temperature, maxTokens, isActive, createdAt, updatedAt
                FROM ai_settings 
                WHERE isActive = 1
                LIMIT 1
            ''')
            result = cursor.fetchone()
            if result:
                # 解密敏感信息
                decrypted_api_key = encryption_service.decrypt(result[3]) if result[3] else None
                decrypted_secret_key = encryption_service.decrypt(result[4]) if result[4] else None
                
                return {
                    'modelId': result[0],
                    'modelName': result[1],
                    'apiUrl': result[2],
                    'apiKey': decrypted_api_key,
                    'secretKey': decrypted_secret_key,
                    'temperature': result[5],
                    'maxTokens': result[6],
                    'isActive': result[7],
                    'createdAt': result[8],
                    'updatedAt': result[9]
                }
            return None
    
    def set_active_ai_model(self, model_id: str) -> bool:
        """设置激活的AI模型"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('UPDATE ai_settings SET isActive = 0')
                cursor.execute('UPDATE ai_settings SET isActive = 1 WHERE modelId = ?', (model_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"设置激活AI模型失败: {e}")
                return False
    
    def delete_ai_setting(self, model_id: str) -> bool:
        """删除AI模型配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM ai_settings WHERE modelId = ?', (model_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"删除AI设置失败: {e}")
                return False
