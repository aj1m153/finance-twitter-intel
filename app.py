
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from scraper.twitter_scraper import TwitterScraper
from nlp.sentiment import FinanceSentimentAnalyzer
from nlp.entities import get_top_tickers
from nlp.topics import extract_topics, get_sector_breakdown, clean_text
from market.market_data import get_market_snapshot, get_ticker_details

st.set_page_config(page_title="Finance Twitter Intelligence", page_icon="📈", layout="wide")

st.sidebar.title("⚙️ Settings")
max_tweets = st.sidebar.slider("Tweets per query", 10, 200, 50)
scrape_btn = st.sidebar.button("🔄 Scrape & Analyze Now", type="primary")
st.sidebar.markdown("---")
st.sidebar.info("Scrapes finance Twitter daily, runs FinBERT sentiment and NLP topic analysis, cross-referenced with live market data.")

@st.cache_data(ttl=1800)
def load_tweets(max_per_query):
    scraper = TwitterScraper(max_tweets_per_query=max_per_query)
    return scraper.scrape_all()

@st.cache_data(ttl=300)
def load_market():
    return get_market_snapshot()

@st.cache_resource
def get_analyzer():
    return FinanceSentimentAnalyzer()

if scrape_btn:
    st.cache_data.clear()

st.title("📈 Finance Twitter Intelligence Dashboard")
st.caption(f"NLP analysis of financial Twitter/X  •  {datetime.now().strftime('%B %d, %Y  %H:%M')}")

tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Market Overview",
    "🔥 Trending Topics",
    "📊 Sentiment Analysis",
    "🏷️ Ticker Intelligence",
])

with tab1:
    st.subheader("Today's Market Snapshot")
    with st.spinner("Fetching live market data..."):
        market_df = load_market()
    if not market_df.empty:
        indices = market_df[market_df["ticker"].str.startswith("^")]
        cols = st.columns(len(indices))
        for col, (_, row) in zip(cols, indices.iterrows()):
            col.metric(
                label=row["name"],
                value=f"{row['price']:,.2f}",
                delta=f"{row['change_pct']:+.2f}%",
            )
        st.markdown("---")
        sectors = market_df[~market_df["ticker"].str.startswith("^")]
        fig = px.bar(
            sectors.sort_values("change_pct"),
            x="change_pct", y="name",
            orientation="h",
            color="change_pct",
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
            title="Sector ETF Performance Today (%)",
            labels={"change_pct": "% Change", "name": "Sector"},
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🔥 What Finance Twitter Is Talking About")
    with st.spinner("Scraping and analyzing topics..."):
        df = load_tweets(max_tweets)
    if df.empty:
        st.warning("No tweets found. Try clicking Scrape & Analyze Now.")
    else:
        st.success(f"✅ Analyzed {len(df):,} tweets from the past 24 hours")
        st.subheader("📂 Sector Breakdown")
        sector_df = get_sector_breakdown(df)
        fig_sec = px.pie(
            sector_df, values="count", names="sector",
            title="Tweet Volume by Finance Sector",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        st.plotly_chart(fig_sec, use_container_width=True)
        st.markdown("---")
        st.subheader("🧩 Topic Clusters")
        topics, df_topics = extract_topics(df, n_topics=6)
        if topics:
            cols = st.columns(2)
            for i, (tid, tdata) in enumerate(topics.items()):
                with cols[i % 2]:
                    with st.expander(f"📌 Topic {tid+1}: {tdata['label']} ({tdata['count']} tweets)", expanded=i < 2):
                        st.write("**Keywords:**", ", ".join(tdata["keywords"][:6]))
                        st.write("**Sample tweets:**")
                        for tw in tdata["top_tweets"]:
                            st.info("💬 " + tw[:240])
        st.markdown("---")
        st.subheader("☁️ Word Cloud")
        all_text = " ".join(df["content"].apply(clean_text).tolist())
        if all_text.strip():
            wc = WordCloud(width=1200, height=350, background_color="black", colormap="YlOrRd", max_words=120).generate(all_text)
            fig_wc, ax = plt.subplots(figsize=(14, 4))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            fig_wc.patch.set_facecolor("black")
            st.pyplot(fig_wc)

with tab3:
    st.subheader("📊 Market Sentiment — Powered by FinBERT")
    with st.spinner("Running FinBERT sentiment analysis..."):
        df2 = load_tweets(max_tweets)
        analyzer = get_analyzer()
        df_s = analyzer.analyze_df(df2.head(300))
    if not df_s.empty and "sentiment" in df_s.columns:
        counts = df_s["sentiment"].value_counts()
        col1, col2 = st.columns([1, 2])
        with col1:
            fig_donut = px.pie(
                values=counts.values,
                names=counts.index,
                hole=0.5,
                color=counts.index,
                color_discrete_map={"positive": "#00C853", "negative": "#D50000", "neutral": "#FFD600"},
                title="Overall Sentiment",
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        with col2:
            df_s["hour"] = pd.to_datetime(df_s["date"], utc=True, errors="coerce").dt.floor("h")
            hourly = df_s.groupby(["hour", "sentiment"]).size().reset_index(name="count")
            fig_line = px.line(
                hourly, x="hour", y="count", color="sentiment",
                color_discrete_map={"positive": "#00C853", "negative": "#D50000", "neutral": "#FFD600"},
                title="Sentiment Trend — Last 24h",
            )
            st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("---")
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("🔺 Top Bullish Tweets")
            bullish = df_s[df_s["sentiment"] == "positive"].nlargest(5, "likes")
            for _, row in bullish.iterrows():
                st.success(f"❤️ {int(row.get('likes', 0)):,}  |  {row['content'][:200]}")
        with col4:
            st.subheader("🔻 Top Bearish Tweets")
            bearish = df_s[df_s["sentiment"] == "negative"].nlargest(5, "likes")
            for _, row in bearish.iterrows():
                st.error(f"❤️ {int(row.get('likes', 0)):,}  |  {row['content'][:200]}")

with tab4:
    st.subheader("🏷️ Most Mentioned Tickers on Finance Twitter")
    df3 = load_tweets(max_tweets)
    with st.spinner("Extracting ticker mentions..."):
        ticker_df = get_top_tickers(df3, top_n=15)
    if not ticker_df.empty:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(ticker_df, use_container_width=True, hide_index=True)
        with col2:
            fig_bar = px.bar(
                ticker_df.head(10), x="ticker", y="mentions",
                color="mentions", color_continuous_scale="Viridis",
                title="Top 10 Most Mentioned Tickers",
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("---")
        st.subheader("📉 Twitter Buzz vs. Market Performance")
        top_tickers = ticker_df["ticker"].head(8).tolist()
        with st.spinner("Fetching market data for top tickers..."):
            ticker_mkt = get_ticker_details(top_tickers)
        if not ticker_mkt.empty:
            merged = ticker_df.merge(ticker_mkt, on="ticker", how="inner")
            if not merged.empty:
                fig_scatter = px.scatter(
                    merged, x="mentions", y="change_pct",
                    size="mentions", color="change_pct", text="ticker",
                    color_continuous_scale="RdYlGn", color_continuous_midpoint=0,
                    title="Social Mentions vs. Price Change % Today",
                    labels={"mentions": "Twitter Mentions", "change_pct": "Price Change %"},
                )
                fig_scatter.update_traces(textposition="top center")
                st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown("---")
        st.subheader("🧠 Analyst Intelligence — Key Signals")
        market_df2 = load_market()
        if not market_df2.empty:
            worst = market_df2.nsmallest(3, "change_pct")[["name", "change_pct"]]
            best  = market_df2.nlargest(3, "change_pct")[["name", "change_pct"]]
            vix_row = market_df2[market_df2["ticker"] == "^VIX"]
            vix_val = float(vix_row["change_pct"].values[0]) if not vix_row.empty else 0
            if vix_val > 10:
                st.warning(f"⚠️ VIX surging +{vix_val:.1f}% — elevated fear. Consider hedges.")
            elif vix_val < -10:
                st.success(f"✅ VIX falling {vix_val:.1f}% — fear subsiding. Risk-on conditions.")
            else:
                st.info(f"ℹ️ VIX change: {vix_val:+.1f}% — normal volatility range.")
            col5, col6 = st.columns(2)
            with col5:
                st.write("**📉 Weakest Sectors Today**")
                for _, r in worst.iterrows():
                    st.error(f"{r['name']}: {r['change_pct']:+.2f}%")
            with col6:
                st.write("**📈 Strongest Sectors Today**")
                for _, r in best.iterrows():
                    st.success(f"{r['name']}: {r['change_pct']:+.2f}%")

st.markdown("---")
st.caption("Refreshes every 30 min  •  Powered by FinBERT + yfinance  •  Built with Streamlit")
