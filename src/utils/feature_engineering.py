# Extracts the meaningful features from each video that the ML model will use to predict engagement 

import re
from datetime import datetime
from typing import Dict, List


def extract_text_features(text: str) -> Dict:
    if not text:
        text = ""
    
    # Basic text features
    caption_length = len(text)
    word_count = len(text.split())
    
    # Emoji detection (basic Unicode ranges for common emojis)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    emojis = emoji_pattern.findall(text)
    has_emoji = len(emojis) > 0
    emoji_count = len(emojis)
    
    # Call-to-action detection
    cta_keywords = [
        'link in bio', 'follow', 'subscribe', 'click', 'check out',
        'visit', 'shop', 'buy', 'get', 'download', 'join', 'sign up',
        'watch', 'see more', 'learn more', 'dm me', 'comment', 'tag'
    ]
    text_lower = text.lower()
    has_call_to_action = any(keyword in text_lower for keyword in cta_keywords)
    
    # Question detection
    has_question = '?' in text
    
    # Sentiment (simple keyword-based)
    positive_words = [
        'love', 'amazing', 'awesome', 'great', 'best', 'happy', 'excited',
        'beautiful', 'perfect', 'wonderful', 'fantastic', 'excellent', 'good'
    ]
    negative_words = [
        'hate', 'bad', 'worst', 'terrible', 'awful', 'horrible', 'sad',
        'angry', 'disappointed', 'annoying', 'wrong', 'fail', 'sucks'
    ]
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        sentiment = 'positive'
    elif negative_count > positive_count:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return {
        'caption_length': caption_length,
        'word_count': word_count,
        'has_emoji': has_emoji,
        'emoji_count': emoji_count,
        'has_call_to_action': has_call_to_action,
        'has_question': has_question,
        'sentiment': sentiment
    }


def extract_hashtags(hashtags_list: List) -> Dict:
    if not hashtags_list:
        return {
            'hashtag_count': 0,
            'hashtags': []
        }
    
    # Extract hashtag names
    if isinstance(hashtags_list[0], dict):
        # TikTok format: [{'name': 'fitness', 'id': '123'}, ...]
        hashtag_names = [tag.get('name', '') for tag in hashtags_list]
    else:
        # Simple list format
        hashtag_names = hashtags_list
    
    return {
        'hashtag_count': len(hashtag_names),
        'hashtags': hashtag_names
    }


def extract_time_features(timestamp_iso: str) -> Dict:
    try:
        dt = datetime.fromisoformat(timestamp_iso.replace('Z', '+00:00'))
        
        return {
            'posting_hour': dt.hour,
            'posting_day': dt.strftime('%A'),  # Monday, Tuesday, etc.
            'posting_month': dt.month,
            'posting_year': dt.year
        }
    except Exception as e:
        # Return defaults if parsing fails
        return {
            'posting_hour': 0,
            'posting_day': 'Unknown',
            'posting_month': 0,
            'posting_year': 0
        }


def calculate_engagement_rate(likes: int, comments: int, shares: int, 
                              saves: int, views: int) -> float:

    if views == 0:
        return 0.0
    
    total_engagement = likes + comments + shares + saves
    return (total_engagement / views) * 100