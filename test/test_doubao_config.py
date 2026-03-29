#!/usr/bin/env python3
"""
测试豆包配置是否正确
"""
import os
import sys
import requests
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_service import AIService
from services.database_service import DatabaseService

def test_doubao_config():
    """测试豆包配置"""
    try:
        # 从数据库中获取豆包配置
        db_service = DatabaseService()
        
        # 获取所有AI模型配置
        all_settings = db_service.get_all_ai_settings()
        
        # 找到豆包（volcengine）配置
        doubao_config = None
        for setting in all_settings:
            if setting['modelId'] == 'volcengine':
                doubao_config = setting
                break
        
        if not doubao_config:
            print('❌ 未找到豆包配置')
            return
        
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
        
        print('测试豆包配置...')
        print(f'模型: {model}')
        print(f'API URL: {api_config.get("apiUrl")}')
        print(f'模型名称: {api_config.get("model")}')
        print(f'API Key: {api_config.get("apiKey")[:20]}...' if api_config.get("apiKey") else 'API Key: None')
        
        # 验证配置是否完整
        if not api_config.get('apiUrl') or not api_config.get('apiKey') or not api_config.get('model'):
            print('❌ 豆包配置不完整')
            return
        
        # 创建AI服务实例
        ai_service = AIService()
        
        # 测试模型
        result = ai_service.test_model(model, params, api_config)
        print(f'测试结果: {result}')
        
        if result.get('status') == 'success':
            print('✅ 豆包配置测试成功')
        else:
            print('❌ 豆包配置测试失败')
            print(f'错误信息: {result.get("message")}')
            
    except Exception as e:
        print(f'测试过程中发生异常: {e}')

if __name__ == '__main__':
    test_doubao_config()
