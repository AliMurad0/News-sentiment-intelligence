import plotly.graph_objects as go
from typing import List
import pandas as pd

# Brand colors used across all charts
COLORS = {
    "positive": "#10B981",  # green
    "negative": "#EF4444",  # red
    "neutral": "#6B7280",   # gray
    "bg": "#0F172A",        # dark background
    "grid": "#1E293B",      # grid lines
    "text": "#E2E8F0",      # axis labels
}


def chart_sentiment_over_time(time_data: List[dict]) -> go.Figure:
    """
    Line chart: average sentiment per hour.
    """
    if not time_data:
        return _empty_chart("No data yet — run a fetch first")

    df = pd.DataFrame(time_data)

    fig = go.Figure()

    # Sentiment trend line
    fig.add_trace(
        go.Scatter(
            x=df["hour"],
            y=df["avg_sentiment"],
            mode="lines+markers",
            name="Avg Sentiment",
            line=dict(color=COLORS["positive"], width=2),
            marker=dict(size=6),
            hovertemplate="%{x}<br>Sentiment: %{y:.3f}<extra></extra>",
        )
    )

    # Neutral reference line
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color=COLORS["neutral"],
        annotation_text="Neutral",
        annotation_position="right",
    )

    # Positive / negative shaded zones
    fig.add_hrect(
        y0=0,
        y1=1,
        fillcolor=COLORS["positive"],
        opacity=0.05,
        line_width=0,
    )

    fig.add_hrect(
        y0=-1,
        y1=0,
        fillcolor=COLORS["negative"],
        opacity=0.05,
        line_width=0,
    )

    fig.update_layout(
        title="Sentiment Over Time",
        xaxis_title="Hour",
        yaxis_title="Avg Sentiment (-1 negative → +1 positive)",

        xaxis=dict(
            gridcolor=COLORS["grid"]
        ),

        yaxis=dict(
            gridcolor=COLORS["grid"],
            range=[-1.1, 1.1]
        ),

        **_dark_theme(),
    )

    return fig


def chart_source_breakdown(articles: List[dict]) -> go.Figure:
    """
    Grouped bar chart: positive vs negative count per news source.
    """
    if not articles:
        return _empty_chart("No data yet")

    df = pd.DataFrame(articles)

    grouped = (
        df.groupby(["source", "label"])
        .size()
        .reset_index(name="count")
    )

    pos = grouped[grouped["label"] == "POSITIVE"]
    neg = grouped[grouped["label"] == "NEGATIVE"]

    sources = df["source"].unique().tolist()

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=sources,
            y=[pos[pos["source"] == s]["count"].sum() for s in sources],
            name="Positive",
            marker_color=COLORS["positive"],
            hovertemplate="%{x}<br>Positive: %{y}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            x=sources,
            y=[neg[neg["source"] == s]["count"].sum() for s in sources],
            name="Negative",
            marker_color=COLORS["negative"],
            hovertemplate="%{x}<br>Negative: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Sentiment by News Source",
        barmode="group",
        xaxis_title="Source",
        yaxis_title="Article Count",

        xaxis=dict(
            gridcolor=COLORS["grid"]
        ),

        yaxis=dict(
            gridcolor=COLORS["grid"]
        ),

        **_dark_theme(),
    )

    return fig


def chart_sentiment_donut(articles: List[dict]) -> go.Figure:
    """
    Donut chart: overall positive vs negative split.
    """
    if not articles:
        return _empty_chart("No data yet")

    labels = [a["label"] for a in articles]

    pos_count = labels.count("POSITIVE")
    neg_count = labels.count("NEGATIVE")

    fig = go.Figure(
        go.Pie(
            labels=["Positive", "Negative"],
            values=[pos_count, neg_count],
            hole=0.6,
            marker_colors=[
                COLORS["positive"],
                COLORS["negative"]
            ],
            textinfo="label+percent",
            hovertemplate="%{label}: %{value} articles (%{percent})<extra></extra>",
        )
    )

    fig.update_layout(
        title="Overall Sentiment Split",
        annotations=[
            dict(
                text=f"{len(articles)}<br>articles",
                x=0.5,
                y=0.5,
                font_size=14,
                showarrow=False,
                font_color=COLORS["text"],
            )
        ],
        **_dark_theme(),
    )

    return fig


def chart_keywords(keywords: List[dict]) -> go.Figure:
    """
    Horizontal keyword frequency chart.
    """
    if not keywords:
        return _empty_chart("No keywords yet")

    kw = keywords[:15]

    words = [k["word"] for k in kw]
    counts = [k["count"] for k in kw]
    sentiments = [k["avg_sentiment"] for k in kw]

    colors = [
        COLORS["positive"] if s > 0 else COLORS["negative"]
        for s in sentiments
    ]

    fig = go.Figure(
        go.Bar(
            x=counts,
            y=words,
            orientation="h",
            marker_color=colors,
            hovertemplate="%{y}: %{x} mentions<extra></extra>",
        )
    )

    fig.update_layout(
        title="Top Keywords (colored by sentiment)",
        xaxis_title="Mentions",

        xaxis=dict(
            gridcolor=COLORS["grid"]
        ),

        yaxis=dict(
            gridcolor=COLORS["grid"],
            categoryorder="total ascending",
        ),

        **_dark_theme(),
    )

    return fig


# ───────────────── Helpers ─────────────────

def _dark_theme() -> dict:
    """
    Shared dark theme settings.
    """
    return dict(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font_color=COLORS["text"],
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=40, t=50, b=40),
    )


def _empty_chart(message: str) -> go.Figure:
    """
    Placeholder chart when no data exists.
    """
    fig = go.Figure()

    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(
            size=16,
            color=COLORS["neutral"]
        ),
    )

    fig.update_layout(**_dark_theme())

    return fig