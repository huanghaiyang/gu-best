from typing import Optional
from services.stock_data_provider import StockDataProvider
from services.eastmoney_api import EastmoneyAPI


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
            # 延迟导入akshare，避免在不需要时初始化mini_racer
            try:
                from services.akshare_api import AkshareAPI, AKSHARE_AVAILABLE
                if AKSHARE_AVAILABLE:
                    return AkshareAPI()
                else:
                    print("akshare未安装，无法创建akshare提供者")
                    return None
            except Exception as e:
                print(f"创建akshare提供者失败: {e}")
                return None
        else:
            print(f"不支持的提供者类型: {provider_type}")
            return None