from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, close_db, close_olap
from app.routers import games, reviews, analytics as analytics_router, ws
from app.services.etl_service import load_games, load_genres, load_game_genres, load_reviews, build_olap
from app.routers.ws import broadcast_players
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("steam")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Steam 分析平台启动中...")
    await init_db()
    logger.info("数据库表已创建")

    # 检查是否需要加载数据
    from app.database import async_session
    from app.models import Game
    from sqlalchemy import select, func

    async with async_session() as session:
        count = await session.scalar(select(func.count(Game.appid)))
        if count == 0:
            logger.info("数据库为空，开始加载数据...")
            await load_genres()
            await load_games()
            await load_game_genres()
            await load_reviews()
            build_olap()
            logger.info("数据加载完成")
        else:
            logger.info(f"数据库已有 {count} 款游戏，跳过加载")

    # 启动 WebSocket 广播任务
    task = asyncio.create_task(broadcast_players())

    yield

    task.cancel()
    await close_db()
    close_olap()
    logger.info("服务关闭")


app = FastAPI(
    title="Steam Game Analytics",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router)
app.include_router(reviews.router)
app.include_router(analytics_router.router)
app.include_router(ws.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
