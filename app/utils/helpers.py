# Imports 
from __future__ import annotations
from pathlib import Path
from typing import Optional
import pandas as pd
import json
import streamlit as st

EXAMPLES_PATH  = Path("data/examples/trends.csv")
TRENDS_JSON_PATH = Path("data/examples/trends.json")
EXPECTED_COLUMNS = [ "topic", "score", "source", "discovered_at", "region", "niche"]   


def render_sidebar():
    
    #Render consistent sidebar across all pages.
    #Shows user info, mini stats, and logout button.
  
    # Import here to avoid circular imports
    from auth.authenticator import is_authenticated, get_current_user, logout_user
    from database.db_manager import get_user_stats
    
    with st.sidebar:
        if is_authenticated():
            user = get_current_user()
            if user:
                # User info with avatar
                st.markdown(f"###  {user['username']}")
                
                # Mini stats
                stats = get_user_stats(user['id'])
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Trends", stats['saved_trends'], label_visibility="visible")
                with col2:
                    st.metric("Ideas", stats['total_ideas'], label_visibility="visible")
                
                st.markdown("---")
                
                # Logout button
                if st.button(" Logout", use_container_width=True):
                    logout_user()
                    st.rerun()


def load_examples(csv_path: Optional[Path] = None) -> pd.DataFrame:
    # Load trends from CSV into clean pandas DataFrame.
    path = csv_path or EXAMPLES_PATH
    if not path.exists():
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    df = pd.read_csv(path)
   
   # Normalise column names and ensure all expected columns are present
    df.columns = [col.strip().lower() for col in df.columns]
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    
    # Parse types 
    df["discovered_at"] = pd.to_datetime(df["discovered_at"], errors="coerce", utc=True)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    # Trim overly long topics 
    df["topic"] = df["topic"].astype(str).str.slice(0, 180)

    # Reorder to expected columns then anything extra 
    extras = [c for c in df.columns if c not in EXPECTED_COLUMNS]  # type: ignore
    df = df[EXPECTED_COLUMNS + extras]

    return df

def load_trends_json(json_path: Optional[Path] = None) -> list[dict]:
    #Load trends with NLP data from JSON.
    path = json_path or TRENDS_JSON_PATH
    
    if not path.exists():
        return []
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, IOError):
        return []