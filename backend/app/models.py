from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Game(Base):
    __tablename__ = "games"

    appid = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False)
    type = Column(String(50), default="game")
    is_free = Column(Boolean, default=False)
    release_date = Column(String(50))
    metacritic_score = Column(Integer)
    recommendations_total = Column(Integer)
    price = Column(Float, default=0.0)
    about_text = Column(Text)
    header_image = Column(String(500))
    developers = Column(String(500))
    publishers = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    genres = relationship("GameGenre", back_populates="game")
    reviews = relationship("Review", back_populates="game")

    __table_args__ = (
        Index("idx_games_price", "price"),
        Index("idx_games_metacritic", "metacritic_score"),
    )


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    game_genres = relationship("GameGenre", back_populates="genre")


class GameGenre(Base):
    __tablename__ = "game_genres"

    appid = Column(Integer, ForeignKey("games.appid", ondelete="CASCADE"), primary_key=True)
    genreid = Column(Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)

    game = relationship("Game", back_populates="genres")
    genre = relationship("Genre", back_populates="game_genres")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_id = Column(String(100), unique=True)
    appid = Column(Integer, ForeignKey("games.appid", ondelete="CASCADE"), nullable=False)
    voted_up = Column(Boolean)
    review_text = Column(Text)
    language = Column(String(20))
    timestamp_created = Column(DateTime)
    author_steamid = Column(String(100))
    votes_funny = Column(Integer, default=0)
    votes_helpful = Column(Integer, default=0)

    game = relationship("Game", back_populates="reviews")

    __table_args__ = (
        Index("idx_reviews_appid", "appid"),
        Index("idx_reviews_language", "language"),
        Index("idx_reviews_voted_up", "voted_up"),
    )


class RealTimeStats(Base):
    """Steam API 实时拉取的游戏在线数据"""
    __tablename__ = "realtime_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    appid = Column(Integer, nullable=False)
    player_count = Column(Integer, default=0)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_stats_appid_time", "appid", "recorded_at"),
    )
