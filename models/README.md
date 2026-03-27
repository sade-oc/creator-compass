# Engagement Prediction Model

**Status:** :white_check_mark: Production Ready  
**Model Type:** Logistic Regression  
**Training Date:** 2026-03-03  
**Last Updated:** 2026-03-06

---

## :bar_chart: Model Performance

### Test Set Results (Final Evaluation)

- **F1 Score:** 0.8751
- **ROC-AUC:** 0.8848
- **Precision:** 0.8507
- **Recall:** 0.9010
- **Accuracy:** 0.7992

### Generalization

- Performance drop from validation: 0.0067 (Excellent ✓)
- Model generalizes well to unseen data

---

## :dart: Core Hypothesis Validation

**Hypothesis:** Trend-aligned content significantly increases engagement probability

**Result:** :white_check_mark: **VALIDATED**

- Trend impact: **45.9% improvement** in predicted engagement
- Statistical significance: **p < 0.001** (highly significant)
- Effect size: **Cohen's d = 1.4339** (large effect)
- SHAP ranking: has_trend is **#1/22 features**

---

## 🔧 Quick Start

### Loading the Model

```python
import joblib
import pandas as pd

# Load model
model = joblib.load('models/engagement_model_logistic_regression.pkl')

# Load configuration
import json
with open('models/model_config.json', 'r') as f:
    config = json.load(f)

# Prepare your data (must have all 22 features)
# features = config['features']['names']
# X = your_data[features]

# Make predictions
predictions = model.predict_proba(X)[:, 1]  # Probability of high engagement
binary_predictions = model.predict(X)  # 0 = Low, 1 = High
```

### Required Features (in order)

```python
[
  "has_trend",
  "trend_rising",
  "trend_seasonal",
  "trend_stable",
  "trend_declining",
  "posting_hour",
  "posting_day",
  "posting_month",
  "is_peak_hour",
  "is_weekend",
  "is_evening",
  "caption_length",
  "hashtag_count",
  "duration_sec",
  "optimal_hashtag_range",
  "has_optimal_caption",
  "has_short_caption",
  "has_long_caption",
  "platform_tiktok",
  "platform_instagram",
  "platform_youtube",
  "category_encoded"
]
```

---

## :chart_increasing: Top 5 Most Important Features (SHAP)

1. **has_trend** - Mean |SHAP|: 1.6339
2. **trend_declining** - Mean |SHAP|: 1.2416
3. **trend_stable** - Mean |SHAP|: 1.1048
4. **platform_youtube** - Mean |SHAP|: 0.6697
5. **platform_tiktok** - Mean |SHAP|: 0.5348

---

## 📦 Saved Artifacts

| File                                       | Description              | Size    |
| ------------------------------------------ | ------------------------ | ------- |
| `engagement_model_logistic_regression.pkl` | Trained model            | 0.00 MB |
| `shap_explainer.pkl`                       | SHAP explainer           | 0.04 MB |
| `model_config.json`                        | Configuration & metadata | -       |
| `model_comparison_results.json`            | Model selection results  | -       |
| `feature_importance_best_model.csv`        | Feature rankings         | -       |

### Figures & Visualizations

All figures saved in `docs/figures/`:

- `shap_importance_bar.png` - Global feature importance
- `shap_summary.png` - SHAP beeswarm plot
- `shap_dependence_*.png` - Feature dependence plots
- `lime_sample_*.png` - Instance explanations
- `trend_impact_validation.png` - Hypothesis validation
- `optimal_posting_times_heatmap.png` - Posting recommendations
- `test_confusion_matrix.png` - Test set confusion matrix
- `test_calibration_curve.png` - Model calibration

---

## :rocket: Use Cases

### UC-02: Content Ideation

Generate content recommendations with engagement predictions:

```python
# Predict engagement for proposed content ideas
ideas_df = pd.DataFrame([...])  # Your content ideas
engagement_scores = model.predict_proba(ideas_df)[:, 1]
top_ideas = ideas_df.iloc[engagement_scores.argsort()[-5:]]  # Top 5
```

### UC-04: Explainable Predictions

Explain why specific content is predicted to perform well:

```python
import shap
explainer = joblib.load('models/shap_explainer.pkl')
shap_values = explainer.shap_values(X_sample)
shap.force_plot(explainer.expected_value, shap_values[0], X_sample.iloc[0])
```

### UC-06: Optimal Posting Times

Load posting recommendations:

```python
with open('docs/figures/optimal_posting_times.json', 'r') as f:
    posting_times = json.load(f)

# Get best times for TikTok
best_hours = posting_times['recommendations']['tiktok']['top_5_hours']
```

---

## :warning: Known Limitations

1. **Calibration:** Model calibration error is 0.1475 (acceptable for ranking, but precise probabilities may need recalibration)
2. **Posting Times:** Model suggests late-night posting (21:00-01:00) due to has_trend dominance; consider stratified recommendations
3. **Data Coverage:** Model trained on 25K samples from TikTok, Instagram, YouTube (2026 data)

---

## 📚 Documentation

- **Notebook:** `notebooks/modelling/engagement_prediction_model.ipynb`
- **Project Design:** `docs/PDD.md`
- **Use Cases:** `docs/Analysis/Use Cases/`

---

## 🔄 Model Version History

- **v1.0** (2026-03-06): Initial production model
  - Algorithm: Logistic Regression
  - Test F1: 0.8751
  - Hypothesis: :white_check_mark: Validated

---

**Contact:** Creator Compass Team  
**License:** Internal Use Only
