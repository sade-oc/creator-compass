# Non-Functional Requirements

## **1. Overview**

Non-functional requirements (NFRs) describe the **qualities and constraints** of the Creator Compass system. They complement functional and technical requirements and ensure the system is robust, maintainable, and user-friendly.

---

## **2. Performance**

| Requirement | Description |
| --- | --- |
| Response Time | Dashboard actions (charts, tables, content generation) should respond within 3–5 seconds for typical dataset sizes. |
| Scalability | Design should allow additional data sources and ML models to be added with minimal performance impact. |

---

## **3. Reliability & Availability**

| Requirement | Description |
| --- | --- |
| Uptime | App should be accessible >99% of the time during active use/testing periods. |
| Error Handling | All exceptions and failed data calls must be logged; the app should continue functioning gracefully. |
| Backup | Dataset and configuration files should be backed up regularly to prevent data loss. |

---

## **4. Security**

| Requirement | Description |
| --- | --- |
| Data Privacy | Ensure compliance with platform API policies and GDPR where applicable. |
| Credential Management | API keys and passwords stored securely (e.g., environment variables, `.env` file). |
| Access Control | Repository is private; app access restricted to the developer until MVP is ready. |

---

## **5. Maintainability**

| Requirement | Description |
| --- | --- |
| Code Organisation | Modular structure (`data/`, `models/`, `pipelines/`, `utils/`, `app/`) for readability and reusability. |
| Documentation | All code functions, classes, and modules should include comments and high-level decisions documented in `docs/`. |
| Testing | Unit tests for key functions and pipelines maintained in `tests/`. |

---

## **6. Usability**

| Requirement | Description |
| --- | --- |
| User Interface | Streamlit app should be intuitive; clearly labelled inputs, outputs, and explanations for XAI outputs. |
| User Guidance | Tooltips, help messages, and example workflows included in the dashboard. |
| Accessibility | Interface components readable on standard laptop screens; consider color contrast and chart clarity. |

---

## **7. Portability & Compatibility**

| Requirement | Description |
| --- | --- |
| Dependencies | All required Python libraries listed in `requirements.txt` or `environment.yml`. |
| Deployment | Local execution first; potential future deployment to cloud or shared server. |

---

## **8. Additional Notes**

- Non-functional requirements should guide design choices, especially for scalability, security, and usability.
- They should be revisited after initial prototypes to ensure alignment with real-world usage.

---