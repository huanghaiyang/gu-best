from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from services.stock_service import StockService
from services.ai_service import AIService
from services.database_service import DatabaseService
from config import stock_filter_config

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

stock_service = StockService()
ai_service = AIService()
db_service = DatabaseService()

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('frontend/css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('frontend/js', filename)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': '服务运行正常'})

@app.route('/api/stocks/sectors', methods=['GET'])
def get_sectors():
    try:
        sectors = stock_service.get_hot_sectors()
        return jsonify({'success': True, 'data': sectors})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/search', methods=['GET'])
def search_stocks():
    try:
        query = request.args.get('query', '').strip()
        if not query:
            return jsonify({'success': False, 'error': '查询参数不能为空'}), 400
        
        stocks = stock_service.search_stocks(query)
        return jsonify({'success': True, 'data': stocks})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/index', methods=['GET'])
def get_index_data():
    try:
        index_data = stock_service.get_index_data()
        return jsonify({'success': True, 'data': index_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/kline', methods=['GET'])
def get_kline_data():
    try:
        code = request.args.get('code', '').strip()
        if not code:
            return jsonify({'success': False, 'error': '股票代码不能为空'}), 400
        
        kline_data = stock_service.get_kline_data(code)
        return jsonify({'success': True, 'data': kline_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/leaders', methods=['GET'])
def get_leader_stocks():
    try:
        sector = request.args.get('sector', None)
        top_n = int(request.args.get('top_n', stock_filter_config['top_n_stocks']))
        
        leaders = stock_service.screen_leader_stocks(sector=sector, top_n=top_n)
        return jsonify({'success': True, 'data': leaders})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stocks/analyze', methods=['POST'])
def analyze_stock():
    try:
        data = request.get_json()
        stock_code = data.get('stock_code')
        stock_name = data.get('stock_name')
        stock_data = data.get('stock_data', {})
        
        if not stock_code:
            return jsonify({'success': False, 'error': '缺少股票代码'}), 400
        
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
def batch_analyze_stocks():
    try:
        data = request.get_json()
        stocks = data.get('stocks', [])
        
        if not stocks:
            return jsonify({'success': False, 'error': '缺少股票数据'}), 400
        
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
def get_stock_quote():
    try:
        code = request.args.get('code', '').strip()
        if not code:
            return jsonify({'success': False, 'error': '股票代码不能为空'}), 400
        
        quote = stock_service.get_quote(code)
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

@app.route('/api/db/settings/<key>', methods=['GET'])
def get_setting(key):
    try:
        value = db_service.get_setting(key)
        return jsonify({'success': True, 'data': value})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/db/settings', methods=['POST'])
def set_setting():
    try:
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
        
        if not key:
            return jsonify({'success': False, 'error': '缺少key参数'}), 400
        
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
def remove_from_watchlist(code):
    try:
        success = db_service.remove_from_watchlist(code)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/db/watchlist', methods=['DELETE'])
def clear_watchlist():
    try:
        success = db_service.clear_watchlist()
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 模型测试API
@app.route('/api/ai/test-model', methods=['POST'])
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
def add_ai_setting():
    try:
        data = request.get_json()
        model_id = data.get('modelId')
        model_name = data.get('modelName')
        api_url = data.get('apiUrl')
        api_key = data.get('apiKey')
        secret_key = data.get('secretKey')
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('maxTokens', 2048)
        is_active = data.get('isActive', 0)
        
        if not model_id or not model_name or not api_url:
            return jsonify({'success': False, 'error': '缺少必要的参数'}), 400
        
        success = db_service.add_ai_setting(
            model_id, model_name, api_url, api_key, 
            secret_key, temperature, max_tokens, is_active
        )
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/settings/<model_id>', methods=['PUT'])
def update_ai_setting(model_id):
    try:
        data = request.get_json()
        
        success = db_service.update_ai_setting(
            model_id=model_id,
            model_name=data.get('modelName'),
            api_url=data.get('apiUrl'),
            api_key=data.get('apiKey'),
            secret_key=data.get('secretKey'),
            temperature=data.get('temperature'),
            max_tokens=data.get('maxTokens'),
            is_active=data.get('isActive')
        )
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/settings/active/<model_id>', methods=['PUT'])
def set_active_ai_model(model_id):
    try:
        success = db_service.set_active_ai_model(model_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/settings/<model_id>', methods=['DELETE'])
def delete_ai_setting(model_id):
    try:
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
