import streamlit as st
import sys
from pathlib import Path

# Add app directory to path for imports
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from auth.authenticator import (
    require_auth,
    get_current_user,
    logout_user,
    hash_password,
    verify_password,
)
from utils.helpers import render_sidebar
from database.db_manager import (
    get_user_by_id,
    update_user,
    delete_user,
    get_user_preferences,
    save_user_preferences,
)

# Page config
st.set_page_config(
    page_title="User Settings - Creator Compass",
    page_icon="⚙️",
    layout="wide"
)

# Require authentication
if not require_auth():
    st.stop()

render_sidebar()

# Get current user
user = get_current_user()
user_data = get_user_by_id(user['id'])
preferences = get_user_preferences(user['id']) or {}

st.title("⚙️ User Settings")
st.markdown("Manage your profile, preferences, and account settings.")
st.markdown("---")

# Create tabs for different settings sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👤 Profile", 
    "🔒 Password", 
    "🎯 Preferences", 
    "⚠️ Account",
    "📋 Privacy & Terms"
])


# TAB 1: PROFILE SETTINGS
with tab1:
    st.subheader("Profile Information")
    
    with st.form("profile_form"):
        new_username = st.text_input(
            "Username",
            value=user_data['username'],
            help="3-20 characters, letters, numbers, and underscores only"
        )
        
        new_email = st.text_input(
            "Email",
            value=user_data['email'],
            help="Your email address"
        )
        
        submitted = st.form_submit_button("Save Changes", type="primary")
        
        if submitted:
            # Validate inputs
            errors = []
            
            if len(new_username) < 3 or len(new_username) > 20:
                errors.append("Username must be 3-20 characters")
            
            if not new_username.replace("_", "").isalnum():
                errors.append("Username can only contain letters, numbers, and underscores")
            
            if "@" not in new_email or "." not in new_email:
                errors.append("Please enter a valid email address")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Only update fields that changed
                update_username = new_username if new_username != user_data['username'] else None
                update_email = new_email if new_email != user_data['email'] else None
                
                if update_username or update_email:
                    success, message = update_user(
                        user['id'],
                        username=update_username,
                        email=update_email
                    )
                    
                    if success:
                        st.success(message)
                        # Update session state
                        if update_username:
                            st.session_state.user['username'] = new_username
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.info("No changes to save")


# TAB 2: PASSWORD CHANGE
with tab2:
    st.subheader("Change Password")
    
    with st.form("password_form"):
        current_password = st.text_input(
            "Current Password",
            type="password"
        )
        
        new_password = st.text_input(
            "New Password",
            type="password",
            help="Minimum 6 characters"
        )
        
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password"
        )
        
        submitted = st.form_submit_button("Update Password", type="primary")
        
        if submitted:
            errors = []
            
            if not current_password:
                errors.append("Please enter your current password")
            
            if len(new_password) < 6:
                errors.append("New password must be at least 6 characters")
            
            if new_password != confirm_password:
                errors.append("New passwords do not match")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Verify current password
                if verify_password(current_password, user_data['password_hash']):
                    new_hash = hash_password(new_password)
                    success, message = update_user(user['id'], password_hash=new_hash)
                    
                    if success:
                        st.success("Password updated successfully!")
                    else:
                        st.error(message)
                else:
                    st.error("Current password is incorrect")


# TAB 3: CONTENT PREFERENCES
with tab3:
    st.subheader("Content Preferences")
    st.markdown("Customize your Creator Compass experience")
    
    with st.form("preferences_form"):
        # Platform preferences
        st.markdown("**Target Platforms**")
        platforms = ["TikTok", "YouTube", "Instagram"]
        current_platforms = preferences.get('preferred_platforms', [])
        
        selected_platforms = []
        cols = st.columns(3)
        for i, platform in enumerate(platforms):
            with cols[i]:
                if st.checkbox(
                    platform, 
                    value=platform.lower() in [p.lower() for p in current_platforms],
                    key=f"platform_{platform}"
                ):
                    selected_platforms.append(platform.lower())
        
        st.markdown("")
        
        # Category preferences
        st.markdown("**Content Categories**")
        categories = ["Tech", "Fitness", "Food", "Lifestyle", "Education", "Entertainment"]
        current_categories = preferences.get('preferred_categories', [])
        
        selected_categories = []
        cols = st.columns(3)
        for i, category in enumerate(categories):
            with cols[i % 3]:
                if st.checkbox(
                    category,
                    value=category.lower() in [c.lower() for c in current_categories],
                    key=f"category_{category}"
                ):
                    selected_categories.append(category.lower())
        
        st.markdown("")
        
        # Default settings
        col1, col2 = st.columns(2)
        
        with col1:
            default_duration = st.selectbox(
                "Default Video Duration (seconds)",
                options=[15, 30, 60, 90, 120, 180],
                index=[15, 30, 60, 90, 120, 180].index(
                    preferences.get('default_duration', 60)
                ) if preferences.get('default_duration', 60) in [15, 30, 60, 90, 120, 180] else 2
            )
        
        with col2:
            default_hour = st.slider(
                "Default Posting Hour",
                min_value=0,
                max_value=23,
                value=preferences.get('default_posting_hour', 18),
                help="Hour of day (24-hour format)"
            )
        
        submitted = st.form_submit_button("Save Preferences", type="primary")
        
        if submitted:
            save_user_preferences(
                user_id=user['id'],
                preferred_platforms=selected_platforms,
                preferred_categories=selected_categories,
                default_duration=default_duration,
                default_posting_hour=default_hour
            )
            st.success("Preferences saved successfully!")
            st.rerun()


# TAB 4: ACCOUNT ACTIONS
with tab4:
    st.subheader("Account Actions")
    
    # Logout section
    st.markdown("### Logout")
    st.markdown("Sign out of your account on this device.")
    
    if st.button("Logout", type="secondary"):
        logout_user()
        st.success("Logged out successfully!")
        st.rerun()
    
    st.markdown("---")
    
    # Delete account section
    st.markdown("### Delete Account")
    st.warning(
        "⚠️ **This action is permanent and cannot be undone.** "
        "All your data including saved trends, content ideas, and predictions will be deleted."
    )
    
    # Initialize delete confirmation state
    if 'delete_confirmed' not in st.session_state:
        st.session_state.delete_confirmed = False
    
    if not st.session_state.delete_confirmed:
        if st.button("Delete My Account", type="primary"):
            st.session_state.delete_confirmed = True
            st.rerun()
    else:
        st.error("Are you absolutely sure? Type your username to confirm:")
        
        confirm_username = st.text_input(
            "Type your username to confirm deletion",
            key="confirm_delete_username"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Cancel", type="secondary"):
                st.session_state.delete_confirmed = False
                st.rerun()
        
        with col2:
            if st.button("Permanently Delete", type="primary"):
                if confirm_username == user_data['username']:
                    delete_user(user['id'])
                    logout_user()
                    st.success("Account deleted successfully. Goodbye! 👋")
                    st.rerun()
                else:
                    st.error("Username doesn't match. Please try again.")


# TAB 5: PRIVACY POLICY & TERMS
with tab5:
    st.subheader("Privacy Policy & Terms of Service")
    
    privacy_terms = st.tabs(["Privacy Policy", "Terms of Service", "Data Rights"])
    
    with privacy_terms[0]:  # Privacy Policy
        st.markdown("""
        ## About This App
        
        Creator Compass is a proof-of-concept project built for a BSc Computer Science final project. 
        It's not a commercial product, so here's how your data actually works:
        
        ### What Gets Stored
        - Your login: username, email, hashed password
        - Your settings: platforms you like, content categories, posting times
        - Your work: trends you save, ideas you generate, engagement predictions
        
        ### Where It Goes
        - **Local Storage:** Everything stays in a local SQLite database
        - **Apify API:** When you search trends, that goes to Apify (just the search query)
        - **OpenAI API:** When you generate ideas, Apify sends your trend + preferences to OpenAI
        - **Nowhere else:** Your data is never sold, shared with ads, or used for anything else
        
        ### Security
        - Passwords are hashed (can't be reversed)
        - Only you can access your account
        - No tracking cookies or analytics
        
        ### Deleting Your Data
        You can delete your account anytime (Account tab). Everything gets removed immediately.
        """)
    
    with privacy_terms[1]:  # Terms of Service
        st.markdown("""
        ## How to Use This App
        
        ### What You Get
        - Trend discovery from social media
        - AI-generated content ideas (powered by OpenAI)
        - Engagement predictions based on historical data
        
        ### What to Know
        ⚠️ **Predictions are guesses**, not guarantees  
        ⚠️ **Generated ideas are suggestions**, not guaranteed viral content  
        ⚠️ You're responsible for checking if content breaks platform rules  
        ⚠️ Don't use this to create spam, fake, or malicious content
        
        ### Your Content
        - Everything you create in this app is yours
        - You can use it anywhere you want
        - You own all rights to your ideas
        
        ### What You Can't Do
        - Copy or reverse-engineer the code
        - Use it commercially without credit
        - Use it to spam or break platform rules
        """)
    
    with privacy_terms[2]:  # Data Rights
        st.markdown("""
        ## Your Rights
        
        **You can:**
        - Access all your data anytime
        - Update your profile info
        - Delete your account (permanent)
        - Download your data if needed
        
        **We don't:**
        - Sell or share your data
        - Track you with cookies
        - Use your content without permission
        - Keep deleted data (removed within 7 days)
        
        This app follows UK GDPR rules for data protection.
        """)


