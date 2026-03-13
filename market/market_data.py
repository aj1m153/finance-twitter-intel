# market/market_data.py
import yfinance as yf
import pandas as pd

SECTOR_ETFS = {
    "Technology":    "XLK",
    "Healthcare":    "XLV",
    "Financials":    "XLF",
    "Energy":        "XLE",
    "Consumer Disc": "XLY",
    "Industrials":   "XLI",
    "Materials":     "XLB",
    "Real Estate":   "XLRE",
    "Utilities":     "XLU",
    "Comm Services": "XLC",
}

INDICES = {
    "S&P 500":      "^GSPC",
    "NASDAQ":       "^IXIC",
    "Dow Jones":    "^DJI",
    "Russell 2000": "^RUT",
    "VIX":          "^VIX",
}

def get_quote(ticker):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="2d")
        if len(hist) >= 2:
            prev  = hist["Close"].iloc[-2]
            curr  = hist["Close"].iloc[-1]
            chg   = ((curr - prev) / prev) * 100
            return {
                "ticker":     ticker,
                "price":      round(curr, 2),
                "change_pct": round(chg, 2),
                "volume":     int(hist["Volume"].iloc[-1]),
            }
    except Exception as e:
        print("  Quote error " + ticker + ": " + str(e))
    return None

def get_market_snapshot():
    rows = []
    all_instruments = {**INDICES, **SECTOR_ETFS}
    for name, ticker in all_instruments.items():
        q = get_quote(ticker)
        if q:
            q["name"] = name
            rows.append(q)
    return pd.DataFrame(rows)

def get_ticker_details(tickers):
    rows = []
    for ticker in tickers:
        try:
            t    = yf.Ticker(ticker)
            info = t.info
            hist = t.history(period="2d")
            if len(hist) >= 2:
                chg = ((hist["Close"].iloc[-1] - hist["Close"].iloc[-2])
                       / hist["Close"].iloc[-2] * 100)
                rows.append({
                    "ticker":     ticker,
                    "name":       info.get("longName", ticker),
                    "sector":     info.get("sector", "N/A"),
                    "price":      round(hist["Close"].iloc[-1], 2),
                    "change_pct": round(chg, 2),
                    "market_cap": info.get("marketCap", 0),
                })
        except Exception as e:
            print("  Ticker error " + ticker + ": " + str(e))
    return pd.DataFrame(rows)
