# Stock-View

A股实时行情查看与 AI 分析平台，参考东方财富、同花顺等主流股票软件的核心功能。

- **实时 A 股行情**：沪深 A 股实时报价、K 线图、分时图、盘口数据
- **AI 股票分析**（预留）：AI 模型智能分析，插件化架构，后续无缝接入
- **自选股管理**：自选股列表管理，实时追踪关注股票

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Pinia + ECharts + Element Plus |
| 后端 | Python 3.11 + FastAPI + SQLAlchemy 2.0 (async) |
| 数据库 | PostgreSQL 15 + Redis 7 |
| 部署 | Docker Compose + Nginx |

---

## 快速启动

### 方式一：Docker Compose 一键启动（推荐）

> 前提：已安装 [Docker](https://docs.docker.com/get-docker/) 和 [Docker Compose](https://docs.docker.com/compose/install/)

```bash
# 1. 克隆项目
git clone <repo-url> stock-view
cd stock-view

# 2. 一键构建并启动所有服务
docker compose up --build
```

启动完成后访问：

- 前端页面：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 方式二：本地开发模式

适合前后端单独调试的开发场景。

#### 1. 启动依赖服务（PostgreSQL + Redis）

```bash
# 仅启动数据库和缓存
docker compose up postgres redis
```

#### 2. 启动后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp ../.env.example .env
# 编辑 .env，确认 DATABASE_URL 和 REDIS_URL 指向 localhost
# DATABASE_URL=postgresql+asyncpg://stockview:stockview123@localhost:5432/stockview
# REDIS_URL=redis://localhost:6379/0

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（含热更新）
npm run dev
```

启动后前端默认运行在 http://localhost:5173，Vite 开发服务器会自动代理 API 请求到后端 8000 端口。

---

## 项目结构

```
stock-view/
├── docker-compose.yml        # 容器编排
├── .env.example              # 环境变量模板
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py           # FastAPI 入口
│       ├── core/             # 配置、数据库、Redis、安全
│       ├── models/           # SQLAlchemy 模型
│       ├── schemas/          # Pydantic 数据校验
│       ├── api/v1/           # REST API 路由（行情/股票/自选/AI）
│       ├── api/websocket.py  # WebSocket 实时推送
│       ├── services/collector/  # 数据采集（东方财富/新浪）
│       ├── ai/               # AI 分析插件架构
│       └── tasks/            # Celery 异步任务
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    └── src/
        ├── main.ts          # Vue 入口
        ├── App.vue          # 根组件
        ├── router/          # 路由配置
        ├── api/             # Axios API 客户端
        ├── stores/          # Pinia 状态管理
        └── pages/           # 页面组件
            ├── MarketPage.vue      # 行情列表
            ├── StockDetailPage.vue # 股票详情（K线/分时）
            ├── WatchlistPage.vue   # 自选股管理
            └── SearchPage.vue      # 股票搜索
```

---

## 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | PostgreSQL 连接串 | `postgresql+asyncpg://stockview:stockview123@postgres:5432/stockview` |
| `REDIS_URL` | Redis 连接串 | `redis://redis:6379/0` |
| `AI_ADAPTER` | AI 适配器（mock/rule） | `mock` |
| `APP_ENV` | 运行环境 | `development` |
| `APP_DEBUG` | 调试模式 | `true` |
| `PRIMARY_DATA_SOURCE` | 主数据源 | `eastmoney` |
| `FALLBACK_DATA_SOURCE` | 备用数据源 | `sina` |

完整变量列表见 `.env.example`。

---

## 常用命令

```bash
# Docker 相关
docker compose up --build          # 构建并启动
docker compose up -d               # 后台启动
docker compose down                # 停止所有服务
docker compose logs -f backend     # 查看后端日志
docker compose restart backend     # 重启后端

# 前端开发
cd frontend && npm run dev         # 启动开发服务器
cd frontend && npm run build       # 生产构建

# 后端开发
cd backend && uvicorn app.main:app --reload   # 启动开发服务器
```
