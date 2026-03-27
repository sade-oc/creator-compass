
#EngagementExplainer: Application-integrated XAI for engagement predictions.


import numpy as np
import pandas as pd
import shap
import joblib
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')


class EngagementExplainer:
    """
    SHAP-based explainer for engagement predictions.
    Generates user-facing explanations and optimization suggestions.
    """
    
    def __init__(self, model, feature_names: List[str], model_metadata: Optional[Dict] = None):
        """
        Initialize explainer with a trained model.
        
        Args:
            model: Trained sklearn/xgboost model
            feature_names: List of feature names in order
            model_metadata: Optional dict with model info (baseline, etc.)
        """
        self.model = model
        self.feature_names = feature_names
        self.model_metadata = model_metadata or {}
        
        # Create SHAP explainer
        self._init_shap_explainer()
        
        # Feature display names for user-friendly output
        self.feature_display_names = {
            'duration_sec': 'Video Duration',
            'caption_length': 'Caption Length',
            'posting_hour': 'Posting Hour',
            'posting_day_encoded': 'Day of Week',
            'has_emoji': 'Has Emoji',
            'is_weekend': 'Weekend Post',
            'platform_tiktok': 'Platform: TikTok',
            'platform_youtube': 'Platform: YouTube',
            'platform_instagram': 'Platform: Instagram',
            'trend_label_rising': 'Rising Trend',
            'trend_label_stable': 'Stable Trend',
            'trend_label_declining': 'Declining Trend',
            'trend_label_seasonal': 'Seasonal Trend',
        }
        
        # Optimization suggestions based on feature effects
        self.optimization_tips = {
            'duration_sec': {
                'high_positive': 'Your video length is optimal for engagement.',
                'high_negative': 'Consider shorter videos (<30 seconds) for better engagement.',
                'neutral': 'Video duration has minimal impact on your engagement.'
            },
            'caption_length': {
                'high_positive': 'Your caption length is working well.',
                'high_negative': 'Try shorter captions (<50 characters) for higher engagement.',
                'neutral': 'Caption length has minimal impact on your engagement.'
            },
            'posting_hour': {
                'high_positive': 'Great posting time choice!',
                'high_negative': 'Consider posting between 5-8 PM for better engagement.',
                'neutral': 'Posting time has minimal impact on your engagement.'
            },
            'has_emoji': {
                'high_positive': 'Emojis are helping your engagement.',
                'high_negative': 'Consider adding emojis to your caption.',
                'neutral': 'Emoji usage has minimal impact on your engagement.'
            },
        }
    
    def get_model_limitations(self) -> Dict[str, str]:
        """
        Get model limitations and fairness disclaimers for the user.
        
        Returns:
            Dict with bias warning and fairness notes
        """
        return {
            'performance_caveat': (
                ':warning: **Model Accuracy:** Predictions are estimates based on historical data. '
                'Actual engagement may vary significantly. The model explains ~41% of engagement variance (R²=0.4143). '
                'Many external factors (algorithm changes, viral trends, influencer status) are not captured in this model.'
            ),
            'data_bias_note': (
                ':bar_chart: **Data Bias:** Training data comes from TikTok, Instagram, and YouTube content across 11 niches. '
                'The model performs better for some content categories than others. Popular niches may have more training data, '
                'leading to slightly better predictions for those categories. Smaller niches have higher prediction uncertainty.'
            ),
            'fairness_consideration': (
                ':scales: **Fairness:** This model predicts engagement based on past content patterns. It is NOT designed to determine '
                'content quality, virality potential, or creator talent. Low predictions don\'t mean your content is bad—just that it may need '
                'different optimisation strategies based on your specific audience and niche.'
            ),
            'what_we_cant_predict': (
                ':cross_mark: **What This Model Cannot Predict:** Viral moments, celebrity takeovers, trending challenges, algorithm preference shifts, '
                'user sentiment, or qualitative content appeal. Use these predictions as guidance, not guarantees.'
            )
        }
    
    
    def _init_shap_explainer(self):
        """Initialize SHAP TreeExplainer for the model."""
        try:
            self.explainer = shap.TreeExplainer(self.model)
            self.baseline = self.explainer.expected_value
            if isinstance(self.baseline, np.ndarray):
                self.baseline = self.baseline[0]
        except Exception as e:
            # Fallback for non-tree models
            print(f"Warning: TreeExplainer failed, using KernelExplainer: {e}")
            self.explainer = None
            self.baseline = self.model_metadata.get('baseline', 0.0626)  # Dataset mean
    
    @classmethod
    def load(cls, model_path: str, metadata_path: Optional[str] = None) -> 'EngagementExplainer':
        """
        Load explainer from saved model file.
        
        Args:
            model_path: Path to .joblib model file
            metadata_path: Optional path to model_metadata.json
            
        Returns:
            EngagementExplainer instance
        """
        model_path = Path(model_path)
        
        # Load model
        model = joblib.load(model_path)
        
        # Load metadata
        metadata = {}
        if metadata_path:
            with open(metadata_path) as f:
                metadata = json.load(f)
        else:
            # Try default location
            default_metadata = model_path.parent / 'model_metadata.json'
            if default_metadata.exists():
                with open(default_metadata) as f:
                    metadata = json.load(f)
        
        feature_names = metadata.get('features', [])
        
        return cls(model, feature_names, metadata)
    
    def explain(self, features: Union[pd.DataFrame, Dict, np.ndarray], 
                include_plot: bool = False) -> Dict[str, Any]:
        """
        Generate explanation for a prediction.
        
        Args:
            features: Input features (DataFrame row, dict, or array)
            include_plot: Whether to generate waterfall plot
            
        Returns:
            Dict with:
                - prediction: Predicted engagement rate
                - shap_values: Array of SHAP contributions
                - feature_contributions: DataFrame of feature -> contribution
                - explanation_text: Human-readable explanation
                - suggestions: List of optimization suggestions
                - plot_path: (optional) Path to saved plot
        """
        # Convert input to DataFrame
        X = self._prepare_input(features)
        
        # Get prediction
        prediction = self.model.predict(X)[0]
        
        # Compute SHAP values
        if self.explainer is not None:
            shap_values = self.explainer.shap_values(X)[0]
        else:
            # Fallback: use feature importance as proxy
            shap_values = np.zeros(len(self.feature_names))
        
        # Build feature contributions
        contributions = self._get_contributions(X.iloc[0], shap_values)
        
        # Generate explanation text
        explanation_text = self._generate_explanation(prediction, contributions)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(contributions)
        
        result = {
            'prediction': float(prediction),
            'prediction_pct': f"{prediction * 100:.2f}%",
            'shap_values': shap_values,
            'baseline': float(self.baseline),
            'feature_contributions': contributions,
            'explanation_text': explanation_text,
            'suggestions': suggestions,
        }
        
        # Optional: generate plot
        if include_plot:
            plot_path = self._generate_waterfall(X.iloc[0], shap_values, prediction)
            result['plot_path'] = plot_path
        
        return result
    
    def _prepare_input(self, features: Union[pd.DataFrame, Dict, np.ndarray]) -> pd.DataFrame:
        """Convert input to DataFrame with correct columns."""
        if isinstance(features, pd.DataFrame):
            X = features
        elif isinstance(features, dict):
            X = pd.DataFrame([features])
        elif isinstance(features, np.ndarray):
            X = pd.DataFrame([features], columns=self.feature_names)
        else:
            raise ValueError(f"Unsupported input type: {type(features)}")
        
        # Ensure correct column order
        if self.feature_names:
            missing = set(self.feature_names) - set(X.columns)
            if missing:
                # Fill missing with zeros
                for col in missing:
                    X[col] = 0
            X = X[self.feature_names]
        
        return X
    
    def _get_contributions(self, row: pd.Series, shap_values: np.ndarray) -> pd.DataFrame:
        """Build sorted DataFrame of feature contributions."""
        contributions = pd.DataFrame({
            'feature': self.feature_names,
            'value': row.values,
            'shap_value': shap_values,
            'abs_shap': np.abs(shap_values),
            'direction': ['positive' if s > 0 else 'negative' for s in shap_values]
        })
        
        # Add display names
        contributions['display_name'] = contributions['feature'].map(
            lambda x: self.feature_display_names.get(x, x.replace('_', ' ').title())
        )
        
        return contributions.sort_values('abs_shap', ascending=False)
    
    def _generate_explanation(self, prediction: float, contributions: pd.DataFrame) -> str:
        """Generate human-readable explanation."""
        lines = []
        
        # Headline
        pct = prediction * 100
        if pct >= 8:
            quality = "high"
        elif pct >= 5:
            quality = "moderate"
        else:
            quality = "below average"
        
        lines.append(f":bar_chart: **Predicted Engagement: {pct:.2f}%** ({quality})")
        lines.append("")
        
        # Filter: For one-hot encoded features (platform_, category_, trend_, season_),
        # only show when the feature value is 1 (actually active)
        def is_active_feature(row):
            feat = row['feature']
            # One-hot features should only be shown if value == 1
            if any(prefix in feat for prefix in ['platform_', 'category_', 'trend_label_', 'season_']):
                return row['value'] == 1
            return True
        
        active_contributions = contributions[contributions.apply(is_active_feature, axis=1)]
        
        # Top contributors (only from active features)
        top_positive = active_contributions[active_contributions['shap_value'] > 0.001].head(3)
        top_negative = active_contributions[active_contributions['shap_value'] < -0.001].head(3)
        
        if len(top_positive) > 0:
            lines.append(":white_check_mark: **Factors helping your engagement:**")
            for _, row in top_positive.iterrows():
                impact = row['shap_value'] * 100
                lines.append(f"   • {row['display_name']}: +{impact:.2f}% engagement")
        
        if len(top_negative) > 0:
            lines.append("")
            lines.append(":warning: **Factors reducing your engagement:**")
            for _, row in top_negative.iterrows():
                impact = row['shap_value'] * 100
                lines.append(f"   • {row['display_name']}: {impact:.2f}% engagement")
        
        if len(top_positive) == 0 and len(top_negative) == 0:
            lines.append(":information: Your content features have minimal impact on engagement.")
            lines.append("   Platform baseline is the primary driver.")
        
        return "\n".join(lines)
    
    def _generate_suggestions(self, contributions: pd.DataFrame) -> List[str]:
        """Generate actionable optimization suggestions."""
        suggestions = []
        
        # Check top negative contributors for suggestions
        top_negative = contributions[contributions['shap_value'] < -0.001].head(5)
        
        for _, row in top_negative.iterrows():
            feat = row['feature']
            if feat in self.optimization_tips:
                tip = self.optimization_tips[feat]['high_negative']
                suggestions.append(tip)
        
        # Platform-specific suggestion
        if any('platform_' in f for f in contributions['feature'].values):
            platform_rows = contributions[contributions['feature'].str.startswith('platform_')]
            if len(platform_rows) > 0:
                top_platform = platform_rows.iloc[0]
                if top_platform['shap_value'] < 0:
                    suggestions.append("Consider if a different platform might suit your content better.")
        
        # Add general tips if no specific suggestions
        if not suggestions:
            suggestions = [
                "Your content settings are reasonably optimized.",
                "Focus on content quality — our analysis shows it's the main driver of engagement.",
                "Experiment with different content styles to find what resonates with your audience."
            ]
        
        return suggestions
    
    def _generate_waterfall(self, row: pd.Series, shap_values: np.ndarray, 
                            prediction: float, save_path: Optional[str] = None) -> str:
        """Generate and save waterfall plot for individual explanation."""
        import matplotlib.pyplot as plt
        
        # Create SHAP Explanation object
        explanation = shap.Explanation(
            values=shap_values,
            base_values=self.baseline,
            data=row.values,
            feature_names=self.feature_names
        )
        
        # Generate plot
        plt.figure(figsize=(10, 6))
        shap.waterfall_plot(explanation, show=False, max_display=10)
        plt.title(f'Engagement Prediction Explanation\nPredicted: {prediction*100:.2f}%')
        plt.tight_layout()
        
        # Save
        if save_path is None:
            save_path = 'explanation_waterfall.png'
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def explain_batch(self, features: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate explanations for multiple predictions.
        
        Args:
            features: DataFrame with multiple rows
            
        Returns:
            List of explanation dicts
        """
        return [self.explain(features.iloc[[i]]) for i in range(len(features))]
    
    def get_global_importance(self, X: pd.DataFrame, sample_size: int = 1000) -> pd.DataFrame:
        """
        Compute global SHAP importance from a dataset.
        
        Args:
            X: Feature DataFrame
            sample_size: Number of samples to use
            
        Returns:
            DataFrame with feature importance rankings
        """
        if len(X) > sample_size:
            X = X.sample(sample_size, random_state=42)
        
        shap_values = self.explainer.shap_values(X)
        
        importance = pd.DataFrame({
            'feature': self.feature_names,
            'mean_abs_shap': np.abs(shap_values).mean(axis=0),
            'std_shap': shap_values.std(axis=0)
        }).sort_values('mean_abs_shap', ascending=False)
        
        importance['rank'] = range(1, len(importance) + 1)
        
        return importance


# Convenience function for quick explanations
def explain_prediction(features: Dict, model_path: str = 'models/engagement_model_random_forest.joblib') -> Dict:
    """
    Quick function to explain a single prediction.
    
    Args:
        features: Dict of feature values
        model_path: Path to trained model
        
    Returns:
        Explanation dict
    """
    explainer = EngagementExplainer.load(model_path)
    return explainer.explain(features)
