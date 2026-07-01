import os
import pandas as pd
from sqlalchemy import text
from app.config import settings
from app.database import get_olap, async_session
from app.models import Game, Genre, GameGenre, Review
from datetime import datetime
import duckdb
import logging

logger = logging.getLogger("steam.etl")

CSV_DIR = settings.csv_dir
RAW_DIR = os.path.join(CSV_DIR, "raw", "steam_dataset_2025_csv")


def _csv_path(name: str) -> str:
    return os.path.join(RAW_DIR, f"{name}.csv")


async def load_games():
    """加载游戏数据到 PostgreSQL"""
    path = _csv_path("applications")
    if not os.path.exists(path):
        logger.warning(f"文件不存在: {path}")
        return 0

    df = pd.read_csv(path, escapechar="\\", quotechar='"', low_memory=False)
    logger.info(f"applications.csv: {len(df)} 行, {list(df.columns)}")

    async with async_session() as session:
        count = 0
        for _, row in df.iterrows():
            game = Game(
                appid=int(row.get("appid", 0)),
                name=str(row.get("name", "Unknown"))[:500],
                type=str(row.get("type", ""))[:50],
                is_free=bool(row.get("is_free", False)),
                release_date=str(row.get("release_date", ""))[:50] if pd.notna(row.get("release_date")) else None,
                metacritic_score=int(row["metacritic_score"]) if pd.notna(row.get("metacritic_score")) else None,
                recommendations_total=int(row["recommendations_total"]) if pd.notna(row.get("recommendations_total")) else 0,
                price=float(row.get("price", 0)),
                developers=str(row.get("developers", ""))[:500] if pd.notna(row.get("developers")) else None,
                publishers=str(row.get("publishers", ""))[:500] if pd.notna(row.get("publishers")) else None,
            )
            session.add(game)
            count += 1
            if count % 5000 == 0:
                await session.flush()
                logger.info(f"  已写入 {count} 条游戏")
        await session.commit()
        logger.info(f"游戏表加载完成: {count} 条")
    return count


async def load_genres():
    """加载类型维度表"""
    path = _csv_path("genres")
    if not os.path.exists(path):
        return 0

    df = pd.read_csv(path)
    async with async_session() as session:
        count = 0
        for _, row in df.iterrows():
            genre = Genre(id=int(row["id"]), name=str(row["name"]))
            session.add(genre)
            count += 1
        await session.commit()
        logger.info(f"类型表: {count} 条")
    return count


async def load_game_genres():
    """加载游戏-类型关联"""
    path = _csv_path("application_genres")
    if not os.path.exists(path):
        return 0

    df = pd.read_csv(path)
    async with async_session() as session:
        count = 0
        for _, row in df.iterrows():
            gg = GameGenre(appid=int(row["appid"]), genreid=int(row["genreid"]))
            session.add(gg)
            count += 1
            if count % 10000 == 0:
                await session.flush()
        await session.commit()
        logger.info(f"游戏-类型关联: {count} 条")
    return count


async def load_reviews():
    """加载评论数据（取样 20%，全量 400 万太慢）"""
    path = _csv_path("reviews")
    if not os.path.exists(path):
        return 0

    import random
    random.seed(42)

    async with async_session() as session:
        count = 0
        for chunk in pd.read_csv(path, chunksize=50000, escapechar="\\", quotechar='"', low_memory=False):
            chunk = chunk.sample(frac=0.2, random_state=42)
            for _, row in chunk.iterrows():
                review = Review(
                    recommendation_id=str(row.get("recommendationid", "")),
                    appid=int(row.get("appid", 0)),
                    voted_up=bool(row.get("voted_up", True)) if pd.notna(row.get("voted_up")) else None,
                    review_text=str(row.get("review_text", "")) if pd.notna(row.get("review_text")) else None,
                    language=str(row.get("language", "english"))[:20] if pd.notna(row.get("language")) else "english",
                    timestamp_created=datetime.fromtimestamp(int(row["timestamp_created"])) if pd.notna(row.get("timestamp_created")) else None,
                    author_steamid=str(row.get("author_steamid", "")),
                    votes_funny=int(row.get("votes_funny", 0)) if pd.notna(row.get("votes_funny")) else 0,
                    votes_helpful=int(row.get("votes_helpful", 0)) if pd.notna(row.get("votes_helpful")) else 0,
                )
                session.add(review)
                count += 1
                if count % 10000 == 0:
                    await session.flush()
                    logger.info(f"  已写入 {count} 条评论")
        await session.commit()
        logger.info(f"评论表加载完成: {count} 条")
    return count


# ─── DuckDB OLAP 构建 ─────────────────────────────────────────────────────

def build_olap():
    """从 PostgreSQL 导数据到 DuckDB，建立分析层"""
    conn = get_olap()
    sync_url = settings.sync_database_url

    logger.info("构建 DuckDB OLAP 层...")

    conn.execute("INSTALL postgres; LOAD postgres;")
    conn.execute(f"ATTACH '{sync_url}' AS pg (TYPE POSTGRES);")

    conn.execute("CREATE SCHEMA IF NOT EXISTS steam;")

    conn.execute("DROP TABLE IF EXISTS steam.dim_games")
    conn.execute("""
        CREATE TABLE steam.dim_games AS
        SELECT
            g.appid,
            g.name,
            g.price,
            g.metacritic_score,
            g.is_free,
            CASE
                WHEN g.price = 0 THEN '免费'
                WHEN g.price < 10 THEN '低价 (<$10)'
                WHEN g.price < 30 THEN '中等 ($10-$30)'
                WHEN g.price < 60 THEN '高价 ($30-$60)'
                ELSE '豪华 (>$60)'
            END as price_tier,
            COALESCE(gn.genre_names, '其他') as genres
        FROM pg.public.games g
        LEFT JOIN (
            SELECT gg.appid, STRING_AGG(ge.name, ',') as genre_names
            FROM pg.public.game_genres gg
            JOIN pg.public.genres ge ON gg.genreid = ge.id
            GROUP BY gg.appid
        ) gn ON g.appid = gn.appid
    """)

    conn.execute("DROP TABLE IF EXISTS steam.fact_reviews")
    conn.execute("""
        CREATE TABLE steam.fact_reviews AS
        SELECT
            r.appid,
            COUNT(*) as total_reviews,
            SUM(CASE WHEN r.voted_up THEN 1 ELSE 0 END) as positive_reviews,
            AVG(CASE WHEN r.voted_up THEN 100.0 ELSE 0 END) as positive_rate,
            COUNT(DISTINCT r.language) as language_count,
            MIN(r.timestamp_created) as first_review,
            MAX(r.timestamp_created) as last_review
        FROM pg.public.reviews r
        GROUP BY r.appid
    """)

    conn.execute("DROP TABLE IF EXISTS steam.daily_trends")
    conn.execute("""
        CREATE TABLE steam.daily_trends AS
        SELECT
            DATE(r.timestamp_created) as review_date,
            r.appid,
            COUNT(*) as review_count,
            SUM(CASE WHEN r.voted_up THEN 1 ELSE 0 END) as positive_count
        FROM pg.public.reviews r
        WHERE r.timestamp_created IS NOT NULL
        GROUP BY DATE(r.timestamp_created), r.appid
    """)

    conn.execute("DROP TABLE IF EXISTS steam.realtime_players")
    conn.execute("""
        CREATE TABLE steam.realtime_players AS
        SELECT
            s.appid,
            s.player_count,
            s.recorded_at
        FROM pg.public.realtime_stats s
    """)

    count = conn.execute("SELECT COUNT(*) FROM steam.dim_games").fetchone()[0]
    logger.info(f"DuckDB OLAP 构建完成: {count} 款游戏")
    return count
