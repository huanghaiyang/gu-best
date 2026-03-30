from typing import Optional
from services.stock_data_provider import StockDataProvider
from services.eastmoney_api import EastmoneyAPI
from services.akshare_api import AkshareAPI


class StockDataFactory:
    """股票数据提供者工厂类"""
    
    @staticmethod
    def create_provider(provider_type: str) -> Optional[StockDataProvider]:
        """创建股票数据提供者实例
        
        Args:
            provider_type: 提供者类型，支持 'eastmoney' 或 'akshare'
            
        Returns:
            股票数据提供者实例
        """
        if provider_type == 'eastmoney':
            return EastmoneyAPI()
        elif provider_type == 'akshare':
            return AkshareAPI()
        else:
            print(f"不支持的提供者类型: {provider_type}")
            return None