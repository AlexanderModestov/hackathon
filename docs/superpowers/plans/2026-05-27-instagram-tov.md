# Instagram Tone of Voice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `build_tov.py` — a script that reads `nadezdi_net_posts.json`, filters posts from 2024 onwards, tags each post with heuristics, and outputs `tone_of_voice.json` + `tone_of_voice.csv` for LLM tone-of-voice prompting.

**Architecture:** Single script with five pure functions (`filter_recent`, `normalize_location`, `tag_post`, `build_summary`, `write_output`) called in sequence. No classes, no external state. Each function is independently testable.

**Tech Stack:** Python 3, stdlib only + `emoji` package. Input: `nadezdi_net_posts.json`. Output: `tone_of_voice.json`, `tone_of_voice.csv`.

---

## File Structure

```
hackathon/
├── build_tov.py               # main script — pipeline entry point
├── tests/
│   └── test_build_tov.py      # all unit tests
├── nadezdi_net_posts.json      # input (already exists)
├── tone_of_voice.json          # output (generated)
└── tone_of_voice.csv           # output (generated)
```

---

### Task 1: `filter_recent` — keep posts from 2024-01-01

**Files:**
- Create: `build_tov.py`
- Create: `tests/test_build_tov.py`

- [ ] **Step 1: Create test file with failing test**

Create `tests/test_build_tov.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from build_tov import filter_recent

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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/alexmodestov/ManyChat/Projects/hackathon
python3 -m pytest tests/test_build_tov.py -v
```

Expected: `ModuleNotFoundError: No module named 'build_tov'`

- [ ] **Step 3: Create `build_tov.py` with `filter_recent`**

Create `build_tov.py`:

```python
import json
import csv
import re
import emoji as emoji_lib
from datetime import date


CUTOFF = "2024-01-01"


def filter_recent(posts: list[dict]) -> list[dict]:
    return [p for p in posts if p.get("timestamp", "") >= CUTOFF]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python3 -m pytest tests/test_build_tov.py::test_filter_recent_keeps_2024_posts tests/test_build_tov.py::test_filter_recent_excludes_pre_2024 tests/test_build_tov.py::test_filter_recent_handles_missing_timestamp -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
cd /Users/alexmodestov/ManyChat/Projects/hackathon
git init
git add build_tov.py tests/test_build_tov.py
git commit -m "feat: add filter_recent — keep posts from 2024-01-01"
```

---

### Task 2: `normalize_location` — parse raw location string

**Files:**
- Modify: `build_tov.py`
- Modify: `tests/test_build_tov.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_build_tov.py`:

```python
from build_tov import normalize_location

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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_build_tov.py -k "normalize_location" -v
```

Expected: `ImportError` or `AttributeError`

- [ ] **Step 3: Implement `normalize_location`**

Append to `build_tov.py`:

```python
EUROPE_KEYWORDS = {
    "france", "germany", "italy", "netherlands", "spain", "portugal",
    "switzerland", "austria", "belgium", "sweden", "norway", "denmark",
    "finland", "poland", "czech", "andorra", "luxembourg", "croatia",
    "greece", "hungary", "romania", "bulgaria", "serbia", "slovakia",
    "leucate", "occitanie", "lyon", "paris", "berlin", "amsterdam",
    "sitges", "badalona", "cataluña", "catalonia", "barcelona",
}

RUSSIA_CIS_KEYWORDS = {
    "russia", "moscow", "санкт", "петербург", "питер", "москва", "псков",
    "россия", "текстильщики", "маросейка", "dombay", "karachayevo",
    "bryanskaya", "ivanovskaya", "kaluga", "dilijan", "georgia",
    "armenia", "kazakhstan", "ukraine", "belarus",
}

HOME_KEYWORDS = {
    "barcelona", "badalona", "cataluña", "catalonia", "sitges",
    "jardín botánico marimurtra",
}


def normalize_location(raw: str | None) -> dict | None:
    if not raw:
        return None

    lower = raw.lower()
    parts = [p.strip() for p in raw.split(",")]
    city = parts[0] if parts else raw
    country = parts[-1].strip() if len(parts) > 1 else ""

    if any(kw in lower for kw in HOME_KEYWORDS):
        region_type = "home"
    elif any(kw in lower for kw in RUSSIA_CIS_KEYWORDS):
        region_type = "russia_past"
    elif any(kw in lower for kw in EUROPE_KEYWORDS):
        region_type = "travel_europe"
    else:
        region_type = "travel_world"

    return {
        "raw": raw,
        "city": city,
        "country": country or "Unknown",
        "region_type": region_type,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_build_tov.py -k "normalize_location" -v
```

Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add build_tov.py tests/test_build_tov.py
git commit -m "feat: add normalize_location — classify raw location strings"
```

---

### Task 3: `tag_post` — length_type, language, topic, emoji_count

**Files:**
- Modify: `build_tov.py`
- Modify: `tests/test_build_tov.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_build_tov.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_build_tov.py -k "tag_post" -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement `tag_post`**

Append to `build_tov.py`:

```python
TOPIC_KEYWORDS = {
    "travel": [
        "поездка", "путешествие", "море", "горы", "город", "flight",
        "страна", "аэропорт", "отель", "поезд", "barcelona", "барселон",
    ],
    "people": ["друг", "подруг", "мы ", "вместе", "люблю", "люблю!"],
    "reflection": [
        "год", "жизнь", "думаю", "чувствую", "понимаю", "стала",
        "раньше", "переехала", "изменил",
    ],
    "humor": ["хехе", " ха ", "забавно", "смешно", "ирони"],
}


def _detect_language(text: str) -> str:
    if not text:
        return "ru"
    alpha = [c for c in text if c.isalpha()]
    if not alpha:
        return "ru"
    cyrillic = sum(1 for c in alpha if "Ѐ" <= c <= "ӿ")
    ratio = cyrillic / len(alpha)
    if ratio > 0.6:
        return "ru"
    if ratio < 0.2:
        return "en"
    return "mixed"


def _detect_topic(text: str) -> str:
    lower = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return topic
    return "daily_life"


def tag_post(post: dict) -> dict:
    caption = post.get("caption") or ""
    length = len(caption)

    if length <= 30:
        length_type = "micro"
    elif length <= 100:
        length_type = "short"
    elif length <= 300:
        length_type = "medium"
    else:
        length_type = "long"

    location_raw = post.get("locationName")
    location = normalize_location(location_raw)

    return {
        "url": post.get("url", ""),
        "date": (post.get("timestamp") or "")[:10],
        "caption": caption,
        "likes": post.get("likesCount", 0),
        "length_type": length_type,
        "language": _detect_language(caption),
        "topic": _detect_topic(caption),
        "has_location": location is not None,
        "location": location,
        "emoji_count": emoji_lib.emoji_count(caption),
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_build_tov.py -k "tag_post" -v
```

Expected: 12 passed

- [ ] **Step 5: Commit**

```bash
git add build_tov.py tests/test_build_tov.py
git commit -m "feat: add tag_post — length, language, topic, emoji tagging"
```

---

### Task 4: `build_summary` — profile_summary block

**Files:**
- Modify: `build_tov.py`
- Modify: `tests/test_build_tov.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_build_tov.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_build_tov.py -k "build_summary" -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement `build_summary`**

Append to `build_tov.py`:

```python
PROFILE = {
    "username": "nadezdi_net",
    "full_name": "Nadezhda",
    "bio": "Живу в Барселоне, пишу код, ухаживаю за зелеными. А завтра посмотрим",
    "home_city": "Barcelona",
}


def build_summary(tagged_posts: list[dict]) -> dict:
    n = len(tagged_posts)
    if n == 0:
        return {}

    captions = [p["caption"] for p in tagged_posts if p["caption"]]
    avg_len = sum(len(c) for c in captions) // max(len(captions), 1)

    lang_counts = {"ru": 0, "en": 0, "mixed": 0}
    for p in tagged_posts:
        lang_counts[p["language"]] = lang_counts.get(p["language"], 0) + 1
    lang_mix = {k: round(v / n, 2) for k, v in lang_counts.items()}

    length_dist = {"micro": 0, "short": 0, "medium": 0, "long": 0}
    for p in tagged_posts:
        length_dist[p["length_type"]] += 1

    topic_counts = {"daily_life": 0, "travel": 0, "people": 0, "reflection": 0, "humor": 0}
    for p in tagged_posts:
        topic_counts[p["topic"]] = topic_counts.get(p["topic"], 0) + 1

    avg_emoji = round(sum(p["emoji_count"] for p in tagged_posts) / n, 2)

    # voice_characteristics: up to 5 real examples per length type, prefer with-caption
    vc: dict[str, list[str]] = {"micro": [], "short": [], "medium": [], "long": []}
    for lt in vc:
        examples = [p["caption"] for p in tagged_posts
                    if p["length_type"] == lt and p["caption"]]
        vc[lt] = examples[:5]

    # places: unique city names per region_type
    places: dict[str, list[str]] = {
        "home": [], "travel_europe": [], "travel_world": [], "russia_past": []
    }
    seen: set[str] = set()
    for p in tagged_posts:
        if p["location"]:
            city = p["location"]["city"]
            rtype = p["location"]["region_type"]
            if city not in seen and rtype in places:
                places[rtype].append(city)
                seen.add(city)

    return {
        "style_patterns": {
            "avg_caption_length": avg_len,
            "language_mix": lang_mix,
            "length_distribution": length_dist,
            "avg_emoji_per_post": avg_emoji,
            "topics": topic_counts,
        },
        "voice_characteristics": vc,
        "places": places,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_build_tov.py -k "build_summary" -v
```

Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add build_tov.py tests/test_build_tov.py
git commit -m "feat: add build_summary — style patterns, voice characteristics, places"
```

---

### Task 5: Main pipeline + output files

**Files:**
- Modify: `build_tov.py`

- [ ] **Step 1: Add failing test for full pipeline**

Append to `tests/test_build_tov.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_build_tov.py::test_run_pipeline_produces_valid_json -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement `run_pipeline` and `__main__` block**

Append to `build_tov.py`:

```python
CSV_FIELDS = [
    "url", "date", "caption", "likes", "length_type",
    "language", "topic", "has_location",
    "location_city", "location_country", "location_region_type",
    "emoji_count",
]


def run_pipeline(input_path: str, out_json: str, out_csv: str) -> None:
    with open(input_path, encoding="utf-8") as f:
        raw_posts = json.load(f)

    recent = filter_recent(raw_posts)
    tagged = [tag_post(p) for p in recent]
    summary = build_summary(tagged)

    output = {
        "profile_summary": {
            **PROFILE,
            "analysis_period": {"from": CUTOFF, "to": str(date.today())},
            "total_posts_analyzed": len(tagged),
            **summary,
        },
        "posts": tagged,
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for p in tagged:
            loc = p["location"] or {}
            writer.writerow({
                "url": p["url"],
                "date": p["date"],
                "caption": p["caption"],
                "likes": p["likes"],
                "length_type": p["length_type"],
                "language": p["language"],
                "topic": p["topic"],
                "has_location": p["has_location"],
                "location_city": loc.get("city", ""),
                "location_country": loc.get("country", ""),
                "location_region_type": loc.get("region_type", ""),
                "emoji_count": p["emoji_count"],
            })


if __name__ == "__main__":
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    run_pipeline(
        input_path=os.path.join(base, "nadezdi_net_posts.json"),
        out_json=os.path.join(base, "tone_of_voice.json"),
        out_csv=os.path.join(base, "tone_of_voice.csv"),
    )
    print("Done. Files written: tone_of_voice.json, tone_of_voice.csv")
```

- [ ] **Step 4: Run all tests**

```bash
python3 -m pytest tests/test_build_tov.py -v
```

Expected: all tests pass

- [ ] **Step 5: Run the actual script**

```bash
cd /Users/alexmodestov/ManyChat/Projects/hackathon
python3 build_tov.py
```

Expected output:
```
Done. Files written: tone_of_voice.json, tone_of_voice.csv
```

- [ ] **Step 6: Verify output**

```bash
python3 -c "
import json
d = json.load(open('tone_of_voice.json'))
print('Posts:', len(d['posts']))
print('Period:', d['profile_summary']['analysis_period'])
print('Style patterns:', d['profile_summary']['style_patterns'])
print('Places home:', d['profile_summary']['places']['home'][:5])
"
```

Expected: posts count > 0, period starts 2024-01-01, style_patterns populated.

- [ ] **Step 7: Commit**

```bash
git add build_tov.py tests/test_build_tov.py tone_of_voice.json tone_of_voice.csv
git commit -m "feat: complete build_tov pipeline — outputs tone_of_voice.json and .csv"
```
