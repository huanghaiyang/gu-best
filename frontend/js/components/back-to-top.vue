<script setup>
import { ref, onMounted, onUnmounted, inject, watch } from 'vue';

const showBackToTop = ref(false);

const pageContainer = inject('pageContainer', null);

const handleScroll = () => {
    // 尝试获取页面容器元素
    const container = document.querySelector('.page-container');
    if (container) {
        showBackToTop.value = container.scrollTop > 300;
    }
};

const backToTop = () => {
    if (pageContainer) {
        pageContainer.scrollToTop();
    } else {
        // 尝试获取页面容器元素
        const container = document.querySelector('.page-container');
        if (container) {
            container.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
    }
};

onMounted(() => {
    // 尝试获取页面容器元素并添加滚动事件监听器
    const container = document.querySelector('.page-container');
    if (container) {
        container.addEventListener('scroll', handleScroll);
        // 初始检查
        handleScroll();
    }
});

onUnmounted(() => {
    // 尝试获取页面容器元素并移除滚动事件监听器
    const container = document.querySelector('.page-container');
    if (container) {
        container.removeEventListener('scroll', handleScroll);
    }
});
</script>

<template>
    <button 
        v-if="showBackToTop" 
        class="back-to-top" 
        @click="backToTop"
        title="返回顶部"
    >
        <i class="bi bi-arrow-up"></i>
    </button>
</template>

<style scoped>
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