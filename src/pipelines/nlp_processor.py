#NLP processing pipeline for tweet analysis.

import re
from collections import Counter
from typing import Any, Optional
import nltk
from textblob import TextBlob
import os
from openai import OpenAI

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


def analyse_sentiment(tweets: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyse sentiment of tweets."""
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

# Categorising the trends using gpt 4 for more acturate niche categorisation 
def categorise_with_gpt(tweets: Optional[list[dict[str, Any]]] = None, topic: str = "") -> str:
   
    
    if not topic:
        return "General"
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not found, falling back to General category")
        return "General"
    
    # Define categories once
    categories_text = """Categories:
- Entertainment/Media (music, movies, TV, celebrities, awards shows, performances)
- Sports (games, teams, athletes, competitions, leagues)
- Tech/Gaming (technology, apps, video games, gaming, AI, crypto)
- Politics/News (government, elections, political figures, breaking news)
- Fitness/Wellness (health, workouts, mental health, wellness)
- Beauty/Fashion (makeup, style, fashion, clothing, design)
- Food/Cooking (recipes, restaurants, chefs, cuisine)
- Finance (stocks, markets, cryptocurrencies, trading, investments, banking, NFTs)
- General (everything else, greetings, general topics)"""
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Build prompt based on available data
        if tweets and len(tweets) > 0:
            # Stage 2: Use tweet context for more accuracy
            sample_tweets = [t.get("text", "")[:150] for t in tweets[:5]]
            tweets_context = "\n".join([f"- {tweet}" for tweet in sample_tweets if tweet])
            
            prompt = f"""Categorize this trending topic into ONE category.

Trending Topic: {topic}

Sample Tweets:
{tweets_context}

{categories_text}

Return ONLY the category name, nothing else."""
        else:
            # Stage 1: Categorize based on topic name only
            prompt = f"""Categorize this trending topic into ONE category.

Trending Topic: {topic}

{categories_text}

Examples:
- "Grammys" → Entertainment/Media
- "#SuperBowl" → Sports
- "ChatGPT" → Tech/Gaming
- "Biden" → Politics/News
- "Bitcoin" → Finance
- "#MondayMotivation" → General

Return ONLY the category name, nothing else."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=20
        )
        
        category = response.choices[0].message.content
        if category is None:
            return "General"
        category = category.strip()
        
        # Validate response
        valid_categories = [
            "Entertainment/Media", "Sports", "Tech/Gaming", "Politics/News",
            "Fitness/Wellness", "Beauty/Fashion", "Food/Cooking", "General"
        ]
        
        if category in valid_categories:
            print(f"GPT categorised '{topic}' as: {category}")
            return category
        else:
            print(f"Invalid GPT response: {category}, using General")
            return "General"
            
    except Exception as e:
        print(f"    ✗ GPT error: {e}, falling back to General")
        return "General"


def process_trend_nlp(trend: dict[str, Any]) -> dict[str, Any]:
    """Process all NLP analysis for a single trend.
    
    Adds the following fields to the trend dict:
    - keywords: Top 10 keywords with counts
    - hashtags: Top 10 hashtags with counts  
    - sentiment: Sentiment analysis (average, positive/neutral/negative counts)
    - niche: GPT-categorised niche
    
    Args:
        trend: Dict containing 'topic' and 'tweets' fields
        
    Returns:
        Updated trend dict with NLP analysis
    """
    tweets = trend.get("tweets", [])
    
    if not tweets:
        return trend
    
    # Add NLP analysis
    trend["keywords"] = extract_keywords(tweets, top_n=10)
    trend["hashtags"] = extract_hashtags(tweets)
    trend["sentiment"] = analyse_sentiment(tweets)

    # Use GPT for intelligent categorization
    topic = trend.get("topic", "")
    trend["niche"] = categorise_with_gpt(tweets, topic)
    
    return trend

