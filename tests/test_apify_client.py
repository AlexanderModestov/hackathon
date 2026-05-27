import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from unittest.mock import patch, MagicMock
import pytest
from apify_client import fetch_trending_reels


def test_fetch_trending_reels_returns_list(monkeypatch):
    monkeypatch.setenv("APIFY_API_TOKEN", "test-token")
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"caption": "Morning workout", "likesCount": 1000, "videoPlayCount": 5000}
    ]
    mock_response.raise_for_status = MagicMock()

    with patch("apify_client.httpx.post", return_value=mock_response):
        result = fetch_trending_reels("fitness")

    assert isinstance(result, list)
    assert result[0]["caption"] == "Morning workout"


def test_fetch_trending_reels_empty(monkeypatch):
    monkeypatch.setenv("APIFY_API_TOKEN", "test-token")
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()

    with patch("apify_client.httpx.post", return_value=mock_response):
        result = fetch_trending_reels("nonexistent")

    assert result == []
