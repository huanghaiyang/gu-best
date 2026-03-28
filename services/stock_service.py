import math
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from config import stock_filter_config

HAS_AKSHARE = False
try:
    import akshare as ak
    import pandas as pd
    import numpy as np
    HAS_AKSHARE = True
except ImportError:
    pass

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
    def __init__(self):
        self.config = stock_filter_config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://quote.eastmoney.com/'
        })
    
    def search_stocks(self, query: str) -> List[Dict]:
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip()
        
        try:
            if query.isdigit() and len(query) == 6:
                return self._search_by_code(query)
            else:
                return self._search_by_name(query)
        except Exception as e:
            print(f"搜索股票失败: {e}")
            return []
    
    def _search_by_code(self, code: str) -> List[Dict]:
        url = 'http://push2.eastmoney.com/api/qt/stock/get'
        params = {
            'secid': f"{'1' if code.startswith('6') else '0'}.{code}",
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'fields': 'f57,f58,f107,f152,f162,f163,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200,f201,f202,f203,f204,f205,f206,f207,f208,f209,f210,f211,f212,f213,f214,f215,f216,f217,f218,f219,f220,f221,f222,f223,f224,f225,f226,f227,f228,f229,f230,f231,f232,f233,f234,f235,f236,f237,f238,f239,f240,f241,f242,f243,f244,f245,f246,f247,f248,f249,f250,f251,f252,f253,f254,f255,f256,f257,f258,f259,f260,f261,f262,f263,f264,f265,f266,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f277,f278,f279,f280,f281,f282,f283,f284,f285,f286,f287,f288,f289,f290,f291,f292,f293,f294,f295,f296,f297,f298,f299,f300,f301,f302,f303,f304,f305,f306,f307,f308,f309,f310,f311,f312,f313,f314,f315,f316,f317,f318,f319,f320,f321,f322,f323,f324,f325,f326,f327,f328,f329,f330,f331,f332,f333,f334,f335,f336,f337,f338,f339,f340,f341,f342,f343,f344,f345,f346,f347,f348,f349,f350,f351,f352,f353,f354,f355,f356,f357,f358,f359,f360,f361,f362,f363,f364,f365,f366,f367,f368,f369,f370,f371,f372,f373,f374,f375,f376,f377,f378,f379,f380,f381,f382,f383,f384,f385,f386,f387,f388,f389,f390,f391,f392,f393,f394,f395,f396,f397,f398,f399,f400,f401,f402,f403,f404,f405,f406,f407,f408,f409,f410,f411,f412,f413,f414,f415,f416,f417,f418,f419,f420,f421,f422,f423,f424,f425,f426,f427,f428,f429,f430,f431,f432,f433,f434,f435,f436,f437,f438,f439,f440,f441,f442,f443,f444,f445,f446,f447,f448,f449,f450,f451,f452,f453,f454,f455,f456,f457,f458,f459,f460,f461,f462,f463,f464,f465,f466,f467,f468,f469,f470,f471,f472,f473,f474,f475,f476,f477,f478,f479,f480,f481,f482,f483,f484,f485,f486,f487,f488,f489,f490,f491,f492,f493,f494,f495,f496,f497,f498,f499,f500,f501,f502,f503,f504,f505,f506,f507,f508,f509,f510,f511,f512,f513,f514,f515,f516,f517,f518,f519,f520,f521,f522,f523,f524,f525,f526,f527,f528,f529,f530,f531,f532,f533,f534,f535,f536,f537,f538,f539,f540,f541,f542,f543,f544,f545,f546,f547,f548,f549,f550,f551,f552,f553,f554,f555,f556,f557,f558,f559,f560,f561,f562,f563,f564,f565,f566,f567,f568,f569,f570,f571,f572,f573,f574,f575,f576,f577,f578,f579,f580,f581,f582,f583,f584,f585,f586,f587,f588,f589,f590,f591,f592,f593,f594,f595,f596,f597,f598,f599,f600,f601,f602,f603,f604,f605,f606,f607,f608,f609,f610,f611,f612,f613,f614,f615,f616,f617,f618,f619,f620,f621,f622,f623,f624,f625,f626,f627,f628,f629,f630,f631,f632,f633,f634,f635,f636,f637,f638,f639,f640,f641,f642,f643,f644,f645,f646,f647,f648,f649,f650,f651,f652,f653,f654,f655,f656,f657,f658,f659,f660,f661,f662,f663,f664,f665,f666,f667,f668,f669,f670,f671,f672,f673,f674,f675,f676,f677,f678,f679,f680,f681,f682,f683,f684,f685,f686,f687,f688,f689,f690,f691,f692,f693,f694,f695,f696,f697,f698,f699,f700,f701,f702,f703,f704,f705,f706,f707,f708,f709,f710,f711,f712,f713,f714,f715,f716,f717,f718,f719,f720,f721,f722,f723,f724,f725,f726,f727,f728,f729,f730,f731,f732,f733,f734,f735,f736,f737,f738,f739,f740,f741,f742,f743,f744,f745,f746,f747,f748,f749,f750,f751,f752,f753,f754,f755,f756,f757,f758,f759,f760,f761,f762,f763,f764,f765,f766,f767,f768,f769,f770,f771,f772,f773,f774,f775,f776,f777,f778,f779,f780,f781,f782,f783,f784,f785,f786,f787,f788,f789,f790,f791,f792,f793,f794,f795,f796,f797,f798,f799,f800,f801,f802,f803,f804,f805,f806,f807,f808,f809,f810,f811,f812,f813,f814,f815,f816,f817,f818,f819,f820,f821,f822,f823,f824,f825,f826,f827,f828,f829,f830,f831,f832,f833,f834,f835,f836,f837,f838,f839,f840,f841,f842,f843,f844,f845,f846,f847,f848,f849,f850,f851,f852,f853,f854,f855,f856,f857,f858,f859,f860,f861,f862,f863,f864,f865,f866,f867,f868,f869,f870,f871,f872,f873,f874,f875,f876,f877,f878,f879,f880,f881,f882,f883,f884,f885,f886,f887,f888,f889,f890,f891,f892,f893,f894,f895,f896,f897,f898,f899,f900,f901,f902,f903,f904,f905,f906,f907,f908,f909,f910,f911,f912,f913,f914,f915,f916,f917,f918,f919,f920,f921,f922,f923,f924,f925,f926,f927,f928,f929,f930,f931,f932,f933,f934,f935,f936,f937,f938,f939,f940,f941,f942,f943,f944,f945,f946,f947,f948,f949,f950,f951,f952,f953,f954,f955,f956,f957,f958,f959,f960,f961,f962,f963,f964,f965,f966,f967,f968,f969,f970,f971,f972,f973,f974,f975,f976,f977,f978,f979,f980,f981,f982,f983,f984,f985,f986,f987,f988,f989,f990,f991,f992,f993,f994,f995,f996,f997,f998,f999,f1000'
        }
        
        response = self.session.get(url, params=params, timeout=10)
        data = response.json()
        
        if data and 'data' in data:
            item = data['data']
            return [{
                'code': item.get('f57', code),
                'name': item.get('f58', ''),
                'price': float(item.get('f107', 0) or 0),
                'change_pct': float(item.get('f170', 0) or 0),
                'volume_ratio': float(item.get('f184', 0) or 0),
                'turnover_rate': float(item.get('f168', 0) or 0),
                'market_cap': float(item.get('f116', 0) or 0),
                'market': get_market_label(code)
            }]
        
        return []
    
    def _search_by_name(self, name: str) -> List[Dict]:
        url = 'http://push2.eastmoney.com/api/qt/suggest/get'
        params = {
            'input': name,
            'type': '14',
            'token': 'd41d8cd98f00b204e9800998ecf8427e',
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'rtntype': '6'
        }
        
        response = self.session.get(url, params=params, timeout=10)
        data = response.json()
        
        stocks = []
        if data and 'data' in data:
            for item in data['data'][:20]:
                code = item.get('id', '')
                if code and len(code) == 6:
                    stocks.append({
                        'code': code,
                        'name': item.get('name', ''),
                        'price': float(item.get('price', 0) or 0),
                        'change_pct': float(item.get('change', 0) or 0),
                        'volume_ratio': 0,
                        'turnover_rate': 0,
                        'market_cap': 0,
                        'market': get_market_label(code)
                    })
        
        return stocks
    
    def get_hot_sectors(self) -> List[Dict]:
        if HAS_AKSHARE:
            try:
                df = ak.board_concept_name_em()
                sectors = []
                for _, row in df.head(50).iterrows():
                    sector_name = row['板块名称']
                    sectors.append({
                        'code': row['板块代码'],
                        'name': sector_name,
                        'change_pct': row.get('涨跌幅', 0),
                        'leading_stock': row.get('领涨股票', ''),
                        'leading_stock_code': row.get('领涨股票-代码', ''),
                        'type': 'concept',
                        'category': get_sector_category(sector_name)
                    })
                return sectors
            except Exception as e:
                print(f"akshare获取板块数据失败: {e}")
        
        try:
            return self._get_real_sectors()
        except Exception as e:
            print(f"获取板块数据失败: {e}")
            return []
    
    def _get_real_sectors(self) -> List[Dict]:
        sectors = []
        
        concept_url = 'http://push2.eastmoney.com/api/qt/clist/get'
        concept_params = {
            'pn': 1,
            'pz': 100,
            'po': 1,
            'np': 1,
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:90+t:2',
            'fields': 'f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13'
        }
        
        try:
            response = self.session.get(concept_url, params=concept_params, timeout=10)
            data = response.json()
            
            if data and 'data' in data and 'diff' in data['data']:
                for item in data['data']['diff']:
                    sector_name = item.get('f14', '')
                    sectors.append({
                        'code': item.get('f12', ''),
                        'name': sector_name,
                        'change_pct': float(item.get('f3', 0) or 0),
                        'leading_stock': '',
                        'leading_stock_code': '',
                        'type': 'concept',
                        'category': get_sector_category(sector_name)
                    })
        except Exception as e:
            print(f"获取概念板块失败: {e}")
        
        industry_url = 'http://push2.eastmoney.com/api/qt/clist/get'
        industry_params = {
            'pn': 1,
            'pz': 50,
            'po': 1,
            'np': 1,
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:90+t:3',
            'fields': 'f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13'
        }
        
        try:
            response = self.session.get(industry_url, params=industry_params, timeout=10)
            data = response.json()
            
            if data and 'data' in data and 'diff' in data['data']:
                for item in data['data']['diff']:
                    sector_name = item.get('f14', '')
                    sectors.append({
                        'code': item.get('f12', ''),
                        'name': sector_name + '(行业)',
                        'change_pct': float(item.get('f3', 0) or 0),
                        'leading_stock': '',
                        'leading_stock_code': '',
                        'type': 'industry',
                        'category': get_sector_category(sector_name)
                    })
        except Exception as e:
            print(f"获取行业板块失败: {e}")
        
        sectors.sort(key=lambda x: x['change_pct'], reverse=True)
        
        return sectors
    
    def get_sector_stocks(self, sector_code: str) -> List[Dict]:
        if HAS_AKSHARE:
            try:
                df = ak.board_concept_cons_em(symbol=sector_code)
                stocks = []
                for _, row in df.iterrows():
                    code = str(row['代码'])
                    stocks.append({
                        'code': code,
                        'name': row['名称'],
                        'price': row.get('最新价', 0),
                        'change_pct': row.get('涨跌幅', 0),
                        'volume_ratio': row.get('量比', 0),
                        'turnover_rate': row.get('换手率', 0),
                        'market_cap': row.get('总市值', 0),
                        'market': get_market_label(code)
                    })
                return stocks
            except Exception as e:
                print(f"akshare获取板块成分股失败: {e}")
        
        try:
            return self._get_real_sector_stocks(sector_code)
        except Exception as e:
            print(f"获取板块成分股失败: {e}")
            return []
    
    def _get_real_sector_stocks(self, sector_code: str) -> List[Dict]:
        url = 'http://push2.eastmoney.com/api/qt/clist/get'
        params = {
            'pn': 1,
            'pz': 100,
            'po': 1,
            'np': 1,
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': f'b:{sector_code}+f:!50',
            'fields': 'f12,f14,f2,f3,f4,f5,f6,f15,f16,f17,f18,f10,f8,f9,f23,f20,f21'
        }
        
        response = self.session.get(url, params=params, timeout=10)
        data = response.json()
        
        stocks = []
        if data and 'data' in data and 'diff' in data['data']:
            for item in data['data']['diff']:
                code = str(item.get('f12', ''))
                stocks.append({
                    'code': code,
                    'name': item.get('f14', ''),
                    'price': float(item.get('f2', 0) or 0),
                    'change_pct': float(item.get('f3', 0) or 0),
                    'change': float(item.get('f4', 0) or 0),
                    'volume': float(item.get('f5', 0) or 0) / 10000,  # 转换为万手
                    'amount': float(item.get('f6', 0) or 0) / 100000000,  # 转换为亿
                    'volume_ratio': float(item.get('f10', 0) or 0),
                    'turnover_rate': float(item.get('f8', 0) or 0),
                    'market_cap': float(item.get('f20', 0) or 0),
                    'market': get_market_label(code)
                })
        
        return stocks
    
    def get_all_a_stocks(self) -> List[Dict]:
        if HAS_AKSHARE:
            try:
                df = ak.stock_zh_a_spot_em()
                stocks = []
                for _, row in df.iterrows():
                    code = str(row['代码'])
                    stocks.append({
                        'code': code,
                        'name': row['名称'],
                        'price': row.get('最新价', 0),
                        'change_pct': row.get('涨跌幅', 0),
                        'volume_ratio': row.get('量比', 0),
                        'turnover_rate': row.get('换手率', 0),
                        'market_cap': row.get('总市值', 0),
                        'amount': row.get('成交额', 0),
                        'market': get_market_label(code)
                    })
                return stocks
            except Exception as e:
                print(f"akshare获取A股数据失败: {e}")
        
        try:
            return self._get_real_all_stocks()
        except Exception as e:
            print(f"获取A股数据失败: {e}")
            return []
    
    def _get_real_all_stocks(self) -> List[Dict]:
        stocks = []
        
        market_configs = [
            ('m:0+t:6,m:0+t:80', '深主板'),
            ('m:0+t:13', '创业板'),
            ('m:1+t:2', '沪主板'),
            ('m:1+t:23', '科创板'),
        ]
        
        for fs, market_name in market_configs:
            try:
                url = 'http://push2.eastmoney.com/api/qt/clist/get'
                params = {
                    'pn': 1,
                    'pz': 500,
                    'po': 1,
                    'np': 1,
                    'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                    'fltt': 2,
                    'invt': 2,
                    'fid': 'f3',
                    'fs': fs,
                    'fields': 'f12,f14,f2,f3,f4,f5,f6,f15,f16,f17,f18,f10,f8,f9,f23,f20,f21,f37'
                }
                
                response = self.session.get(url, params=params, timeout=15)
                data = response.json()
                
                if data and 'data' in data and 'diff' in data['data']:
                    for item in data['data']['diff']:
                        change_pct = float(item.get('f3', 0) or 0)
                        price = float(item.get('f2', 0) or 0)
                        code = str(item.get('f12', ''))
                        
                        if price > 0:
                            stocks.append({
                                'code': code,
                                'name': item.get('f14', ''),
                                'price': price,
                                'change_pct': change_pct,
                                'change': float(item.get('f4', 0) or 0),
                                'volume': float(item.get('f5', 0) or 0) / 10000,  # 转换为万手
                                'amount': float(item.get('f6', 0) or 0) / 100000000,  # 转换为亿
                                'volume_ratio': float(item.get('f10', 0) or 0),
                                'turnover_rate': float(item.get('f8', 0) or 0),
                                'market_cap': float(item.get('f20', 0) or 0),
                                'market': get_market_label(code)
                            })
            except Exception as e:
                print(f"获取{market_name}数据失败: {e}")
        
        return stocks
    
    def screen_leader_stocks(self, sector: Optional[str] = None, top_n: int = 10) -> List[Dict]:
        if sector:
            stocks = self.get_sector_stocks(sector)
        else:
            stocks = self.get_all_a_stocks()
        
        if not stocks:
            return []
        
        for stock in stocks:
            stock['score'] = self._calculate_single_score(stock)
        
        stocks.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return stocks[:top_n]
    
    def _calculate_single_score(self, stock: Dict) -> float:
        score = 0.0
        
        change_pct = stock.get('change_pct', 0)
        score += max(-30, min(30, change_pct * 3))
        
        volume_ratio = stock.get('volume_ratio', 0)
        score += max(0, min(10, (volume_ratio - 1) * 2))
        
        turnover_rate = stock.get('turnover_rate', 0)
        if 3 < turnover_rate < 10:
            score += 5
        elif turnover_rate >= 10:
            score += 3
        
        market_cap = stock.get('market_cap', 0)
        if market_cap > 0:
            score += min(10, math.log10(market_cap) - 8)
        
        return round(score, 2)
    
    def get_stock_detail(self, stock_code: str) -> Dict:
        if HAS_AKSHARE:
            try:
                df = ak.stock_individual_info_em(symbol=stock_code)
                detail = {}
                for _, row in df.iterrows():
                    detail[row['item']] = row['value']
                detail['market'] = get_market_label(stock_code)
                return detail
            except Exception as e:
                print(f"获取股票详情失败: {e}")
        
        try:
            return self._get_real_stock_detail(stock_code)
        except Exception as e:
            print(f"获取股票详情失败: {e}")
            return {'code': stock_code, 'name': '', 'industry': '', 'market': get_market_label(stock_code)}
    
    def _get_real_stock_detail(self, stock_code: str) -> Dict:
        market = '1' if stock_code.startswith('6') else '0'
        secid = f"{market}.{stock_code}"
        url = 'http://push2.eastmoney.com/api/qt/stock/get'
        params = {
            'secid': secid,
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'fields': 'f57,f58,f84,f85,f116,f117,f162,f167,f92,f173,f187,f105,f190'
        }
        
        response = self.session.get(url, params=params, timeout=10)
        data = response.json()
        
        if data and 'data' in data:
            item = data['data']
            return {
                'code': item.get('f57', stock_code),
                'name': item.get('f58', ''),
                'industry': item.get('f116', ''),
                'total_share': item.get('f84', 0),
                'float_share': item.get('f85', 0),
                'market': get_market_label(stock_code)
            }
        
        return {'code': stock_code, 'name': '', 'industry': '', 'market': get_market_label(stock_code)}
    
    def get_stock_history(self, stock_code: str, days: int = 30) -> List[Dict]:
        if HAS_AKSHARE:
            try:
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
                
                df = ak.stock_zh_a_hist(symbol=stock_code, period='daily', 
                                        start_date=start_date, end_date=end_date, adjust='qfq')
                
                history = []
                for _, row in df.iterrows():
                    history.append({
                        'date': row['日期'],
                        'open': row['开盘'],
                        'close': row['收盘'],
                        'high': row['最高'],
                        'low': row['最低'],
                        'volume': row['成交量'],
                        'amount': row['成交额'],
                        'change_pct': row.get('涨跌幅', 0)
                    })
                return history
            except Exception as e:
                print(f"获取股票历史数据失败: {e}")
        
        try:
            return self._get_real_stock_history(stock_code, days)
        except Exception as e:
            print(f"获取股票历史数据失败: {e}")
            return []
    
    def _get_real_stock_history(self, stock_code: str, days: int = 30) -> List[Dict]:
        market = '1' if stock_code.startswith('6') else '0'
        secid = f"{market}.{stock_code}"
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')
        
        url = 'http://push2his.eastmoney.com/api/qt/stock/kline/get'
        params = {
            'secid': secid,
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'fields1': 'f1,f2,f3,f4,f5,f6',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
            'klt': 101,
            'fqt': 1,
            'beg': start_date,
            'end': end_date
        }
        
        response = self.session.get(url, params=params, timeout=10)
        data = response.json()
        
        history = []
        if data and 'data' in data and 'klines' in data['data']:
            for kline in data['data']['klines'][-days:]:
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
    
    def get_index_data(self) -> Dict:
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
        
        for key, secid in index_codes:
            try:
                url = 'http://push2.eastmoney.com/api/qt/stock/get'
                params = {
                    'secid': secid,
                    'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                    'fields': 'f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f169,f170'
                }
                
                response = self.session.get(url, params=params, timeout=5)
                data = response.json()
                
                if data and 'data' in data:
                    item = data['data']
                    indexes[key]['price'] = float(item.get('f43', 0) or 0) / 100
                    indexes[key]['change'] = float(item.get('f169', 0) or 0) / 100
                    indexes[key]['change_pct'] = float(item.get('f170', 0) or 0) / 100
            except Exception as e:
                print(f"获取{indexes[key]['name']}数据失败: {e}")
        
        return indexes
    
    def get_kline_data(self, stock_code: str, days: int = 60) -> Dict:
        history = self._get_real_stock_history(stock_code, days)
        
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
    
    def get_quote(self, stock_code: str) -> Dict:
        """获取单个股票的实时行情"""
        try:
            return self._get_real_stock_quote(stock_code)
        except Exception as e:
            print(f"获取股票实时行情失败: {e}")
            # 返回模拟数据
            return {
                'code': stock_code,
                'name': '',
                'price': 0,
                'change': 0,
                'change_pct': 0,
                'volume': 0
            }
    
    def _get_real_stock_quote(self, stock_code: str) -> Dict:
        """从东方财富获取实时行情"""
        market = '1' if stock_code.startswith('6') else '0'
        secid = f"{market}.{stock_code}"
        url = 'http://push2.eastmoney.com/api/qt/stock/get'
        params = {
            'secid': secid,
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'fields': 'f57,f58,f107,f108,f109,f110,f111,f112,f113,f114,f115,f116,f117,f169,f170,f152'
        }
        
        response = self.session.get(url, params=params, timeout=10)
        data = response.json()
        
        if data and 'data' in data:
            item = data['data']
            price = float(item.get('f107', 0) or 0)
            change = float(item.get('f169', 0) or 0) / 100
            change_pct = float(item.get('f170', 0) or 0) / 100
            volume = float(item.get('f152', 0) or 0)
            
            return {
                'code': item.get('f57', stock_code),
                'name': item.get('f58', ''),
                'price': price,
                'change': change,
                'change_pct': change_pct,
                'volume': volume
            }
        
        return {
            'code': stock_code,
            'name': '',
            'price': 0,
            'change': 0,
            'change_pct': 0,
            'volume': 0
        }
