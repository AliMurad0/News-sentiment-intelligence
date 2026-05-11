from transformers import pipeline
from dataclasses import dataclass
from typing import List
from collections import Counter
import re, nltk
from config import MODEL_NAME, BATCH_SIZE, MAX_TEXT_LENGTH
from fetcher import Article

# Download stopwords list on first run (small, ~1MB)
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
from nltk.corpus import stopwords

STOPWORDS = set(stopwords.words("english"))


@dataclass
class ScoredArticle:
    """An Article with sentiment score attached."""

    article: Article
    label: str  # 'POSITIVE' or 'NEGATIVE'
    score: float  # confidence 0.0 - 1.0
    sentiment: float  # normalized: +1.0 (very positive) to -1.0 (very negative)


class SentimentAnalyzer:
    """
    Wraps DistilBERT for sentiment analysis.
    Loads the model once, reuses it for all requests.
    """

    def __init__(self):
        print(f"Loading model: {MODEL_NAME}")
        print("(Downloads ~250MB on first run, then cached locally)")

        # pipeline() handles: download, tokenization, inference, decoding
        self.classifier = pipeline(
            task="sentiment-analysis",
            model=MODEL_NAME,
            truncation=True,
            max_length=MAX_TEXT_LENGTH,
        )
        print("Model loaded successfully!")

    def score_articles(self, articles: List[Article]) -> List[ScoredArticle]:
        """
        Runs DistilBERT on a list of articles in batches.
        Returns ScoredArticle objects with sentiment attached.
        """
        if not articles:
            return []

        # Extract text from each article for the model
        texts = [a.text for a in articles]

        # Run inference in batches (much faster than one at a time)
        print(f"Scoring {len(texts)} articles in batches of {BATCH_SIZE}...")
        results = self.classifier(texts, batch_size=BATCH_SIZE)

        scored = []
        for article, result in zip(articles, results):
            label = result["label"]  # 'POSITIVE' or 'NEGATIVE'
            score = result["score"]  # confidence 0.0 - 1.0

            # Convert to a -1.0 to +1.0 scale for charting
            # POSITIVE with 0.9 confidence -> +0.9
            # NEGATIVE with 0.9 confidence -> -0.9
            sentiment = score if label == "POSITIVE" else -score

            scored.append(
                ScoredArticle(
                    article=article,
                    label=label,
                    score=score,
                    sentiment=sentiment,
                )
            )

        return scored

    def score_text(self, text: str) -> dict:
        """Score a single piece of text. Used by the /analyze API endpoint."""
        result = self.classifier([text])[0]
        label = result["label"]
        score = result["score"]
        return {
            "label": label,
            "score": round(score, 4),
            "sentiment": round(score if label == "POSITIVE" else -score, 4),
        }


def extract_keywords(articles: List[ScoredArticle], top_n: int = 20) -> List[dict]:
    """
    Extracts the most frequent meaningful words from article titles.
    Returns list of {word, count, avg_sentiment} dicts.
    """
    word_sentiments = {}  # word -> list of sentiment scores

    for sa in articles:
        # Tokenize: lowercase, remove punctuation, split
        words = re.sub(r"[^a-zA-Z\s]", "", sa.article.title.lower()).split()

        for word in words:
            # Filter: skip stopwords and short words
            if word not in STOPWORDS and len(word) > 3:
                if word not in word_sentiments:
                    word_sentiments[word] = []
                word_sentiments[word].append(sa.sentiment)

    # Build keyword list with frequency and average sentiment
    keywords = []
    for word, sentiments in word_sentiments.items():
        keywords.append(
            {
                "word": word,
                "count": len(sentiments),
                "avg_sentiment": round(sum(sentiments) / len(sentiments), 3),
            }
        )

    # Sort by frequency, return top N
    keywords.sort(key=lambda x: x["count"], reverse=True)
    return keywords[:top_n]


# Test: python src/analyzer.py
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    tests = [
        "Stock markets reach record high as inflation eases",
        "Major data breach exposes millions of user records",
        "Scientists discover breakthrough cancer treatment",
    ]
    for text in tests:
        result = analyzer.score_text(text)
        print(f"{result['label']:8} ({result['score']:.2%}) | {text[:60]}")
