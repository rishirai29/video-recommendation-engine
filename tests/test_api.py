from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def setup_function():
    main.cache.clear()


def test_known_video_returns_recommendations():
    r = client.get("/recommendations/video_1?use_cache=false")
    assert r.status_code == 200
    assert len(r.json()["recommendations"]) == 5


def test_second_request_is_served_from_cache():
    first = client.get("/recommendations/video_1").json()
    second = client.get("/recommendations/video_1").json()
    assert first["cached"] is False
    assert second["cached"] is True
    assert first["recommendations"] == second["recommendations"]


def test_use_cache_false_skips_cache():
    client.get("/recommendations/video_1")
    assert client.get("/recommendations/video_1?use_cache=false").json()["cached"] is False


def test_unknown_video_is_404():
    assert client.get("/recommendations/does_not_exist").status_code == 404


def test_bad_algo_is_rejected():
    assert client.get("/recommendations/video_1?algo=xyz").status_code == 422
