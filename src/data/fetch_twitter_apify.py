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


def categorise_trend_to_niche(topic: str) -> str:
  
    # Map a Twitter trend to a niche based on enhanced pattern matching.
    topic_lower = topic.lower()
    
    # Sports: Teams, leagues, events, and common athlete names
    sports_patterns = [
        'bowl', 'nfl', 'nba', 'mlb', 'nhl', '#wwe', 'ufc', 'soccer', 'football',
        'patriots', 'rams', 'seahawks', 'broncos', 'chiefs', 'cowboys', 'pats',
        'lakers', 'celtics', 'warriors', 'yankees', 'dodgers',
        'playoffs', 'championship', 'finals', 'game', 'match',
        'darnold', 'mahomes', 'brady', 'curry', 'lebron', 'messi',
        'seattle', 'dallas', 'boston', 'lakers'  # Cities often refer to teams in sports context
    ]
    # Check for sport-related hashtags
    if topic.startswith('#') and any(s in topic_lower for s in ['wwe', 'nfl', 'nba', 'mlb', 'ufc']):
        return "Entertainment/Media"
    
    if any(p in topic_lower for p in sports_patterns):
      return "Sports"
    
    # Gaming: Game titles, gaming terms, gaming hashtags
    gaming_patterns = [
        'game', 'gaming', 'gamer', 'esports', 'twitch', 'fortnite', 'cod',
        'minecraft', 'roblox', 'valorant', 'league', 'warzone', 'apex',
        'playstation', 'xbox', 'nintendo', 'steam', 'highguard'
    ]
    if any(p in topic_lower for p in gaming_patterns):
        return "Tech/Gaming"
    
    # Politics/News 
    political_patterns = [
        'politics', 'senate', 'congress', 'president', 'governor',
        'election', 'vote', 'bill', 'law', 'capitol', 'white house',
        'pretti', 'homan', 'walz', 'noem', 'rittenhouse', 'riley',
        'minnesota', 'minneapolis', 'bovino'  # Current political trend names
    ]
    if any(p in topic_lower for p in political_patterns):
      return "Politics/News"
    
    # Tech/Apps: Signal, social media, tech companies
    tech_patterns = ['signal', 'telegram', 'whatsapp', 'tiktok', 'instagram', 
                     'twitter', 'meta', 'google', 'apple', 'ai', 'tech']
    if any(p in topic_lower for p in tech_patterns):
        return "Tech/Gaming"
    
    # Now check creator-focused niches with keyword matching
    niches = get_all_niches()
    niche_scores = {}
    
    for niche in niches:
        keywords = get_keywords_for_niche(niche)
        score = sum(1 for kw in keywords if kw.lower() in topic_lower)
        if score > 0:
            niche_scores[niche] = score
    
    # Return the niche with highest score, or 'General' if none match
    if niche_scores:
        return max(niche_scores, key=lambda k: niche_scores.get(k, 0))
    
    return "General"


def fetch_twitter_trends(
    apify_token: str | None = None,
    max_trends: int = 50
) -> list[dict[str, Any]]:
   
    # Fetch trending topics from Twitter via Apify scraper (US trends, live only).
    
    # Get API token
    token = apify_token or os.getenv("APIFY_API_TOKEN")
    if not token:
        raise ValueError(
            "Apify API token required. Set APIFY_API_TOKEN env var."
        )
    
    print("Fetching Twitter trends (US, live)...")
    
    # Initialize Apify client
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
    
    print(f"  ✓ Retrieved {len(raw_trends)} raw trends from Apify")
    
    # Parse and normalize trends
    trends = []
    now = datetime.now(timezone.utc).isoformat()
    
    # Since Apify doesn't provide volumes, use rank-based scoring
    # Top trends get higher scores (9.5 for #1, decreasing to 7.0)

    
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
        
        # Categorise into niche
        niche = categorise_trend_to_niche(topic)
        
        trends.append({
            "topic": topic[:180],
            "score": rank_score,
            "source": "twitter",
            "discovered_at": now,
            "region": "twitter_us",
            "niche": niche
        })
    
    print(f"  ✓ Processed {len(trends)} trends, categorised into niches")
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