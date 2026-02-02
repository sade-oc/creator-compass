import streamlit as st
import pandas as pd
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from data.fetch_twitter_apify import fetch_twitter_trends, fetch_tweets_for_trend
from pipelines.nlp_processor import process_trend_nlp
st.title("Trend Discovery")

# Sidebar - Stage 1: Quick Preview
st.sidebar.header("Stage 1: Browse Trends")

# Niche selection
niche_options = ["All", "Tech/Gaming", "Sports", "Entertainment/Media", 
                 "Politics/News", "Fitness/Wellness", "Beauty/Fashion", 
                 "Food/Cooking", "Travel", "Finance", "General"]
selected_niche = st.sidebar.selectbox("Filter by Niche", niche_options)

# Number of trends to fetch
max_trends = st.sidebar.slider("Number of trends", 10, 50, 25)

# Stage 1: Fetch trending topics (FAST - no tweets)
if st.sidebar.button("Get Trending Topics", type="primary"):
    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        st.error("APIFY_API_TOKEN not found. Set it in your .env file.")
        st.stop()
    
    with st.spinner(f"Fetching {max_trends} trending topics..."):
        try:
            # Fetch trends WITHOUT tweets (fast!)
            trends = fetch_twitter_trends(
                apify_token=apify_token,
                max_trends=max_trends,
                fetch_tweets=False  # Skip tweets for now
            )
            
            # Store in session state
            st.session_state.preview_trends = trends
            st.session_state.analyzed_trends = {}  # Reset analyzed trends
            st.success(f"Loaded {len(trends)} trending topics!")
            
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

# Check if we have preview trends
if "preview_trends" not in st.session_state or not st.session_state.preview_trends:
    st.info("👆 Click 'Get Trending Topics' to see what's trending!")
    st.stop()

# Filter preview trends by niche
preview_trends = st.session_state.preview_trends
if selected_niche != "All":
    filtered_preview = [t for t in preview_trends if t.get("niche") == selected_niche]
else:
    filtered_preview = preview_trends

if not filtered_preview:
    st.warning(f"No trends found for '{selected_niche}'. Try 'All' or a different niche.")
    st.stop()

# Display preview trends
st.subheader(f"📊 {len(filtered_preview)} Trending Topics")

# Create DataFrame for preview
preview_data = []
for trend in filtered_preview:
    preview_data.append({
        "Select": False,
        "Topic": trend.get("topic", ""),
        "Score": trend.get("score", 0),
        "Niche": trend.get("niche", ""),
    })

preview_df = pd.DataFrame(preview_data)

# Display preview table
st.dataframe(preview_df[["Topic", "Score", "Niche"]], use_container_width=True, hide_index=True)

# Stage 2: Select trends for deep analysis
st.markdown("---")
st.subheader("Stage 2: Deep Analysis")

# Multi-select for trends
topic_names = [t["Topic"] for t in preview_data]
selected_topics = st.multiselect(
    "Select trends to analyze (pick 3-5 for best performance)",
    topic_names,
    max_selections=10
)

# Analyze button
if st.button("Analyze Selected Trends", type="primary", disabled=len(selected_topics) == 0):
    if len(selected_topics) > 5:
        st.warning("Analyzing more than 5 trends may take 3-5 minutes. Consider selecting fewer.")
    
    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        st.error("APIFY_API_TOKEN not found. Set it in your .env file.")
        st.stop()
    
    with st.spinner(f"Analyzing {len(selected_topics)} trends (fetching tweets + NLP)..."):
        analyzed = st.session_state.get("analyzed_trends", {})
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, topic in enumerate(selected_topics):
            # Skip if already analyzed
            if topic in analyzed:
                progress_bar.progress((i + 1) / len(selected_topics))
                continue
            
            status_text.text(f"Analyzing: {topic}")
            
            try:
                # Find the trend in preview
                trend = next(t for t in filtered_preview if t.get("topic") == topic)
                
                # Fetch tweets for this trend
                tweets = fetch_tweets_for_trend(
                    topic=topic,
                    apify_token=apify_token,
                    max_tweets=50
                )
                
                # Add tweets to trend
                trend["tweets"] = tweets
                
                # Process NLP
                analyzed_trend = process_trend_nlp(trend)
                
                # Store in session state
                analyzed[topic] = analyzed_trend
                
            except Exception as e:
                st.error(f"Error analyzing '{topic}': {e}")
            
            progress_bar.progress((i + 1) / len(selected_topics))
        
        st.session_state.analyzed_trends = analyzed
        status_text.empty()
        st.success(f"Analysis complete for {len(analyzed)} trends!")

# Display analyzed trends
if "analyzed_trends" in st.session_state and st.session_state.analyzed_trends:
    st.markdown("---")
    st.subheader("Analysis Results")
    
    analyzed_trends = st.session_state.analyzed_trends
    
    # Convert to DataFrame
    df_data = []
    for topic, trend in analyzed_trends.items():
        keywords = trend.get("keywords", [])[:3]
        keywords_str = ", ".join([f"{kw[0]} ({kw[1]})" for kw in keywords]) if keywords else "-"
        
        sentiment = trend.get("sentiment", {})
        avg_sent = sentiment.get("average", 0)
        
        if avg_sent > 0.1:
            sentiment_display = f"{avg_sent:.2f}"
        elif avg_sent < -0.1:
            sentiment_display = f"{avg_sent:.2f}"
        else:
            sentiment_display = f"{avg_sent:.2f}"
        
        hashtags = trend.get("hashtags", [])[:3]
        hashtags_str = ", ".join([ht[0] for ht in hashtags]) if hashtags else "-"
        
        df_data.append({
            "topic": trend.get("topic", ""),
            "score": trend.get("score", 0),
            "niche": trend.get("niche", ""),
            "keywords": keywords_str,
            "sentiment": sentiment_display,
            "hashtags": hashtags_str,
            "tweet_count": len(trend.get("tweets", [])),
            "_full_data": trend
        })
    
    df = pd.DataFrame(df_data)
    df = df.sort_values(by=["score"], ascending=[False])
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Analyzed Trends", len(df))
    col2.metric("Total Tweets", df["tweet_count"].sum())
    avg_sentiment = df["_full_data"].apply(lambda x: x.get("sentiment", {}).get("average", 0)).mean()
    col3.metric("Avg Sentiment", f"{avg_sentiment:.2f}")
    
    # Display table
    show_cols = ["topic", "score", "niche", "keywords", "sentiment", "hashtags", "tweet_count"]
    st.dataframe(df[show_cols], use_container_width=True, hide_index=True)
    
    # Detailed expanders
    st.markdown("---")
    st.subheader("Detailed Analysis")
    
    for idx, row in df.iterrows():
        trend = row["_full_data"]
        
        with st.expander(f"🔍 {row['topic']} - Score: {row['score']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Top Keywords**")
                keywords = trend.get("keywords", [])[:10]
                if keywords:
                    for kw, count in keywords:
                        st.text(f"• {kw}: {count}")
                else:
                    st.text("No keywords")
            
            with col2:
                st.markdown("**Sentiment Breakdown**")
                sentiment = trend.get("sentiment", {})
                total = sentiment.get("total", 0)
                if total > 0:
                    pos = sentiment.get("positive", 0)
                    neu = sentiment.get("neutral", 0)
                    neg = sentiment.get("negative", 0)
                    st.metric("Average", f"{sentiment.get('average', 0):.3f}")
                    st.text(f"Positive: {pos} ({pos/total*100:.1f}%)")
                    st.text(f"Neutral: {neu} ({neu/total*100:.1f}%)")
                    st.text(f"Negative: {neg} ({neg/total*100:.1f}%)")
                else:
                    st.text("No sentiment data")
            
            with col3:
                st.markdown("**#️⃣ Hashtags**")
                hashtags = trend.get("hashtags", [])[:10]
                if hashtags:
                    for ht, count in hashtags:
                        st.text(f"• {ht}: {count}")
                else:
                    st.text("No hashtags")
            
            st.markdown("---")
            st.markdown("**📱 Sample Tweets**")
            tweets = trend.get("tweets", [])[:5]
            if tweets:
                for i, tweet in enumerate(tweets, 1):
                    text = tweet.get("text", "")[:200]
                    likes = tweet.get("likes", 0)
                    retweets = tweet.get("retweets", 0)
                    author = tweet.get("author", "Unknown")
                    st.markdown(f"**{i}.** @{author} - ❤️ {likes} | 🔁 {retweets}")
                    st.text(text)
                    st.markdown("")
            else:
                st.text("No tweets available")