import time
import asyncio
from typing import Dict, List, Optional
from services.stock_data_provider import StockDataProvider

# 尝试导入akshare
try:
    import akshare as ak
    import pandas as pd
    AKSHARE_AVAILABLE = True
except ImportError:
    print("警告: akshare模块未安装，akshare数据源将不可用")
    AKSHARE_AVAILABLE = False


class AkshareAPI(StockDataProvider):
    """Akshare API封装"""
    
    async def get_stock_quote(self, code: str) -> Optional[Dict]:
        """获取股票实时行情"""
        if not AKSHARE_AVAILABLE:
            print("akshare未安装，无法获取股票实时行情")
            return None
            
        try:
            # 转换为akshare格式的代码
            ak_code = self._convert_code(code)
            if not ak_code:
                return None
            
            # 使用akshare获取实时行情
            df = await asyncio.to_thread(ak.stock_zh_a_spot_em)
            stock_data = df[df['代码'] == ak_code]
            
            if stock_data.empty:
                return None
            
            data = stock_data.iloc[0].to_dict()
            return {
                'code': data['代码'],
                'name': data['名称'],
                'price': data['最新价'],
                'change': data['涨跌额'],
                'change_pct': data['涨跌幅'],  # 转换为百分比
                'volume': data['成交量'],
                'amount': data['成交额'],
                'open': data['开盘价'],
                'high': data['最高价'],
                'low': data['最低价'],
                'prev_close': data['昨收价']
            }
        except Exception as e:
            print(f"获取股票实时行情失败: {e}")
            return None
    
    async def get_stock_detail(self, code: str) -> Optional[Dict]:
        """获取股票详细信息"""
        if not AKSHARE_AVAILABLE:
            print("akshare未安装，无法获取股票详细信息")
            return None
            
        try:
            # 转换为akshare格式的代码
            ak_code = self._convert_code(code)
            if not ak_code:
                return None
            
            # 使用akshare获取股票基本信息
            df = await asyncio.to_thread(ak.stock_zh_a_basic)
            stock_data = df[df['代码'] == ak_code]
            
            if stock_data.empty:
                return None
            
            data = stock_data.iloc[0].to_dict()
            return {
                'code': data['代码'],
                'name': data['名称'],
                'industry': data.get('所属行业', ''),
                'total_share': data.get('总股本', 0),
                'float_share': data.get('流通股本', 0)
            }
        except Exception as e:
            print(f"获取股票详细信息失败: {e}")
            return None
    
    async def get_sector_stocks(self, sector_code: str, page_size: int = 100) -> Optional[List]:
        """获取板块成分股"""
        if not AKSHARE_AVAILABLE:
            print("akshare未安装，无法获取板块成分股")
            return None
            
        try:
            # 使用akshare获取概念板块成分股
            df = await asyncio.to_thread(ak.stock_board_concept_name_ths)
            sector_data = df[df['代码'] == sector_code]
            
            if sector_data.empty:
                return None
            
            sector_name = sector_data.iloc[0]['名称']
            stocks_df = await asyncio.to_thread(ak.stock_board_concept_cons_ths, sector_name=sector_name)
            
            result = []
            for _, row in stocks_df.head(page_size).iterrows():
                result.append({
                    'code': row['代码'],
                    'name': row['名称'],
                    'price': 0,  # 需要额外获取
                    'change_pct': 0  # 需要额外获取
                })
            
            return result
        except Exception as e:
            print(f"获取板块成分股失败: {e}")
            return None
    
    async def get_all_stocks(self, fs: str, page_size: int = 500) -> Optional[List]:
        """获取所有股票"""
        if not AKSHARE_AVAILABLE:
            print("akshare未安装，无法获取所有股票")
            return None
            
        try:
            # 使用akshare获取A股列表
            df = await asyncio.to_thread(ak.stock_zh_a_spot_em)
            
            # 根据fs参数过滤
            if 'm:0+t:6' in fs:  # 深主板
                df = df[df['代码'].str.startswith('00')]
            elif 'm:0+t:80' in fs:  # 创业板
                df = df[df['代码'].str.startswith('30')]
            elif 'm:1+t:2' in fs:  # 沪主板
                df = df[df['代码'].str.startswith('6') & ~df['代码'].str.startswith('688')]
            elif 'm:1+t:23' in fs:  # 科创板
                df = df[df['代码'].str.startswith('688')]
            
            result = []
            for _, row in df.head(page_size).iterrows():
                result.append({
                    'code': row['代码'],
                    'name': row['名称'],
                    'price': row['最新价'],
                    'change_pct': row['涨跌幅'],
                    'change': row['涨跌额'],
                    'volume': row['成交量'],
                    'amount': row['成交额'],
                    'turnover_rate': 0,  # 换手率
                    'volume_ratio': 0,  # 量比
                    'market_cap': 0  # 市值
                })
            
            return result
        except Exception as e:
            print(f"获取所有股票失败: {e}")
            return None
    
    async def get_sectors(self, page_size: int = 100, sector_type: str = 'concept') -> Optional[List]:
        """获取板块数据"""
        if not AKSHARE_AVAILABLE:
            print("akshare未安装，无法获取板块数据")
            return None

        try:
            print(f"尝试获取{sector_type}类型板块数据...")

            if sector_type == 'concept':
                # 概念板块 - 使用摘要接口获取涨跌幅等实时数据
                try:
                    df = await asyncio.to_thread(ak.stock_board_concept_summary_ths)
                    print(f"使用stock_board_concept_summary_ths成功获取概念板块数据，共{len(df)}条")
                    print(f"数据列: {list(df.columns)}")

                    # 检查是否有涨跌幅字段
                    if '涨跌幅' in df.columns:
                        change_pct_col = '涨跌幅'
                    else:
                        change_pct_col = None
                        print("警告: 概念板块数据缺少涨跌幅字段")

                    result = []
                    for _, row in df.head(page_size).iterrows():
                        result.append({
                            'code': row.get('概念名称', ''),
                            'name': row.get('概念名称', ''),
                            'change_pct': float(row[change_pct_col]) if change_pct_col and pd.notna(row.get(change_pct_col)) else 0,
                            'price': 0,
                            'change': 0,
                            'volume': 0,
                            'amount': 0,
                            'turnover_rate': 0,
                            'volume_ratio': 0
                        })
                    return result

                except Exception as e:
                    print(f"获取概念板块数据失败: {e}")
                    return None

            elif sector_type == 'industry':
                # 行业板块 - 使用摘要接口获取涨跌幅等实时数据
                try:
                    df = await asyncio.to_thread(ak.stock_board_industry_summary_ths)
                    print(f"使用stock_board_industry_summary_ths成功获取行业板块数据，共{len(df)}条")
                    print(f"数据列: {list(df.columns)}")

                    result = []
                    for _, row in df.head(page_size).iterrows():
                        result.append({
                            'code': row.get('板块', ''),
                            'name': row.get('板块', ''),
                            'change_pct': float(row['涨跌幅']) if '涨跌幅' in df.columns and pd.notna(row.get('涨跌幅')) else 0,
                            'price': 0,
                            'change': 0,
                            'volume': float(row['总成交量']) if '总成交量' in df.columns and pd.notna(row.get('总成交量')) else 0,
                            'amount': float(row['总成交额']) if '总成交额' in df.columns and pd.notna(row.get('总成交额')) else 0,
                            'turnover_rate': 0,
                            'volume_ratio': 0
                        })
                    return result

                except Exception as e:
                    print(f"获取行业板块数据失败: {e}")
                    return None

            else:
                # 地域板块
                try:
                    df = await asyncio.to_thread(ak.stock_board_area_name_ths)
                    print(f"使用stock_board_area_name_ths成功获取地域板块数据，共{len(df)}条")

                    result = []
                    for _, row in df.head(page_size).iterrows():
                        result.append({
                            'code': row.get('code', ''),
                            'name': row.get('name', ''),
                            'change_pct': 0,
                            'price': 0,
                            'change': 0,
                            'volume': 0,
                            'amount': 0,
                            'turnover_rate': 0,
                            'volume_ratio': 0
                        })
                    return result

                except Exception as e:
                    print(f"获取地域板块数据失败: {e}")
                    return None

        except Exception as e:
            print(f"获取板块数据失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def search_stocks(self, name: str) -> List[Dict]:
        """搜索股票"""
        if not AKSHARE_AVAILABLE:
            print("akshare未安装，无法搜索股票")
            return []
            
        try:
            # 使用akshare获取股票列表
            df = await asyncio.to_thread(ak.stock_zh_a_spot_em)
            # 搜索代码或名称包含关键字的股票
            result_df = df[df['代码'].str.contains(name) | df['名称'].str.contains(name)]
            
            result = []
            for _, row in result_df.iterrows():
                result.append({
                    'code': row['代码'],
                    'name': row['名称']
                })
            
            return result
        except Exception as e:
            print(f"搜索股票失败: {e}")
            return []
    
    async def get_stock_history(self, code: str, start_date: str, end_date: str) -> Optional[List]:
        """获取股票历史数据"""
        if not AKSHARE_AVAILABLE:
            print("akshare未安装，无法获取股票历史数据")
            return None
            
        try:
            # 转换为akshare格式的代码
            ak_code = self._convert_code(code)
            if not ak_code:
                return None
            
            # 使用akshare获取历史数据
            df = await asyncio.to_thread(
                ak.stock_zh_a_hist,
                symbol=ak_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            
            result = []
            for _, row in df.iterrows():
                result.append({
                    'date': row['日期'],
                    'open': row['开盘'],
                    'high': row['最高'],
                    'low': row['最低'],
                    'close': row['收盘'],
                    'volume': row['成交量'],
                    'amount': row['成交额']
                })
            
            return result
        except Exception as e:
            print(f"获取股票历史数据失败: {e}")
            return None
    
    async def get_index_data(self, secid: str) -> Optional[Dict]:
        """获取指数数据"""
        if not AKSHARE_AVAILABLE:
            print("akshare未安装，无法获取指数数据")
            return None
            
        try:
            # 转换为akshare格式的代码
            if secid in ['0.000001', '1.000001']:  # 上证指数
                ak_code = 'sh000001'
            elif secid == '0.399001':  # 深证成指
                ak_code = 'sz399001'
            elif secid == '0.399006':  # 创业板指
                ak_code = 'sz399006'
            elif secid == '1.000688':  # 科创50
                ak_code = 'sh000688'
            else:
                return None
            
            # 使用akshare获取指数数据，使用sina接口
            df = await asyncio.to_thread(ak.stock_zh_index_spot_sina)
            
            index_data = df[df['代码'] == ak_code]
            
            if index_data.empty:
                return None
            
            data = index_data.iloc[0].to_dict()
            return {
                'code': data['代码'],
                'name': data['名称'],
                'price': data['最新价'],
                'change': data['涨跌额'],
                'change_pct': data['涨跌幅']
            }
        except Exception as e:
            print(f"获取指数数据失败: {e}")
            return None
    
    def _convert_code(self, code: str) -> str:
        """转换股票代码为akshare格式"""
        if code.startswith('6'):
            return f'sh{code}'
        elif code.startswith('00') or code.startswith('30'):
            return f'sz{code}'
        elif code.startswith('8') or code.startswith('4'):
            return f'bj{code}'
        return code