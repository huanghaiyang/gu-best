<script setup>
import { ref } from 'vue';
import StockSearch from './stock-search.vue';
import PageContainer from './page-container.vue';
import api from '../api.js';

const searchResults = ref([]);
const searchLoading = ref(false);

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

const refreshStockPrices = async () => {
    if (searchResults.value.length > 0) {
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

const analyzeStock = (stock) => {
    window.dispatchEvent(new CustomEvent('analyze-stock', { detail: stock }));
};

defineExpose({
    refreshStockPrices
});
</script>

<template>
    <page-container page-id="search">
        <div class="search-page">
            <stock-search 
                :loading="searchLoading"
                :results="searchResults"
                @search="searchStock"
                @analyze="analyzeStock"
                @refresh-prices="refreshStockPrices"
            ></stock-search>
        </div>
    </page-container>
</template>