#NLP processing pipeline for tweet analysis.

import re
from collections import Counter
from typing import Any
import nltk
from textblob import TextBlob

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

STOP_WORDS = set(stopwords.words('english'))


def tokenize_text(text: str) -> list[str]:
    """Tokenize and clean tweet text."""
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Remove @mentions
    text = re.sub(r'@\w+', '', text)
    # Tokenize
    tokens = word_tokenize(text.lower())
    # Remove stopwords and short tokens
    tokens = [t for t in tokens if t.isalnum() and len(t) > 2 and t not in STOP_WORDS]
    return tokens


def extract_keywords(tweets: list[dict[str, Any]], top_n: int = 10) -> list[tuple[str, int]]:
    """Extract top keywords from tweets."""
    all_tokens = []
    for tweet in tweets:
        text = tweet.get("text", "")
        all_tokens.extend(tokenize_text(text))
    
    # Count and return top N
    counter = Counter(all_tokens)
    return counter.most_common(top_n)


def extract_hashtags(tweets: list[dict[str, Any]]) -> list[tuple[str, int]]:
    """Extract hashtags from tweets."""
    hashtags = []
    for tweet in tweets:
        text = tweet.get("text", "")
        hashtags.extend(re.findall(r'#\w+', text.lower()))
    
    counter = Counter(hashtags)
    return counter.most_common(10)


def analyze_sentiment(tweets: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze sentiment of tweets."""
    sentiments = []
    
    for tweet in tweets:
        text = tweet.get("text", "")
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # type: ignore 
        sentiments.append(polarity)
    
    if not sentiments:
        return {"average": 0, "positive": 0, "neutral": 0, "negative": 0}
    
    avg_sentiment = sum(sentiments) / len(sentiments)
    positive = sum(1 for s in sentiments if s > 0.1)
    neutral = sum(1 for s in sentiments if -0.1 <= s <= 0.1)
    negative = sum(1 for s in sentiments if s < -0.1)
    
    return {
        "average": round(avg_sentiment, 3),
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "total": len(sentiments)
    }


def process_trend_nlp(trend: dict[str, Any]) -> dict[str, Any]:
    """Process all NLP for a single trend."""
    tweets = trend.get("tweets", [])
    
    if not tweets:
        return trend
    
    # Add NLP analysis
    trend["keywords"] = extract_keywords(tweets, top_n=10)
    trend["hashtags"] = extract_hashtags(tweets)
    trend["sentiment"] = analyze_sentiment(tweets)

    # Re-categorize based on extracted keywords and content (more accurate!)
    trend["niche"] = categorize_from_content(trend["keywords"], tweets)
    
    return trend


def categorize_from_content(keywords: list[tuple[str, int]], tweets: list[dict[str, Any]]) -> str:
    """Categorize trend using extracted keywords and tweet context."""
    
    if not keywords and not tweets:
        return "General"
    
    # Define category patterns - keywords that strongly indicate each category
    category_patterns = {
        "Entertainment/Media": {
            "strong": ["grammys", "grammy", "oscar", "emmy", "award", "concert", "album", 
                      "song", "music", "movie", "film", "netflix", "show", "episode",
                      "performance", "artist", "rapper", "singer", "actor", "actress"],
            "moderate": ["stage", "tour", "release", "debut", "premiere", "streaming",
                        "watched", "listen", "video", "entertainment", "celebrity"]
        },
        "Sports": {
            "strong": ["game", "team", "player", "score", "goal", "championship",
                      "playoff", "season", "league", "coach", "win", "victory",
                      "nfl", "nba", "mlb", "nhl", "football", "basketball", "soccer"],
            "moderate": ["match", "stadium", "fans", "draft", "athletic", "sport"]
        },
        "Tech/Gaming": {
            "strong": ["gaming", "gamer", "console", "playstation", "xbox", "nintendo",
                      "twitch", "streamer", "gameplay", "tech", "ai", "software",
                      "app", "update", "launch", "crypto", "bitcoin", "blockchain"],
            "moderate": ["technology", "digital", "online", "virtual", "code", "developer"]
        },
        "Politics/News": {
            "strong": ["president", "senate", "congress", "election", "vote", "政治",
                      "government", "political", "politician", "law", "bill", "policy",
                      "democrat", "republican", "debate", "campaign"],
            "moderate": ["breaking", "news", "report", "statement", "announcement"]
        },
        "Fitness/Wellness": {
            "strong": ["workout", "fitness", "gym", "training", "exercise", "health",
                      "wellness", "yoga", "meditation", "diet", "nutrition"],
            "moderate": ["healthy", "weight", "muscle", "cardio", "mental"]
        },
        "Beauty/Fashion": {
            "strong": ["makeup", "beauty", "skincare", "fashion", "style", "outfit",
                      "dress", "designer", "model", "runway", "cosmetics"],
            "moderate": ["look", "wear", "hair", "nails", "clothing"]
        },
        "Food/Cooking": {
            "strong": ["recipe", "cooking", "chef", "restaurant", "food", "meal",
                      "dish", "cuisine", "baking", "kitchen"],
            "moderate": ["tasty", "delicious", "eat", "dinner", "lunch", "breakfast"]
        }
    }
    
    # Score each category based on keyword matches
    category_scores = {}
    
    for category, patterns in category_patterns.items():
        score = 0
        
        # Check keywords (already extracted and cleaned!)
        for keyword, count in keywords[:15]:  # Top 15 keywords
            kw_lower = keyword.lower()
            
            # Strong match: 3 points × frequency
            if kw_lower in patterns["strong"]:
                score += 3 * min(count, 10)  # Cap frequency impact
            
            # Moderate match: 1 point × frequency
            elif kw_lower in patterns["moderate"]:
                score += 1 * min(count, 5)
        
        # Also check tweet text for context (but weighted less)
        if tweets:
            sample_text = " ".join([t.get("text", "").lower() for t in tweets[:10]])
            
            for strong_kw in patterns["strong"]:
                if strong_kw in sample_text:
                    score += 2
            
            for mod_kw in patterns["moderate"]:
                if mod_kw in sample_text:
                    score += 1
        
        if score > 0:
            category_scores[category] = score
    
    # Return category with highest score (require minimum score of 5 to avoid false positives)
    if category_scores:
        best_category = max(category_scores, key=lambda x: category_scores[x])
        if category_scores[best_category] >= 5:
            return best_category
    
    return "General"