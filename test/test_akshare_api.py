#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Akshare API调用
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.akshare_api import AkshareAPI, AKSHARE_AVAILABLE


def test_akshare_available():
    """测试akshare是否可用"""
    print("测试akshare是否可用...")
    print(f"AKSHARE_AVAILABLE: {AKSHARE_AVAILABLE}")
    if AKSHARE_AVAILABLE:
        print("✓ akshare已安装")
    else:
        print("✗ akshare未安装")
    return AKSHARE_AVAILABLE


def test_get_stock_quote():
    """测试获取股票实时行情"""
    print("\n测试获取股票实时行情...")
    api = AkshareAPI()
    # 测试获取贵州茅台的实时行情
    result = api.get_stock_quote('600519')
    if result:
        print(f"✓ 成功获取股票行情: {result['name']} ({result['code']})")
        print(f"  最新价: {result['price']}")
        print(f"  涨跌幅: {result['change_pct']}%")
        print(f"  涨跌额: {result['change']}")
    else:
        print("✗ 获取股票行情失败")
    return result is not None


def test_get_stock_detail():
    """测试获取股票详细信息"""
    print("\n测试获取股票详细信息...")
    api = AkshareAPI()
    # 测试获取贵州茅台的详细信息
    result = api.get_stock_detail('600519')
    if result:
        print(f"✓ 成功获取股票详细信息: {result['name']} ({result['code']})")
        print(f"  所属行业: {result['industry']}")
        print(f"  总股本: {result['total_share']}")
        print(f"  流通股本: {result['float_share']}")
    else:
        print("✗ 获取股票详细信息失败")
    return result is not None


def test_get_sectors():
    """测试获取板块数据"""
    print("\n测试获取板块数据...")
    api = AkshareAPI()
    # 测试获取概念板块
    result = api.get_sectors(sector_type='concept')
    if result and len(result) > 0:
        print(f"✓ 成功获取概念板块数据，共 {len(result)} 个板块")
        print("  前5个板块:")
        for i, sector in enumerate(result[:5]):
            print(f"  {i+1}. {sector['name']} ({sector['code']})")
    else:
        print("✗ 获取板块数据失败")
    return result is not None and len(result) > 0


def test_get_all_stocks():
    """测试获取所有股票"""
    print("\n测试获取所有股票...")
    api = AkshareAPI()
    # 测试获取深主板股票
    result = api.get_all_stocks('m:0+t:6', page_size=10)
    if result and len(result) > 0:
        print(f"✓ 成功获取股票数据，共 {len(result)} 只股票")
        print("  前5只股票:")
        for i, stock in enumerate(result[:5]):
            print(f"  {i+1}. {stock['name']} ({stock['code']}) - {stock['price']}元")
    else:
        print("✗ 获取股票数据失败")
    return result is not None and len(result) > 0


def test_search_stocks():
    """测试搜索股票"""
    print("\n测试搜索股票...")
    api = AkshareAPI()
    # 测试搜索包含"茅台"的股票
    result = api.search_stocks('茅台')
    if result and len(result) > 0:
        print(f"✓ 成功搜索到 {len(result)} 只股票")
        for stock in result:
            print(f"  - {stock['name']} ({stock['code']})")
    else:
        print("✗ 搜索股票失败")
    return result is not None


def test_get_index_data():
    """测试获取指数数据"""
    print("\n测试获取指数数据...")
    api = AkshareAPI()
    # 测试获取上证指数
    result = api.get_index_data('1.000001')
    if result:
        print(f"✓ 成功获取指数数据: {result['name']} ({result['code']})")
        print(f"  最新价: {result['price']}")
        print(f"  涨跌幅: {result['change_pct']}%")
        print(f"  涨跌额: {result['change']}")
    else:
        print("✗ 获取指数数据失败")
    return result is not None


def test_get_stock_history():
    """测试获取股票历史数据"""
    print("\n测试获取股票历史数据...")
    api = AkshareAPI()
    # 测试获取贵州茅台最近7天的历史数据
    import datetime
    end_date = datetime.datetime.now().strftime('%Y%m%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y%m%d')
    result = api.get_stock_history('600519', start_date, end_date)
    if result and len(result) > 0:
        print(f"✓ 成功获取股票历史数据，共 {len(result)} 条记录")
        print("  最近5天数据:")
        for i, record in enumerate(result[-5:]):
            print(f"  {record['date']}: {record['close']}元")
    else:
        print("✗ 获取股票历史数据失败")
    return result is not None and len(result) > 0


def test_get_sector_stocks():
    """测试获取板块成分股"""
    print("\n测试获取板块成分股...")
    api = AkshareAPI()
    # 测试获取芯片概念板块的成分股
    # 先获取概念板块列表，找到芯片概念的代码
    sectors = api.get_sectors(sector_type='concept')
    if sectors:
        chip_sector = None
        for sector in sectors:
            if '芯片' in sector['name']:
                chip_sector = sector
                break
        
        if chip_sector:
            result = api.get_sector_stocks(chip_sector['code'], page_size=10)
            if result and len(result) > 0:
                print(f"✓ 成功获取{chip_sector['name']}板块成分股，共 {len(result)} 只股票")
                print("  前5只股票:")
                for i, stock in enumerate(result[:5]):
                    print(f"  {i+1}. {stock['name']} ({stock['code']})")
                return True
            else:
                print("✗ 获取板块成分股失败")
        else:
            print("✗ 未找到芯片概念板块")
    else:
        print("✗ 获取板块列表失败")
    return False


def run_all_tests():
    """运行所有测试"""
    print("开始测试Akshare API...")
    print("=" * 60)
    
    # 首先测试akshare是否可用
    if not test_akshare_available():
        print("\n✗ akshare未安装，无法进行其他测试")
        return
    
    # 运行其他测试
    tests = [
        test_get_stock_quote,
        test_get_stock_detail,
        test_get_sectors,
        test_get_all_stocks,
        test_search_stocks,
        test_get_index_data,
        test_get_stock_history,
        test_get_sector_stocks
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    if passed == total:
        print("✓ 所有测试通过！")
    else:
        print("✗ 部分测试失败，请检查akshare安装和网络连接")


if __name__ == '__main__':
    run_all_tests()
