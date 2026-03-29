/**
 * 前端安全工具类
 * 提供输入验证和XSS防护功能
 */

const security = {
    /**
     * 验证输入是否为空
     * @param {string} value - 要验证的值
     * @returns {boolean} 是否为空
     */
    isEmpty(value) {
        return value === null || value === undefined || value.trim() === '';
    },

    /**
     * 验证股票代码格式
     * @param {string} code - 股票代码
     * @returns {boolean} 是否有效
     */
    validateStockCode(code) {
        if (this.isEmpty(code)) return false;
        // 股票代码格式：数字或字母，长度4-10
        const regex = /^[A-Z0-9]{4,10}$/i;
        return regex.test(code);
    },

    /**
     * 验证URL格式
     * @param {string} url - URL地址
     * @returns {boolean} 是否有效
     */
    validateUrl(url) {
        if (this.isEmpty(url)) return false;
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    },

    /**
     * 验证API密钥格式
     * @param {string} key - API密钥
     * @returns {boolean} 是否有效
     */
    validateApiKey(key) {
        if (this.isEmpty(key)) return false;
        // API密钥通常是字母数字组合，长度10-50
        const regex = /^[A-Za-z0-9_-]{10,50}$/;
        return regex.test(key);
    },

    /**
     * 验证温度值（0-1之间）
     * @param {number} temperature - 温度值
     * @returns {boolean} 是否有效
     */
    validateTemperature(temperature) {
        const num = parseFloat(temperature);
        return !isNaN(num) && num >= 0 && num <= 1;
    },

    /**
     * 验证最大 tokens 值
     * @param {number} maxTokens - 最大 tokens 值
     * @returns {boolean} 是否有效
     */
    validateMaxTokens(maxTokens) {
        const num = parseInt(maxTokens);
        return !isNaN(num) && num > 0 && num <= 100000;
    },

    /**
     * 转义HTML特殊字符，防止XSS攻击
     * @param {string} html - 要转义的HTML字符串
     * @returns {string} 转义后的字符串
     */
    escapeHtml(html) {
        if (!html || typeof html !== 'string') return '';
        const escapeMap = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
            '/': '&#x2F;'
        };
        return html.replace(/[&<>"'/]/g, char => escapeMap[char]);
    },

    /**
     * 清理用户输入，防止XSS攻击
     * @param {string} input - 用户输入
     * @returns {string} 清理后的输入
     */
    sanitizeInput(input) {
        if (!input || typeof input !== 'string') return '';
        return this.escapeHtml(input);
    },

    /**
     * 验证搜索查询
     * @param {string} query - 搜索查询
     * @returns {boolean} 是否有效
     */
    validateSearchQuery(query) {
        if (this.isEmpty(query)) return false;
        // 搜索查询长度限制：1-50个字符
        const length = query.trim().length;
        return length >= 1 && length <= 50;
    },

    /**
     * 验证模型ID
     * @param {string} modelId - 模型ID
     * @returns {boolean} 是否有效
     */
    validateModelId(modelId) {
        if (this.isEmpty(modelId)) return false;
        // 模型ID格式：字母、数字、下划线，长度3-30
        const regex = /^[A-Za-z0-9_]{3,30}$/;
        return regex.test(modelId);
    },

    /**
     * 验证模型名称
     * @param {string} modelName - 模型名称
     * @returns {boolean} 是否有效
     */
    validateModelName(modelName) {
        if (this.isEmpty(modelName)) return false;
        // 模型名称长度限制：1-50个字符
        const length = modelName.trim().length;
        return length >= 1 && length <= 50;
    },

    /**
     * 验证整数
     * @param {number|string} value - 要验证的值
     * @returns {boolean} 是否为整数
     */
    isInteger(value) {
        return Number.isInteger(parseInt(value));
    },

    /**
     * 验证浮点数
     * @param {number|string} value - 要验证的值
     * @returns {boolean} 是否为浮点数
     */
    isFloat(value) {
        return !isNaN(parseFloat(value));
    },

    /**
     * 验证正整数
     * @param {number|string} value - 要验证的值
     * @returns {boolean} 是否为正整数
     */
    isPositiveInteger(value) {
        const num = parseInt(value);
        return Number.isInteger(num) && num > 0;
    },

    /**
     * 验证非负数
     * @param {number|string} value - 要验证的值
     * @returns {boolean} 是否为非负数
     */
    isNonNegative(value) {
        const num = parseFloat(value);
        return !isNaN(num) && num >= 0;
    },

    /**
     * 验证字符串长度
     * @param {string} value - 要验证的字符串
     * @param {number} min - 最小长度
     * @param {number} max - 最大长度
     * @returns {boolean} 是否在范围内
     */
    validateLength(value, min, max) {
        if (!value || typeof value !== 'string') return false;
        const length = value.trim().length;
        return length >= min && length <= max;
    },

    /**
     * 验证数组长度
     * @param {Array} array - 要验证的数组
     * @param {number} min - 最小长度
     * @param {number} max - 最大长度
     * @returns {boolean} 是否在范围内
     */
    validateArrayLength(array, min, max) {
        if (!Array.isArray(array)) return false;
        const length = array.length;
        return length >= min && length <= max;
    },

    /**
     * 清理对象中的所有字符串属性，防止XSS攻击
     * @param {Object} obj - 要清理的对象
     * @returns {Object} 清理后的对象
     */
    sanitizeObject(obj) {
        if (!obj || typeof obj !== 'object') return obj;
        
        const sanitized = {};
        for (const key in obj) {
            if (Object.prototype.hasOwnProperty.call(obj, key)) {
                const value = obj[key];
                if (typeof value === 'string') {
                    sanitized[key] = this.sanitizeInput(value);
                } else if (typeof value === 'object' && value !== null) {
                    sanitized[key] = this.sanitizeObject(value);
                } else {
                    sanitized[key] = value;
                }
            }
        }
        return sanitized;
    }
};

export default security;
