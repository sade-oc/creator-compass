# Merges Kaggle datasets into a single dataset for EDA and model training.
# Uses NATIVE engagement_rate from both sources — no computed scores.

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ── Column schema ──
# The output CSV will have these columns in this order:
#
# IDENTIFIERS:      content_id, data_source
# INDEPENDENT VARS: platform, category, caption_length, hashtag_count,
#                   posting_hour, posting_day, is_weekend,
#                   duration_sec*, has_emoji*, has_trend*, trend_label*,
#                   season*, has_call_to_action*, media_type*
#                   (* = platform-specific, NaN where unavailable)
# EDA METRICS:      views, likes, comments, shares, saves
# TARGET VARS:      engagement_rate (continuous), engagement_rating (categorical)


def assign_engagement_rating(df):
    #Assign engagement rating using quintile bins of native engagement_rate.

    rate = df['engagement_rate']
    
    p20 = rate.quantile(0.20)
    p40 = rate.quantile(0.40)
    p60 = rate.quantile(0.60)
    p80 = rate.quantile(0.80)
    
    conditions = [
        rate >= p80,
        rate >= p60,
        rate >= p40,
        rate >= p20,
    ]
    choices = ['excellent', 'good', 'average', 'below_average']
    
    df['engagement_rating'] = np.select(conditions, choices, default='poor')
    
    print(f"   Rating thresholds (from native engagement_rate):")
    print(f"     excellent:   >= {p80:.4f} (top 20%)")
    print(f"     good:        >= {p60:.4f} (60th–80th percentile)")
    print(f"     average:     >= {p40:.4f} (40th–60th percentile)")
    print(f"     below_avg:   >= {p20:.4f} (20th–40th percentile)")
    print(f"     poor:        <  {p20:.4f} (bottom 20%)")
    
    return df


def process_instagram_kaggle():
    # Process Instagram Kaggle dataset.
    print("\nProcessing Instagram (Kaggle) dataset...")
    df = pd.read_csv('data/kaggle/Instagram_Analytics.csv')
    print(f"   Loaded {len(df)} posts")
    
    # Parse dates for temporal features
    df['post_date_parsed'] = pd.to_datetime(df['post_date'], errors='coerce')
    
    # Map day names to standardised format if needed
    day_mapping = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
                   4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    
    df_processed = pd.DataFrame({
        # Identifiers
        'content_id': 'ig_' + df['post_id'].astype(str),
        'data_source': 'kaggle_instagram',
        
        # Independent variables (universal)
        'platform': 'instagram',
        'category': df['content_category'].str.lower().str.strip(),
        'caption_length': df['caption_length'],
        'hashtag_count': df['hashtags_count'],
        'posting_hour': df['post_hour'],
        'posting_day': df['day_of_week'],
        
        # Independent variables (only for tiktok and youtube datasets, NaN for Instagram)
        'duration_sec': np.nan,
        'has_emoji': np.nan,
        'trend_label': np.nan,
        'season': np.nan,
        'has_call_to_action': df['has_call_to_action'],
        'media_type': df['media_type'] if 'media_type' in df.columns else np.nan,
        
        # EDA metrics
        'views': df['reach'],  # reach as proxy for views
        'likes': df['likes'],
        'comments': df['comments'],
        'shares': df['shares'],
        'saves': df['saves'],
        
        # Target (native)
        'engagement_rate': df['engagement_rate'],
    })
    
    print(f"   Processed {len(df_processed)} Instagram posts")
    print(f"   engagement_rate: min={df_processed['engagement_rate'].min():.4f}, "
          f"max={df_processed['engagement_rate'].max():.4f}, "
          f"mean={df_processed['engagement_rate'].mean():.4f}")
    return df_processed


def process_cross_platform_kaggle():
    #Process TikTok+YouTube Kaggle dataset.
    print("\nProcessing TikTok+YouTube (Kaggle) dataset...")
    df = pd.read_csv('data/kaggle/youtube_shorts_tiktok_trends_2025.csv')
    print(f"   Loaded {len(df)} videos")
    
    df_processed = pd.DataFrame({
        # Identifiers
        'content_id': df['row_id'],
        'data_source': 'kaggle_cross_platform',
        
        # Independent variables (universal)
        'platform': df['platform'].str.lower().str.strip(),
        'category': df['category'].str.lower().str.strip(),
        'caption_length': df['title_length'],
        'hashtag_count': df['hashtag'].notna().astype(int),
        'posting_hour': df['upload_hour'],
        'posting_day': df['publish_dayofweek'],
        
        # Independent variables (platform-specific)
        'duration_sec': df['duration_sec'],
        'has_emoji': df['has_emoji'],
        'trend_label': df['trend_label'].str.lower().str.strip(),
        'season': df['season'].str.lower().str.strip() if 'season' in df.columns else np.nan,
        'has_call_to_action': np.nan,
        'media_type': np.nan,
        
        # EDA metrics
        'views': df['views'],
        'likes': df['likes'],
        'comments': df['comments'],
        'shares': df['shares'],
        'saves': df['saves'],
        
        # Target (native)
        'engagement_rate': df['engagement_rate'],
    })
    
    print(f"   Processed {len(df_processed)} cross-platform videos")
    print(f"   engagement_rate: min={df_processed['engagement_rate'].min():.4f}, "
          f"max={df_processed['engagement_rate'].max():.4f}, "
          f"mean={df_processed['engagement_rate'].mean():.4f}")
    return df_processed


def integrate_datasets():
    #Main integration 
    print("DATASET INTEGRATION PIPELINE")

    print("Sources: Kaggle Instagram + Kaggle TikTok/YouTube")
    print("Target:  Native engagement_rate (no computed scores)")

    
    # Process each dataset
    instagram_df = process_instagram_kaggle()
    cross_platform_df = process_cross_platform_kaggle()
    
    # Combine
    print("\nCombining datasets...")
    combined_df = pd.concat([instagram_df, cross_platform_df], ignore_index=True)
    print(f"   Total records: {len(combined_df)}")
    
    # ── Data cleaning ──
    
    # Drop rows with missing or zero engagement_rate
    before = len(combined_df)
    combined_df = combined_df.dropna(subset=['engagement_rate'])
    combined_df = combined_df[combined_df['engagement_rate'] > 0]
    after = len(combined_df)
    if before != after:
        print(f"   Dropped {before - after} rows with missing/zero engagement_rate")
    
    # ── Derived features ──
    
    # has_trend: binary flag from trend_label
    combined_df['has_trend'] = combined_df['trend_label'].apply(
        lambda x: 1 if pd.notna(x) and str(x).strip() != '' else 0
    )
    
    # is_weekend: derived from posting_day
    weekend_days = ['saturday', 'sunday']
    combined_df['is_weekend'] = combined_df['posting_day'].apply(
        lambda x: 1 if pd.notna(x) and str(x).strip().lower() in weekend_days else 0
    )
    
    # Normalise category names
    combined_df['category'] = combined_df['category'].fillna('unknown')
    
    # ── Assign engagement ratings from native distribution ──
    print("\nAssigning engagement ratings from native distribution...")
    combined_df = assign_engagement_rating(combined_df)
    
    # ── Reorder columns to match agreed schema ──
    column_order = [
        # Identifiers
        'content_id', 'data_source',
        # Independent variables (universal)
        'platform', 'category', 'caption_length', 'hashtag_count',
        'posting_hour', 'posting_day', 'is_weekend',
        # Independent variables (platform-specific)
        'duration_sec', 'has_emoji', 'has_trend', 'trend_label',
        'season', 'has_call_to_action', 'media_type',
        # EDA metrics
        'views', 'likes', 'comments', 'shares', 'saves',
        # Targets
        'engagement_rate', 'engagement_rating',
    ]
    combined_df = combined_df[column_order]
    
    # ── Data quality report ──
    print("DATA QUALITY REPORT")
    
    print(f"\n   Platform distribution:")
    for platform, count in combined_df['platform'].value_counts().items():
        print(f"     {platform}: {count:,}")
    
    print(f"\n   Engagement rating distribution:")
    for rating, count in combined_df['engagement_rating'].value_counts().items():
        print(f"     {rating}: {count:,}")
    
    print(f"\n   Engagement rate by platform:")
    for platform in sorted(combined_df['platform'].unique()):
        subset = combined_df[combined_df['platform'] == platform]['engagement_rate']
        print(f"     {platform}: mean={subset.mean():.4f}, median={subset.median():.4f}, "
              f"std={subset.std():.4f}, range=[{subset.min():.4f}, {subset.max():.4f}]")
    
    print(f"\n   has_trend distribution:")
    for val, count in combined_df['has_trend'].value_counts().items():
        print(f"     {val}: {count:,}")
    
    print(f"\n   Missing values:")
    missing_pct = (combined_df.isnull().sum() / len(combined_df) * 100).sort_values(ascending=False)
    for col, pct in missing_pct.items():
        if pct > 0:
            print(f"     {col}: {pct:.1f}%")
    
    # ── Save ──
    output_path = 'data/processed/combined_training.csv'
    print(f"\nSaving to {output_path}...")
    combined_df.to_csv(output_path, index=False)
    
    # ── Summary ──
    print("\n" + "=" * 70)
    print("INTEGRATION COMPLETE")
    print("=" * 70)
    print(f"  Rows:     {len(combined_df):,}")
    print(f"  Columns:  {len(combined_df.columns)}")
    print(f"  Platforms: {list(combined_df['platform'].unique())}")
    print(f"  Target:   engagement_rate [{combined_df['engagement_rate'].min():.4f} – {combined_df['engagement_rate'].max():.4f}]")
    print(f"  Output:   {output_path}")
    print("=" * 70)
    
    return combined_df


if __name__ == '__main__':
    df = integrate_datasets()
