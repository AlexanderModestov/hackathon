import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from build_tov import filter_recent, normalize_location

def test_filter_recent_keeps_2024_posts():
    posts = [
        {"timestamp": "2024-03-15T10:00:00.000Z", "caption": "hello"},
        {"timestamp": "2023-12-31T23:59:00.000Z", "caption": "old"},
        {"timestamp": "2026-01-01T00:00:00.000Z", "caption": "new"},
    ]
    result = filter_recent(posts)
    assert len(result) == 2
    assert all(p["timestamp"] >= "2024-01-01" for p in result)

def test_filter_recent_excludes_pre_2024():
    posts = [{"timestamp": "2023-06-01T00:00:00.000Z", "caption": "old"}]
    result = filter_recent(posts)
    assert result == []

def test_filter_recent_handles_missing_timestamp():
    posts = [{"caption": "no timestamp"}]
    result = filter_recent(posts)
    assert result == []

def test_normalize_location_barcelona():
    result = normalize_location("Barcelona, Spain")
    assert result["city"] == "Barcelona"
    assert result["country"] == "Spain"
    assert result["region_type"] == "home"

def test_normalize_location_europe():
    result = normalize_location("Paris, France")
    assert result["country"] == "France"
    assert result["region_type"] == "travel_europe"

def test_normalize_location_world():
    result = normalize_location("New York City")
    assert result["region_type"] == "travel_world"

def test_normalize_location_russia():
    result = normalize_location("Moscow, Russia")
    assert result["region_type"] == "russia_past"

def test_normalize_location_none():
    assert normalize_location(None) is None

def test_normalize_location_andorra():
    result = normalize_location("Andorra")
    assert result["region_type"] == "travel_europe"

from build_tov import tag_post

def test_tag_post_micro():
    post = {"caption": "On a bluebird day", "locationName": None}
    result = tag_post(post)
    assert result["length_type"] == "micro"

def test_tag_post_short():
    post = {"caption": "Details\n\nBadalona\nSeptember, 2025", "locationName": None}
    result = tag_post(post)
    assert result["length_type"] == "short"

def test_tag_post_medium():
    post = {"caption": "а" * 150, "locationName": None}
    result = tag_post(post)
    assert result["length_type"] == "medium"

def test_tag_post_long():
    post = {"caption": "а" * 400, "locationName": None}
    result = tag_post(post)
    assert result["length_type"] == "long"

def test_tag_post_language_ru():
    post = {"caption": "Живу в Барселоне", "locationName": None}
    result = tag_post(post)
    assert result["language"] == "ru"

def test_tag_post_language_en():
    post = {"caption": "Living in Barcelona now", "locationName": None}
    result = tag_post(post)
    assert result["language"] == "en"

def test_tag_post_emoji_count():
    post = {"caption": "Hello 🌸 world 🌿", "locationName": None}
    result = tag_post(post)
    assert result["emoji_count"] == 2

def test_tag_post_topic_travel():
    post = {"caption": "поездка в горы была чудесной", "locationName": None}
    result = tag_post(post)
    assert result["topic"] == "travel"

def test_tag_post_topic_people():
    post = {"caption": "мы с другом гуляли вместе", "locationName": None}
    result = tag_post(post)
    assert result["topic"] == "people"

def test_tag_post_topic_reflection():
    post = {"caption": "думаю о том, как изменилась жизнь", "locationName": None}
    result = tag_post(post)
    assert result["topic"] == "reflection"

def test_tag_post_topic_daily_life_fallback():
    post = {"caption": "просто хороший день", "locationName": None}
    result = tag_post(post)
    assert result["topic"] == "daily_life"

def test_tag_post_no_caption():
    post = {"caption": None, "locationName": None}
    result = tag_post(post)
    assert result["length_type"] == "micro"
    assert result["emoji_count"] == 0

from build_tov import build_summary

SAMPLE_TAGGED = [
    {"caption": "Живу в Барселоне", "length_type": "short", "language": "ru",
     "topic": "daily_life", "emoji_count": 0, "has_location": True,
     "location": {"raw": "Barcelona, Spain", "city": "Barcelona", "country": "Spain", "region_type": "home"}},
    {"caption": "On a bluebird day", "length_type": "micro", "language": "en",
     "topic": "travel", "emoji_count": 0, "has_location": False, "location": None},
    {"caption": "думаю о жизни " * 10, "length_type": "long", "language": "ru",
     "topic": "reflection", "emoji_count": 1, "has_location": True,
     "location": {"raw": "Paris, France", "city": "Paris", "country": "France", "region_type": "travel_europe"}},
]

def test_build_summary_keys():
    summary = build_summary(SAMPLE_TAGGED)
    assert "style_patterns" in summary
    assert "voice_characteristics" in summary
    assert "places" in summary

def test_build_summary_language_mix():
    summary = build_summary(SAMPLE_TAGGED)
    mix = summary["style_patterns"]["language_mix"]
    assert "ru" in mix and "en" in mix
    assert abs(sum(mix.values()) - 1.0) < 0.01

def test_build_summary_places():
    summary = build_summary(SAMPLE_TAGGED)
    assert "Barcelona" in summary["places"]["home"]
    assert "Paris" in summary["places"]["travel_europe"]

def test_build_summary_voice_characteristics():
    summary = build_summary(SAMPLE_TAGGED)
    vc = summary["voice_characteristics"]
    assert "micro" in vc
    assert "On a bluebird day" in vc["micro"]

import json, tempfile, pathlib
from build_tov import run_pipeline

def test_run_pipeline_produces_valid_json(tmp_path):
    posts = [
        {
            "timestamp": "2025-06-01T10:00:00.000Z",
            "caption": "Small reminder to myself that I live in Spain now",
            "locationName": "Barcelona, Spain",
            "url": "https://www.instagram.com/p/test1/",
            "likesCount": 90,
        },
        {
            "timestamp": "2023-01-01T10:00:00.000Z",
            "caption": "Old post",
            "locationName": None,
            "url": "https://www.instagram.com/p/old/",
            "likesCount": 10,
        },
    ]
    input_path = tmp_path / "posts.json"
    input_path.write_text(json.dumps(posts))
    out_json = tmp_path / "tov.json"
    out_csv = tmp_path / "tov.csv"

    run_pipeline(str(input_path), str(out_json), str(out_csv))

    data = json.loads(out_json.read_text())
    assert "profile_summary" in data
    assert "posts" in data
    assert len(data["posts"]) == 1
    assert data["posts"][0]["date"] == "2025-06-01"
    assert out_csv.exists()
