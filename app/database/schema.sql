-- Creator Compass Database Schema
-- SQLite database for user management and data persistence


-- USERS TABLE
-- Stores user account information
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active INTEGER DEFAULT 1
);


-- USER PREFERENCES TABLE
-- Stores user settings and preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    preferred_platforms TEXT,  -- JSON array: ["tiktok", "youtube"]
    preferred_categories TEXT,  -- JSON array: ["fitness", "tech"]
    default_duration INTEGER DEFAULT 60,
    default_posting_hour INTEGER DEFAULT 18,
    theme TEXT DEFAULT 'light',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- SAVED TRENDS TABLE
-- Bookmarked/saved trends from Trend Discovery
CREATE TABLE IF NOT EXISTS saved_trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    trend_topic TEXT NOT NULL,
    trend_score REAL,
    trend_source TEXT,  -- twitter, tiktok, etc.
    trend_niche TEXT,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- CONTENT IDEAS TABLE
-- Generated ideas from Content Ideation
CREATE TABLE IF NOT EXISTS content_ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    idea_title TEXT NOT NULL,
    idea_description TEXT,
    platform TEXT,
    category TEXT,
    trend_topic TEXT,  -- linked trend if any
    predicted_engagement REAL,
    engagement_score INTEGER,  -- 0-100 performance score
    is_favorite INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- PREDICTIONS TABLE
-- Engagement predictions from Optimiser
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    -- Input data
    caption TEXT,
    platform TEXT,
    category TEXT,
    posting_hour INTEGER,
    posting_day TEXT,
    duration_sec INTEGER,
    has_trend INTEGER,
    trend_type TEXT,
    -- Results
    predicted_engagement REAL,
    performance_score INTEGER,  -- 0-100 normalised score
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- INDEXES for performance
CREATE INDEX IF NOT EXISTS idx_saved_trends_user ON saved_trends(user_id);
CREATE INDEX IF NOT EXISTS idx_content_ideas_user ON content_ideas(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_user ON predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
