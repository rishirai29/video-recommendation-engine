from app.graph import WatchGraph


def build():
    g = WatchGraph()
    # alice and bob both watched A and B; carol watched A and C; dave watched only D
    for user, vid in [("alice", "A"), ("alice", "B"), ("bob", "A"), ("bob", "B"),
                      ("carol", "A"), ("carol", "C"), ("dave", "D")]:
        g.add_watch(user, vid)
    return g


def test_bfs_ranks_most_co_watched_first():
    recs = build().recommend_bfs("A", limit=5)
    assert [v for v, _ in recs][:2] == ["B", "C"]  # B shared by 2 users, C by 1


def test_start_video_never_recommended():
    g = build()
    assert "A" not in [v for v, _ in g.recommend_bfs("A")]
    assert "A" not in [v for v, _ in g.recommend_dfs("A")]


def test_unknown_video_returns_empty():
    g = build()
    assert g.recommend_bfs("nope") == []
    assert g.recommend_dfs("nope") == []


def test_disconnected_video_not_reached():
    g = build()
    assert "D" not in [v for v, _ in g.recommend_bfs("A")]
    assert "D" not in [v for v, _ in g.recommend_dfs("A")]


def test_dfs_respects_limit_and_is_deterministic():
    g = build()
    assert g.recommend_dfs("A", limit=1) == g.recommend_dfs("A", limit=1)
    assert len(g.recommend_dfs("A", limit=1)) == 1
