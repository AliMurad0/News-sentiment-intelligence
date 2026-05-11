import os
from dotenv import load_dotenv

load_dotenv()

# ─── Model ────────────────────────────────────────────────────────
MODEL_NAME = os.getenv("MODEL_NAME", "distilbert-base-uncased-finetuned-sst-2-english")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 16))
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", 512))

# ─── RSS Feed Sources ─────────────────────────────────────────────
# You can add or remove feeds from this list freely
RSS_FEEDS = {
    "BBC Technology": "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "CNN Top Stories": "http://rss.cnn.com/rss/edition.rss",
    "TechCrunch": "https://techcrunch.com/feed/",
}

# ─── Refresh interval ─────────────────────────────────────────────
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 300))  # seconds

# ─── Database ─────────────────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", "./data/sentiment.db")

# ─── API ──────────────────────────────────────────────────────────
API_HOST = "0.0.0.0"
API_PORT = 8000
