<script setup>
import { ref, watch, onBeforeUnmount, nextTick } from 'vue';
import api from '../api.js';

const props = defineProps({
    stocks: Array,
    loading: Boolean,
    category: String
});

const emit = defineEmits(['refresh-prices', 'analyze', 'filter']);

const expandedRow = ref(null);
const klineData = ref(null);
const klineLoading = ref(false);
const localAutoRefresh = ref(false);
const refreshTimer = ref(null);
const refreshInterval = ref(1);
const filterModalVisible = ref(false);
const filters = ref({
    minPrice: '',
    maxPrice: '',
    minChangePct: '',
    maxChangePct: '',
    minVolume: '',
    maxVolume: ''
});

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

const toggleRow = async (stock) => {
    if (expandedRow.value === stock.code) {
        expandedRow.value = null;
        klineData.value = null;
    } else {
        expandedRow.value = stock.code;
        klineLoading.value = true;
        klineData.value = null;
        try {
            const data = await api.getKlineData(stock.code);
            if (data.success) {
                klineData.value = data.data;
                console.log('K线数据:', data.data);
                // 使用requestAnimationFrame确保DOM完全更新
                requestAnimationFrame(() => {
                    renderKlineChart(stock);
                });
            } else {
                console.error('获取K线数据失败:', data.error);
            }
        } catch (error) {
            console.error('加载K线数据失败:', error);
        }
        klineLoading.value = false;
    }
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

const renderKlineChart = (stock) => {
    if (!klineData.value || !klineData.value.kline || klineData.value.kline.length === 0) {
        console.log('没有K线数据');
        return;
    }
    
    const container = document.getElementById(`kline-${stock.code}`);
    if (!container) {
        console.log('容器不存在:', `kline-${stock.code}`);
        return;
    }
    
    console.log('容器宽度:', container.clientWidth);
    
    container.innerHTML = '';
    
    const kline = klineData.value.kline;
    const kdj = klineData.value.kdj || [];
    const macd = klineData.value.macd || [];
    
    const width = container.clientWidth || 800;
    const chartHeight = 200;
    const indicatorHeight = 120;
    const indicatorGap = 25;
    
    // 计算各图表的基准Y位置
    const volBaseY = chartHeight + indicatorGap;
    const kdjBaseY = volBaseY + indicatorHeight + indicatorGap;
    const bollBaseY = kdjBaseY + indicatorHeight + indicatorGap;
    
    // 计算BOLL数据供后续使用
    const calculateBollData = (data, period = 20, multiplier = 2) => {
        const closes = data.map(d => parseFloat(d.close));
        const boll = [];
        for (let i = period - 1; i < data.length; i++) {
            const slice = closes.slice(i - period + 1, i + 1);
            const ma = slice.reduce((sum, price) => sum + price, 0) / period;
            const variance = slice.reduce((sum, price) => sum + Math.pow(price - ma, 2), 0) / period;
            const stdDev = Math.sqrt(variance);
            const upper = ma + multiplier * stdDev;
            const lower = ma - multiplier * stdDev;
            boll.push({ ma, upper, lower });
        }
        return boll;
    };
    const bollData = calculateBollData(kline);
    
    const height = chartHeight + indicatorGap + indicatorHeight + indicatorGap + indicatorHeight + indicatorGap + indicatorHeight + indicatorGap + indicatorHeight;
    
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    svg.setAttribute('class', 'kline-chart');
    
    const prices = kline.map(d => [d.high, d.low]).flat();
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice || 1;
    
    const volumes = kline.map(d => d.volume);
    const maxVolume = Math.max(...volumes) || 1;
    
    const barWidth = (width - 60) / kline.length;
    
    const bgColor = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bgColor.setAttribute('width', width);
    bgColor.setAttribute('height', height);
    bgColor.setAttribute('fill', '#1a1a2e');
    svg.appendChild(bgColor);
    
    // 绘制坐标轴
    // X轴（时间轴）
    const xAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    xAxis.setAttribute('x1', '30');
    xAxis.setAttribute('y1', chartHeight + 10);
    xAxis.setAttribute('x2', width - 10);
    xAxis.setAttribute('y2', chartHeight + 10);
    xAxis.setAttribute('stroke', '#64748b');
    xAxis.setAttribute('stroke-width', '1');
    svg.appendChild(xAxis);
    
    // Y轴（价格轴）
    const yAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    yAxis.setAttribute('x1', '30');
    yAxis.setAttribute('y1', '10');
    yAxis.setAttribute('x2', '30');
    yAxis.setAttribute('y2', chartHeight + 10);
    yAxis.setAttribute('stroke', '#64748b');
    yAxis.setAttribute('stroke-width', '1');
    svg.appendChild(yAxis);
    
    // 成交量X轴
    const volumeXAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    volumeXAxis.setAttribute('x1', '30');
    volumeXAxis.setAttribute('y1', chartHeight + indicatorGap + indicatorHeight);
    volumeXAxis.setAttribute('x2', width - 10);
    volumeXAxis.setAttribute('y2', chartHeight + indicatorGap + indicatorHeight);
    volumeXAxis.setAttribute('stroke', '#64748b');
    volumeXAxis.setAttribute('stroke-width', '1');
    svg.appendChild(volumeXAxis);
    
    // 成交量Y轴
    const volumeYAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    volumeYAxis.setAttribute('x1', '30');
    volumeYAxis.setAttribute('y1', chartHeight + indicatorGap);
    volumeYAxis.setAttribute('x2', '30');
    volumeYAxis.setAttribute('y2', chartHeight + indicatorGap + indicatorHeight);
    volumeYAxis.setAttribute('stroke', '#64748b');
    volumeYAxis.setAttribute('stroke-width', '1');
    svg.appendChild(volumeYAxis);
    
    // KDJ X轴
    const kdjXAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    kdjXAxis.setAttribute('x1', '30');
    kdjXAxis.setAttribute('y1', chartHeight + indicatorGap * 2 + indicatorHeight * 2);
    kdjXAxis.setAttribute('x2', width - 10);
    kdjXAxis.setAttribute('y2', chartHeight + indicatorGap * 2 + indicatorHeight * 2);
    kdjXAxis.setAttribute('stroke', '#64748b');
    kdjXAxis.setAttribute('stroke-width', '1');
    svg.appendChild(kdjXAxis);
    
    // KDJ Y轴
    const kdjYAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    kdjYAxis.setAttribute('x1', '30');
    kdjYAxis.setAttribute('y1', chartHeight + indicatorGap * 2 + indicatorHeight);
    kdjYAxis.setAttribute('x2', '30');
    kdjYAxis.setAttribute('y2', chartHeight + indicatorGap * 2 + indicatorHeight * 2);
    kdjYAxis.setAttribute('stroke', '#64748b');
    kdjYAxis.setAttribute('stroke-width', '1');
    svg.appendChild(kdjYAxis);
    
    // MACD X轴
    const macdXAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    macdXAxis.setAttribute('x1', '30');
    macdXAxis.setAttribute('y1', chartHeight + indicatorGap * 3 + indicatorHeight * 3);
    macdXAxis.setAttribute('x2', width - 10);
    macdXAxis.setAttribute('y2', chartHeight + indicatorGap * 3 + indicatorHeight * 3);
    macdXAxis.setAttribute('stroke', '#64748b');
    macdXAxis.setAttribute('stroke-width', '1');
    svg.appendChild(macdXAxis);
    
    // MACD Y轴
    const macdYAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    macdYAxis.setAttribute('x1', '30');
    macdYAxis.setAttribute('y1', chartHeight + indicatorGap * 3 + indicatorHeight * 2);
    macdYAxis.setAttribute('x2', '30');
    macdYAxis.setAttribute('y2', chartHeight + indicatorGap * 3 + indicatorHeight * 3);
    macdYAxis.setAttribute('stroke', '#64748b');
    macdYAxis.setAttribute('stroke-width', '1');
    svg.appendChild(macdYAxis);
    
    // 绘制网格线
    // 价格网格线
    for (let i = 0; i <= 5; i++) {
        const y = 10 + (chartHeight / 5) * i;
        const gridLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        gridLine.setAttribute('x1', '30');
        gridLine.setAttribute('y1', y);
        gridLine.setAttribute('x2', width - 10);
        gridLine.setAttribute('y2', y);
        gridLine.setAttribute('stroke', '#334155');
        gridLine.setAttribute('stroke-width', '0.5');
        gridLine.setAttribute('stroke-dasharray', '2,2');
        svg.appendChild(gridLine);
    }
    
    // 时间网格线
    for (let i = 0; i <= kline.length; i += 5) {
        if (i < kline.length) {
            const x = 30 + i * barWidth + barWidth / 2;
            const gridLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            gridLine.setAttribute('x1', x);
            gridLine.setAttribute('y1', '10');
            gridLine.setAttribute('x2', x);
            gridLine.setAttribute('y2', chartHeight + 190);
            gridLine.setAttribute('stroke', '#334155');
            gridLine.setAttribute('stroke-width', '0.5');
            gridLine.setAttribute('stroke-dasharray', '2,2');
            svg.appendChild(gridLine);
        }
    }
    
    // 绘制价格标签
    for (let i = 0; i <= 5; i++) {
        const price = maxPrice - (priceRange / 5) * i;
        const y = 10 + (chartHeight / 5) * i;
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', '25');
        text.setAttribute('y', y + 4);
        text.setAttribute('fill', '#94a3b8');
        text.setAttribute('font-size', '8');
        text.setAttribute('text-anchor', 'end');
        text.textContent = price.toFixed(2);
        svg.appendChild(text);
    }
    
    // 绘制时间标签
    for (let i = 0; i < kline.length; i += 10) {
        const date = kline[i].date;
        const x = 30 + i * barWidth + barWidth / 2;
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', x);
        text.setAttribute('y', chartHeight + 15);
        text.setAttribute('fill', '#94a3b8');
        text.setAttribute('font-size', '8');
        text.setAttribute('text-anchor', 'middle');
        text.textContent = date.slice(4);
        svg.appendChild(text);
    }
    
    kline.forEach((d, i) => {
        const x = 30 + i * barWidth + barWidth / 2;
        const isUp = d.close >= d.open;
        const color = isUp ? '#ef4444' : '#10b981';
        
        const highY = chartHeight - ((d.high - minPrice) / priceRange) * chartHeight + 10;
        const lowY = chartHeight - ((d.low - minPrice) / priceRange) * chartHeight + 10;
        const openY = chartHeight - ((d.open - minPrice) / priceRange) * chartHeight + 10;
        const closeY = chartHeight - ((d.close - minPrice) / priceRange) * chartHeight + 10;
        
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x);
        line.setAttribute('y1', highY);
        line.setAttribute('x2', x);
        line.setAttribute('y2', lowY);
        line.setAttribute('stroke', color);
        line.setAttribute('stroke-width', '1');
        svg.appendChild(line);
        
        const body = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        const bodyTop = Math.min(openY, closeY);
        const bodyHeight = Math.abs(closeY - openY) || 1;
        body.setAttribute('x', x - barWidth * 0.4);
        body.setAttribute('y', bodyTop);
        body.setAttribute('width', barWidth * 0.8);
        body.setAttribute('height', bodyHeight);
        body.setAttribute('fill', color);
        svg.appendChild(body);
        
        const volHeight = (d.volume / maxVolume) * indicatorHeight;
        const volRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        volRect.setAttribute('x', x - barWidth * 0.4);
        volRect.setAttribute('y', chartHeight + indicatorGap + indicatorHeight - volHeight);
        volRect.setAttribute('width', barWidth * 0.8);
        volRect.setAttribute('height', volHeight);
        volRect.setAttribute('fill', color);
        volRect.setAttribute('opacity', '0.5');
        svg.appendChild(volRect);
        
        // 添加成交量数字显示
        const volText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        volText.setAttribute('x', x);
        volText.setAttribute('y', chartHeight + indicatorGap + indicatorHeight - volHeight - 5);
        volText.setAttribute('fill', color);
        volText.setAttribute('font-size', '6');
        volText.setAttribute('text-anchor', 'middle');
        volText.textContent = (d.volume / 10000).toFixed(1) + '万';
        svg.appendChild(volText);
    });
    
    // 绘制成交量Y轴数值
    for (let i = 0; i <= 5; i++) {
        const value = maxVolume - (maxVolume / 5) * i;
        const y = chartHeight + indicatorGap + (indicatorHeight - ((value / maxVolume) * indicatorHeight));
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', '25');
        text.setAttribute('y', y + 4);
        text.setAttribute('fill', '#94a3b8');
        text.setAttribute('font-size', '8');
        text.setAttribute('text-anchor', 'end');
        text.textContent = (value / 10000).toFixed(1) + '万';
        svg.appendChild(text);
    }
    
    // 绘制BOLL指标图表
    if (bollData.length > 0) {
        // BOLL显示在KDJ下方
        
        // 绘制BOLL X轴
        const bollXAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        bollXAxis.setAttribute('x1', '30');
        bollXAxis.setAttribute('y1', bollBaseY + indicatorHeight);
        bollXAxis.setAttribute('x2', width - 10);
        bollXAxis.setAttribute('y2', bollBaseY + indicatorHeight);
        bollXAxis.setAttribute('stroke', '#64748b');
        bollXAxis.setAttribute('stroke-width', '1');
        svg.appendChild(bollXAxis);
        
        // 绘制BOLL Y轴
        const bollYAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        bollYAxis.setAttribute('x1', '30');
        bollYAxis.setAttribute('y1', bollBaseY);
        bollYAxis.setAttribute('x2', '30');
        bollYAxis.setAttribute('y2', bollBaseY + indicatorHeight);
        bollYAxis.setAttribute('stroke', '#64748b');
        bollYAxis.setAttribute('stroke-width', '1');
        svg.appendChild(bollYAxis);
        
        // 计算BOLL价格范围
        const bollPrices = bollData.flatMap(d => [d.ma, d.upper, d.lower]);
        const minBollPrice = Math.min(...bollPrices);
        const maxBollPrice = Math.max(...bollPrices);
        const bollPriceRange = maxBollPrice - minBollPrice || 1;
        
        // 绘制BOLL Y轴数值
        for (let i = 0; i <= 5; i++) {
            const value = maxBollPrice - (bollPriceRange / 5) * i;
            const y = bollBaseY + (indicatorHeight - ((value - minBollPrice) / bollPriceRange) * indicatorHeight);
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', '25');
            text.setAttribute('y', y + 4);
            text.setAttribute('fill', '#94a3b8');
            text.setAttribute('font-size', '8');
            text.setAttribute('text-anchor', 'end');
            text.textContent = value.toFixed(2);
            svg.appendChild(text);
        }
        
        // 绘制BOLL线
        const createBollPath = (values, color, width = '1') => {
            let path = '';
            values.forEach((v, i) => {
                const x = 30 + (i + kline.length - bollData.length) * barWidth + barWidth / 2;
                const y = bollBaseY + (indicatorHeight - ((v - minBollPrice) / bollPriceRange) * indicatorHeight);
                path += (i === 0 ? 'M' : 'L') + `${x},${y}`;
            });
            const pathEl = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            pathEl.setAttribute('d', path);
            pathEl.setAttribute('stroke', color);
            pathEl.setAttribute('stroke-width', width);
            pathEl.setAttribute('fill', 'none');
            return pathEl;
        };
        
        const maValues = bollData.map(d => d.ma);
        const upperValues = bollData.map(d => d.upper);
        const lowerValues = bollData.map(d => d.lower);
        
        svg.appendChild(createBollPath(maValues, '#3b82f6', '1.5'));
        svg.appendChild(createBollPath(upperValues, '#10b981', '1'));
        svg.appendChild(createBollPath(lowerValues, '#ef4444', '1'));
        
        // 添加BOLL图例
        const bollLegend = [
            { color: '#3b82f6', text: 'BOLL中轨' },
            { color: '#10b981', text: 'BOLL上轨' },
            { color: '#ef4444', text: 'BOLL下轨' }
        ];
        
        bollLegend.forEach((item, index) => {
            const legendX = width - 80 - index * 60;
            const legendY = bollBaseY + indicatorHeight - 5;
            
            // 绘制颜色块
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', legendX);
            rect.setAttribute('y', legendY - 4);
            rect.setAttribute('width', '8');
            rect.setAttribute('height', '8');
            rect.setAttribute('fill', item.color);
            svg.appendChild(rect);
            
            // 绘制文字
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', legendX + 12);
            text.setAttribute('y', legendY + 3);
            text.setAttribute('fill', '#94a3b8');
            text.setAttribute('font-size', '8');
            text.textContent = item.text;
            svg.appendChild(text);
        });
    }
    
    if (kdj.length > 0) {
        const kdjG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        const kValues = kdj.map(d => d.k);
        const dValues = kdj.map(d => d.d);
        const jValues = kdj.map(d => d.j);
        // 计算实际的KDJ值范围
        const allKdjValues = [...kValues, ...dValues, ...jValues];
        const maxKdj = Math.max(...allKdjValues) || 100;
        const minKdj = Math.min(...allKdjValues) || 0;
        
        // KDJ显示在成交量下方
        
        // 绘制KDJ Y轴数值
        const kdjRange = maxKdj - minKdj || 1;
        for (let i = 0; i <= 5; i++) {
            const value = maxKdj - (kdjRange / 5) * i;
            const y = kdjBaseY + (maxKdj - value) / kdjRange * indicatorHeight;
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', '25');
            text.setAttribute('y', y + 4);
            text.setAttribute('fill', '#94a3b8');
            text.setAttribute('font-size', '8');
            text.setAttribute('text-anchor', 'end');
            text.textContent = value.toFixed(0);
            svg.appendChild(text);
        }
        
        const createPath = (values, color) => {
            let path = '';
            values.forEach((v, i) => {
                const x = 30 + i * barWidth + barWidth / 2;
                const y = kdjBaseY + (maxKdj - v) / kdjRange * indicatorHeight;
                path += (i === 0 ? 'M' : 'L') + `${x},${y}`;
            });
            const pathEl = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            pathEl.setAttribute('d', path);
            pathEl.setAttribute('stroke', color);
            pathEl.setAttribute('stroke-width', '1');
            pathEl.setAttribute('fill', 'none');
            return pathEl;
        };
        
        kdjG.appendChild(createPath(kValues, '#f59e0b'));
        kdjG.appendChild(createPath(dValues, '#3b82f6'));
        kdjG.appendChild(createPath(jValues, '#ec4899'));
        svg.appendChild(kdjG);
        
        // 检测并绘制KDJ金叉和死叉
        const detectCrossovers = (k, d) => {
            const crossovers = [];
            for (let i = 1; i < k.length; i++) {
                if (k[i-1] < d[i-1] && k[i] > d[i]) {
                    // 金叉发生在i-1和i之间，计算交点价格
                    const price = (k[i] + d[i]) / 2;
                    crossovers.push({ type: 'golden', index: i - 0.5, price: price });
                } else if (k[i-1] > d[i-1] && k[i] < d[i]) {
                    // 死叉发生在i-1和i之间，计算交点价格
                    const price = (k[i] + d[i]) / 2;
                    crossovers.push({ type: 'death', index: i - 0.5, price: price });
                }
            }
            return crossovers;
        };
        
        // 检测并绘制KDJ背离
        const detectDivergences = (prices, k, d) => {
            const divergences = [];
            const closes = prices.map(p => parseFloat(p.close));
            
            // 检测顶背离
            for (let i = 3; i < closes.length; i++) {
                if (closes[i] > closes[i-2] && closes[i-1] > closes[i-3] && 
                    k[i] < k[i-2] && k[i-1] < k[i-3]) {
                    divergences.push({ type: 'top', index: i, price: (k[i] + d[i]) / 2 });
                }
            }
            
            // 检测底背离
            for (let i = 3; i < closes.length; i++) {
                if (closes[i] < closes[i-2] && closes[i-1] < closes[i-3] && 
                    k[i] > k[i-2] && k[i-1] > k[i-3]) {
                    divergences.push({ type: 'bottom', index: i, price: (k[i] + d[i]) / 2 });
                }
            }
            
            return divergences;
        };
        
        // 绘制标记
        const drawMarkers = (markers) => {
            markers.forEach(marker => {
                const x = 30 + marker.index * barWidth + barWidth / 2;
                const y = kdjBaseY + (maxKdj - marker.price) / kdjRange * indicatorHeight;
                
                let color, text;
                switch (marker.type) {
                    case 'golden':
                        color = '#10b981';
                        text = '金叉';
                        break;
                    case 'death':
                        color = '#ef4444';
                        text = '死叉';
                        break;
                    case 'top':
                        color = '#f59e0b';
                        text = '顶背离';
                        break;
                    case 'bottom':
                        color = '#3b82f6';
                        text = '底背离';
                        break;
                }
                
                // 绘制标记点
                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', x);
                circle.setAttribute('cy', y);
                circle.setAttribute('r', '4');
                circle.setAttribute('fill', color);
                circle.setAttribute('stroke', '#ffffff');
                circle.setAttribute('stroke-width', '1');
                svg.appendChild(circle);
                
                // 绘制文字
                const textEl = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                textEl.setAttribute('x', x + 8);
                textEl.setAttribute('y', y + 3);
                textEl.setAttribute('fill', color);
                textEl.setAttribute('font-size', '8');
                textEl.textContent = text;
                svg.appendChild(textEl);
            });
        };
        
        // 检测并绘制KDJ信号
        const crossovers = detectCrossovers(kValues, dValues);
        const divergences = detectDivergences(kline, kValues, dValues);
        drawMarkers([...crossovers, ...divergences]);
        
        // 绘制KDJ X轴
        const kdjXAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        kdjXAxis.setAttribute('x1', '30');
        kdjXAxis.setAttribute('y1', kdjBaseY + indicatorHeight);
        kdjXAxis.setAttribute('x2', width - 10);
        kdjXAxis.setAttribute('y2', kdjBaseY + indicatorHeight);
        kdjXAxis.setAttribute('stroke', '#64748b');
        kdjXAxis.setAttribute('stroke-width', '1');
        svg.appendChild(kdjXAxis);
        
        // 绘制KDJ Y轴
        const kdjYAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        kdjYAxis.setAttribute('x1', '30');
        kdjYAxis.setAttribute('y1', kdjBaseY);
        kdjYAxis.setAttribute('x2', '30');
        kdjYAxis.setAttribute('y2', kdjBaseY + indicatorHeight);
        kdjYAxis.setAttribute('stroke', '#64748b');
        kdjYAxis.setAttribute('stroke-width', '1');
        svg.appendChild(kdjYAxis);
        
        // 添加KDJ图例
        const kdjLegend = [
            { color: '#f59e0b', text: 'K' },
            { color: '#3b82f6', text: 'D' },
            { color: '#ec4899', text: 'J' }
        ];
        
        kdjLegend.forEach((item, index) => {
            const legendX = width - 80 - index * 60;
            const legendY = kdjBaseY + indicatorHeight - 5;
            
            // 绘制颜色块
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', legendX);
            rect.setAttribute('y', legendY - 4);
            rect.setAttribute('width', '8');
            rect.setAttribute('height', '8');
            rect.setAttribute('fill', item.color);
            svg.appendChild(rect);
            
            // 绘制文字
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', legendX + 12);
            text.setAttribute('y', legendY + 3);
            text.setAttribute('fill', '#94a3b8');
            text.setAttribute('font-size', '8');
            text.textContent = item.text;
            svg.appendChild(text);
        });
    }
    
    // 绘制标签和数值
    const drawLabel = (y, title, values, colors) => {
        // 绘制标题
        const titleText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        titleText.setAttribute('x', 5);
        titleText.setAttribute('y', y);
        titleText.setAttribute('fill', '#e2e8f0');
        titleText.setAttribute('font-size', '11');
        titleText.setAttribute('font-weight', 'bold');
        titleText.textContent = title;
        svg.appendChild(titleText);
        
        // 绘制数值
        if (values && values.length > 0) {
            let xOffset = 5 + title.length * 11 + 20;
            values.forEach((val, idx) => {
                const valText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                valText.setAttribute('x', xOffset);
                valText.setAttribute('y', y);
                valText.setAttribute('fill', colors[idx] || '#94a3b8');
                valText.setAttribute('font-size', '10');
                valText.textContent = val;
                svg.appendChild(valText);
                xOffset += val.length * 10 + 15;
            });
        }
    };
    
    // 获取最新数据
    const latestKline = kline[kline.length - 1];
    const latestKdj = kdj[kdj.length - 1];
    const latestBoll = bollData[bollData.length - 1];
    
    // K线图标签 - 显示最新价格
    drawLabel(15, `K线图 - ${stock.name}`, [
        `最新: ${parseFloat(latestKline.close).toFixed(2)}`,
        `涨跌幅: ${((parseFloat(latestKline.close) - parseFloat(latestKline.open)) / parseFloat(latestKline.open) * 100).toFixed(2)}%`
    ], ['#f59e0b', parseFloat(latestKline.close) >= parseFloat(latestKline.open) ? '#ef4444' : '#10b981']);
    
    // 成交量标签 - 显示最新成交量
    drawLabel(volBaseY - 10, '成交量', [
        `最新: ${(latestKline.volume / 10000).toFixed(2)}万`
    ], ['#3b82f6']);
    
    // KDJ标签 - 显示最新KDJ值
    if (latestKdj) {
        drawLabel(kdjBaseY - 10, 'KDJ', [
            `K: ${latestKdj.k.toFixed(2)}`,
            `D: ${latestKdj.d.toFixed(2)}`,
            `J: ${latestKdj.j.toFixed(2)}`
        ], ['#f59e0b', '#3b82f6', '#ec4899']);
    } else {
        drawLabel(kdjBaseY - 10, 'KDJ', [], []);
    }
    
    // BOLL标签 - 显示最新BOLL值
    if (latestBoll) {
        drawLabel(bollBaseY - 10, 'BOLL', [
            `上轨: ${latestBoll.upper.toFixed(2)}`,
            `中轨: ${latestBoll.ma.toFixed(2)}`,
            `下轨: ${latestBoll.lower.toFixed(2)}`
        ], ['#10b981', '#3b82f6', '#ef4444']);
    } else {
        drawLabel(bollBaseY - 10, 'BOLL', [], []);
    }
    
    container.appendChild(svg);
    console.log('K线图绘制完成');
};

const formatChange = (change) => {
    const value = parseFloat(change);
    if (isNaN(value)) return '-';
    return value > 0 ? `+${value.toFixed(2)}` : value.toFixed(2);
};

const formatChangePct = (change_pct) => {
    const value = parseFloat(change_pct);
    if (isNaN(value)) return '-';
    return value > 0 ? `+${value.toFixed(2)}%` : `${value.toFixed(2)}%`;
};

const getMarketType = (code) => {
    if (code.startsWith('6')) return '沪';
    if (code.startsWith('000')) return '深';
    if (code.startsWith('002')) return '深';
    if (code.startsWith('300')) return '创业';
    if (code.startsWith('688')) return '科创';
    if (code.startsWith('8') || code.startsWith('4')) return '北交';
    return '';
};

const getMarketClass = (code) => {
    if (code.startsWith('6')) return 'market-sh';
    if (code.startsWith('000') || code.startsWith('002')) return 'market-sz';
    if (code.startsWith('300')) return 'market-cy';
    if (code.startsWith('688')) return 'market-kc';
    if (code.startsWith('8') || code.startsWith('4')) return 'market-bj';
    return '';
};

const formatVolume = (volume) => {
    return parseFloat(volume).toFixed(4);
};

const formatAmount = (amount) => {
    return parseFloat(amount).toFixed(4);
};

const analyzeStock = (stock) => {
    emit('analyze', stock);
};

const openFilterModal = () => {
    filterModalVisible.value = true;
};

const applyFilters = () => {
    emit('filter', filters.value);
    filterModalVisible.value = false;
};

const resetFilters = () => {
    filters.value = {
        minPrice: '',
        maxPrice: '',
        minChangePct: '',
        maxChangePct: '',
        minVolume: '',
        maxVolume: ''
    };
};

const closeFilterModal = () => {
    filterModalVisible.value = false;
};
</script>

<template>
    <div class="stock-table-container">
        <div class="table-header">
            <div class="header-left d-flex align-items-center">
                <h3 class="mb-0">{{ category || '股票列表' }}</h3>
                <button class="btn btn-sm btn-outline-primary ms-3" @click="openFilterModal">
                    手动筛选
                </button>
            </div>
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
        <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>加载中...</p>
        </div>
        <div v-else-if="stocks && stocks.length > 0" class="table-responsive">
            <table class="stock-table">
                <thead>
                    <tr>
                        <th>股票</th>
                        <th>最新价</th>
                        <th>涨跌幅</th>
                        <th>涨跌额</th>
                        <th>成交量(万)</th>
                        <th>成交额(亿)</th>
                        <th>市值(亿)</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <template v-for="stock in stocks" :key="stock.code">
                        <tr class="stock-row" @click="toggleRow(stock)">
                            <td>
                                <div class="stock-info">
                                    <span class="stock-name">{{ stock.name }}</span>
                                    <span :class="['stock-code', getMarketClass(stock.code)]">
                                        {{ stock.code }}<span class="market-type">{{ getMarketType(stock.code) }}</span>
                                    </span>
                                </div>
                            </td>
                            <td class="price">{{ stock.price }}</td>
                            <td :class="['change-pct', stock.change_pct >= 0 ? 'up' : 'down']">
                                {{ formatChangePct(stock.change_pct) }}
                            </td>
                            <td :class="['change', stock.change >= 0 ? 'up' : 'down']">
                                {{ formatChange(stock.change) }}
                            </td>
                            <td>{{ formatVolume(stock.volume) }}</td>
                            <td>{{ formatAmount(stock.amount) }}</td>
                            <td>{{ stock.market_cap ? parseFloat(stock.market_cap).toFixed(2) : '-' }}</td>
                            <td class="action">
                                <button class="btn btn-sm btn-primary" @click.stop="analyzeStock(stock)">
                                    AI分析
                                </button>
                            </td>
                        </tr>
                        <tr v-if="expandedRow === stock.code" class="expanded-row">
                            <td colspan="8">
                                <div class="kline-container">
                                    <div v-if="klineLoading" class="kline-loading">
                                        <div class="spinner"></div>
                                        <p>加载K线数据中...</p>
                                    </div>
                                    <div v-else-if="klineData" :id="`kline-${stock.code}`" class="kline-chart-container"></div>
                                    <div v-else class="kline-error">
                                        <p>无法加载K线数据</p>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </template>
                </tbody>
            </table>
        </div>
        <div v-else class="no-data">
            <p>暂无股票数据</p>
        </div>
        
        <!-- 筛选弹窗 -->
        <div v-if="filterModalVisible" class="modal-overlay" @click.self="closeFilterModal">
            <div class="filter-modal">
                <div class="modal-header">
                    <h4>股票筛选</h4>
                    <button class="close-btn" @click="closeFilterModal">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="filter-form">
                        <div class="form-group">
                            <label>价格范围</label>
                            <div class="d-flex">
                                <input type="number" v-model.number="filters.minPrice" class="form-control" placeholder="最低价格">
                                <span class="mx-2">至</span>
                                <input type="number" v-model.number="filters.maxPrice" class="form-control" placeholder="最高价格">
                            </div>
                        </div>
                        <div class="form-group">
                            <label>涨跌幅范围(%)</label>
                            <div class="d-flex">
                                <input type="number" v-model.number="filters.minChangePct" class="form-control" placeholder="最低涨跌幅">
                                <span class="mx-2">至</span>
                                <input type="number" v-model.number="filters.maxChangePct" class="form-control" placeholder="最高涨跌幅">
                            </div>
                        </div>
                        <div class="form-group">
                            <label>成交量范围(万)</label>
                            <div class="d-flex">
                                <input type="number" v-model.number="filters.minVolume" class="form-control" placeholder="最低成交量">
                                <span class="mx-2">至</span>
                                <input type="number" v-model.number="filters.maxVolume" class="form-control" placeholder="最高成交量">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" @click="resetFilters">重置</button>
                    <button class="btn btn-primary" @click="applyFilters">应用</button>
                </div>
            </div>
        </div>
    </div>
</template>