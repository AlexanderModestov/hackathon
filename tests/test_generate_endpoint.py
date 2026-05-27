import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import httpx
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

MOCK_REELS = [{"caption": "test", "likesCount": 100, "videoPlayCount": 500}]
MOCK_RESULT = {
    "beat_sheet": {"hook": "h", "conflict": "c", "resolution": "r", "cta": "cta"},
    "script": "[0:00] test",
}


def test_generate_success():
    with patch("main.fetch_trending_reels", return_value=MOCK_REELS), \
         patch("main.generate_script", return_value=MOCK_RESULT):
        response = client.post(
            "/generate",
            json={"hashtag": "fitness", "creator_topic": "gym"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "beat_sheet" in data
    assert "script" in data


def test_generate_empty_reels_returns_400():
    with patch("main.fetch_trending_reels", return_value=[]):
        response = client.post(
            "/generate",
            json={"hashtag": "xyz123notreal", "creator_topic": "test"},
        )

    assert response.status_code == 400
    assert "Хэштег не найден" in response.json()["detail"]


def test_generate_apify_timeout_returns_504():
    with patch("main.fetch_trending_reels", side_effect=httpx.TimeoutException("timeout")):
        response = client.post(
            "/generate",
            json={"hashtag": "fitness", "creator_topic": "test"},
        )

    assert response.status_code == 504


def test_generate_claude_error_returns_502():
    with patch("main.fetch_trending_reels", return_value=MOCK_REELS), \
         patch("main.generate_script", side_effect=Exception("claude error")):
        response = client.post(
            "/generate",
            json={"hashtag": "fitness", "creator_topic": "test"},
        )

    assert response.status_code == 502
