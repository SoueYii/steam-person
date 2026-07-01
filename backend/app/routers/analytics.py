from fastapi import APIRouter, Query
from app.services import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/genre-summary")
async def genre_summary():
    """类型分布统计"""
    data = analytics_service.genre_summary()
    return {"items": data}


@router.get("/price-distribution")
async def price_distribution():
    """价格段分布"""
    data = analytics_service.price_distribution()
    return {"items": data}


@router.get("/daily-trends")
async def daily_trends(days: int = Query(90, ge=7, le=365)):
    """每日评论趋势"""
    data = analytics_service.daily_trends(days)
    return {"items": data}


@router.get("/top-games")
async def top_games(limit: int = Query(20, ge=5, le=50)):
    """综合排名"""
    data = analytics_service.top_games(limit)
    return {"items": data}


@router.get("/genre-cross")
async def genre_cross():
    """类型 x 价格 交叉分析"""
    data = analytics_service.genre_cross_analysis()
    return {"items": data}


@router.get("/realtime-players")
async def realtime_players(limit: int = Query(20, ge=5, le=50)):
    """实时在线玩家"""
    data = analytics_service.realtime_players(limit)
    return {"items": data}
