# Model Loader Utility for Creator Compass

# This module provides functions to load, cache, and use the engagement prediction model.

import joblib
import pandas as pd
import numpy as np
import json
import streamlit as st
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime



# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "engagement_model_logistic_regression.pkl"
SHAP_PATH = MODELS_DIR / "shap_explainer.pkl"
CONFIG_PATH = MODELS_DIR / "model_config.json"

# Feature list (MUST match training order else predictions may be wrong - 22 features)
REQUIRED_FEATURES = [
    # Trend features (5)
    "has_trend",
    "trend_rising",
    "trend_seasonal",
    "trend_stable",
    "trend_declining",
    
    # Temporal features (6)
    "posting_hour",
    "posting_day",
    "posting_month",
    "is_peak_hour",
    "is_weekend",
    "is_evening",
    
    # Content features (7)
    "caption_length",
    "hashtag_count",
    "duration_sec",
    "optimal_hashtag_range",
    "has_optimal_caption",
    "has_short_caption",
    "has_long_caption",
    
    # Platform features (3)
    "platform_tiktok",
    "platform_instagram",
    "platform_youtube",
    
    # Category feature (1)
    "category_encoded"
]

# Platform list
VALID_PLATFORMS = ['tiktok', 'instagram', 'youtube']

# Trend types
VALID_TREND_TYPES = ['rising', 'seasonal', 'stable', 'declining']

# Category mapping (simplified for MVP) - model needs numeric encoding
CATEGORY_MAPPING = {
    'tech/gaming': 0,
    'tech': 0,
    'gaming': 0,
    'fashion/beauty': 1,
    'fashion': 1,
    'beauty': 1,
    'finance/crypto': 2,
    'finance': 2,
    'crypto': 2,
    'health/fitness': 3,
    'health': 3,
    'fitness': 3,
    'food/cooking': 4,
    'food': 4,
    'cooking': 4,
    'travel': 5,
    'entertainment/media': 6,
    'entertainment': 6,
    'media': 6,
    'business/marketing': 7,
    'business': 7,
    'marketing': 7,
    'lifestyle/vlogs': 8,
    'lifestyle': 8,
    'vlogs': 8,
    'celebrities/pop culture': 9,
    'celebrities': 9,
    'pop culture': 9,
    'sports': 10,
    'politics/news': 11,
    'politics': 11,
    'news': 11,
    'faith/religion': 12,
    'faith': 12,
    'religion': 12,
    'general': 13
}

# Day of week mapping
DAY_MAPPING = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6
}



# MODEL LOADING FUNCTIONS

@st.cache_resource # Cache the loaded model to avoid reloading on every prediction
# loads trained model from disk and caches it for future use
def load_model():
   
    try:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Please ensure the model has been trained."
            )
        
        model = joblib.load(MODEL_PATH)
        print(f" Model loaded successfully from {MODEL_PATH}")
        return model
        
    except Exception as e:
        print(f" Error loading model: {str(e)}")
        raise


@st.cache_resource 
# loads SHAP explainer from disk and caches it for future use
def load_shap_explainer():
  
    try:
        if not SHAP_PATH.exists():
            raise FileNotFoundError(
                f"SHAP explainer not found at {SHAP_PATH}. "
                "Explainability features may not work."
            )
        
        explainer = joblib.load(SHAP_PATH)
        print(f"SHAP explainer loaded successfully from {SHAP_PATH}")
        return explainer
        
    except Exception as e:
        print(f" Warning: Could not load SHAP explainer: {str(e)}")
        return None

# loads models metadate from config file 
def load_model_config() -> Dict[str, Any]:

    try:
        if not CONFIG_PATH.exists():
            print(f"  Warning: Config not found at {CONFIG_PATH}")
            return {}
        
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        
        return config
        
    except Exception as e:
        print(f" Warning: Could not load config: {str(e)}")
        return {}


# FEATURE ENGINEERING FUNCTIONS

def prepare_features(input_data: Dict[str, Any]) -> pd.DataFrame:
   
    # Extract input with defaults
    caption = input_data.get('caption', '')
    hashtags = input_data.get('hashtags', [])
    platform = input_data.get('platform', 'tiktok').lower()
    posting_hour = input_data.get('posting_hour', 19)  # Default: 7 PM
    posting_day = input_data.get('posting_day', 'saturday')  # Default: Saturday
    duration_sec = input_data.get('duration_sec', 30)
    has_trend = input_data.get('has_trend', 0)
    trend_type = input_data.get('trend_type', None)
    category = input_data.get('category', 'general').lower()
    
    # Initialize feature dictionary
    features = {}
    
  
    # 1. TREND FEATURES
 
    features['has_trend'] = int(has_trend)
    
    # One-hot encode trend type (only if has_trend=1)
    if features['has_trend'] == 1 and trend_type:
        trend_type_lower = trend_type.lower()
        features['trend_rising'] = 1 if trend_type_lower == 'rising' else 0
        features['trend_seasonal'] = 1 if trend_type_lower == 'seasonal' else 0
        features['trend_stable'] = 1 if trend_type_lower == 'stable' else 0
        features['trend_declining'] = 1 if trend_type_lower == 'declining' else 0
    else:
        features['trend_rising'] = 0
        features['trend_seasonal'] = 0
        features['trend_stable'] = 0
        features['trend_declining'] = 0
    

    # 2. TEMPORAL FEATURES
    features['posting_hour'] = int(posting_hour)
    
    # Convert day to number if string
    if isinstance(posting_day, str):
        features['posting_day'] = DAY_MAPPING.get(posting_day.lower(), 5)  # Default Saturday
    else:
        features['posting_day'] = int(posting_day)
    
    # Current month (or could be from input)
    features['posting_month'] = datetime.now().month
    
    # Derived temporal features
    features['is_peak_hour'] = 1 if features['posting_hour'] in [18, 19, 20] else 0
    features['is_weekend'] = 1 if features['posting_day'] in [5, 6] else 0
    features['is_evening'] = 1 if features['posting_hour'] >= 18 else 0

    # 3. CONTENT FEATURES
    features['caption_length'] = len(caption)
    features['hashtag_count'] = len(hashtags)
    features['duration_sec'] = int(duration_sec)
    
    # Derived content features
    features['optimal_hashtag_range'] = 1 if 5 <= features['hashtag_count'] <= 10 else 0
    features['has_optimal_caption'] = 1 if 100 <= features['caption_length'] <= 300 else 0
    features['has_short_caption'] = 1 if features['caption_length'] < 100 else 0
    features['has_long_caption'] = 1 if features['caption_length'] > 300 else 0
    

    # 4. PLATFORM FEATURES (one-hot)
    platform_clean = platform.replace(' ', '').lower()
    if 'youtube' in platform_clean:
        platform_clean = 'youtube'
    elif 'instagram' in platform_clean or 'insta' in platform_clean:
        platform_clean = 'instagram'
    elif 'tiktok' in platform_clean or 'tik tok' in platform_clean:
        platform_clean = 'tiktok'
    
    features['platform_tiktok'] = 1 if platform_clean == 'tiktok' else 0
    features['platform_instagram'] = 1 if platform_clean == 'instagram' else 0
    features['platform_youtube'] = 1 if platform_clean == 'youtube' else 0
    
    # 5. CATEGORY FEATURE
    features['category_encoded'] = CATEGORY_MAPPING.get(category, 13)  # Default: general

    # CREATE DATAFRAME WITH FEATURES IN CORRECT ORDER
    df = pd.DataFrame([features], columns=REQUIRED_FEATURES)
    
    # Ensure all numeric types
    df = df.astype(float)
    
    return df


# PREDICTION FUNCTIONS
# Takes raw input data, prepares features, and returns prediction results

def predict_engagement(input_data: Dict[str, Any]) -> Dict[str, Any]:
 
    try:
        # Load model (cached)
        model = load_model()
        
        # Prepare features
        features_df = prepare_features(input_data)
        
        # Make predictions
        probability = model.predict_proba(features_df)[0, 1]  # Probability of class 1 (High)
        binary_pred = model.predict(features_df)[0]  # 0 or 1
        
        # Calculate confidence level
        if probability > 0.75 or probability < 0.25:
            confidence = 'High'
        elif probability > 0.55 or probability < 0.45:
            confidence = 'Medium'
        else:
            confidence = 'Low'
        
        # Load config for version info
        config = load_model_config()
        model_version = config.get('model_info', {}).get('name', 'Logistic Regression v1.0')
        
        # Format result
        result = {
            'probability': float(probability),
            'score': int(probability * 100),
            'prediction': 'High' if binary_pred == 1 else 'Low',
            'confidence': confidence,
            'features_used': len(REQUIRED_FEATURES),
            'model_version': model_version,
            'features_df': features_df  # Include for debugging/SHAP
        }
        
        return result
        
    except Exception as e:
        print(f" Prediction error: {str(e)}")
        return {
            'error': str(e),
            'probability': 0.5,
            'score': 50,
            'prediction': 'Unknown',
            'confidence': 'Low',
            'features_used': 0,
            'model_version': 'Error'
        }


# HELPER FUNCTIONS

def get_category_mapping() -> Dict[str, int]:
    return CATEGORY_MAPPING.copy()


def get_valid_platforms() -> list:
    return VALID_PLATFORMS.copy()


def get_valid_trend_types() -> list:
    return VALID_TREND_TYPES.copy()

# checks user inpyt before it reaches the model 
def validate_input(input_data: Dict[str, Any]) -> tuple[bool, str]:

    # Check required fields
    if 'platform' not in input_data:
        return False, "Missing required field: 'platform'"
    
    # Validate platform
    platform = input_data['platform'].lower()
    if not any(p in platform for p in VALID_PLATFORMS):
        return False, f"Invalid platform. Must be one of: {VALID_PLATFORMS}"
    
    # Validate posting_hour if provided
    if 'posting_hour' in input_data:
        hour = input_data['posting_hour']
        if not (0 <= hour <= 23):
            return False, f"Invalid posting_hour: {hour}. Must be 0-23"
    
    # Validate duration if provided
    if 'duration_sec' in input_data:
        duration = input_data['duration_sec']
        if duration < 0 or duration > 300:
            return False, f"Invalid duration_sec: {duration}. Must be 0-300"
    
    # Validate hashtags if provided
    if 'hashtags' in input_data:
        if not isinstance(input_data['hashtags'], list):
            return False, "hashtags must be a list"
    
    # All validations passed
    return True, ""

if __name__ == "__main__":
    print("=" * 70)
    print("MODEL LOADER UTILITY - Creator Compass")
    print("=" * 70)
    print(f"\nModel Path: {MODEL_PATH}")
    print(f"SHAP Path: {SHAP_PATH}")
    print(f"Config Path: {CONFIG_PATH}")
    print(f"\nRequired Features: {len(REQUIRED_FEATURES)}")
    print(f"Valid Platforms: {VALID_PLATFORMS}")
    print(f"Valid Trend Types: {VALID_TREND_TYPES}")
    print(f"Categories: {len(CATEGORY_MAPPING)}")
    print("\n" + "=" * 70)
