# Authentication module for Creator Compass
from .authenticator import (
    hash_password,
    verify_password,
    register_user,
    login_user,
    logout_user,
    get_current_user,
    is_authenticated,
    require_auth,
    render_auth_sidebar,
    render_login_form,
    render_signup_form,
)

__all__ = [
    'hash_password',
    'verify_password',
    'register_user',
    'login_user',
    'logout_user',
    'get_current_user',
    'is_authenticated',
    'require_auth',
    'render_auth_sidebar',
    'render_login_form',
    'render_signup_form',
]
