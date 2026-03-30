<script setup>
import { ref } from 'vue';

const props = defineProps({
    loading: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['search']);

const searchQuery = ref('');

const handleSearch = () => {
    if (!searchQuery.value.trim()) {
        return;
    }
    emit('search', searchQuery.value);
};

const clearSearch = () => {
    searchQuery.value = '';
};
</script>

<template>
    <div class="card">
        <div class="card-header">
            <span><i class="bi bi-search me-2"></i>股票查询</span>
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
                        v-if="searchQuery" 
                        class="btn btn-outline-secondary" 
                        @click="clearSearch"
                        style="border-left: none; border-radius: 0 .25rem .25rem 0;"
                    >
                        <i class="bi bi-x-circle"></i>
                    </button>
                    <button 
                        class="btn btn-primary" 
                        @click="handleSearch"
                        :disabled="loading || !searchQuery.trim()"
                        style="border-radius: .25rem; margin-left: 0.5rem;"
                    >
                        <i class="bi bi-search me-1"></i>查询
                    </button>
                </div>
            </div>

            <div v-if="loading" class="loading-spinner" style="display: block;">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
                <p class="mt-2 text-muted">正在查询...</p>
            </div>

            <div v-if="!searchQuery" class="text-muted text-center py-4">
                <i class="bi bi-search" style="font-size: 3rem;"></i>
                <p class="mt-2">输入股票名称或代码进行查询</p>
            </div>
        </div>
    </div>
</template>