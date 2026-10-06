"""A small in-memory cache with expiry (TTL) and least-recently-used (LRU) eviction.

- TTL: an entry older than `ttl_seconds` is treated as missing, so answers do not go stale forever.
- LRU: when the cache is full, the entry that was used longest ago is removed first.
- A lock makes it safe to use from several request threads at once.
"""
import time
from collections import OrderedDict
from threading import Lock


class TTLCache:
    def __init__(self, max_entries=1000, ttl_seconds=300, clock=time.monotonic):
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self._clock = clock
        self._data = OrderedDict()  # key -> (expires_at, value), oldest-used first
        self._lock = Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        with self._lock:
            item = self._data.get(key)
            if item is not None:
                expires_at, value = item
                if self._clock() < expires_at:
                    self._data.move_to_end(key)  # mark as recently used
                    self.hits += 1
                    return value
                del self._data[key]  # expired
            self.misses += 1
            return None

    def set(self, key, value):
        with self._lock:
            self._data[key] = (self._clock() + self.ttl_seconds, value)
            self._data.move_to_end(key)
            while len(self._data) > self.max_entries:
                self._data.popitem(last=False)  # drop least recently used

    def clear(self):
        with self._lock:
            self._data.clear()
            self.hits = 0
            self.misses = 0

    def stats(self):
        with self._lock:
            return {"size": len(self._data), "max_entries": self.max_entries,
                    "ttl_seconds": self.ttl_seconds, "hits": self.hits, "misses": self.misses}
