"""
Trend Discovery Page

Two-stage workflow to discover and analyse trending topics:
1. Fetch trending topics from Twitter/X via Apify (fast, no tweets)
2. Deep analyse selected trends: fetch tweets, extract keywords/sentiment/hashtags via NLP
3. Display results with option to save trends or create content ideas

Users can filter by niche and control number of trends analysed.
"""

import streamlit as st
import pandas as pd
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from data.fetch_twitter_apify import fetch_twitter_trends, fetch_tweets_for_trend
from pipelines.nlp_processor import process_trend_nlp

# Authentication
from auth.authenticator import require_auth, get_current_user
from utils.helpers import render_sidebar
from utils.session_state import SessionKeys, set_selected_trend
from database.db_manager import save_trend, get_saved_trends

if not require_auth():
    st.stop()
render_sidebar()

# Get current user for save functionality
user = get_current_user()
# Get already saved trends to prevent duplicates
saved_trend_topics = [t['trend_topic'] for t in get_saved_trends(user['id'])] if user else []

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
            st.session_state[SessionKeys.PREVIEW_TRENDS] = trends
            # Initialise analysed_trends if it doesn't exist (don't reset existing ones)
            if SessionKeys.ANALYSED_TRENDS not in st.session_state:
                st.session_state[SessionKeys.ANALYSED_TRENDS] = {}
            st.success(f"Loaded {len(trends)} trending topics!")
            
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

# Check if we have preview trends
if SessionKeys.PREVIEW_TRENDS not in st.session_state or not st.session_state[SessionKeys.PREVIEW_TRENDS]:
    st.info("Click 'Get Trending Topics' to see what's trending!")
    st.stop()

# Filter preview trends by niche
preview_trends = st.session_state[SessionKeys.PREVIEW_TRENDS]
if selected_niche != "All":
    filtered_preview = [t for t in preview_trends if t.get("niche") == selected_niche]
else:
    filtered_preview = preview_trends

if not filtered_preview:
    st.warning(f"No trends found for '{selected_niche}'. Try 'All' or a different niche.")
    st.stop()

# Display preview trends
st.subheader(f"{len(filtered_preview)} Trending Topics")

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
    "Select trends to analyse (pick 3-5 for best performance)",
    topic_names,
    max_selections=10
)

# Analyse button
if st.button("Analyse Selected Trends", type="primary", disabled=len(selected_topics) == 0):
    if len(selected_topics) > 5:
        st.warning("Analysing more than 5 trends may take 3-5 minutes. Consider selecting fewer.")
    
    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        st.error("APIFY_API_TOKEN not found. Set it in your .env file.")
        st.stop()
    
    # Fetch tweets and perform NLP analysis for each selected trend
    with st.spinner(f"Analysing {len(selected_topics)} trends (fetching tweets + NLP)..."):
        analysed = st.session_state.get(SessionKeys.ANALYSED_TRENDS, {})
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, topic in enumerate(selected_topics):
            # Skip if already analysed
            if topic in analysed:
                progress_bar.progress((i + 1) / len(selected_topics))
                continue
            
            status_text.text(f"Analysing: {topic}")
            
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
                analysed_trend = process_trend_nlp(trend)
                
                # Store in session state
                analysed[topic] = analysed_trend
                
            except Exception as e:
                st.error(f"Error analysing '{topic}': {e}")
            
            progress_bar.progress((i + 1) / len(selected_topics))
        
        st.session_state[SessionKeys.ANALYSED_TRENDS] = analysed
        status_text.empty()
        st.success(f"Analysis complete for {len(analysed)} trends!")

# Display analysed trends
if SessionKeys.ANALYSED_TRENDS in st.session_state and st.session_state[SessionKeys.ANALYSED_TRENDS]:
    st.markdown("---")
    st.subheader("Analysis Results")
    
    analysed_trends = st.session_state[SessionKeys.ANALYSED_TRENDS]
    
    # Convert to DataFrame
    df_data = []
    for topic, trend in analysed_trends.items():
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
    col1.metric("Analysed Trends", len(df))
    col2.metric("Total Tweets", df["tweet_count"].sum())
    avg_sentiment = df["_full_data"].apply(lambda x: x.get("sentiment", {}).get("average", 0)).mean()
    col3.metric("Avg Sentiment", f"{avg_sentiment:.2f}")
    
    # Display table
    show_cols = ["topic", "score", "niche", "keywords", "sentiment", "hashtags", "tweet_count"]
    st.dataframe(df[show_cols], use_container_width=True, hide_index=True)
    
    # Detailed expanders
    # Expandable sections for each trend showing keywords, sentiment, hashtags, tweets, and action buttons
    st.markdown("---")
    st.subheader("Detailed Analysis")
    
    for idx, row in df.iterrows():
        trend = row["_full_data"]
        
        with st.expander(f"{row['topic']} - Score: {row['score']}"):
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
                st.markdown("**Hashtags**")
                hashtags = trend.get("hashtags", [])[:10]
                if hashtags:
                    for ht, count in hashtags:
                        st.text(f"• {ht}: {count}")
                else:
                    st.text("No hashtags")
            
            st.markdown("---")
            st.markdown("**Sample Tweets**")
            tweets = trend.get("tweets", [])[:5]
            if tweets:
                for i, tweet in enumerate(tweets, 1):
                    text = tweet.get("text", "")[:200]
                    likes = tweet.get("likes", 0)
                    retweets = tweet.get("retweets", 0)
                    # Mask author username for privacy
                    st.markdown(f"**{i}.** @Anonymous User - Likes: {likes} | Retweets: {retweets}")
                    st.text(text)
                    st.markdown("")
            else:
                st.text("No tweets available")
            
            # Action buttons
            st.markdown("---")
            col_act1, col_act2 = st.columns(2)
            
            with col_act1:
                if st.button("Use for Content Ideas", key=f"use_trend_{row['topic']}", type="primary"):
                    set_selected_trend(row['topic'])
                    st.switch_page("pages/Content_Ideation.py")
            
            with col_act2:
                is_saved = row['topic'] in saved_trend_topics
                if is_saved:
                    st.success("Saved")
                else:
                    if st.button("Save Trend", key=f"save_trend_{row['topic']}"):
                        save_trend(
                            user_id=user['id'],
                            trend_topic=row['topic'],
                            trend_score=row['score'],
                            trend_source="twitter",
                            trend_niche=row['niche']
                        )
                        st.success("Trend saved!")
                        st.rerun()
    
    # What's Next? section
    st.markdown("---")
    st.subheader("What's Next?")
    st.info("Select a trend above and click **'Use for Content Ideas'** to generate AI-powered content ideas!")
    
    col_next1, col_next2 = st.columns(2)
    with col_next1:
        if st.button("Go to Content Ideation", use_container_width=True):
            st.switch_page("pages/Content_Ideation.py")
    with col_next2:
        if st.button("Back to Dashboard", use_container_width=True):
            st.switch_page("main.py")