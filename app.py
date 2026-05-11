import streamlit as st
import httpx
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from charts import (
    chart_sentiment_over_time,
    chart_source_breakdown,
    chart_sentiment_donut,
    chart_keywords,
)

API_BASE = "http://localhost:8000"

# ─── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Sentiment Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS for dark theme ────────────────────────────────────
st.markdown(
    """
<style>
.metric-card {
    background: #1E293B;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    border-left: 4px solid #0F766E;
}
.positive { color: #10B981; font-weight: bold; }
.negative { color: #EF4444; font-weight: bold; }
</style>
""",
    unsafe_allow_html=True,
)


# ─── Helper to call API ───────────────────────────────────────────
def api_get(endpoint: str, params=None):
    try:
        r = httpx.get(f"{API_BASE}{endpoint}", params=params, timeout=60)
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}. Make sure the FastAPI server is running.")
        return None


def api_post(endpoint: str, json_body: dict):
    try:
        r = httpx.post(f"{API_BASE}{endpoint}", json=json_body, timeout=30)
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


# ─── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.title("📰 Sentiment Dashboard")
    st.caption("Real-time news sentiment analysis")
    st.divider()

    # Time range selector
    hours = st.selectbox(
        "Time range",
        options=[6, 12, 24, 48, 72],
        index=2,
        format_func=lambda x: f"Last {x} hours",
    )

    st.divider()

    # Refresh button
    if st.button("🔄 Refresh Feed", type="primary", use_container_width=True):
        with st.spinner("Fetching and analyzing news..."):
            result = api_get("/feed")
        if result:
            st.success(f"Fetched {result['fetched']} articles")
            st.metric("Positive", result["positive"])
            st.metric("Negative", result["negative"])

    st.divider()

    # Custom text analyzer
    st.subheader("Analyze Your Own Text")
    custom_text = st.text_area(
        label="Enter any text:",
        placeholder="Paste a headline or sentence here...",
        height=100,
    )
    if st.button("Analyze", use_container_width=True) and custom_text:
        with st.spinner("Analyzing..."):
            result = api_post("/analyze", {"text": custom_text})
        if result:
            label = result["label"]
            score = result["score"]
            color = "positive" if label == "POSITIVE" else "negative"
            st.markdown(
                f"**Result:** <span class='{color}'>{label}</span>",
                unsafe_allow_html=True,
            )
            st.progress(score)
            st.caption(f"Confidence: {score:.1%}")


# ─── Main dashboard area ──────────────────────────────────────────
st.title("Real-Time News Sentiment")

# Load dashboard data
data = api_get("/dashboard", params={"hours": hours})

if not data or not data.get("articles"):
    st.info("No data yet. Click **Refresh Feed** in the sidebar to fetch news.")
    st.stop()

articles = data["articles"]
time_data = data["time_data"]
keywords = data["keywords"]

# ── KPI row ───────────────────────────────────────────────────────
total = len(articles)
pos = sum(1 for a in articles if a["label"] == "POSITIVE")
neg = total - pos
avg_sent = sum(a["sentiment"] for a in articles) / total if total else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Articles", total)
col2.metric("Positive", pos, delta=f"{pos / total:.0%}")
col3.metric("Negative", neg, delta=f"-{neg / total:.0%}", delta_color="inverse")
col4.metric("Avg Sentiment", f"{avg_sent:+.3f}")

st.divider()

# ── Row 1: Timeline + Donut ───────────────────────────────────────
left, right = st.columns([2, 1])
with left:
    st.plotly_chart(chart_sentiment_over_time(time_data), use_container_width=True)
with right:
    st.plotly_chart(chart_sentiment_donut(articles), use_container_width=True)

# ── Row 2: Source bars + Keywords ─────────────────────────────────
left2, right2 = st.columns(2)
with left2:
    st.plotly_chart(chart_source_breakdown(articles), use_container_width=True)
with right2:
    st.plotly_chart(chart_keywords(keywords), use_container_width=True)

# ── Recent headlines table ────────────────────────────────────────
st.divider()
st.subheader("Recent Headlines")

for article in articles[:20]:
    label = article["label"]
    score = article["score"]
    color = "positive" if label == "POSITIVE" else "negative"
    badge = "🟢" if label == "POSITIVE" else "🔴"

    st.markdown(
        f"{badge} <span class='{color}'>{label} {score:.0%}</span> — "
        f"[{article['title']}]({article['url']}) <small>({article['source']})</small>",
        unsafe_allow_html=True,
    )
