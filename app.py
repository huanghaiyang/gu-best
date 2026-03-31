import inspect
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from services.stock_service import StockService
from services.ai_service import AIService
from services.database_service import DatabaseService
from services.csrf_service import csrf_service
from services.security_service import security_service
from services.dependency_checker import run_all_checks, print_check_results
from config import stock_filter_config

app = Flask(__name__, static_folder='frontend', static_url_path='')

# 运行依赖检查
print("\n正在进行服务启动依赖检查...")
checks = run_all_checks()
print_check_results(checks)

# 配置会话密钥
app.secret_key = 'stock_analysis_session_secret_2024'

# 配置CORS策略
CORS(app, 
     resources={
         r"/api/*": {
             "origins": ["http://localhost:8000", "http://127.0.0.1:8000"],  # 允许的源
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 允许的HTTP方法
             "allow_headers": ["Content-Type", "X-CSRF-Token", "Authorization"],  # 允许的请求头
             "supports_credentials": True,  # 支持凭证
             "max_age": 86400  # 预检请求的缓存时间（秒）
         }
     }
)

db_service = DatabaseService()
ai_service = AIService()

# 从数据库获取默认数据源，默认使用eastmoney避免akshare的mini_racer问题
default_data_source = db_service.get_setting('dataSource') or 'eastmoney'

# 尝试创建StockService，如果失败则使用备用数据源
try:
    stock_service = StockService(provider_type=default_data_source)
except Exception as e:
    print(f"创建StockService失败: {e}")
    print("尝试使用备用数据源")
    try:
        stock_service = StockService(provider_type='eastmoney')
    except Exception as e2:
        print(f"备用数据源也失败: {e2}")
        raise

def csrf_protected(f):
    """CSRF保护装饰器（支持同步和异步函数）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # GET请求不需要CSRF保护
        if request.method == 'GET':
            return f(*args, **kwargs)
        
        # 从请求头获取CSRF令牌
        token = request.headers.get('X-CSRF-Token')
        if not token:
            # 从请求体获取CSRF令牌
            data = request.get_json(silent=True) or {}
            token = data.get('csrf_token')
        
        # 使用会话ID作为用户标识符
        session_id = request.cookies.get('session_id', 'anonymous')
        if not token or not csrf_service.validate_token(token, session_id):
            return jsonify({'success': False, 'error': 'CSRF令牌无效或已过期'}), 403
        
        return f(*args, **kwargs)
    
    @wraps(f)
    async def async_decorated_function(*args, **kwargs):
        # GET请求不需要CSRF保护
        if request.method == 'GET':
            return await f(*args, **kwargs)
        
        # 从请求头获取CSRF令牌
        token = request.headers.get('X-CSRF-Token')
        if not token:
            # 从请求体获取CSRF令牌
            data = request.get_json(silent=True) or {}
            token = data.get('csrf_token')
        
        # 使用会话ID作为用户标识符
        session_id = request.cookies.get('session_id', 'anonymous')
        if not token or not csrf_service.validate_token(token, session_id):
            return jsonify({'success': False, 'error': 'CSRF令牌无效或已过期'}), 403
        
        return await f(*args, **kwargs)
    
    # 根据被装饰函数是否为协程函数返回相应的装饰器
    if inspect.iscoroutinefunction(f):
        return async_decorated_function
    return decorated_function

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('frontend/css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('frontend/js', filename)

@app.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    """获取CSRF令牌"""
    # 使用会话ID作为用户标识符
    session_id = request.cookies.get('session_id', 'anonymous')
    token = csrf_service.generate_token(session_id)
    return jsonify({'success': True, 'token': token})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': '服务运行正常'})

@app.route('/api/stocks/sectors', methods=['GET'])
async def get_sectors():
    try:
        sectors = await stock_service.get_sectors()
        return jsonify({'success': True, 'data': sectors})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/search', methods=['GET'])
async def search_stocks():
    try:
        query = request.args.get('query', '').strip()
        
        # 验证搜索查询
        if not security_service.validate_search_query(query):
            return jsonify({'success': False, 'error': '查询参数不能为空，长度1-50'}), 400
        
        # 清理输入
        sanitized_query = security_service.sanitize_input(query)
        
        stocks = await stock_service.search_stocks(sanitized_query)
        return jsonify({'success': True, 'data': stocks})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/index', methods=['GET'])
async def get_index_data():
    try:
        index_data = await stock_service.get_index_data()
        return jsonify({'success': True, 'data': index_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/kline', methods=['GET'])
async def get_kline_data():
    try:
        code = request.args.get('code', '').strip()
        
        # 验证股票代码
        if not security_service.validate_stock_code(code):
            return jsonify({'success': False, 'error': '股票代码格式不正确，仅允许字母和数字，长度4-10'}), 400
        
        # 清理输入
        sanitized_code = security_service.sanitize_input(code)
        
        kline_data = await stock_service.get_kline_data(sanitized_code)
        return jsonify({'success': True, 'data': kline_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/leaders', methods=['GET'])
async def get_leader_stocks():
    try:
        sector = request.args.get('sector', None)
        top_n = request.args.get('top_n', stock_filter_config['top_n_stocks'])
        
        # 验证top_n
        if not security_service.validate_positive_integer(top_n):
            return jsonify({'success': False, 'error': 'top_n必须是正整数'}), 400
        
        # 转换为整数
        top_n = int(top_n)
        
        # 清理输入
        if sector:
            sector = security_service.sanitize_input(sector)
        
        leaders = await stock_service.screen_leader_stocks(sector=sector, top_n=top_n)
        return jsonify({'success': True, 'data': leaders})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/analyze', methods=['POST'])
@csrf_protected
def analyze_stock():
    try:
        data = request.get_json()
        
        # 验证请求数据
        error = security_service.validate_request_data(data, ['stock_code'])
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        # 清理数据
        sanitized_data = security_service.sanitize_object(data)
        stock_code = sanitized_data.get('stock_code')
        stock_name = sanitized_data.get('stock_name')
        stock_data = sanitized_data.get('stock_data', {})
        
        # 验证股票代码
        if not security_service.validate_stock_code(stock_code):
            return jsonify({'success': False, 'error': '股票代码格式不正确'}), 400
        
        # 从数据库获取当前激活的AI模型配置
        active_setting = db_service.get_active_ai_setting()
        if active_setting:
            ai_service.set_model_config(
                active_setting['modelId'],
                {
                    'apiUrl': active_setting['apiUrl'],
                    'apiKey': active_setting['apiKey'],
                    'model': active_setting['modelName']
                },
                {
                    'temperature': active_setting['temperature'],
                    'maxTokens': active_setting['maxTokens']
                }
            )
        
        analysis = ai_service.analyze_stock(stock_code, stock_name, stock_data)
        return jsonify({'success': True, 'data': analysis})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/batch-analyze', methods=['POST'])
@csrf_protected
def batch_analyze_stocks():
    try:
        data = request.get_json()
        
        # 验证请求数据
        error = security_service.validate_request_data(data, ['stocks'])
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        # 清理数据
        sanitized_data = security_service.sanitize_object(data)
        stocks = sanitized_data.get('stocks', [])
        
        # 验证股票列表
        if not isinstance(stocks, list) or len(stocks) == 0:
            return jsonify({'success': False, 'error': '股票列表不能为空'}), 400
        
        if len(stocks) > 50:
            return jsonify({'success': False, 'error': '股票数量不能超过50个'}), 400
        
        # 验证每个股票
        for stock in stocks:
            stock_error = security_service.validate_stock_data(stock)
            if stock_error:
                return jsonify({'success': False, 'error': stock_error}), 400
        
        # 从数据库获取当前激活的AI模型配置
        active_setting = db_service.get_active_ai_setting()
        if active_setting:
            ai_service.set_model_config(
                active_setting['modelId'],
                {
                    'apiUrl': active_setting['apiUrl'],
                    'apiKey': active_setting['apiKey'],
                    'model': active_setting['modelName']
                },
                {
                    'temperature': active_setting['temperature'],
                    'maxTokens': active_setting['maxTokens']
                }
            )
        
        results = ai_service.batch_analyze_stocks(stocks)
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/quote', methods=['GET'])
async def get_stock_quote():
    try:
        code = request.args.get('code', '').strip()
        
        # 验证股票代码
        if not security_service.validate_stock_code(code):
            return jsonify({'success': False, 'error': '股票代码格式不正确，仅允许字母和数字，长度4-10'}), 400
        
        # 清理输入
        sanitized_code = security_service.sanitize_input(code)
        
        quote = await stock_service.get_quote(sanitized_code)
        return jsonify({'success': True, 'data': quote})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 数据库相关API
@app.route('/api/db/settings', methods=['GET'])
def get_settings():
    try:
        settings = db_service.get_all_settings()
        return jsonify({'success': True, 'data': settings})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/db/settings/data-source', methods=['POST'])
@csrf_protected
async def set_data_source():
    try:
        data = request.get_json()
        if not data or 'dataSource' not in data:
            return jsonify({'success': False, 'error': '缺少数据源参数'}), 400
        
        data_source = data['dataSource']
        # 验证数据源类型是否有效
        valid_sources = ['akshare', 'eastmoney']
        if data_source not in valid_sources:
            return jsonify({'success': False, 'error': '无效的数据源类型'}), 400
        
        # 更新数据库中的数据源设置
        db_service.set_setting('dataSource', data_source)
        
        # 切换StockService的数据源
        await stock_service.set_provider(data_source)
        
        return jsonify({'success': True, 'data': {'dataSource': data_source}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/db/settings/<key>', methods=['GET'])
def get_setting(key):
    try:
        value = db_service.get_setting(key)
        return jsonify({'success': True, 'data': value})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/db/settings', methods=['POST'])
@csrf_protected
def set_setting():
    try:
        data = request.get_json()
        
        # 验证请求数据
        error = security_service.validate_request_data(data, ['key'])
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        # 清理数据
        sanitized_data = security_service.sanitize_object(data)
        key = sanitized_data.get('key')
        value = sanitized_data.get('value')
        
        # 验证key长度
        if not security_service.validate_length(key, 1, 50):
            return jsonify({'success': False, 'error': 'key长度必须在1-50之间'}), 400
        
        # 验证value长度（如果有）
        if value and isinstance(value, str) and not security_service.validate_length(value, 0, 1000):
            return jsonify({'success': False, 'error': 'value长度不能超过1000'}), 400
        
        success = db_service.set_setting(key, value)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/db/watchlist', methods=['GET'])
def get_watchlist():
    try:
        watchlist = db_service.get_watchlist()
        return jsonify({'success': True, 'data': watchlist})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/db/watchlist', methods=['POST'])
@csrf_protected
def add_to_watchlist():
    try:
        data = request.get_json()
        code = data.get('code')
        name = data.get('name')
        
        if not code or not name:
            return jsonify({'success': False, 'error': '缺少code或name参数'}), 400
        
        success = db_service.add_to_watchlist(code, name)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/db/watchlist/<code>', methods=['DELETE'])
@csrf_protected
def remove_from_watchlist(code):
    try:
        success = db_service.remove_from_watchlist(code)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/db/watchlist', methods=['DELETE'])
@csrf_protected
def clear_watchlist():
    try:
        success = db_service.clear_watchlist()
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 模型测试API
@app.route('/api/ai/test-model', methods=['POST'])
@csrf_protected
def test_model():
    try:
        data = request.get_json()
        model = data.get('model')
        params = data.get('params', {})
        api_config = data.get('apiConfig', {})
        
        if not model or not api_config.get('apiUrl') or not api_config.get('apiKey') or not api_config.get('model'):
            return jsonify({'success': False, 'error': '缺少必要的模型配置参数'}), 400
        
        # 测试模型连接
        result = ai_service.test_model(model, params, api_config)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# AI设置相关API
@app.route('/api/ai/settings', methods=['GET'])
def get_ai_settings():
    try:
        ai_settings = db_service.get_all_ai_settings()
        return jsonify({'success': True, 'data': ai_settings})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/settings/<model_id>', methods=['GET'])
def get_ai_setting(model_id):
    try:
        ai_setting = db_service.get_ai_setting(model_id)
        if ai_setting:
            return jsonify({'success': True, 'data': ai_setting})
        else:
            return jsonify({'success': False, 'error': '未找到指定的AI模型配置'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/settings/active', methods=['GET'])
def get_active_ai_setting():
    try:
        ai_setting = db_service.get_active_ai_setting()
        if ai_setting:
            return jsonify({'success': True, 'data': ai_setting})
        else:
            return jsonify({'success': False, 'error': '未找到激活的AI模型配置'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/settings', methods=['POST'])
@csrf_protected
def add_ai_setting():
    try:
        data = request.get_json()
        
        # 验证请求数据
        error = security_service.validate_request_data(data, ['modelId', 'modelName', 'apiUrl'])
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        # 清理数据
        sanitized_data = security_service.sanitize_object(data)
        model_id = sanitized_data.get('modelId')
        model_name = sanitized_data.get('modelName')
        api_url = sanitized_data.get('apiUrl')
        api_key = sanitized_data.get('apiKey')
        secret_key = sanitized_data.get('secretKey')
        temperature = sanitized_data.get('temperature', 0.7)
        max_tokens = sanitized_data.get('maxTokens', 2048)
        is_active = sanitized_data.get('isActive', 0)
        
        # 验证模型ID
        if not security_service.validate_model_id(model_id):
            return jsonify({'success': False, 'error': '模型ID格式不正确，仅允许字母、数字和下划线，长度3-30'}), 400
        
        # 验证模型名称
        if not security_service.validate_model_name(model_name):
            return jsonify({'success': False, 'error': '模型名称不能为空，长度1-50'}), 400
        
        # 验证API URL
        if not security_service.validate_url(api_url):
            return jsonify({'success': False, 'error': 'API URL格式不正确'}), 400
        
        # 验证API Key（可选）
        if api_key and not security_service.validate_api_key(api_key):
            return jsonify({'success': False, 'error': 'API Key格式不正确'}), 400
        
        # 验证温度值
        if not security_service.validate_temperature(temperature):
            return jsonify({'success': False, 'error': '温度值必须在0-1之间'}), 400
        
        # 验证最大tokens
        if not security_service.validate_max_tokens(max_tokens):
            return jsonify({'success': False, 'error': '最大tokens必须是正整数，不超过100000'}), 400
        
        success = db_service.add_ai_setting(
            model_id, model_name, api_url, api_key, 
            secret_key, temperature, max_tokens, is_active
        )
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/settings/<model_id>', methods=['PUT'])
@csrf_protected
def update_ai_setting(model_id):
    try:
        data = request.get_json()
        
        # 验证模型ID
        if not security_service.validate_model_id(model_id):
            return jsonify({'success': False, 'error': '模型ID格式不正确'}), 400
        
        # 清理数据
        sanitized_data = security_service.sanitize_object(data)
        
        # 验证模型名称（如果提供）
        if 'modelName' in sanitized_data and sanitized_data['modelName']:
            if not security_service.validate_model_name(sanitized_data['modelName']):
                return jsonify({'success': False, 'error': '模型名称格式不正确'}), 400
        
        # 验证API URL（如果提供）
        if 'apiUrl' in sanitized_data and sanitized_data['apiUrl']:
            if not security_service.validate_url(sanitized_data['apiUrl']):
                return jsonify({'success': False, 'error': 'API URL格式不正确'}), 400
        
        # 验证API Key（如果提供）
        if 'apiKey' in sanitized_data and sanitized_data['apiKey']:
            if not security_service.validate_api_key(sanitized_data['apiKey']):
                return jsonify({'success': False, 'error': 'API Key格式不正确'}), 400
        
        # 验证温度值（如果提供）
        if 'temperature' in sanitized_data:
            if not security_service.validate_temperature(sanitized_data['temperature']):
                return jsonify({'success': False, 'error': '温度值必须在0-1之间'}), 400
        
        # 验证最大tokens（如果提供）
        if 'maxTokens' in sanitized_data:
            if not security_service.validate_max_tokens(sanitized_data['maxTokens']):
                return jsonify({'success': False, 'error': '最大tokens必须是正整数，不超过100000'}), 400
        
        success = db_service.update_ai_setting(
            model_id=model_id,
            model_name=sanitized_data.get('modelName'),
            api_url=sanitized_data.get('apiUrl'),
            api_key=sanitized_data.get('apiKey'),
            secret_key=sanitized_data.get('secretKey'),
            temperature=sanitized_data.get('temperature'),
            max_tokens=sanitized_data.get('maxTokens'),
            is_active=sanitized_data.get('isActive')
        )
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/settings/active/<model_id>', methods=['PUT'])
@csrf_protected
def set_active_ai_model(model_id):
    try:
        # 验证模型ID
        if not security_service.validate_model_id(model_id):
            return jsonify({'success': False, 'error': '模型ID格式不正确'}), 400
        
        success = db_service.set_active_ai_model(model_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/settings/<model_id>', methods=['DELETE'])
@csrf_protected
def delete_ai_setting(model_id):
    try:
        # 验证模型ID
        if not security_service.validate_model_id(model_id):
            return jsonify({'success': False, 'error': '模型ID格式不正确'}), 400
        
        success = db_service.delete_ai_setting(model_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 获取AI模型列表
@app.route('/api/ai/models', methods=['GET'])
def get_ai_models():
    try:
        # 从数据库中读取所有AI模型配置
        db_settings = db_service.get_all_ai_settings()
        
        # 转换为前端需要的格式
        models = []
        for setting in db_settings:
            model = {
                'id': setting['modelId'],
                'name': setting['modelName'],
                'apiUrl': setting['apiUrl'],
                'apiKey': setting['apiKey'],
                'secretKey': setting['secretKey'],
                'model': setting['modelName'],  # 前端需要的字段
                'temperature': setting['temperature'],
                'maxTokens': setting['maxTokens'],
                'isActive': setting['isActive']
            }
            models.append(model)
        
        return jsonify({'success': True, 'data': models})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
