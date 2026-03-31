#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
akshare 数据字段映射与单位换算模块
用于统一处理 akshare 返回的数据格式
"""

from typing import Dict, Any, Optional
import pandas as pd

# ==================== 股票实时行情字段映射 ====================
# akshare.stock_zh_a_spot_em 返回的字段
STOCK_QUOTE_FIELDS = {
    '代码': 'code',
    '名称': 'name',
    '最新价': 'price',
    '涨跌幅': 'change_pct',
    '涨跌额': 'change',
    '成交量': 'volume',
    '成交额': 'amount',
    '振幅': 'amplitude',
    '最高': 'high',
    '最低': 'low',
    '今开': 'open',
    '昨收': 'prev_close',
    '量比': 'volume_ratio',
    '换手率': 'turnover_rate',
    '市盈率-动态': 'pe_ratio',
    '市净率': 'pb_ratio',
    '总市值': 'total_market_cap',
    '流通市值': 'float_market_cap',
    '涨速': 'change_speed',
    '5分钟涨跌': 'change_5min',
    '60日涨跌幅': 'change_60d',
    '年初至今涨跌幅': 'change_ytd',
}

# ==================== 指数实时行情字段映射 ====================
# akshare.stock_zh_index_spot_sina 返回的字段
INDEX_QUOTE_FIELDS = {
    '代码': 'code',
    '名称': 'name',
    '最新价': 'price',
    '涨跌额': 'change',
    '涨跌幅': 'change_pct',
    '昨收': 'prev_close',
    '今开': 'open',
    '最高': 'high',
    '最低': 'low',
    '成交量': 'volume',
    '成交额': 'amount',
}

# ==================== 板块数据字段映射 ====================
# akshare.stock_board_concept_name_ths / stock_board_industry_name_ths 返回的字段
BOARD_FIELDS = {
    '代码': 'code',
    '名称': 'name',
    'code': 'code',
    'name': 'name',
}

# ==================== 股票历史数据字段映射 ====================
# akshare.stock_zh_a_hist 返回的字段
STOCK_HISTORY_FIELDS = {
    '日期': 'date',
    '开盘': 'open',
    '收盘': 'close',
    '最高': 'high',
    '最低': 'low',
    '成交量': 'volume',
    '成交额': 'amount',
    '振幅': 'amplitude',
    '涨跌幅': 'change_pct',
    '涨跌额': 'change',
    '换手率': 'turnover_rate',
}

# ==================== 单位换算配置 (Divider) ====================
# 金额单位换算 (原始数据通常是元，转换为万元或亿元)
# divider = 1: 保持原样
# divider = 10000: 转换为万元
# divider = 100000000: 转换为亿元
AMOUNT_UNIT_CONVERTERS = {
    'volume': 1,  # 成交量保持原样（股）
    'amount': 10000,  # 成交额转换为万元
    'total_market_cap': 100000000,  # 总市值转换为亿元
    'float_market_cap': 100000000,  # 流通市值转换为亿元
}

# 百分比单位换算 (原始数据通常是小数，转换为百分比)
# multiplier = 100: 小数转百分比 (0.01 -> 1.0)
# multiplier = 1: 保持原样 (已经是百分比格式)
PERCENTAGE_FIELDS = [
    'change_pct',
    'turnover_rate',
    'amplitude',
    'change_speed',
    'change_5min',
    'change_60d',
    'change_ytd',
]

# 数据源特定的 divider 配置
# 统一使用 divider (除法) 进行单位换算
# divider = 1: 保持原样
# divider = 100: 小数转百分比 (0.01 -> 1.0)
# divider = 10000: 转换为万元
# divider = 100000000: 转换为亿元
DIVIDER_CONFIG = {
    # 东方财富接口 (em): 金额单位为元，涨跌幅为小数
    'em': {
        'amount': {'divider': 10000, 'unit': '万元'},  # 成交额
        'volume': {'divider': 1, 'unit': '手'},  # 成交量
        'total_market_cap': {'divider': 1, 'unit': '亿元'},  # 总市值
        'float_market_cap': {'divider': 1, 'unit': '亿元'},  # 流通市值
        'change_pct': {'divider': 100, 'unit': '%'},  # 涨跌幅: 小数转百分比 (除以0.01等于乘以100)
        'turnover_rate': {'divider': 100, 'unit': '%'},  # 换手率
        'amplitude': {'divider': 100, 'unit': '%'},  # 振幅
    },
    # 新浪财经接口 (sina): 金额单位为元，涨跌幅已经是百分比
    'sina': {
        'amount': {'divider': 10000, 'unit': '万元'},
        'volume': {'divider': 1, 'unit': '手'},
        'total_market_cap': {'divider': 1, 'unit': '亿元'},
        'float_market_cap': {'divider': 1, 'unit': '亿元'},
        'change_pct': {'divider': 100, 'unit': '%'},  # 已经是百分比，保持不变
        'turnover_rate': {'divider': 100, 'unit': '%'},
        'amplitude': {'divider': 100, 'unit': '%'},
    },
    # 同花顺接口 (ths): 金额单位为元，涨跌幅为小数
    'ths': {
        'amount': {'divider': 10000, 'unit': '万元'},
        'volume': {'divider': 1, 'unit': '手'},
        'total_market_cap': {'divider': 1, 'unit': '亿元'},
        'float_market_cap': {'divider': 1, 'unit': '亿元'},
        'change_pct': {'divider': 100, 'unit': '%'},  # 涨跌幅: 小数转百分比
        'turnover_rate': {'divider': 100, 'unit': '%'},
        'amplitude': {'divider': 100, 'unit': '%'},
    },
}


def convert_units(data: Dict[str, Any], field_type: str = 'stock',
                  percent_format: str = 'decimal') -> Dict[str, Any]:
    """
    转换数据单位

    Args:
        data: 原始数据字典
        field_type: 数据类型 ('stock', 'index', 'board', 'history')
        percent_format: 百分比字段格式 ('decimal' 表示小数如0.01, 'percent' 表示百分比如1.0)

    Returns:
        转换后的数据字典
    """
    result = data.copy()

    # 百分比字段转换
    # 如果原始数据是小数格式(如0.01表示1%)，需要乘以100
    # 如果原始数据已经是百分比格式(如1.0表示1%)，不需要转换
    if percent_format == 'decimal':
        for field in PERCENTAGE_FIELDS:
            if field in result and result[field] is not None:
                try:
                    result[field] = float(result[field]) * 100
                except (ValueError, TypeError):
                    result[field] = 0

    # 金额字段转换
    for field, divisor in AMOUNT_UNIT_CONVERTERS.items():
        if field in result and result[field] is not None:
            try:
                result[field] = float(result[field]) / divisor
            except (ValueError, TypeError):
                result[field] = 0

    return result


def apply_dividers(data: Dict[str, Any], source: str = 'em') -> Dict[str, Any]:
    """
    使用 divider 配置进行数据换算

    Args:
        data: 原始数据字典
        source: 数据源类型 ('em', 'sina', 'ths')

    Returns:
        换算后的数据字典
    """
    result = data.copy()

    if source not in DIVIDER_CONFIG:
        return result

    config = DIVIDER_CONFIG[source]

    for field, settings in config.items():
        if field in result and result[field] is not None:
            try:
                value = float(result[field])

                # 应用 divider (除法) 进行单位换算
                # divider = 1: 保持原样
                # divider = 0.01: 小数转百分比 (除以0.01等于乘以100)
                # divider = 10000: 元转万元
                # divider = 100000000: 元转亿元
                if 'divider' in settings and settings['divider'] != 0:
                    value = value / settings['divider']

                result[field] = value
            except (ValueError, TypeError):
                result[field] = 0

    return result


def get_field_unit(field: str, source: str = 'em') -> str:
    """
    获取字段的单位

    Args:
        field: 字段名
        source: 数据源类型

    Returns:
        单位字符串
    """
    if source in DIVIDER_CONFIG and field in DIVIDER_CONFIG[source]:
        return DIVIDER_CONFIG[source][field].get('unit', '')
    return ''


def format_value_with_unit(value: float, field: str, source: str = 'em') -> str:
    """
    格式化数值并添加单位

    Args:
        value: 数值
        field: 字段名
        source: 数据源类型

    Returns:
        带单位的字符串
    """
    unit = get_field_unit(field, source)

    # 根据数值大小选择合适的小数位数
    if field in ['change_pct', 'turnover_rate', 'amplitude']:
        formatted = f"{value:.2f}"
    elif field in ['amount', 'total_market_cap', 'float_market_cap']:
        formatted = f"{value:.2f}"
    else:
        formatted = f"{value:.2f}"

    return f"{formatted}{unit}"


def parse_akshare_data(df: pd.DataFrame, field_mapping: Dict[str, str], 
                       code: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    解析 akshare 返回的 DataFrame 数据
    
    Args:
        df: akshare 返回的 DataFrame
        field_mapping: 字段映射字典
        code: 股票代码（用于筛选特定股票）
    
    Returns:
        解析后的数据字典
    """
    if df is None or df.empty:
        return None
    
    # 如果指定了代码，筛选特定股票
    if code:
        # 处理中英文列名
        if '代码' in df.columns:
            df = df[df['代码'] == code]
        elif 'code' in df.columns:
            df = df[df['code'] == code]
        else:
            return None
        
        if df.empty:
            return None
    
    # 获取第一条数据
    data = df.iloc[0].to_dict()
    
    # 字段映射转换
    result = {}
    for ak_field, std_field in field_mapping.items():
        if ak_field in data:
            result[std_field] = data[ak_field]
        elif ak_field.lower() in [k.lower() for k in data.keys()]:
            # 尝试大小写不敏感匹配
            for k in data.keys():
                if k.lower() == ak_field.lower():
                    result[std_field] = data[k]
                    break
    
    return result


def parse_stock_quote(df: pd.DataFrame, code: str) -> Optional[Dict[str, Any]]:
    """
    解析股票实时行情数据
    
    Args:
        df: akshare.stock_zh_a_spot_em 返回的 DataFrame
        code: 股票代码
    
    Returns:
        标准化的股票行情数据
    """
    data = parse_akshare_data(df, STOCK_QUOTE_FIELDS, code)
    if data:
        return convert_units(data, 'stock')
    return None


def parse_index_quote(df: pd.DataFrame, code: str) -> Optional[Dict[str, Any]]:
    """
    解析指数实时行情数据

    Args:
        df: akshare.stock_zh_index_spot_sina 返回的 DataFrame
        code: 指数代码

    Returns:
        标准化的指数行情数据
    """
    data = parse_akshare_data(df, INDEX_QUOTE_FIELDS, code)
    if data:
        # 使用 sina 的 divider 配置进行数据换算
        return apply_dividers(data, source='sina')
    return None


def parse_board_data(df: pd.DataFrame) -> list:
    """
    解析板块数据
    
    Args:
        df: akshare 返回的板块数据 DataFrame
    
    Returns:
        板块列表
    """
    if df is None or df.empty:
        return []
    
    result = []
    for _, row in df.iterrows():
        data = row.to_dict()
        item = {}
        
        # 处理中英文列名
        for ak_field, std_field in BOARD_FIELDS.items():
            if ak_field in data:
                item[std_field] = data[ak_field]
        
        # 添加默认值
        item.setdefault('change_pct', 0)
        item.setdefault('price', 0)
        item.setdefault('change', 0)
        item.setdefault('volume', 0)
        item.setdefault('amount', 0)
        
        result.append(item)
    
    return result


def parse_stock_history(df: pd.DataFrame) -> list:
    """
    解析股票历史数据
    
    Args:
        df: akshare.stock_zh_a_hist 返回的 DataFrame
    
    Returns:
        历史数据列表
    """
    if df is None or df.empty:
        return []
    
    result = []
    for _, row in df.iterrows():
        data = row.to_dict()
        item = {}
        
        for ak_field, std_field in STOCK_HISTORY_FIELDS.items():
            if ak_field in data:
                item[std_field] = data[ak_field]
        
        # 转换百分比字段
        if 'change_pct' in item:
            try:
                item['change_pct'] = float(item['change_pct'])
            except (ValueError, TypeError):
                item['change_pct'] = 0
        
        result.append(item)
    
    return result


# ==================== 代码转换工具 ====================
def convert_to_akshare_code(code: str) -> str:
    """
    将股票代码转换为 akshare 格式
    
    Args:
        code: 原始股票代码（如 '000001'）
    
    Returns:
        akshare 格式的代码（如 'sz000001'）
    """
    if code.startswith('6'):
        return f'sh{code}'
    elif code.startswith('00') or code.startswith('30'):
        return f'sz{code}'
    elif code.startswith('8') or code.startswith('4'):
        return f'bj{code}'
    return code


def convert_from_akshare_code(ak_code: str) -> str:
    """
    将 akshare 格式的代码转换为原始股票代码
    
    Args:
        ak_code: akshare 格式的代码（如 'sz000001'）
    
    Returns:
        原始股票代码（如 '000001'）
    """
    if ak_code.startswith(('sh', 'sz', 'bj')):
        return ak_code[2:]
    return ak_code


# ==================== 指数代码映射 ====================
INDEX_CODE_MAP = {
    '0.000001': 'sh000001',  # 上证指数
    '1.000001': 'sh000001',  # 上证指数（另一种格式）
    '0.399001': 'sz399001',  # 深证成指
    '0.399006': 'sz399006',  # 创业板指
    '1.000688': 'sh000688',  # 科创50
    '0.000016': 'sh000016',  # 上证50
    '0.000300': 'sh000300',  # 沪深300
    '0.000905': 'sh000905',  # 中证500
}


def get_akshare_index_code(secid: str) -> Optional[str]:
    """
    获取 akshare 格式的指数代码
    
    Args:
        secid: 原始指数代码（如 '0.000001'）
    
    Returns:
        akshare 格式的指数代码
    """
    return INDEX_CODE_MAP.get(secid)
