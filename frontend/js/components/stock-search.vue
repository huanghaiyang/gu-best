<script setup>
import { ref, watch, onBeforeUnmount } from 'vue';
import api from '../api.js';

const props = defineProps({
    loading: {
        type: Boolean,
        default: false
    },
    results: {
        type: Array,
        default: () => []
    }
});

const emit = defineEmits(['search', 'analyze', 'refresh-prices']);

const searchQuery = ref('');
const localAutoRefresh = ref(false);
const refreshTimer = ref(null);
const refreshInterval = ref(1);

watch(localAutoRefresh, (newVal) => {
    if (newVal) {
        startAutoRefresh();
    } else {
        stopAutoRefresh();
    }
});

onBeforeUnmount(() => {
    stopAutoRefresh();
});

const handleSearch = () => {
    if (!searchQuery.value.trim()) {
        return;
    }
    emit('search', searchQuery.value);
};

const clearSearch = () => {
    searchQuery.value = '';
};

const startAutoRefresh = () => {
    stopAutoRefresh();
    refreshTimer.value = setInterval(() => {
        emit('refresh-prices');
    }, refreshInterval.value * 1000);
};

const stopAutoRefresh = () => {
    if (refreshTimer.value) {
        clearInterval(refreshTimer.value);
        refreshTimer.value = null;
    }
};
</script>

<template>
    <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
            <span><i class="bi bi-search me-2"></i>股票查询</span>
            <div class="auto-refresh-control d-flex align-items-center">
                <label class="switch">
                    <input type="checkbox" v-model="localAutoRefresh">
                    <span class="slider"></span>
                </label>
                <span class="ms-2">自动刷新</span>
                <div class="interval-control ms-3">
                    <select v-model.number="refreshInterval" style="width: 60px;">
                        <option v-for="second in 10" :key="second" :value="second">{{ second }}秒</option>
                    </select>
                </div>
            </div>
        </div>
        <div class="card-body">
            <div class="search-container">
                <div class="input-group mb-3">
                    <input 
                        type="text" 
                        class="form-control form-control-lg" 
                        v-model="searchQuery"
                        @keyup.enter="handleSearch"
                        placeholder="输入股票名称或代码（如：贵州茅台 或 600519）"
                    >
                    <button 
                        class="btn btn-primary" 
                        @click="handleSearch"
                        :disabled="loading || !searchQuery.trim()"
                    >
                        <i class="bi bi-search me-1"></i>查询
                    </button>
                </div>
                <button 
                    v-if="searchQuery" 
                    class="btn btn-sm btn-outline-secondary mb-3"
                    @click="clearSearch"
                >
                    <i class="bi bi-x-circle me-1"></i>清除
                </button>
            </div>

            <div v-if="loading" class="loading-spinner" style="display: block;">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
                <p class="mt-2 text-muted">正在查询...</p>
            </div>

            <div v-else-if="results.length > 0" class="search-results">
                <h6 class="mb-3">查询结果 ({{ results.length }})</h6>
                <div class="table-responsive">
                    <table class="table stock-table">
                        <thead>
                            <tr>
                                <th>股票代码</th>
                                <th>股票名称</th>
                                <th>最新价</th>
                                <th>涨跌幅</th>
                                <th>市场</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="stock in results" :key="stock.code">
                                <td><code>{{ stock.code }}</code></td>
                                <td><strong>{{ stock.name }}</strong></td>
                                <td>{{ stock.price ? stock.price.toFixed(2) : '-' }}</td>
                                <td :class="stock.change_pct > 0 ? 'change-up' : stock.change_pct < 0 ? 'change-down' : ''">
                                    {{ stock.change_pct > 0 ? '+' : '' }}{{ (stock.change_pct || 0).toFixed(2) }}%
                                </td>
                                <td>
                                    <span v-if="stock.market" class="badge bg-secondary">{{ stock.market }}</span>
                                </td>
                                <td>
                                    <button 
                                        class="btn btn-sm btn-outline-primary"
                                        @click="$emit('analyze', stock)"
                                    >
                                        <i class="bi bi-robot me-1"></i>AI分析
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div v-else-if="searchQuery && !loading" class="text-muted text-center py-4">
                <i class="bi bi-search" style="font-size: 3rem;"></i>
                <p class="mt-2">点击查询按钮搜索股票</p>
            </div>

            <div v-else class="text-muted text-center py-4">
                <i class="bi bi-search" style="font-size: 3rem;"></i>
                <p class="mt-2">输入股票名称或代码进行查询</p>
            </div>
        </div>
    </div>
</template>