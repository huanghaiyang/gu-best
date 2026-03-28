from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from services.stock_service import StockService
from services.ai_service import AIService
from config import Config
import os

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

stock_service = StockService()
ai_service = AIService()

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
        top_n = int(request.args.get('top_n', Config.STOCK_FILTER_CONFIG['top_n_stocks']))
        
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
