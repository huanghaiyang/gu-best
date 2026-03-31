from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class StockDataProvider(ABC):
    """股票数据提供者抽象接口"""
    
    @abstractmethod
    async def get_stock_quote(self, code: str) -> Optional[Dict]:
        """获取股票实时行情"""
        pass
    
    @abstractmethod
    async def get_stock_detail(self, code: str) -> Optional[Dict]:
        """获取股票详细信息"""
        pass
    
    @abstractmethod
    async def get_sector_stocks(self, sector_code: str, page_size: int = 100) -> Optional[List]:
        """获取板块成分股"""
        pass
    
    @abstractmethod
    async def get_all_stocks(self, fs: str, page_size: int = 500) -> Optional[List]:
        """获取所有股票"""
        pass
    
    @abstractmethod
    async def get_sectors(self, page_size: int = 100, sector_type: str = 'concept') -> Optional[List]:
        """获取板块数据"""
        pass
    
    @abstractmethod
    async def search_stocks(self, name: str) -> List[Dict]:
        """搜索股票"""
        pass
    
    @abstractmethod
    async def get_stock_history(self, code: str, start_date: str, end_date: str) -> Optional[List]:
        """获取股票历史数据"""
        pass
    
    @abstractmethod
    async def get_index_data(self, secid: str) -> Optional[Dict]:
        """获取指数数据"""
        pass