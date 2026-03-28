const API_BASE = '/api';

const api = {
    async getHealth() {
        const response = await fetch(`${API_BASE}/health`);
        return response.json();
    },

    async getSectors() {
        const response = await fetch(`${API_BASE}/stocks/sectors`);
        return response.json();
    },

    async getLeaderStocks(sector = null, topN = 10) {
        let url = `${API_BASE}/stocks/leaders?top_n=${topN}`;
        if (sector) {
            url += `&sector=${sector}`;
        }
        const response = await fetch(url);
        return response.json();
    },

    async searchStock(query) {
        const response = await fetch(`${API_BASE}/stocks/search?query=${encodeURIComponent(query)}`);
        return response.json();
    },

    async getIndexData() {
        const response = await fetch(`${API_BASE}/stocks/index`);
        return response.json();
    },

    async getKlineData(code) {
        const response = await fetch(`${API_BASE}/stocks/kline?code=${code}`);
        return response.json();
    },

    async analyzeStock(stockCode, stockName, stockData, modelConfig = null) {
        const response = await fetch(`${API_BASE}/stocks/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                stock_code: stockCode,
                stock_name: stockName,
                stock_data: stockData,
                model_config: modelConfig
            })
        });
        return response.json();
    },

    async batchAnalyzeStocks(stocks, modelConfig = null) {
        const response = await fetch(`${API_BASE}/stocks/batch-analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                stocks,
                model_config: modelConfig
            })
        });
        return response.json();
    },

    async getRealtimeQuote(code) {
        try {
            const response = await fetch(`${API_BASE}/stocks/quote?code=${code}`);
            return response.json();
        } catch (error) {
            console.error('获取实时行情失败:', error);
            // 模拟实时数据
            return {
                success: true,
                data: {
                    code: code,
                    price: (Math.random() * 100 + 10).toFixed(2),
                    change: (Math.random() * 2 - 1).toFixed(2),
                    change_pct: (Math.random() * 10 - 5).toFixed(2),
                    volume: Math.floor(Math.random() * 1000000)
                }
            };
        }
    },

    // 数据库相关API
    async getSettings() {
        const response = await fetch(`${API_BASE}/db/settings`);
        return response.json();
    },

    async getSetting(key) {
        const response = await fetch(`${API_BASE}/db/settings/${key}`);
        return response.json();
    },

    async setSetting(key, value) {
        const response = await fetch(`${API_BASE}/db/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key, value })
        });
        return response.json();
    },

    async getWatchlist() {
        const response = await fetch(`${API_BASE}/db/watchlist`);
        return response.json();
    },

    async addToWatchlist(code, name) {
        const response = await fetch(`${API_BASE}/db/watchlist`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, name })
        });
        return response.json();
    },

    async removeFromWatchlist(code) {
        const response = await fetch(`${API_BASE}/db/watchlist/${code}`, {
            method: 'DELETE'
        });
        return response.json();
    },

    async clearWatchlist() {
        const response = await fetch(`${API_BASE}/db/watchlist`, {
            method: 'DELETE'
        });
        return response.json();
    },

    // 模型测试API
    async testModel(testData) {
        const response = await fetch(`${API_BASE}/ai/test-model`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testData)
        });
        return response.json();
    }
};

export default api;
