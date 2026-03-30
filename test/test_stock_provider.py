from services.stock_data_factory import StockDataFactory
from services.stock_service import StockService

# 测试eastmoney提供者
print("测试东方财富API提供者...")
try:
    eastmoney_provider = StockDataFactory.create_provider('eastmoney')
    print(f"东方财富API提供者创建成功: {eastmoney_provider.__class__.__name__}")
    
    # 测试获取股票实时行情
    quote = eastmoney_provider.get_stock_quote('600000')
    print(f"股票实时行情: {quote}")
    
    # 测试搜索股票
    search_result = eastmoney_provider.search_stocks('浦发银行')
    print(f"搜索股票结果: {search_result}")
    
except Exception as e:
    print(f"东方财富API测试失败: {e}")

# 测试akshare提供者
print("\n测试Akshare提供者...")
try:
    akshare_provider = StockDataFactory.create_provider('akshare')
    print(f"Akshare提供者创建成功: {akshare_provider.__class__.__name__}")
    
    # 测试获取股票实时行情
    quote = akshare_provider.get_stock_quote('600000')
    print(f"股票实时行情: {quote}")
    
    # 测试搜索股票
    search_result = akshare_provider.search_stocks('浦发银行')
    print(f"搜索股票结果: {search_result}")
    
    # 测试获取所有股票
    stocks = akshare_provider.get_all_stocks('m:0+t:6,m:0+t:80', 10)
    print(f"获取股票列表: {len(stocks)} 条")
    
    # 测试获取板块数据
    sectors = akshare_provider.get_sectors(10, 'concept')
    print(f"获取板块数据: {len(sectors)} 条")
    
except Exception as e:
    print(f"Akshare测试失败: {e}")

# 测试StockService使用不同的提供者
print("\n测试StockService...")
try:
    # 使用eastmoney
    eastmoney_service = StockService(provider_type='eastmoney')
    print(f"使用东方财富API的StockService创建成功")
    
    # 使用akshare
    akshare_service = StockService(provider_type='akshare')
    print(f"使用Akshare的StockService创建成功")
    
    # 测试搜索功能
    search_result = akshare_service.search_stocks('600000')
    print(f"StockService搜索结果: {search_result}")
    
    # 测试获取板块
    sectors = akshare_service.get_sectors()
    print(f"StockService获取板块: {len(sectors)} 条")
    
except Exception as e:
    print(f"StockService测试失败: {e}")

print("\n测试完成！")