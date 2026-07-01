# Steam Game Analytics

全栈实时 Steam 游戏数据分析平台。

基于 Zenodo Steam Dataset 2025（24 万游戏 + 398 万评论），从 CSV 加载到 PostgreSQL，用 DuckDB 做 OLAP 分析层，前端 React 可视化展示，并通过 Steam Web API 定时采集实时在线玩家数据。

## 技术栈

| 层级 | 技术 |
|:-----|:-----|
| 前端 | React 18 + TypeScript + Vite + Tailwind CSS + Recharts |
| 后端 | FastAPI + SQLAlchemy 2.0 + Alembic（异步） |
| 分析层 | DuckDB（列式 OLAP 引擎） |
| 业务数据库 | PostgreSQL 16 |
| 消息队列 | Redis + Celery（异步任务） |
| 实时通信 | WebSocket（在线玩家实时推送） |
| 部署 | Docker Compose（4 服务） |

## 架构

```
CSV 数据 (1.2 GB)
    ↓ ETL
PostgreSQL (业务存储)
    ↓
DuckDB (OLAP 分析层)    ← Steam Web API → Celery Worker (定时采集)
    ↓                              ↓
FastAPI (REST + WebSocket)    Redis (消息队列)
    ↓
React + TypeScript (前端)
```

## 快速启动

```bash
# 1. 将 Zenodo 数据放在 data/raw/steam_dataset_2025_csv/
# 2. 启动所有服务
docker compose up -d

# 3. 访问前端
open http://localhost:5173
```

首次启动自动完成 ETL 数据加载。

## API 接口

| 路径 | 说明 |
|:-----|:-----|
| `GET /api/games` | 游戏列表（分页/排序） |
| `GET /api/games/search?q=` | 搜索游戏 |
| `GET /api/games/:id` | 游戏详情 |
| `GET /api/reviews` | 评论列表（支持筛选） |
| `GET /api/analytics/genre-summary` | 类型分布统计 |
| `GET /api/analytics/price-distribution` | 价格段分布 |
| `GET /api/analytics/daily-trends` | 每日评论趋势 |
| `GET /api/analytics/top-games` | 综合排名 |
| `GET /api/analytics/genre-cross` | 类型x价格交叉分析 |
| `GET /api/analytics/realtime-players` | 实时在线玩家 |
| `WS /ws/live` | WebSocket 实时推送 |

## 实时数据

配置 Steam Web API Key 后，Celery worker 每 10 分钟采集一次热门游戏在线玩家数：

```bash
docker compose run -e STEAM_API_KEY=your_key worker
```

## 项目结构

```
steam-analysis/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py             # 配置
│   │   ├── database.py           # PostgreSQL + DuckDB 连接
│   │   ├── models.py             # SQLAlchemy 模型
│   │   ├── schemas.py            # Pydantic 模型
│   │   ├── routers/              # API 路由
│   │   ├── services/
│   │   │   ├── etl_service.py    # CSV 数据加载
│   │   │   └── analytics_service.py  # DuckDB OLAP 查询
│   │   └── workers/
│   │       └── steam_api.py      # Celery 异步任务
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx               # 主布局 + 导航
│   │   ├── api/client.ts         # API 客户端
│   │   ├── types/index.ts        # TypeScript 类型
│   │   └── pages/                # 5 个页面
│   │       ├── Dashboard.tsx     # 概览
│   │       ├── Games.tsx         # 游戏 + 搜索
│   │       ├── Trends.tsx        # 趋势
│   │       ├── Reviews.tsx       # 评论
│   │       └── Realtime.tsx      # 实时在线
│   └── package.json
├── data/raw/steam_dataset_2025_csv/  # Zenodo 原始数据
├── docker-compose.yml
└── README.md
```
