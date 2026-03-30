"""
东方财富API字段映射配置

本模块定义了东方财富API返回的字段(f开头)与实际业务字段的映射关系，
以及字段的单位转换规则。

注意：不同接口返回的数据格式可能不同：
1. qt/stock/get 接口：价格字段需要除以100
2. qt/clist/get 接口：价格字段已经是正确格式，不需要除以100
"""

from typing import Dict, Callable, Any

# ============================================
# 1. 股票实时行情字段映射 (qt/stock/get 接口)
# ============================================
# 接口: http://push2.eastmoney.com/api/qt/stock/get
# 参数: secid, ut, fields
# 注意：此接口返回的价格字段需要除以100

STOCK_QUOTE_FIELDS = {
    # 基础信息
    'f57': {'name': 'code', 'desc': '股票代码', 'unit': None},
    'f58': {'name': 'name', 'desc': '股票名称', 'unit': None},

    # 价格信息 (需要除以100)
    'f43': {'name': 'price', 'desc': '最新价', 'unit': '元', 'divisor': 100},
    'f44': {'name': 'open', 'desc': '开盘价', 'unit': '元', 'divisor': 100},
    'f45': {'name': 'high', 'desc': '最高价', 'unit': '元', 'divisor': 100},
    'f46': {'name': 'low', 'desc': '最低价', 'unit': '元', 'divisor': 100},
    'f47': {'name': 'volume', 'desc': '成交量(股)', 'unit': '股', 'divisor': 1},
    'f48': {'name': 'amount', 'desc': '成交额(元)', 'unit': '元', 'divisor': 1},

    # 涨跌信息 (需要除以100)
    'f169': {'name': 'change', 'desc': '涨跌额', 'unit': '元', 'divisor': 100},
    'f170': {'name': 'change_pct', 'desc': '涨跌幅', 'unit': '%', 'divisor': 100},

    # 市值 (原始单位：元)
    'f116': {'name': 'market_cap', 'desc': '总市值', 'unit': '元', 'divisor': 1},
    'f117': {'name': 'float_market_cap', 'desc': '流通市值', 'unit': '元', 'divisor': 1},
}

# ============================================
# 2. 股票列表/板块字段映射 (qt/clist/get 接口)
# ============================================
# 接口: http://push2.eastmoney.com/api/qt/clist/get
# 参数: pn, pz, po, np, ut, fltt, invt, fid, fs, fields
# 注意：此接口返回的价格字段已经是正确格式，不需要除以100

STOCK_LIST_FIELDS = {
    # 基础信息
    'f12': {'name': 'code', 'desc': '股票代码', 'unit': None},
    'f14': {'name': 'name', 'desc': '股票名称', 'unit': None},

    # 价格信息 (已经是正确格式，不需要除以100)
    'f2': {'name': 'price', 'desc': '最新价', 'unit': '元', 'divisor': 1},
    'f3': {'name': 'change_pct', 'desc': '涨跌幅', 'unit': '%', 'divisor': 1},
    'f4': {'name': 'change', 'desc': '涨跌额', 'unit': '元', 'divisor': 1},
    'f15': {'name': 'high', 'desc': '最高价', 'unit': '元', 'divisor': 1},
    'f16': {'name': 'low', 'desc': '最低价', 'unit': '元', 'divisor': 1},
    'f17': {'name': 'open', 'desc': '开盘价', 'unit': '元', 'divisor': 1},
    'f18': {'name': 'prev_close', 'desc': '昨收', 'unit': '元', 'divisor': 1},

    # 成交量和成交额 (原始单位)
    'f5': {'name': 'volume', 'desc': '成交量', 'unit': '手', 'divisor': 1},
    'f6': {'name': 'amount', 'desc': '成交额', 'unit': '元', 'divisor': 1},

    # 其他指标 (已经是正确格式)
    'f8': {'name': 'turnover_rate', 'desc': '换手率', 'unit': '%', 'divisor': 1},
    'f9': {'name': 'pe_ratio', 'desc': '市盈率', 'unit': '倍', 'divisor': 1},
    'f10': {'name': 'volume_ratio', 'desc': '量比', 'unit': '倍', 'divisor': 1},
    'f20': {'name': 'market_cap', 'desc': '总市值', 'unit': '亿元', 'divisor': 1},
    'f21': {'name': 'float_market_cap', 'desc': '流通市值', 'unit': '亿元', 'divisor': 1},
    'f23': {'name': 'pb_ratio', 'desc': '市净率', 'unit': '倍', 'divisor': 1},
    'f37': {'name': 'roe', 'desc': '净资产收益率', 'unit': '%', 'divisor': 1},
}

# ============================================
# 3. 股票详细信息字段映射 (qt/stock/get 接口)
# ============================================
# 接口: http://push2.eastmoney.com/api/qt/stock/get
# 参数: secid, ut, fields
# 注意：此接口返回的数据需要除以100

STOCK_DETAIL_FIELDS = {
    # 基础信息
    'f57': {'name': 'code', 'desc': '股票代码', 'unit': None},
    'f58': {'name': 'name', 'desc': '股票名称', 'unit': None},
    'f107': {'name': 'industry', 'desc': '所属行业', 'unit': None},

    # 股本信息
    'f84': {'name': 'total_share', 'desc': '总股本', 'unit': '股', 'divisor': 1},
    'f85': {'name': 'float_share', 'desc': '流通股本', 'unit': '股', 'divisor': 1},

    # 市值信息 (原始单位：元)
    'f116': {'name': 'market_cap', 'desc': '总市值', 'unit': '元', 'divisor': 1},
    'f117': {'name': 'float_market_cap', 'desc': '流通市值', 'unit': '元', 'divisor': 1},

    # 估值指标 (需要除以100)
    'f162': {'name': 'pe_ratio', 'desc': '市盈率(静)', 'unit': '倍', 'divisor': 1},
    'f167': {'name': 'pb_ratio', 'desc': '市净率', 'unit': '倍', 'divisor': 1},
    'f92': {'name': 'roe', 'desc': '净资产收益率', 'unit': '%', 'divisor': 1},
    'f173': {'name': 'eps', 'desc': '每股收益', 'unit': '元', 'divisor': 1},
    'f187': {'name': 'bps', 'desc': '每股净资产', 'unit': '元', 'divisor': 1},

    # 财务数据 (原始单位：元)
    'f105': {'name': 'revenue', 'desc': '营业收入', 'unit': '元', 'divisor': 1},
    'f190': {'name': 'profit', 'desc': '净利润', 'unit': '元', 'divisor': 1},
}

# ============================================
# 4. 历史数据字段映射 (qt/stock/kline/get 接口)
# ============================================
# 接口: http://push2his.eastmoney.com/api/qt/stock/kline/get
# 参数: secid, ut, fields1, fields2, klt, fqt, beg, end

STOCK_HISTORY_FIELDS = {
    'f51': {'name': 'date', 'desc': '日期', 'unit': None},
    'f52': {'name': 'open', 'desc': '开盘价', 'unit': '元', 'divisor': 1},
    'f53': {'name': 'close', 'desc': '收盘价', 'unit': '元', 'divisor': 1},
    'f54': {'name': 'high', 'desc': '最高价', 'unit': '元', 'divisor': 1},
    'f55': {'name': 'low', 'desc': '最低价', 'unit': '元', 'divisor': 1},
    'f56': {'name': 'volume', 'desc': '成交量', 'unit': '手', 'divisor': 1},
    'f57': {'name': 'amount', 'desc': '成交额', 'unit': '元', 'divisor': 1},
    'f58': {'name': 'amplitude', 'desc': '振幅', 'unit': '%', 'divisor': 1},
    'f59': {'name': 'change_pct', 'desc': '涨跌幅', 'unit': '%', 'divisor': 1},
    'f60': {'name': 'change', 'desc': '涨跌额', 'unit': '元', 'divisor': 1},
    'f61': {'name': 'turnover_rate', 'desc': '换手率', 'unit': '%', 'divisor': 1},
}

# ============================================
# 5. 板块数据字段映射 (qt/clist/get 接口)
# ============================================
# 接口: http://push2.eastmoney.com/api/qt/clist/get
# 参数: pn, pz, po, np, ut, fltt, invt, fid, fs, fields

SECTOR_FIELDS = {
    'f12': {'name': 'code', 'desc': '板块代码', 'unit': None},
    'f14': {'name': 'name', 'desc': '板块名称', 'unit': None},
    'f3': {'name': 'change_pct', 'desc': '涨跌幅', 'unit': '%', 'divisor': 1},
    'f2': {'name': 'price', 'desc': '最新价', 'unit': '元', 'divisor': 1},
    'f4': {'name': 'change', 'desc': '涨跌额', 'unit': '元', 'divisor': 1},
    'f5': {'name': 'volume', 'desc': '成交量', 'unit': '手', 'divisor': 1},
    'f6': {'name': 'amount', 'desc': '成交额', 'unit': '元', 'divisor': 1},
    'f8': {'name': 'turnover_rate', 'desc': '换手率', 'unit': '%', 'divisor': 1},
    'f10': {'name': 'volume_ratio', 'desc': '量比', 'unit': '倍', 'divisor': 1},
    'f15': {'name': 'high', 'desc': '最高价', 'unit': '元', 'divisor': 1},
    'f16': {'name': 'low', 'desc': '最低价', 'unit': '元', 'divisor': 1},
    'f17': {'name': 'open', 'desc': '开盘价', 'unit': '元', 'divisor': 1},
    'f18': {'name': 'prev_close', 'desc': '昨收', 'unit': '元', 'divisor': 1},
}

# ============================================
# 6. 字段转换工具函数
# ============================================

def convert_field(value: Any, field_config: Dict) -> Any:
    """
    根据字段配置转换值

    Args:
        value: 原始值
        field_config: 字段配置字典

    Returns:
        转换后的值
    """
    if value is None or value == '':
        return 0

    divisor = field_config.get('divisor', 1)
    if divisor and divisor != 1:
        try:
            return float(value) / divisor
        except (ValueError, TypeError):
            return 0
    return value


def parse_eastmoney_data(data: Dict, field_mapping: Dict) -> Dict:
    """
    解析东方财富API返回的数据

    Args:
        data: API返回的原始数据
        field_mapping: 字段映射配置

    Returns:
        解析后的业务数据
    """
    result = {}
    for east_field, config in field_mapping.items():
        if east_field in data:
            value = data[east_field]
            business_name = config['name']
            result[business_name] = convert_field(value, config)
    return result


# ============================================
# 6. 常用字段组合
# ============================================

# 实时行情常用字段
QUOTE_FIELDS_BASIC = 'f57,f58,f43,f169,f170'  # 代码、名称、价格、涨跌额、涨跌幅
QUOTE_FIELDS_FULL = 'f57,f58,f43,f44,f45,f46,f47,f48,f169,f170,f116,f152'  # 完整行情

# 列表查询常用字段
LIST_FIELDS_BASIC = 'f12,f14,f2,f3,f4'  # 代码、名称、价格、涨跌幅、涨跌额
LIST_FIELDS_FULL = 'f12,f14,f2,f3,f4,f5,f6,f8,f9,f10,f20,f21'  # 完整列表

# 详细信息常用字段
DETAIL_FIELDS_BASIC = 'f57,f58,f107,f84,f85,f116,f117'  # 代码、名称、行业、股本、市值
DETAIL_FIELDS_FULL = 'f57,f58,f107,f84,f85,f116,f117,f162,f167,f92,f173,f187,f105,f190'  # 完整详情


# ============================================
# 7. 使用示例
# ============================================
"""
使用示例:

from services.eastmoney_fields import (
    STOCK_QUOTE_FIELDS,
    STOCK_LIST_FIELDS,
    STOCK_DETAIL_FIELDS,
    parse_eastmoney_data,
    QUOTE_FIELDS_FULL,
    LIST_FIELDS_FULL
)

# 1. 解析实时行情数据 (qt/stock/get 接口)
raw_data = {
    'f57': '600519',
    'f58': '贵州茅台',
    'f43': 141602,      # 需要除以100
    'f169': 1484,       # 需要除以100
    'f170': 106,        # 需要除以100
    'f103': 86239108106.25,
    'f116': 1773239669844.3
}
parsed_data = parse_eastmoney_data(raw_data, STOCK_QUOTE_FIELDS)
# 结果: {
#     'code': '600519',
#     'name': '贵州茅台',
#     'price': 1416.02,  # 141602 / 100
#     'change': 14.84,   # 1484 / 100
#     'change_pct': 1.06, # 106 / 100
#     'amount': 86239108106.25,
#     'market_cap': 1773239669844.3
# }

# 2. 解析列表数据 (qt/clist/get 接口)
raw_data = {
    'f12': '600519',
    'f14': '贵州茅台',
    'f2': 1416.02,      # 已经是正确格式
    'f3': 1.06,         # 已经是正确格式
    'f4': 14.84,        # 已经是正确格式
    'f20': 17732.4      # 已经是亿元单位
}
parsed_data = parse_eastmoney_data(raw_data, STOCK_LIST_FIELDS)
# 结果: {
#     'code': '600519',
#     'name': '贵州茅台',
#     'price': 1416.02,   # 保持不变
#     'change_pct': 1.06, # 保持不变
#     'change': 14.84,    # 保持不变
#     'market_cap': 17732.4  # 保持不变
# }

# 3. 获取字段描述
print(STOCK_QUOTE_FIELDS['f43']['desc'])  # 输出: 最新价
print(STOCK_QUOTE_FIELDS['f43']['unit'])  # 输出: 元

# 4. 构建API请求参数
params = {
    'fields': QUOTE_FIELDS_FULL
}
"""