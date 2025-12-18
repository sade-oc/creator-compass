"""Reddit trend ingestion script.

Fetches niche-specific trends from Reddit subreddits.
"""
#Import statements
from __future__ import annotations
import csv
from pathlib import Path
from typing import Any
from .fetch_reddit import fetch_all_niches as fetch_reddit_trends

# Save trends to CSV
def save_trends(
    trends: list[dict[str, Any]],
    output_path: Path
) -> None:
    # Save trends to a CSV file.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["topic", "score", "source", "discovered_at", "region", "niche"]
    
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trends)


# Fetch all trends and save to CSV
def fetch_all_trends(
    reddit_posts_per_sub: int = 5,
    output_path: Path = Path("data/examples/trends.csv")
) -> None:
    # Fetch trends from Reddit and save to CSV.
    print("=" * 60)
    print("=" * 60)
    
    # Fetch Reddit trends
    print("\nFetching Reddit trends by niche...")
    reddit_trends = fetch_reddit_trends(posts_per_subreddit=reddit_posts_per_sub)
    print(f"✓ Got {len(reddit_trends)} trends")
    
    # Save to CSV
    print(f"\nSaving to {output_path}...")
    save_trends(reddit_trends, output_path)
    
    print(f"\n{'=' * 60}")
    print(f"SUCCESS: {len(reddit_trends)} trends saved to {output_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch Reddit trends by niche")
    parser.add_argument(
        "--posts-per-sub",
        type=int,
        default=5,
        help="Posts to fetch per subreddit"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/examples/trends.csv"),
        help="Output CSV path"
    )
    
    args = parser.parse_args()
    fetch_all_trends(
        reddit_posts_per_sub=args.posts_per_sub,
        output_path=args.out
    )
