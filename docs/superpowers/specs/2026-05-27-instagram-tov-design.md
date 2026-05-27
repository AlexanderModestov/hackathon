# Instagram Tone of Voice — Design Spec

**Date:** 2026-05-27  
**Source:** @nadezdi_net (Instagram)  
**Goal:** Build a structured JSON dataset for LLM prompting that generates text in Nadezhda's style — Instagram captions, messages, and social posts.

---

## Context

We have collected 394 Instagram posts (2016–2026) from @nadezdi_net via Apify scraper. The account belongs to Nadezhda — a Russian-speaking developer living in Barcelona. Her style has clearly evolved over time; we focus on **2024–2026 posts** as the target voice.

Raw data files:
- `nadezdi_net_posts.json` — 394 posts with caption, location, likes, type
- `nadezdi_net_profile.json` — profile metadata
- `nadezdi_net_posts.csv` — same posts in tabular form

---

## Approach

**Flat JSON with filtering and auto-tagging** (no external LLM API calls).

Filter to recent posts → normalize locations → tag each post with heuristics → build profile summary with few-shot examples → write output files.

---

## Data Pipeline

```
nadezdi_net_posts.json
        ↓
1. filter_recent()      — keep posts from 2024-01-01 onwards
        ↓
2. normalize_location() — parse locationName → city / country / region_type
        ↓
3. tag_post()           — length_type, language, topic, emoji_count
        ↓
4. build_summary()      — compute style_patterns, pick voice_characteristics examples
        ↓
5. write output         — tone_of_voice.json + tone_of_voice.csv
```

Single script: `build_tov.py`  
Dependencies: Python stdlib + `emoji` package only. No external API calls.

---

## Tagging Logic

### length_type
| Type | Range |
|---|---|
| `micro` | 1–30 chars |
| `short` | 31–100 chars |
| `medium` | 101–300 chars |
| `long` | 300+ chars |

### language
- `ru` — caption contains Cyrillic characters (>50% of alpha chars)
- `en` — caption is mostly Latin
- `mixed` — significant presence of both

### topic (keyword heuristics)
| Topic | Keywords |
|---|---|
| `travel` | barcelona, поездка, город, море, горы, flight, путешествие, страна |
| `people` | @mention present, друг, мы, вместе, люблю |
| `reflection` | год, жизнь, думаю, чувствую, понимаю, стала, раньше |
| `humor` | хехе, ха, ирония, забавно, смешно |
| `daily_life` | fallback — everything else |

### region_type (location normalization)
| Type | Definition |
|---|---|
| `home` | Barcelona, Badalona, or surrounding area |
| `travel_europe` | European countries/cities outside Spain |
| `travel_world` | Non-European locations |
| `russia_past` | Russia, Moscow, and CIS locations |
| `unknown` | Cannot be classified |

---

## Output JSON Structure

`location` is `null` when a post has no geotag. When present, it's an object with `raw`, `city`, `country`, `region_type`.

```json
{
  "profile_summary": {
    "username": "nadezdi_net",
    "full_name": "Nadezhda",
    "bio": "Живу в Барселоне, пишу код, ухаживаю за зелеными",
    "home_city": "Barcelona",
    "analysis_period": {
      "from": "2024-01-01",
      "to": "2026-05-27"
    },
    "total_posts_analyzed": "<int>",

    "style_patterns": {
      "avg_caption_length": "<int>",
      "language_mix": {"ru": 0.0, "en": 0.0, "mixed": 0.0},
      "length_distribution": {"micro": 0, "short": 0, "medium": 0, "long": 0},
      "avg_emoji_per_post": 0.0,
      "topics": {"daily_life": 0, "travel": 0, "people": 0, "reflection": 0, "humor": 0}
    },

    "voice_characteristics": {
      "micro": ["...", "..."],
      "short": ["...", "..."],
      "medium": ["...", "..."],
      "long": ["..."]
    },

    "places": {
      "home": [],
      "travel_europe": [],
      "travel_world": [],
      "russia_past": []
    }
  },

  "posts": [
    {
      "url": "https://www.instagram.com/p/...",
      "date": "YYYY-MM-DD",
      "caption": "...",
      "likes": 0,
      "length_type": "short",
      "language": "ru",
      "topic": "daily_life",
      "has_location": false,
      "location": null,
      "emoji_count": 0
    }
  ]
}
```

---

## Output Files

| File | Purpose |
|---|---|
| `tone_of_voice.json` | Full structured dataset for LLM prompting |
| `tone_of_voice.csv` | Flat table for human review |

Both saved to project root `/Users/alexmodestov/ManyChat/Projects/hackathon/`.

---

## Success Criteria

1. `tone_of_voice.json` is valid JSON with `profile_summary` and `posts` keys
2. All posts in `posts` array are from 2024-01-01 onwards
3. Every post has `length_type`, `language`, `topic`, `emoji_count` fields populated
4. `voice_characteristics` contains at least 2 real caption examples per length type (where available)
5. `places` dict has at least the home and travel_europe categories populated
6. Script runs with `python3 build_tov.py` and produces both output files in under 5 seconds
