from sqlalchemy import create_engine, Column, String, Float, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Session
from datetime import datetime, timedelta
from typing import List, Optional
from config import DB_PATH
from analyzer import ScoredArticle


# ─── Database Model ───────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


class ArticleRecord(Base):
    """SQLAlchemy model — maps to the 'articles' table in SQLite."""

    __tablename__ = "articles"

    id = Column(String, primary_key=True)  # unique article hash
    title = Column(Text)  # headline
    source = Column(String)  # feed name
    url = Column(String)  # article link
    published = Column(DateTime)  # when published
    analyzed = Column(DateTime, default=datetime.now)  # when we scored it
    label = Column(String)  # POSITIVE / NEGATIVE
    score = Column(Float)  # confidence 0-1
    sentiment = Column(Float)  # -1.0 to +1.0


# ─── Database Manager ─────────────────────────────────────────────
class SentimentDB:
    """Handles all database read/write operations."""

    def __init__(self, db_path: str = DB_PATH):
        # Create SQLite engine (creates the .db file if it doesn't exist)
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)

        # Create tables if they don't exist yet
        Base.metadata.create_all(self.engine)
        print(f"Database ready at {db_path}")

    def save_articles(self, scored_articles: List[ScoredArticle]) -> int:
        """
        Saves scored articles to database.
        Skips articles already in DB (by ID).
        Returns the number of NEW articles saved.
        """
        saved = 0
        with Session(self.engine) as session:
            for sa in scored_articles:
                # Check if this article is already stored
                existing = session.get(ArticleRecord, sa.article.id)
                if existing:
                    continue  # skip duplicates

                record = ArticleRecord(
                    id=sa.article.id,
                    title=sa.article.title,
                    source=sa.article.source,
                    url=sa.article.url,
                    published=sa.article.published,
                    label=sa.label,
                    score=sa.score,
                    sentiment=sa.sentiment,
                )
                session.add(record)
                saved += 1

            session.commit()

        print(f"Saved {saved} new articles to database")
        return saved

    def get_recent(self, hours: int = 24) -> List[dict]:
        """Fetches articles from the last N hours as a list of dicts."""
        cutoff = datetime.now() - timedelta(hours=hours)

        with Session(self.engine) as session:
            records = (
                session.query(ArticleRecord)
                .filter(ArticleRecord.analyzed >= cutoff)
                .order_by(ArticleRecord.analyzed.desc())
                .all()
            )

            return [
                {
                    "id": r.id,
                    "title": r.title,
                    "source": r.source,
                    "url": r.url,
                    "published": r.published.isoformat(),
                    "analyzed": r.analyzed.isoformat(),
                    "label": r.label,
                    "score": r.score,
                    "sentiment": r.sentiment,
                }
                for r in records
            ]

    def get_sentiment_over_time(self, hours: int = 24) -> List[dict]:
        """
        Returns average sentiment per hour for trend charting.
        Groups articles by hour bucket and averages the sentiment.
        """
        articles = self.get_recent(hours=hours)
        if not articles:
            return []

        # Group by hour
        buckets = {}
        for a in articles:
            dt = datetime.fromisoformat(a["analyzed"])
            hour_key = dt.strftime("%Y-%m-%d %H:00")
            if hour_key not in buckets:
                buckets[hour_key] = []
            buckets[hour_key].append(a["sentiment"])

        # Average each bucket
        return [
            {"hour": k, "avg_sentiment": round(sum(v) / len(v), 4), "count": len(v)}
            for k, v in sorted(buckets.items())
        ]
