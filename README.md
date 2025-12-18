# Creator Compass

An AI-powered content creation platform that helps content creators discover trending topics, generate optimized content ideas, and understand engagement predictions through explainable AI.

## Features

- Trend Analysis- Discover trending topics across platforms and niches
- AI Content Generation - Generate personalized content ideas with engagement predictions
- Engagement Optimization - Get AI-powered suggestions to improve content performance
- Explainable AI - Understand why AI made specific recommendations
- User Profiling - Personalized recommendations based on creator preferences
- Optimal Scheduling - Find the best times to post for maximum engagement

## System Architecture

![System Architecture](docs/Analysis/Architechture/System%20Architecture%20Diagram.png)

_High-level architecture showing the 6 core AI services integrated with Streamlit frontend_

## Documentation

### Project Planning

- [Project Definition Document](docs/PDD.md) - Complete project overview and scope

### Analysis Phase

- [High-Level Architecture](docs/Analysis/Architechture/high_level_architecture.md)
- [Functional Requirements](docs/Analysis/requirements/Functional%20Requirements.md)
- [🔧 Technical Requirements](docs/Analysis/requirements/Technical%20Requirements.md)
- [Non-Functional Requirements](docs/Analysis/requirements/Non-Functional%20Requirements.md)
- [Use Cases](docs/Analysis/Use%20Cases/) - UC-01 through UC-07

### Design Phase

- [User Interface Design](docs/Design/UI-UX/) - Complete UI/UX specifications

## Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with FastAPI microservices
- **AI/ML**: scikit-learn, SHAP, LIME for explainable AI
- **Data**: CSV/JSON file storage, pandas for processing
- **APIs**: Twitter/X API for trend data
- **Deployment**: Docker containers, cloud hosting ready

## 🎯 Use Cases

Creator Compass supports 7 core use cases:

1. **UC-01**: Trend Discovery and Analysis
2. **UC-02**: AI-Powered Content Ideation
3. **UC-03**: Content Engagement Optimization
4. **UC-04**: Explainable AI Insights
5. **UC-05**: User Profile Management
6. **UC-06**: Content Performance Analytics
7. **UC-07**: Optimal Posting Schedule

## Run locally

To run the prototype locally (macOS / zsh):

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Launch the Streamlit app:

```bash
streamlit run app/main.py
```