
import pandas as pd
from nlp.topics import extract_topics, classify_sector, get_sector_breakdown

tweets = [
    "NVDA earnings beat by 18%. AI capex cycle still intact.",
    "Fed signals no rate cuts until Q3. Treasury yields rising.",
    "Oil inventories surprise to upside. XLE under pressure.",
    "Goldman raising SP500 target. Bull market intact.",
    "FDA approval delays hitting Pfizer and Moderna hard.",
    "CPI hotter than expected. Inflation not cooling fast enough.",
    "Apple and Microsoft leading tech rally. Semiconductors up.",
    "JPMorgan earnings beat. Banking sector outperforming.",
    "Recession fears growing. GDP forecast cut by analysts.",
    "SPY breaking above 200-day MA. Bulls in control.",
]
df = pd.DataFrame({"content": tweets, "likes": range(10, 110, 10)})

print("--- Sector Classification ---")
for t in tweets[:4]:
    print("  " + classify_sector(t).ljust(15) + " | " + t[:55])

print("\n--- Sector Breakdown ---")
print(get_sector_breakdown(df))

print("\n--- Topic Clusters ---")
topics, df_topics = extract_topics(df, n_topics=4)
for tid, tdata in topics.items():
    print("\n  Topic " + str(tid) + ": " + tdata["label"])
    print("  Keywords: " + str(tdata["keywords"][:5]))
    print("  Tweets:   " + str(tdata["count"]))
