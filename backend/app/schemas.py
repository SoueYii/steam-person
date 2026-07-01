from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ─── Game ─────────────────────────────────────────────────────────────────
class GameOut(BaseModel):
    appid: int
    name: str
    type: str | None = None
    is_free: bool | None = None
    release_date: str | None = None
    metacritic_score: int | None = None
    recommendations_total: int | None = None
    price: float | None = None
    developers: str | None = None
    publishers: str | None = None

    class Config:
        from_attributes = True


class GameDetail(GameOut):
    about_text: str | None = None
    genres: list[str] = []
    review_count: int = 0
    positive_rate: float | None = None


# ─── Review ───────────────────────────────────────────────────────────────
class ReviewOut(BaseModel):
    id: int
    appid: int
    voted_up: bool | None = None
    review_text: str | None = None
    language: str | None = None
    timestamp_created: datetime | None = None

    class Config:
        from_attributes = True


# ─── Analytics ────────────────────────────────────────────────────────────
class GenreSummary(BaseModel):
    genre: str
    game_count: int
    avg_price: float
    avg_metacritic: float
    total_reviews: int
    positive_rate: float


class PriceDistribution(BaseModel):
    tier: str
    game_count: int
    avg_rating: float
    total_reviews: int


class TrendPoint(BaseModel):
    date: str
    count: int
    avg_price: float
    positive_rate: float


class RealtimePlayer(BaseModel):
    appid: int
    game_name: str
    player_count: int
    recorded_at: datetime


# ─── Query ────────────────────────────────────────────────────────────────
class Pagination(BaseModel):
    page: int = 1
    page_size: int = 20


class AnalyticsFilter(BaseModel):
    genre: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    language: str | None = None
    date_from: str | None = None
    date_to: str | None = None
