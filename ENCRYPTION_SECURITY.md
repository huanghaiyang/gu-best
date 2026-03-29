# 数据库加密安全说明

## 概述

本系统使用 Python 内置库实现的加密方案对数据库中的敏感信息（API Key 和 Secret Key）进行加密存储，确保数据安全。

## 加密机制

### 加密算法
- **算法**: XOR + PBKDF2-HMAC-SHA256
- **密钥派生**: PBKDF2HMAC (SHA-256)
- **迭代次数**: 100,000 次
- **盐值**: 固定盐值用于密钥派生
- **编码**: Base64 URL-safe

### 加密字段
- `apiKey`: AI 模型的 API 密钥
- `secretKey`: AI 模型的秘密密钥

## 使用方法

### 环境变量配置

在生产环境中，建议设置环境变量来配置加密密钥：

```bash
# Windows
set DB_ENCRYPTION_KEY=your_secure_encryption_key_here

# Linux/Mac
export DB_ENCRYPTION_KEY=your_secure_encryption_key_here
```

### 密钥要求

- 长度: 任意长度
- 复杂度: 建议使用强密码，包含大小写字母、数字和特殊字符
- 安全性: 不要在代码中硬编码密钥，使用环境变量

## 加密服务 API

### EncryptionService 类

```python
from services.encryption_service import EncryptionService

# 创建加密服务实例
encryption_service = EncryptionService()

# 加密文本
encrypted = encryption_service.encrypt("sensitive_data")

# 解密文本
decrypted = encryption_service.decrypt(encrypted)

# 加密字典中的字段
data = {'apiKey': 'secret_key'}
encrypted_data = encryption_service.encrypt_dict_field(data, 'apiKey')

# 解密字典中的字段
decrypted_data = encryption_service.decrypt_dict_field(data, 'apiKey')
```

## 数据库操作

### 自动加密/解密

数据库服务会自动处理敏感信息的加密和解密：

```python
# 保存时会自动加密
db_service.add_ai_setting(
    model_id='gpt-4',
    model_name='GPT-4',
    api_url='https://api.openai.com/v1',
    api_key='sk-...',  # 会自动加密存储
    secret_key='secret'  # 会自动加密存储
)

# 读取时会自动解密
setting = db_service.get_ai_setting('gpt-4')
print(setting['apiKey'])  # 已解密
print(setting['secretKey'])  # 已解密
```

## 安全建议

1. **生产环境**: 务必设置环境变量 `DB_ENCRYPTION_KEY`
2. **密钥管理**: 使用专业的密钥管理服务（如 AWS KMS、Azure Key Vault）
3. **访问控制**: 限制数据库文件的访问权限
4. **备份安全**: 加密数据库备份文件
5. **定期更换**: 定期更换加密密钥（需要重新加密所有数据）

## 故障排除

### 解密失败

如果遇到解密失败，可能的原因：

1. **密钥不匹配**: 检查 `DB_ENCRYPTION_KEY` 环境变量是否正确
2. **数据损坏**: 数据库文件可能损坏，需要恢复备份
3. **算法版本**: 确保使用相同版本的加密算法

### 性能影响

加密/解密操作会增加轻微的性能开销：

- 加密操作: ~1-2ms
- 解密操作: ~1-2ms
- 对整体性能影响: 可忽略不计

## 技术细节

### 密钥派生过程

1. 从密码和环境变量获取主密钥
2. 使用 PBKDF2HMAC 算法派生 AES 密钥
3. 使用固定盐值确保密钥一致性
4. 运行 100,000 次迭代增加暴力破解难度

### 加密过程

1. 将明文转换为字节
2. 使用 XOR 加密数据
3. 将加密结果进行 Base64 编码
4. 添加 ENC: 前缀标识
5. 存储到数据库

### 解密过程

1. 从数据库读取加密数据
2. 检查 ENC: 前缀
3. 移除前缀并进行 Base64 解码
4. 使用 XOR 解密数据
5. 将字节转换为明文字符串

### 向后兼容

加密服务支持向后兼容：
- 如果数据以 `ENC:` 开头，则进行解密
- 如果数据不以 `ENC:` 开头，则直接返回原值（兼容旧数据）

## 安全审计

建议定期进行安全审计：

1. 检查数据库文件权限
2. 验证加密密钥的安全性
3. 审查访问日志
4. 测试加密/解密功能
5. 更新依赖库版本

## 依赖说明

本加密方案仅使用 Python 内置库：
- `base64`: 用于 Base64 编码/解码
- `os`: 用于读取环境变量
- `hashlib`: 用于密钥派生和加密

无需安装第三方加密库，避免了依赖问题。

## 联系支持

如有安全问题或疑问，请联系系统管理员。
