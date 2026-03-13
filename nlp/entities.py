# nlp/entities.py
import re
import pandas as pd
from collections import Counter

def load_nlp():
    import spacy
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        import subprocess, sys
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        return spacy.load("en_core_web_sm")

nlp = load_nlp()

KNOWN_TICKERS = {
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX",
    "JPM", "GS", "BAC", "WFC", "MS", "C", "BLK",
    "XOM", "CVX", "COP", "SLB",
    "JNJ", "PFE", "MRNA", "UNH", "ABBV",
    "SPY", "QQQ", "IWM", "DIA", "GLD", "TLT",
    "XLK", "XLF", "XLE", "XLV", "XLY", "XLI",
    "VIX", "BTC", "ETH",
}

def extract_tickers(text):
    pattern = r"\$([A-Z]{1,5})"
    found = re.findall(pattern, text.upper())
    words = re.findall(r"\b([A-Z]{2,5})\b", text.upper())
    found += [w for w in words if w in KNOWN_TICKERS]
    return list(set(found))

def extract_entities(text):
    doc = nlp(text)
    entities = {"companies": [], "people": [], "money": [], "percent": []}
    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities["companies"].append(ent.text)
        elif ent.label_ == "PERSON":
            entities["people"].append(ent.text)
        elif ent.label_ == "MONEY":
            entities["money"].append(ent.text)
        elif ent.label_ == "PERCENT":
            entities["percent"].append(ent.text)
    return entities

def get_top_tickers(df, top_n=10):
    all_tickers = []
    for text in df["content"]:
        all_tickers.extend(extract_tickers(str(text)))
    counter = Counter(all_tickers)
    return pd.DataFrame(counter.most_common(top_n), columns=["ticker", "mentions"])

def get_top_entities(df, entity_type="companies", top_n=10):
    all_entities = []
    for text in df["content"]:
        ents = extract_entities(str(text))
        all_entities.extend(ents.get(entity_type, []))
    counter = Counter(all_entities)
    return pd.DataFrame(counter.most_common(top_n), columns=["entity", "mentions"])
