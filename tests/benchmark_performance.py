
# Performance Benchmarking Script for M1 and M2 Modules


import sys
import os
import time
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data.fetch_twitter_apify import fetch_twitter_trends, fetch_tweets_for_trend
from src.pipelines.nlp_processor import process_trend_nlp
from src.pipelines.content_ideation import generate_content_ideas, generate_detailed_script
from src.data.niche_config import NICHES



# Measure execution time of an operation
def benchmark_operation(operation_name, func, *args, **kwargs):
    
    print(f"\n[{operation_name}] Starting...", flush=True)
    start_time = time.perf_counter()
    
    try:
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start_time
        status = "PASS"
        print(f"    Completed in {elapsed:.4f}s", flush=True)
        return {
            "operation": operation_name,
            "status": status,
            "time_seconds": round(elapsed, 4),
            "result": str(result)[:100]  
        }
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        status = " FAIL"
        print(f"    Failed after {elapsed:.4f}s: {str(e)[:50]}", flush=True)
        return {
            "operation": operation_name,
            "status": status,
            "time_seconds": round(elapsed, 4),
            "error": str(e)[:100]
        }

# Run all performance benchmarks for M1 and M2 modules
def run_benchmarks():
    
    print("=" * 70)
    print("CREATOR COMPASS - MODULE PERFORMANCE BENCHMARKING")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    results = []
    
    # Check for required environment variables
    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        print("\n  WARNING: APIFY_API_TOKEN not set. M1 trend fetching will be skipped.")
        print("   Set the token in .env to test real trend fetching.\n")
    
    # --- M1: TREND DISCOVERY BENCHMARKS ---
    print("\n" + "=" * 70)
    print("M1: TREND DISCOVERY MODULE PERFORMANCE")
    print("=" * 70)
    
    if apify_token:
        # Benchmark 1: Fetch trending topics
        print("\n[M1-01] Fetching trending topics from Twitter...", flush=True)
        start = time.perf_counter()
        try:
            trends = fetch_twitter_trends(max_trends=10, fetch_tweets=False)
            elapsed = time.perf_counter() - start
            print(f"   └─ Completed in {elapsed:.4f}s | Fetched {len(trends) if isinstance(trends, list) else '?'} trends", flush=True)
            results.append({
                "operation": "M1-01: Fetch trending topics",
                "status": " PASS",
                "time_seconds": round(elapsed, 4),
                "trends_fetched": len(trends) if isinstance(trends, list) else 0
            })
        except Exception as e:
            elapsed = time.perf_counter() - start
            print(f"   └─ Failed after {elapsed:.4f}s: {str(e)[:60]}", flush=True)
            results.append({
                "operation": "M1-01: Fetch trending topics",
                "status": " FAIL",
                "time_seconds": round(elapsed, 4),
                "error": str(e)[:100]
            })
    else:
        print("[M1-01] Skipped (no APIFY_API_TOKEN)")
    
    # Benchmark 2: NLP processing of trends
    print("\n[M1-02] Processing trends with NLP (categorisation)...", flush=True)
    sample_trends = [
        {"text": "AI and machine learning revolutionizing software development", "platform": "twitter"},
        {"text": "New gaming console announcement sparks excitement", "platform": "twitter"},
        {"text": "Fitness trends 2026: Personalized workout apps dominate", "platform": "twitter"},
    ]
    
    start = time.perf_counter()
    try:
        processed_trends = {}
        for trend in sample_trends:
            nlp_result = process_trend_nlp(trend)
            processed_trends[trend["text"]] = nlp_result
        
        elapsed = time.perf_counter() - start
        print(f"   └─ Completed in {elapsed:.4f}s | Processed {len(processed_trends)} trends", flush=True)
        results.append({
            "operation": "M1-02: NLP trend categorisation",
            "status": " PASS",
            "time_seconds": round(elapsed, 4),
            "trends_processed": len(processed_trends),
            "avg_per_trend": round(elapsed / len(processed_trends), 4)
        })
    except Exception as e:
        elapsed = time.perf_counter() - start
        print(f"   └─ Failed after {elapsed:.4f}s: {str(e)[:60]}", flush=True)
        results.append({
            "operation": "M1-02: NLP trend categorisation",
            "status": " FAIL",
            "time_seconds": round(elapsed, 4),
            "error": str(e)[:100]
        })
    
    # --- M2: CONTENT IDEATION BENCHMARKS ---
    print("\n" + "=" * 70)
    print("M2: CONTENT IDEATION MODULE PERFORMANCE")
    print("=" * 70)
    
    # Benchmark 3: Generate content ideas
    print("\n[M2-01] Generating content ideas (single trend)...", flush=True)
    start = time.perf_counter()
    ideas_result = None
    try:
        ideas_result = generate_content_ideas(
            trend_topic="AI in education",
            niche="Tech/Gaming",
            platform="TikTok"
        )
        elapsed = time.perf_counter() - start
        ideas_count = 1 if ideas_result else 0
        print(f"   └─ Completed in {elapsed:.4f}s | Generated idea set", flush=True)
        results.append({
            "operation": "M2-01: Generate content ideas",
            "status": " PASS",
            "time_seconds": round(elapsed, 4),
            "result_keys": list(ideas_result.keys()) if isinstance(ideas_result, dict) else []
        })
    except Exception as e:
        elapsed = time.perf_counter() - start
        print(f"   └─ Failed after {elapsed:.4f}s: {str(e)[:60]}", flush=True)
        results.append({
            "operation": "M2-01: Generate content ideas",
            "status": " FAIL",
            "time_seconds": round(elapsed, 4),
            "error": str(e)[:100]
        })
    
    # Benchmark 4: Generate detailed scripts (only if ideas were generated)
    print("\n[M2-02] Generating detailed video scripts...", flush=True)
    start = time.perf_counter()
    try:
        if ideas_result:
            script = generate_detailed_script(ideas_result)
            elapsed = time.perf_counter() - start
            print(f"   └─ Completed in {elapsed:.4f}s | Generated script", flush=True)
            results.append({
                "operation": "M2-02: Generate detailed script",
                "status": " PASS",
                "time_seconds": round(elapsed, 4),
                "script_keys": list(script.keys()) if isinstance(script, dict) else []
            })
        else:
            elapsed = time.perf_counter() - start
            raise Exception("Skipped - no ideas generated in previous step")
    except Exception as e:
        elapsed = time.perf_counter() - start
        print(f"   └─ Failed after {elapsed:.4f}s: {str(e)[:60]}", flush=True)
        results.append({
            "operation": "M2-02: Generate detailed script",
            "status": " FAIL",
            "time_seconds": round(elapsed, 4),
            "error": str(e)[:100]
        })
    
    # --- SUMMARY AND OUTPUT ---
    print("\n" + "=" * 70)
    print("BENCHMARK RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in results if "PASS" in r.get("status", ""))
    failed = sum(1 for r in results if "FAIL" in r.get("status", ""))
    total_time = sum(r.get("time_seconds", 0) for r in results)
    
    print(f"\nTotal Operations: {len(results)}")
    print(f"Passed: {passed} ")
    print(f"Failed: {failed} ")
    print(f"Total Time: {total_time:.4f} seconds")
    
    # Detailed results
    print("\nDETAILED RESULTS:")
    print("-" * 70)
    for r in results:
        status = r.get("status", "")
        time_val = r.get("time_seconds", 0)
        operation = r.get("operation", "")
        
        # Extract additional metrics
        extras = []
        if "trends_fetched" in r:
            extras.append(f"Fetched: {r['trends_fetched']}")
        if "trends_processed" in r:
            extras.append(f"Processed: {r['trends_processed']}")
            if "avg_per_trend" in r:
                extras.append(f"Avg/trend: {r['avg_per_trend']:.4f}s")
        if "result_keys" in r:
            extras.append(f"Keys: {', '.join(r['result_keys'][:2])}")
        if "script_keys" in r:
            extras.append(f"Keys: {', '.join(r['script_keys'][:2])}")
        if "error" in r:
            extras.append(f"Error: {r['error'][:40]}")
        
        extra_str = " | ".join(extras)
        if extra_str:
            extra_str = " | " + extra_str
        
        print(f"{status} {operation}")
        print(f"   ├─ Time: {time_val:.4f}s{extra_str}")
    
    # Performance targets
    print("\n" + "=" * 70)
    print("PERFORMANCE TARGETS")
    print("=" * 70)
    print("\nBenchmark Goals (from PDD):")
    print("  • M1 Trend Fetching: < 60s for full analysis")
    print("  • M1 NLP Categorisation: < 20s for batch")
    print("  • M2 Idea Generation: < 15s per trend")
    print("  • M2 Script Generation: < 30s per idea")
    
    # Save results to file
    output_file = "/Users/sadeoc/Documents/PROJECTS/creator-compass/PERFORMANCE_RESULTS.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "module": "M1 & M2 Pipeline Performance",
            "total_operations": len(results),
            "passed": passed,
            "failed": failed,
            "total_time_seconds": round(total_time, 4),
            "results": results,
            "targets": {
                "M1_trend_fetching": "< 60s",
                "M1_nlp_categorisation": "< 20s",
                "M2_idea_generation": "< 15s",
                "M2_script_generation": "< 30s"
            }
        }, f, indent=2)
    
    print(f"\n Results saved to: PERFORMANCE_RESULTS.json")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    run_benchmarks()
