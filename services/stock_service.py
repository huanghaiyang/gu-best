import math
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from config import stock_filter_config
from services.stock_data_factory import StockDataFactory
from services.stock_data_provider import StockDataProvider

MARKET_NAMES = {
    'sh': '沪',
    'sz': '深',
    'bj': '京',
}

SECTOR_CATEGORIES = {
    '科技': ['人工智能', '半导体', '芯片', '算力', '机器人', '通信', '电子', '软件', '云计算', '物联网', '元宇宙', '数字经济', '5G', '区块链', '量子', '车联网', '互联网', '计算机', '大数据', '网络安全', '操作系统', '数据库', '服务器', '存储', '光模块', 'CPO', '液冷', '边缘计算', '数字孪生', '虚拟现实', '增强现实', '脑机接口'],
    '新能源': ['新能源', '光伏', '锂电池', '储能', '风电', '氢能', '充电桩', '电动车', '智能汽车', '新能源车', '动力电池', '正极材料', '负极材料', '电解液', '隔膜', '铜箔', '铝箔', '锂矿', '钴', '镍', '稀土', '硅料', '硅片', '电池片', '组件', '逆变器', '风电叶片', '风电塔筒', '风电轴承'],
    '医药': ['医药', '创新药', '医疗', '生物', '疫苗', '医疗器械', 'CXO', '中医药', '化学制药', '生物制药', '医疗服务', '医美', '眼科', '口腔', '血液制品', '疫苗', '诊断试剂', '基因检测', '细胞治疗', '免疫治疗', '靶向药', '仿制药', '原料药', '中药饮片', '中成药'],
    '消费': ['消费', '食品', '饮料', '白酒', '家电', '零售', '旅游', '餐饮', '电商', '体育', '服装', '美妆', '珠宝', '奢侈品', '免税', '酒店', '景区', '影视', '游戏', '出版', '教育', '体育用品', '户外用品', '宠物', '母婴', '个护', '家居', '家具', '建材', '装修'],
    '金融': ['金融', '银行', '保险', '券商', '基金', '证券', '信托', '期货', '租赁', '小贷', '担保', '典当', '拍卖', '交易所', '金融科技', '支付', '征信', '评级', '资管', '信托', '期货', '期权', '外汇'],
    '周期': ['化工', '有色', '钢铁', '煤炭', '建材', '地产', '建筑', '机械', '电力', '石油', '天然气', '水泥', '玻璃', '造纸', '包装', '印刷', '化肥', '农药', '钛白粉', '纯碱', 'PVC', 'MDI', 'TDI', '聚丙烯', '聚乙烯', 'PTA', '乙二醇', '甲醇', '沥青', '橡胶', '塑料', '纤维'],
    '汽车': ['汽车', '零部件', '整车', '智能驾驶', '燃料电池', '汽车电子', '汽车服务', '汽车拆解', '汽车回收', '汽车金融', '汽车租赁', '汽车后市场', '发动机', '变速箱', '底盘', '车身', '内饰', '轮胎', '轮毂', '玻璃', '车灯', '音响'],
    '军工': ['军工', '国防', '航天', '航空', '船舶', '兵器', '雷达', '导弹', '卫星', '无人机', '军工电子', '军工材料', '军工装备', '军工信息化', '军工通信', '军工导航', '军工雷达', '军工导弹', '军工飞机', '军工直升机', '军工坦克', '军工舰船'],
    '农业': ['农业', '养殖', '种植', '种业', '农产品', '化肥', '农药', '农机', '饲料', '兽药', '水产', '林业', '牧业', '渔业', '农产品加工', '食品加工', '食品制造', '饮料制造', '酒类', '烟草', '纺织', '服装', '皮革', '造纸', '木材'],
    '传媒': ['传媒', '影视', '游戏', '出版', '广告', '营销', '体育', '电竞', '直播', '短视频', '社交', '视频', '音乐', '动漫', '文学', '新闻', '出版', '印刷', '发行', '院线', '影院', '演艺', '经纪'],
    '环保': ['环保', '水务', '固废', '大气', '土壤', '噪声', '监测', '治理', '修复', '节能', '减排', '循环经济', '清洁能源', '再生资源', '环保设备', '环保工程', '环保服务', '环保咨询', '环保检测'],
    '交运': ['交运', '铁路', '公路', '水路', '航空', '机场', '港口', '物流', '快递', '仓储', '供应链', '冷链', '货运', '客运', '出租车', '网约车', '地铁', '轻轨', '公交', '高速', '桥梁', '隧道'],
    '公用': ['公用', '电力', '燃气', '供热', '供水', '污水处理', '垃圾处理', '市政', '园林', '环卫', '照明', '公交', '地铁', '轻轨', '高速', '港口', '机场'],
    '其他': []
}


def get_market_type(code: str) -> str:
    if code.startswith('6'):
        return 'sh'
    elif code.startswith('00'):
        return 'sz'
    elif code.startswith('30'):
        return 'sz'
    elif code.startswith('68'):
        return 'sh'
    elif code.startswith('8') or code.startswith('4'):
        return 'bj'
    return 'sz'


def get_market_label(code: str) -> str:
    market = get_market_type(code)
    if code.startswith('688'):
        return '科创'
    elif code.startswith('30'):
        return '创业'
    elif code.startswith('8') or code.startswith('4'):
        return '北交'
    return MARKET_NAMES.get(market, '')


def get_sector_category(sector_name: str) -> str:
    sector_name = sector_name.replace('(行业)', '').strip()
    for category, keywords in SECTOR_CATEGORIES.items():
        for keyword in keywords:
            if keyword in sector_name:
                return category
    return '其他'


class StockService:
    def __init__(self, provider_type: str = 'akshare'):
        self.config = stock_filter_config
        self.provider_type = provider_type
        self.provider = StockDataFactory.create_provider(provider_type)
        if not self.provider:
            raise Exception(f"无法创建股票数据提供者: {provider_type}")
    
    async def set_provider(self, provider_type: str):
        """设置数据源提供者
        
        Args:
            provider_type: 提供者类型，支持 'eastmoney' 或 'akshare'
        """
        new_provider = StockDataFactory.create_provider(provider_type)
        if new_provider:
            self.provider_type = provider_type
            self.provider = new_provider
            return True
        return False

    async def search_stocks(self, query: str) -> List[Dict]:
        if not query or len(query.strip()) < 2:
            return []

        query = query.strip()

        try:
            if query.isdigit() and len(query) == 6:
                stocks = await self._search_by_code(query)
            else:
                stocks = await self._search_by_name(query)
            return stocks
        except Exception as e:
            print(f"搜索股票失败: {e}")
            return []

    async def _search_by_code(self, code: str) -> List[Dict]:
        """通过股票代码搜索"""
        try:
            # 直接调用 get_stock_quote 获取股票信息
            quote = await self.provider.get_stock_quote(code)
            if quote:
                return [quote]
            else:
                return []
        except Exception as e:
            print(f"通过代码搜索股票失败: {e}")
            return []

    async def _search_by_name(self, name: str) -> List[Dict]:
        """通过股票名称搜索"""
        try:
            # 使用抽象接口搜索股票
            results = await self.provider.search_stocks(name)
            return results
        except Exception as e:
            print(f"通过名称搜索股票失败: {e}")
            return []

    async def get_sectors(self) -> List[Dict]:
        try:
            return await self._get_real_sectors()
        except Exception as e:
            print(f"获取板块数据失败: {e}")
            return []

    async def _get_real_sectors(self) -> List[Dict]:
        # 调用抽象接口获取板块数据
        # 同时获取行业板块和概念板块
        # 使用 asyncio.gather 并行获取
        industry_sectors, concept_sectors = await asyncio.gather(
            self.provider.get_sectors(sector_type='industry'),
            self.provider.get_sectors(sector_type='concept')
        )
        
        sectors = []
        
        # 处理行业板块
        if industry_sectors:
            for item in industry_sectors:
                sector_code = item.get('code', '')
                sector_name = item.get('name', '')

                sectors.append({
                    'code': sector_code,
                    'name': sector_name + '(行业)',
                    'change_pct': float(item.get('change_pct', 0) or 0),
                    'leading_stock': '',
                    'leading_stock_code': '',
                    'type': 'industry',
                    'category': get_sector_category(sector_name)
                })
        
        # 处理概念板块
        if concept_sectors:
            for item in concept_sectors:
                sector_code = item.get('code', '')
                sector_name = item.get('name', '')

                sectors.append({
                    'code': sector_code,
                    'name': sector_name + '(概念)',
                    'change_pct': float(item.get('change_pct', 0) or 0),
                    'leading_stock': '',
                    'leading_stock_code': '',
                    'type': 'concept',
                    'category': get_sector_category(sector_name)
                })

        sectors.sort(key=lambda x: x['change_pct'], reverse=True)

        return sectors

    async def get_sector_stocks(self, sector_code: str) -> List[Dict]:
        try:
            return await self._get_real_sector_stocks(sector_code)
        except Exception as e:
            print(f"获取板块成分股失败: {e}")
            return []

    async def _get_real_sector_stocks(self, sector_code: str) -> List[Dict]:
        items = await self.provider.get_sector_stocks(sector_code, 100)

        stocks = []
        if items:
            for item in items:
                code = str(item.get('code', ''))
                # 列表接口返回的数据已经通过 parse_eastmoney_data 解析
                # 但单位需要进一步转换
                stocks.append({
                    'code': code,
                    'name': item.get('name', ''),
                    'price': item.get('price', 0),
                    'change_pct': item.get('change_pct', 0),
                    'change': item.get('change', 0),
                    'volume': item.get('volume', 0),  # 转换为万手
                    'amount': item.get('amount', 0),  # 转换为亿
                    'volume_ratio': item.get('volume_ratio', 0),
                    'turnover_rate': item.get('turnover_rate', 0),
                    'market_cap': item.get('market_cap', 0),
                    'market': get_market_label(code)
                })

        return stocks

    async def get_all_a_stocks(self) -> List[Dict]:
        try:
            return await self._get_real_all_stocks()
        except Exception as e:
            print(f"获取A股数据失败: {e}")
            return []

    async def _get_real_all_stocks(self) -> List[Dict]:
        stocks = []

        market_configs = [
            ('m:0+t:6,m:0+t:80', '深主板'),
            ('m:0+t:13', '创业板'),
            ('m:1+t:2', '沪主板'),
            ('m:1+t:23', '科创板'),
        ]

        # 并行获取所有市场数据
        async def get_market_data(fs, market_name):
            try:
                items = await self.provider.get_all_stocks(fs, 500)
                market_stocks = []
                if items:
                    for item in items:
                        change_pct = item.get('change_pct', 0)
                        price = item.get('price', 0)
                        code = str(item.get('code', ''))

                        if price > 0:
                            market_stocks.append({
                                'code': code,
                                'name': item.get('name', ''),
                                'price': price,
                                'change_pct': change_pct,
                                'change': item.get('change', 0),
                                'volume': item.get('volume', 0),  # 转换为万手
                                'amount': item.get('amount', 0),  # 转换为亿
                                'volume_ratio': item.get('volume_ratio', 0),
                                'turnover_rate': item.get('turnover_rate', 0),
                                'market_cap': item.get('market_cap', 0),
                                'market': get_market_label(code)
                            })
                return market_stocks
            except Exception as e:
                print(f"获取{market_name}数据失败: {e}")
                return []

        # 使用 asyncio.gather 并行获取
        tasks = [get_market_data(fs, market_name) for fs, market_name in market_configs]
        market_results = await asyncio.gather(*tasks)

        # 合并结果
        for market_stocks in market_results:
            stocks.extend(market_stocks)

        return stocks

    async def screen_leader_stocks(self, sector: Optional[str] = None, top_n: int = 10) -> List[Dict]:
        if sector:
            stocks = await self.get_sector_stocks(sector)
        else:
            stocks = await self.get_all_a_stocks()

        if not stocks:
            return []

        for stock in stocks:
            stock['score'] = self._calculate_single_score(stock)

        stocks.sort(key=lambda x: x.get('score', 0), reverse=True)

        return stocks[:top_n]

    def _calculate_single_score(self, stock: Dict) -> float:
        score = 0.0

        # 辅助函数：将值转换为浮点数，处理非数字值
        def to_float(value, default=0):
            if value == '-' or value is None:
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        # 转换为数值类型，避免类型错误
        change_pct = to_float(stock.get('change_pct', 0))
        score += max(-30, min(30, change_pct * 3))

        volume_ratio = to_float(stock.get('volume_ratio', 0))
        score += max(0, min(10, (volume_ratio - 1) * 2))

        turnover_rate = to_float(stock.get('turnover_rate', 0))
        if 3 < turnover_rate < 10:
            score += 5
        elif turnover_rate >= 10:
            score += 3

        market_cap = to_float(stock.get('market_cap', 0))
        if market_cap > 0:
            score += min(10, math.log10(market_cap) - 8)

        return round(score, 2)

    async def get_stock_detail(self, stock_code: str) -> Dict:
        try:
            return await self._get_real_stock_detail(stock_code)
        except Exception as e:
            print(f"获取股票详情失败: {e}")
            return {'code': stock_code, 'name': '', 'industry': '', 'market': get_market_label(stock_code)}

    async def _get_real_stock_detail(self, stock_code: str) -> Dict:
        item = await self.provider.get_stock_detail(stock_code)

        if item:
            return {
                'code': item.get('code', stock_code),
                'name': item.get('name', ''),
                'industry': item.get('industry', ''),
                'total_share': item.get('total_share', 0),
                'float_share': item.get('float_share', 0),
                'market': get_market_label(stock_code)
            }

        return {'code': stock_code, 'name': '', 'industry': '', 'market': get_market_label(stock_code)}

    async def get_stock_history(self, stock_code: str, days: int = 30) -> List[Dict]:
        try:
            return await self._get_real_stock_history(stock_code, days)
        except Exception as e:
            print(f"获取股票历史数据失败: {e}")
            return []

    async def _get_real_stock_history(self, stock_code: str, days: int = 30) -> List[Dict]:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')

        klines = await self.provider.get_stock_history(stock_code, start_date, end_date)

        history = []
        if klines:
            for kline in klines[-days:]:
                parts = kline.split(',')
                if len(parts) >= 7:
                    history.append({
                        'date': parts[0],
                        'open': float(parts[1]),
                        'close': float(parts[2]),
                        'high': float(parts[3]),
                        'low': float(parts[4]),
                        'volume': float(parts[5]),
                        'amount': float(parts[6]),
                        'change_pct': float(parts[7]) if len(parts) > 7 else 0
                    })

        return history

    async def get_index_data(self) -> Dict:
        indexes = {
            'sh': {'name': '上证指数', 'code': '000001', 'price': 0, 'change': 0, 'change_pct': 0},
            'sz': {'name': '深证成指', 'code': '399001', 'price': 0, 'change': 0, 'change_pct': 0},
            'cy': {'name': '创业板指', 'code': '399006', 'price': 0, 'change': 0, 'change_pct': 0},
            'kc': {'name': '科创50', 'code': '000688', 'price': 0, 'change': 0, 'change_pct': 0}
        }

        index_codes = [
            ('sh', '1.000001'),
            ('sz', '0.399001'),
            ('cy', '0.399006'),
            ('kc', '1.000688')
        ]

        # 并行获取指数数据
        async def get_index(key, secid):
            try:
                item = await self.provider.get_index_data(secid)
                if item:
                    return key, item
                return key, None
            except Exception as e:
                print(f"获取{indexes[key]['name']}数据失败: {e}")
                return key, None

        # 使用 asyncio.gather 并行获取
        tasks = [get_index(key, secid) for key, secid in index_codes]
        results = await asyncio.gather(*tasks)

        # 处理结果
        for key, item in results:
            if item:
                indexes[key]['price'] = item.get('price', 0)
                indexes[key]['change'] = item.get('change', 0)
                indexes[key]['change_pct'] = item.get('change_pct', 0)

        return indexes

    async def get_kline_data(self, stock_code: str, days: int = 60) -> Dict:
        history = await self._get_real_stock_history(stock_code, days)

        if not history:
            return {'kline': [], 'kdj': [], 'macd': []}

        kline = []
        for h in history:
            kline.append({
                'date': h['date'],
                'open': h['open'],
                'close': h['close'],
                'high': h['high'],
                'low': h['low'],
                'volume': h['volume']
            })

        kdj = self._calculate_kdj(history)
        macd = self._calculate_macd(history)

        return {'kline': kline, 'kdj': kdj, 'macd': macd}

    def _calculate_kdj(self, history: List[Dict], n: int = 9, m1: int = 3, m2: int = 3) -> List[Dict]:
        kdj = []
        if len(history) < n:
            return kdj

        rsv_list = []
        for i in range(len(history)):
            if i < n - 1:
                rsv_list.append(50)
            else:
                high_list = [h['high'] for h in history[i-n+1:i+1]]
                low_list = [h['low'] for h in history[i-n+1:i+1]]
                high_n = max(high_list)
                low_n = min(low_list)

                if high_n == low_n:
                    rsv = 50
                else:
                    rsv = (history[i]['close'] - low_n) / (high_n - low_n) * 100
                rsv_list.append(rsv)

        k = 50
        d = 50
        for i, rsv in enumerate(rsv_list):
            k = (m1 - 1) / m1 * k + 1 / m1 * rsv
            d = (m2 - 1) / m2 * d + 1 / m2 * k
            j = 3 * k - 2 * d
            kdj.append({'k': round(k, 2), 'd': round(d, 2), 'j': round(j, 2)})

        return kdj

    def _calculate_macd(self, history: List[Dict], short: int = 12, long: int = 26, signal: int = 9) -> List[Dict]:
        macd = []
        if len(history) < long:
            return macd

        closes = [h['close'] for h in history]

        ema_short = closes[0]
        ema_long = closes[0]

        for i, close in enumerate(closes):
            ema_short = ema_short * (short - 1) / (short + 1) + close * 2 / (short + 1)
            ema_long = ema_long * (long - 1) / (long + 1) + close * 2 / (long + 1)

            dif = ema_short - ema_long

            if i == 0:
                dea = dif
            else:
                dea = dea * (signal - 1) / (signal + 1) + dif * 2 / (signal + 1)

            macd_val = 2 * (dif - dea)

            macd.append({
                'macd': round(dif, 4),
                'signal': round(dea, 4),
                'histogram': round(macd_val, 4)
            })

        return macd

    def _get_empty_quote(self, stock_code: str) -> Dict:
        """生成空白的股价数据"""
        return {
            'code': stock_code,
            'name': '',
            'price': 0,
            'change': 0,
            'change_pct': 0,
            'volume': 0,
            'amount': 0,
            'market_cap': 0
        }

    async def get_quote(self, stock_code: str) -> Dict:
        """获取单个股票的实时行情"""
        try:
            return await self._get_real_stock_quote(stock_code)
        except Exception as e:
            print(f"获取股票实时行情失败: {e}")
            return self._get_empty_quote(stock_code)

    async def _get_real_stock_quote(self, stock_code: str) -> Dict:
        """从数据源获取实时行情"""
        item = await self.provider.get_stock_quote(stock_code)

        if item:
            # 数据已经通过解析和转换
            # 只需要进行单位转换
            return {
                'code': item.get('code', stock_code),
                'name': item.get('name', ''),
                'price': item.get('price', 0),
                'change': item.get('change', 0),
                'change_pct': item.get('change_pct', 0),
                'volume': item.get('volume', 0),
                'amount': item.get('amount', 0),
                'market_cap': item.get('market_cap', 0)
            }

        return self._get_empty_quote(stock_code)
