# Technical Requirements

## **1. Overview**

This document specifies the **technical requirements** needed to implement the Creator Compass system. It complements the functional requirements and focuses on the software architecture, technology stack, data pipelines, and integrations.

---

## **2. Backend Requirements**

| Requirement | Description |
| --- | --- |
| Programming Language | Python 3.10+ |
| Framework | FastAPI or Flask (for any APIs, optional for internal use) |
| ML/AI Libraries | Scikit-learn, pandas, numpy, matplotlib, seaborn, SHAP, LIME |
| Data Handling | Support for CSV, JSON, and API responses |
| Modularity | Clear separation of modules: `data`, `models`, `pipelines`, `utils` |
| Version Control | GitHub repository |

---

## **3. Frontend Requirements**

| Requirement | Description |
| --- | --- |
| UI Framework | Streamlit (main app + pages) |
| Pages | Main dashboard, trend analysis, content generation, engagement optimisation, XAI visualisation |
| Components | Interactive charts, tables, forms, buttons, downloadable reports |
| Responsiveness | Works on desktop and laptop screen sizes |
| Accessibility | Tooltips, labels, and hover explanations for XAI outputs |

---

## **4. Data Pipelines**

| Requirement | Description |
| --- | --- |
| Data Ingestion | Scripts to fetch data from external APIs (Twitter/X) and raw CSVs |
| Preprocessing | Cleaning missing or inconsistent data, normalising fields |
| Feature Engineering | Generate metrics such as engagement ratios, trend velocity, hashtag frequency |
| Dataset Storage | `data/raw/`, `data/processed/`, `data/examples/` folders |

---

## **5. API & Integration Requirements**

| Requirement | Description |
| --- | --- |
| API Access | Manage credentials securely; use environment variables or `.env` |
| Rate Limits | Respect platform limits; implement error handling and retries |
| Legal/Compliance | Ensure API usage aligns with platform terms of service and privacy regulations |
| Extensibility | Structure code to allow additional APIs or integrations in the future |

---

## **6. System Architecture & Design Considerations**

- **Modular Design:** Each module (`data`, `models`, `pipelines`, `utils`, `app`) is self-contained.
- **Reusability:** Helper functions and ML pipelines designed to be reused across different experiments.
- **XAI Integration:** All ML models should output SHAP or LIME explanations in a standardized format consumable by the Streamlit app.
- **Scalability:** Structure code so new features (e.g., new platforms, additional metrics) can be added without major refactoring.
- **Testing:** Include unit tests in the `tests/` folder for critical functions and pipelines.