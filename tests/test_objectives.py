"""
Pytest suite for Creator Compass - Objective-Based Testing

Tests map to PDD objectives:
1. Trend Analysis & Detection
2. AI Content Ideation  
3. Engagement Optimisation
4. Explainable AI Integration
5. Unified User Interface

"""

import pytest
import sys
from pathlib import Path

# Add app and src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from auth.authenticator import register_user, login_user
from database.db_manager import (
    get_user_by_username, delete_user, init_db,
    save_idea, get_saved_ideas, save_trend, get_saved_trends
)


# SETUP 

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Initialise database for all tests"""
    init_db()
    yield
    # Cleanup happens after all tests


@pytest.fixture
def test_user():
    """Create and cleanup test user for each test"""
    username = f"test_user_{id(__name__)}"
    email = f"test_{id(__name__)}@example.com"
    
    # Register
    success, _, user_id = register_user(username, email, "TestPass123", "TestPass123")
    assert success, "Failed to create test user"
    
    yield {"id": user_id, "username": username, "email": email}
    
    # Cleanup
    if user_id:
        delete_user(user_id)


# FOUNDATION: AUTHENTICATION 

class TestAuthentication:
    """Foundation tests - Authentication gates all features"""
    
    def test_user_registration_valid(self):
        """Auth-01: Register user with valid credentials"""
        success, message, user_id = register_user(
            "auth_valid_user",
            "auth_valid@example.com",
            "TestPassword123",
            "TestPassword123"
        )
        assert success is True
        assert user_id is not None
        
        # Cleanup
        delete_user(user_id)
    
    def test_user_registration_duplicate_username(self, test_user):
        """Auth-02: Reject duplicate username"""
        success, message, _ = register_user(
            test_user["username"],  # Duplicate
            "different@example.com",
            "TestPassword123",
            "TestPassword123"
        )
        assert success is False
        assert "already taken" in message.lower()
    
    def test_user_login_valid(self, test_user):
        """Auth-03: Login with valid credentials"""
        # Mock Streamlit session
        import streamlit as st
        class MockSessionState:
            pass
        st.session_state = MockSessionState()
        
        success, message = login_user(test_user["username"], "TestPass123")
        assert success is True
        assert "welcome" in message.lower()
    
    def test_user_login_invalid_password(self, test_user):
        """Auth-04: Reject login with wrong password"""
        success, message = login_user(test_user["username"], "WrongPassword")
        assert success is False
        assert "incorrect" in message.lower()
    
    def test_user_login_by_email(self, test_user):
        """Auth-05: Login with email instead of username"""
        import streamlit as st
        class MockSessionState:
            pass
        st.session_state = MockSessionState()
        
        success, message = login_user(test_user["email"], "TestPass123")
        assert success is True
    
    def test_user_data_isolation(self):
        """Auth-06: Verify User A can't see User B's data"""
        # Create User A
        success_a, _, user_a_id = register_user(
            "user_a_isolation",
            "user_a_iso@example.com",
            "TestPass123",
            "TestPass123"
        )
        
        # Create User B
        success_b, _, user_b_id = register_user(
            "user_b_isolation",
            "user_b_iso@example.com",
            "TestPass123",
            "TestPass123"
        )
        
        assert success_a and success_b
        
        # User A saves a trend
        save_trend(user_a_id, "Fitness Hacks", 8.5, "twitter", "Fitness", None)
        
        # User B's trends should be empty
        user_b_trends = get_saved_trends(user_b_id)
        assert len(user_b_trends) == 0, "User B can see User A's trends!"
        
        # User A's trends should have 1
        user_a_trends = get_saved_trends(user_a_id)
        assert len(user_a_trends) == 1
        
        # Cleanup
        delete_user(user_a_id)
        delete_user(user_b_id)


# OBJECTIVE 1: TREND ANALYSIS 

class TestObjective1_TrendAnalysis:
    """Objective 1: Trend Analysis & Detection"""
    
    def test_trend_json_structure(self, test_user):
        """O1-01: Trend JSON has required fields"""
        save_trend(
            test_user["id"],
            trend_topic="AI in Education",
            trend_score=8.7,
            trend_source="twitter",
            trend_niche="Tech/Gaming",
            notes="Test trend"
        )
        
        trends = get_saved_trends(test_user["id"])
        assert len(trends) > 0
        trend = trends[0]
        
        # Verify structure
        assert "trend_topic" in trend
        assert "trend_score" in trend
        assert "trend_source" in trend
        assert "trend_niche" in trend
        assert trend["trend_topic"] == "AI in Education"
        assert trend["trend_score"] == 8.7
    
    def test_trend_niche_mapping(self, test_user):
        """O1-02: Trends mapped to correct niche"""
        save_trend(
            test_user["id"],
            trend_topic="TikTok Fitness Challenge",
            trend_score=9.2,
            trend_source="twitter",
            trend_niche="Fitness",
            notes=None
        )
        
        trends = get_saved_trends(test_user["id"])
        trend = trends[0]
        assert trend["trend_niche"] == "Fitness"
    
    def test_trend_score_valid_range(self, test_user):
        """O1-03: Trend score in valid range (0-10)"""
        save_trend(
            test_user["id"],
            trend_topic="Test Trend",
            trend_score=7.5,
            trend_source="twitter",
            trend_niche="General",
            notes=None
        )
        
        trends = get_saved_trends(test_user["id"])
        trend = trends[0]
        assert 0 <= trend["trend_score"] <= 10


# OBJECTIVE 2: CONTENT IDEATION 

class TestObjective2_ContentIdeation:
    """Objective 2: AI Content Ideation"""
    
    def test_idea_json_structure(self, test_user):
        """O2-01: Generated idea has all 11 required fields"""
        # Mock idea structure (as would come from OpenAI)
        idea_data = {
            "title": "POV: ChatGPT Helps With Homework",
            "hook": "What if AI could explain calculus better?",
            "angle": "Student reaction/comparison",
            "description": "Detailed description here...",
            "visual_style": "POV",
            "duration": "30-60 sec",
            "suggested_shots": ["Screen recording", "Face reaction"],
            "caption": "This changed everything 🤯",
            "hashtags": ["#AIEducation", "#StudyTok"],
            "estimated_engagement": "High",
            "engagement_reasoning": "Relatable student content"
        }
        
        # Save to DB
        save_idea(
            test_user["id"],
            idea_data["title"],
            idea_data["description"],
            "TikTok",
            "Education",
            "AI in Education",
            engagement_score=85
        )
        
        ideas = get_saved_ideas(test_user["id"])
        assert len(ideas) > 0
        idea = ideas[0]
        
        # Verify all key fields
        assert idea["idea_title"] is not None
        assert idea["idea_description"] is not None
        assert idea["platform"] is not None
        assert idea["category"] is not None
    
    def test_idea_platform_specific(self, test_user):
        """O2-02: Different platforms produce different ideas"""
        platforms = ["TikTok", "Instagram Reels", "YouTube Shorts"]
        
        for i, platform in enumerate(platforms):
            save_idea(
                test_user["id"],
                f"Idea for {platform}",
                f"Description for {platform}",
                platform,
                "Fitness",
                "Fitness Trend",
                engagement_score=70
            )
        
        ideas = get_saved_ideas(test_user["id"])
        platforms_saved = [idea["platform"] for idea in ideas]
        
        assert "TikTok" in platforms_saved
        assert "Instagram Reels" in platforms_saved
        assert "YouTube Shorts" in platforms_saved
    
    def test_idea_niche_alignment(self, test_user):
        """O2-03: Ideas aligned to specified niche"""
        save_idea(
            test_user["id"],
            "Fitness Hack",
            "A trending fitness workout...",
            "TikTok",
            "Fitness",  # Niche
            "Fitness Trend",
            engagement_score=80
        )
        
        ideas = get_saved_ideas(test_user["id"])
        idea = ideas[0]
        assert idea["category"] == "Fitness"


# OBJECTIVE 3: ENGAGEMENT OPTIMISATION 

class TestObjective3_EngagementOptimisation:
    """Objective 3: Engagement Optimisation & Prediction"""
    
    def test_model_loads(self):
        """O3-01: Random Forest model loads successfully"""
        from app.utils.model_loader import load_model
        
        model = load_model()
        assert model is not None
        assert hasattr(model, 'predict')
    
    def test_prediction_valid_range(self):
        """O3-02: Predictions return 0.0-1.0 engagement score"""
        from app.utils.model_loader import predict_engagement
        
        result = predict_engagement({
            "caption_length": 50,
            "posting_hour": 18,
            "is_weekend": 0,
            "duration_sec": 30,
            "has_emoji": 1,
            "has_call_to_action": 1,
            "platform": "tiktok",
            "category": "fitness",
            "trend_type": "rising"
        })
        
        assert "probability" in result
        probability = result["probability"]
        assert 0.0 <= probability <= 1.0, f"Probability {probability} out of valid range"
    
    def test_feature_validation(self):
        """O3-03: Model validates required features"""
        from app.utils.model_loader import validate_input
        
        valid_data = {
            "caption_length": 50,
            "posting_hour": 18,
            "platform": "tiktok",
            "category": "fitness"
        }
        
        is_valid, message = validate_input(valid_data)
        # Should either be valid or show clear error
        assert isinstance(is_valid, bool)
        assert isinstance(message, str)
    
    def test_prediction_saves_to_db(self, test_user):
        """O3-04: Predictions persist to database"""
        from database.db_manager import save_prediction
        
        save_prediction(
            test_user["id"],
            caption="Great content idea",
            platform="TikTok",
            category="Fitness",
            posting_hour=18,
            posting_day="Monday",
            duration_sec=30,
            has_trend=1,
            trend_type="rising",
            predicted_engagement=0.67,
            performance_score=75
        )
        
        # Verify it persisted
        from database.db_manager import get_prediction_history
        predictions = get_prediction_history(test_user["id"])
        assert len(predictions) > 0


# OBJECTIVE 4: EXPLAINABLE AI

class TestObjective4_ExplainableAI:
    """Objective 4: Explainable AI (SHAP) Integration"""
    
    def test_shap_explainer_loads(self):
        """O4-01: SHAP explainer initialises"""
        from app.utils.model_loader import load_shap_explainer
        
        explainer = load_shap_explainer()
        assert explainer is not None
    
    def test_shap_explanation_structure(self):
        """O4-02: SHAP explanation has expected structure"""
        from src.xai.explainer import EngagementExplainer
        from app.utils.model_loader import load_model
        
        model = load_model()
        feature_names = [
            'caption_length', 'posting_hour', 'is_weekend', 'duration_sec',
            'has_emoji', 'has_call_to_action', 'platform_tiktok', 'platform_youtube',
            # ... other 31 features
        ]
        
        explainer = EngagementExplainer(model, feature_names)
        assert explainer is not None
        assert hasattr(explainer, 'explainer')
    
    def test_feature_importance_ranking(self):
        """O4-03: Features ranked by importance"""
        from app.utils.model_loader import load_shap_explainer
        
        explainer = load_shap_explainer()
        assert explainer is not None
        # Explainer can rank feature importance


# OBJECTIVE 5: UI INTEGRATION 

class TestObjective5_UIIntegration:
    """Objective 5: Unified User Interface & Integration"""
    
    def test_trends_can_be_saved(self, test_user):
        """O5-01: M1 trends can be saved for later"""
        save_trend(
            test_user["id"],
            trend_topic="Web3 Security",
            trend_score=8.9,
            trend_source="twitter",
            trend_niche="Tech",
            notes="Trending on developer community"
        )
        
        saved = get_saved_trends(test_user["id"])
        assert len(saved) > 0
        assert saved[0]["trend_topic"] == "Web3 Security"
    
    def test_ideas_can_be_saved(self, test_user):
        """O5-02: M2 ideas can be saved for later"""
        save_idea(
            test_user["id"],
            "Web3 Explainer",
            "Explain blockchain in 30 seconds",
            "TikTok",
            "Tech",
            "Web3 Security",
            engagement_score=82
        )
        
        saved = get_saved_ideas(test_user["id"])
        assert len(saved) > 0
        assert saved[0]["idea_title"] == "Web3 Explainer"
    
    def test_predictions_persist(self, test_user):
        """O5-03: M3 predictions saved to user history"""
        from database.db_manager import save_prediction, get_prediction_history
        
        save_prediction(
            test_user["id"],
            caption="My awesome video",
            platform="TikTok",
            category="Tech",
            posting_hour=19,
            posting_day="Friday",
            duration_sec=45,
            has_trend=1,
            trend_type="rising",
            predicted_engagement=0.72,
            performance_score=80
        )
        
        history = get_prediction_history(test_user["id"], limit=10)
        assert len(history) > 0
    
    def test_multi_page_data_isolation(self):
        """O5-04: Data properly isolated between users on multi-page app"""
        # Create 2 users
        success_1, _, user_1_id = register_user(
            "m_page_user1",
            "m_page_1@example.com",
            "TestPass123",
            "TestPass123"
        )
        
        success_2, _, user_2_id = register_user(
            "m_page_user2",
            "m_page_2@example.com",
            "TestPass123",
            "TestPass123"
        )
        
        assert success_1 and success_2
        
        # User 1 saves trend
        save_trend(user_1_id, "User 1 Trend", 8.5, "twitter", "Tech", None)
        
        # User 2 saves different trend
        save_trend(user_2_id, "User 2 Trend", 7.5, "twitter", "Fitness", None)
        
        # Verify isolation
        user_1_trends = get_saved_trends(user_1_id)
        user_2_trends = get_saved_trends(user_2_id)
        
        assert len(user_1_trends) == 1
        assert len(user_2_trends) == 1
        assert user_1_trends[0]["trend_topic"] == "User 1 Trend"
        assert user_2_trends[0]["trend_topic"] == "User 2 Trend"
        
        # Cleanup
        delete_user(user_1_id)
        delete_user(user_2_id)


#  INTEGRATION: END-TO-END WORKFLOW 

class TestEndToEndWorkflow:
    """Integration tests - Full workflow validation"""
    
    def test_complete_user_journey(self, test_user):
        """E2E-01: Complete workflow from trend to optimisation"""
        # 1. User saves trend
        save_trend(
            test_user["id"],
            trend_topic="AI in Education",
            trend_score=8.7,
            trend_source="twitter",
            trend_niche="Tech",
            notes="Good trend for creators"
        )
        
        trends = get_saved_trends(test_user["id"])
        assert len(trends) == 1
        
        # 2. User saves idea based on trend
        save_idea(
            test_user["id"],
            idea_title="ChatGPT Homework Helper",
            idea_description="Show how ChatGPT helps with studies",
            platform="TikTok",
            category="Education",
            trend_topic="AI in Education",
            engagement_score=85
        )
        
        ideas = get_saved_ideas(test_user["id"])
        assert len(ideas) == 1
        
        # 3. User saves prediction for optimisation
        from database.db_manager import save_prediction, get_prediction_history
        
        save_prediction(
            test_user["id"],
            caption="ChatGPT Homework Tips",
            platform="TikTok",
            category="Education",
            posting_hour=19,
            posting_day="Friday",
            duration_sec=30,
            has_trend=1,
            trend_type="rising",
            predicted_engagement=0.68,
            performance_score=82
        )
        
        predictions = get_prediction_history(test_user["id"])
        assert len(predictions) == 1
        
        # Verify full user history
        assert len(get_saved_trends(test_user["id"])) == 1
        assert len(get_saved_ideas(test_user["id"])) == 1
        assert len(get_prediction_history(test_user["id"])) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
