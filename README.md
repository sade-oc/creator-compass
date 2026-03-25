# Creator Compass

**An AI-powered micro-content coaching platform** that helps content creators discover trending topics, generate optimised video ideas, and predict engagement through explainable AI.

## Project Overview

Creator Compass is a **proof-of-concept MVP** demonstrating an integrated AI system for content creation workflow optimisation. The platform integrates three core modules (M1, M2, M3) into a unified Streamlit interface:

- **M1 (Trend Discovery)**: Identifies trending topics via Apify API and analyses them using NLP
- **M2 (Content Ideation)**: Generates platform-specific video ideas using GPT-4o-mini
- **M3 (Engagement Optimiser)**: Predicts engagement potential using machine learning with explainable AI (SHAP)

**Target Users**: Content creators (TikTok, Instagram Reels, YouTube Shorts) seeking data-driven content strategy

**Dataset**: 78,077 social media posts (Instagram 38.4%, TikTok 36.9%, YouTube 24.6%) with 39 engineered features

---

## System Architecture

**Technology Stack:**

- **Frontend**: Streamlit (single-framework MVP architecture)
- **Backend**: Python (FastAPI-ready, currently file-based)
- **AI/ML**: scikit-learn (Random Forest), SHAP (explainability), LIME, textblob (NLP)
- **Data**: SQLite (user data), CSV/JSON (trend data, models)
- **APIs**: Apify (Twitter trends), OpenAI (GPT-4o-mini for content generation)
- **Authentication**: Custom session-based with bcrypt password hashing
- **Visualisation**: Plotly, matplotlib, Streamlit native components

**Key Design Decision**: Single-framework Streamlit architecture prioritises functional completeness over production polish—appropriate for academic proof-of-concept validation.

---

## Prerequisites & Requirements

### System Requirements

- **OS**: macOS, Linux, or Windows (with WSL)
- **Python**: 3.11+ (tested on 3.11.x)
- **Memory**: 4GB minimum (8GB recommended)
- **Internet**: Required for API calls (Apify, OpenAI)

### Required API Keys

Before setup, obtain:

1. **APIFY_API_TOKEN** — For Twitter/X trend data
   - Sign up: https://apify.com
   - Create data collection task
   - API token in dashboard

2. **OPENAI_API_KEY** — For GPT-4o-mini content generation
   - Sign up: https://platform.openai.com
   - Create API key in account settings
   - Requires paid account (estimate: $1-5 per test session)

### System Dependencies

- ffprobe (for video duration detection)
  - **macOS**: `brew install ffmpeg` (includes ffprobe)
  - **Linux**: `sudo apt install ffmpeg`
  - **Windows**: Download from https://ffmpeg.org/download.html

---

## Setup Instructions

### Step 1: Clone/Extract Repository

```bash
cd path/to/creator-compass
pwd  # Verify you're in the project root
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# OR: .venv\Scripts\activate  # Windows

# Verify activation (should show .venv in prompt)
which python
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify installation
python -c "import streamlit; import sklearn; print('✓ Dependencies OK')"
```

### Step 4: Configure Environment Variables

Create `.env` file in project root (or update existing):

```bash
# Required API Keys
APIFY_API_TOKEN=your_apify_token_here
OPENAI_API_KEY=your_openai_key_here

# Optional: Database
DATABASE_PATH=data/creator_compass.db  # Auto-created if missing

# Optional: Logging
LOG_LEVEL=INFO
```

**Security Note**: `.env` is in `.gitignore` — never commit API keys to version control.

### Step 5: Initialize Database

```bash
# Database auto-initializes on first app run, but you can pre-initialize:
python -c "from src.database.db_manager import init_db; init_db(); print('✓ Database initialized')"
```

### Step 6: Verify Installation

```bash
# Test imports
python -c "
from app.auth.authenticator import register_user
from src.pipelines.content_ideation import generate_content_ideas
from src.pipelines.nlp_processor import process_trend_nlp
print('✓ All modules importable')
"
```

---

## Running the Application

### Start the Streamlit Server

```bash
streamlit run app/main.py
```

**Expected Output:**

```
  You can now view your Streamlit app in your browser.

  URL: http://localhost:8501
```

The app opens automatically in your default browser at `http://localhost:8501`

### First-Time Login

1. **Create Account**: Click "Sign Up" on login page
   - Username: e.g., "test_creator"
   - Email: any email
   - Password: any password (min 8 chars)

2. **Verify Database**: Account saves to `data/creator_compass.db`

### Navigate the Interface

**Main Dashboard** (after login):

- Shows personalised stats (trends saved, ideas generated, predictions made)
- Three main buttons: "Discover Trends", "Generate Ideas", "Optimise Engagement"

**Module Navigation**:

- Sidebar shows current user + mini-stats + logout
- `st.switch_page()` enables seamless M1→M2→M3 transitions
- Data pre-fills across modules via session state

---

## Testing the System

### Automated Tests (pytest)

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test class
pytest tests/test_objectives.py::TestAuthentication -v

# Run with coverage
pip install pytest-cov
pytest tests/ --cov=app --cov=src --cov-report=html
```

**Test Coverage**:

- ✅ Authentication (user registration, login, password validation)
- ✅ Database operations (save/retrieve trends, ideas, predictions)
- ✅ M1 pipeline (trend fetching, NLP categorization)
- ✅ M2 pipeline (content idea generation, validation)
- ✅ M3 pipeline (engagement prediction, SHAP explanations)

**Test Results Location**: `tests/results/`

- `PERFORMANCE_BENCHMARK_RESULTS.csv` — M1/M2/E2E timings (5 runs each)
- `m2_quality_assessment_BLANK.csv` — M2 idea quality scores
- `TREND_CATEGORISATION_REVIEW.csv` — M1 categorization accuracy
- `hypothesis_results_comprehensive.json` — Statistical validation of H1-H5

### Manual Testing Workflows

#### Workflow 1: M1 Trend Discovery (2 minutes)

1. **Start app** → Login → Click "📈 Discover Trends"

2. **Stage 1 - Quick Preview** (8-15s):
   - Select niche: "Tech/Gaming"
   - Set trends: 10-20
   - Click "Get Trending Topics"
   - Expected: Table of 10-20 trends with names, scores, niches

3. **Stage 2 - Deep Analysis** (1-2 min for 3-5 trends):
   - Multi-select 3-5 trends from table
   - Click "Analyse Selected Trends"
   - **Warning**: May take 1-5 min (Apify API + NLP processing)
   - Expected: Expandable cards showing:
     - Keywords (top 10)
     - Sentiment (positive/neutral/negative %)
     - Recommended hashtags
     - Save button for persistence

4. **Verify**:
   - Save a trend by clicking "💾 Save Trend"
   - Dashboard should update "Saved Trends" count
   - Navigate away and back — trend should persist

#### Workflow 2: M2 Content Ideation (1 minute)

1. **Start from M1 Trend**: Click "Use for Content Ideas" on analysed trend
   - Should auto-navigate to M2 with trend pre-filled

2. **Or start from M2 directly**: Click "🎬 Generate Ideas"
   - If no trends analysed, shows warning with link to M1
   - Select analysed trend from sidebar dropdown

3. **Configure idea generation**:
   - Platform: Select "TikTok", "Instagram Reels", or "YouTube Shorts"
   - Variations: Slider 1-5 (default: 3)
   - Click "🎬 Generate Ideas"

4. **Expected output** (17.8s ± 1.5s):
   - 3 expandable idea cards with:
     - **11-field structure**: title, hook, angle, description, visual_style, duration, suggested_shots, caption, hashtags, estimated_engagement, engagement_reasoning
     - Metadata row: Engagement level, duration, visual style
     - Expansion reveals full details
     - Buttons: "Generate Full Script", "📊 Optimise Engagement", "💾 Save Idea"

5. **Generate Full Script** (optional):
   - Click button on any idea
   - **Expected**: Shot-by-shot breakdown (5-8 shots) with:
     - Timing (0:00-0:03)
     - Visual description
     - Dialogue/voiceover text
     - Text overlays
     - Camera notes
     - Transitions
     - Props needed
     - Editing notes

6. **Verify**:
   - Save idea → Dashboard "Content Ideas" count increments
   - "Optimise Engagement" → Auto-navigates to M3 with data pre-filled

#### Workflow 3: M3 Engagement Optimiser (30 seconds)

1. **Start from M2 Idea**: Click "📊 Optimise Engagement"
   - Form auto-fills: caption (hook + description), hashtags, platform, niche

2. **Or start from M3 directly**: Click "📊 Engagement Optimiser"
   - Manual form entry

3. **Form fields**:
   - Caption: Text area (shows character count feedback)
   - Hashtags: Comma-separated (shows count guidance, optimal 5-10)
   - Platform: Radio (TikTok/Instagram/YouTube)
   - Category: Dropdown (14 options)
   - Posting Hour: Slider 0-23 (peak hours 18-20 highlighted)
   - Posting Day: Selector Monday-Sunday
   - Duration: Number input (30s default) OR video upload for auto-detect
   - Video Upload: Optional MP4/MOV (uses ffprobe for duration extraction)
   - Trend Alignment: Checkbox + trend type selector (Rising/Seasonal/Stable/Declining)

4. **Run Prediction**:
   - Click "🔍 Analyse Engagement"
   - **Expected** (sub-1s):
     - Performance Score (0-100) with star rating
     - Engagement Rate (%) vs dataset average
     - Confidence Interval (±2.3pp)
     - Comparison metrics (4 columns)

5. **Explainability**:
   - SHAP waterfall: Top 5 feature contributions
   - Feature names: platform_tiktok, duration_sec, caption_length, posting_hour, etc.
   - Directional impact (green=positive, red=negative)
   - Recommendation cards: "Try posting at 7-9 PM for 38% more engagement"

6. **Verify**:
   - Save prediction → Dashboard "Predictions Made" increments
   - Prediction saved to user profile (visible after logout/login)

### Performance Validation

**Benchmark Targets** (from requirements):

- M1: <60s target → **Actual: 19.70s ± 1.35s** ✅ PASS
- M2: <15s target → **Actual: 17.83s ± 1.57s** ⚠️ FAIL (19% over)
- E2E: <90s target → **Actual: 37.53s ± 2.69s** ✅ PASS

**To Reproduce Benchmarks**:

```bash
python tests/benchmark_performance.py
# Generates: tests/results/PERFORMANCE_BENCHMARK_RESULTS.csv
```


## Key Features & Workflows

### Feature 1: Trend Discovery (M1)

- **Two-stage workflow**: Preview (8-15s) + Analysis (1-2 min)
- **11 niche categories**: Tech, Sports, Finance, Food, Travel, etc.
- **NLP features**: Keywords, hashtags, sentiment analysis
- **Output**: Categorised trends with metadata for downstream modules

**Performance**: 19.70s ± 1.35s (5 runs)

### Feature 2: AI Content Ideation (M2)

- **Platform optimization**: TikTok, Instagram Reels, YouTube Shorts
- **GPT-4o-mini generation**: 3-5 creative variations per trend
- **11-field output**: Title, hook, angle, description, visual style, duration, shots, caption, hashtags, engagement estimate, reasoning
- **Script generation**: Optional shot-by-shot breakdown with dialogue & timing

**Performance**: 17.83s ± 1.57s (5 runs idea gen), ~15-25s script gen (estimated)

### Feature 3: Engagement Prediction (M3)

- **Random Forest model**: R² = 0.4143 (explains 41.43% variance)
- **39 features**: Platform, duration, caption length, hashtags, posting time, trend alignment, etc.
- **SHAP explainability**: Top 5 feature contributions with directional impact
- **Confidence intervals**: ±2.3pp based on model MAE
- **Actionable recommendations**: Platform-specific optimization tips

**Performance**: <1 second (local model inference)

### Feature 4: User Persistence

- **SQLite database**: Per-user data isolation via foreign keys
- **Saved entities**: Trends, ideas, predictions with timestamps
- **Cross-session state**: Data persists across logouts/logins
- **Dashboard aggregation**: Stats for saved trends, ideas, average engagement

### Feature 5: Explainable AI

- **SHAP integration**: Waterfall plots showing feature importance
- **Human-readable explanations**: "Duration is most important feature (24.87% contribution)"
- **Directional insight**: Positive/negative impact of each feature
- **Feature context**: Model uses 39 features including temporal (hour/day/season), content (duration, hashtags), and platform (TikTok/Instagram/YouTube)

---

## Performance Characteristics

### Timing Benchmarks (5 runs, mean ± SD)

| Component                              | Time           | Target | Status             |
| -------------------------------------- | -------------- | ------ | ------------------ |
| M1 Stage 1 (Fetch Trends)              | 8-15s          | <60s   | ✅ Pass            |
| M1 Stage 2 (Deep Analysis, 3-5 trends) | 1-2 min        | <60s   | ⚠️ Marginal        |
| M1 Total (E2E)                         | 19.70s ± 1.35s | <60s   | ✅ Pass            |
| M2 Idea Generation                     | 17.83s ± 1.57s | <15s   | ⚠️ Fail (19% over) |
| M2 Script Generation                   | ~15-25s        | <30s   | ✅ Pass (est.)     |
| M3 Prediction (Local)                  | <1s            | N/A    | ✅ < 1ms           |
| E2E Workflow                           | 37.53s ± 2.69s | <90s   | ✅ Pass            |

**Notes**:

- M1 Stage 2 timing varies with trend complexity and Apify API response time
- M2 overage (19%) acceptable for MVP (Nielsen guideline: <20s maintains attention)
- M3 is instantly local (no API calls needed after model load)
- E2E includes only core operations (excludes user think time)

### Resource Usage

- **Memory**: ~200-400MB typical (500MB peak during SHAP generation)
- **API Costs**: ~$0.05-0.15 per full workflow (M1 free, M2 ~$0.05-0.10, M3 free)
- **Database Size**: ~2MB (SQLite) + ~100MB data assets
- **Model Size**: Engagement model pickle ~25MB + SHAP explainer ~30MB

### Scalability Constraints

- **Single-user**: No concurrency issues (MVP architecture)
- **Apify API**: Free tier rate limits ~5 req/min
- **OpenAI API**: Subject to tier-specific rate limits
- **Database**: SQLite suitable for <10k users; production would need PostgreSQL

---

## Troubleshooting

### Issue: "APIFY_API_TOKEN not found"

**Solution**:

```bash
# 1. Verify .env file exists in project root
ls -la .env

# 2. Check .env contents
cat .env | grep APIFY

# 3. If missing, add it
echo "APIFY_API_TOKEN=your_token_here" >> .env

# 4. Restart Streamlit
streamlit run app/main.py
```

### Issue: "OPENAI_API_KEY not found"

**Solution**: Same as above, but for OpenAI key. Verify key format starts with `sk-proj-`

### Issue: "ffprobe not found" (video duration auto-detection fails)

**Solution**:

```bash
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg

# Windows (download from https://ffmpeg.org/download.html)
# Then add to PATH

# Verify
ffprobe -version
```

### Issue: App crashes on "Analyse Engagement"

**Scenarios**:

1. **Missing model files**: Check `/models/` contains `.pkl` files
2. **Feature mismatch**: Input features don't match model expectations
3. **Invalid input**: Caption empty, hashtags malformed

**Debug**:

```bash
# Test model loading
python -c "from app.utils.model_loader import predict_engagement; print('Model OK')"

# Test direct prediction
python -c "
from app.utils.model_loader import predict_engagement
result = predict_engagement({
    'caption': 'test caption',
    'hashtags': ['#test'],
    'platform': 'TikTok',
    'posting_hour': 20,
    'posting_day': 'monday',
    'duration_sec': 45,
    'has_trend': 1,
    'trend_type': 'rising',
    'category': 'tech'
})
print(result)
"
```

### Issue: Database locked / User data not persisting

**Solution**:

```bash
# Kill any locked database connections
lsof | grep creator_compass.db

# Reset database (loses all user data)
rm data/creator_compass.db

# Restart app (auto-reinitializes)
streamlit run app/main.py
```

### Issue: Streamlit port 8501 already in use

**Solution**:

```bash
# Use different port
streamlit run app/main.py --server.port 8502

# Or kill existing process
lsof -i :8501
kill -9 <PID>
```

### Issue: M2 idea generation returns empty or low-quality ideas

**Likely causes**:

1. **Trend keywords low quality**: Use "Tech" niche for best results
2. **OpenAI model rate limited**: Wait 5min, retry
3. **Network timeout**: Check internet connectivity

**Solution**: Try different trend or retry after waiting

### Issue: M3 predictions unrealistic (80%+ engagement)

**Context**: Model trained on ~7.5% average engagement rate (realistic: 3-15%)

- Performance scores scale to 0-100 for UX (not actual percentages)
- Check "vs average" comparison for context
- SHAP breakdown shows which factors drove score

---

