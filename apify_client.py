import os
import httpx
from typing import Any

_ACTOR_ID = "apify~instagram-scraper"


def fetch_trending_reels(hashtag: str) -> list[dict[str, Any]]:
    token = os.environ["APIFY_API_TOKEN"]
    url = f"https://api.apify.com/v2/acts/{_ACTOR_ID}/run-sync-get-dataset-items"
    response = httpx.post(
        url,
        params={"token": token},
        json={"hashtags": [hashtag], "resultsType": "posts", "resultsLimit": 10},
        timeout=60.0,
    )
    response.raise_for_status()
    return response.json()
