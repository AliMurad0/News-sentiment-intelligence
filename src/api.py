from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

# Import our modules
from fetcher import fetch_all_feeds
from analyzer import SentimentAnalyzer, extract_keywords
from storage import SentimentDB
from config import API_HOST, API_PORT


# ─── App setup ────────────────────────────────────────────────────
app = FastAPI(
    title="Sentiment Dashboard API",
    description="Real-time news sentiment analysis powered by DistilBERT",
    version="1.0.0",
)

# Allow Streamlit (running on port 8501) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Startup: load model and DB once ──────────────────────────────
# These are loaded once when the server starts, reused for all requests
analyzer = None
db = None


@app.on_event("startup")
async def startup():
    global analyzer, db
    print("Loading DistilBERT model...")
    analyzer = SentimentAnalyzer()
    db = SentimentDB()
    print("API ready!")


# ─── Request / Response models ────────────────────────────────────
class TextInput(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    text: str
    label: str
    score: float
    sentiment: float


# ─── Endpoints ────────────────────────────────────────────────────
@app.get("/")
def health_check():
    """Quick health check — confirms API is running."""
    return {"status": "ok", "message": "Sentiment API is running"}


@app.post("/analyze", response_model=SentimentResponse)
def analyze_text(body: TextInput):
    """
    Analyze any custom text for sentiment.
    Used by the 'Analyze your own text' box in the dashboard.
    """
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    result = analyzer.score_text(body.text)
    return SentimentResponse(text=body.text[:200], **result)


@app.get("/feed")
def refresh_feed():
    """
    Fetches all RSS feeds, scores every headline, saves to DB.
    Returns summary stats for the fetch.
    """
    # 1. Fetch articles from all RSS feeds
    articles = fetch_all_feeds()

    # 2. Score every article with DistilBERT
    scored = analyzer.score_articles(articles)

    # 3. Save to database
    saved_count = db.save_articles(scored)

    # 4. Return summary
    labels = [s.label for s in scored]
    return {
        "fetched": len(articles),
        "saved": saved_count,
        "positive": labels.count("POSITIVE"),
        "negative": labels.count("NEGATIVE"),
    }


@app.get("/dashboard")
def get_dashboard_data(hours: int = 24):
    """
    Returns everything the dashboard needs in one request:
    - recent articles with sentiment scores
    - sentiment over time (for line chart)
    - keywords (for bar chart)
    """
    articles = db.get_recent(hours=hours)
    time_data = db.get_sentiment_over_time(hours=hours)

    # Extract keywords from in-memory scored articles
    # (We rebuild ScoredArticle objects from stored data)
    keywords = []
    if articles:
        from dataclasses import dataclass
        from fetcher import Article
        from analyzer import ScoredArticle
        from datetime import datetime

        pseudo_scored = []
        for a in articles:
            art = Article(
                id=a["id"],
                title=a["title"],
                summary="",
                source=a["source"],
                url=a["url"],
                published=datetime.fromisoformat(a["published"]),
                text=a["title"],
            )
            pseudo_scored.append(
                ScoredArticle(
                    article=art,
                    label=a["label"],
                    score=a["score"],
                    sentiment=a["sentiment"],
                )
            )
        keywords = extract_keywords(pseudo_scored)

    return {
        "articles": articles,
        "time_data": time_data,
        "keywords": keywords,
        "total": len(articles),
    }


# Run directly: python src/api.py
if __name__ == "__main__":
    uvicorn.run("api:app", host=API_HOST, port=API_PORT, reload=True)
