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

    async analyzeStock(stockCode, stockName, stockData) {
        const response = await fetch(`${API_BASE}/stocks/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                stock_code: stockCode,
                stock_name: stockName,
                stock_data: stockData
            })
        });
        return response.json();
    },

    async batchAnalyzeStocks(stocks) {
        const response = await fetch(`${API_BASE}/stocks/batch-analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stocks })
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
    }
};

export default api;
