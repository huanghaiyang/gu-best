<script setup>
import { watch } from 'vue';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    stock: {
        type: Object,
        default: () => ({})
    },
    analysis: {
        type: Object,
        default: () => ({})
    },
    loading: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['close']);

watch(() => props.visible, (val) => {
    if (val) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
});

const getRecommendationClass = (recommendation) => {
    if (recommendation === '买入') return 'bg-danger';
    if (recommendation === '卖出') return 'bg-success';
    return 'bg-warning';
};
</script>

<template>
    <div class="modal fade" :class="{ show: visible }" :style="{ display: visible ? 'block' : 'none' }" tabindex="-1">
        <div class="modal-dialog modal-lg modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="bi bi-robot me-2"></i>
                        AI分析报告 - {{ stock.name }}({{ stock.code }})
                    </h5>
                    <button type="button" class="btn-close" @click="$emit('close')"></button>
                </div>
                <div class="modal-body">
                    <div v-if="loading" class="text-center py-4">
                        <div class="spinner-border text-primary" role="status"></div>
                        <p class="mt-2 text-muted">AI正在分析中...</p>
                    </div>
                    <div v-else>
                        <div class="mb-3">
                            <span class="badge me-2" :class="getRecommendationClass(analysis.recommendation)">
                                {{ analysis.recommendation || '观望' }}
                            </span>
                            <span class="text-muted">
                                置信度: {{ Math.round((analysis.confidence || 0) * 100) }}%
                            </span>
                        </div>
                        <div class="analysis-card p-3 rounded">
                            <pre style="white-space: pre-wrap; font-family: inherit; margin: 0;">{{ analysis.analysis }}</pre>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" @click="$emit('close')">关闭</button>
                </div>
            </div>
        </div>
        <div v-if="visible" class="modal-backdrop fade show"></div>
    </div>
</template>