#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试akshare板块数据获取功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.akshare_api import AkshareAPI, AKSHARE_AVAILABLE


def test_akshare_sectors():
    """测试akshare板块数据获取"""
    print("测试akshare板块数据获取功能...")
    
    if not AKSHARE_AVAILABLE:
        print("✗ akshare未安装，无法测试")
        return False
    
    api = AkshareAPI()
    
    # 测试获取概念板块
    print("\n测试获取概念板块:")
    try:
        concept_sectors = api.get_sectors(sector_type='concept')
        if concept_sectors and len(concept_sectors) > 0:
            print(f"✓ 成功获取概念板块，共 {len(concept_sectors)} 个")
            print("前10个概念板块:")
            for i, sector in enumerate(concept_sectors[:10]):
                print(f"  {i+1}. {sector['name']} ({sector['code']})")
        else:
            print("✗ 获取概念板块失败，返回空数据")
    except Exception as e:
        print(f"✗ 获取概念板块异常: {e}")
    
    # 测试获取行业板块
    print("\n测试获取行业板块:")
    try:
        industry_sectors = api.get_sectors(sector_type='industry')
        if industry_sectors and len(industry_sectors) > 0:
            print(f"✓ 成功获取行业板块，共 {len(industry_sectors)} 个")
            print("前10个行业板块:")
            for i, sector in enumerate(industry_sectors[:10]):
                print(f"  {i+1}. {sector['name']} ({sector['code']})")
        else:
            print("✗ 获取行业板块失败，返回空数据")
    except Exception as e:
        print(f"✗ 获取行业板块异常: {e}")
    
    # 测试获取地域板块
    print("\n测试获取地域板块:")
    try:
        area_sectors = api.get_sectors(sector_type='area')
        if area_sectors and len(area_sectors) > 0:
            print(f"✓ 成功获取地域板块，共 {len(area_sectors)} 个")
            print("前10个地域板块:")
            for i, sector in enumerate(area_sectors[:10]):
                print(f"  {i+1}. {sector['name']} ({sector['code']})")
        else:
            print("✗ 获取地域板块失败，返回空数据")
    except Exception as e:
        print(f"✗ 获取地域板块异常: {e}")


if __name__ == '__main__':
    test_akshare_sectors()
