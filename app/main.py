"""REST API: GET /recommendations/{video_id}, with an in-memory TTL/LRU cache."""
import os
import time

from fastapi import FastAPI, HTTPException, Query

from app.cache import TTLCache
from app.graph import load_graph

DATA_FILE = os.getenv("DATA_FILE", "data/watch_history.json")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
CACHE_MAX_ENTRIES = int(os.getenv("CACHE_MAX_ENTRIES", "1000"))

app = FastAPI(title="Video Recommendation Engine")
graph = load_graph(DATA_FILE)
cache = TTLCache(max_entries=CACHE_MAX_ENTRIES, ttl_seconds=CACHE_TTL_SECONDS)


@app.get("/health")
def health():
    return {"status": "ok", "cache": cache.stats()}


@app.get("/recommendations/{video_id}")
def recommendations(
    video_id: str,
    algo: str = Query("bfs", pattern="^(bfs|dfs)$"),
    limit: int = Query(5, ge=1, le=20),
    use_cache: bool = True,
):
    started = time.perf_counter()
    if not graph.has_video(video_id):
        raise HTTPException(status_code=404, detail=f"Unknown video: {video_id}")

    key = f"rec:{algo}:{video_id}:{limit}"
    if use_cache:
        hit = cache.get(key)
        if hit is not None:
            return {"video_id": video_id, "algo": algo, "cached": True,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                    "recommendations": hit}

    compute = graph.recommend_bfs if algo == "bfs" else graph.recommend_dfs
    results = [{"video_id": vid, "score": score} for vid, score in compute(video_id, limit)]
    if use_cache:
        cache.set(key, results)
    return {"video_id": video_id, "algo": algo, "cached": False,
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "recommendations": results}
