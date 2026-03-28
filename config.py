import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    STOCK_FILTER_CONFIG = {
        'min_market_cap': 50,
        'min_volume_ratio': 1.5,
        'min_turnover_rate': 3.0,
        'min_rise_days': 3,
        'top_n_stocks': 10
    }
