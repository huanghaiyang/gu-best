<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
    sectors: {
        type: Array,
        default: () => []
    },
    currentSector: {
        type: String,
        default: null
    },
    loading: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['select', 'refresh']);

const collapsedCategories = ref({});
const allCollapsed = ref(false);

const sectorsByCategory = computed(() => {
    const grouped = { '其他': [] };
    
    props.sectors.forEach(sector => {
        const category = sector.category || '其他';
        if (!grouped[category]) {
            grouped[category] = [];
        }
        grouped[category].push(sector);
    });
    
    if (grouped['其他'].length === 0) {
        delete grouped['其他'];
    }
    
    return grouped;
});

const sortedCategories = computed(() => {
    const categories = Object.keys(sectorsByCategory.value);
    const order = ['科技', '新能源', '医药', '消费', '金融', '汽车', '军工', '周期', '农业', '其他'];
    return categories.sort((a, b) => {
        const aIndex = order.indexOf(a);
        const bIndex = order.indexOf(b);
        if (aIndex === -1 && bIndex === -1) return a.localeCompare(b);
        if (aIndex === -1) return 1;
        if (bIndex === -1) return -1;
        return aIndex - bIndex;
    });
});

const toggleCategory = (category) => {
    collapsedCategories.value[category] = !collapsedCategories.value[category];
};

const toggleAll = () => {
    allCollapsed.value = !allCollapsed.value;
    // 遍历所有分类并设置为相同的折叠状态
    Object.keys(sectorsByCategory.value).forEach(category => {
        collapsedCategories.value[category] = allCollapsed.value;
    });
};

const isCollapsed = (category) => {
    return collapsedCategories.value[category] === true;
};

const refreshSectors = () => {
    emit('refresh');
};
</script>

<template>
    <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
            <span><i class="bi bi-grid-3x3-gap me-2"></i>热门板块</span>
            <div class="d-flex gap-2">
                <button class="btn btn-sm btn-outline-primary" @click="toggleAll">
                    <i :class="allCollapsed ? 'bi bi-chevron-down' : 'bi bi-chevron-up'" class="me-1"></i>
                    {{ allCollapsed ? '展开全部' : '折叠全部' }}
                </button>
                <button class="btn btn-sm btn-outline-primary" @click="refreshSectors">
                    <i class="bi bi-arrow-clockwise me-1"></i>刷新
                </button>
            </div>
        </div>
        <div class="card-body">
            <div v-if="loading" class="loading">
                <span class="text-muted">加载中...</span>
            </div>
            <div v-else-if="sectors.length === 0" class="text-muted">
                暂无板块数据
            </div>
            <div v-else>
                <div v-for="category in sortedCategories" :key="category" class="mb-2">
                    <div 
                        class="category-header d-flex justify-content-between align-items-center" 
                        @click="toggleCategory(category)"
                        style="cursor: pointer;"
                    >
                        <h6 class="text-muted mb-0">
                            <i :class="isCollapsed(category) ? 'bi bi-chevron-right' : 'bi bi-chevron-down'" class="me-1"></i>
                            {{ category }}
                            <span class="badge bg-secondary ms-1" style="font-size: 0.7em;">{{ sectorsByCategory[category].length }}</span>
                        </h6>
                    </div>
                    <div v-show="!isCollapsed(category)" class="sector-tags-container mt-2">
                        <span 
                            v-for="sector in sectorsByCategory[category]" 
                            :key="sector.code"
                            class="sector-tag"
                            :class="{ active: currentSector === sector.code }"
                            @click="$emit('select', sector.code)"
                        >
                            {{ sector.name }}
                            <span :class="sector.change_pct > 0 ? 'text-danger' : 'text-success'">
                                {{ sector.change_pct > 0 ? '+' : '' }}{{ sector.change_pct.toFixed(2) }}%
                            </span>
                            <span class="leading-stock" v-if="sector.leading_stock">
                                {{ sector.leading_stock }}
                            </span>
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>