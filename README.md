# 🧠 News Sentiment Intelligence

> Real-time AI-powered news sentiment analysis platform built with FastAPI, Streamlit, Hugging Face Transformers, and Plotly.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow?style=for-the-badge)
![Plotly](https://img.shields.io/badge/Plotly-Visualization-3F4F75?style=for-the-badge&logo=plotly)

---

## 🚀 Overview

News Sentiment Intelligence is a real-time NLP analytics platform that collects live news headlines from multiple RSS feeds, performs AI-powered sentiment analysis using DistilBERT, and visualizes insights through an interactive dashboard.

The system combines:
- 📰 Live News Aggregation
- 🤖 Transformer-Based NLP
- 📊 Interactive Data Visualization
- ⚡ FastAPI Backend Services
- 🗄️ SQLite Data Persistence

---

# ✨ Features

## 📰 Real-Time News Collection

Aggregates headlines from:
- BBC Technology
- BBC Business
- Reuters Business
- CNN Top Stories
- TechCrunch

---

## 🤖 AI Sentiment Analysis

Powered by:

- Hugging Face Transformers
- DistilBERT SST-2
- PyTorch Inference Pipeline

Provides:
- Positive / Negative classification
- Confidence scores
- Normalized sentiment scoring
- Batched inference processing

---

## 📊 Interactive Dashboard

Built using Streamlit + Plotly.

### Dashboard Analytics:
- 📈 Sentiment Trend Analysis
- 🟢 Positive vs 🔴 Negative Distribution
- 🏢 Source-Level Sentiment Breakdown
- 🔑 Keyword Intelligence
- 📰 Real-Time Article Monitoring

---

## ⚡ FastAPI Backend

REST API endpoints:

| Endpoint | Description |
|---|---|
| `GET /` | Health check |
| `GET /feed` | Refresh RSS feeds |
| `GET /dashboard` | Dashboard analytics |
| `POST /analyze` | Analyze custom text |

---

## 🗄️ Persistent Storage

- SQLite Database
- SQLAlchemy ORM
- Automatic article deduplication
- Historical sentiment tracking

---

# 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| NLP | Hugging Face Transformers |
| ML Framework | PyTorch |
| Visualization | Plotly |
| Database | SQLite |
| ORM | SQLAlchemy |
| Data Source | RSS Feeds |

---

# 📁 Project Structure

```text
news-sentiment-intelligence/
│
├── src/
│   ├── analyzer.py
│   ├── api.py
│   ├── charts.py
│   ├── config.py
│   ├── fetcher.py
│   └── storage.py
│
├── data/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/news-sentiment-intelligence.git
cd news-sentiment-intelligence
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Application

## Start FastAPI Backend

```bash
python src/api.py
```

Backend runs at:

```text
http://localhost:8000
```

---

## Start Streamlit Dashboard

Open a second terminal:

```bash
streamlit run app.py
```

Dashboard runs at:

```text
http://localhost:8501
```

---

# 🧪 API Example

## Analyze Custom Text

### Request

```http
POST /analyze
```

### JSON Body

```json
{
  "text": "Markets rally after positive earnings report"
}
```

### Example Response

```json
{
  "label": "POSITIVE",
  "score": 0.998,
  "sentiment": 0.998
}
```

---

# 🧠 Machine Learning Model

Model used:

```text
distilbert-base-uncased-finetuned-sst-2-english
```

Capabilities:
- Binary sentiment classification
- Confidence estimation
- Real-time inference
- Transformer-based NLP

---

# 📊 Dashboard Preview

Features:
- 📈 Sentiment Timeline
- 📰 Headline Monitoring
- 🟢🔴 Sentiment Distribution
- 🔑 Trending Keywords
- 🏢 Source Analytics

---

# 🔮 Future Enhancements

Potential upgrades:
- Multi-class sentiment analysis
- Financial market sentiment tracking
- Kafka streaming pipelines
- PostgreSQL integration
- Docker deployment
- Cloud-native deployment
- User authentication
- Real-time websocket streaming
- GPU acceleration

---

# 📄 License

MIT License

---

# 👨‍💻 Author

## Ali Murad

AI Engineer • NLP • Data Analytics • Full-Stack AI Systems

---

# ⭐ Support

If you found this project useful:

- ⭐ Star the repository
- 🍴 Fork the project
- 🧠 Contribute improvements
- 🚀 Share with others