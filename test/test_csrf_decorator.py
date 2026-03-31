#!/usr/bin/env python3
"""测试 csrf_protected 装饰器是否支持同步和异步函数"""
import inspect
import asyncio
from functools import wraps

def csrf_protected(f):
    """CSRF保护装饰器（支持同步和异步函数）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f'Sync wrapper called for {f.__name__}')
        return f(*args, **kwargs)
    
    @wraps(f)
    async def async_decorated_function(*args, **kwargs):
        print(f'Async wrapper called for {f.__name__}')
        return await f(*args, **kwargs)
    
    # 根据被装饰函数是否为协程函数返回相应的装饰器
    if inspect.iscoroutinefunction(f):
        return async_decorated_function
    return decorated_function

# 测试同步函数
@csrf_protected
def sync_func():
    return 'sync result'

# 测试异步函数
@csrf_protected
async def async_func():
    return 'async result'

def main():
    print(f'sync_func is coroutine: {inspect.iscoroutinefunction(sync_func)}')
    print(f'async_func is coroutine: {inspect.iscoroutinefunction(async_func)}')
    print(f'sync_func name: {sync_func.__name__}')
    print(f'async_func name: {async_func.__name__}')
    
    # 测试同步函数
    result = sync_func()
    print(f'Sync result: {result}')
    
    # 测试异步函数
    async_result = asyncio.run(async_func())
    print(f'Async result: {async_result}')
    
    print('\nAll tests passed!')

if __name__ == '__main__':
    main()
