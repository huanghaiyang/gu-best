#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖检查模块
用于检查服务启动所需的依赖项
"""

import sys
import os
from typing import Dict, List, Tuple


def check_python_version() -> Tuple[bool, str]:
    """检查Python版本"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        return True, f"Python {version.major}.{version.minor}.{version.micro} ✓"
    else:
        return False, f"Python {version.major}.{version.minor}.{version.micro} ✗ (需要Python 3.7+"


def check_akshare() -> Tuple[bool, str]:
    """检查akshare模块"""
    try:
        import akshare as ak
        return True, f"akshare {ak.__version__} ✓"
    except ImportError:
        return False, "akshare 未安装 ✗"
    except Exception as e:
        return False, f"akshare 安装异常: {e} ✗"


def check_eastmoney_keys() -> Tuple[bool, str]:
    """检查东方财富API密钥文件"""
    if os.path.exists('eastmoney_keys.py'):
        try:
            from eastmoney_keys import BASE_URL, UT_TOKEN_STOCK, UT_TOKEN_LIST, SEARCH_TOKEN
            return True, "东方财富API密钥文件 ✓"
        except Exception as e:
            return False, f"东方财富API密钥文件异常: {e} ✗"
    else:
        return False, "东方财富API密钥文件不存在 ✗"


def check_database() -> Tuple[bool, str]:
    """检查数据库"""
    try:
        import sqlite3
        from services.database_service import DatabaseService
        db_service = DatabaseService()
        # 测试数据库连接
        settings = db_service.get_all_settings()
        return True, "数据库连接正常 ✓"
    except Exception as e:
        return False, f"数据库连接异常: {e} ✗"


def check_flask() -> Tuple[bool, str]:
    """检查Flask"""
    try:
        import flask
        return True, f"Flask {flask.__version__} ✓"
    except ImportError:
        return False, "Flask 未安装 ✗"


def check_required_packages() -> List[Tuple[bool, str]]:
    """检查所有必要的Python包"""
    packages = [
        ('requests', 'requests'),
        ('pandas', 'pandas'),
        ('flask_cors', 'Flask-CORS'),
    ]
    
    results = []
    for import_name, package_name in packages:
        try:
            __import__(import_name)
            results.append((True, f"{package_name} ✓"))
        except ImportError:
            results.append((False, f"{package_name} 未安装 ✗"))
    
    return results


def run_all_checks() -> Dict[str, List[Tuple[bool, str]]]:
    """运行所有依赖检查"""
    checks = {
        '系统环境': [
            check_python_version(),
        ],
        '核心依赖': [
            check_flask(),
        ],
        '数据源': [
            check_akshare(),
            check_eastmoney_keys(),
        ],
        '数据库': [
            check_database(),
        ],
        '其他依赖': check_required_packages(),
    }
    
    return checks


def print_check_results(checks: Dict[str, List[Tuple[bool, str]]]):
    """打印检查结果"""
    print("=" * 60)
    print("服务启动依赖检查")
    print("=" * 60)
    
    all_passed = True
    
    for category, items in checks.items():
        print(f"\n{category}:")
        print("-" * 40)
        
        for passed, message in items:
            print(f"  {message}")
            if not passed:
                all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("所有依赖检查通过 ✓")
    else:
        print("部分依赖检查失败 ✗")
    print("=" * 60)
    
    return all_passed


if __name__ == '__main__':
    checks = run_all_checks()
    print_check_results(checks)
