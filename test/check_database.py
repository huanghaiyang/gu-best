#!/usr/bin/env python3
"""
检查数据库中的豆包配置
"""
import os
import sys
import sqlite3
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.encryption_service import encryption_service

db_path = 'data/data.db'

def check_ai_settings():
    """检查AI模型配置"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT modelId, modelName, apiUrl, apiKey, secretKey, temperature, maxTokens, isActive, createdAt, updatedAt
                FROM ai_settings 
                ORDER BY createdAt DESC
            ''')
            results = cursor.fetchall()
            
            print('AI模型配置:')
            print('-' * 80)
            
            for result in results:
                model_id, model_name, api_url, api_key, secret_key, temperature, max_tokens, is_active, created_at, updated_at = result
                
                # 解密敏感信息
                decrypted_api_key = encryption_service.decrypt(api_key) if api_key else None
                decrypted_secret_key = encryption_service.decrypt(secret_key) if secret_key else None
                
                print(f'模型ID: {model_id}')
                print(f'模型名称: {model_name}')
                print(f'API URL: {api_url}')
                print(f'API Key: {decrypted_api_key[:20]}...' if decrypted_api_key else 'API Key: None')
                print(f'Secret Key: {decrypted_secret_key[:20]}...' if decrypted_secret_key else 'Secret Key: None')
                print(f'温度: {temperature}')
                print(f'最大tokens: {max_tokens}')
                print(f'是否激活: {is_active}')
                print(f'创建时间: {created_at}')
                print(f'更新时间: {updated_at}')
                print('-' * 80)
                
    except Exception as e:
        print(f'检查数据库失败: {e}')

if __name__ == '__main__':
    check_ai_settings()
