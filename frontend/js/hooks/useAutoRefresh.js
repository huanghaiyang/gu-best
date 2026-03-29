import { ref, onBeforeUnmount } from 'vue';
import { isMarketOpen } from '../store/marketStatus.js';

export function useAutoRefresh(callback, options = {}) {
    const {
        interval = 1000,
        onlyDuringMarketHours = true,
        immediate = true
    } = options;

    const timer = ref(null);
    const isRunning = ref(false);

    const refresh = async () => {
        if (onlyDuringMarketHours && !isMarketOpen.value) {
            return;
        }
        
        try {
            await callback();
        } catch (error) {
            console.error('自动刷新失败:', error);
        }
    };

    const start = () => {
        stop();
        
        if (immediate) {
            refresh();
        }
        
        timer.value = setInterval(refresh, interval);
        isRunning.value = true;
    };

    const stop = () => {
        if (timer.value) {
            clearInterval(timer.value);
            timer.value = null;
            isRunning.value = false;
        }
    };

    onBeforeUnmount(() => {
        stop();
    });

    return {
        isRunning,
        start,
        stop
    };
}
