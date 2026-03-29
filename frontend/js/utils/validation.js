/**
 * 表单验证工具
 * 提供常用表单验证功能
 */

import security from './security.js';

const validation = {
    /**
     * 验证AI模型设置表单
     * @param {Object} formData - 表单数据
     * @returns {Object} 验证结果 { isValid: boolean, errors: Object }
     */
    validateAISetting(formData) {
        const errors = {};
        
        // 验证模型ID
        if (!security.validateModelId(formData.modelId)) {
            errors.modelId = '模型ID格式不正确，仅允许字母、数字和下划线，长度3-30';
        }
        
        // 验证模型名称
        if (!security.validateModelName(formData.modelName)) {
            errors.modelName = '模型名称不能为空，长度1-50';
        }
        
        // 验证API URL
        if (!security.validateUrl(formData.apiUrl)) {
            errors.apiUrl = 'API URL格式不正确';
        }
        
        // 验证API Key（可选）
        if (formData.apiKey && !security.validateApiKey(formData.apiKey)) {
            errors.apiKey = 'API Key格式不正确';
        }
        
        // 验证温度值
        if (!security.validateTemperature(formData.temperature)) {
            errors.temperature = '温度值必须在0-1之间';
        }
        
        // 验证最大tokens
        if (!security.validateMaxTokens(formData.maxTokens)) {
            errors.maxTokens = '最大tokens必须是正整数，不超过100000';
        }
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    },

    /**
     * 验证搜索表单
     * @param {Object} formData - 表单数据
     * @returns {Object} 验证结果 { isValid: boolean, errors: Object }
     */
    validateSearchForm(formData) {
        const errors = {};
        
        // 验证搜索查询
        if (!security.validateSearchQuery(formData.query)) {
            errors.query = '搜索查询不能为空，长度1-50';
        }
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    },

    /**
     * 验证股票代码
     * @param {string} code - 股票代码
     * @returns {Object} 验证结果 { isValid: boolean, error: string }
     */
    validateStockCode(code) {
        if (!security.validateStockCode(code)) {
            return {
                isValid: false,
                error: '股票代码格式不正确，仅允许字母和数字，长度4-10'
            };
        }
        return {
            isValid: true,
            error: ''
        };
    },

    /**
     * 验证设置表单
     * @param {Object} formData - 表单数据
     * @returns {Object} 验证结果 { isValid: boolean, errors: Object }
     */
    validateSettingForm(formData) {
        const errors = {};
        
        // 验证key
        if (security.isEmpty(formData.key)) {
            errors.key = '设置键不能为空';
        } else if (!security.validateLength(formData.key, 1, 50)) {
            errors.key = '设置键长度必须在1-50之间';
        }
        
        // 验证value（可选）
        if (formData.value && typeof formData.value === 'string' && 
            !security.validateLength(formData.value, 0, 1000)) {
            errors.value = '设置值长度不能超过1000';
        }
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    },

    /**
     * 验证批量分析表单
     * @param {Object} formData - 表单数据
     * @returns {Object} 验证结果 { isValid: boolean, errors: Object }
     */
    validateBatchAnalyzeForm(formData) {
        const errors = {};
        
        // 验证股票列表
        if (!Array.isArray(formData.stocks)) {
            errors.stocks = '股票列表格式不正确';
        } else if (!security.validateArrayLength(formData.stocks, 1, 50)) {
            errors.stocks = '股票数量必须在1-50之间';
        } else {
            // 验证每个股票
            formData.stocks.forEach((stock, index) => {
                if (!stock.code || !security.validateStockCode(stock.code)) {
                    errors[`stocks[${index}].code`] = `第${index + 1}个股票代码格式不正确`;
                }
                if (!stock.name || !security.validateLength(stock.name, 1, 50)) {
                    errors[`stocks[${index}].name`] = `第${index + 1}个股票名称格式不正确`;
                }
            });
        }
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    },

    /**
     * 验证模型测试表单
     * @param {Object} formData - 表单数据
     * @returns {Object} 验证结果 { isValid: boolean, errors: Object }
     */
    validateModelTestForm(formData) {
        const errors = {};
        
        // 验证模型
        if (security.isEmpty(formData.model)) {
            errors.model = '模型不能为空';
        }
        
        // 验证API配置
        if (!formData.apiConfig) {
            errors.apiConfig = 'API配置不能为空';
        } else {
            if (!security.validateUrl(formData.apiConfig.apiUrl)) {
                errors['apiConfig.apiUrl'] = 'API URL格式不正确';
            }
            if (!security.validateApiKey(formData.apiConfig.apiKey)) {
                errors['apiConfig.apiKey'] = 'API Key格式不正确';
            }
            if (security.isEmpty(formData.apiConfig.model)) {
                errors['apiConfig.model'] = '模型名称不能为空';
            }
        }
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    },

    /**
     * 清理表单数据
     * @param {Object} formData - 表单数据
     * @returns {Object} 清理后的数据
     */
    sanitizeFormData(formData) {
        return security.sanitizeObject(formData);
    }
};

export default validation;
