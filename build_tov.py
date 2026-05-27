import json
import csv
import re
import emoji as emoji_lib
from datetime import date
from typing import Optional


CUTOFF = "2024-01-01"


def filter_recent(posts: list[dict]) -> list[dict]:
    return [p for p in posts if p.get("timestamp", "") >= CUTOFF]


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


def normalize_location(raw: Optional[str]) -> Optional[dict]:
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


PROFILE = {
    "username": "nadezdi_net",
    "full_name": "Nadezhda",
    "bio": "Живу в Барселоне, пишу код, ухаживаю за зелеными. А завтра посмотрим",
    "home_city": "Barcelona",
}


def build_summary(tagged_posts: list) -> dict:
    n = len(tagged_posts)
    if n == 0:
        return {}

    captions = [p["caption"] for p in tagged_posts if p["caption"]]
    avg_len = sum(len(c) for c in captions) // max(len(captions), 1)

    lang_counts: dict = {"ru": 0, "en": 0, "mixed": 0}
    for p in tagged_posts:
        lang_counts[p["language"]] = lang_counts.get(p["language"], 0) + 1
    lang_mix = {k: round(v / n, 2) for k, v in lang_counts.items()}

    length_dist: dict = {"micro": 0, "short": 0, "medium": 0, "long": 0}
    for p in tagged_posts:
        length_dist[p["length_type"]] += 1

    topic_counts: dict = {"daily_life": 0, "travel": 0, "people": 0, "reflection": 0, "humor": 0}
    for p in tagged_posts:
        topic_counts[p["topic"]] = topic_counts.get(p["topic"], 0) + 1

    avg_emoji = round(sum(p["emoji_count"] for p in tagged_posts) / n, 2)

    # voice_characteristics: up to 5 real examples per length type, prefer with-caption
    vc: dict = {"micro": [], "short": [], "medium": [], "long": []}
    for lt in vc:
        examples = [p["caption"] for p in tagged_posts
                    if p["length_type"] == lt and p["caption"]]
        vc[lt] = examples[:5]

    # places: unique city names per region_type
    places: dict = {
        "home": [], "travel_europe": [], "travel_world": [], "russia_past": []
    }
    seen: set = set()
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
