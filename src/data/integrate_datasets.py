#Merges all datasets into a single datset for EDA and model building 

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def calculate_engagement_score(row):
  #Calculate standardized engagement score across platforms
    weights = {
        'likes': 0.10,
        'comments': 0.20,
        'shares': 0.30,
        'saves': 0.40
    }
    
    score = 0
    if pd.notna(row.get('likes')) and row.get('likes') > 0:
        score += weights['likes'] * np.log1p(row['likes'])
    if pd.notna(row.get('comments')) and row.get('comments') > 0:
        score += weights['comments'] * np.log1p(row['comments'])
    if pd.notna(row.get('shares')) and row.get('shares') > 0:
        score += weights['shares'] * np.log1p(row['shares'])
    if pd.notna(row.get('saves')) and row.get('saves') > 0:
        score += weights['saves'] * np.log1p(row['saves'])
    
    return round(score, 4)


def calculate_engagement_rating(score):
   # place engagement score into categorical rating
    if pd.isna(score):
        return 'unknown'
    elif score >= 2.93:
        return 'excellent'
    elif score >= 2.04:
        return 'good'
    elif score >= 1.23:
        return 'average'
    elif score >= 0.67:
        return 'below_average'
    else:
        return 'poor'


def process_tiktok_scraped():
   #Process scraped TikTok dataset
    print("\nProcessing TikTok (scraped) dataset...")
    df = pd.read_csv('data/processed/tiktok_training.csv')
    print(f"   Loaded {len(df)} videos")
    
    # Rename and select columns
    df_processed = pd.DataFrame({
        'content_id': df['content_id'],
        'platform': 'tiktok',
        'category': 'general',  # Not specified in scraped data
        'caption': df['caption'],
        'caption_length': df['caption_length'],
        'hashtag_count': df['hashtag_count'],
        'hashtags': df['hashtags'],
        'duration_sec': df['video_duration'],
        'views': df['views'],
        'likes': df['likes'],
        'comments': df['comments'],
        'shares': df['shares'],
        'saves': df['saves'],
        'engagement_rate': df['engagement_rate'],
        'engagement_score': df['engagement_score'],
        'engagement_rating': df['engagement_rating'],
        'creator_username': df['creator_username'],
        'creator_follower_count': df['creator_follower_count'],
        'creator_verified': df['creator_verified'],
        'posting_hour': df['posting_hour'],
        'posting_day': df['posting_day'],
        'posting_month': df['posting_month'],
        'posting_year': df['posting_year'],
        'sentiment': df['sentiment'],
        'has_emoji': df['has_emoji'],
        'emoji_count': df['emoji_count'],
        'has_call_to_action': df['has_call_to_action'],
        'has_question': df['has_question'],
        'word_count': df['word_count'],
        'trend_label': np.nan,  # Not available
        'data_source': 'scraped_apify'
    })
    
    print(f"   ✓ Processed {len(df_processed)} TikTok videos")
    return df_processed


def process_instagram_kaggle():
  #Process Instagram Kaggle dataset
    print("\n Processing Instagram (Kaggle) dataset...")
    df = pd.read_csv('data/kaggle/Instagram_Analytics.csv')
    print(f"   Loaded {len(df)} posts")
    
    # Parse post_date to extract month/year
    df['post_date_parsed'] = pd.to_datetime(df['post_date'], errors='coerce')
    df['posting_month'] = df['post_date_parsed'].dt.month.fillna(0).astype(int)  # type: ignore
    df['posting_year'] = df['post_date_parsed'].dt.year.fillna(0).astype(int)  # type: ignore
    
    # Map performance labels to engagement ratings
    performance_mapping = {
        'viral': 'excellent',
        'high': 'good',
        'medium': 'average',
        'low': 'below_average',
        'poor': 'poor'
    }
    
    df_processed = pd.DataFrame({
        'content_id': 'ig_' + df['post_id'].astype(str),
        'platform': 'instagram',
        'category': df['content_category'],
        'caption': np.nan,  # Not available
        'caption_length': df['caption_length'],
        'hashtag_count': df['hashtags_count'],
        'hashtags': np.nan,  # Not available
        'duration_sec': np.nan,  # Not video-specific
        'views': df['reach'],  # Use reach as proxy for views
        'likes': df['likes'],
        'comments': df['comments'],
        'shares': df['shares'],
        'saves': df['saves'],
        'engagement_rate': df['engagement_rate'],
        'engagement_score': np.nan,  # Will calculate
        'engagement_rating': df['performance_bucket_label'].map(performance_mapping),
        'creator_username': df['account_id'],
        'creator_follower_count': df['follower_count'],
        'creator_verified': np.nan,  # Not available
        'posting_hour': df['post_hour'],
        'posting_day': df['day_of_week'],  # Using day_of_week from source
        'posting_month': df['posting_month'],
        'posting_year': df['posting_year'],
        'sentiment': np.nan,  # Not available
        'has_emoji': np.nan,
        'emoji_count': np.nan,
        'has_call_to_action': df['has_call_to_action'],
        'has_question': np.nan,
        'word_count': np.nan,
        'trend_label': np.nan,
        'data_source': 'kaggle_instagram'
    })
    
    # Calculate engagement score for rows missing it
    print("   Calculating engagement scores...")
    df_processed['engagement_score'] = df_processed.apply(calculate_engagement_score, axis=1)
    
    print(f"   ✓ Processed {len(df_processed)} Instagram posts")
    return df_processed


def process_cross_platform_kaggle():
    #Process TikTok+YouTube Kaggle dataset
    print("\nProcessing TikTok+YouTube (Kaggle) dataset...")
    df = pd.read_csv('data/kaggle/youtube_shorts_tiktok_trends_2025.csv')
    print(f"   Loaded {len(df)} videos")
    
    # Parse approximate dates if needed - wrap in fillna to avoid type errors
    df['publish_date_approx'] = pd.to_datetime(df['publish_date_approx'], errors='coerce')
    df['posting_day_parsed'] = df['publish_date_approx'].dt.day.fillna(0).astype(int)  # type: ignore
    df['posting_month_parsed'] = df['publish_date_approx'].dt.month.fillna(0).astype(int)  # type: ignore
    df['posting_year_parsed'] = df['publish_date_approx'].dt.year.fillna(0).astype(int)  # type: ignore
    
    df_processed = pd.DataFrame({
        'content_id': df['row_id'],
        'platform': df['platform'].str.lower(),  # tiktok or youtube
        'category': df['category'],
        'caption': df['title'],
        'caption_length': df['title_length'],
        'hashtag_count': df['hashtag'].notna().astype(int),  # Binary: has hashtag
        'hashtags': df['hashtag'],
        'duration_sec': df['duration_sec'],
        'views': df['views'],
        'likes': df['likes'],
        'comments': df['comments'],
        'shares': df['shares'],
        'saves': df['saves'],
        'engagement_rate': df['engagement_rate'],
        'engagement_score': np.nan,  # Will calculate
        'engagement_rating': np.nan,  # Will calculate
        'creator_username': df['author_handle'],
        'creator_follower_count': np.nan,  # Not directly available
        'creator_verified': np.nan,
        'posting_hour': df['upload_hour'],
        'posting_day': df.get('publish_dayofweek', df['posting_day_parsed']),
        'posting_month': df['posting_month_parsed'],
        'posting_year': df['posting_year_parsed'],
        'sentiment': np.nan,
        'has_emoji': df['has_emoji'],
        'emoji_count': np.nan,
        'has_call_to_action': np.nan,
        'has_question': np.nan,
        'word_count': np.nan,
        'trend_label': df['trend_label'],
        'data_source': 'kaggle_cross_platform'
    })
    
    # Calculate engagement score and rating
    print("   Calculating engagement scores and ratings...")
    df_processed['engagement_score'] = df_processed.apply(calculate_engagement_score, axis=1)
    df_processed['engagement_rating'] = df_processed['engagement_score'].apply(calculate_engagement_rating)
    
    print(f"   ✓ Processed {len(df_processed)} cross-platform videos")
    return df_processed


def integrate_datasets():
    """Main integration function"""
    print("=" * 70)
    print("DATASET INTEGRATION PIPELINE")
    print("=" * 70)
    
    # Process each dataset
    tiktok_df = process_tiktok_scraped()
    instagram_df = process_instagram_kaggle()
    cross_platform_df = process_cross_platform_kaggle()
    
    # Combine all datasets
    print("\nCombining all datasets...")
    combined_df = pd.concat([tiktok_df, instagram_df, cross_platform_df], ignore_index=True)
    print(f"   Total records: {len(combined_df)}")
    
    # Data quality report
    print("\nData Quality Report:")
    print(f"   Platform distribution:")
    print(combined_df['platform'].value_counts().to_string())
    print(f"\n   Engagement rating distribution:")
    print(combined_df['engagement_rating'].value_counts().to_string())
    print(f"\n   Missing values (top 10):")
    missing_pct = (combined_df.isnull().sum() / len(combined_df) * 100).sort_values(ascending=False).head(10)
    for col, pct in missing_pct.items():
        print(f"   {col}: {pct:.1f}%")
    
    # Save integrated dataset
    output_path = 'data/processed/combined_training.csv'
    print(f"\nSaving integrated dataset to {output_path}...")
    combined_df.to_csv(output_path, index=False)
    print(f"   ✓ Saved {len(combined_df)} records")
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("INTEGRATION COMPLETE")
    print("=" * 70)
    print(f"Final dataset: {len(combined_df)} videos/posts")
    print(f"Platforms: {combined_df['platform'].nunique()}")
    print(f"Features: {len(combined_df.columns)}")
    print(f"Output: {output_path}")
    print("=" * 70)
    
    return combined_df


if __name__ == '__main__':
    df = integrate_datasets()
