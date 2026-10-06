"""Generate SAMPLE watch history (synthetic, not real users) for the demo.

Run:  python scripts/generate_data.py
Creates data/watch_history.json with users who mostly watch videos from a few
favourite categories, so related-video results are meaningful.
"""
import json
import random

random.seed(42)
NUM_USERS, NUM_VIDEOS, NUM_CATEGORIES = 2000, 1000, 10

videos_by_cat = {c: [] for c in range(NUM_CATEGORIES)}
for i in range(1, NUM_VIDEOS + 1):
    videos_by_cat[i % NUM_CATEGORIES].append(f"video_{i}")

watches = []
for u in range(1, NUM_USERS + 1):
    favourites = random.sample(range(NUM_CATEGORIES), 2)
    seen = set()
    for _ in range(random.randint(15, 40)):
        # 85% of the time pick from a favourite category, otherwise anything
        if random.random() < 0.85:
            vid = random.choice(videos_by_cat[random.choice(favourites)])
        else:
            vid = f"video_{random.randint(1, NUM_VIDEOS)}"
        seen.add(vid)
    watches.extend([f"user_{u}", v] for v in sorted(seen))

with open("data/watch_history.json", "w", encoding="utf-8") as f:
    json.dump({"watches": watches}, f)
print(f"Wrote {len(watches)} watch events for {NUM_USERS} users and {NUM_VIDEOS} videos")
