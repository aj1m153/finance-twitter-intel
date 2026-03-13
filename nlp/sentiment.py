# nlp/sentiment.py
from transformers import pipeline
import pandas as pd

class FinanceSentimentAnalyzer:
    """
    FinBERT: BERT fine-tuned on financial text.
    Labels: positive / negative / neutral
    """

    def __init__(self):
        print("  📦 Loading FinBERT model (first run downloads ~500MB)...")
        self.model = pipeline(
            "text-classification",
            model="ProsusAI/finbert",
            top_k=None,
        )
        print("  ✅ FinBERT loaded")

    def analyze_batch(self, texts: list) -> list:
        """Run sentiment on a list of texts, returns list of dicts."""
        results = []

        # Process in batches of 32 for speed
        for i in range(0, len(texts), 32):
            batch = [t[:512] for t in texts[i:i+32]]  # BERT 512 token limit
            try:
                preds = self.model(batch)
                for pred in preds:
                    scores = {p['label']: p['score'] for p in pred}
                    dominant = max(scores, key=scores.get)
                    results.append({
                        'sentiment':  dominant,
                        'positive':   round(scores.get('positive', 0), 4),
                        'negative':   round(scores.get('negative', 0), 4),
                        'neutral':    round(scores.get('neutral',   0), 4),
                        'confidence': round(scores[dominant], 4),
                    })
            except Exception as e:
                print(f"  ⚠️ Batch sentiment error: {e}")
                # Fill failed batch with neutral
                results.extend([{
                    'sentiment': 'neutral',
                    'positive': 0, 'negative': 0,
                    'neutral': 1, 'confidence': 0,
                }] * len(batch))

        return results

    def analyze_df(self, df: pd.DataFrame, text_col: str = 'content') -> pd.DataFrame:
        """Add sentiment columns to a tweets DataFrame."""
        if df.empty:
            return df

        print(f"  🔍 Analyzing sentiment for {len(df)} tweets...")
        sentiments = self.analyze_batch(df[text_col].tolist())
        sentiment_df = pd.DataFrame(sentiments)

        return pd.concat([df.reset_index(drop=True), sentiment_df], axis=1)