"""
Engagement Optimiser Page

Predict engagement scores for user-provided or AI-generated content ideas.
Displays SHAP-based explanations showing which content features drive engagement.
Allows users to optimise content and save predictions to their profile.
"""

import streamlit as st
import pandas as pd
import sys
import re
import tempfile
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Authentication
from auth.authenticator import require_auth, get_current_user
from utils.helpers import render_sidebar
from utils.session_state import SessionKeys, consume_selected_idea
from database.db_manager import save_prediction

if not require_auth():
    st.stop()
render_sidebar()

# Get current user for save functionality
user = get_current_user()

# Import model loader utilities
from utils.model_loader import (
    predict_engagement,
    validate_input,
    load_shap_explainer,
    get_valid_categories,
    get_category_aliases,
    get_valid_platforms,
    get_valid_trend_types,
    REQUIRED_FEATURES,
)

st.title("Engagement Optimiser")
st.markdown("Predict engagement potential and get data-driven suggestions to optimise your content.")

# Clear any pre-filled idea data (view-only mode now)
consume_selected_idea()

# Platform-specific styling
PLATFORM_COLORS = {
    'TikTok': '#00f2ea',
    'Instagram': '#E1306C', 
    'YouTube': '#FF0000'
}

PLATFORM_ICONS = {
    'TikTok': 'TikTok',
    'Instagram': 'Instagram',
    'YouTube': 'YouTube'
}

# --- INPUT FORM ---
st.subheader("Content Details")

# Video upload — duration auto-detected, video itself not analysed by model
uploaded_video = st.file_uploader(
    "Upload your video",
    type=["mp4", "mov", "avi", "webm"],
    help="Drop your video here. Duration will be auto-detected. The video itself won't be analysed — predictions are based on the details you fill in below."
)

# Auto-detect duration from uploaded video
detected_duration = None
if uploaded_video:
    st.video(uploaded_video)
    st.caption(f"📎 {uploaded_video.name} ({uploaded_video.size / 1024:.0f} KB)")
    
    # Try to extract duration using ffprobe
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(uploaded_video.getvalue())
            tmp_path = tmp.name
        
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", tmp_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            detected_duration = int(float(result.stdout.strip()))
            st.caption(f"Duration auto-detected: {detected_duration}s")
        
        Path(tmp_path).unlink(missing_ok=True)
    except Exception:
        pass  # ffprobe not available or failed — user can enter manually

# Caption
caption = st.text_area(
    "Caption",
    value=st.session_state.get("caption_input", ""),
    height=120,
    placeholder="Write your post caption here...",
    key="caption_input",
    help="The text content of your post. Optimal length is 100-300 characters."
)
if caption:
    char_count = len(caption)
    if 100 <= char_count <= 300:
        st.caption(f"{char_count} characters (optimal range)")
    elif char_count < 100:
        st.caption(f"{char_count} characters (short — aim for 100-300)")
    else:
        st.caption(f"{char_count} characters (long — aim for 100-300)")

# Hashtags
hashtags_raw = st.text_input(
    "Hashtags",
    value=st.session_state.get("hashtags_input", ""),
    placeholder="#fitness, #trending, #viral, #fyp, #workout",
    key="hashtags_input",
    help="Comma-separated hashtags. Optimal range is 5-10 hashtags."
)
# Parse hashtags into list
hashtags = [tag.strip() for tag in hashtags_raw.split(",") if tag.strip()] if hashtags_raw else []
if hashtags:
    count = len(hashtags)
    if 5 <= count <= 10:
        st.caption(f"{count} hashtags (optimal range)")
    else:
        st.caption(f"{count} hashtags (aim for 5-10)")

# Two-column layout for selectors
col1, col2 = st.columns(2)

# Platform options
platform_options = ["TikTok", "Instagram", "YouTube"]
platform_prefill = st.session_state.get('platform_input', "TikTok")
# Map "Instagram Reels" to "Instagram", "YouTube Shorts" to "YouTube"
if "Instagram" in platform_prefill:
    platform_prefill = "Instagram"
elif "YouTube" in platform_prefill:
    platform_prefill = "YouTube"
platform_index = platform_options.index(platform_prefill) if platform_prefill in platform_options else 0

# Category options
category_options = [
    "Tech/Gaming", "Fashion/Beauty", "Finance/Crypto", "Health/Fitness",
    "Food/Cooking", "Travel", "Entertainment/Media", "Business/Marketing",
    "Lifestyle/Vlogs", "Celebrities/Pop Culture", "Sports",
    "Politics/News", "Faith/Religion", "General"
]
niche_prefill = st.session_state.get('category_input', "General")
# Try to find matching category
category_index = 13  # Default: General
for i, cat in enumerate(category_options):
    if niche_prefill.lower() in cat.lower() or cat.lower() in niche_prefill.lower():
        category_index = i
        break

with col1:
    # Platform
    platform = st.selectbox(
        "Platform",
        platform_options,
        index=platform_index,
        help="Which platform are you posting to?"
    )

with col2:
    # Category / Niche
    category = st.selectbox(
        "Content Category",
        category_options,
        index=category_index,
        help="What niche does your content fall into?"
    )

# Posting schedule row
st.subheader("Posting Schedule")
col3, col4 = st.columns(2)

with col3:
    posting_hour = st.slider(
        "Posting Hour",
        min_value=0,
        max_value=23,
        value=19,
        help="What hour will you post? (24h format). Peak hours: 6-8 PM"
    )
    # Friendly time label
    time_period = "Morning" if 5 <= posting_hour < 12 else "Afternoon" if 12 <= posting_hour < 18 else "Evening"
    hour_label = f"{time_period} {posting_hour:02d}:00"
    if posting_hour in [18, 19, 20]:
        hour_label += " (Peak)"
    st.caption(hour_label)

with col4:
    posting_day = st.selectbox(
        "Posting Day",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        index=5,
        help="Which day of the week will you post?"
    )

# Duration — auto-detected from video, or manual entry if no video uploaded
default_duration = st.session_state.get('duration_input', 30)

if detected_duration:
    duration_sec = detected_duration
else:
    if uploaded_video:
        st.warning("Couldn't auto-detect video duration. Please enter it manually.")
        duration_sec = st.number_input(
            "Video Duration (seconds)",
            min_value=1,
            max_value=300,
            value=default_duration,
            step=5,
            help="Enter your video length manually (1-300s)"
        )
    else:
        duration_sec = st.number_input(
            "Video Duration (seconds)",
            min_value=1,
            max_value=300,
            value=default_duration,
            step=5,
            help="Upload a video to auto-detect, or enter manually (1-300s)"
        )

# Trend alignment
st.subheader("Trend Alignment")
col6, col7 = st.columns(2)

with col6:
    has_trend = st.checkbox(
        "Content is trend-aligned",
        value=st.session_state.get('has_trend_input', False),
        help="Is this content based on a current trend?"
    )

trend_type = None
if has_trend:
    with col7:
        trend_type = st.selectbox(
            "Trend Type",
            ["Rising", "Seasonal", "Stable", "Declining"],
            help="Rising: gaining popularity fast. Seasonal: recurring at certain times of year. Stable: consistently popular. Declining: losing traction."
        )

# Analyse Button
st.markdown("---")
analyse_clicked = st.button("Analyse Engagement", type="primary", use_container_width=True)

# --- RESULTS AREA ---

if analyse_clicked:
    # Build input data dictionary
    input_data = {
        'caption': caption,
        'hashtags': hashtags,
        'platform': platform,
        'posting_hour': posting_hour,
        'posting_day': (posting_day or 'monday').lower(),
        'duration_sec': duration_sec,
        'has_trend': 1 if has_trend else 0,
        'trend_type': trend_type.lower() if trend_type else None,
        'category': (category or 'general').lower(),
    }
    
    # Validate input
    is_valid, error_msg = validate_input(input_data)
    if not is_valid:
        st.error(f"{error_msg}")
    else:
        # Run prediction
        with st.spinner("Analysing engagement potential..."):
            result = predict_engagement(input_data)
        
        # Check for errors
        if 'error' in result:
            st.error(f"Prediction failed: {result['error']}")
        else:
            # Store in session state
            st.session_state[SessionKeys.OPTIMISER_INPUT] = input_data
            st.session_state[SessionKeys.OPTIMISER_RESULT] = result
            
            # Auto-save prediction
            score = result['score']
            # Calculate performance score for saving
            DATASET_AVERAGE = 7.5
            DATASET_MIN = 3.0
            DATASET_MAX = 15.0
            if score <= DATASET_AVERAGE:
                perf_score = int((score - DATASET_MIN) / (DATASET_AVERAGE - DATASET_MIN) * 50)
            else:
                perf_score = int(50 + (score - DATASET_AVERAGE) / (DATASET_MAX - DATASET_AVERAGE) * 50)
            perf_score = max(0, min(100, perf_score))
            
            save_prediction(
                user_id=user['id'],
                caption=caption[:500] if caption else "No caption",
                platform=platform,
                category=category,
                posting_hour=posting_hour,
                posting_day=posting_day,
                duration_sec=duration_sec,
                has_trend=has_trend,
                trend_type=trend_type if has_trend else None,
                predicted_engagement=score,
                performance_score=perf_score
            )
            
            # --- ENGAGEMENT SCORE ---
            st.markdown("---")
            st.subheader("Engagement Prediction")
            
            score = result['score']  # Raw engagement rate (e.g., 9 = 9%)
            prediction = result['prediction']
            confidence = result['confidence']
            probability = result['probability']
            
            # Calculate relative performance
            # Dataset average is ~7.5%, range is typically 3-15%
            DATASET_AVERAGE = 7.5
            DATASET_MIN = 3.0  # Approximate 5th percentile
            DATASET_MAX = 15.0  # Approximate 95th percentile
            
            # Normalize to 0-100 scale for "Performance Score"
            # This makes it intuitive: 50 = average, 100 = excellent
            if score <= DATASET_AVERAGE:
                # Below average: 0-50 range
                performance_score = int((score - DATASET_MIN) / (DATASET_AVERAGE - DATASET_MIN) * 50)
            else:
                # Above average: 50-100 range
                performance_score = int(50 + (score - DATASET_AVERAGE) / (DATASET_MAX - DATASET_AVERAGE) * 50)
            performance_score = max(0, min(100, performance_score))
            
            # Calculate percentage difference from average
            vs_average = ((score - DATASET_AVERAGE) / DATASET_AVERAGE) * 100
            vs_average_text = f"+{vs_average:.0f}%" if vs_average > 0 else f"{vs_average:.0f}%"
            
            # Score display with colour coding
            if performance_score >= 70:
                score_colour = "green"
                score_label = "Excellent (5/5)"
            elif performance_score >= 55:
                score_colour = "green"
                score_label = "Good (4/5)"
            elif performance_score >= 45:
                score_colour = "yellow"
                score_label = "Average (3/5)"
            elif performance_score >= 30:
                score_colour = "yellow"
                score_label = "Below Average (2/5)"
            else:
                score_colour = "red"
                score_label = "Needs Improvement (1/5)"
            
            # Main score display - clear performance indicator
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 10px; margin-bottom: 20px;">
                <h1 style="font-size: 3rem; margin: 0;">{performance_score}</h1>
                <p style="font-size: 1.2rem; color: #888; margin: 5px 0;">Performance Score</p>
                <p style="font-size: 1.5rem; margin: 10px 0;">{score_label}</p>
                <p style="font-size: 1rem; color: {'#2ecc71' if vs_average > 0 else '#e74c3c' if vs_average < 0 else '#888'};">
                    {vs_average_text} vs average
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics row with context
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            
            with col_s1:
                st.metric(
                    label="Engagement Rate",
                    value=f"{score}%",
                    delta=f"{vs_average_text} vs avg",
                    help="Predicted engagement rate (likes+comments / views)"
                )
            
            with col_s2:
                st.metric(
                    label="Rating",
                    value=f"{score_colour} {score_label}",
                    help="Excellent: top 30%, Good: top 50%, Average: middle, Below Average: bottom 50%"
                )
            
            with col_s3:
                st.metric(
                    label="Confidence",
                    value=confidence,
                    help="How confident the model is in this prediction"
                )
            
            with col_s4:
                st.metric(
                    label="Avg. Rate",
                    value=f"{DATASET_AVERAGE}%",
                    help="Average engagement rate across all content in our dataset"
                )
            
            # Progress bar with context
            st.progress(performance_score / 100, text=f"{score_label} ({score}% engagement rate)")
            
            # Contextual explanation
            with st.expander("What do these numbers mean?"):
                st.markdown(f"""
                **Understanding Engagement Rates:**
                
                Engagement rate is calculated as (likes + comments) / views × 100. Here's how to interpret your score:
                
                | Engagement Rate | Performance | What it means |
                |-----------------|-------------|---------------|
                | **10%+** | Excellent (5/5) | Top-performing content |
                | **8-10%** | Good (4/5) | Above average |
                | **6-8%** | Average (3/5) | Typical performance |
                | **4-6%** | Below Average (2/5) | Room for improvement |
                | **<4%** | Low (1/5) | Needs optimisation |
                
                **Your prediction: {score}%** → This puts you in the **{score_label.lower()}** category.
                
                *Note: Engagement rates vary by platform. TikTok typically sees higher rates (8-15%) while YouTube tends to be lower (3-8%).*
                """)
            
            # Model info
            st.caption(f"Model: {result['model_version']} · {result['features_used']} features analysed")
            
            # Input summary
            with st.expander("Input Summary"):
                sum_col1, sum_col2 = st.columns(2)
                with sum_col1:
                    st.write(f"**Caption:** {len(caption)} characters")
                    st.write(f"**Hashtags:** {len(hashtags)} tags")
                    st.write(f"**Platform:** {platform}")
                    st.write(f"**Category:** {category}")
                with sum_col2:
                    st.write(f"**Posting Time:** {posting_day} at {posting_hour:02d}:00")
                    st.write(f"**Duration:** {duration_sec}s")
                    st.write(f"**Trend:** {'Yes (' + (trend_type or '') + ')' if has_trend else 'No'}")
                    st.write(f"**Probability:** {probability:.4f}")

            # --- XAI EXPLANATIONS SECTION ---
            st.markdown("---")
            st.subheader("Why This Score?")
            
            # Load SHAP explainer and generate explanation
            try:
                explainer = load_shap_explainer()
                if explainer and 'features_df' in result:
                    explanation = explainer.explain(result['features_df'])
                    
                    # Display human-readable explanation
                    st.markdown(explanation['explanation_text'])
                    
                    # Top feature contributions
                    with st.expander("Feature Contributions (SHAP Analysis)", expanded=True):
                        contributions = explanation['feature_contributions'].copy()
                        
                        # Filter: For one-hot encoded features, only show active ones (value=1)
                        def is_active_feature(row):
                            feat = row['feature']
                            if any(prefix in feat for prefix in ['platform_', 'category_', 'trend_label_', 'season_']):
                                return row['value'] == 1
                            return True
                        
                        active_contribs = contributions[contributions.apply(is_active_feature, axis=1)]
                        chart_data = active_contribs.sort_values('abs_shap', ascending=False).head(10)
                        
                        # Create a horizontal bar chart
                        import plotly.express as px
                        
                        chart_data = chart_data.copy()
                        chart_data['color'] = chart_data['shap_value'].apply(lambda x: 'Positive' if x > 0 else 'Negative')
                        chart_data['shap_pct'] = chart_data['shap_value'] * 100  # Convert to percentage points
                        
                        fig = px.bar(
                            chart_data,
                            x='shap_pct',
                            y='display_name',
                            orientation='h',
                            color='color',
                            color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c'},
                            labels={'shap_pct': 'Impact on Engagement (%)', 'display_name': 'Feature'},
                            title='Top Factors Influencing Your Engagement Prediction'
                        )
                        fig.update_layout(
                            showlegend=True,
                            legend_title_text='Impact',
                            yaxis={'categoryorder': 'total ascending'},
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Baseline info
                        st.caption(f"Baseline engagement: {explanation['baseline']*100:.2f}% (average across all content)")
                    
                    # Model Limitations & Fairness Disclaimer
                    with st.expander("About These Predictions (Model Limitations & Fairness)", expanded=False):
                        limitations = explainer.get_model_limitations()
                        st.warning(limitations['performance_caveat'])
                        st.info(limitations['data_bias_note'])
                        st.info(limitations['fairness_consideration'])
                        st.error(limitations['what_we_cant_predict'])
                    
                    # --- OPTIMISATION SUGGESTIONS ---
                    st.markdown("---")
                    st.subheader("Optimisation Suggestions")
                    
                    suggestions = explanation.get('suggestions', [])
                    if suggestions:
                        for i, suggestion in enumerate(suggestions, 1):
                            st.markdown(f"**{i}.** {suggestion}")
                    else:
                        st.success("Your content is well-optimised! No major improvements suggested.")
                    
                    # Quick optimisation tips based on current input
                    st.markdown("---")
                    st.subheader("Quick Wins")
                    
                    quick_wins = []
                    
                    # Caption length optimisation
                    caption_len = len(caption)
                    if caption_len < 100:
                        quick_wins.append({
                            'tip': 'Extend your caption',
                            'detail': f'Your caption is {caption_len} chars. Aim for 100-200 characters for better engagement.',
                            'impact': '+0.5-1%'
                        })
                    elif caption_len > 300:
                        quick_wins.append({
                            'tip': 'Shorten your caption',
                            'detail': f'Your caption is {caption_len} chars. Keep it under 300 for best results.',
                            'impact': '+0.3%'
                        })
                    
                    # Posting time optimisation
                    if posting_hour not in [18, 19, 20, 21]:
                        quick_wins.append({
                            'tip': 'Post during peak hours',
                            'detail': f'You selected {posting_hour}:00. Peak engagement is 6-9 PM.',
                            'impact': '+0.5-1%'
                        })
                    
                    # Weekend posting
                    if (posting_day or '').lower() not in ['saturday', 'sunday']:
                        quick_wins.append({
                            'tip': 'Consider weekend posting',
                            'detail': f'Weekends typically see higher engagement than {posting_day}.',
                            'impact': '+0.3-0.5%'
                        })
                    
                    # Emoji and CTA check
                    features_df = result.get('features_df')
                    if features_df is not None:
                        if features_df['has_emoji'].values[0] == 0:
                            quick_wins.append({
                                'tip': 'Add emojis to your caption',
                                'detail': 'Captions with emojis tend to get more engagement.',
                                'impact': '+0.2-0.5%'
                            })
                        if features_df['has_call_to_action'].values[0] == 0:
                            quick_wins.append({
                                'tip': 'Add a call-to-action',
                                'detail': 'Include phrases like "Follow for more", "Comment below", or "Link in bio".',
                                'impact': '+0.3-0.7%'
                            })
                    
                    # Trend alignment
                    if not has_trend:
                        quick_wins.append({
                            'tip': 'Align with current trends',
                            'detail': 'Content aligned with rising trends typically sees higher engagement.',
                            'impact': '+0.5-1.5%'
                        })
                    
                    if quick_wins:
                        for qw in quick_wins:
                            with st.container():
                                col_tip, col_impact = st.columns([4, 1])
                                with col_tip:
                                    st.markdown(f"**{qw['tip']}**")
                                    st.caption(qw['detail'])
                                with col_impact:
                                    st.metric(label="Est. Impact", value=qw['impact'], delta=None)
                    else:
                        st.success("Great job! Your content is already well-optimised.")
                    
                    # Store explanation in session state for optimisation suggestions
                    st.session_state[SessionKeys.CURRENT_EXPLANATION] = explanation
                    
                else:
                    st.info("SHAP explanations not available. The model prediction is based on your content's features compared to historical data.")
                    
            except Exception as e:
                st.warning(f"Could not generate explanation: {str(e)}")
                st.info("The engagement prediction is still valid - explanations are an optional enhancement.")

# What's Next? section (always visible)
st.markdown("---")
st.subheader("What's Next?")
st.info("After analysing your content, you can refine your ideas or explore new trends!")

col_next1, col_next2, col_next3 = st.columns(3)
with col_next1:
    if st.button("Discover More Trends", use_container_width=True):
        st.switch_page("pages/Trend_Discovery.py")
with col_next2:
    if st.button("Generate New Ideas", use_container_width=True):
        st.switch_page("pages/Content_Ideation.py")
with col_next3:
    if st.button("Back to Dashboard", use_container_width=True):
        st.switch_page("main.py")