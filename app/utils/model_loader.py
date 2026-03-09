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
MODEL_PATH = MODELS_DIR / "engagement_model_random_forest.joblib"  # Random Forest model
METADATA_PATH = MODELS_DIR / "model_metadata.json"  # Model metadata with feature list
CONFIG_PATH = MODELS_DIR / "model_config_rf.json"  # RF model config (replace old Ridge config)

# Import EngagementExplainer for SHAP explanations
EngagementExplainer = None  # Type placeholder
EXPLAINER_AVAILABLE = False
try:
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.xai.explainer import EngagementExplainer
    EXPLAINER_AVAILABLE = True
except ImportError:
    print("Warning: EngagementExplainer not available - XAI features disabled")

# Load feature list from metadata (MUST match training order)
def _load_features_from_metadata():
    """Load feature names from model metadata file."""
    if METADATA_PATH.exists():
        with open(METADATA_PATH, 'r') as f:
            metadata = json.load(f)
        return metadata.get('features', [])
    return []

REQUIRED_FEATURES = _load_features_from_metadata()

# If metadata not available, fall back to hardcoded list (39 features for RF model)
if not REQUIRED_FEATURES:
    REQUIRED_FEATURES = [
        # Core features
        "caption_length", "posting_hour", "is_weekend", "duration_sec",
        "has_emoji", "has_call_to_action",
        # Platform (one-hot, note: instagram is reference category so not included)
        "platform_tiktok", "platform_youtube",
        # Categories (one-hot)
        "category_art", "category_automotive", "category_beauty", "category_comedy",
        "category_diy", "category_education", "category_fashion", "category_finance",
        "category_fitness", "category_food", "category_gaming", "category_lifestyle",
        "category_music", "category_news", "category_pets", "category_science",
        "category_sports", "category_tech", "category_travel",
        # Trends (one-hot)
        "trend_label_declining", "trend_label_rising", "trend_label_seasonal", "trend_label_stable",
        # Seasons (one-hot)
        "season_fall", "season_spring", "season_summer", "season_winter",
        # Other
        "media_type_nan", "posting_day_encoded", "caption_bin_encoded", "posting_hour_bin_encoded"
    ]

print(f"Model features loaded: {len(REQUIRED_FEATURES)} features")

# Platform list
VALID_PLATFORMS = ['tiktok', 'instagram', 'youtube']

# Trend types
VALID_TREND_TYPES = ['rising', 'seasonal', 'stable', 'declining']

# Valid categories (must match training one-hot columns)
VALID_CATEGORIES = [
    'art', 'automotive', 'beauty', 'comedy', 'diy', 'education', 'fashion',
    'finance', 'fitness', 'food', 'gaming', 'lifestyle', 'music', 'news',
    'pets', 'science', 'sports', 'tech', 'travel'
]

# Valid seasons (must match training one-hot columns)
VALID_SEASONS = ['fall', 'spring', 'summer', 'winter']

# Category aliases for user-facing categories
CATEGORY_ALIASES = {
    'technology': 'tech',
    'tech/gaming': 'tech',
    'fashion/beauty': 'beauty',
    'health/fitness': 'fitness',
    'health': 'fitness',
    'food/cooking': 'food',
    'cooking': 'food',
    'entertainment': 'comedy',
    'entertainment/media': 'comedy',
    'media': 'comedy',
    'business': 'finance',
    'business/marketing': 'finance',
    'marketing': 'finance',
    'lifestyle/vlogs': 'lifestyle',
    'vlogs': 'lifestyle',
    'celebrities': 'news',
    'celebrities/pop culture': 'news',
    'pop culture': 'news',
    'politics': 'news',
    'politics/news': 'news',
    'faith/religion': 'lifestyle',
    'faith': 'lifestyle',
    'religion': 'lifestyle',
    'finance/crypto': 'finance',
    'crypto': 'finance',
    'general': 'lifestyle',
    'photography': 'art',
}

# Label encoder mappings (alphabetical order as used by sklearn LabelEncoder)
# posting_day: Friday=0, Monday=1, Saturday=2, Sunday=3, Thursday=4, Tuesday=5, Wednesday=6
DAY_LABEL_ENCODER = {
    'friday': 0, 'monday': 1, 'saturday': 2, 'sunday': 3,
    'thursday': 4, 'tuesday': 5, 'wednesday': 6
}

# caption_bin: ['0-50', '101-150', '151-200', '201-300', '300+', '51-100'] -> 0-5 alphabetically
CAPTION_BIN_ENCODER = {
    '0-50': 0, '101-150': 1, '151-200': 2, '201-300': 3, '300+': 4, '51-100': 5
}

# posting_hour_bin: ['Afternoon', 'Evening', 'Morning', 'Night'] -> 0-3 alphabetically
HOUR_BIN_ENCODER = {
    'afternoon': 0, 'evening': 1, 'morning': 2, 'night': 3
}

# Output scaling parameters (loaded from model_config.json at startup)
# RF model outputs engagement rate directly - light scaling for display
_OUTPUT_SCALING = {
    'display_min': 0.01,
    'display_max': 0.50,  # Cap at 50% engagement (realistic maximum)
}
try:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as _f:
            _cfg = json.load(_f)
        if 'output_scaling' in _cfg:
            _OUTPUT_SCALING.update(_cfg['output_scaling'])
except Exception:
    pass


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
# loads SHAP explainer using EngagementExplainer class
def load_shap_explainer():
    """
    Load SHAP explainer for engagement predictions.
    Uses EngagementExplainer class which creates TreeExplainer for Random Forest.
    """
    try:
        if not EXPLAINER_AVAILABLE or EngagementExplainer is None:
            raise ImportError("EngagementExplainer not available")
        
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Please ensure the model has been trained."
            )
        
        explainer = EngagementExplainer.load(  # type: ignore
            str(MODEL_PATH), 
            str(METADATA_PATH) if METADATA_PATH.exists() else None
        )
        print(f"EngagementExplainer loaded successfully with {len(explainer.feature_names)} features")
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

import re

def _detect_emoji(text: str) -> bool:
    """Detect if text contains emoji."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return bool(emoji_pattern.search(text))


def _detect_cta(text: str) -> bool:
    """Detect if text contains call-to-action keywords."""
    cta_keywords = [
        'link in bio', 'follow', 'subscribe', 'click', 'check out',
        'visit', 'shop', 'buy', 'get', 'download', 'join', 'sign up',
        'watch', 'see more', 'learn more', 'dm me', 'comment', 'tag'
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in cta_keywords)


def _get_season(month: int) -> str:
    """Get season from month (1-12)."""
    if month in [3, 4, 5]:
        return 'spring'
    elif month in [6, 7, 8]:
        return 'summer'
    elif month in [9, 10, 11]:
        return 'fall'
    else:  # 12, 1, 2
        return 'winter'


def _get_caption_bin(length: int) -> str:
    """Bin caption length into categories matching training data."""
    if length <= 50:
        return '0-50'
    elif length <= 100:
        return '51-100'
    elif length <= 150:
        return '101-150'
    elif length <= 200:
        return '151-200'
    elif length <= 300:
        return '201-300'
    else:
        return '300+'


def _get_hour_bin(hour: int) -> str:
    """Bin posting hour into time-of-day categories."""
    if hour < 6:
        return 'night'
    elif hour < 12:
        return 'morning'
    elif hour < 18:
        return 'afternoon'
    else:
        return 'evening'


def prepare_features(input_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Prepare features for engagement model prediction.
    
    Generates exactly the 39 features expected by the Random Forest model,
    in the correct order as specified in model_metadata.json.
    """
    # Extract input with defaults
    caption = input_data.get('caption', '')
    platform = input_data.get('platform', 'tiktok').lower()
    posting_hour = input_data.get('posting_hour', 19)  # Default: 7 PM
    posting_day = input_data.get('posting_day', 'saturday').lower()  # Default: Saturday
    duration_sec = input_data.get('duration_sec', 30)
    trend_type = input_data.get('trend_type', None)  # 'rising', 'seasonal', 'stable', 'declining'
    category = input_data.get('category', 'lifestyle').lower()
    month = input_data.get('month', datetime.now().month)  # For season calculation
    has_media = input_data.get('has_media', True)  # Whether post has media
    
    # Normalize category using aliases
    category = CATEGORY_ALIASES.get(category, category)
    if category not in VALID_CATEGORIES:
        category = 'lifestyle'  # Default fallback
    
    # Initialize feature dictionary (in model feature order)
    features = {}
    
    # ══════════════════════════════════════════════════════════════════════════
    # 1. CORE NUMERIC FEATURES (features 1-6)
    # ══════════════════════════════════════════════════════════════════════════
    features['caption_length'] = len(caption)
    features['posting_hour'] = int(posting_hour)
    
    # is_weekend: based on day name
    if isinstance(posting_day, str):
        day_lower = posting_day.lower()
        features['is_weekend'] = 1 if day_lower in ['saturday', 'sunday'] else 0
    else:
        features['is_weekend'] = 1 if posting_day in [5, 6] else 0
    
    features['duration_sec'] = int(duration_sec)
    features['has_emoji'] = 1 if _detect_emoji(caption) else 0
    features['has_call_to_action'] = 1 if _detect_cta(caption) else 0
    
    # ══════════════════════════════════════════════════════════════════════════
    # 2. PLATFORM ONE-HOT (features 7-8) - instagram is reference category
    # ══════════════════════════════════════════════════════════════════════════
    platform_clean = platform.replace(' ', '').lower()
    if 'youtube' in platform_clean:
        platform_clean = 'youtube'
    elif 'instagram' in platform_clean or 'insta' in platform_clean:
        platform_clean = 'instagram'
    elif 'tiktok' in platform_clean or 'tik tok' in platform_clean:
        platform_clean = 'tiktok'
    
    features['platform_tiktok'] = 1 if platform_clean == 'tiktok' else 0
    features['platform_youtube'] = 1 if platform_clean == 'youtube' else 0
    
    # ══════════════════════════════════════════════════════════════════════════
    # 3. CATEGORY ONE-HOT (features 9-27) - 19 categories alphabetically
    # ══════════════════════════════════════════════════════════════════════════
    for cat in VALID_CATEGORIES:
        features[f'category_{cat}'] = 1 if category == cat else 0
    
    # ══════════════════════════════════════════════════════════════════════════
    # 4. TREND LABEL ONE-HOT (features 28-31)
    # ══════════════════════════════════════════════════════════════════════════
    trend_lower = trend_type.lower() if trend_type else None
    for trend in VALID_TREND_TYPES:
        features[f'trend_label_{trend}'] = 1 if trend_lower == trend else 0
    
    # ══════════════════════════════════════════════════════════════════════════
    # 5. SEASON ONE-HOT (features 32-35)
    # ══════════════════════════════════════════════════════════════════════════
    current_season = _get_season(month)
    for season in VALID_SEASONS:
        features[f'season_{season}'] = 1 if current_season == season else 0
    
    # ══════════════════════════════════════════════════════════════════════════
    # 6. ENCODED FEATURES (features 36-39)
    # ══════════════════════════════════════════════════════════════════════════
    # media_type_nan: 1 if no media type info, 0 if known
    features['media_type_nan'] = 0 if has_media else 1
    
    # posting_day_encoded: LabelEncoder (alphabetical)
    if isinstance(posting_day, str):
        day_lower = posting_day.lower()
        features['posting_day_encoded'] = DAY_LABEL_ENCODER.get(day_lower, 2)  # Default: Saturday=2
    else:
        # Convert numeric day (0=Mon,...,6=Sun) to label encoded value
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_name = day_names[posting_day % 7]
        features['posting_day_encoded'] = DAY_LABEL_ENCODER.get(day_name, 2)
    
    # caption_bin_encoded: LabelEncoder on binned caption lengths
    caption_bin = _get_caption_bin(features['caption_length'])
    features['caption_bin_encoded'] = CAPTION_BIN_ENCODER.get(caption_bin, 0)
    
    # posting_hour_bin_encoded: LabelEncoder on time-of-day bins
    hour_bin = _get_hour_bin(features['posting_hour'])
    features['posting_hour_bin_encoded'] = HOUR_BIN_ENCODER.get(hour_bin, 0)
    
    # ══════════════════════════════════════════════════════════════════════════
    # CREATE DATAFRAME WITH FEATURES IN CORRECT ORDER
    # ══════════════════════════════════════════════════════════════════════════
    df = pd.DataFrame([features])
    
    # Ensure columns are in the exact order expected by the model
    df = df[REQUIRED_FEATURES]
    
    # Ensure all numeric types
    df = df.astype(float)
    
    return df


# PREDICTION FUNCTIONS
# Takes raw input data, prepares features, and returns prediction results

def predict_engagement(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict engagement rate for content using the Random Forest model.
    
    Args:
        input_data: Dictionary containing content parameters (caption, platform, etc.)
    
    Returns:
        Dictionary with prediction results including probability, score, confidence
    """
    try:
        # Load model (cached)
        model = load_model()
        
        # Prepare features (generates exactly 39 features in correct order)
        features_df = prepare_features(input_data)
        
        # Random Forest regression prediction
        # Model outputs engagement rate directly (trained on engagement_rate 0-1)
        raw_pred = float(model.predict(features_df)[0])
        
        # Clamp to reasonable display range
        d_min = _OUTPUT_SCALING['display_min']
        d_max = _OUTPUT_SCALING['display_max']
        probability = np.clip(raw_pred, d_min, d_max)
        
        # Binary prediction (high vs low engagement)
        # Dataset mean is ~7.5%, so above 8% is considered "High"
        binary_pred = 1 if probability >= 0.08 else 0
        
        # Confidence level based on how far from average threshold
        if probability > 0.12 or probability < 0.04:
            confidence = 'High'
        elif probability > 0.10 or probability < 0.06:
            confidence = 'Medium'
        else:
            confidence = 'Low'
        
        # Load config for version info
        config = load_model_config()
        model_version = config.get('model_info', {}).get('name', 'Random Forest v1.0')
        
        # Format result
        result = {
            'probability': float(probability),
            'score': int(probability * 100),  # Convert to percentage (0-100)
            'raw_prediction': float(raw_pred),  # Unclamped model output
            'prediction': 'High' if binary_pred == 1 else 'Low',
            'confidence': confidence,
            'features_used': len(REQUIRED_FEATURES),
            'model_version': model_version,
            'features_df': features_df  # Include for SHAP explanations
        }
        
        return result
        
    except Exception as e:
        print(f" Prediction error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'probability': 0.05,
            'score': 5,
            'prediction': 'Unknown',
            'confidence': 'Low',
            'features_used': 0,
            'model_version': 'Error'
        }


# HELPER FUNCTIONS

def get_valid_categories() -> list:
    """Return list of valid content categories."""
    return VALID_CATEGORIES.copy()


def get_category_aliases() -> Dict[str, str]:
    """Return category alias mapping for user-facing conversions."""
    return CATEGORY_ALIASES.copy()


def get_valid_platforms() -> list:
    return VALID_PLATFORMS.copy()


def get_valid_trend_types() -> list:
    return VALID_TREND_TYPES.copy()


def get_valid_seasons() -> list:
    return VALID_SEASONS.copy()


# checks user input before it reaches the model 
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
        if duration < 0 or duration > 3600:
            return False, f"Invalid duration_sec: {duration}. Must be 0-3600"
    
    # Validate category if provided
    if 'category' in input_data:
        category = input_data['category'].lower()
        # Check if it's a valid category or has an alias
        if category not in VALID_CATEGORIES and category not in CATEGORY_ALIASES:
            return False, f"Unknown category: {category}. Valid categories: {VALID_CATEGORIES}"
    
    # All validations passed
    return True, ""


if __name__ == "__main__":
    print("=" * 70)
    print("MODEL LOADER UTILITY - Creator Compass")
    print("=" * 70)
    print(f"\nModel Path: {MODEL_PATH}")
    print(f"Metadata Path: {METADATA_PATH}")
    print(f"Config Path: {CONFIG_PATH}")
    print(f"\nRequired Features: {len(REQUIRED_FEATURES)}")
    print(f"Feature list: {REQUIRED_FEATURES}")
    print(f"\nValid Platforms: {VALID_PLATFORMS}")
    print(f"Valid Categories: {len(VALID_CATEGORIES)}")
    print(f"Valid Trend Types: {VALID_TREND_TYPES}")
    print(f"Valid Seasons: {VALID_SEASONS}")
    
    # Test prediction
    print("\n" + "-" * 70)
    print("Testing prediction...")
    test_input = {
        'caption': 'Check out this amazing fitness tip! 💪 Follow for more! #fitness',
        'platform': 'tiktok',
        'posting_hour': 19,
        'posting_day': 'saturday',
        'duration_sec': 45,
        'trend_type': 'rising',
        'category': 'fitness'
    }
    result = predict_engagement(test_input)
    print(f"Test prediction result: {result['score']}% ({result['prediction']})")
    print(f"Features used: {result['features_used']}")
    print(f"Model version: {result['model_version']}")
    
    print("\n" + "=" * 70)
