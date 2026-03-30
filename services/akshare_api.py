from typing import Dict, List, Optional
from services.stock_data_provider import StockDataProvider

# 尝试导入akshare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    print("警告: akshare模块未安装，akshare数据源将不可用")
    AKSHARE_AVAILABLE = False


class AkshareAPI(StockDataProvider):
    """Akshare API封装"""
    
    def get_stock_quote(self, code: str) -> Optional[Dict]:
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
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == ak_code]
            
            if stock_data.empty:
                return None
            
            data = stock_data.iloc[0].to_dict()
            return {
                'code': data['代码'],
                'name': data['名称'],
                'price': data['最新价'],
                'change': data['涨跌额'],
                'change_pct': data['涨跌幅'] * 100,  # 转换为百分比
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
    
    def get_stock_detail(self, code: str) -> Optional[Dict]:
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
            df = ak.stock_zh_a_basic()
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
    
    def get_sector_stocks(self, sector_code: str, page_size: int = 100) -> Optional[List]:
        """获取板块成分股"""
        if not AKSHARE_AVAILABLE:
            print("akshare未安装，无法获取板块成分股")
            return None
            
        try:
            # 使用akshare获取概念板块成分股
            df = ak.stock_board_concept_name_ths()
            sector_data = df[df['代码'] == sector_code]
            
            if sector_data.empty:
                return None
            
            sector_name = sector_data.iloc[0]['名称']
            stocks_df = ak.stock_board_concept_cons_ths(sector_name=sector_name)
            
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
    
    def get_all_stocks(self, fs: str, page_size: int = 500) -> Optional[List]:
        """获取所有股票"""
        if not AKSHARE_AVAILABLE:
            print("akshare未安装，无法获取所有股票")
            return None
            
        try:
            # 使用akshare获取A股列表
            df = ak.stock_zh_a_spot_em()
            
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
                    'change_pct': row['涨跌幅'] * 100,
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
    
    def get_sectors(self, page_size: int = 100, sector_type: str = 'concept') -> Optional[List]:
        """获取板块数据"""
        if not AKSHARE_AVAILABLE:
            print("akshare未安装，无法获取板块数据")
            return None
            
        try:
            print(f"尝试获取{sector_type}类型板块数据...")
            
            # 尝试使用不同的函数名获取板块数据
            if sector_type == 'concept':
                # 概念板块
                try:
                    df = ak.stock_board_concept_name_ths()
                    print(f"使用stock_board_concept_name_ths成功获取概念板块数据，共{len(df)}条")
                except AttributeError:
                    try:
                        df = ak.stock_board_concept_index_ths()
                        print(f"使用stock_board_concept_index_ths成功获取概念板块数据，共{len(df)}条")
                    except Exception as e:
                        print(f"获取概念板块数据失败: {e}")
                        return None
            elif sector_type == 'industry':
                # 行业板块
                try:
                    df = ak.stock_board_industry_name_ths()
                    print(f"使用stock_board_industry_name_ths成功获取行业板块数据，共{len(df)}条")
                except AttributeError:
                    try:
                        df = ak.stock_board_industry_index_ths()
                        print(f"使用stock_board_industry_index_ths成功获取行业板块数据，共{len(df)}条")
                    except Exception as e:
                        print(f"获取行业板块数据失败: {e}")
                        return None
            else:
                # 地域板块
                try:
                    df = ak.stock_board_area_name_ths()
                    print(f"使用stock_board_area_name_ths成功获取地域板块数据，共{len(df)}条")
                except Exception as e:
                    print(f"获取地域板块数据失败: {e}")
                    return None
            
            # 检查数据是否为空
            if df.empty:
                print(f"获取{sector_type}类型板块数据为空")
                return None
            
            # 检查数据列是否存在
            if '代码' not in df.columns or '名称' not in df.columns:
                print(f"数据列不完整，缺少必要字段")
                print(f"实际列: {list(df.columns)}")
                return None
            
            result = []
            for _, row in df.head(page_size).iterrows():
                result.append({
                    'code': row['代码'],
                    'name': row['名称'],
                    'change_pct': 0,  # 需要额外获取
                    'price': 0,  # 板块指数
                    'change': 0,  # 涨跌额
                    'volume': 0,  # 成交量
                    'amount': 0,  # 成交额
                    'turnover_rate': 0,  # 换手率
                    'volume_ratio': 0  # 量比
                })
            
            print(f"成功处理{len(result)}个板块数据")
            return result
        except Exception as e:
            print(f"获取板块数据失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def search_stocks(self, name: str) -> List[Dict]:
        """搜索股票"""
        if not AKSHARE_AVAILABLE:
            print("akshare未安装，无法搜索股票")
            return []
            
        try:
            # 使用akshare获取股票列表
            df = ak.stock_zh_a_spot_em()
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
    
    def get_stock_history(self, code: str, start_date: str, end_date: str) -> Optional[List]:
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
            df = ak.stock_zh_a_hist(
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
    
    def get_index_data(self, secid: str) -> Optional[Dict]:
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
            
            # 使用akshare获取指数数据
            df = ak.stock_zh_index_spot_em()
            index_data = df[df['代码'] == ak_code]
            
            if index_data.empty:
                return None
            
            data = index_data.iloc[0].to_dict()
            return {
                'code': data['代码'],
                'name': data['名称'],
                'price': data['最新价'],
                'change': data['涨跌额'],
                'change_pct': data['涨跌幅'] * 100
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