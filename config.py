import json

# 读取配置文件
with open('config.json', 'r', encoding='utf-8') as f:
    _config = json.load(f)

# 导出配置
db_path = _config['DB_PATH']
default_ai_config_file = _config['DEFAULT_AI_CONFIG_FILE']
default_model_id = _config['DEFAULT_MODEL_ID']
stock_filter_config = _config['STOCK_FILTER_CONFIG']
default_data_settings = _config.get('DEFAULT_DATA_SETTINGS', {
    'autoRefresh': True,
    'refreshInterval': 30,
    'dataSource': 'akshare'
})
default_display_settings = _config.get('DEFAULT_DISPLAY_SETTINGS', {
    'theme': 'light',
    'showVolume': True,
    'showMarketCap': True,
    'sortBy': 'change_pct'
})
default_notify_settings = _config.get('DEFAULT_NOTIFY_SETTINGS', {
    'enableNotification': False,
    'notificationThreshold': 5.0,
    'notificationSound': True
})

# 提供一个获取配置的函数
def get_config():
    return _config
