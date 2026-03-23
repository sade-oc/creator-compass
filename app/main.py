"""
Creator Compass Main Dashboard

Entry point for the Streamlit application. Provides authenticated users with:
- Personal dashboard showing stats (trends, ideas, predictions)
- Navigation to Trend Discovery, Content Ideation, Engagement Optimiser, User Settings
- Management of saved trends, ideas, and prediction history

Unauthenticated users see login/signup forms.
"""

import streamlit as st
from utils.helpers import load_examples, render_sidebar
from auth.authenticator import (
    render_login_form,
    render_signup_form,
    is_authenticated,
    get_current_user,
)
from database.db_manager import (
    get_user_stats, 
    init_db,
    get_saved_trends,
    get_saved_ideas,
    get_prediction_history,
    delete_saved_trend,
    delete_saved_idea,
)

# Initialise database
init_db()

# Configure Streamlit page layout and metadata
st.set_page_config(
    page_title="Creator Compass",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render sidebar with user info (only when logged in)
render_sidebar()

# Main content
st.title("🧭 Creator Compass")
st.subheader("AI-powered micro-content coaching platform")

if is_authenticated():
    # Load user data and render dashboard with stats, navigation, and saved items
    user = get_current_user()
    if user:
        stats = get_user_stats(user['id'])
        saved_trends = get_saved_trends(user['id'], limit=5)
        saved_ideas = get_saved_ideas(user['id'], limit=5)
        recent_predictions = get_prediction_history(user['id'], limit=5)
    
    st.success(f"Welcome back, **{user['username']}**! 👋")
    
    # Dashboard stats
    st.markdown("---")
    st.subheader("📊 Your Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Saved Trends", stats['saved_trends'])
    with col2:
        st.metric("Content Ideas", stats['total_ideas'])
    with col3:
        st.metric("Predictions Made", stats['total_predictions'])
    with col4:
        st.metric("Avg Performance", f"{stats['avg_performance_score']}/100")
    
    # Quick actions with navigation buttons
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📈 Discover Trends")
        st.caption("Find trending topics across social platforms.")
        if st.button("Go to Trend Discovery", key="nav_trends", use_container_width=True):
            st.switch_page("pages/Trend_Discovery.py")
    with col2:
        st.markdown("### 💡 Generate Ideas")
        st.caption("Get AI-powered content ideas based on trends.")
        if st.button("Go to Content Ideation", key="nav_ideas", use_container_width=True):
            st.switch_page("pages/Content_Ideation.py")
    with col3:
        st.markdown("### ⚡ Optimize Content")
        st.caption("Predict engagement and get optimization tips.")
        if st.button("Go to Engagement Optimiser", key="nav_optimiser", use_container_width=True):
            st.switch_page("pages/Engagement_Optimiser.py")
    
    # Saved Items Section
    st.markdown("---")
    st.subheader("📌 Your Saved Items")
    
    tab_trends, tab_ideas, tab_preds = st.tabs(["💾 Saved Trends", "💡 Saved Ideas", "📊 Recent Predictions"])
    
    with tab_trends:
        if saved_trends:
            for trend in saved_trends:
                col_info, col_action = st.columns([4, 1])
                with col_info:
                    st.markdown(f"**{trend['trend_topic']}**")
                    st.caption(f"Score: {trend['trend_score']} | Niche: {trend['trend_niche']} | Saved: {trend['saved_at'][:10]}")
                with col_action:
                    if st.button("🗑️", key=f"del_trend_{trend['id']}", help="Delete"):
                        delete_saved_trend(trend['id'], user['id'])
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No saved trends yet. Go to Trend Discovery to find and save trends!")
    
    with tab_ideas:
        if saved_ideas:
            for idea in saved_ideas:
                col_info, col_action = st.columns([4, 1])
                with col_info:
                    st.markdown(f"**{idea['idea_title']}**")
                    st.caption(f"Platform: {idea['platform']} | Category: {idea['category']} | Saved: {idea['created_at'][:10]}")
                with col_action:
                    if st.button("🗑️", key=f"del_idea_{idea['id']}", help="Delete"):
                        delete_saved_idea(idea['id'], user['id'])
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No saved ideas yet. Go to Content Ideation to generate and save ideas!")
    
    with tab_preds:
        if recent_predictions:
            for pred in recent_predictions:
                col_info, col_score = st.columns([3, 1])
                with col_info:
                    caption_text = pred['caption'] or "No caption"
                    summary = caption_text[:80] + "..." if len(caption_text) > 80 else caption_text
                    st.markdown(f"**{summary}**")
                    st.caption(f"Platform: {pred['platform']} | Category: {pred['category']} | Date: {pred['created_at'][:10]}")
                with col_score:
                    score = pred['performance_score']
                    color = "🟢" if score >= 55 else "🟡" if score >= 40 else "🔴"
                    st.metric("Score", f"{color} {score}")
                st.markdown("---")
        else:
            st.info("No predictions yet. Go to Engagement Optimiser to analyse your content!")

else:
    # Display login/signup forms for unauthenticated users
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            render_login_form()
        with tab2:
            render_signup_form()

