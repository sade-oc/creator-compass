#Database Manager that handles all database operations using SQLite.

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

# Database file location
DB_DIR = Path(__file__).parent
DB_PATH = DB_DIR / "creator_compass.db"
SCHEMA_PATH = DB_DIR / "schema.sql"


@contextmanager
def get_connection():
    """Get database connection with context manager."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize database with schema."""
    with get_connection() as conn:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
        conn.commit()
    print(f"✓ Database initialized at {DB_PATH}")



# USER OPERATIONS

def create_user(username: str, email: str, password_hash: str) -> Optional[int]:
   
    #Create a new user account.
    #Returns user ID if successful, None if username/email exists.
   
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (username, email, password_hash)
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # Username or email already exists


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    # Get user by username.
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    # Get user by email.
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    # Get user by ID.
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None


def update_last_login(user_id: int):
    # Update user's last login timestamp.
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now(), user_id)
        )
        conn.commit()

# Update user profile (username, email, password). Returns (success, message).
def update_user(
    user_id: int,
    username: str = None,
    email: str = None,
    password_hash: str = None
) -> tuple[bool, str]:
    with get_connection() as conn:
        # Build dynamic update query
        updates = []
        values = []
        
        if username:
            # Check username uniqueness
            existing = conn.execute(
                "SELECT id FROM users WHERE username = ? AND id != ?",
                (username, user_id)
            ).fetchone()
            if existing:
                return False, "Username already taken"
            updates.append("username = ?")
            values.append(username)
        
        if email:
            # Check email uniqueness
            existing = conn.execute(
                "SELECT id FROM users WHERE email = ? AND id != ?",
                (email, user_id)
            ).fetchone()
            if existing:
                return False, "Email already in use"
            updates.append("email = ?")
            values.append(email)
        
        if password_hash:
            updates.append("password_hash = ?")
            values.append(password_hash)
        
        if not updates:
            return False, "No fields to update"
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        conn.execute(query, values)
        conn.commit()
        return True, "Profile updated successfully"

# Account deactivation 
def delete_user(user_id: int) -> bool:
    #Delete user and all associated data.
  
    with get_connection() as conn:
        # Delete in order to respect foreign key constraints
        conn.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM content_ideas WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM saved_trends WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM user_preferences WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    return True



# USER PREFERENCES

def save_user_preferences(
    user_id: int,
    preferred_platforms: List[str] = None,
    preferred_categories: List[str] = None,
    default_duration: int = 60,
    default_posting_hour: int = 18,
    theme: str = 'light'
) -> bool:
    # Save or update user preferences.
    platforms_json = json.dumps(preferred_platforms or [])
    categories_json = json.dumps(preferred_categories or [])
    
    with get_connection() as conn:
        # Use REPLACE to insert or update
        conn.execute(
            """
            INSERT OR REPLACE INTO user_preferences 
            (user_id, preferred_platforms, preferred_categories, 
             default_duration, default_posting_hour, theme, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, platforms_json, categories_json, 
             default_duration, default_posting_hour, theme, datetime.now())
        )
        conn.commit()
    return True


def get_user_preferences(user_id: int) -> Optional[Dict[str, Any]]:
    # Get user preferences.
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM user_preferences WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        
        if not row:
            return None
            
        prefs = dict(row)
        # Parse JSON arrays
        prefs['preferred_platforms'] = json.loads(prefs.get('preferred_platforms') or '[]')
        prefs['preferred_categories'] = json.loads(prefs.get('preferred_categories') or '[]')
        return prefs



# SAVED TRENDS

def save_trend(
    user_id: int,
    trend_topic: str,
    trend_score: float = None,
    trend_source: str = None,
    trend_niche: str = None,
    notes: str = None
) -> int:
   # Save a trend for a user. Returns trend ID.
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO saved_trends 
            (user_id, trend_topic, trend_score, trend_source, trend_niche, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, trend_topic, trend_score, trend_source, trend_niche, notes)
        )
        conn.commit()
        return cursor.lastrowid


def get_saved_trends(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    # Get saved trends for a user, most recent first.
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM saved_trends 
            WHERE user_id = ? 
            ORDER BY saved_at DESC 
            LIMIT ?
            """,
            (user_id, limit)
        ).fetchall()
        return [dict(row) for row in rows]


def delete_saved_trend(trend_id: int, user_id: int) -> bool:
    # Delete a saved trend. Returns True if deleted.
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM saved_trends WHERE id = ? AND user_id = ?",
            (trend_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0



# CONTENT IDEAS

def save_idea(
    user_id: int,
    idea_title: str,
    idea_description: str = None,
    platform: str = None,
    category: str = None,
    trend_topic: str = None,
    predicted_engagement: float = None,
    engagement_score: int = None
) -> int:
    # Save a content idea. Returns idea ID.
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO content_ideas 
            (user_id, idea_title, idea_description, platform, category, 
             trend_topic, predicted_engagement, engagement_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, idea_title, idea_description, platform, category,
             trend_topic, predicted_engagement, engagement_score)
        )
        conn.commit()
        return cursor.lastrowid


def get_saved_ideas(
    user_id: int, 
    limit: int = 50,
    favorites_only: bool = False
) -> List[Dict[str, Any]]:
    # Get saved ideas for a user, most recent first.
    query = "SELECT * FROM content_ideas WHERE user_id = ?"
    params = [user_id]
    
    if favorites_only:
        query += " AND is_favorite = 1"
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def toggle_idea_favorite(idea_id: int, user_id: int) -> bool:
    # Toggle favorite status of an idea.
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE content_ideas 
            SET is_favorite = NOT is_favorite 
            WHERE id = ? AND user_id = ?
            """,
            (idea_id, user_id)
        )
        conn.commit()
        return True


def delete_saved_idea(idea_id: int, user_id: int) -> bool:
    # Delete a saved idea. Returns True if deleted.
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM content_ideas WHERE id = ? AND user_id = ?",
            (idea_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0



# PREDICTIONS

def save_prediction(
    user_id: int,
    caption: str,
    platform: str,
    category: str,
    posting_hour: int,
    posting_day: str,
    duration_sec: int,
    has_trend: bool,
    trend_type: str,
    predicted_engagement: float,
    performance_score: int
) -> int:
    # Save a prediction. Returns prediction ID.
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO predictions 
            (user_id, caption, platform, category, posting_hour, posting_day,
             duration_sec, has_trend, trend_type, predicted_engagement, performance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, caption, platform, category, posting_hour, posting_day,
             duration_sec, has_trend, trend_type, predicted_engagement, performance_score)
        )
        conn.commit()
        return cursor.lastrowid


def get_prediction_history(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    # Get prediction history for a user, most recent first.
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM predictions 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
            """,
            (user_id, limit)
        ).fetchall()
        return [dict(row) for row in rows]


# STATISTICS

def get_user_stats(user_id: int) -> Dict[str, Any]:
    # Get user statistics for dashboard.
    with get_connection() as conn:
        stats = {}
        
        # Count saved trends
        stats['saved_trends'] = conn.execute(
            "SELECT COUNT(*) FROM saved_trends WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        
        # Count ideas
        stats['total_ideas'] = conn.execute(
            "SELECT COUNT(*) FROM content_ideas WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        
        # Count predictions
        stats['total_predictions'] = conn.execute(
            "SELECT COUNT(*) FROM predictions WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        
        # Average performance score
        avg = conn.execute(
            "SELECT AVG(performance_score) FROM predictions WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        stats['avg_performance_score'] = round(avg, 1) if avg else 0
        
        return stats


# Initialize database on import (creates tables if not exist)
if __name__ == "__main__":
    init_db()
