<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import Sidebar from './components/sidebar.vue';
import StatsCard from './components/stats-card.vue';
import SectorTags from './components/sector-tags.vue';
import StockTable from './components/stock-table.vue';
import StockSearch from './components/stock-search.vue';
import AnalysisModal from './components/analysis-modal.vue';
import api from './api.js';

const currentPage = ref('leader');
const sectors = ref([]);
const stocks = ref([]);
const searchResults = ref([]);
const currentSector = ref(null);
const sectorsLoading = ref(false);
const stocksLoading = ref(false);
const searchLoading = ref(false);
const modalVisible = ref(false);
const modalLoading = ref(false);
const currentStock = ref({});
const currentAnalysis = ref({});
const searchQuery = ref('');
const currentTime = ref('');

const autoRefresh = ref(false);
const refreshInterval = ref(30);
let refreshTimer = null;

// 设置相关状态
const showModelSettings = ref(false);
const showAbout = ref(false);
const selectedModel = ref('volcengine');
const modelParams = ref({
    temperature: 0.7,
    maxTokens: 2048
});
const apiConfigs = ref({
    volcengine: {
        apiUrl: 'https://ark.cn-beijing.volces.com/api/v3/responses',
        apiKey: '',
        model: 'doubao-seed-2-0-pro-260215'
    },
    openai: {
        apiUrl: 'https://api.openai.com/v1',
        apiKey: '',
        model: 'gpt-4'
    },
    claude: {
        apiUrl: 'https://api.anthropic.com/v1',
        apiKey: '',
        model: 'claude-3-opus-20240229'
    },
    gemini: {
        apiUrl: 'https://generativelanguage.googleapis.com/v1beta',
        apiKey: '',
        model: 'gemini-pro'
    },
    qwen: {
        apiUrl: 'https://dashscope.aliyuncs.com/api/v1',
        apiKey: '',
        model: 'qwen-turbo'
    },
    ernie: {
        apiUrl: 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1',
        apiKey: '',
        secretKey: '',
        model: 'ernie-bot-4'
    }
});
const models = ref([
    {
        id: 'volcengine',
        name: '火山引擎',
        description: '字节跳动旗下AI模型，中文理解能力强，响应速度快'
    },
    {
        id: 'gpt4',
        name: 'GPT-4',
        description: 'OpenAI最新模型，逻辑推理和创意能力出色'
    },
    {
        id: 'claude',
        name: 'Claude 3',
        description: 'Anthropic开发的AI模型，安全可靠，长文本处理能力强'
    },
    {
        id: 'gemini',
        name: 'Gemini',
        description: 'Google开发的多模态模型，综合能力强大'
    },
    {
        id: 'llama3',
        name: 'Llama 3',
        description: 'Meta开源模型，可本地部署，隐私性好'
    },
    {
        id: 'kimi',
        name: 'Kimi',
        description: '深度求索开发的中文模型，知识更新及时'
    },
    {
        id: 'doubao',
        name: '豆包',
        description: '字节跳动开发的对话模型，日常交互友好'
    }
]);

const indexData = ref({
    sh: { name: '上证指数', code: '000001', price: 0, change: 0, change_pct: 0 },
    sz: { name: '深证成指', code: '399001', price: 0, change: 0, change_pct: 0 },
    cy: { name: '创业板指', code: '399006', price: 0, change: 0, change_pct: 0 },
    kc: { name: '科创50', code: '000688', price: 0, change: 0, change_pct: 0 }
});

const stats = computed(() => {
    if (stocks.value.length === 0) {
        return {
            total: '-',
            avgChange: '-',
            avgVolume: '-',
            avgScore: '-'
        };
    }
    const total = stocks.value.length;
    const avgChange = stocks.value.reduce((sum, s) => sum + (s.change_pct || 0), 0) / total;
    const avgVolume = stocks.value.reduce((sum, s) => sum + (s.volume_ratio || 0), 0) / total;
    const avgScore = stocks.value.reduce((sum, s) => sum + (s.score || 0), 0) / total;
    return {
        total,
        avgChange: avgChange.toFixed(2) + '%',
        avgVolume: avgVolume.toFixed(2),
        avgScore: avgScore.toFixed(1)
    };
});

const loadIndexData = async () => {
    try {
        const data = await api.getIndexData();
        if (data.success) {
            indexData.value = data.data;
        }
    } catch (error) {
        console.error('加载指数数据失败:', error);
    }
};

const loadSectors = async () => {
    sectorsLoading.value = true;
    try {
        const data = await api.getSectors();
        if (data.success) {
            sectors.value = data.data;
        }
    } catch (error) {
        console.error('加载板块失败:', error);
    }
    sectorsLoading.value = false;
};

const loadStocks = async (topN = 10) => {
    stocksLoading.value = true;
    try {
        const data = await api.getLeaderStocks(currentSector.value, topN);
        if (data.success) {
            stocks.value = data.data;
        }
    } catch (error) {
        console.error('加载股票失败:', error);
    }
    stocksLoading.value = false;
};

const searchStock = async (query) => {
    searchLoading.value = true;
    searchResults.value = [];
    try {
        const data = await api.searchStock(query);
        if (data.success) {
            searchResults.value = data.data;
        }
    } catch (error) {
        console.error('查询失败:', error);
    }
    searchLoading.value = false;
};

const selectSector = (sectorCode) => {
    currentSector.value = currentSector.value === sectorCode ? null : sectorCode;
    loadStocks();
};

const analyzeStock = async (stock) => {
    currentStock.value = stock;
    modalVisible.value = true;
    modalLoading.value = true;
    currentAnalysis.value = {};

    try {
        // 准备模型配置
        const modelConfig = {
            model: selectedModel.value,
            params: modelParams.value,
            apiConfig: apiConfigs.value[selectedModel.value]
        };
        
        const data = await api.analyzeStock(stock.code, stock.name, stock, modelConfig);
        if (data.success) {
            currentAnalysis.value = data.data;
        }
    } catch (error) {
        console.error('分析失败:', error);
    }
    modalLoading.value = false;
};

const closeModal = () => {
    modalVisible.value = false;
};

const navigateTo = (page) => {
    currentPage.value = page;
    if (page === 'leader') {
        loadSectors();
        loadStocks();
    }
};

const toggleAutoRefresh = () => {
    if (autoRefresh.value) {
        startAutoRefresh();
    } else {
        stopAutoRefresh();
    }
};

const startAutoRefresh = () => {
    stopAutoRefresh();
    refreshTimer = setInterval(() => {
        if (currentPage.value === 'leader') {
            loadStocks();
            loadIndexData();
        } else if (currentPage.value === 'search' && searchResults.value.length > 0) {
            const lastQuery = searchResults.value[0]?.name || '';
            if (lastQuery) {
                searchStock(lastQuery);
            }
        }
    }, refreshInterval.value * 1000);
};

const stopAutoRefresh = () => {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
    }
};

const updateRefreshInterval = () => {
    if (autoRefresh.value) {
        startAutoRefresh();
    }
};

const refreshAll = () => {
    if (currentPage.value === 'leader') {
        loadSectors();
        loadStocks();
        loadIndexData();
    } else if (currentPage.value === 'search' && searchResults.value.length > 0) {
        const lastQuery = searchResults.value[0]?.name || '';
        if (lastQuery) {
            searchStock(lastQuery);
        }
    }
};

const refreshStockPrices = async () => {
    if (currentPage.value === 'leader' && stocks.value.length > 0) {
        try {
            // 只刷新股价数据，不刷新整个股票列表
            const updatedStocks = await Promise.all(stocks.value.map(async (stock) => {
                try {
                    const realtimeData = await api.getRealtimeQuote(stock.code);
                    if (realtimeData && realtimeData.success) {
                        return {
                            ...stock,
                            price: realtimeData.data.price,
                            change: realtimeData.data.change,
                            change_pct: realtimeData.data.change_pct,
                            volume: realtimeData.data.volume
                        };
                    }
                    return stock;
                } catch (error) {
                    console.error('刷新股票价格失败:', error);
                    return stock;
                }
            }));
            
            stocks.value = updatedStocks;
        } catch (error) {
            console.error('刷新股价数据失败:', error);
        }
    } else if (currentPage.value === 'search' && searchResults.value.length > 0) {
        try {
            const updatedResults = await Promise.all(searchResults.value.map(async (stock) => {
                try {
                    const realtimeData = await api.getRealtimeQuote(stock.code);
                    if (realtimeData && realtimeData.success) {
                        return {
                            ...stock,
                            price: realtimeData.data.price,
                            change: realtimeData.data.change,
                            change_pct: realtimeData.data.change_pct,
                            volume: realtimeData.data.volume
                        };
                    }
                    return stock;
                } catch (error) {
                    console.error('刷新搜索结果价格失败:', error);
                    return stock;
                }
            }));
            
            searchResults.value = updatedResults;
        } catch (error) {
            console.error('刷新搜索结果股价数据失败:', error);
        }
    }
};

const updateTime = () => {
    currentTime.value = new Date().toLocaleString('zh-CN');
};

// 模型设置方法
const loadModelSettings = async () => {
    try {
        const response = await api.getSetting('modelSettings');
        if (response.success && response.data) {
            const settings = response.data;
            selectedModel.value = settings.model || 'volcengine';
            modelParams.value = { ...modelParams.value, ...settings.params };
            if (settings.apiConfigs) {
                apiConfigs.value = { ...apiConfigs.value, ...settings.apiConfigs };
            }
        }
    } catch (error) {
        console.error('加载模型设置失败:', error);
    }
};

const saveModelSettings = async () => {
    try {
        const settings = {
            model: selectedModel.value,
            params: modelParams.value,
            apiConfigs: apiConfigs.value
        };
        await api.setSetting('modelSettings', settings);
        showModelSettings.value = false;
        alert('模型设置已保存');
    } catch (error) {
        console.error('保存模型设置失败:', error);
        alert('保存模型设置失败，请稍后重试');
    }
};

onMounted(async () => {
    loadIndexData();
    loadSectors();
    loadStocks();
    updateTime();
    await loadModelSettings();
    setInterval(updateTime, 1000);
});

onUnmounted(() => {
    stopAutoRefresh();
});
</script>

<template>
    <div class="app-container">
        <sidebar :current-page="currentPage" @navigate="navigateTo"></sidebar>
        
        <div class="main-content">
            <!-- 模型设置弹窗 -->
            <div v-if="showModelSettings" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content bg-dark text-white">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-brain me-2"></i>AI模型设置
                            </h5>
                            <button type="button" class="btn-close btn-close-white" @click="showModelSettings = false"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-4">
                                <label class="form-label fw-bold">选择AI模型</label>
                                <div class="list-group">
                                    <div 
                                        v-for="model in models" 
                                        :key="model.id"
                                        class="list-group-item bg-dark text-white border border-gray-700 cursor-pointer"
                                        :class="{ 'active': selectedModel === model.id }"
                                        @click="selectedModel = model.id"
                                    >
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div>
                                                <h6 class="mb-1">{{ model.name }}</h6>
                                                <p class="text-muted text-sm">{{ model.description }}</p>
                                            </div>
                                            <input 
                                                type="radio" 
                                                :name="'model'" 
                                                :checked="selectedModel === model.id"
                                                @change="selectedModel = model.id"
                                            >
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-4">
                                <label class="form-label fw-bold">模型参数</label>
                                <div class="row">
                                    <div class="col-md-6">
                                        <label class="form-label">温度 (Temperature)</label>
                                        <input 
                                            type="range" 
                                            v-model.number="modelParams.temperature" 
                                            class="form-range"
                                            min="0.1" 
                                            max="1.0" 
                                            step="0.1"
                                        >
                                        <small class="text-muted">{{ modelParams.temperature }}</small>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">最大 tokens</label>
                                        <input 
                                            type="number" 
                                            v-model.number="modelParams.maxTokens" 
                                            class="form-control bg-gray-800 border-gray-700 text-white"
                                            min="100" 
                                            max="4096"
                                        >
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mb-4">
                                <label class="form-label fw-bold">API配置</label>
                                <div class="mb-3">
                                    <label class="form-label">API地址</label>
                                    <input 
                                        type="text" 
                                        v-model="apiConfigs[selectedModel].apiUrl" 
                                        class="form-control bg-gray-800 border-gray-700 text-white"
                                        placeholder="请输入API地址"
                                    >
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">API Key</label>
                                    <input 
                                        type="password" 
                                        v-model="apiConfigs[selectedModel].apiKey" 
                                        class="form-control bg-gray-800 border-gray-700 text-white"
                                        placeholder="请输入API Key"
                                    >
                                </div>
                                <div class="mb-3" v-if="selectedModel === 'ernie'">
                                    <label class="form-label">Secret Key</label>
                                    <input 
                                        type="password" 
                                        v-model="apiConfigs[selectedModel].secretKey" 
                                        class="form-control bg-gray-800 border-gray-700 text-white"
                                        placeholder="请输入Secret Key"
                                    >
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">模型名称</label>
                                    <input 
                                        type="text" 
                                        v-model="apiConfigs[selectedModel].model" 
                                        class="form-control bg-gray-800 border-gray-700 text-white"
                                        placeholder="请输入模型名称"
                                    >
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="showModelSettings = false">取消</button>
                            <button type="button" class="btn btn-primary" @click="saveModelSettings">保存设置</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 关于弹窗 -->
            <div v-if="showAbout" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
                <div class="modal-dialog">
                    <div class="modal-content bg-dark text-white">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-info-circle me-2"></i>关于系统
                            </h5>
                            <button type="button" class="btn-close btn-close-white" @click="showAbout = false"></button>
                        </div>
                        <div class="modal-body">
                            <p class="mb-2">智能选股系统 v1.0.0</p>
                            <p class="mb-2">基于Node.js + Vue + Python开发</p>
                            <p class="mb-2">提供实时股票分析和AI预测</p>
                            <p class="text-muted">© 2026 智能选股系统</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-primary" @click="showAbout = false">确定</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="content-wrapper">
                <div v-if="currentPage === 'leader'" class="index-bar mb-3">
                    <div class="row">
                        <div class="col-md-3" v-for="(idx, key) in indexData" :key="key">
                            <div class="index-card" :class="idx.change_pct >= 0 ? 'up' : 'down'">
                                <div class="index-name">{{ idx.name }}</div>
                                <div class="index-price">{{ idx.price.toFixed(2) }}</div>
                                <div class="index-change">
                                    <span>{{ idx.change >= 0 ? '+' : '' }}{{ idx.change.toFixed(2) }}</span>
                                    <span class="ms-2">{{ idx.change_pct >= 0 ? '+' : '' }}{{ idx.change_pct.toFixed(2) }}%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-if="currentPage === 'leader'">
                    <div class="row mb-4">
                        <div class="col-md-3">
                            <stats-card title="筛选股票数" :value="stats.total"></stats-card>
                        </div>
                        <div class="col-md-3">
                            <stats-card title="平均涨幅" :value="stats.avgChange" value-class="text-danger"></stats-card>
                        </div>
                        <div class="col-md-3">
                            <stats-card title="平均量比" :value="stats.avgVolume" value-class="text-success"></stats-card>
                        </div>
                        <div class="col-md-3">
                            <stats-card title="平均得分" :value="stats.avgScore"></stats-card>
                        </div>
                    </div>

                    <div class="row mb-4">
                        <div class="col-12">
                            <sector-tags 
                                :sectors="sectors" 
                                :current-sector="currentSector"
                                :loading="sectorsLoading"
                                @select="selectSector"
                                @refresh="loadSectors"
                            ></sector-tags>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-12">
                            <stock-table 
                                :stocks="stocks"
                                :loading="stocksLoading"
                                @analyze="analyzeStock"
                                @refresh-prices="refreshStockPrices"
                            ></stock-table>
                        </div>
                    </div>
                </div>

                <div v-if="currentPage === 'search'">
                    <stock-search 
                        :loading="searchLoading"
                        :results="searchResults"
                        @search="searchStock"
                        @analyze="analyzeStock"
                        @refresh-prices="refreshStockPrices"
                    ></stock-search>
                </div>



                <div v-if="currentPage === 'portfolio'">
                    <div class="card">
                        <div class="card-body text-center py-5">
                            <i class="bi bi-wallet2" style="font-size: 3rem; color: #64748b;"></i>
                            <h5 class="mt-3">自选股功能</h5>
                            <p class="text-muted">功能开发中，敬请期待...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <analysis-modal 
            :visible="modalVisible"
            :stock="currentStock"
            :analysis="currentAnalysis"
            :loading="modalLoading"
            @close="closeModal"
        ></analysis-modal>
    </div>
</template>