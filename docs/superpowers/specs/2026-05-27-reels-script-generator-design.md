# Reels Script Generator — Design Spec

**Date:** 2026-05-27
**Context:** Hackathon, 2-hour build

---

## Overview

A web app for content creators. The user inputs an Instagram hashtag and their video topic — the service fetches top trending Reels from that hashtag via Apify, then uses Claude to generate a beat sheet and full script in the style of those trends.

---

## Architecture

```
[HTML page]
    │
    │ POST /generate { hashtag, creator_topic }
    ▼
[FastAPI]
    ├─► Apify (apify/instagram-scraper)
    │       └─ top-10 Reels by hashtag
    │          (caption, likesCount, videoPlayCount, url)
    │
    └─► Claude API (claude-sonnet-4-6)
            ├─ STEP 1: Beat sheet (Hook / Conflict / Resolution / CTA)
            └─ STEP 2: Full script with timestamps
```

---

## Backend

**Stack:** Python 3.11+, FastAPI, httpx, anthropic SDK

**Single endpoint:** `POST /generate`

Request body:
```json
{
  "hashtag": "fitness",
  "creator_topic": "домашние тренировки"
}
```

Response body:
```json
{
  "beat_sheet": {
    "hook": "...",
    "conflict": "...",
    "resolution": "...",
    "cta": "..."
  },
  "script": "[0:00] ...\n[0:05] ..."
}
```

**Apify call:**
- Actor: `apify/instagram-scraper`
- Input: `{ "hashtags": ["<hashtag>"], "resultsType": "posts", "resultsLimit": 10 }`
- Run synchronously via Apify REST API, wait for dataset
- Extract: `caption`, `likesCount`, `videoPlayCount`, `url` per post

**Claude call:**
- Model: `claude-sonnet-4-6`
- Single prompt — system sets the role (viral content strategist), user message includes the 10 Reels data + creator topic
- Claude returns JSON with `beat_sheet` and `script` fields (instructed via prompt)

---

## Frontend

Single `index.html` file. No JS framework.

**Layout (top to bottom):**
1. Title: "Reels Script Generator"
2. Input: hashtag (text field, `#` prefix shown)
3. Input: creator topic (text field)
4. Button: "Generate Script" — disabled + spinner while request in flight
5. Error block (red, hidden by default) — shown on any API error
6. Beat Sheet block (hidden until response) — four labeled lines: Hook / Conflict / Resolution / CTA
7. Full Script block (hidden until response) — preformatted text with timestamps

Uses `fetch` to call the FastAPI backend. Renders result via `innerHTML`.

---

## Data Flow

1. User fills in hashtag + topic, clicks Generate
2. Frontend disables button, shows spinner, clears previous result
3. `POST /generate` hits FastAPI
4. FastAPI calls Apify synchronously (timeout: 30s)
5. FastAPI feeds Apify results + creator topic to Claude
6. Claude returns beat sheet + script as JSON
7. FastAPI returns 200 with the JSON
8. Frontend renders Beat Sheet and Full Script sections

---

## Error Handling

Only at system boundaries:

| Condition | HTTP code | UI message |
|-----------|-----------|------------|
| Apify returns 0 results | 400 | "Хэштег не найден или нет Reels" |
| Apify timeout (>30s) | 504 | "Сервис временно недоступен, попробуй снова" |
| Claude API error | 502 | "Ошибка генерации, попробуй снова" |

All errors surface as a red block in the UI. Button re-enables on error.

---

## Environment Variables

```
APIFY_API_TOKEN=...
ANTHROPIC_API_KEY=...
```

---

## Out of Scope

- Auth / user accounts
- Saving / history of generated scripts
- Multiple hashtags in one request
- Language selection (output language follows input topic language)
