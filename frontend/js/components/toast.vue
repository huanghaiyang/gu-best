<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

const props = defineProps({
    message: {
        type: String,
        required: true
    },
    type: {
        type: String,
        default: 'info',
        validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
    },
    duration: {
        type: Number,
        default: 3000
    },
    position: {
        type: String,
        default: 'top-right',
        validator: (value) => ['top-left', 'top-center', 'top-right', 'bottom-left', 'bottom-center', 'bottom-right'].includes(value)
    }
});

const emit = defineEmits(['close']);

const visible = ref(false);
const timer = ref(null);

const typeIcons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
};

const typeClasses = {
    success: 'toast-success',
    error: 'toast-error',
    warning: 'toast-warning',
    info: 'toast-info'
};

onMounted(() => {
    visible.value = true;
    
    if (props.duration > 0) {
        timer.value = setTimeout(() => {
            close();
        }, props.duration);
    }
});

onBeforeUnmount(() => {
    if (timer.value) {
        clearTimeout(timer.value);
    }
});

const close = () => {
    visible.value = false;
    setTimeout(() => {
        emit('close');
    }, 300);
};

const onMouseEnter = () => {
    if (timer.value) {
        clearTimeout(timer.value);
    }
};

const onMouseLeave = () => {
    if (props.duration > 0) {
        timer.value = setTimeout(() => {
            close();
        }, props.duration);
    }
};
</script>

<template>
    <transition name="toast-fade">
        <div 
            v-if="visible"
            class="toast-container"
            :class="[
                typeClasses[type],
                `toast-${position}`
            ]"
            @mouseenter="onMouseEnter"
            @mouseleave="onMouseLeave"
        >
            <div class="toast-icon">{{ typeIcons[type] }}</div>
            <div class="toast-message">{{ message }}</div>
            <button class="toast-close" @click="close">×</button>
        </div>
    </transition>
</template>

<style scoped>
.toast-container {
    position: fixed;
    min-width: 300px;
    max-width: 500px;
    padding: 16px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    display: flex;
    align-items: center;
    gap: 12px;
    z-index: 9999;
    font-size: 14px;
    line-height: 1.5;
    backdrop-filter: blur(10px);
}

.toast-top-left {
    top: 20px;
    left: 20px;
}

.toast-top-center {
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
}

.toast-top-right {
    top: 20px;
    right: 20px;
}

.toast-bottom-left {
    bottom: 20px;
    left: 20px;
}

.toast-bottom-center {
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
}

.toast-bottom-right {
    bottom: 20px;
    right: 20px;
}

.toast-icon {
    font-size: 20px;
    font-weight: bold;
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.toast-message {
    flex: 1;
    word-break: break-word;
}

.toast-close {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: inherit;
    opacity: 0.6;
    transition: opacity 0.2s;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.toast-close:hover {
    opacity: 1;
}

.toast-success {
    background: rgba(16, 185, 129, 0.95);
    color: white;
    border-left: 4px solid #059669;
}

.toast-error {
    background: rgba(239, 68, 68, 0.95);
    color: white;
    border-left: 4px solid #dc2626;
}

.toast-warning {
    background: rgba(245, 158, 11, 0.95);
    color: white;
    border-left: 4px solid #d97706;
}

.toast-info {
    background: rgba(59, 130, 246, 0.95);
    color: white;
    border-left: 4px solid #2563eb;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
    transition: all 0.3s ease;
}

.toast-fade-enter-from {
    opacity: 0;
    transform: translateY(-20px);
}

.toast-fade-leave-to {
    opacity: 0;
    transform: translateY(-20px);
}
</style>
