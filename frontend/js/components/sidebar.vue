<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import _ from 'lodash';
import api from '../api.js';
import toast from '../utils/toast.js';

const emit = defineEmits(['navigate']);

const menuItems = ref([
    { id: 'leader', icon: 'bi-trophy', label: '龙头股筛选' },
    { id: 'search', icon: 'bi-search', label: '股票查询' },
    { id: 'portfolio', icon: 'bi-wallet2', label: '自选股' }
]);

const currentHash = ref(window.location.hash.slice(1) || '');

const handleHashChange = () => {
    currentHash.value = window.location.hash.slice(1) || '';
};

const showSettingsPanel = ref(false);
const activeSettingsTab = ref('model');
const selectedModel = ref('volcengine');
const DEFAULT_TEMPERATURE = 0.7;
const DEFAULT_MODEL_TOKENS = 1024;
const DEFAULT_MODEL_CONFIG = {
    apiUrl: '',
    apiKey: '',
    secretKey: '',
    model: '',
    temperature: DEFAULT_TEMPERATURE,
    maxTokens: DEFAULT_MODEL_TOKENS
};

// 统一的模型配置对象，包含API配置和模型参数
const modelConfigs = ref({});
const showApiKey = ref({});

// 修改跟踪标记
const isModelChanged = ref(false);
const isModelConfigChanged = ref(false);

// 模型测试相关状态
const testModelLoading = ref(false);
const testModelResult = ref(null);
const testModelError = ref(null);
const models = ref([]);
const settingsTabs = ref([
        { id: 'model', icon: 'bi-brain', label: '模型设置' },
        { id: 'data', icon: 'bi-database', label: '数据源' },
        { id: 'notify', icon: 'bi-bell', label: '通知设置' },
        { id: 'display', icon: 'bi-palette', label: '显示设置' },
        { id: 'about', icon: 'bi-info-circle', label: '关于' }
    ]);
const dataSettings = ref({
    autoRefresh: true,
    refreshInterval: 30,
    dataSource: 'eastmoney'
});
const notifySettings = ref({
    priceAlert: false,
    priceThreshold: 5,
    volumeAlert: false,
    volumeThreshold: 2,
    systemNotify: true
});
const displaySettings = ref({
    theme: 'dark',
    fontSize: 'medium',
    showKline: true
});

const getModelIcon = (modelId) => {
    const icons = {
        'volcengine': 'bi-lightning-charge',
        'openai': 'bi-robot',
        'claude': 'bi-chat-dots',
        'gemini': 'bi-stars',
        'qwen': 'bi-cpu',
        'ernie': 'bi-brain'
    };
    return icons[modelId] || 'bi-cpu';
};

const openSettingsPanel = async () => {
    showSettingsPanel.value = true;

    // 重置修改标记
    isModelChanged.value = false;
    isModelConfigChanged.value = false;

    // 加载当前激活的模型数据
    try {
        const response = await api.getActiveAISetting();
        if (response.success && response.data) {
            const activeModel = response.data;
            selectedModel.value = activeModel.modelId;
            // 后端返回的字段已经是驼峰形式，直接使用
            modelConfigs.value[activeModel.modelId] = {
                apiUrl: activeModel.apiUrl || '',
                apiKey: activeModel.apiKey || '',
                secretKey: activeModel.secretKey || '',
                model: activeModel.modelName || '',
                temperature: activeModel.temperature || DEFAULT_TEMPERATURE,
                maxTokens: activeModel.maxTokens || DEFAULT_MODEL_TOKENS
            };
        }
    } catch (error) {
        console.error('加载激活模型配置失败:', error);
    }
};

const closeSettingsPanel = () => {
    showSettingsPanel.value = false;
};

const selectSettingsTab = (tabId) => {
    activeSettingsTab.value = tabId;
};

const selectModel = async (modelId) => {
    selectedModel.value = modelId;
    isModelChanged.value = true; // 标记模型已切换

    // 从后端获取该模型的配置
    try {
        const response = await api.getAISetting(modelId);
        if (response.success && response.data) {
            const data = response.data;
            // 后端返回的字段已经是驼峰形式，直接使用
            modelConfigs.value[modelId] = {
                apiUrl: data.apiUrl || '',
                apiKey: data.apiKey || '',
                secretKey: data.secretKey || '',
                model: data.modelName || '',
                temperature: data.temperature || DEFAULT_TEMPERATURE,
                maxTokens: data.maxTokens || DEFAULT_MODEL_TOKENS
            };
        } else {
            // 如果后端没有该模型的配置，初始化空配置
            if (!modelConfigs.value[modelId]) {
                modelConfigs.value[modelId] = _.cloneDeep(DEFAULT_MODEL_CONFIG);
            }
        }
    } catch (error) {
        console.error('加载模型配置失败:', error);
        // 确保配置对象存在
        if (!modelConfigs.value[modelId]) {
            modelConfigs.value[modelId] = _.cloneDeep(DEFAULT_MODEL_CONFIG);
        }
    }
};

const toggleApiKeyVisibility = (modelId) => {
    showApiKey.value[modelId] = !showApiKey.value[modelId];
};

// 确保模型配置对象存在
const ensureModelConfig = (modelId) => {
    if (!modelConfigs.value[modelId]) {
        modelConfigs.value[modelId] = _.cloneDeep(DEFAULT_MODEL_CONFIG);
    }
    return modelConfigs.value[modelId];
};

// 计算属性：获取当前模型配置
const currentModelConfig = computed(() => {
    return ensureModelConfig(selectedModel.value);
});

// 模型测试方法
const testModel = async () => {
    try {
        testModelLoading.value = true;
        testModelResult.value = null;
        testModelError.value = null;

        const modelConfig = ensureModelConfig(selectedModel.value);
        
        // 验证配置
        if (!modelConfig.apiUrl || !modelConfig.apiKey || !modelConfig.model) {
            testModelError.value = '请填写完整的API配置';
            testModelLoading.value = false;
            return;
        }
        
        // 准备测试数据
        const testData = {
            model: selectedModel.value,
            params: {
                temperature: modelConfig.temperature,
                maxTokens: modelConfig.maxTokens
            },
            apiConfig: {
                apiUrl: modelConfig.apiUrl,
                apiKey: modelConfig.apiKey,
                secretKey: modelConfig.secretKey,
                model: modelConfig.model
            }
        };
        
        // 调用API测试模型
        const response = await api.testModel(testData);
        
        if (response.success) {
            testModelResult.value = response.data;
        } else {
            testModelError.value = response.error || '测试失败，请检查参数配置';
        }
    } catch (error) {
        testModelError.value = `测试失败: ${error.message}`;
    } finally {
        testModelLoading.value = false;
    }
};

const loadModelSettings = async () => {
    try {
        // 加载所有AI模型配置（从ai_settings表）
        const allSettingsResponse = await api.getAISettings();
        if (allSettingsResponse.success && allSettingsResponse.data) {
            const allSettings = allSettingsResponse.data;
            // 遍历所有模型配置并更新
            allSettings.forEach(setting => {
                // 后端返回的字段已经是驼峰形式，直接使用
                modelConfigs.value[setting.modelId] = {
                    apiUrl: setting.apiUrl || '',
                    apiKey: setting.apiKey || '',
                    secretKey: setting.secretKey || '',
                    model: setting.modelName || '',
                    temperature: setting.temperature || DEFAULT_TEMPERATURE,
                    maxTokens: setting.maxTokens || DEFAULT_MODEL_TOKENS
                };
            });
        }

        // 加载当前激活的模型配置
        const activeResponse = await api.getActiveAISetting();
        if (activeResponse.success && activeResponse.data) {
            const activeModel = activeResponse.data;
            selectedModel.value = activeModel.modelId || 'volcengine';
            // 后端返回的字段已经是驼峰形式，直接使用
            if (!modelConfigs.value[activeModel.modelId]) {
                modelConfigs.value[activeModel.modelId] = {
                    apiUrl: activeModel.apiUrl || '',
                    apiKey: activeModel.apiKey || '',
                    secretKey: activeModel.secretKey || '',
                    model: activeModel.modelName || '',
                    temperature: activeModel.temperature || DEFAULT_TEMPERATURE,
                    maxTokens: activeModel.maxTokens || DEFAULT_MODEL_TOKENS
                };
            }
        }

        // 加载模型列表
        const modelsResponse = await api.getAIModels();
        if (modelsResponse.success && modelsResponse.data) {
            models.value = modelsResponse.data;
        }

        // 确保当前选中模型的配置对象存在
        if (!modelConfigs.value[selectedModel.value]) {
            modelConfigs.value[selectedModel.value] = _.cloneDeep(DEFAULT_MODEL_CONFIG);
        }
    } catch (error) {
        console.error('加载模型设置失败:', error);
    }
};

const loadAllSettings = async () => {
    try {
        const response = await api.getSettings();
        if (response.success && response.data) {
            const settings = response.data;
            if (settings.dataSettings) {
                dataSettings.value = { ...dataSettings.value, ...settings.dataSettings };
            }
            if (settings.notifySettings) {
                notifySettings.value = { ...notifySettings.value, ...settings.notifySettings };
            }
            if (settings.displaySettings) {
                displaySettings.value = { ...displaySettings.value, ...settings.displaySettings };
            }
        }
    } catch (error) {
        console.error('加载设置失败:', error);
    }
};

const saveAllSettings = async () => {
    try {
        const promises = [];

        // 1. 如果切换了激活模型，更新settings表中的currentAiModel和ai_settings表的激活状态
        if (isModelChanged.value) {
            promises.push(api.setSetting('currentAiModel', selectedModel.value));
            promises.push(api.setActiveAIModel(selectedModel.value));
        }

        // 2. 如果模型配置有修改，更新ai_settings表
        if (isModelConfigChanged.value) {
            const currentConfig = ensureModelConfig(selectedModel.value);
            const updateData = {
                apiUrl: currentConfig.apiUrl,
                apiKey: currentConfig.apiKey,
                secretKey: currentConfig.secretKey,
                modelName: currentConfig.model,
                temperature: currentConfig.temperature,
                maxTokens: currentConfig.maxTokens
            };
            promises.push(api.updateAISetting(selectedModel.value, updateData));
        }

        // 4. 其他设置（dataSettings, notifySettings, displaySettings）
        // 这些设置改动较少，每次保存时都更新
        promises.push(api.setSetting('dataSettings', dataSettings.value));
        promises.push(api.setSetting('notifySettings', notifySettings.value));
        promises.push(api.setSetting('displaySettings', displaySettings.value));

        await Promise.all(promises);

        // 重置修改标记
        isModelChanged.value = false;
        isModelConfigChanged.value = false;

        toast.success('设置已保存');
    } catch (error) {
        console.error('保存设置失败:', error);
        toast.error('保存设置失败，请稍后重试: ' + error.message);
    }
};

onMounted(async () => {
    await loadModelSettings();
    await loadAllSettings();
    window.addEventListener('hashchange', handleHashChange);
});

onUnmounted(() => {
    window.removeEventListener('hashchange', handleHashChange);
});
</script>

<template>
    <div class="sidebar">
        <div class="sidebar-header">
            <h4 class="sidebar-title">
                <i class="bi bi-graph-up-arrow me-2"></i>智能选股
            </h4>
        </div>
        <nav class="sidebar-nav">
            <a 
                v-for="item in menuItems" 
                :key="item.id"
                class="nav-item"
                :class="{ active: currentHash === item.id }"
                @click="$emit('navigate', item.id)"
            >
                <i :class="'bi ' + item.icon + ' me-2'"></i>
                {{ item.label }}
            </a>
        </nav>
        <div class="sidebar-footer">
            <button 
                class="btn btn-outline-light w-100" 
                @click="openSettingsPanel"
            >
                <i class="bi bi-gear me-2"></i>设置
            </button>
        </div>
        
        <!-- 设置页面 -->
        <div v-if="showSettingsPanel" class="settings-page-overlay" @click.self="closeSettingsPanel">
            <div class="settings-page">
                <div class="settings-page-header">
                    <h3><i class="bi bi-gear me-2"></i>系统设置</h3>
                    <button class="close-btn" @click="closeSettingsPanel">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                
                <div class="settings-page-body">
                    <div class="settings-sidebar">
                        <a 
                            v-for="tab in settingsTabs" 
                            :key="tab.id"
                            class="settings-tab"
                            :class="{ active: activeSettingsTab === tab.id }"
                            @click="selectSettingsTab(tab.id)"
                        >
                            <i :class="'bi ' + tab.icon + ' me-2'"></i>
                            {{ tab.label }}
                        </a>
                    </div>
                    
                    <div class="settings-content">
                        <!-- 模型设置 -->
                        <div v-if="activeSettingsTab === 'model'" class="settings-section">
                            <h4 class="section-title">AI模型设置</h4>
                            <div class="model-grid">
                                <div 
                                    v-for="model in models" 
                                    :key="model.id"
                                    class="model-card"
                                    :class="{ 'selected': selectedModel === model.id }"
                                    @click="selectModel(model.id)"
                                >
                                    <div class="model-icon">
                                        <i :class="'bi ' + getModelIcon(model.id)"></i>
                                    </div>
                                    <div class="model-info">
                                        <h6>{{ model.name }}</h6>
                                        <p>{{ model.description }}</p>
                                    </div>
                                    <div class="model-check" v-if="selectedModel === model.id">
                                        <i class="bi bi-check-circle-fill"></i>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="params-section">
                                <h5 class="params-title">模型参数</h5>
                                <div class="param-item">
                                    <label>温度 (Temperature)</label>
                                    <div class="param-slider">
                                        <input
                                            type="range"
                                            v-model.number="currentModelConfig.temperature"
                                            min="0.1"
                                            max="1.0"
                                            step="0.1"
                                            @change="isModelConfigChanged = true"
                                        >
                                        <span class="param-value">{{ currentModelConfig.temperature }}</span>
                                    </div>
                                    <small class="param-hint">值越低输出越确定，值越高输出越随机</small>
                                </div>
                                <div class="param-item">
                                    <label>最大 Tokens</label>
                                    <input
                                            type="number"
                                            v-model.number="currentModelConfig.maxTokens"
                                            min="100"
                                            max="4096"
                                            @change="isModelConfigChanged = true"
                                        >
                                    <small class="param-hint">控制生成文本的最大长度</small>
                                </div>
                            </div>
                            
                            <div class="api-config-section">
                                <h5 class="params-title">
                                    <i class="bi bi-key me-2"></i>API 配置
                                    <span class="config-model-name">({{ models.find(m => m.id === selectedModel)?.name }})</span>
                                </h5>
                                <div class="api-config-card">
                                    <div class="api-config-item">
                                        <label>
                                            <i class="bi bi-link-45deg me-1"></i>API 地址
                                        </label>
                                        <input
                                            type="text"
                                            class="form-control"
                                            v-model="currentModelConfig.apiUrl"
                                            :placeholder="'例如: ' + models.find(m => m.id === selectedModel)?.defaultUrl"
                                            @change="isModelConfigChanged = true"
                                        >
                                        <small class="param-hint">模型的API服务地址</small>
                                    </div>
                                    <div class="api-config-item">
                                        <label>
                                            <i class="bi bi-key me-1"></i>API Key
                                        </label>
                                        <div class="api-key-input-group">
                                            <input
                                                :type="showApiKey[selectedModel] ? 'text' : 'password'"
                                                class="form-control"
                                                v-model="currentModelConfig.apiKey"
                                                placeholder="请输入您的 API Key"
                                                @change="isModelConfigChanged = true"
                                            >
                                            <button
                                                class="btn btn-outline-secondary"
                                                type="button"
                                                @click="toggleApiKeyVisibility(selectedModel)"
                                            >
                                                <i :class="showApiKey[selectedModel] ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                                            </button>
                                        </div>
                                        <small class="param-hint">您的API密钥，将安全存储在本地</small>
                                    </div>
                                    <div class="api-config-item">
                                        <label>
                                            <i class="bi bi-cpu me-1"></i>模型名称
                                        </label>
                                        <input
                                                type="text"
                                                class="form-control"
                                                v-model="currentModelConfig.model"
                                                :placeholder="'例如: ' + models.find(m => m.id === selectedModel)?.defaultModel"
                                                @change="isModelConfigChanged = true"
                                            >
                                        <small class="param-hint">具体使用的模型版本</small>
                                    </div>
                                    <div class="api-config-item">
                                        <label>
                                            <i class="bi bi-shield-lock me-1"></i>Secret Key (可选)
                                        </label>
                                        <div class="api-key-input-group">
                                            <input
                                                :type="showApiKey[selectedModel] ? 'text' : 'password'"
                                                class="form-control"
                                                v-model="currentModelConfig.secretKey"
                                                placeholder="请输入您的 Secret Key (如果需要)"
                                                @change="isModelConfigChanged = true"
                                            >
                                            <button
                                                class="btn btn-outline-secondary"
                                                type="button"
                                                @click="toggleApiKeyVisibility(selectedModel)"
                                            >
                                                <i :class="showApiKey[selectedModel] ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                                            </button>
                                        </div>
                                        <small class="param-hint">某些模型需要额外的 Secret Key</small>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 模型测试 -->
                            <div class="model-test-section">
                                <h5 class="params-title">
                                    <i class="bi bi-play-circle me-2"></i>模型测试
                                </h5>
                                <div class="model-test-card">
                                    <p class="test-hint">点击下方按钮测试模型配置是否正确</p>
                                    <button 
                                        class="btn btn-primary w-100" 
                                        @click="testModel"
                                        :disabled="testModelLoading"
                                    >
                                        <i v-if="testModelLoading" class="bi bi-spinner bi-spin me-2"></i>
                                        <span>{{ testModelLoading ? '测试中...' : '测试模型' }}</span>
                                    </button>
                                    
                                    <!-- 测试结果 -->
                                    <div v-if="testModelResult" class="test-result success">
                                        <div class="test-result-header">
                                            <i class="bi bi-check-circle-fill"></i>
                                            <h6>测试成功</h6>
                                        </div>
                                        <div class="test-result-content">
                                            <p>模型配置正确，可以正常使用</p>
                                            <div class="test-result-detail">
                                                <pre>{{ JSON.stringify(testModelResult, null, 2) }}</pre>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div v-if="testModelError" class="test-result error">
                                        <div class="test-result-header">
                                            <i class="bi bi-exclamation-circle-fill"></i>
                                            <h6>测试失败</h6>
                                        </div>
                                        <div class="test-result-content">
                                            <p>{{ testModelError }}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 数据源设置 -->
                        <div v-if="activeSettingsTab === 'data'" class="settings-section">
                            <h4 class="section-title">数据源设置</h4>
                            <div class="setting-item">
                                <div class="setting-label">
                                    <i class="bi bi-arrow-repeat me-2"></i>自动刷新
                                </div>
                                <div class="form-check form-switch">
                                    <input 
                                        type="checkbox" 
                                        class="form-check-input" 
                                        v-model="dataSettings.autoRefresh"
                                    >
                                </div>
                            </div>
                            <div class="setting-item" v-if="dataSettings.autoRefresh">
                                <div class="setting-label">
                                    <i class="bi bi-clock me-2"></i>刷新间隔（秒）
                                </div>
                                <input 
                                    type="number" 
                                    class="form-control setting-input"
                                    v-model.number="dataSettings.refreshInterval"
                                    min="10"
                                    max="300"
                                >
                            </div>
                            <div class="setting-item">
                                <div class="setting-label">
                                    <i class="bi bi-database me-2"></i>数据源
                                </div>
                                <select class="form-select setting-input" v-model="dataSettings.dataSource">
                                    <option value="eastmoney">东方财富</option>
                                    <option value="sina">新浪财经</option>
                                    <option value="tushare">Tushare</option>
                                </select>
                            </div>
                        </div>
                        
                        <!-- 通知设置 -->
                        <div v-if="activeSettingsTab === 'notify'" class="settings-section">
                            <h4 class="section-title">通知设置</h4>
                            <div class="setting-item">
                                <div class="setting-label">
                                    <i class="bi bi-graph-up me-2"></i>价格预警
                                </div>
                                <div class="form-check form-switch">
                                    <input 
                                        type="checkbox" 
                                        class="form-check-input" 
                                        v-model="notifySettings.priceAlert"
                                    >
                                </div>
                            </div>
                            <div class="setting-item" v-if="notifySettings.priceAlert">
                                <div class="setting-label">
                                    <i class="bi bi-percent me-2"></i>涨跌幅阈值（%）
                                </div>
                                <input 
                                    type="number" 
                                    class="form-control setting-input"
                                    v-model.number="notifySettings.priceThreshold"
                                    min="1"
                                    max="20"
                                >
                            </div>
                            <div class="setting-item">
                                <div class="setting-label">
                                    <i class="bi bi-bar-chart me-2"></i>量比预警
                                </div>
                                <div class="form-check form-switch">
                                    <input 
                                        type="checkbox" 
                                        class="form-check-input" 
                                        v-model="notifySettings.volumeAlert"
                                    >
                                </div>
                            </div>
                            <div class="setting-item">
                                <div class="setting-label">
                                    <i class="bi bi-bell me-2"></i>系统通知
                                </div>
                                <div class="form-check form-switch">
                                    <input 
                                        type="checkbox" 
                                        class="form-check-input" 
                                        v-model="notifySettings.systemNotify"
                                    >
                                </div>
                            </div>
                        </div>
                        
                        <!-- 显示设置 -->
                        <div v-if="activeSettingsTab === 'display'" class="settings-section">
                            <h4 class="section-title">显示设置</h4>
                            <div class="setting-item">
                                <div class="setting-label">
                                    <i class="bi bi-palette me-2"></i>主题
                                </div>
                                <select class="form-select setting-input" v-model="displaySettings.theme">
                                    <option value="dark">深色模式</option>
                                    <option value="light">浅色模式</option>
                                    <option value="auto">跟随系统</option>
                                </select>
                            </div>
                            <div class="setting-item">
                                <div class="setting-label">
                                    <i class="bi bi-type me-2"></i>字体大小
                                </div>
                                <select class="form-select setting-input" v-model="displaySettings.fontSize">
                                    <option value="small">小</option>
                                    <option value="medium">中</option>
                                    <option value="large">大</option>
                                </select>
                            </div>
                            <div class="setting-item">
                                <div class="setting-label">
                                    <i class="bi bi-graph-up-arrow me-2"></i>显示K线图
                                </div>
                                <div class="form-check form-switch">
                                    <input 
                                        type="checkbox" 
                                        class="form-check-input" 
                                        v-model="displaySettings.showKline"
                                    >
                                </div>
                            </div>
                        </div>
                        
                        <!-- 关于 -->
                        <div v-if="activeSettingsTab === 'about'" class="settings-section">
                            <h4 class="section-title">关于系统</h4>
                            <div class="about-content">
                                <div class="about-logo">
                                    <i class="bi bi-graph-up-arrow"></i>
                                </div>
                                <h3 class="about-title">智能选股系统</h3>
                                <p class="about-version">版本 1.0.0</p>
                                <div class="about-info">
                                    <div class="info-item">
                                        <i class="bi bi-code-slash me-2"></i>
                                        <span>基于 Python + Vue 开发</span>
                                    </div>
                                    <div class="info-item">
                                        <i class="bi bi-cpu me-2"></i>
                                        <span>集成 AI 智能分析</span>
                                    </div>
                                    <div class="info-item">
                                        <i class="bi bi-lightning me-2"></i>
                                        <span>实时股票数据更新</span>
                                    </div>
                                </div>
                                <p class="about-copyright">© 2026 智能选股系统</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="settings-page-footer">
                    <button class="btn btn-secondary" @click="closeSettingsPanel">取消</button>
                    <button class="btn btn-primary" @click="saveAllSettings">
                        <i class="bi bi-check me-1"></i>保存设置
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* 模型测试 */
.model-test-section {
    margin-top: 20px;
    margin-bottom: 30px;
}

.model-test-card {
    background-color: #2a2a3f;
    border-radius: 8px;
    padding: 20px;
}

.test-hint {
    margin-bottom: 15px;
    color: #b0b0b0;
    font-size: 14px;
}

.model-test-card button {
    margin-bottom: 20px;
}

.test-result {
    margin-top: 20px;
    padding: 15px;
    border-radius: 6px;
}

.test-result.success {
    background-color: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.test-result.error {
    background-color: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.test-result-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.test-result-header i {
    font-size: 18px;
    margin-right: 10px;
}

.test-result.success .test-result-header i {
    color: #10b981;
}

.test-result.error .test-result-header i {
    color: #ef4444;
}

.test-result-header h6 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
}

.test-result-content p {
    margin: 0 0 10px 0;
    color: #e0e0e0;
}

.test-result-detail {
    background-color: #1e1e2f;
    border-radius: 4px;
    padding: 10px;
    max-height: 200px;
    overflow-y: auto;
}

.test-result-detail pre {
    margin: 0;
    font-size: 12px;
    color: #a78bfa;
    white-space: pre-wrap;
    word-wrap: break-word;
}
</style>