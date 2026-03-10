# Database module for Creator Compass
from .db_manager import (
    init_db,
    get_connection,
    # User operations
    create_user,
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    # Preferences
    save_user_preferences,
    get_user_preferences,
    # Trends
    save_trend,
    get_saved_trends,
    delete_saved_trend,
    # Ideas
    save_idea,
    get_saved_ideas,
    delete_saved_idea,
    # Predictions
    save_prediction,
    get_prediction_history,
)

__all__ = [
    'init_db',
    'get_connection',
    'create_user',
    'get_user_by_username',
    'get_user_by_email',
    'get_user_by_id',
    'save_user_preferences',
    'get_user_preferences',
    'save_trend',
    'get_saved_trends',
    'delete_saved_trend',
    'save_idea',
    'get_saved_ideas',
    'delete_saved_idea',
    'save_prediction',
    'get_prediction_history',
]
