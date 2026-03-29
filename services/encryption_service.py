import base64
import os
import hashlib

class EncryptionService:
    """使用 Python 内置库实现的简单加密服务"""
    
    def __init__(self, password: str = None):
        self.password = password or self._get_default_password()
        self.key = self._derive_key(self.password)
    
    def _get_default_password(self) -> str:
        """获取默认密码，优先使用环境变量"""
        env_password = os.environ.get('DB_ENCRYPTION_KEY')
        if env_password:
            return env_password
        
        # 如果没有环境变量，使用一个固定的密钥（生产环境应该使用环境变量）
        return "stock_analysis_system_default_key_2024"
    
    def _derive_key(self, password: str) -> bytes:
        """使用 SHA-256 从密码派生密钥"""
        salt = b'stock_analysis_salt_2024'
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return key
    
    def _xor_encrypt(self, data: bytes, key: bytes) -> bytes:
        """使用 XOR 加密数据"""
        encrypted = bytearray()
        key_len = len(key)
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key[i % key_len])
        return bytes(encrypted)
    
    def encrypt(self, plaintext: str) -> str:
        """加密文本"""
        if not plaintext:
            return None
        
        try:
            # 将文本转换为字节
            data = plaintext.encode('utf-8')
            
            # 使用 XOR 加密
            encrypted_data = self._xor_encrypt(data, self.key)
            
            # 使用 Base64 编码
            encoded = base64.urlsafe_b64encode(encrypted_data).decode('ascii')
            
            # 添加前缀标识这是加密数据
            return f"ENC:{encoded}"
        except Exception as e:
            print(f"加密失败: {e}")
            return None
    
    def decrypt(self, encrypted_text: str) -> str:
        """解密文本"""
        if not encrypted_text:
            return None
        
        # 检查是否是加密数据（以 ENC: 开头）
        if not encrypted_text.startswith("ENC:"):
            # 如果不是加密数据，直接返回原值（兼容旧数据）
            return encrypted_text
        
        try:
            # 移除前缀
            encoded = encrypted_text[4:]
            
            # Base64 解码
            encrypted_data = base64.urlsafe_b64decode(encoded.encode('ascii'))
            
            # 使用 XOR 解密（XOR 是对称的）
            decrypted_data = self._xor_encrypt(encrypted_data, self.key)
            
            # 转换为字符串
            return decrypted_data.decode('utf-8')
        except Exception as e:
            print(f"解密失败: {e}")
            return None
    
    def encrypt_dict_field(self, data: dict, field_name: str) -> dict:
        """加密字典中的指定字段"""
        if field_name in data and data[field_name]:
            encrypted_value = self.encrypt(data[field_name])
            if encrypted_value:
                data[field_name] = encrypted_value
        return data
    
    def decrypt_dict_field(self, data: dict, field_name: str) -> dict:
        """解密字典中的指定字段"""
        if field_name in data and data[field_name]:
            decrypted_value = self.decrypt(data[field_name])
            if decrypted_value:
                data[field_name] = decrypted_value
        return data


# 全局加密服务实例
encryption_service = EncryptionService()
