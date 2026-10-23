"""Concurrent endpoint test harness; run equally against AWS and Azure."""
import argparse
import concurrent.futures
import json
import statistics
import time
import requests


def request_one(url, timeout, headers):
    started = time.perf_counter()
    try:
        r = requests.get(url, timeout=timeout, headers=headers)
        return {"ok": 200 <= r.status_code < 300, "status": r.status_code,
                "ms": round((time.perf_counter() - started) * 1000, 2)}
    except requests.RequestException as exc:
        return {"ok": False, "status": None,
                "ms": round((time.perf_counter() - started) * 1000, 2), "error": str(exc)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Full HTTPS endpoint including ?city=London")
    parser.add_argument("--requests", type=int, default=20)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--bearer-token", default=None)
    args = parser.parse_args()
    headers = {"Authorization": f"Bearer {args.bearer_token}"} if args.bearer_token else {}
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        futures = [pool.submit(request_one, args.url, args.timeout, headers) for _ in range(args.requests)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    elapsed = time.perf_counter() - start
    latencies = sorted(r["ms"] for r in results)
    successes = sum(r["ok"] for r in results)
    summary = {
        "url": args.url.split("?")[0], "requests": args.requests, "concurrency": args.concurrency,
        "successes": successes, "failures": len(results) - successes,
        "success_rate_pct": round(100 * successes / len(results), 2) if results else 0,
        "wall_time_ms": round(elapsed * 1000, 2),
        "throughput_requests_per_second": round(len(results) / elapsed, 2) if elapsed else None,
        "mean_latency_ms": round(statistics.mean(latencies), 2) if latencies else None,
        "p95_latency_ms": latencies[min(len(latencies)-1, int(0.95 * len(latencies)))] if latencies else None,
        "min_latency_ms": min(latencies) if latencies else None, "max_latency_ms": max(latencies) if latencies else None,
        "results": results
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
