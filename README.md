# 股票分析平台 (Gu-Best Stock Platform)

基于Node.js + Vue.js的股票分析平台，提供实时行情、K线图、技术指标等功能。

## 功能特性

- 📊 **实时行情** - WebSocket实时推送股票价格
- 📈 **K线图** - 支持日K、周K、月K等多种周期
- 🔍 **技术指标** - KDJ、MACD、BOLL等常用指标
- 🔎 **股票搜索** - 支持代码和名称搜索
- 📱 **响应式设计** - 适配桌面和移动设备

## 技术栈

### 后端
- **Node.js** - 运行环境
- **Express** - Web框架
- **WebSocket** - 实时数据推送
- **Axios** - HTTP客户端

### 前端
- **Vue 3** - 前端框架
- **Vite** - 构建工具
- **SVG** - 图表绘制

## 项目结构

```
gu-best/
├── server/                 # Node.js后端
│   ├── index.js           # 服务器入口
│   ├── routes/            # API路由
│   │   ├── stock.js       # 股票相关API
│   │   └── kline.js       # K线数据API
│   └── services/          # 业务逻辑
│       ├── stockService.js
│       ├── klineService.js
│       └── websocket.js
├── frontend/              # 前端代码
│   ├── index.html
│   ├── css/
│   └── js/
│       ├── components/    # Vue组件
│       ├── api.js         # API封装
│       └── app.js         # 应用入口
├── package.json           # 项目配置
├── vite.config.js         # Vite配置
└── .env.example           # 环境变量示例
```

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置你的API密钥
```

### 3. 启动开发服务器

```bash
# 同时启动前端和后端
npm run dev
```

或者分别启动：

```bash
# 启动后端API服务器
npm run server:dev

# 启动前端开发服务器
npm run client:dev
```

### 4. 访问应用

- 前端: http://localhost:5173
- 后端API: http://localhost:3000/api
- 健康检查: http://localhost:3000/api/health

## 可用脚本

```bash
# 开发模式（同时启动前后端）
npm run dev

# 仅启动后端开发服务器
npm run server:dev

# 仅启动前端开发服务器
npm run client:dev

# 生产模式启动后端
npm run server:prod

# 构建前端
npm run build

# 预览生产构建
npm run client:preview

# 代码检查
npm run lint

# 自动修复代码
npm run lint:fix
```

## API文档

### 股票API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/stocks | 获取股票列表 |
| GET | /api/stocks/search?keyword=xxx | 搜索股票 |
| GET | /api/stocks/:code | 获取股票详情 |
| GET | /api/stocks/:code/realtime | 获取实时行情 |
| GET | /api/stocks/sectors/list | 获取板块列表 |

### K线API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/kline/:code | 获取K线数据 |
| GET | /api/kline/:code/indicators | 获取技术指标 |
| GET | /api/kline/:code/history | 获取历史数据 |

### WebSocket

连接: `ws://localhost:3000`

**消息格式:**

```javascript
// 订阅股票
{ type: 'subscribe', code: '000001' }

// 取消订阅
{ type: 'unsubscribe', code: '000001' }

// 心跳
{ type: 'ping' }
```

## 部署

### 生产环境构建

```bash
# 构建前端
npm run build

# 启动生产服务器
npm start
```

### Docker部署（可选）

```bash
# 构建镜像
docker build -t gu-best-stock .

# 运行容器
docker run -p 3000:3000 gu-best-stock
```

## 开发计划

- [ ] 接入真实股票API
- [ ] 用户系统与登录
- [ ] 自选股功能
- [ ] 股票预警通知
- [ ] 数据分析报表

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License