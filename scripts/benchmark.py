"""Measure response time WITHOUT and WITH the in-memory cache.

Start the service first (uvicorn app.main:app --port 8000), then run:  python scripts/benchmark.py
"""
import json
import statistics
import time
import urllib.request

BASE = "http://127.0.0.1:8000"
VIDEO = "video_1"
RUNS = 100


def call(use_cache):
    url = f"{BASE}/recommendations/{VIDEO}?algo=bfs&limit=5&use_cache={str(use_cache).lower()}"
    started = time.perf_counter()
    with urllib.request.urlopen(url) as resp:
        json.loads(resp.read())
    return (time.perf_counter() - started) * 1000


call(False)  # warm-up so one-time start-up costs are not counted
no_cache = [call(False) for _ in range(RUNS)]
call(True)   # first cached call fills the cache
with_cache = [call(True) for _ in range(RUNS)]

avg_no, avg_with = statistics.mean(no_cache), statistics.mean(with_cache)
print(f"Requests per test       : {RUNS}")
print(f"Average WITHOUT cache   : {avg_no:.2f} ms")
print(f"Average WITH cache      : {avg_with:.2f} ms")
print(f"Speed-up                : {avg_no / avg_with:.1f}x faster "
      f"({(1 - avg_with / avg_no) * 100:.0f}% lower response time)")
