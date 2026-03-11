import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path
from typing import Literal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from pipelines.content_ideation import generate_content_ideas, generate_detailed_script

# Authentication
from auth.authenticator import require_auth, get_current_user
from utils.helpers import render_sidebar
from utils.session_state import SessionKeys, consume_selected_trend, set_selected_idea
from database.db_manager import save_idea, get_saved_ideas

if not require_auth():
    st.stop()
render_sidebar()

# Get current user for save functionality
user = get_current_user()
# Get already saved ideas to prevent duplicates
saved_idea_titles = [i['idea_title'] for i in get_saved_ideas(user['id'])] if user else []

Platform = Literal["TikTok", "Instagram Reels", "YouTube Shorts"]

st.title("🎬 AI Content Ideation")
st.markdown("Generate creative video ideas from trending topics, then get detailed shot-by-shot scripts.")

# Check if we have analysed trends from Objective 1
if SessionKeys.ANALYZED_TRENDS not in st.session_state or not st.session_state[SessionKeys.ANALYZED_TRENDS]:
    st.warning("⚠️ No analysed trends found. Please go to Trend Discovery first and analyse some trends.")
    if st.button("Go to Trend Discovery"):
        st.switch_page("pages/Trend_Discovery.py")
    st.stop()

# Sidebar - Trend Selection
st.sidebar.header("🎯 Select Trend")

analyzed_trends = st.session_state[SessionKeys.ANALYZED_TRENDS]
trend_topics = list(analyzed_trends.keys())

# Check if a trend was selected from Trend Discovery page (consume once)
default_index = 0
selected_from_flow = consume_selected_trend()
if selected_from_flow and selected_from_flow in trend_topics:
    default_index = trend_topics.index(selected_from_flow)

selected_topic = st.sidebar.selectbox(
    "Choose a trending topic",
    trend_topics,
    index=default_index,
    help="Select from your analysed trends"
)

selected_platform = st.sidebar.radio(
    "Target Platform",
    ["TikTok", "Instagram Reels", "YouTube Shorts"],
    help="Platform optimization for your content"
)

num_variations = st.sidebar.slider(
    "Number of Idea Variations",
    min_value=1,
    max_value=5,
    value=3,
    help="More variations = more creative options (but higher cost)"
)

# Generate Ideas Button
if st.sidebar.button("🎬 Generate Ideas", type="primary"):
    trend = analyzed_trends[selected_topic]
    
    with st.spinner("✨ Generating creative content ideas..."):
        try:
            # Extract trend data
            keywords_list = [kw[0] for kw in trend.get("keywords", [])[:10]]
            hashtags_list = [ht[0] for ht in trend.get("hashtags", [])[:10]]
            sentiment_score = trend.get("sentiment", {}).get("average", 0)
            
            # Format sentiment
            if sentiment_score > 0.1:
                sentiment = "positive"
            elif sentiment_score < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            # Generate ideas
            result = generate_content_ideas(
                trend_topic=trend["topic"],
                niche=trend["niche"],
                platform=selected_platform,  # type: ignore
                keywords=keywords_list,
                hashtags=hashtags_list,
                sentiment=sentiment,
                num_variations=num_variations
            )
            
            if result["success"]:
                # Store in session state
                st.session_state[SessionKeys.GENERATED_IDEAS] = result["ideas"]
                st.session_state[SessionKeys.CURRENT_TREND_TOPIC] = selected_topic
                st.session_state[SessionKeys.CURRENT_PLATFORM] = selected_platform
                
                st.success(f"✅ Generated {result['total_generated']} ideas in {result['generation_time']}s")
            else:
                st.error(f"❌ Generation failed: {result['error']}")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display Generated Ideas
if SessionKeys.GENERATED_IDEAS in st.session_state and st.session_state[SessionKeys.GENERATED_IDEAS]:
    st.markdown("---")
    
    # Header with regenerate button
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.subheader(f"💡 Content Ideas for: {st.session_state[SessionKeys.CURRENT_TREND_TOPIC]}")
        st.caption(f"Platform: {st.session_state[SessionKeys.CURRENT_PLATFORM]}")
    
    with col_header2:
        if st.button("🔄 Regenerate Ideas", help="Generate new ideas for the same trend"):
            trend = analyzed_trends[st.session_state[SessionKeys.CURRENT_TREND_TOPIC]]
            
            with st.spinner("✨ Regenerating content ideas..."):
                try:
                    # Extract trend data
                    keywords_list = [kw[0] for kw in trend.get("keywords", [])[:10]]
                    hashtags_list = [ht[0] for ht in trend.get("hashtags", [])[:10]]
                    sentiment_score = trend.get("sentiment", {}).get("average", 0)
                    
                    # Format sentiment
                    if sentiment_score > 0.1:
                        sentiment = "positive"
                    elif sentiment_score < -0.1:
                        sentiment = "negative"
                    else:
                        sentiment = "neutral"
                    
                    # Regenerate with same parameters
                    result = generate_content_ideas(
                        trend_topic=trend["topic"],
                        niche=trend["niche"],
                        platform=st.session_state[SessionKeys.CURRENT_PLATFORM],  # type: ignore
                        keywords=keywords_list,
                        hashtags=hashtags_list,
                        sentiment=sentiment,
                        num_variations=len(st.session_state[SessionKeys.GENERATED_IDEAS])  # Keep same number
                    )
                    
                    if result["success"]:
                        # Replace existing ideas
                        st.session_state[SessionKeys.GENERATED_IDEAS] = result["ideas"]
                        
                        st.success(f"✅ Regenerated {result['total_generated']} new ideas!")
                        st.rerun()
                    else:
                        st.error(f"❌ Regeneration failed: {result['error']}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    for idx, idea in enumerate(st.session_state[SessionKeys.GENERATED_IDEAS], 1):
        # Engagement emoji
        engagement_emoji = {
            "High": "🔥",
            "Medium": "⚡",
            "Low": "💡"
        }.get(idea.get("estimated_engagement", "Medium"), "💡")
        
        with st.expander(f"{engagement_emoji} {idx}. {idea['title']}", expanded=(idx == 1)):
            # Metadata row
            col1, col2, col3 = st.columns(3)
            col1.metric("Engagement", idea.get("estimated_engagement", "Medium"))
            col2.metric("Duration", idea.get("duration", "30-60 sec"))
            col3.metric("Style", idea.get("visual_style", "N/A"))
            
            # Hook
            st.markdown("### Hook")
            st.info(idea.get("hook", ""))
            
            # Angle
            st.markdown("### Angle")
            st.write(idea.get("angle", ""))
            
            # Description
            st.markdown("### Description")
            st.write(idea.get("description", ""))
            
            # Suggested Shots
            st.markdown("### Suggested Shots")
            shots = idea.get("suggested_shots", [])
            if shots:
                for shot_idx, shot in enumerate(shots, 1):
                    st.markdown(f"{shot_idx}. {shot}")
            else:
                st.write("No shots specified")
            
            # Caption
            st.markdown("### Caption")
            st.write(idea.get("caption", ""))
            
            # Hashtags
            st.markdown("### Hashtags")
            hashtags = idea.get("hashtags", [])
            if hashtags:
                st.write(" ".join(hashtags))
            else:
                st.write("No hashtags")
            
            # Engagement Reasoning
            if idea.get("engagement_reasoning"):
                st.markdown("### 📊 Why this engagement level?")
                st.caption(idea.get("engagement_reasoning"))
            
            # Generate Script Button
            st.markdown("---")
            script_key = f"script_{idea['idea_id']}"
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn1:
                if st.button(f"Generate Full Script", key=f"gen_script_{idx}"):
                    with st.spinner("✨ Generating detailed script..."):
                        try:
                            script_result = generate_detailed_script(idea, include_dialogue=True)
                            
                            if script_result["success"]:
                                st.session_state[script_key] = script_result["script"]
                                st.success(f"Script generated!")
                            else:
                                st.error(f" Script generation failed: {script_result['error']}")
                        except Exception as e:
                            st.error(f" Error: {str(e)}")
            
            with col_btn2:
                if st.button("📊 Optimize Engagement", key=f"optimize_{idx}"):
                    # Store idea data for Engagement Optimiser using helper function
                    set_selected_idea({
                        "title": idea.get("title", ""),
                        "hook": idea.get("hook", ""),
                        "description": idea.get("description", ""),
                        "caption": idea.get("caption", ""),
                        "hashtags": idea.get("hashtags", []),
                        "duration": idea.get("duration", "30-60 sec"),
                        "platform": st.session_state.get(SessionKeys.CURRENT_PLATFORM, "TikTok"),
                        "niche": analyzed_trends.get(st.session_state[SessionKeys.CURRENT_TREND_TOPIC], {}).get("niche", "General"),
                    })
                    st.switch_page("pages/Engagement_Optimiser.py")
            
            with col_btn3:
                is_saved = idea.get("title", "") in saved_idea_titles
                if is_saved:
                    st.success("✅ Saved")
                else:
                    if st.button("💾 Save Idea", key=f"save_idea_{idx}"):
                        save_idea(
                            user_id=user['id'],
                            idea_title=idea.get("title", ""),
                            idea_description=idea.get("description", ""),
                            platform=st.session_state.get(SessionKeys.CURRENT_PLATFORM, ""),
                            category=analyzed_trends.get(st.session_state[SessionKeys.CURRENT_TREND_TOPIC], {}).get("niche", ""),
                            trend_topic=st.session_state.get(SessionKeys.CURRENT_TREND_TOPIC, ""),
                            predicted_engagement=idea.get("estimated_engagement", "Medium")
                        )
                        st.success("✅ Idea saved!")
                        st.rerun()
            
            # Display Script if Generated
            if script_key in st.session_state:
                st.markdown("---")
                script = st.session_state[script_key]
                
                st.markdown("### Full Video Script")
                
                # Script metadata
                info_col1, info_col2, info_col3 = st.columns(3)
                info_col1.metric("Duration", script.get("total_duration", "N/A"))
                info_col2.metric("Shots", len(script.get("shots", [])))
                info_col3.metric("Props", len(script.get("props_needed", [])))
                
                # Location and Props
                st.markdown("#### Setup Requirements")
                st.write(f"**Location:** {script.get('location', 'Not specified')}")
                props = script.get("props_needed", [])
                if props:
                    st.write(f"**Props:** {', '.join(props)}")
                
                # Shot-by-Shot Breakdown
                st.markdown("#### Shot-by-Shot Breakdown")
                
                shots = script.get("shots", [])
                for shot in shots:
                    with st.container():
                        st.markdown(f"**━━━ Shot {shot.get('shot_number')} ({shot.get('timing')}) ━━━**")
                        
                        shot_col1, shot_col2 = st.columns([2, 1])
                        
                        with shot_col1:
                            st.markdown(f"🎥 **Visual:** {shot.get('visual', '')}")
                            if shot.get('dialogue'):
                                st.markdown(f" **Dialogue:** _{shot.get('dialogue')}_")
                            if shot.get('text_overlay'):
                                st.markdown(f" **Text:** `{shot.get('text_overlay')}`")
                        
                        with shot_col2:
                            if shot.get('camera_notes'):
                                st.caption(f" {shot.get('camera_notes')}")
                            if shot.get('transition'):
                                st.caption(f" {shot.get('transition')}")
                        
                        st.markdown("")
                
                # Additional Details
                col_details1, col_details2 = st.columns(2)
                
                with col_details1:
                    st.markdown("#### Music Cues")
                    music = script.get("music_cues", [])
                    if music:
                        for cue in music:
                            st.write(f"• {cue}")
                    else:
                        st.write("No music cues specified")
                    
                    st.markdown("#### Editing Notes")
                    editing = script.get("editing_notes", [])
                    if editing:
                        for note in editing:
                            st.write(f"• {note}")
                    else:
                        st.write("No editing notes")
                
                with col_details2:
                    st.markdown("#### Filming Tips")
                    tips = script.get("filming_tips", [])
                    if tips:
                        for tip in tips:
                            st.write(f"• {tip}")
                    else:
                        st.write("No filming tips")

    # What's Next? section (after all ideas)
    st.markdown("---")
    st.subheader("🚀 What's Next?")
    st.info("Click **'Optimize Engagement'** on any idea above to predict its performance and get optimization tips!")
    
    col_next1, col_next2 = st.columns(2)
    with col_next1:
        if st.button("📊 Go to Engagement Optimiser", use_container_width=True):
            st.switch_page("pages/Engagement_Optimiser.py")
    with col_next2:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.switch_page("main.py")