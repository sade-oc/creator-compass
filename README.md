# Creator Compass - Installation and Testing Guide

An AI-powered micro-content coaching platform that helps content creators discover trending topics, generate platform-optimised video ideas, and predict engagement through explainable artificial intelligence (SHAP).

---

## Important Notice for Markers

**Creator Compass requires paid API access to run the full application.** However, you have two options to evaluate the project:

1. **Watch the Demo Video** — Shows the complete working application with all three modules in action (submitted separately)
2. **Run Automated Tests** — Test all functionality without API keys: `pytest tests/ -v` (24 tests, all passing)

**Skip the API setup** unless you want to interact with the live application directly.

---

## Product Package Contents

```
creator-compass/
├── README.md                          # Installation & testing guide
├── requirements.txt                   # Python dependencies (17 packages)
├── .env.example                       # Template for API keys
│
├── app/                               # Streamlit frontend application
│   ├── main.py                        # Dashboard entry point (session state, navigation)
│   ├── pages/
│   │   ├── Trend_Discovery.py         # M1: Trend analysis (325 lines)
│   │   ├── Content_Ideation.py        # M2: Content generation (371 lines)
│   │   └── Engagement_Optimiser.py    # M3: Engagement prediction + SHAP
│   ├── auth/
│   │   └── authenticator.py           # Login/registration with bcrypt hashing
│   ├── database/
│   │   └── db_manager.py              # SQLite operations
│   └── utils/
│       ├── model_loader.py            # ML model loading & 39-feature engineering
│       ├── explainer.py               # SHAP-based explainability
│       └── theme.py                   # Streamlit UI styling
│
├── src/                               # Backend logic (API integration, pipelines)
│   ├── data/
│   │   ├── fetch_twitter_apify.py     # Apify API for Twitter trends
│   │   ├── niche_config.py            # 13 content categories for filtering
│   │   └── feature_engineering.py     # Feature extraction & transformation
│   ├── pipelines/
│   │   ├── content_ideation.py        # GPT-4o-mini integration (383 lines)
│   │   └── nlp_processor.py           # NLP (sentiment, keywords, hashtags)
│   └── utils/
│       └── helpers.py                 # Utility functions
│
├── data/                              # Training data & models
│   ├── raw/
│   │   ├── instagram/                 # Instagram posts (30,000 posts, 38.4%)
│   │   ├── tiktok/                    # TikTok posts (28,800 posts, 36.9%)
│   │   └── youtube/                   # YouTube Shorts (19,200 posts, 24.6%)
│   ├── processed/
│   │   ├── combined_training.csv      # 78,077 posts × 39 features
│   │   └── tiktok_training.csv        # TikTok-specific subset
│   └── examples/
│       ├── trends.csv & trends.json   # Sample API responses
│
├── models/
│   └── engagement_model_random_forest.joblib    # RF model (R²=0.41)
│
├── tests/                             # Automated test suite
│   ├── test_objectives.py             # 24 pytest tests
│   └── results/                       # Benchmark outputs
│
├── notebooks/                         # Jupyter notebooks
│   ├── eda/                           # Data exploration
│   ├── modelling/                     # Model training (modelling_v1.ipynb)
│   └── xai/                           # SHAP explainability demos
│
├── docs/                              # Project documentation
│   ├── PDD.md                         # Product Design Document
│   ├── Analysis/                      # Requirements & Use Cases
│   └── Design/                        # UI-UX wireframes
│
└── verify_app.py                      # Pre-submission verification script
```

---

## System Requirements

### Prerequisites

**Required Software:**

- **Python**: 3.11+ (tested on 3.12.4)
- **pip**: Python package manager (included with Python)
- **ffmpeg/ffprobe**: For video duration detection

**Supported Operating Systems:**

- macOS 10.14+
- Linux (Ubuntu 18.04+, Debian, Fedora)
- Windows 10+ (WSL2 recommended) or native

**Hardware:**

- Minimum: 4GB RAM, 500MB free disk
- Recommended: 8GB RAM for smooth operation

### Verify Python Installation

```bash
# Check Python version (should be 3.11+)
python3 --version

# Check pip version
pip --version

# Verify openssl (for bcrypt)
python3 -c "import ssl; print('SSL available')"
```

### Install FFmpeg/FFprobe

**macOS:**

```bash
brew install ffmpeg
ffprobe -version  # Verify installation
```

**Ubuntu/Debian Linux:**

```bash
sudo apt update
sudo apt install ffmpeg
ffprobe -version
```

**Windows (WSL2):**

```bash
sudo apt update && sudo apt install ffmpeg
```

---

## Testing Without API Keys

This is the **recommended approach** for markers. Requires **no API key setup** and verifies all functionality through automated tests.

### 1. Extract Repository

```bash
# Extract the project folder
cd creator-compass
pwd  # Confirm you're in project root directory
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate      # macOS/Linux
# OR on Windows:
# .venv\Scripts\activate

# Verify activation (your prompt should show (.venv))
which python
```

### 3. Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements from file
pip install -r requirements.txt

```

### 4. Run Automated Tests

```bash
# Run all 24 tests
pytest tests/test_objectives.py -v

```

### What Gets Tested (24 Tests Total):

**Authentication (6 tests)**

- User registration with valid credentials
- Duplicate username prevention
- Login with correct/incorrect passwords
- User data isolation

**M1 - Trend Discovery (3 tests)**

- Trend data structure validation
- Niche categorization (13 categories: Tech, Fashion, Finance, Health, Food, Travel, Entertainment, Business, Lifestyle, Celebrities, Sports, Politics, Faith)
- Engagement score range validation (7.0-9.5 scale)

**M2 - Content Ideation (3 tests)**

- Idea JSON structure verification (11 fields: title, hook, angle, etc.)
- Platform-specific content generation (TikTok, Instagram, YouTube)
- Category alignment checking

**M3 - Engagement Optimiser (4 tests)**

- Random Forest model loading (R² = 0.41)
- Prediction output format & valid range (0-100 score)
- 39-feature engineering pipeline
- Database persistence of predictions

**SHAP Explainability (3 tests)**

- SHAP TreeExplainer initialization
- Feature attribution explanation structure
- Feature importance ranking (top 5 drivers)

**UI Integration (4 tests)**

- Trend saving & retrieval
- Idea persistence across sessions
- Prediction history tracking
- Multi-page data isolation

**End-to-End Workflow (1 test)**

- Complete user journey: Register → Find Trend → Generate Idea → Predict Engagement

---

## Full Installation

Only choose this path if you want to run the **live Streamlit application** with real API integration.

### Step 1: Install Dependencies

Follow steps 1-3 from above:

1. Extract repository
2. Create virtual environment (`.venv`)
3. Install dependencies (`pip install -r requirements.txt`)

### Step 2: Obtain API Keys

#### **Apify API Key** (for Twitter trend scraping)

1. Visit: https://apify.com
2. Click "Sign Up" → Create free account ($5 monthly credit)
3. Log in to dashboard
4. Navigate to: Settings → Integrations → API tokens
5. Create new token or copy existing token
6. **Cost**: Free tier: $5/month
   **What it's used for:**

- Fetching ~50 trending topics from Twitter/X (US)
- Extracting top 50-100 tweets per trend for NLP analysis
- Categorizing trends into 13 content niches

#### **OpenAI API Key** (for content generation)

1. Visit: https://platform.openai.com/account/api-keys
2. Click "Create new secret key"
3. Copy key (save securely - not shown again!)
4. **Cost Structure**: Pay-as-you-go; average $1-5 per testing session

**What it's used for:**

- Generate creative video ideas tailored to specific platforms
- Platform-specific optimisation (TikTok hooks, Instagram aesthetics, YouTube CTAs)
- Full script generation (5-8 shots with timing, dialogue, editing notes)

### Step 3: Configure API Keys

```bash
# Copy template to create .env file
cp .env.example .env

# Edit .env and add your keys
nano .env  # Or use your preferred editor
```

**Update `.env` file with:**

```
# Required API Keys
APIFY_API_TOKEN=your_apify_token_here
OPENAI_API_KEY=your_openai_api_key_here

```

### Step 4: Verify API Access

```bash
# Test Apify connection
python -c "
from apify_client import ApifyClient
import os
token = os.getenv('APIFY_API_TOKEN')
if token:
    try:
        client = ApifyClient(token)
        print(' Apify API connection successful')
    except Exception as e:
        print(f' Apify API error: {e}')
else:
    print(' APIFY_API_TOKEN not found in .env')
"

# Test OpenAI connection
python -c "
from openai import OpenAI
import os
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    try:
        client = OpenAI(api_key=api_key)
        print('✓ OpenAI API connection successful')
    except Exception as e:
        print(f'✗ OpenAI API error: {e}')
else:
    print('✗ OPENAI_API_KEY not found in .env')
"
```

### Step 5: Run Application

```bash
# Start Streamlit server
streamlit run app/main.py

# Expected output:
# You can now view your Streamlit app in your browser.
# URL: http://localhost:8501
```

**The app will automatically open at:** http://localhost:8501

### Step 6: First-Time Login

1. Click **"Sign Up"** on the login page
2. Create account:
   - Username: (any username)
   - Email: (any email)
   - Password: Any password (8+ characters)
3. Click **"Register"**
4. Login with credentials
5. You're now in the **Main Dashboard**

---

## Example Workflow (2-3 minutes with API keys)

### Module 1: Trend Discovery (45-60 seconds)

**Stage 1 - Quick Browse Trends:**

1. Click "Discover Trends" from dashboard
2. Select niche: **"Entertainment/Media"**
3. Set number of trends: **10**
4. Click **"Get Trending Topics"**

**Stage 2 - Deep Analysis:**

1. Select 3-5 trends from table (multi-select)
2. Click **"Analyse Selected Trends"**

3. Review analysis in expandable cards
4. Click **"Save Trend"** to store for later
5. Click **"Use for Content Ideas"** → Goes to Module 2

### Module 2: Content Ideation (30-45 seconds)

1. **Pre-filled with trend** (from Module 1), or manually select trend
2. Choose **Platform**: TikTok, Instagram Reels, or YouTube Shorts
3. Set **Variations**: 1-5 ideas (default: 3)
4. Click **"Generate Ideas"**
5. Review idea cards
6. Click **" Generate Full Script"** to see shot-by-shot breakdown
7. Click **" Optimise Engagement"** → Goes to Module 3
8. Click **" Save Idea"** to store in history

### Module 3: Engagement Optimiser (5-10 seconds)

1. **Form pre-filled** from Module 2 (or manual entry):
2. Click **"Predict Engagement Score"**
3. Click **" View Optimisation Tips"** to see SHAP explanations
4. Click **"Save Prediction"** to history



## Technical Details

### Technology Stack

- **Frontend**: Streamlit 1.28+ — Web dashboard UI (3 modules)
- **Backend**: Python 3.12 — Core logic, API integration
- **Database**: SQLite3 — User auth, saved trends/ideas
- **ML Model**: scikit-learn RF — Engagement prediction (39 features)
- **Explainability**: SHAP TreeExplainer — Feature attribution for predictions
- **External APIs**: Apify + OpenAI — Real-time data + content generation
- **NLP**: TextBlob + NLTK — Sentiment analysis, tokenization
- **Visualisation**: Plotly + Matplotlib — Interactive charts & reports

### Model Performance

- **Algorithm**: Random Forest Regressor (100 trees)
- **Training Data**: 78,077 social media posts (62,462 train, 15,615 test)
- **Features**: 39 engineered features (temporal, content, categorical)
- **R² Score**: 0.41 (explains 41% of engagement variance)
- **RMSE**: 0.0232 (±2.3% prediction error)
- **Cross-Validation**: 5-fold CV R² = 0.41 ± 0.01 (stable)

### Dataset Composition

- **Instagram**: 30,000 posts (38.4%) — 11 niches
- **TikTok**: 28,800 posts (36.9%) — 11 niches
- **YouTube Shorts**: 19,200 posts (24.6%) — 11 niches
- **Total**: 78,077 posts (100%) — 13 total categories

### 39 Features Engineering Pipeline

**Engineered features** from 23 raw variables:

- **Temporal** (6): posting_hour, posting_day, is_weekend, season (4 variants)
- **Content** (6): caption_length, hashtag_count, has_emoji, has_call_to_action, video_duration, media_type
- **Categorical** (19): platform (3) + content_category (14) + trend_label (4) + season (4)
- **Derived** (3): hour_bin (9 bins), caption_bin (5 bins), trending_interaction
- **Stats** (3): sentiment_score, keyword_diversity, engagement_history

---

## Markers Checklist

- [ ] Python 3.11+ installed
- [ ] Repository extracted
- [ ] Virtual environment created (`.venv`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Tests run successfully (`pytest tests/test_objectives.py -v` → 24/24 passed)
- [ ] (Optional) API keys configured and app runs (`streamlit run app/main.py`)

---
