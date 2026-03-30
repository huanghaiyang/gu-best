<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import Sidebar from './components/sidebar.vue';
import LeaderPage from './components/leader-page.vue';
import SearchPage from './components/search-page.vue';
import PortfolioPage from './components/portfolio-page.vue';
import AnalysisModal from './components/analysis-modal.vue';
import api from './api.js';
import toast from './utils/toast.js';

const tabs = ref([]);
const activeTab = ref(null);
const modalVisible = ref(false);
const modalLoading = ref(false);
const currentStock = ref({});
const currentAnalysis = ref({});

const pageNames = {
    'leader': '龙头股票',
    'search': '股票搜索',
    'portfolio': '自选股'
};

const pageComponents = {
    'leader': LeaderPage,
    'search': SearchPage,
    'portfolio': PortfolioPage
};

const pageRefs = ref({});

const navigateTo = (page) => {
    const existingTab = tabs.value.find(tab => tab.id === page);
    if (existingTab) {
        activeTab.value = page;
    } else {
        tabs.value.push({ id: page, name: pageNames[page] || page });
        activeTab.value = page;
    }
    updateHash(page);
};

const closeTab = (tabId, event) => {
    event.stopPropagation();
    const index = tabs.value.findIndex(tab => tab.id === tabId);
    if (index > -1) {
        tabs.value.splice(index, 1);
        if (activeTab.value === tabId) {
            if (tabs.value.length > 0) {
                const newActiveTab = tabs.value[Math.max(0, index - 1)];
                activeTab.value = newActiveTab.id;
                updateHash(newActiveTab.id);
            } else {
                activeTab.value = null;
                updateHash('');
            }
        }
    }
};

const updateHash = (page) => {
    if (page) {
        window.location.hash = `#${page}`;
    } else {
        window.location.hash = '';
    }
};

const handleHashChange = () => {
    const hash = window.location.hash.slice(1);
    if (hash) {
        const existingTab = tabs.value.find(tab => tab.id === hash);
        if (existingTab) {
            activeTab.value = hash;
        } else {
            tabs.value.push({ id: hash, name: pageNames[hash] || hash });
            activeTab.value = hash;
        }
    } else {
        if (tabs.value.length === 0) {
            activeTab.value = null;
        }
    }
};

const analyzeStock = async (stock) => {
    currentStock.value = stock;
    modalVisible.value = true;
    modalLoading.value = true;
    currentAnalysis.value = {};

    try {
        const data = await api.analyzeStock(stock.code, stock.name, stock);
        if (data.success) {
            currentAnalysis.value = data.data;
            toast.success('股票分析完成');
        } else {
            toast.error('股票分析失败: ' + (data.error || '未知错误'));
        }
    } catch (error) {
        console.error('分析失败:', error);
        toast.error('股票分析失败: ' + error.message);
    }
    modalLoading.value = false;
};

const closeModal = () => {
    modalVisible.value = false;
};

const refreshActiveTabPrices = () => {
    if (activeTab.value && pageRefs.value[activeTab.value]) {
        const pageComponent = pageRefs.value[activeTab.value];
        if (pageComponent && pageComponent.refreshStockPrices) {
            pageComponent.refreshStockPrices();
        }
    }
};

const handleAnalyzeStock = (event) => {
    const stock = event.detail;
    analyzeStock(stock);
};

onMounted(() => {
    handleHashChange();
    // 如果没有激活的标签页，默认打开龙头股票页面
    if (!activeTab.value && tabs.value.length === 0) {
        navigateTo('leader');
    }
    window.addEventListener('hashchange', handleHashChange);
    window.addEventListener('analyze-stock', handleAnalyzeStock);
});

onUnmounted(() => {
    window.removeEventListener('hashchange', handleHashChange);
    window.removeEventListener('analyze-stock', handleAnalyzeStock);
});
</script>

<template>
    <div class="app-container">
        <sidebar @navigate="navigateTo"></sidebar>
        
        <div class="main-content">
            <div class="content-wrapper">
                <div v-if="tabs.length > 0" class="tabs-container mb-3">
                    <div 
                        v-for="tab in tabs" 
                        :key="tab.id"
                        :class="['tab-item', { active: activeTab === tab.id }]"
                        @click="activeTab = tab.id; updateHash(tab.id)"
                    >
                        <span class="tab-title">{{ tab.name }}</span>
                        <span class="tab-close" @click="closeTab(tab.id, $event)">&times;</span>
                    </div>
                </div>

                <div v-if="activeTab && pageComponents[activeTab]" class="page-content">
                    <keep-alive>
                        <component 
                            :is="pageComponents[activeTab]" 
                            :ref="(el) => { if (el) pageRefs[activeTab] = el; }"
                            @analyze="analyzeStock"
                        ></component>
                    </keep-alive>
                </div>

                <div v-if="!activeTab" class="empty-tabs-state">
                    <div class="card">
                        <div class="card-body text-center py-5">
                            <i class="bi bi-grid-3x3-gap" style="font-size: 3rem; color: #64748b;"></i>
                            <h5 class="mt-3">欢迎使用股票分析系统</h5>
                            <p class="text-muted">请从左侧菜单选择功能开始使用</p>
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