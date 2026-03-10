import streamlit as st
from utils.helpers import load_examples
from auth.authenticator import (
    render_auth_sidebar,
    render_login_form,
    render_signup_form,
    is_authenticated,
    get_current_user,
    logout_user,
)
from database.db_manager import get_user_stats, init_db

# Initialize database
init_db()

st.set_page_config(
    page_title="Creator Compass",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render authentication status in sidebar (only shows logout when logged in)
render_auth_sidebar()

# Main content
st.title("🧭 Creator Compass")
st.subheader("AI-powered micro-content coaching platform")

if is_authenticated():
    user = get_current_user()
    if user:
        stats = get_user_stats(user['id'])
    
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
    
    # Quick actions
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        ### 📈 Discover Trends
        Find trending topics across social platforms.
        
        👉 Go to **Trend Discovery** in the sidebar
        """)
    with col2:
        st.markdown("""
        ### 💡 Generate Ideas
        Get AI-powered content ideas based on trends.
        
        👉 Go to **Content Ideation** in the sidebar
        """)
    with col3:
        st.markdown("""
        ### ⚡ Optimize Content
        Predict engagement and get optimization tips.
        
        👉 Go to **Engagement Optimiser** in the sidebar
        """)

else:
    # Not logged in - show centered login/signup
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            render_login_form()
        with tab2:
            render_signup_form()

