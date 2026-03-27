"""Twitter trend ingestion script.

Fetches trending topics from Twitter via Apify scraper.
"""
#Import statements
from __future__ import annotations
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from .fetch_twitter_apify import fetch_twitter_trends

# Add parent directory to path to import from pipelines
sys.path.insert(0, str(Path(__file__).parent.parent))
from pipelines.nlp_processor import process_trend_nlp

# Load environment variables
load_dotenv()


# Save trends to JSON (to preserve tweets data)
def save_trends_json(
    trends: list[dict[str, Any]],
    output_path: Path
) -> None:
    """Save trends with tweets to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(trends, f, indent=2, ensure_ascii=False)


# Save trends to CSV (without tweets, for simple viewing)
def save_trends_csv(
    trends: list[dict[str, Any]],
    output_path: Path
) -> None:
    """Save trends summary to CSV (without tweets)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "topic", "score", "source", "discovered_at", "region", "niche",
        "tweet_count", "keywords", "sentiment", "hashtags"
    ]

    # Add tweet count for each trend and format lists for CSV
    csv_trends = []
    for trend in trends:
        trend_copy = {k: v for k, v in trend.items() if k != "tweets"}
        trend_copy["tweet_count"] = len(trend.get("tweets", []))

        # Join lists for better CSV formatting
        for field in ["keywords", "hashtags"]:
            if field in trend_copy and isinstance(trend_copy[field], list):
                # Ensure all items are strings (e.g., if they are tuples from NLP)
                items = [str(item[0]) if isinstance(item, tuple) else str(item) for item in trend_copy[field]]
                trend_copy[field] = ", ".join(items)

        csv_trends.append(trend_copy)
    
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_trends)


# Fetch all trends and save to CSV
def fetch_all_trends(
    max_trends: int = 50,
    output_path: Path = Path("data/examples/trends.csv")
) -> None:
    """Fetch trends from Twitter and save to CSV."""
    print("=" * 60)
    print("TWITTER TREND INGESTION")
    print("=" * 60)
    
    # Check for API token
    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        print("\n✗ ERROR: APIFY_API_TOKEN not found in environment")
        print("  Set it in your .env file or export it")
        return
    
    # Fetch Twitter trends
    print("\nFetching Twitter trends (US, live)...")
    try:
        twitter_trends = fetch_twitter_trends(
            apify_token=apify_token,
            max_trends=max_trends
        )
        print(f" Got {len(twitter_trends)} Twitter trends")
    except Exception as e:
        print(f"✗ Twitter fetch failed: {e}")
        return
    
    # Process NLP for each trend
    print("\nProcessing NLP (keywords, sentiment, hashtags)...")
    for i, trend in enumerate(twitter_trends, 1):
        print(f"  [{i}/{len(twitter_trends)}] {trend['topic']}")
        twitter_trends[i-1] = process_trend_nlp(trend)
    print(" NLP processing complete")
    
    # Save to both JSON and CSV
    json_path = output_path.parent / "trends.json"
    csv_path = output_path
    
    print(f"\nSaving to {json_path} and {csv_path}...")
    save_trends_json(twitter_trends, json_path)
    save_trends_csv(twitter_trends, csv_path)
    
    # Count total tweets
    total_tweets = sum(len(t.get("tweets", [])) for t in twitter_trends)
    
    print(f"\n{'=' * 60}")
    print(f"SUCCESS: {len(twitter_trends)} trends with {total_tweets} tweets saved")
    print(f"  JSON (with tweets): {json_path}")
    print(f"  CSV (summary): {csv_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch Twitter trends via Apify")
    parser.add_argument(
        "--max-trends",
        type=int,
        default=50,
        help="Maximum number of trends to fetch"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/examples/trends.csv"),
        help="Output CSV path"
    )
    
    args = parser.parse_args()
    fetch_all_trends(
        max_trends=args.max_trends,
        output_path=args.out
    )