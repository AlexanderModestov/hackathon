import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import json
import pytest
from unittest.mock import patch, MagicMock
from claude_client import generate_script

SAMPLE_REELS = [
    {"caption": "Morning workout tips", "likesCount": 5000, "videoPlayCount": 20000},
    {"caption": "3 mistakes beginners make", "likesCount": 8000, "videoPlayCount": 35000},
]

SAMPLE_RESPONSE = {
    "beat_sheet": {
        "hook": "You've been doing pushups wrong",
        "conflict": "Most people skip form and get zero results",
        "resolution": "3 adjustments that double your gains",
        "cta": "Save this for your next workout",
    },
    "script": "[0:00] You've been doing pushups wrong\n[0:05] Most people skip form\n[0:10] Here are 3 fixes",
}


def test_generate_script_returns_beat_sheet_and_script():
    mock_message = MagicMock()
    mock_message.content[0].text = json.dumps(SAMPLE_RESPONSE)

    with patch("claude_client.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = mock_message
        result = generate_script(SAMPLE_REELS, "домашние тренировки")

    assert "beat_sheet" in result
    assert "script" in result
    assert "hook" in result["beat_sheet"]
    assert "conflict" in result["beat_sheet"]
    assert "resolution" in result["beat_sheet"]
    assert "cta" in result["beat_sheet"]


def test_generate_script_passes_reels_to_claude():
    mock_message = MagicMock()
    mock_message.content[0].text = json.dumps(SAMPLE_RESPONSE)

    with patch("claude_client.anthropic.Anthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create.return_value = mock_message
        generate_script(SAMPLE_REELS, "домашние тренировки")

    call_kwargs = instance.messages.create.call_args
    user_content = call_kwargs.kwargs["messages"][0]["content"]
    assert "Morning workout tips" in user_content
    assert "домашние тренировки" in user_content


def test_generate_script_raises_on_invalid_json():
    mock_message = MagicMock()
    mock_message.content[0].text = "Not valid JSON at all"

    with patch("claude_client.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = mock_message
        with pytest.raises(ValueError):
            generate_script(SAMPLE_REELS, "test topic")
