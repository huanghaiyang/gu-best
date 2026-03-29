<script setup>
import { ref } from 'vue';
import StockSearch from './stock-search.vue';
import PageContainer from './page-container.vue';
import StockTable from './stock-table.vue';
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

const analyzeStock = (stock) => {
    window.dispatchEvent(new CustomEvent('analyze-stock', { detail: stock }));
};
</script>

<template>
    <page-container page-id="search">
        <div class="search-page">
            <stock-search 
                :loading="searchLoading"
                @search="searchStock"
            ></stock-search>
            
            <div v-if="searchResults.length > 0" class="mt-4">
                <stock-table 
                    :stocks="searchResults"
                    :loading="searchLoading"
                    category="查询结果"
                    :show-filter="false"
                    :show-sort="true"
                    :show-actions="true"
                    :show-kline="true"
                    @analyze="analyzeStock"
                ></stock-table>
            </div>
        </div>
    </page-container>
</template>