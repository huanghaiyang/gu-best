import json

# 读取配置文件
with open('config.json', 'r', encoding='utf-8') as f:
    _config = json.load(f)

# 导出配置
db_path = _config['DB_PATH']
default_ai_config_file = _config['DEFAULT_AI_CONFIG_FILE']
default_model_id = _config['DEFAULT_MODEL_ID']
stock_filter_config = _config['STOCK_FILTER_CONFIG']

# 提供一个获取配置的函数
def get_config():
    return _config
