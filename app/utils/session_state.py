#Session State Management 
#Handles cross-page data flow and preserves workflow progress on refresh.

import streamlit as st
from typing import Optional, Dict

# SESSION STATE KEY CONSTANTS
# Centralised keys for session state to avoid typos and ensure consistency across the app.
class SessionKeys:
    # Central definition of session state keys
    
    # Cross-Page Flow
    SELECTED_TREND = "selected_trend"    # str: Trend passed to Content Ideation
    SELECTED_IDEA = "selected_idea"      # Dict: Idea passed to Engagement Optimiser
    
    # Trend Discovery
    PREVIEW_TRENDS = "preview_trends"
    ANALYSED_TRENDS = "analysed_trends"
    
    # Content Ideation
    GENERATED_IDEAS = "generated_ideas"
    CURRENT_TREND_TOPIC = "current_trend_topic"
    CURRENT_PLATFORM = "current_platform"
    
    # Engagement Optimiser
    OPTIMISER_INPUT = "optimiser_input"
    OPTIMISER_RESULT = "optimiser_result"
    CURRENT_EXPLANATION = "current_explanation"


# CROSS-PAGE FLOW HELPERS
# These functions manage the flow of data between pages, allowing users to click on a trend in the dashboard and have it available in the 
# Content Ideation page, or to select an idea and have it available in the Engagement Optimiser.

def set_selected_trend(trend_topic: str) -> None:
    st.session_state[SessionKeys.SELECTED_TREND] = trend_topic


def consume_selected_trend() -> Optional[str]:
    """
    Retrieve and remove a selected trend from session state (one-time use).
    
    Returns the trend topic if it exists, otherwise None.
    IMPORTANT: Deletes the trend from session state after retrieval to prevent
    stale data when the page reloads. This ensures fresh data on subsequent visits.
    """
    trend = st.session_state.get(SessionKeys.SELECTED_TREND)
    if trend is not None:
        del st.session_state[SessionKeys.SELECTED_TREND]
    return trend


def set_selected_idea(idea_data: Dict) -> None:
    st.session_state[SessionKeys.SELECTED_IDEA] = idea_data


def consume_selected_idea() -> Optional[Dict]:
    """
    Retrieve and remove a selected idea from session state (one-time use).
    Returns the idea dictionary if it exists, otherwise None.
    """
    idea = st.session_state.get(SessionKeys.SELECTED_IDEA)
    if idea is not None:
        del st.session_state[SessionKeys.SELECTED_IDEA]
    return idea
