from app.database import get_olap
from typing import Any
import logging

logger = logging.getLogger("steam.analytics")


def genre_summary() -> list[dict[str, Any]]:
    """类型维度聚合分析"""
    conn = get_olap()
    rows = conn.execute("""
        SELECT
            TRIM(genre) as genre,
            COUNT(*) as game_count,
            ROUND(AVG(price), 2) as avg_price,
            ROUND(AVG(metacritic_score), 1) as avg_metacritic,
            COALESCE(SUM(fr.total_reviews), 0) as total_reviews,
            ROUND(COALESCE(AVG(fr.positive_rate), 0), 1) as positive_rate
        FROM steam.dim_games g
        LEFT JOIN steam.fact_reviews fr ON g.appid = fr.appid
        CROSS JOIN LATERAL UNNEST(STRING_SPLIT(g.genres, ',')) AS genre
        WHERE g.genres != '其他'
        GROUP BY genre
        ORDER BY game_count DESC
    """).fetchall()

    return [
        {
            "genre": r[0],
            "game_count": r[1],
            "avg_price": r[2],
            "avg_metacritic": r[3],
            "total_reviews": r[4],
            "positive_rate": r[5],
        }
        for r in rows
    ]


def price_distribution() -> list[dict[str, Any]]:
    """价格段分布"""
    conn = get_olap()
    rows = conn.execute("""
        SELECT
            price_tier,
            COUNT(*) as game_count,
            ROUND(AVG(metacritic_score), 1) as avg_rating,
            COALESCE(SUM(fr.total_reviews), 0) as total_reviews
        FROM steam.dim_games g
        LEFT JOIN steam.fact_reviews fr ON g.appid = fr.appid
        GROUP BY price_tier
        ORDER BY
            CASE price_tier
                WHEN '免费' THEN 1
                WHEN '低价 (<$10)' THEN 2
                WHEN '中等 ($10-$30)' THEN 3
                WHEN '高价 ($30-$60)' THEN 4
                WHEN '豪华 (>$60)' THEN 5
            END
    """).fetchall()
    return [
        {"tier": r[0], "game_count": r[1], "avg_rating": r[2], "total_reviews": r[3]}
        for r in rows
    ]


def daily_trends(days: int = 90) -> list[dict[str, Any]]:
    """每日评论趋势"""
    conn = get_olap()
    rows = conn.execute(f"""
        SELECT
            review_date,
            COUNT(DISTINCT appid) as count,
            ROUND(AVG(positive_count * 100.0 / NULLIF(review_count, 0)), 1) as positive_rate
        FROM steam.daily_trends
        WHERE review_date >= CURRENT_DATE - INTERVAL '{days} days'
        GROUP BY review_date
        ORDER BY review_date
    """).fetchall()
    return [
        {"date": str(r[0]), "count": r[1], "positive_rate": r[2]}
        for r in rows
    ]


def top_games(limit: int = 20) -> list[dict[str, Any]]:
    """综合排名：评论数 × 好评率"""
    conn = get_olap()
    rows = conn.execute(f"""
        SELECT
            g.appid, g.name, g.price, g.metacritic_score,
            fr.total_reviews, ROUND(fr.positive_rate, 1) as positive_rate
        FROM steam.dim_games g
        JOIN steam.fact_reviews fr ON g.appid = fr.appid
        WHERE fr.total_reviews >= 100
        ORDER BY fr.total_reviews * fr.positive_rate DESC
        LIMIT {limit}
    """).fetchall()
    return [
        {
            "appid": r[0], "name": r[1], "price": r[2],
            "metacritic_score": r[3], "total_reviews": r[4],
            "positive_rate": r[5],
        }
        for r in rows
    ]


def genre_cross_analysis() -> list[dict[str, Any]]:
    """类型 x 价格 交叉分析"""
    conn = get_olap()
    rows = conn.execute("""
        SELECT
            TRIM(genre) as genre,
            g.price_tier,
            COUNT(*) as game_count,
            ROUND(AVG(g.metacritic_score), 1) as avg_metacritic
        FROM steam.dim_games g
        CROSS JOIN LATERAL UNNEST(STRING_SPLIT(g.genres, ',')) AS genre
        WHERE g.genres != '其他'
        GROUP BY genre, g.price_tier
        HAVING COUNT(*) >= 5
        ORDER BY genre, game_count DESC
    """).fetchall()
    return [
        {"genre": r[0], "price_tier": r[1], "game_count": r[2], "avg_metacritic": r[3]}
        for r in rows
    ]


def realtime_players(limit: int = 20) -> list[dict[str, Any]]:
    """实时在线玩家（取最新记录）"""
    conn = get_olap()
    rows = conn.execute(f"""
        SELECT s.appid, s.player_count, s.recorded_at
        FROM steam.realtime_players s
        WHERE s.recorded_at >= CURRENT_TIMESTAMP - INTERVAL '1 day'
        ORDER BY s.player_count DESC
        LIMIT {limit}
    """).fetchall()
    return [
        {"appid": r[0], "player_count": r[1], "recorded_at": str(r[2])}
        for r in rows
    ]


def search_games(query: str, limit: int = 20) -> list[dict]:
    """搜索游戏（通过 PostgreSQL）"""
    from app.database import async_session
    from app.models import Game
    from sqlalchemy import select
    import asyncio

    async def _search():
        async with async_session() as session:
            result = await session.execute(
                select(Game).where(Game.name.ilike(f"%{query}%")).limit(limit)
            )
            games = result.scalars().all()
            return [
                {
                    "appid": g.appid,
                    "name": g.name,
                    "price": g.price,
                    "metacritic_score": g.metacritic_score,
                }
                for g in games
            ]

    return asyncio.run(_search())
