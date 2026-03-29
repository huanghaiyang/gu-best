#!/usr/bin/env python3
"""
生成自签名SSL证书用于HTTPS通信
"""
import os
import ssl
from OpenSSL import crypto

# 证书配置
CERT_FILE = 'ssl_cert.pem'
KEY_FILE = 'ssl_key.pem'

# 证书信息
SUBJECT = {
    'C': 'CN',           # 国家
    'ST': 'Shanghai',    # 州/省
    'L': 'Shanghai',     # 城市
    'O': 'StockAnalysis', # 组织
    'OU': 'IT',          # 部门
    'CN': 'localhost'    # 通用名称
}

def generate_certificate():
    """生成自签名SSL证书"""
    # 生成私钥
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    
    # 创建证书请求
    req = crypto.X509Req()
    subject = req.get_subject()
    
    for key, value in SUBJECT.items():
        setattr(subject, key, value)
    
    req.set_pubkey(key)
    req.sign(key, 'sha256')
    
    # 创建证书
    cert = crypto.X509()
    cert.set_subject(req.get_subject())
    cert.set_issuer(req.get_subject())  # 自签名
    cert.set_pubkey(req.get_pubkey())
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # 1年有效期
    cert.sign(key, 'sha256')
    
    # 写入文件
    with open(CERT_FILE, 'wb') as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    with open(KEY_FILE, 'wb') as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    
    print(f"证书生成成功:")
    print(f"  - 证书文件: {CERT_FILE}")
    print(f"  - 密钥文件: {KEY_FILE}")
    print(f"  - 有效期: 1年")
    print(f"  - 主题: {SUBJECT}")

if __name__ == '__main__':
    # 检查是否已存在证书
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        print(f"证书已存在，跳过生成。")
        print(f"  - 证书文件: {CERT_FILE}")
        print(f"  - 密钥文件: {KEY_FILE}")
    else:
        generate_certificate()
