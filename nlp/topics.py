# nlp/topics.py
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.cluster import KMeans

FINANCE_STOPWORDS = [
    "stock", "market", "today", "amp", "rt", "via", "https", "http",
    "just", "need", "like", "get", "make", "will", "one", "new",
    "time", "year", "week", "day", "going", "know", "think", "said",
    "says", "say", "also", "back", "still", "way", "well", "even",
]

SECTOR_KEYWORDS = {
    "Technology": ["ai", "tech", "semiconductor", "nvidia", "apple", "microsoft", "chip"],
    "Energy":     ["oil", "gas", "energy", "crude", "opec", "xle", "exxon", "chevron"],
    "Financials": ["bank", "banking", "fed", "rates", "interest", "jpmorgan", "goldman"],
    "Healthcare": ["biotech", "fda", "pharma", "drug", "pfizer", "mrna", "healthcare"],
    "Macro":      ["inflation", "cpi", "recession", "gdp", "economy", "treasury", "yield"],
    "Equities":   ["spy", "sp500", "nasdaq", "qqq", "earnings", "bull", "bear", "rally"],
}

def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#(\w+)", r"", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()

def classify_sector(text):
    text_lower = text.lower()
    scores = {}
    for sector, keywords in SECTOR_KEYWORDS.items():
        scores[sector] = sum(1 for kw in keywords if kw in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "General"

def get_sector_breakdown(df):
    df = df.copy()
    df["sector"] = df["content"].apply(classify_sector)
    breakdown = df["sector"].value_counts().reset_index()
    breakdown.columns = ["sector", "count"]
    return breakdown

def extract_topics(df, n_topics=6):
    if df.empty or len(df) < n_topics:
        return {}, df
    texts = df["content"].apply(clean_text).tolist()
    stop_words = list(ENGLISH_STOP_WORDS) + FINANCE_STOPWORDS
    vectorizer = TfidfVectorizer(
        max_features=300,
        stop_words=stop_words,
        ngram_range=(1, 2),
        min_df=2,
    )
    try:
        X = vectorizer.fit_transform(texts)
        n_clusters = min(n_topics, len(df) // 3)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        df = df.copy()
        df["topic"] = labels
        terms = vectorizer.get_feature_names_out()
        topics = {}
        for i in range(n_clusters):
            center = kmeans.cluster_centers_[i]
            top_indices = center.argsort()[-8:][::-1]
            keywords = [terms[j] for j in top_indices]
            topic_tweets = df[df["topic"] == i]
            topics[i] = {
                "keywords":   keywords,
                "count":      len(topic_tweets),
                "label":      " · ".join(keywords[:3]).title(),
                "top_tweets": topic_tweets.nlargest(3, "likes")["content"].tolist()
                              if "likes" in topic_tweets.columns else
                              topic_tweets["content"].head(3).tolist(),
            }
        return topics, df
    except Exception as e:
        print("  Topic modeling error: " + str(e))
        return {}, df
