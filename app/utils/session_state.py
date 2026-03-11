#Session State Management 

#Handles cross-page data flow and preserves workflow progress on refresh.


import streamlit as st
from typing import Optional, Dict

# SESSION STATE KEY CONSTANTS

class SessionKeys:
    # Central definition of session state keys
    
    # Cross-Page Flow
    SELECTED_TREND = "selected_trend"    # str: Trend passed to Content Ideation
    SELECTED_IDEA = "selected_idea"      # Dict: Idea passed to Engagement Optimiser
    
    # Trend Discovery
    PREVIEW_TRENDS = "preview_trends"
    ANALYZED_TRENDS = "analyzed_trends"
    
    # Content Ideation
    GENERATED_IDEAS = "generated_ideas"
    CURRENT_TREND_TOPIC = "current_trend_topic"
    CURRENT_PLATFORM = "current_platform"
    
    # Engagement Optimiser
    OPTIMISER_INPUT = "optimiser_input"
    OPTIMISER_RESULT = "optimiser_result"
    CURRENT_EXPLANATION = "current_explanation"


# CROSS-PAGE FLOW HELPERS

def set_selected_trend(trend_topic: str) -> None:
    st.session_state[SessionKeys.SELECTED_TREND] = trend_topic


def consume_selected_trend() -> Optional[str]:
    trend = st.session_state.get(SessionKeys.SELECTED_TREND)
    if trend is not None:
        del st.session_state[SessionKeys.SELECTED_TREND]
    return trend


def set_selected_idea(idea_data: Dict) -> None:
    st.session_state[SessionKeys.SELECTED_IDEA] = idea_data


def consume_selected_idea() -> Optional[Dict]:
    idea = st.session_state.get(SessionKeys.SELECTED_IDEA)
    if idea is not None:
        del st.session_state[SessionKeys.SELECTED_IDEA]
    return idea
