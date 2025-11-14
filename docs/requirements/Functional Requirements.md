# Functional Requirements

| Version | Date | Author | Changes / Notes |
| --- | --- | --- | --- |
| 0.1 | 14-Nov-2025 | Sade Onitiri-Coker | Initial draft  |

## **1. Overview**

The purpose of this document is to detail the functional requirements for **Creator Compass**, an explainable content ideation system for short-form videos. These requirements focus on four key areas: trend detection, content idea generation, engagement optimisation, and explainable AI (XAI) outputs.

---

## **2. Functional Requirements**

### **2.1 Trend Detection**

**Objective:** Identify current content trends relevant to specific niches and regions using Natural Language Processing (NLP).

| Requirement | Description |
| --- | --- |
| Platforms | Twitter/X |
| Frequency | Daily updates of trending content |
| Filters | Niche, language, region, keywords |
| NLP Processing | Tokenisation, keyword extraction, sentiment analysis, and hashtag recognition |
| Output | Structured trend data (JSON/CSV) with metadata: trend title, URL, engagement metrics, timestamp |

---

### **2.2 Content Idea Generation**

**Objective:** Generate creative content suggestions based on trends and user preferences.

| Requirement | Description |
| --- | --- |
| Inputs | Trend data, historical engagement data, user-selected niche preferences |
| Outputs | Content suggestions including titles, hooks, scripts, shot-lists, hashtags, style/tone recommendations etc.  |
| Workflow | Automated generation pipeline → review interface → user selection |

---

### **2.3 Engagement Optimisation**

**Objective:** Predict and optimise content performance using historical data and metrics.

| Requirement | Description |
| --- | --- |
| Metrics | Likes, shares, comments, views |
| Optimisation Targets | Suggested captions, hashtags, keywords for maximum engagement |
| Feedback Loop | Model updates based on user-selected content performance |
| Output | Ranked suggestions based on predicted engagement score |

---

### **2.4 Explainable AI (XAI) Outputs**

**Objective:** Provide interpretable explanations for content suggestions and engagement predictions.

| Requirement | Description |
| --- | --- |
| Explainability Method | SHAP or LIME applied to prediction models |
| Visualisation | Charts, tables, or heat maps showing influential features |
| User Interpretation | Highlighted features and textual summaries to inform content decisions |
| Accessibility | Clear UI in Streamlit app, with hoverable tooltips or downloadable reports |

---

## **3. Additional Notes**

- Requirements are modular; each functional area can be developed independently and integrated incrementally.
- Future updates may include support for additional platforms, automated scheduling, and advanced analytics dashboards.