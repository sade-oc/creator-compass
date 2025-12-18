"""Reddit trend ingestion with niche categorization.

Fetches hot posts from niche-specific subreddits and tags them appropriately.
No authentication required.
"""

#Import statements
from __future__ import annotations
import csv
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import requests
from .niche_config import get_all_niches, get_subreddits_for_niche, get_keywords_for_niche

# User-Agent to tell reditt im not a bot 
UA = {"User-Agent": "CreatorCompass/1.0 (+https://github.com/sade-oc/creator-compass)"}

# Filter patterns for meta posts that aren't useful trends
META_PATTERNS = [
    "daily", "weekly", "monthly", "thread", "megathread",
    "discussion thread", "simple questions", "looking for mods",
    "welcome to r/", "reminder", "rules", "mod post",
    "official daily", "general discussion", "advice thread",
    "rate my", "what are you", "[meta]", "casual talk",
    "[ama]", "ask us anything", "suggest me"
]

# Fetch posts from subreddit
def fetch_subreddit_hot(subreddit: str, limit: int = 10) -> list[dict[str, Any]]:
    # Fetch hot posts from a specific subreddit.
    url = f"https://www.reddit.com/r/{subreddit}/hot.json"
    params = {"limit": limit}
    r = requests.get(url, headers=UA, params=params, timeout=15)
    
    # Add delay to avoid rate limiting
    time.sleep(0.5)
    
    if r.status_code != 200:
        print(f"Warning: Failed to fetch r/{subreddit} ({r.status_code})")
        return [] # Return empty list on failure
    
    payload = r.json()
    posts = payload.get("data", {}).get("children", [])
    return [p["data"] for p in posts] # Returns a list of post objects


# Decide if post is relevant 
def is_relevant_post(post: dict[str, Any], niche_keywords: list[str]) -> bool:
    # Check if post is relevant to niche and not a meta post.
    title = post.get("title", "").lower()
    selftext = post.get("selftext", "").lower()
    
    # Filter out meta posts
    for pattern in META_PATTERNS:
        if pattern in title:
            return False
    
    # Check if any niche keyword appears in title or body
    combined_text = f"{title} {selftext}"
    for keyword in niche_keywords:
        if keyword.lower() in combined_text:
            return True
    
    # If no keywords match but title is substantial (likely content), keep it
    # This catches posts that are relevant but don't use exact keywords
    return len(title) > 30 and not any(p in title for p in ["?", "daily", "thread"])

# Normalize Reddit upvotes into a trend score
def normalize_scores(scores: list[int]) -> list[float]:
    # Use logarithmic scaling to map scores into 6.0 - 9.5 range
    if not scores:
        return []
    m = max(scores)
    if m <= 0:
        return [6.0 for _ in scores]
    
    out = []
    for s in scores:
        val = 6.0 + 3.5 * (math.log10(s + 1) / math.log10(m + 1))
        out.append(round(val, 1))
    return out

# Fetch trends for a specific niche
def fetch_niche_trends(niche: str, posts_per_subreddit: int = 5) -> list[dict[str, Any]]:
    # Fetch trends for a specific niche from its configured subreddits.
    subreddits = get_subreddits_for_niche(niche)
    niche_keywords = get_keywords_for_niche(niche)
    all_posts = []
    
    for sub in subreddits:
        posts = fetch_subreddit_hot(sub, limit=posts_per_subreddit * 2)  # Fetch extra to account for filtering
        # Filter for relevant posts
        relevant_posts = [p for p in posts if is_relevant_post(p, niche_keywords)]
        all_posts.extend(relevant_posts[:posts_per_subreddit])  # Take top N after filtering
    
    # Extract scores and normalize
    scores = [int(p.get("score", 0)) for p in all_posts]
    normalized = normalize_scores(scores)
    
    # Build trend rows
    trends = []
    now = datetime.now(timezone.utc).isoformat()
    
    for i, post in enumerate(all_posts):
        title = post.get("title", "").strip()
        created_utc = post.get("created_utc")
        ts = (
            datetime.fromtimestamp(created_utc, tz=timezone.utc).isoformat()
            if created_utc
            else now
        )
        
        trends.append({
            "topic": title[:180],
            "score": normalized[i] if i < len(normalized) else 6.0,
            "source": "reddit",
            "discovered_at": ts,
            "region": "reddit_global",
            "niche": niche
        })
    
    return trends

# Fetch trends across all niches
def fetch_all_niches(posts_per_subreddit: int = 5) -> list[dict[str, Any]]:
    # Fetch trends across all configured niches.
    all_trends = []
    niches = get_all_niches()
    
    print(f"Fetching trends for {len(niches)} niches...")
    # Loops through each niche and calls fetch_niche_trends
    for niche in niches:
        print(f"  - {niche}...")
        trends = fetch_niche_trends(niche, posts_per_subreddit)
        all_trends.extend(trends)
        print(f"    Found {len(trends)} trends")
    
    return all_trends

# Save results to csv 
def save_to_csv(trends: list[dict[str, Any]], output_path: Path) -> None:
    # Save trends to CSV file.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = ["topic", "score", "source", "discovered_at", "region", "niche"]
    
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trends)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch Reddit trends by niche")
    parser.add_argument("--posts-per-sub", type=int, default=5, help="Posts to fetch per subreddit")
    parser.add_argument("--niche", type=str, help="Specific niche to fetch (omit for all)")
    parser.add_argument("--out", type=Path, default=Path("data/examples/trends_reddit.csv"))
    args = parser.parse_args()
    
    if args.niche:
        trends = fetch_niche_trends(args.niche, args.posts_per_sub)
    else:
        trends = fetch_all_niches(args.posts_per_sub)
    
    save_to_csv(trends, args.out)
    print(f"\n✓ Saved {len(trends)} trends to {args.out}")
