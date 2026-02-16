#Conversts JSON data into a training ready CSV format 

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.feature_engineering import (
    extract_text_features,
    extract_hashtags,
    extract_time_features,
    calculate_engagement_rate
)

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Platform-specific engagement weights
PLATFORM_WEIGHTS = {
    'tiktok': {
      # based off of tiktoks point system 
      'likes': 0.10,      # 1 point - basic engagement
      'comments': 0.20,   # 2 points - deeper engagement
      'shares': 0.30,     # 3 points - viral indicator
      'saves': 0.40,      # 4-5 points - rewatch/completion intent (highest value)
    },
    'youtube': {
        'likes': 0.25,
        'comments': 0.30,
        'view_engagement_rate': 0.45
    },
    'instagram': {
        'likes': 0.60,
        'comments': 0.40
    }
}


def transform_tiktok_data(raw_json_path: str) -> pd.DataFrame:
  
    print(f"Loading {raw_json_path}...")
    
    with open(raw_json_path, 'r') as f:
        data = json.load(f)
    
    print(f"   Found {len(data)} videos")
    
    transformed_data = []
    
    for item in data:
        try:
            # Basic content info
            record = {
                'content_id': item.get('id', ''),
                'platform': 'tiktok',
                'url': item.get('webVideoUrl', ''),
            }
            
            # Caption and text features
            caption = item.get('text', '')
            record['caption'] = caption
            text_features = extract_text_features(caption)
            record.update(text_features)
            
            # Hashtags
            hashtags = item.get('hashtags', [])
            hashtag_features = extract_hashtags(hashtags)
            record.update(hashtag_features)
            
            # Video metadata
            video_meta = item.get('videoMeta', {})
            record['video_duration'] = video_meta.get('duration', 0)
            
            # Engagement metrics
            record['likes'] = item.get('diggCount', 0)
            record['comments'] = item.get('commentCount', 0)
            record['shares'] = item.get('shareCount', 0)
            record['saves'] = item.get('collectCount', 0)
            record['views'] = item.get('playCount', 0)
            
            # Creator info
            author_meta = item.get('authorMeta', {})
            record['creator_username'] = author_meta.get('name', '')
            record['creator_follower_count'] = author_meta.get('fans', 0)
            record['creator_verified'] = author_meta.get('verified', False)
            
            # Time features
            timestamp = item.get('createTimeISO', '')
            time_features = extract_time_features(timestamp)
            record.update(time_features)
            
            # Additional metrics
            record['engagement_rate'] = calculate_engagement_rate(
                record['likes'], record['comments'], record['shares'],
                record['saves'], record['views']
            )
            
            transformed_data.append(record)
            
        except Exception as e:
            print(f" Error processing item {item.get('id', 'unknown')}: {e}")
            continue
    
    df = pd.DataFrame(transformed_data)
    print(f" Transformed {len(df)} videos successfully")
    
    return df


def calculate_engagement_score(df: pd.DataFrame, platform: str = 'tiktok') -> pd.DataFrame:
    weights = PLATFORM_WEIGHTS.get(platform, PLATFORM_WEIGHTS['tiktok'])
    
    if platform == 'tiktok':
        # Avoid division by zero
        df['engagement_score'] = df.apply(
            lambda row: (
                (row['likes'] * weights['likes'] +
                 row['comments'] * weights['comments'] +
                 row['shares'] * weights['shares'] +
                 row['saves'] * weights['saves']) / 
                max(row['views'], 1) * 100
            ) if row['views'] > 0 else 0,
            axis=1
        )
    elif platform == 'youtube':
        df['engagement_score'] = df.apply(
            lambda row: (
                (row['likes'] * weights['likes'] +
                 row['comments'] * weights['comments'] +
                 row['engagement_rate'] * weights['view_engagement_rate'])
            ),
            axis=1
        )
    elif platform == 'instagram':
        df['engagement_score'] = df.apply(
            lambda row: (
                (row['likes'] * weights['likes'] +
                 row['comments'] * weights['comments']) / 
                max(row.get('views', row.get('creator_follower_count', 1)), 1) * 100
            ),
            axis=1
        )
    
    # Cap at 100
    df['engagement_score'] = df['engagement_score'].clip(upper=100)
    
    # Add engagement rating (adjusted for realistic engagement rates)
    def get_rating(score):
        if score >= 2.93:           # Top 10% (95th percentile)
            return 'excellent'
        elif score >= 2.04:         # Top 25% (75th percentile)
            return 'good'
        elif score >= 1.23:         # Above median (50th percentile)
            return 'average'
        elif score >= 0.67:         # Above bottom 25%
            return 'below_average'
        else:                       # Bottom 25%
            return 'poor'
    
    df['engagement_rating'] = df['engagement_score'].apply(get_rating)
    
    return df


def process_all_raw_files(raw_data_dir: str, platform: str = 'tiktok') -> pd.DataFrame:
    """
    Process all raw JSON files in a directory
    
    Args:
        raw_data_dir: Directory containing raw JSON files
        platform: Platform name
        
    Returns:
        Combined DataFrame with all processed data
    """
    raw_path = PROJECT_ROOT / raw_data_dir
    
    print(f"\n{'='*60}")
    print(f"Processing all {platform.upper()} files from: {raw_path}")
    print(f"{'='*60}\n")
    
    # Find all JSON files
    json_files = list(raw_path.glob('*.json'))
    
    if not json_files:
        print(f" No JSON files found in {raw_path}")
        return pd.DataFrame()
    
    print(f"Found {len(json_files)} JSON files\n")
    
    all_dfs = []
    
    for json_file in json_files:
        df = pd.DataFrame()
        if platform == 'tiktok':
            df = transform_tiktok_data(str(json_file))
        # Add other platforms here later

        if not df.empty:
            all_dfs.append(df)
    
    # Combine all dataframes
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    print(f"\n{'='*60}")
    print(f"Combined dataset: {len(combined_df)} total videos")
    print(f"{'='*60}")
    
    # Remove duplicates based on content_id
    original_count = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['content_id'], keep='first')
    duplicates_removed = original_count - len(combined_df)
    
    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed} duplicate videos")
    
    # Calculate engagement scores
    print(f"\nCalculating engagement scores...")
    combined_df = calculate_engagement_score(combined_df, platform)
    
    return combined_df


if __name__ == "__main__":
    # Test with existing data
    print("TEST MODE: Processing TikTok data\n")
    
    # Process all TikTok files
    df = process_all_raw_files('data/raw/tiktok', platform='tiktok')
    
    if len(df) > 0:
        # Display summary
        print("\n" + "="*60)
        print("DATASET SUMMARY")
        print("="*60)
        print(f"Total videos: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"\nEngagement score distribution:")
        print(df['engagement_rating'].value_counts())
        print(f"\nMissing values:")
        print(df.isnull().sum()[df.isnull().sum() > 0])
        
        print(f"\nFirst few rows:")
        print(df[['content_id', 'caption_length', 'likes', 'views', 'engagement_score', 'engagement_rating']].head())
        
        # Save to CSV
        output_path = PROJECT_ROOT / 'data/processed/tiktok_training.csv'
        df.to_csv(output_path, index=False)
        print(f"\nSaved training data to: {output_path}")
        print(f"   Shape: {df.shape}")
    else:
        print("No data processed")