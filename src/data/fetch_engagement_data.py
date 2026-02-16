# Fetch engagement data for model training 

from apify_client import ApifyClient
import json
import os
from datetime import datetime
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Your Apify token
APIFY_TOKEN = os.getenv('APIFY_API_TOKEN')

# Apify Actor IDs
ACTORS = {
    'tiktok': 'clockworks/tiktok-scraper',
    'instagram': 'apify/instagram-scraper',
    'youtube': 'apify/youtube-shorts-scraper'
}

# Preset collections for diverse training data
PRESET_COLLECTIONS = {
    'fitness': ['fitness', 'workout', 'gym'],
    'food': ['cooking', 'recipe', 'foodtok'],
    'tech': ['tech', 'technology', 'gadgets'],
    'lifestyle': ['lifestyle', 'vlog', 'dailylife'],
    'education': ['learn', 'education', 'tutorial'],
    'beauty': ['beauty', 'makeup', 'skincare'],
    'finance': ['finance', 'money', 'investing'],
    'travel': ['travel', 'wanderlust', 'explore'],
    'comedy': ['funny', 'comedy', 'humor'],
    'fashion': ['fashion', 'style', 'ootd']
}


def ensure_data_dirs():
    """Create data directories if they don't exist"""
    dirs = [
        PROJECT_ROOT / 'data/raw/tiktok',
        PROJECT_ROOT / 'data/raw/instagram',
        PROJECT_ROOT / 'data/raw/youtube',
        PROJECT_ROOT / 'data/processed'
    ]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Data directories ensured at: {PROJECT_ROOT / 'data'}")


def scrape_tiktok(label: str, hashtags: list, results_per_hashtag: int = 50):
 
    client = ApifyClient(APIFY_TOKEN)
    
    run_input = {
        "hashtags": [f"#{tag}" for tag in hashtags],
        "resultsPerPage": results_per_hashtag,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadSlideshowImages": False
    }
    
    print(f"\n{'='*60}")
    print(f"Scraping TikTok - {label.upper()}")
    print(f"   Hashtags: {', '.join(hashtags)}")
    print(f"   Target: {results_per_hashtag} videos per hashtag")
    print(f"{'='*60}")
    
    try:
        run = client.actor(ACTORS['tiktok']).call(run_input=run_input)
        
        if not run or "defaultDatasetId" not in run:
            print(f"TikTok scraper failed to run for {label}")
            return []
        
        items = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            items.append(item)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = PROJECT_ROOT / f"data/raw/tiktok/tiktok_{label}_{timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(items, f, indent=2)
        
        print(f"Saved {len(items)} TikTok videos to {output_path}")
        return items
        
    except Exception as e:
        print(f"Error scraping TikTok for {label}: {str(e)}")
        return []


def scrape_instagram(label: str, hashtags: list, results_limit: int = 50):
    """Scrape Instagram Reels for given hashtags"""
    client = ApifyClient(APIFY_TOKEN)
    
    run_input = {
        "hashtags": hashtags,
        "resultsLimit": results_limit,
        "resultsType": "posts",
        "searchType": "hashtag"
    }
    
    print(f"\n{'='*60}")
    print(f"📸 Scraping Instagram Reels - {label.upper()}")
    print(f"   Hashtags: {', '.join(hashtags)}")
    print(f"   Target: {results_limit} Reels")
    print(f"{'='*60}")
    
    try:
        run = client.actor(ACTORS['instagram']).call(run_input=run_input)
        
        if not run or "defaultDatasetId" not in run:
            print(f"Instagram scraper failed to run for {label}")
            return []
        
        items = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            if item.get('type') in ['Video', 'Sidecar']:
                items.append(item)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = PROJECT_ROOT / f"data/raw/instagram/instagram_{label}_{timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(items, f, indent=2)
        
        print(f"Saved {len(items)} Instagram Reels to {output_path}")
        return items
        
    except Exception as e:
        print(f"Error scraping Instagram for {label}: {str(e)}")
        return []


def scrape_youtube(label: str, channels: list, max_results: int = 50):
    """Scrape YouTube Shorts from given channels"""
    client = ApifyClient(APIFY_TOKEN)
    
    run_input = {
        "channels": channels,
        "maxResultsShorts": max_results // len(channels),
    }
    
    print(f"\n{'='*60}")
    print(f"Scraping YouTube Shorts - {label.upper()}")
    print(f"   Channels: {', '.join(channels)}")
    print(f"   Target: {max_results} Shorts total")
    print(f"{'='*60}")
    
    try:
        run = client.actor(ACTORS['youtube']).call(run_input=run_input)
        
        if not run or "defaultDatasetId" not in run:
            print(f"YouTube scraper failed to run for {label}")
            return []
        
        items = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            items.append(item)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = PROJECT_ROOT / f"data/raw/youtube/youtube_{label}_{timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(items, f, indent=2)
        
        print(f"Saved {len(items)} YouTube Shorts to {output_path}")
        return items
        
    except Exception as e:
        print(f"Error scraping YouTube for {label}: {str(e)}")
        return []


def collect_tiktok_data(label: str, hashtags: list, results_total: int = 50):
    """Collect TikTok data for any hashtags"""
    ensure_data_dirs()
    results_per_hashtag = results_total // len(hashtags)
    return scrape_tiktok(label, hashtags, results_per_hashtag)


def collect_instagram_data(label: str, hashtags: list, results_total: int = 50):
    """Collect Instagram data for any hashtags"""
    ensure_data_dirs()
    return scrape_instagram(label, hashtags, results_total)


def collect_youtube_data(label: str, channels: list, results_total: int = 50):
    """Collect YouTube Shorts from any channels"""
    ensure_data_dirs()
    return scrape_youtube(label, channels, results_total)


def collect_batch(collections: list, platform: str = 'tiktok'):
    
    print(f"\n{'#'*60}")
    print(f"  BATCH COLLECTION - {platform.upper()}")
    print(f"  Collections: {len(collections)}")
    print(f"  Estimated time: {len(collections) * 2-5} minutes")
    print(f"{'#'*60}\n")
    
    results = {}
    
    for idx, collection in enumerate(collections, 1):
        label = collection['label']
        count = collection.get('count', 50)
        
        print(f"\n[{idx}/{len(collections)}] Processing: {label}")
        
        if platform == 'tiktok':
            hashtags = collection.get('hashtags', [])
            results[label] = collect_tiktok_data(label, hashtags, count)
            
        elif platform == 'instagram':
            hashtags = collection.get('hashtags', [])
            results[label] = collect_instagram_data(label, hashtags, count)
            
        elif platform == 'youtube':
            channels = collection.get('channels', [])
            results[label] = collect_youtube_data(label, channels, count)
    
    # Summary
    print(f"\n{'#'*60}")
    print(f"  COLLECTION COMPLETE")
    print(f"{'#'*60}")
    
    total_items = 0
    for label, items in results.items():
        count = len(items)
        total_items += count
        print(f"   {label}: {count} items")
    
    print(f"\n   TOTAL: {total_items} items collected")
    print(f"{'#'*60}\n")
    
    return results


if __name__ == "__main__":
    if not APIFY_TOKEN:
        print("Error: APIFY_API_TOKEN environment variable not set!")
        print("   Set it with: export APIFY_API_TOKEN='your_token_here'")
        exit(1)
    
    print("\n" + "="*60)
    print("  TRAINING DATA COLLECTION")
    print("  Goal: Collect diverse dataset for engagement prediction model")
    print("="*60 + "\n")
    
    
    training_batch = [
        {'label': 'fitness', 'hashtags': PRESET_COLLECTIONS['fitness'], 'count': 200},
        {'label': 'food', 'hashtags': PRESET_COLLECTIONS['food'], 'count': 200},
        {'label': 'tech', 'hashtags': PRESET_COLLECTIONS['tech'], 'count': 200},
        {'label': 'lifestyle', 'hashtags': PRESET_COLLECTIONS['lifestyle'], 'count': 200},
        {'label': 'education', 'hashtags': PRESET_COLLECTIONS['education'], 'count': 200}
    ]
    
    print("Collecting 1000 TikTok videos across 5 categories...")
    print("   This will take approximately 10-15 minutes\n")
    
    results = collect_batch(training_batch, platform='tiktok')
    
    print("\nTraining data collection complete!")
    print("Data saved in: data/raw/tiktok/")
    print("\nNext steps:")
    print("1. Run: python src/data/ingest_engagement_data.py")
    print("2. This will process all JSONs into: data/processed/tiktok_training.csv")
    print("3. Then you can start building your engagement prediction model!")