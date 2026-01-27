"""Twitter trend ingestion script.

Fetches trending topics from Twitter via Apify scraper.
"""
#Import statements
from __future__ import annotations
import csv
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from .fetch_twitter_apify import fetch_twitter_trends

# Load environment variables
load_dotenv()


# Save trends to CSV
def save_trends(
    trends: list[dict[str, Any]],
    output_path: Path
) -> None:
    # Save the trends to the CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["topic", "score", "source", "discovered_at", "region", "niche"]
    
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trends)


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
        print(f"✓ Got {len(twitter_trends)} Twitter trends")
    except Exception as e:
        print(f"✗ Twitter fetch failed: {e}")
        return
    
    # Save to CSV
    print(f"\nSaving to {output_path}...")
    save_trends(twitter_trends, output_path)
    
    print(f"\n{'=' * 60}")
    print(f"SUCCESS: {len(twitter_trends)} trends saved to {output_path}")
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