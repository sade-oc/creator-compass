
#Authentication System that handles user registration, login, logout, and session management.


import bcrypt
import streamlit as st
from typing import Optional, Dict, Any, Tuple
import re

# Import database functions
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.db_manager import (
    create_user,
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    update_last_login,
    init_db,
)


# PASSWORD HASHING
def hash_password(password: str) -> str:
    # Hash a password using bcrypt.
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    # Verify a password against its hash.
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            password_hash.encode('utf-8')
        )
    except Exception:
        return False



# VALIDATION

def validate_email(email: str) -> bool:
    # Validate email format.
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> Tuple[bool, str]:
    # Validate username. Returns (is_valid, error_message).
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 20:
        return False, "Username must be at most 20 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    # Validate password strength. Returns (is_valid, error_message).
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if len(password) > 50:
        return False, "Password must be at most 50 characters"
    return True, ""


# REGISTRATION


def register_user(
    username: str, 
    email: str, 
    password: str,
    confirm_password: str
) -> Tuple[bool, str, Optional[int]]:

    #Register a new user.

    # Validate username
    valid, error = validate_username(username)
    if not valid:
        return False, error, None
    
    # Validate email
    if not validate_email(email):
        return False, "Invalid email format", None
    
    # Validate password
    valid, error = validate_password(password)
    if not valid:
        return False, error, None
    
    # Check password confirmation
    if password != confirm_password:
        return False, "Passwords do not match", None
    
    # Check if username exists
    if get_user_by_username(username):
        return False, "Username already taken", None
    
    # Check if email exists
    if get_user_by_email(email):
        return False, "Email already registered", None
    
    # Hash password and create user
    password_hash = hash_password(password)
    user_id = create_user(username, email, password_hash)
    
    if user_id:
        return True, "Account created successfully!", user_id
    else:
        return False, "Failed to create account. Please try again.", None



# LOGIN / LOGOUT

def login_user(username_or_email: str, password: str) -> Tuple[bool, str]:

    # Authenticate user and create session.

    # Try to find user by username first, then by email
    user = get_user_by_username(username_or_email)
    if not user:
        user = get_user_by_email(username_or_email)
    
    if not user:
        return False, "Invalid username or email"
    
    # Check if account is active
    if not user.get('is_active', True):
        return False, "Account is deactivated"
    
    # Verify password
    if not verify_password(password, user['password_hash']):
        return False, "Incorrect password"
    
    # Create session
    st.session_state.user = {
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
    }
    st.session_state.authenticated = True
    
    # Update last login
    update_last_login(user['id'])
    
    return True, f"Welcome back, {user['username']}!"


def logout_user():
    #Clear user session.
    if 'user' in st.session_state:
        del st.session_state.user
    if 'authenticated' in st.session_state:
        del st.session_state.authenticated
    
    # Clear any other session data
    keys_to_clear = ['selected_trend', 'generated_idea', 'last_prediction']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


# SESSION MANAGEMENT

def get_current_user() -> Optional[Dict[str, Any]]:
    # Get current logged-in user from session.
    if is_authenticated():
        return st.session_state.get('user')
    return None


def is_authenticated() -> bool:
    # Check if user is authenticated.
    return st.session_state.get('authenticated', False)


def require_auth() -> bool:
    # Check authentication and show login prompt if not authenticated.
    # Returns True if authenticated, False otherwise.
    if not is_authenticated():
        st.warning("Please log in to access this page.")
        st.info("Use the login form in the sidebar or go to the Home page.")
        return False
    return True


def get_user_id() -> Optional[int]:
    # Get current user's ID. Returns None if not authenticated.
    user = get_current_user()
    return user['id'] if user else None


# UI COMPONENTS

def render_login_form() -> bool:

    # Render login form in sidebar or main area.
    # Returns True if login successful this render.
    with st.form("login_form"):
        st.subheader("Login")
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if username and password:
                success, message = login_user(username, password)
                if success:
                    st.success(message)
                    st.rerun()
                    return True
                else:
                    st.error(message)
            else:
                st.error("Please enter username and password")
    return False


def render_signup_form() -> bool:
    # Render signup form.
    # Returns True if signup successful this render.
    with st.form("signup_form"):
        st.subheader("Create Account")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up", use_container_width=True)
        
        if submit:
            success, message, user_id = register_user(
                username, email, password, confirm
            )
            if success:
                st.success(message)
                st.info("You can now log in with your credentials.")
                return True
            else:
                st.error(message)
    return False


def render_auth_sidebar():
    """Render authentication status in sidebar (logout only when logged in)."""
    with st.sidebar:
        if is_authenticated():
            user = get_current_user()
            if user:
                st.success(f"Logged in as **{user['username']}**")
                if st.button("Logout", use_container_width=True):
                    logout_user()
                    st.rerun()


# Initialize database when module loads
init_db()
