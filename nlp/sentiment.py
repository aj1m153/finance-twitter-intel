# nlp/sentiment.py
import re
import pandas as pd

# Finance-specific word lists — no heavy ML dependencies
BULLISH_WORDS = [
    "surge", "soar", "rally", "beat", "bullish", "breakout", "buy",
    "upgrade", "outperform", "strong", "gain", "rise", "boom", "growth",
    "positive", "profit", "record", "high", "opportunity", "upside",
    "recover", "rebound", "momentum", "accelerate", "crush", "exceed",
]

BEARISH_WORDS = [
    "crash", "plunge", "fall", "miss", "bearish", "breakdown", "sell",
    "downgrade", "underperform", "weak", "loss", "drop", "bust", "decline",
    "negative", "risk", "low", "warning", "downside", "recession",
    "correction", "selloff", "fear", "collapse", "disappoint", "cut",
]

INTENSIFIERS = ["very", "extremely", "massive", "huge", "major", "significant"]

def analyze_text(text):
    text_lower = text.lower()
    words = re.findall(r"\b\w+\b", text_lower)

    bull_score = sum(1 for w in words if w in BULLISH_WORDS)
    bear_score = sum(1 for w in words if w in BEARISH_WORDS)

    # Boost scores if intensifiers present
    if any(i in text_lower for i in INTENSIFIERS):
        bull_score *= 1.3
        bear_score *= 1.3

    # Negation check
    negations = ["not", "no", "never", "neither", "barely", "hardly"]
    if any(n in text_lower for n in negations):
        bull_score, bear_score = bear_score * 0.5, bull_score * 0.5

    total = bull_score + bear_score + 0.001
    pos = round(bull_score / total, 4)
    neg = round(bear_score / total, 4)
    neu = round(1 - pos - neg, 4)

    if bull_score > bear_score and bull_score > 0:
        sentiment = "positive"
        confidence = round(pos, 4)
    elif bear_score > bull_score and bear_score > 0:
        sentiment = "negative"
        confidence = round(neg, 4)
    else:
        sentiment = "neutral"
        confidence = round(neu, 4)

    return {
        "sentiment":  sentiment,
        "positive":   pos,
        "negative":   neg,
        "neutral":    neu,
        "confidence": confidence,
    }

class FinanceSentimentAnalyzer:
    def __init__(self):
        print("  ✅ Lexicon-based finance sentiment analyzer ready")

    def analyze_batch(self, texts):
        return [analyze_text(t) for t in texts]

    def analyze_df(self, df, text_col="content"):
        if df.empty:
            return df
        print(f"  🔍 Analyzing sentiment for {len(df)} tweets...")
        sentiments = self.analyze_batch(df[text_col].tolist())
        sentiment_df = pd.DataFrame(sentiments)
        return pd.concat([df.reset_index(drop=True), sentiment_df], axis=1)
