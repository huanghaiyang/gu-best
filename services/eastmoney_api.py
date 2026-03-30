import requests
from typing import Dict, List, Optional
from services.eastmoney_fields import (
    QUOTE_FIELDS_FULL,
    LIST_FIELDS_FULL,
    DETAIL_FIELDS_FULL,
    STOCK_QUOTE_FIELDS,
    STOCK_LIST_FIELDS,
    STOCK_DETAIL_FIELDS,
    SECTOR_FIELDS,
    parse_eastmoney_data
)


class EastmoneyAPI:
    """东方财富API封装"""

    BASE_URL = 'http://push2.eastmoney.com/api'
    HISTORY_URL = 'http://push2his.eastmoney.com/api'

    UT_TOKEN_STOCK = 'fa5fd1943c7b386f172d6893dbfba10b'
    UT_TOKEN_LIST = 'bd1d9ddb04089700cf9c27f6f7426281'
    SEARCH_TOKEN = 'd41d8cd98f00b204e9800998ecf8427e'

    DEFAULT_TIMEOUT = 10
    SHORT_TIMEOUT = 5
    LONG_TIMEOUT = 15

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://quote.eastmoney.com/'
        })

    def _get_secid(self, code: str) -> str:
        """根据股票代码生成secid"""
        market = '1' if code.startswith('6') else '0'
        return f"{market}.{code}"

    def _make_request(self, url: str, params: Dict, timeout: int = None) -> Optional[Dict]:
        """发送HTTP请求并返回JSON数据"""
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT

        try:
            response = self.session.get(url, params=params, timeout=timeout)
            data = response.json()

            if data and 'data' in data:
                return data['data']

            return None
        except Exception as e:
            print(f"请求失败: {e}")
            return None

    def _get_list_params(self, fs: str, page_size: int = 100, fields: str = None) -> Dict:
        """生成列表查询的通用参数"""
        params = {
            'pn': 1,
            'pz': page_size,
            'po': 1,
            'np': 1,
            'ut': self.UT_TOKEN_LIST,
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': fs
        }

        if fields:
            params['fields'] = fields

        return params

    def get_stock_info(self, code: str, fields: str = 'f57,f58') -> Optional[Dict]:
        """获取股票基本信息"""
        try:
            url = f'{self.BASE_URL}/qt/stock/get'
            params = {
                'secid': self._get_secid(code),
                'ut': self.UT_TOKEN_STOCK,
                'fields': fields
            }

            return self._make_request(url, params)
        except Exception as e:
            print(f"获取股票基本信息失败: {e}")
            return None

    def get_stock_quote(self, code: str) -> Optional[Dict]:
        """获取股票实时行情"""
        try:
            url = f'{self.BASE_URL}/qt/stock/get'
            params = {
                'secid': self._get_secid(code),
                'ut': self.UT_TOKEN_STOCK,
                'fields': QUOTE_FIELDS_FULL
            }

            data = self._make_request(url, params)
            if data:
                return parse_eastmoney_data(data, STOCK_QUOTE_FIELDS)
            return None
        except Exception as e:
            print(f"获取股票实时行情失败: {e}")
            return None

    def get_stock_detail(self, code: str) -> Optional[Dict]:
        """获取股票详细信息"""
        try:
            url = f'{self.BASE_URL}/qt/stock/get'
            params = {
                'secid': self._get_secid(code),
                'ut': self.UT_TOKEN_STOCK,
                'fields': DETAIL_FIELDS_FULL
            }

            data = self._make_request(url, params)
            if data:
                return parse_eastmoney_data(data, STOCK_DETAIL_FIELDS)
            return None
        except Exception as e:
            print(f"获取股票详细信息失败: {e}")
            return None

    def search_stocks(self, name: str) -> List[Dict]:
        """搜索股票"""
        try:
            url = f'{self.BASE_URL}/qt/suggest/get'
            params = {
                'input': name,
                'type': '14',
                'token': self.SEARCH_TOKEN,
                'ut': self.UT_TOKEN_LIST,
                'rtntype': '6'
            }

            response = self.session.get(url, params=params, timeout=self.DEFAULT_TIMEOUT)
            data = response.json()

            if data and 'data' in data:
                return data['data']

            return []
        except Exception as e:
            print(f"搜索股票失败: {e}")
            return []

    def get_stock_history(self, code: str, start_date: str, end_date: str) -> Optional[List]:
        """获取股票历史数据"""
        try:
            url = f'{self.HISTORY_URL}/qt/stock/kline/get'
            params = {
                'secid': self._get_secid(code),
                'ut': self.UT_TOKEN_STOCK,
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': 101,
                'fqt': 1,
                'beg': start_date,
                'end': end_date
            }

            response = self.session.get(url, params=params, timeout=self.DEFAULT_TIMEOUT)
            data = response.json()

            if data and 'data' in data and 'klines' in data['data']:
                return data['data']['klines']

            return None
        except Exception as e:
            print(f"获取股票历史数据失败: {e}")
            return None

    def get_sector_stocks(self, sector_code: str, page_size: int = 100) -> Optional[List]:
        """获取板块成分股"""
        try:
            url = f'{self.BASE_URL}/qt/clist/get'
            params = self._get_list_params(
                fs=f'b:{sector_code}+f:!50',
                page_size=page_size,
                fields=LIST_FIELDS_FULL
            )

            response = self.session.get(url, params=params, timeout=self.DEFAULT_TIMEOUT)
            data = response.json()

            if data and 'data' in data and 'diff' in data['data']:
                items = data['data']['diff']
                # 解析每个股票的字段
                result = []
                for item in items:
                    parsed = parse_eastmoney_data(item, STOCK_LIST_FIELDS)
                    result.append(parsed)
                return result

            return None
        except Exception as e:
            print(f"获取板块成分股失败: {e}")
            return None

    def get_all_stocks(self, fs: str, page_size: int = 500) -> Optional[List]:
        """获取所有股票"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                url = f'{self.BASE_URL}/qt/clist/get'
                params = self._get_list_params(
                    fs=fs,
                    page_size=page_size,
                    fields=LIST_FIELDS_FULL
                )

                response = self.session.get(url, params=params, timeout=self.LONG_TIMEOUT)
                
                # 检查响应状态码
                if response.status_code != 200:
                    print(f"获取所有股票失败: 状态码 {response.status_code}")
                    retry_count += 1
                    continue
                
                data = response.json()
                
                # 检查API返回的错误码
                if data.get('rc') != 0:
                    print(f"获取所有股票失败: API错误码 {data.get('rc')}")
                    retry_count += 1
                    continue

                if data and 'data' in data and 'diff' in data['data']:
                    items = data['data']['diff']
                    # 解析每个股票的字段
                    result = []
                    for item in items:
                        parsed = parse_eastmoney_data(item, STOCK_LIST_FIELDS)
                        result.append(parsed)
                    return result

                return None
            except Exception as e:
                print(f"获取所有股票失败: {e}")
                retry_count += 1
                continue
        
        return None

    def get_index_data(self, secid: str) -> Optional[Dict]:
        """获取指数数据"""
        try:
            url = f'{self.BASE_URL}/qt/stock/get'
            params = {
                'secid': secid,
                'ut': self.UT_TOKEN_STOCK,
                'fields': QUOTE_FIELDS_FULL
            }

            data = self._make_request(url, params)
            if data:
                return parse_eastmoney_data(data, STOCK_QUOTE_FIELDS)
            return None
        except Exception as e:
            print(f"获取指数数据失败: {e}")
            return None

    def get_sectors(self, page_size: int = 100, sector_type: str = 'concept') -> Optional[List]:
        """获取板块数据
        
        Args:
            page_size: 每页数量
            sector_type: 板块类型: 'industry' (行业), 'concept' (概念), 'region' (地域)
            
        Returns:
            板块数据列表
        """
        try:
            url = f'{self.BASE_URL}/qt/clist/get'
            
            # 根据板块类型选择参数
            sector_map = {
                'industry': 'm:90+t:1',  # 行业板块
                'concept': 'm:90+t:2',    # 概念板块
                'region': 'm:90+t:3'      # 地域板块
            }
            
            fs_param = sector_map.get(sector_type, 'm:90+t:2')  # 默认概念板块
            
            params = {
                'pn': 1,
                'pz': page_size,
                'po': 1,
                'np': 1,
                'ut': self.UT_TOKEN_LIST,
                'fltt': 2,
                'invt': 2,
                'fid': 'f3',
                'fs': fs_param,
                'fields': 'f12,f14,f3,f2,f4,f5,f6,f8,f10,f15,f16,f17,f18'
            }

            response = self.session.get(url, params=params, timeout=self.DEFAULT_TIMEOUT)
            data = response.json()
            
            if data and 'data' in data and 'diff' in data['data']:
                items = data['data']['diff']
                # 解析板块数据
                result = []
                for item in items:
                    parsed = parse_eastmoney_data(item, SECTOR_FIELDS)
                    result.append(parsed)
                return result

            return None
        except Exception as e:
            print(f"获取板块数据失败: {e}")
            return None
