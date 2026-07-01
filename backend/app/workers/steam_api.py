"""Celery 异步任务：定时采集 Steam Web API 实时数据"""
from celery import Celery
from app.config import settings
from datetime import datetime
import httpx
import logging

logger = logging.getLogger("steam.worker")

celery_app = Celery(
    "steam_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    task_serializer="json",
    accept_content=["json"],
)

celery_app.conf.beat_schedule = {
    "fetch-player-counts": {
        "task": "app.workers.steam_api.fetch_player_counts",
        "schedule": 600,  # 每 10 分钟
    },
}


@celery_app.task
def fetch_player_counts():
    """采集 Steam 在线玩家数"""
    if not settings.steam_api_key:
        logger.warning("STEAM_API_KEY 未配置，跳过实时数据采集")
        return

    try:
        # 获取热门游戏列表
        url = "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/"
        params = {"key": settings.steam_api_key}
        response = httpx.get(url, params=params, timeout=30)
        data = response.json()
        ranks = data.get("response", {}).get("ranks", [])
        logger.info(f"获取到 {len(ranks)} 款游戏的在线数据")
    except Exception as e:
        logger.error(f"获取在线玩家失败: {e}")
