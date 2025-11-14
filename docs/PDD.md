# PDD

### **Creator Compass – Cross-Platform Content Optimisation AI Tool**

**Author:** Sade Onitiri-Coker

**Email:** [sade.onitiri-coker@city.ac.uk](mailto:sade.onitiri-coker@city.ac.uk)

**Degree Programme:** BSc Computer Science

**Consultant:** Abigail Parisaca Vargas

**Project Proposed By:** Sade Onitiri-Coker

**Word Count:** 1672

**Proprietary Interests:** None (Not a client-based project)

**Promises Made to Secure Acceptance:** None

---

# **1. Proposal**

## **1.1 Problem to Be Solved**

In today’s digital society, content creation is increasingly competitive and deeply data-driven.

Short-form content platforms such as **TikTok, Instagram Reels, and YouTube Shorts** dominate the landscape and shape how creators achieve visibility and engagement (Manic, 2024).

Current solutions are limited because:

- Most tools rely on **retrospective analytics** (views, likes, shares).
- They offer **little insight** into *why* certain content performs better (Varga & Cucu, 2025).
- Many AI-powered optimisation tools act as **“black boxes”**, providing recommendations without transparency or explainability (Hase & Bansal, 2020).

As a result, creators rely heavily on intuition, copying trends, and trial-and-error content ideation.

### **Project Aim**

This project will develop an **AI-driven, explainable content ideation and optimisation system** that supports creators during the *pre-publication* stage by:

- Identifying emerging trends
- Generating content ideas
- Optimising user-provided or AI-generated ideas
- Providing **transparent, explainable recommendations**

### **Technical Approach**

The system will utilise:

- **NLP** for trend detection and semantic analysis
- **Deep learning** for engagement prediction
- **Explainable AI (XAI)** techniques such as SHAP and LIME to make predictions interpretable (Mosca et al., 2022)

The goal is to bridge the gap between complex AI models and practical creative decision-making, converting intuition-based workflows into **data-driven, explainable, adaptive processes**.

---

# **2. Project Objectives**

## **Main Objective**

To build an AI-driven, explainable system that assists creators in generating, refining, and understanding short-form video ideas based on real-time trends.

## **Sub-Objectives and Tests**

### **1) Trend Analysis**

**Objective:** Retrieve and analyse trending topics from Twitter (X) and open datasets using NLP.

**Test:** Verify successful data retrieval and identification of emerging niche-relevant topics.

### **2) AI Content Ideation**

**Objective:** Generate tailored short-form content ideas using NLP aligned with user-provided niches.

**Test:** Ensure generated ideas are coherent, relevant, and aligned with user intent.

### **3) Engagement Optimisation**

**Objective:** Recommend improvements (e.g., captions, keywords, hashtag selection).

**Test:** Confirm optimisation suggestions are produced per content idea.

### **4) Explainable AI Integration**

**Objective:** Apply SHAP and LIME to interpret predictions and recommendations.

**Test:** Explanations should correctly correspond to model outputs.

### **5) Unified User Interface**

**Objective:** Provide a user-friendly dashboard integrating all system modules.

**Test:** Verify smooth communication between frontend and backend.

## **Additional Enhancement Objectives**

### **6) User Profiling**

Adaptive recommendations based on historical user data

**Test:** Ensure user data is stored, retrieved, and influences future outputs.

### **7) Predictive Posting Scheduler**

Recommend optimal posting times using engagement patterns

**Test:** Validate posting time predictions against historical data.

---

# **3. Project Beneficiaries**

### **Content Creators & Influencers**

Gain transparent, actionable insights to improve content quality and engagement.

### **Digital Marketing Professionals**

Analyse engagement trends more effectively and justify strategic decisions.

### **XAI Researchers & Developers**

Study practical applications of explainability in social media prediction systems.

---

# **4. Project Work Plan**

### **Methodology:** Agile (Notion for sprint planning & tracking)

Project has **4 phases**, each with **3 two-week sprints**.

---

## **Phase 1: Environment Setup & Technology Exploration**

**Sprint 1–3: 13 Oct – 23 Nov 2025**

Activities:

- Finalise tech stack: FastAPI/Flask (backend), Streamlit (UI)
- Explore SHAP, LIME, TensorFlow/PyTorch
- Perform test API calls
- Build early preprocessing scripts

**Deliverable:** Development environment + initial test scripts

---

## **Phase 2: Data Collection & Preprocessing**

**Sprint 4–6: 24 Nov 2025 – 4 Jan 2026**

Activities:

- Collect trend and engagement datasets
- Build preprocessing and data pipelines
- Perform EDA
- Prepare datasets for trend analysis and prediction tasks

**Deliverable:** Cleaned datasets + preprocessing modules

---

## **Phase 3: Model Development & Explainability**

**Sprint 7–9: 5 Jan – 15 Feb 2026**

Activities:

- Develop predictive models
- Build trend-driven ideation models
- Integrate SHAP/LIME explainability
- Connect outputs across modules

**Deliverable:** Predictive model + trend ideation module + explanation engine

---

## **Phase 4: System Integration & Optimisation**

**Sprint 10–12: 16 Feb – 29 Mar 2026**

Activities:

- Integrate all modules (UI + backend + models + explainability)
- Conduct full system testing
- Final optimisation

**Deliverable:** Fully integrated and tested prototype + documentation

---

# **5. Risk Assessment**

| Risk | Description | Impact | Likelihood | Mitigation | Contingency |
| --- | --- | --- | --- | --- | --- |
| Learning curve | Difficulty with FastAPI, Streamlit, SHAP, DL/NLP libraries | High | High | Early exploration | Simplify architecture |
| Data quality & ethics | API limits, bias, poor data | High | Medium | Use verified, anonymised datasets | Use cached/synthetic data |
| Scope creep | Adding advanced features too early | High | Medium | Enforce MVP | Delay non-essential features |
| Model performance | SHAP/LIME may underperform | High | Medium | Validate baseline metrics | Use simpler models |
| Time management | Illness or overlapping deadlines | Medium | High | Add buffers | Defer tasks |
| Trend analysis noise | Low-quality topics | Medium | High | Filter using semantic scoring | Allow custom topics |
| Recommendation accuracy | Biased or ineffective suggestions | High | Medium | Continuous validation | Flag low-confidence outputs |

---

# **6. Legal, Social, Ethical & Professional Considerations**

### **Legal Compliance**

- Follows **UK GDPR** and **Data Protection Act 2018**
- Uses anonymised/public datasets
- Adheres to platform terms of service
- Secure storage of all collected data

### **Ethical Considerations**

- Ensures fairness, transparency, and explainability
- Uses SHAP & LIME for model interpretability
- Balanced datasets to minimise bias
- Clear advisory disclaimers

### **Social Impact**

- Empowers creators with data literacy
- Encourages responsible use of analytics
- Enhances digital creativity and opportunity

### **Professional Standards**

- Follows **BCS Code of Conduct (2022)**
- Transparent, reproducible development
- Ethical research protocols

---