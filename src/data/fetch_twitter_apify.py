"""Twitter (X) trend ingestion via Apify scraper.
Fetches trending topics from Twitter using Apify's Twitter Trends Scraper.
Maps trends to niches based on keywords.
"""

from __future__ import annotations
import os
import math
from datetime import datetime, timezone
from typing import Any
from dotenv import load_dotenv
from apify_client import ApifyClient

from .niche_config import get_all_niches, get_keywords_for_niche

# Load environment variables from .env file
load_dotenv()

#Converts raw tweet volumes into a normalised score 
def normalise_tweet_volumes(volumes: list[int]) -> list[float]:
    #Normalise tweet volumes to 7.0-9.5 range using logarithmic scaling.
    if not volumes:
        return []
    m = max(volumes)
    if m <= 0:
        return [7.0 for _ in volumes]
    
    out = []
    for v in volumes:
        val = 7.0 + 2.5 * (math.log10(v + 1) / math.log10(m + 1))
        out.append(round(val, 1))
    return out

# For each trend we want to get the top tweets for it to see what the general consensus is 
def fetch_tweets_for_trend(
    topic: str,
    apify_token: str,
    max_tweets: int = 100
) -> list[dict[str, Any]]:
    
    client = ApifyClient(apify_token)
    
    # Build search query
    run_input = {
        "searchTerms": [topic],
        "sort": "Top", # We want to see what the more viral tweets are saying 
        "maxItems": max_tweets,
        "tweetLanguage": "en"
    }
    
    print(f"    Fetching {max_tweets} tweets for: {topic}")
    
    try:
        # Run tweet scraper
        run = client.actor("apidojo/tweet-scraper").call(run_input=run_input)
        
        # Extract tweets
        tweets = []
        if run and "defaultDatasetId" in run:
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                tweets.append({
                    "text": item.get("text", ""),
                    "likes": item.get("likeCount", 0),
                    "retweets": item.get("retweetCount", 0),
                    "replies": item.get("replyCount", 0),
                    "timestamp": item.get("createdAt", ""),
                    "author": item.get("author", {}).get("userName", "")
                })
        
        print(f"     Got {len(tweets)} tweets")
        return tweets
    
    except Exception as e:
        print(f"    ✗ Error fetching tweets: {e}")
        return []


def fetch_twitter_trends(
    apify_token: str | None = None,
    max_trends: int = 50,
    fetch_tweets: bool = True,
) -> list[dict[str, Any]]:
   
    # Fetch trending topics from Twitter via Apify scraper (US trends, live only).
    
    # Get API token
    token = apify_token or os.getenv("APIFY_API_TOKEN")
    if not token:
        raise ValueError(
            "Apify API token required. Set APIFY_API_TOKEN env var."
        )
    
    print("Fetching Twitter trends (US, live)...")
    
    # Initialise Apify client
    client = ApifyClient(token)
    
    # Prepare Actor input - US only, live only
    run_input = {
        "country": "2",  # United States
        "live": True,
        "hour1": False,
        "hour3": False,
        "hour6": False,
        "hour12": False,
        "hour24": False,
        "day2": False,
        "day3": False,
        "proxyOptions": {
            "useApifyProxy": True
        }
    }
    
    # Run the Actor and wait for it to finish
    print("  Starting Apify scraper...")
    run = client.actor("karamelo/twitter-trends-scraper").call(run_input=run_input)
    
    # Fetch results from the Actor's default dataset
    raw_trends = []
    if run and "defaultDatasetId" in run:
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            raw_trends.append(item)
    
    print(f"   Retrieved {len(raw_trends)} raw trends from Apify")
    
    # Parse and normalize trends
    trends = []
    now = datetime.now(timezone.utc).isoformat()
   
    # Build trend records with rank-based scoring
    for i, item in enumerate(raw_trends[:max_trends]):
        # Try different possible field names for topic
        topic = (
            item.get("trend") or
            item.get("name") or 
            item.get("topic") or 
            ""
        )
        if not topic:
            continue
        
        # Rank-based score: #1 gets 9.5, gradually decreasing
        # Formula: 9.5 - (rank * 2.5 / max_trends)
        rank_score = max(7.0, 9.5 - (i * 2.5 / max_trends))
        rank_score = round(rank_score, 1)
        
        # Categorize using GPT
        if not fetch_tweets:
            # Stage 1: Use GPT to categorize by topic name only
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from pipelines.nlp_processor import categorise_with_gpt
            
            niche = categorise_with_gpt(tweets=None, topic=topic)
        else:
            # Stage 2: Placeholder - will be overridden by GPT categorization in NLP processing
            niche = "General"
        
        # Only fetch tweets if requested (Stage 2 - user selected trends)
        if fetch_tweets:
            tweets = fetch_tweets_for_trend(topic, token, max_tweets=50)
        else:
            tweets = []

        trends.append({
            "topic": topic[:180],
            "score": rank_score,
            "source": "twitter",
            "discovered_at": now,
            "region": "twitter_us",
            "niche": niche,
            "tweets": tweets 
        })
    
    print(f"   Processed {len(trends)} trends, categorised into niches")
    return trends


if __name__ == "__main__":
    import argparse
    import csv
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="Fetch Twitter trends via Apify")
    parser.add_argument("--token", type=str, help="Apify API token")
    parser.add_argument("--max-trends", type=int, default=50)
    parser.add_argument("--out", type=Path, default=Path("data/examples/trends_twitter.csv"))
    
    args = parser.parse_args()
    
    trends = fetch_twitter_trends(
        apify_token=args.token,
        max_trends=args.max_trends
    )
    
    # Save to CSV
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["topic", "score", "source", "discovered_at", "region", "niche"]
    
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trends)
    
    print(f"\n Saved {len(trends)} Twitter trends to {args.out}")