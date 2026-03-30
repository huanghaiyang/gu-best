# 股票分析系统

## 项目简介

这是一个基于Flask和Vue的股票分析系统，支持股票实时行情、板块分析、龙头股推荐等功能。

## 功能特性

- 股票实时行情查询
- 板块分析与成分股查询
- 龙头股推荐
- AI股票分析
- 多数据源支持（东方财富、Akshare）
- 系统设置管理

## 技术栈

- 后端：Python, Flask
- 前端：Vue.js, Bootstrap
- 数据库：SQLite
- 数据源：东方财富API, Akshare

## 快速开始

### 环境要求

- Python 3.7+
- Node.js 14+

### 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装前端依赖
npm install
```

### 配置东方财富API密钥

1. 创建 `eastmoney_keys.py` 文件，内容如下：

```python
# 东方财富API密钥配置
# 此文件会被.gitignore忽略，请勿提交到版本控制系统

# API基础URL
BASE_URL = 'http://push2.eastmoney.com/api'

# API访问令牌
UT_TOKEN_STOCK = ''  # 股票实时行情令牌
UT_TOKEN_LIST = ''  # 股票列表令牌
SEARCH_TOKEN = ''  # 搜索令牌

# 超时设置（秒）
DEFAULT_TIMEOUT = 10
LONG_TIMEOUT = 15
```

### 初始化数据库

```bash
python scripts/db_manage.py init
```

### 启动服务

```bash
# 启动后端服务
python app.py

# 启动前端开发服务器（在另一个终端）
npm run dev
```

服务将在 `http://127.0.0.1:8000` 运行。

## 项目结构

- `app.py` - 后端主应用
- `services/` - 服务层代码
  - `stock_service.py` - 股票服务
  - `eastmoney_api.py` - 东方财富API封装
  - `akshare_api.py` - Akshare API封装
  - `database_service.py` - 数据库服务
  - `ai_service.py` - AI分析服务
- `frontend/` - 前端代码
- `scripts/` - 脚本工具
  - `db_manage.py` - 数据库管理工具
- `data/` - 数据目录（会被.gitignore忽略）
- `eastmoney_keys.py` - 东方财富API密钥（会被.gitignore忽略）

## 数据源配置

系统支持多种数据源，默认使用Akshare。可以在系统设置中切换数据源。

## 安全注意事项

- `eastmoney_keys.py` 文件包含API访问令牌，请勿提交到版本控制系统
- 生产环境中应使用环境变量存储敏感信息
- 定期更新API令牌以确保安全性

## 许可证

MIT License
