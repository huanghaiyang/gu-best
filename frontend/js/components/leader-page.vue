<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import StatsCard from './stats-card.vue';
import SectorTags from './sector-tags.vue';
import StockTable from './stock-table.vue';
import PageContainer from './page-container.vue';
import api from '../api.js';
import { startMarketStatusCheck, stopMarketStatusCheck } from '../store/marketStatus.js';
import { useAutoRefresh } from '../hooks/useAutoRefresh.js';
import toast from '../utils/toast.js';

const sectors = ref([]);
const stocks = ref([]);
const currentSector = ref(null);
const sectorsLoading = ref(false);
const stocksLoading = ref(false);

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

const currentSectorInfo = computed(() => {
    if (!currentSector.value) return null;
    return sectors.value.find(sector => sector.code === currentSector.value) || null;
});



const loadIndexData = async () => {
    try {
        const data = await api.getIndexData();
        if (data.success) {
            indexData.value = data.data;
        }
    } catch (error) {
        console.error('加载指数数据失败:', error);
        toast.error('加载指数数据失败: ' + error.message);
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
        toast.error('加载板块失败: ' + error.message);
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
        toast.error('加载股票失败: ' + error.message);
    }
    stocksLoading.value = false;
};

const selectSector = (sectorCode) => {
    currentSector.value = currentSector.value === sectorCode ? null : sectorCode;
    loadStocks();
};

const refreshAllData = async () => {
    await loadIndexData();
    await loadSectors();
    
    if (stocks.value.length > 0) {
        try {
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
    }
};

const { start: startAutoRefresh, stop: stopAutoRefresh } = useAutoRefresh(refreshAllData, {
    interval: 1000,
    onlyDuringMarketHours: true,
    immediate: true
});

const analyzeStock = (stock) => {
    window.dispatchEvent(new CustomEvent('analyze-stock', { detail: stock }));
};

onMounted(() => {
    loadIndexData();
    loadSectors();
    loadStocks();
    startMarketStatusCheck();
    startAutoRefresh();
});

onBeforeUnmount(() => {
    stopAutoRefresh();
    stopMarketStatusCheck();
});

defineExpose({
    refreshStockPrices: refreshAllData
});
</script>

<template>
    <page-container page-id="leader">
        <div class="leader-page">
            <div class="index-bar mb-3">
                <div class="row">
                    <div class="col-md-3" v-for="(idx, key) in indexData" :key="key">
                        <div class="index-card" :class="idx.change_pct >= 0 ? 'up' : 'down'">
                            <div class="index-name">{{ idx.name }}</div>
                            <div class="index-price">{{ (idx.price).toFixed(2) }}</div>
                            <div class="index-change">
                                <span>{{ idx.change >= 0 ? '+' : '' }}{{ (idx.change).toFixed(2) }}</span>
                                <span class="ms-2">{{ idx.change_pct >= 0 ? '+' : '' }}{{ (idx.change_pct).toFixed(2) }}%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

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
                        :category="currentSectorInfo ? currentSectorInfo.name : '涨幅榜'"
                        :sector="currentSectorInfo"
                        @analyze="analyzeStock"
                    ></stock-table>
                </div>
            </div>
        </div>
    </page-container>
</template>