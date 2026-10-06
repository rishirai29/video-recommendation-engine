from app.cache import TTLCache


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def test_stores_and_returns_value():
    c = TTLCache()
    c.set("a", [1, 2])
    assert c.get("a") == [1, 2]


def test_missing_key_returns_none():
    assert TTLCache().get("nope") is None


def test_entry_expires_after_ttl():
    clock = FakeClock()
    c = TTLCache(ttl_seconds=10, clock=clock)
    c.set("a", "x")
    clock.now = 9.9
    assert c.get("a") == "x"
    clock.now = 10.1
    assert c.get("a") is None


def test_least_recently_used_is_evicted():
    c = TTLCache(max_entries=2)
    c.set("a", 1)
    c.set("b", 2)
    c.get("a")          # "a" is now more recently used than "b"
    c.set("c", 3)       # cache is full, so "b" is dropped
    assert c.get("b") is None
    assert c.get("a") == 1 and c.get("c") == 3


def test_hit_and_miss_counts():
    c = TTLCache()
    c.set("a", 1)
    c.get("a")
    c.get("missing")
    s = c.stats()
    assert s["hits"] == 1 and s["misses"] == 1
