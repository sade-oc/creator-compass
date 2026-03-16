"""
Performance Benchmarking Script for M1 and M2 Modules
Runs M1 and M2 pipelines 5 times each and generates CSV report with statistics
"""

import sys
import os
import time
import csv
import statistics
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data.fetch_twitter_apify import fetch_twitter_trends
from src.pipelines.nlp_processor import process_trend_nlp
from src.pipelines.content_ideation import generate_content_ideas


def run_m1_benchmark(run_number):
    """Run M1 pipeline (Trend Discovery: fetch + categorize)"""
    print(f"\n[M1 Run {run_number}/5] Starting...", flush=True)
    
    start = time.perf_counter()
    apify_token = os.getenv("APIFY_API_TOKEN")
    
    try:
        # Fetch 10 trends from Twitter
        trends = fetch_twitter_trends(apify_token=apify_token, max_trends=10, fetch_tweets=False)
        
        # Categorize 3 sample trends with NLP
        sample_trends = [
            {"text": "AI and machine learning revolutionizing software development"},
            {"text": "New gaming console announcement sparks excitement"},
            {"text": "Fitness trends 2026: Personalized workout apps dominate"},
        ]
        
        for trend in sample_trends:
            process_trend_nlp(trend)
        
        elapsed = time.perf_counter() - start
        print(f"   └─ Completed in {elapsed:.2f}s", flush=True)
        return elapsed, True
        
    except Exception as e:
        elapsed = time.perf_counter() - start
        print(f"   └─ Failed after {elapsed:.2f}s: {str(e)[:50]}", flush=True)
        return elapsed, False


def run_m2_benchmark(run_number):
    """Run M2 pipeline (Content Ideation: generate ideas)"""
    print(f"\n[M2 Run {run_number}/5] Starting...", flush=True)
    
    start = time.perf_counter()
    
    try:
        # Generate 3 ideas for "AI in education" trend
        ideas_result = generate_content_ideas(
            trend_topic="AI in education",
            niche="Tech/Gaming",
            platform="TikTok",
            num_variations=3
        )
        
        elapsed = time.perf_counter() - start
        print(f"   └─ Completed in {elapsed:.2f}s", flush=True)
        return elapsed, True
        
    except Exception as e:
        elapsed = time.perf_counter() - start
        print(f"   └─ Failed after {elapsed:.2f}s: {str(e)[:50]}", flush=True)
        return elapsed, False


def run_benchmarks():
    """Run all performance benchmarks and generate CSV report"""
    
    print("=" * 80)
    print("CREATOR COMPASS - PERFORMANCE BENCHMARKING (5 RUNS)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Check for Apify token
    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        print("\n⚠️  ERROR: APIFY_API_TOKEN not set in environment")
        print("   Set the token to benchmark M1 trend fetching")
        return
    
    # Performance targets (from PDD)
    targets = {
        "M1_time_seconds": 60.0,
        "M2_time_seconds": 15.0,
        "E2E_time_seconds": 90.0
    }
    
    # Run M1 benchmark 5 times
    print("\n" + "=" * 80)
    print("M1: TREND DISCOVERY (5 RUNS)")
    print("=" * 80)
    
    m1_times = []
    for i in range(1, 6):
        elapsed, success = run_m1_benchmark(i)
        if success:
            m1_times.append(elapsed)
        else:
            m1_times.append(None)
    
    # Run M2 benchmark 5 times
    print("\n" + "=" * 80)
    print("M2: CONTENT IDEATION (5 RUNS)")
    print("=" * 80)
    
    m2_times = []
    for i in range(1, 6):
        elapsed, success = run_m2_benchmark(i)
        if success:
            m2_times.append(elapsed)
        else:
            m2_times.append(None)
    
    # Calculate end-to-end times
    print("\n" + "=" * 80)
    print("E2E: END-TO-END WORKFLOW (M1 + M2)")
    print("=" * 80)
    
    e2e_times = []
    for i in range(5):
        if m1_times[i] is not None and m2_times[i] is not None:
            e2e_time = m1_times[i] + m2_times[i]
            e2e_times.append(e2e_time)
            print(f"\nRun {i+1}: M1({m1_times[i]:.2f}s) + M2({m2_times[i]:.2f}s) = {e2e_time:.2f}s")
        else:
            e2e_times.append(None)
            print(f"\nRun {i+1}: FAILED (one or both modules failed)")
    
    # Generate CSV report
    output_file = "/Users/sadeoc/Documents/PROJECTS/creator-compass/PERFORMANCE_BENCHMARK_RESULTS.csv"
    
    print("\n" + "=" * 80)
    print("GENERATING CSV REPORT")
    print("=" * 80)
    
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow(["component", "run_1", "run_2", "run_3", "run_4", "run_5", "mean", "std_dev", "target", "status"])
        
        # M1 row
        m1_valid = [t for t in m1_times if t is not None]
        if m1_valid:
            m1_mean = statistics.mean(m1_valid)
            m1_std = statistics.stdev(m1_valid) if len(m1_valid) > 1 else 0.0
            m1_status = "PASS" if m1_mean <= targets["M1_time_seconds"] else "FAIL"
            m1_row = ["M1_time_seconds"] + [f"{t:.1f}" if t else "FAIL" for t in m1_times] + [f"{m1_mean:.2f}", f"{m1_std:.2f}", f"{targets['M1_time_seconds']:.1f}", m1_status]
        else:
            m1_row = ["M1_time_seconds"] + ["FAIL"]*5 + ["N/A", "N/A", f"{targets['M1_time_seconds']:.1f}", "FAIL"]
        writer.writerow(m1_row)
        
        # M2 row
        m2_valid = [t for t in m2_times if t is not None]
        if m2_valid:
            m2_mean = statistics.mean(m2_valid)
            m2_std = statistics.stdev(m2_valid) if len(m2_valid) > 1 else 0.0
            m2_status = "PASS" if m2_mean <= targets["M2_time_seconds"] else "FAIL"
            m2_row = ["M2_time_seconds"] + [f"{t:.1f}" if t else "FAIL" for t in m2_times] + [f"{m2_mean:.2f}", f"{m2_std:.2f}", f"{targets['M2_time_seconds']:.1f}", m2_status]
        else:
            m2_row = ["M2_time_seconds"] + ["FAIL"]*5 + ["N/A", "N/A", f"{targets['M2_time_seconds']:.1f}", "FAIL"]
        writer.writerow(m2_row)
        
        # E2E row
        e2e_valid = [t for t in e2e_times if t is not None]
        if e2e_valid:
            e2e_mean = statistics.mean(e2e_valid)
            e2e_std = statistics.stdev(e2e_valid) if len(e2e_valid) > 1 else 0.0
            e2e_status = "PASS" if e2e_mean <= targets["E2E_time_seconds"] else "FAIL"
            e2e_row = ["E2E_time_seconds"] + [f"{t:.1f}" if t else "FAIL" for t in e2e_times] + [f"{e2e_mean:.2f}", f"{e2e_std:.2f}", f"{targets['E2E_time_seconds']:.1f}", e2e_status]
        else:
            e2e_row = ["E2E_time_seconds"] + ["FAIL"]*5 + ["N/A", "N/A", f"{targets['E2E_time_seconds']:.1f}", "FAIL"]
        writer.writerow(e2e_row)
    
    # Display results
    print(f"\n✅ CSV report saved: PERFORMANCE_BENCHMARK_RESULTS.csv")
    print("\nResults Summary:")
    print("-" * 80)
    
    with open(output_file, "r") as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:
                print(" | ".join(f"{cell:18}" for cell in row))
            else:
                print(" | ".join(f"{cell:18}" for cell in row))
    
    print("\n" + "=" * 80)
    print("PERFORMANCE TARGETS:")
    print("=" * 80)
    print(f"  • M1 (Trend Discovery):     < {targets['M1_time_seconds']}s")
    print(f"  • M2 (Content Ideation):   < {targets['M2_time_seconds']}s")
    print(f"  • E2E (Full Workflow):     < {targets['E2E_time_seconds']}s")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmarks()
