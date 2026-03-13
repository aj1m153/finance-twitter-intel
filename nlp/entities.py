# nlp/entities.py
import re
import pandas as pd
from collections import Counter

KNOWN_TICKERS = {
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX",
    "JPM", "GS", "BAC", "WFC", "MS", "C", "BLK",
    "XOM", "CVX", "COP", "SLB",
    "JNJ", "PFE", "MRNA", "UNH", "ABBV",
    "SPY", "QQQ", "IWM", "DIA", "GLD", "TLT",
    "XLK", "XLF", "XLE", "XLV", "XLY", "XLI",
    "VIX", "BTC", "ETH",
}

KNOWN_COMPANIES = [
    "Apple", "Microsoft", "Google", "Amazon", "Nvidia", "Meta", "Tesla",
    "JPMorgan", "Goldman Sachs", "Bank of America", "Wells Fargo",
    "ExxonMobil", "Chevron", "Pfizer", "Moderna", "Johnson",
    "Federal Reserve", "Fed", "BlackRock", "Morgan Stanley",
]

KNOWN_PEOPLE = [
    "Powell", "Yellen", "Buffett", "Musk", "Dimon", "Fink",
    "Munger", "Dalio", "Ackman", "Burry", "Lynch", "Gross",
]

def extract_tickers(text):
    found = re.findall(r"\$([A-Z]{1,5})", text.upper())
    words = re.findall(r"\b([A-Z]{2,5})\b", text.upper())
    found += [w for w in words if w in KNOWN_TICKERS]
    return list(set(found))

def extract_entities(text):
    entities = {"companies": [], "people": [], "money": [], "percent": []}
    for company in KNOWN_COMPANIES:
        if company.lower() in text.lower():
            entities["companies"].append(company)
    for person in KNOWN_PEOPLE:
        if person.lower() in text.lower():
            entities["people"].append(person)
    entities["money"]   = re.findall(r"\$[\d,]+(?:\.\d+)?[BMK]?", text)
    entities["percent"] = re.findall(r"\d+\.?\d*%", text)
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
