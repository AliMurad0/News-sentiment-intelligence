import feedparser
import hashlib
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional
from config import RSS_FEEDS


@dataclass
class Article:
    """Represents a single fetched news article."""

    id: str  # unique hash of title+source
    title: str  # headline text
    summary: str  # article summary (may be empty)
    source: str  # feed name e.g. 'BBC Technology'
    url: str  # link to full article
    published: datetime  # when article was published
    text: str  # title + summary combined for analysis


def fetch_feed(source_name: str, url: str) -> List[Article]:
    """
    Fetches all articles from a single RSS feed URL.
    Returns a list of Article objects.
    """
    articles = []

    try:
        # feedparser handles HTTP, XML parsing, and encoding automatically
        feed = feedparser.parse(url)

        for entry in feed.entries:
            title = getattr(entry, "title", "").strip()
            summary = getattr(entry, "summary", "").strip()

            # Skip empty entries
            if not title:
                continue

            # Parse publication date (feedparser normalizes this)
            published = datetime.now()  # fallback
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])

            # Create a unique ID by hashing title + source
            # This prevents storing the same article twice
            uid = hashlib.md5(f"{title}{source_name}".encode()).hexdigest()[:12]

            # Combine title + summary for richer sentiment analysis
            text = f"{title}. {summary}" if summary else title
            # Truncate to avoid exceeding model token limit
            text = text[:500]

            articles.append(
                Article(
                    id=uid,
                    title=title,
                    summary=summary[:300] if summary else "",
                    source=source_name,
                    url=getattr(entry, "link", ""),
                    published=published,
                    text=text,
                )
            )

    except Exception as e:
        print(f"Error fetching {source_name}: {e}")

    return articles


def fetch_all_feeds(feeds: dict = None) -> List[Article]:
    """
    Fetches articles from all configured RSS feeds.
    Returns combined, deduplicated list sorted by published date.
    """
    if feeds is None:
        feeds = RSS_FEEDS

    all_articles = []
    seen_ids = set()

    for source_name, url in feeds.items():
        print(f"Fetching: {source_name}...")
        articles = fetch_feed(source_name, url)

        # Deduplicate across feeds
        for article in articles:
            if article.id not in seen_ids:
                seen_ids.add(article.id)
                all_articles.append(article)

    # Sort newest first
    all_articles.sort(key=lambda x: x.published, reverse=True)

    print(f"Fetched {len(all_articles)} unique articles from {len(feeds)} feeds")
    return all_articles


# Test: python src/fetcher.py
if __name__ == "__main__":
    articles = fetch_all_feeds()
    for a in articles[:5]:
        print(f"[{a.source}] {a.title[:80]}")
