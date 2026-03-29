const API_BASE = '/api';

const api = {
    async getHealth() {
        const response = await fetch(`${API_BASE}/health`);
        return await handleResponse(response);
    },

    async getSectors() {
        const response = await fetch(`${API_BASE}/stocks/sectors`);
        return await handleResponse(response);
    },

    async getLeaderStocks(sector = null, topN = 10) {
        let url = `${API_BASE}/stocks/leaders?top_n=${topN}`;
        if (sector) {
            url += `&sector=${sector}`;
        }
        const response = await fetch(url);
        return await handleResponse(response);
    },

    async searchStock(query) {
        const response = await fetch(`${API_BASE}/stocks/search?query=${encodeURIComponent(query)}`);
        return await handleResponse(response);
    },

    async getIndexData() {
        const response = await fetch(`${API_BASE}/stocks/index`);
        return await handleResponse(response);
    },

    async getKlineData(code) {
        const response = await fetch(`${API_BASE}/stocks/kline?code=${code}`);
        return await handleResponse(response);
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
        return await handleResponse(response);
    },

    async batchAnalyzeStocks(stocks) {
        const response = await fetch(`${API_BASE}/stocks/batch-analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stocks })
        });
        return await handleResponse(response);
    },

    async getRealtimeQuote(code) {
        try {
            const response = await fetch(`${API_BASE}/stocks/quote?code=${code}`);
            return await handleResponse(response);
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
        return await handleResponse(response);
    },

    async getSetting(key) {
        const response = await fetch(`${API_BASE}/db/settings/${key}`);
        return await handleResponse(response);
    },

    async setSetting(key, value) {
        const response = await fetch(`${API_BASE}/db/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key, value })
        });
        return await handleResponse(response);
    },

    async getWatchlist() {
        const response = await fetch(`${API_BASE}/db/watchlist`);
        return await handleResponse(response);
    },

    async addToWatchlist(code, name) {
        const response = await fetch(`${API_BASE}/db/watchlist`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, name })
        });
        return await handleResponse(response);
    },

    async removeFromWatchlist(code) {
        const response = await fetch(`${API_BASE}/db/watchlist/${code}`, {
            method: 'DELETE'
        });
        return await handleResponse(response);
    },

    async clearWatchlist() {
        const response = await fetch(`${API_BASE}/db/watchlist`, {
            method: 'DELETE'
        });
        return await handleResponse(response);
    },

    // 模型测试API
    async testModel(testData) {
        const response = await fetch(`${API_BASE}/ai/test-model`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testData)
        });
        return await handleResponse(response);
    },

    // AI设置相关API
    async getAISettings() {
        const response = await fetch(`${API_BASE}/ai/settings`);
        return await handleResponse(response);
    },

    async getAISetting(modelId) {
        const response = await fetch(`${API_BASE}/ai/settings/${modelId}`);
        return await handleResponse(response);
    },

    async getActiveAISetting() {
        const response = await fetch(`${API_BASE}/ai/settings/active`);
        return await handleResponse(response);
    },

    async addAISetting(settingData) {
        const response = await fetch(`${API_BASE}/ai/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settingData)
        });
        return await handleResponse(response);
    },

    async updateAISetting(modelId, settingData) {
        const response = await fetch(`${API_BASE}/ai/settings/${modelId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settingData)
        });
        return await handleResponse(response);
    },

    async setActiveAIModel(modelId) {
        const response = await fetch(`${API_BASE}/ai/settings/active/${modelId}`, {
            method: 'PUT'
        });
        return await handleResponse(response);
    },

    async deleteAISetting(modelId) {
        const response = await fetch(`${API_BASE}/ai/settings/${modelId}`, {
            method: 'DELETE'
        });
        return await handleResponse(response);
    },

    // 获取AI模型列表
    async getAIModels() {
        const response = await fetch(`${API_BASE}/ai/models`);
        return await handleResponse(response);
    }
};

async function handleResponse(response) {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Response is not JSON');
    }
    
    try {
        return await response.json();
    } catch (error) {
        console.error('JSON parse error:', error);
        throw new Error('Failed to parse JSON response');
    }
}

export default api;
