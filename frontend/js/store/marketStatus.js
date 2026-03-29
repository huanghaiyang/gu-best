import { ref, computed } from 'vue';

// 全局状态管理 - 市场状态
const isMarketOpen = ref(false);
const refreshTimer = ref(null);

// 检查是否处于开市时间
const checkMarketStatus = () => {
    const now = new Date();
    const dayOfWeek = now.getDay();
    const hour = now.getHours();
    const minute = now.getMinutes();
    
    // 周一到周五
    if (dayOfWeek < 1 || dayOfWeek > 5) {
        isMarketOpen.value = false;
        return false;
    }
    
    // 上午 9:30 - 11:30
    const isMorningSession = (hour === 9 && minute >= 30) || (hour === 10) || (hour === 11 && minute < 30);
    // 下午 13:00 - 15:00
    const isAfternoonSession = (hour === 13) || (hour === 14) || (hour === 15 && minute === 0);
    
    isMarketOpen.value = isMorningSession || isAfternoonSession;
    return isMarketOpen.value;
};

// 启动市场状态检查
const startMarketStatusCheck = () => {
    stopMarketStatusCheck();
    
    // 立即检查一次
    checkMarketStatus();
    
    // 然后每分钟检查一次
    refreshTimer.value = setInterval(checkMarketStatus, 60000);
};

// 停止市场状态检查
const stopMarketStatusCheck = () => {
    if (refreshTimer.value) {
        clearInterval(refreshTimer.value);
        refreshTimer.value = null;
    }
};

export {
    isMarketOpen,
    checkMarketStatus,
    startMarketStatusCheck,
    stopMarketStatusCheck
};
