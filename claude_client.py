import json
import anthropic
from typing import Any


def generate_script(reels: list[dict[str, Any]], creator_topic: str) -> dict:
    client = anthropic.Anthropic()

    reels_text = "\n\n".join(
        f"Video {i + 1}:\nCaption: {r.get('caption', '')}\n"
        f"Likes: {r.get('likesCount', 0)}\nViews: {r.get('videoPlayCount', 0)}"
        for i, r in enumerate(reels)
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=(
            "You are a viral content strategist specializing in Instagram Reels. "
            "Analyze trending content patterns and create scripts that match those patterns."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Here are trending Instagram Reels:\n\n{reels_text}\n\n"
                    f"Create a Reel script for the topic: {creator_topic}\n\n"
                    "Return ONLY valid JSON with this exact structure:\n"
                    '{"beat_sheet": {"hook": "...", "conflict": "...", '
                    '"resolution": "...", "cta": "..."}, '
                    '"script": "[0:00] ...\\n[0:05] ..."}'
                ),
            }
        ],
    )

    try:
        return json.loads(message.content[0].text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude returned invalid JSON: {message.content[0].text[:200]}") from e
