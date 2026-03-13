<img width="1223" height="517" alt="Screenshot 2026-03-12 at 8 30 27 PM" src="https://github.com/user-attachments/assets/94160a0a-28e4-43af-be50-df2e38269637" />



# 📈 Finance Twitter Intelligence Dashboard

> A real-time NLP dashboard that scrapes finance Twitter/X daily, analyzes market sentiment, surfaces trending topics by sector, and cross-references social signals with live market data.

**Live App:** [https://finance-twitter-aj1m153.streamlit.app/](https://finance-twitter-aj1m153.streamlit.app/)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running Locally](#running-locally)
- [Deployment](#deployment)
- [How It Works](#how-it-works)
- [NLP Pipeline](#nlp-pipeline)
- [Market Data](#market-data)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Finance Twitter is one of the most real-time sources of market intelligence available — traders, analysts, and institutions share signals, reactions, and forecasts the moment news breaks. This dashboard automates the process of monitoring that signal at scale.

Every time you hit **Scrape & Analyze Now**, the app:

1. Scrapes hundreds of finance-related tweets across 10 curated search queries
2. Runs a custom lexicon-based sentiment engine tuned for financial language
3. Clusters tweets into topic groups using TF-IDF + KMeans
4. Classifies tweets into finance sectors (Tech, Energy, Financials, Macro, Healthcare)
5. Extracts ticker mentions and named entities (companies, people, money values)
6. Pulls live market data for all major indices, sector ETFs, and mentioned tickers
7. Cross-references Twitter buzz with actual price performance

The result is a single dashboard giving analysts a synthesized view of what the market is talking about and how it's moving.

---

## Features

### 🌍 Market Overview
- Live prices and daily % change for S&P 500, NASDAQ, Dow Jones, Russell 2000, and VIX
- Interactive sector heatmap showing all 10 SPDR sector ETFs (XLK, XLF, XLE, etc.)
- Color-coded red/green visualization for instant directional reading

### 🔥 Trending Topics
- Sector pie chart showing tweet volume distribution across finance categories
- Topic clustering — tweets grouped into 6 thematic clusters with keyword labels
- Interactive expandable cards showing representative tweets per cluster
- Word cloud visualization of the day's most prominent finance language

### 📊 Sentiment Analysis
- Bullish / Bearish / Neutral classification for every tweet
- Overall sentiment donut chart
- Hourly sentiment trend line (last 24 hours)
- Top 5 highest-engagement bullish tweets surfaced in green
- Top 5 highest-engagement bearish tweets surfaced in red

### 🏷️ Ticker Intelligence
- Most mentioned tickers ranked by frequency across all scraped tweets
- Bar chart of top 10 tickers by mention count
- Scatter plot: Twitter mention volume vs. actual price change % — reveals divergences between social buzz and market reality
- Analyst signals panel: VIX spike alerts, weakest and strongest sectors of the day

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| UI Framework | Streamlit | Dashboard rendering and interactivity |
| Scraping | httpx + BeautifulSoup | HTTP requests and HTML parsing for Nitter instances |
| Scraping fallback | fake-useragent | Rotating user agents to reduce block rate |
| Sentiment NLP | Custom lexicon engine | Finance-tuned bullish/bearish/neutral scoring |
| Topic Modeling | scikit-learn TF-IDF + KMeans | Tweet clustering into thematic groups |
| Sector Classification | Keyword matching | Maps tweets to finance sectors |
| Entity Extraction | Regex NER | Extracts tickers, companies, people, money values |
| Market Data | yfinance | Live prices, sector ETFs, index performance |
| Visualization | Plotly Express | Interactive charts and scatter plots |
| Word Cloud | wordcloud + matplotlib | Visual frequency map of finance language |
| Data Handling | pandas | DataFrame operations throughout the pipeline |
| Environment | python-dotenv | Secrets and config management |

---

## Project Structure

```
finance_twitter_intel/
│
├── app.py                        # Main Streamlit application
│
├── scraper/
│   ├── __init__.py
│   └── twitter_scraper.py        # Nitter-based scraper with mock data fallback
│
├── nlp/
│   ├── __init__.py
│   ├── sentiment.py              # Lexicon-based finance sentiment analyzer
│   ├── entities.py               # Regex ticker + entity extraction
│   └── topics.py                 # TF-IDF topic modeling + sector classification
│
├── market/
│   ├── __init__.py
│   └── market_data.py            # yfinance market snapshot + ticker details
│
├── requirements.txt              # Python dependencies
├── .gitignore                    # Excludes venv, .env, __pycache__
└── README.md                     # This file
```

---

## Installation

### Prerequisites
- Python 3.9 – 3.12 (Python 3.13+ has compatibility issues with some dependencies)
- pip
- Git

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/finance-twitter-intel.git
cd finance-twitter-intel
```

### Step 2 — Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Environment variables (optional)
Create a `.env` file in the root directory if you plan to add API keys later:
```bash
touch .env
```

---

## Running Locally

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

### Optional: better performance
```bash
xcode-select --install       # macOS only
pip install watchdog          # enables fast file watching / auto-reload
```

---

## Deployment

The app is deployed on **Streamlit Community Cloud** (free tier).

### To deploy your own instance:

1. Fork this repository on GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click **New app**
5. Select your forked repo, set branch to `main`, main file to `app.py`
6. Click **Deploy**

Streamlit Cloud handles all dependency installation automatically via `requirements.txt`.

---

## How It Works

### Scraping Strategy

The scraper targets 10 finance search queries covering broad market terms, sector-specific language, and analyst vocabulary:

```python
FINANCE_QUERIES = [
    "stock market",
    "S&P500 SPX",
    "Fed interest rates",
    "inflation economy",
    "tech stocks AI semiconductor",
    "energy oil gas stocks",
    "banking finance earnings",
    "healthcare biotech FDA",
    "bull market bear market",
    "earnings guidance outlook",
]
```

It first attempts to scrape via public Nitter instances (open-source Twitter frontends). If all instances are unavailable — which is common since X actively blocks them — it falls back to a mock dataset of realistic finance tweets that exercises the full NLP pipeline identically.

**Caching:** All scraped data is cached for 30 minutes using `@st.cache_data(ttl=1800)` to avoid redundant scrapes and stay within rate limits.

---

## NLP Pipeline

### Sentiment Analysis (`nlp/sentiment.py`)

Rather than a heavy transformer model, the app uses a custom **finance lexicon** approach tuned specifically for market language. This gives faster inference, zero dependency on torch/transformers, and works on all Python versions.

**Scoring logic:**
- Counts bullish signal words (surge, rally, beat, breakout, upgrade...)
- Counts bearish signal words (crash, plunge, miss, downgrade, recession...)
- Applies an intensity multiplier when intensifiers are detected (massive, extremely...)
- Flips scores when negation words are present (not, never, barely...)
- Returns `positive`, `negative`, or `neutral` with a confidence score

### Topic Modeling (`nlp/topics.py`)

Uses **TF-IDF vectorization** + **KMeans clustering** to group tweets into thematic clusters:

1. Text is cleaned — URLs, mentions, hashtag symbols, and special characters removed
2. TF-IDF vectors built with bigram support (`ngram_range=(1,2)`) and finance-specific stopwords
3. KMeans clusters the vectors into N topics (default: 6)
4. Top 8 TF-IDF terms per cluster centroid become the topic keywords
5. Each cluster is labeled with its top 3 keywords

### Sector Classification (`nlp/topics.py`)

A fast keyword-matching classifier maps each tweet to one of 6 finance sectors:

| Sector | Signal keywords |
|---|---|
| Technology | ai, tech, semiconductor, nvidia, apple, chip |
| Energy | oil, gas, crude, opec, xle, exxon |
| Financials | bank, fed, rates, interest, goldman, jpmorgan |
| Healthcare | biotech, fda, pharma, pfizer, mrna |
| Macro | inflation, cpi, recession, gdp, yield, treasury |
| Equities | spy, nasdaq, qqq, earnings, bull, bear, rally |

### Entity Extraction (`nlp/entities.py`)

Pure regex-based NER — no spaCy dependency — making it fully compatible with Python 3.14+:

- **Tickers:** matches `$NVDA` patterns and bare uppercase symbols against a watchlist of 40+ known tickers
- **Companies:** matches against a curated list of major financial institutions and public companies
- **People:** matches known market personalities (Powell, Buffett, Musk, Dimon...)
- **Money / Percent:** regex patterns for `$4.2B`, `18%` etc.

---

## Market Data

Live data is pulled from **Yahoo Finance** via the `yfinance` library — no API key required.

### Indices tracked
S&P 500, NASDAQ Composite, Dow Jones Industrial Average, Russell 2000, VIX

### Sector ETFs tracked
XLK, XLV, XLF, XLE, XLY, XLI, XLB, XLRE, XLU, XLC

### Per-ticker data
For tickers extracted from tweets, the app fetches: current price, daily % change, sector, market cap, and company name.

Market data is cached for 5 minutes (`ttl=300`) — more frequent than tweet data since prices move continuously.

---

## Roadmap

- [ ] **SQLite historical storage** — persist daily sentiment scores to track trends over weeks
- [ ] **Email / Slack alerts** — notify when sentiment flips sharply on a watched ticker
- [ ] **Options flow correlation** — cross-reference Twitter signals with unusual options activity
- [ ] **Earnings calendar integration** — flag tickers with upcoming earnings in the ticker view
- [ ] **Twitter API v2 support** — drop-in upgrade from Nitter scraping for production use
- [ ] **User watchlist** — let users pin specific tickers to track throughout the day
- [ ] **News RSS integration** — add Reuters / Bloomberg RSS feeds alongside Twitter data
- [ ] **Scheduled daily digest** — auto-generate a morning briefing PDF from overnight signals

---

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add: your feature description"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

Please keep PRs focused on a single feature or fix. For major changes, open an issue first to discuss the approach.

---

## License

© 2026 Ajim. All rights reserved.
This project is not open source. No part of this codebase may be used, 
copied, or distributed without explicit written permission from the author.
---

*Built with Python, Streamlit, and a lot of coffee. If this helped you, give it a star.*
