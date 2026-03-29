<script setup>
import { ref, onActivated, provide, onMounted, onUnmounted } from 'vue';

const props = defineProps({
    pageId: {
        type: String,
        required: true
    },
    backToTopThreshold: {
        type: Number,
        default: 0
    }
});

const containerRef = ref(null);
const scrollPosition = ref(0);
const showBackToTop = ref(false);

const handleScroll = () => {
    if (containerRef.value) {
        scrollPosition.value = containerRef.value.scrollTop;
        showBackToTop.value = containerRef.value.scrollTop > props.backToTopThreshold;
    }
};

const scrollToTop = () => {
    if (containerRef.value) {
        containerRef.value.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
};

onMounted(() => {
    if (containerRef.value) {
        containerRef.value.addEventListener('scroll', handleScroll);
    }
});

onUnmounted(() => {
    if (containerRef.value) {
        containerRef.value.removeEventListener('scroll', handleScroll);
    }
});

onActivated(() => {
    if (containerRef.value && scrollPosition.value > 0) {
        containerRef.value.scrollTop = scrollPosition.value;
    }
});

// 提供页面容器的方法给子组件
provide('pageContainer', {
    scrollToTop
});
</script>

<template>
    <div class="page-container" ref="containerRef">
        <slot></slot>
        <button 
            v-if="showBackToTop" 
            class="back-to-top" 
            @click="scrollToTop"
            title="返回顶部"
        >
            <i class="bi bi-arrow-up"></i>
        </button>
    </div>
</template>

<style scoped>
.page-container {
    min-height: 100%;
    position: relative;
    overflow-y: auto;
    height: calc(100vh - 120px); /* 减去顶部导航栏和标签栏的高度 */
}

.back-to-top {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background-color: rgba(0, 0, 0, 0.6);
    color: white;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    transition: all 0.3s ease;
}

.back-to-top:hover {
    background-color: rgba(0, 0, 0, 0.8);
    transform: translateY(-2px);
}

.back-to-top i {
    font-size: 1.5rem;
}
</style>