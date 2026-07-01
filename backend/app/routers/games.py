from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Game, GameGenre, Genre, Review
from app.schemas import GameOut, GameDetail
from app.services.analytics_service import search_games
from typing import Optional
import asyncio

router = APIRouter(prefix="/api/games", tags=["games"])


@router.get("")
async def list_games(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str = Query("name", regex="^(name|price|metacritic_score|recommendations_total)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    col = getattr(Game, sort)
    order_col = col.desc() if order == "desc" else col.asc()
    result = await db.execute(
        select(Game).order_by(order_col).offset((page - 1) * page_size).limit(page_size)
    )
    games = result.scalars().all()
    total = await db.scalar(select(func.count(Game.appid)))
    return {
        "items": [GameOut.model_validate(g).model_dump() for g in games],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/search")
async def search(q: str = Query(min_length=1), limit: int = Query(20, le=50)):
    """搜索游戏"""
    items = await asyncio.to_thread(search_games, q, limit)
    return {"items": items}


@router.get("/{appid}")
async def get_game(appid: int, db: AsyncSession = Depends(get_db)):
    """游戏详情"""
    game = await db.scalar(select(Game).where(Game.appid == appid))
    if not game:
        return {"error": "not found"}

    genres = await db.execute(
        select(Genre.name).join(GameGenre).where(GameGenre.appid == appid)
    )
    genre_names = [g[0] for g in genres]

    review_stats = await db.execute(
        select(
            func.count(Review.id),
            func.avg(Review.voted_up.cast(float)),
        ).where(Review.appid == appid)
    )
    row = review_stats.one()
    review_count = row[0] or 0
    positive_rate = round(row[1] * 100, 1) if row[1] else None

    detail = GameDetail(
        **GameOut.model_validate(game).model_dump(),
        genres=genre_names,
        review_count=review_count,
        positive_rate=positive_rate,
    )
    return detail
