from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Review
from app.schemas import ReviewOut
from typing import Optional

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("")
async def list_reviews(
    appid: Optional[int] = Query(None),
    language: Optional[str] = Query(None),
    voted_up: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Review)
    if appid:
        query = query.where(Review.appid == appid)
    if language:
        query = query.where(Review.language == language)
    if voted_up is not None:
        query = query.where(Review.voted_up == voted_up)

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    result = await db.execute(
        query.order_by(Review.timestamp_created.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    reviews = result.scalars().all()
    return {
        "items": [ReviewOut.model_validate(r).model_dump() for r in reviews],
        "total": total or 0,
        "page": page,
        "page_size": page_size,
    }


@router.get("/languages")
async def review_languages(db: AsyncSession = Depends(get_db)):
    """获取评论语言分布"""
    result = await db.execute(
        select(Review.language, func.count(Review.id))
        .group_by(Review.language)
        .order_by(func.count(Review.id).desc())
        .limit(20)
    )
    return {"items": [{"language": r[0] or "unknown", "count": r[1]} for r in result]}
