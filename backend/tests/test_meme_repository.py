from unittest.mock import MagicMock, patch

import pytest

from agent.services.meme_repository import (
    MAX_RESULTS,
    get_memes_by_emotion,
    get_memes_by_emotion_safe,
)


def _mock_client(rows: list[dict], public_url_fn=lambda path: f"https://cdn.example/{path}"):
    client = MagicMock()
    client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = rows
    client.storage.from_.return_value.get_public_url.side_effect = public_url_fn
    return client


@patch("agent.services.meme_repository.get_supabase_client")
def test_get_memes_by_emotion_queries_table_and_builds_public_urls(mock_get_client):
    mock_get_client.return_value = _mock_client(
        [{"id": 1, "emotion": "joy", "title": "웃긴 짤", "image_path": "joy/1.png"}]
    )

    results = get_memes_by_emotion("joy")

    mock_get_client.return_value.table.assert_called_once_with("memes")
    mock_get_client.return_value.table.return_value.select.assert_called_once_with("*")
    mock_get_client.return_value.table.return_value.select.return_value.eq.assert_called_once_with(
        "emotion", "joy"
    )
    assert results == [{"id": 1, "imageUrl": "https://cdn.example/joy/1.png", "title": "웃긴 짤"}]


@patch("agent.services.meme_repository.random.shuffle")
@patch("agent.services.meme_repository.get_supabase_client")
def test_get_memes_by_emotion_caps_at_max_results(mock_get_client, mock_shuffle):
    mock_shuffle.side_effect = None
    rows = [
        {"id": i, "emotion": "joy", "title": f"t{i}", "image_path": f"joy/{i}.png"}
        for i in range(5)
    ]
    mock_get_client.return_value = _mock_client(rows)

    results = get_memes_by_emotion("joy", limit=10)

    assert len(results) == MAX_RESULTS
    assert [r["id"] for r in results] == [0, 1, 2]


@patch("agent.services.meme_repository.get_supabase_client")
def test_get_memes_by_emotion_returns_empty_list_when_no_rows(mock_get_client):
    mock_get_client.return_value = _mock_client([])

    assert get_memes_by_emotion("neutral") == []


@patch("agent.services.meme_repository.get_supabase_client")
def test_get_memes_by_emotion_propagates_supabase_errors(mock_get_client):
    client = MagicMock()
    client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception(
        "network error"
    )
    mock_get_client.return_value = client

    with pytest.raises(Exception):
        get_memes_by_emotion("joy")


@patch("agent.services.meme_repository.get_supabase_client")
def test_get_memes_by_emotion_safe_returns_empty_list_on_error(mock_get_client):
    client = MagicMock()
    client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception(
        "network error"
    )
    mock_get_client.return_value = client

    assert get_memes_by_emotion_safe("joy") == []


@patch("agent.services.meme_repository.get_supabase_client")
def test_get_memes_by_emotion_safe_passes_through_on_success(mock_get_client):
    mock_get_client.return_value = _mock_client(
        [{"id": 1, "emotion": "joy", "title": "t", "image_path": "joy/1.png"}]
    )

    assert get_memes_by_emotion_safe("joy") == [
        {"id": 1, "imageUrl": "https://cdn.example/joy/1.png", "title": "t"}
    ]
