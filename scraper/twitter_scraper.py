# scraper/twitter_scraper.py
import httpx
import pandas as pd
import json
import re
import time
import random
from datetime import datetime, timedelta
from fake_useragent import UserAgent

class TwitterScraper:

    FINANCE_QUERIES = [
        "stock market",
        "S&P500 SPX",
        "Fed interest rates",
        "inflation economy",
        "tech stocks AI",
        "energy oil gas stocks",
        "banking finance earnings",
        "healthcare biotech",
        "bull market bear market",
        "earnings guidance outlook",
    ]

    # Working public Nitter instances (updated list)
    NITTER_INSTANCES = [
        "https://nitter.poast.org",
        "https://nitter.privacydev.net",
        "https://nitter.1d4.us",
        "https://nitter.kavin.rocks",
        "https://nitter.unixfox.eu",
    ]

    def __init__(self, max_tweets_per_query: int = 50):
        self.max_tweets = max_tweets_per_query
        self.ua = UserAgent()
        self.working_instance = None

    def _get_headers(self) -> dict:
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

    def _find_working_instance(self) -> str | None:
        """Try each Nitter instance and return the first working one."""
        for instance in self.NITTER_INSTANCES:
            try:
                r = httpx.get(f"{instance}/search?q=test", 
                             headers=self._get_headers(), 
                             timeout=5, 
                             follow_redirects=True)
                if r.status_code == 200 and "tweet" in r.text.lower():
                    print(f"  ✅ Working instance: {instance}")
                    return instance
            except Exception:
                continue
        return None

    def scrape_query_nitter(self, query: str, instance: str) -> list:
        """Scrape via a Nitter instance."""
        from bs4 import BeautifulSoup

        tweets = []
        url = f"{instance}/search?q={query.replace(' ', '+')}&f=tweets"

        try:
            r = httpx.get(url, headers=self._get_headers(), 
                         timeout=10, follow_redirects=True)
            if r.status_code != 200:
                return []

            soup = BeautifulSoup(r.text, 'html.parser')
            tweet_items = soup.find_all('div', class_='timeline-item')

            for item in tweet_items[:self.max_tweets]:
                try:
                    content = item.find('div', class_='tweet-content')
                    username = item.find('a', class_='username')
                    date_tag = item.find('span', class_='tweet-date')
                    stats = item.find_all('span', class_='tweet-stat')

                    likes = 0
                    retweets = 0
                    for stat in stats:
                        icon = stat.find('div', class_='icon-heart')
                        if icon:
                            likes = int(re.sub(r'\D', '', stat.text) or 0)
                        icon_rt = stat.find('div', class_='icon-retweet')
                        if icon_rt:
                            retweets = int(re.sub(r'\D', '', stat.text) or 0)

                    if content and username:
                        tweets.append({
                            'id': f"{username.text}_{date_tag.text if date_tag else ''}",
                            'date': date_tag['title'] if date_tag and date_tag.has_attr('title') else str(datetime.utcnow()),
                            'content': content.text.strip(),
                            'user': username.text.strip().replace('@', ''),
                            'followers': 0,
                            'likes': likes,
                            'retweets': retweets,
                            'query_tag': query[:40],
                        })
                except Exception:
                    continue

        except Exception as e:
            print(f"  ⚠️ Nitter scrape error: {e}")

        return tweets

    def scrape_mock_data(self, query: str) -> list:
        """
        Fallback: generate realistic mock finance tweets for development.
        Replace this with a real source once scraping is unblocked.
        """
        mock_tweets = [
            {"content": f"$SPY breaking above 200-day MA — bulls in control today. #{query.split()[0]}",
             "user": "tradingdesk", "likes": 342, "retweets": 87},
            {"content": f"Fed signals no rate cuts until Q3 at earliest. Markets repricing risk assets. #Fed #rates",
             "user": "macroanalyst", "likes": 891, "retweets": 204},
            {"content": f"NVDA earnings beat by 18%. AI capex cycle still intact. Adding on dips. #NVDA #AI",
             "user": "techtrader99", "likes": 1203, "retweets": 445},
            {"content": f"Oil inventories surprise to the upside. $XLE under pressure heading into close.",
             "user": "energydesk", "likes": 156, "retweets": 43},
            {"content": f"Yield curve steepening — watch regional banks $KRE as spread widens. #bonds #banking",
             "user": "fixedincome", "likes": 567, "retweets": 123},
            {"content": f"CPI hotter than expected. Risk-off tone. $VIX spiking. Hedge accordingly.",
             "user": "riskdesk", "likes": 2341, "retweets": 892},
            {"content": f"Healthcare sector lagging. FDA approval delays hitting $PFE $MRNA hard today.",
             "user": "biotrader", "likes": 234, "retweets": 67},
            {"content": f"Small caps outperforming large caps — $IWM/SPY ratio breaking out. Rotation underway.",
             "user": "quant_signals", "likes": 445, "retweets": 134},
            {"content": f"Goldman raising S&P target to 5800. Earnings revision cycle turning positive.",
             "user": "wallstanalyst", "likes": 3210, "retweets": 1203},
            {"content": f"Dollar index DXY breaking down — good for $GLD $EEM commodities. Watch this.",
             "user": "fxtrader", "likes": 678, "retweets": 189},
        ]

        results = []
        now = datetime.utcnow()
        for i, t in enumerate(mock_tweets):
            results.append({
                'id': f"mock_{query[:10]}_{i}",
                'date': (now - timedelta(hours=random.randint(1, 23))).isoformat(),
                'content': t['content'],
                'user': t['user'],
                'followers': random.randint(1000, 50000),
                'likes': t['likes'] + random.randint(-50, 50),
                'retweets': t['retweets'] + random.randint(-10, 10),
                'query_tag': query[:40],
            })
        return results

    def scrape_query(self, query: str, since_hours: int = 24) -> list:
        """Try live scraping first, fall back to mock data."""
        # Try Nitter if we have a working instance
        if self.working_instance is None:
            print("  🔍 Finding working Nitter instance...")
            self.working_instance = self._find_working_instance()

        if self.working_instance:
            tweets = self.scrape_query_nitter(query, self.working_instance)
            if tweets:
                return tweets

        # Fallback to mock data for development
        print(f"  ℹ️  Using mock data for '{query}' (live scraping unavailable)")
        return self.scrape_mock_data(query)

    def scrape_all(self) -> pd.DataFrame:
        """Run all finance queries and return a single deduplicated DataFrame."""
        all_tweets = []

        for i, query in enumerate(self.FINANCE_QUERIES):
            print(f"\n  Query {i+1}/{len(self.FINANCE_QUERIES)}: {query}")
            tweets = self.scrape_query(query)
            all_tweets.extend(tweets)
            print(f"  → {len(tweets)} tweets collected")
            time.sleep(random.uniform(0.5, 1.5))  # polite delay

        df = pd.DataFrame(all_tweets)

        if not df.empty:
            df.drop_duplicates(subset='id', inplace=True)
            df.sort_values('date', ascending=False, inplace=True)
            df.reset_index(drop=True, inplace=True)

        print(f"\n✅ Total unique tweets: {len(df)}")
        return df