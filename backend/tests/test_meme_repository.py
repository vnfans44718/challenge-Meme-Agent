from unittest.mock import MagicMock, patch

import pytest

from agent.services.meme_repository import (
    DEFAULT_PAGE_SIZE,
    get_memes_by_emotion,
    get_memes_by_emotion_safe,
)


def _query_chain(client: MagicMock) -> MagicMock:
    return client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value


def _mock_client(rows: list[dict], public_url_fn=lambda path: f"https://cdn.example/{path}"):
    client = MagicMock()
    _query_chain(client).execute.return_value.data = rows
    client.storage.from_.return_value.get_public_url.side_effect = public_url_fn
    return client


def _mock_client_raising(error: Exception) -> MagicMock:
    client = MagicMock()
    _query_chain(client).execute.side_effect = error
    return client


@patch("agent.services.meme_repository.get_supabase_client")
def test_get_memes_by_emotion_queries_table_and_builds_public_urls(mock_get_client):
    mock_get_client.return_value = _mock_client(
        [{"id": 1, "emotion": "joy", "title": "웃긴 짤", "image_path": "joy/1.png"}]
    )

    memes, has_more = get_memes_by_emotion("joy")

    table = mock_get_client.return_value.table
    table.assert_called_once_with("memes")
    table.return_value.select.assert_called_once_with("*")
    table.return_value.select.return_value.eq.assert_called_once_with("emotion", "joy")
    table.return_value.select.return_value.eq.return_value.order.assert_called_once_with("id")
    table.return_value.select.return_value.eq.return_value.order.return_value.range.assert_called_once_with(
        0, DEFAULT_PAGE_SIZE
    )
    assert memes == [{"id": 1, "imageUrl": "https://cdn.example/joy/1.png", "title": "웃긴 짤"}]
    assert has_more is False


@patch("agent.services.meme_repository.get_supabase_client")
def test_get_memes_by_emotion_uses_given_offset(mock_get_client):
    mock_get_client.return_value = _mock_client([])

    get_memes_by_emotion("joy", offset=24, limit=12)

    mock_get_client.return_value.table.return_value.select.return_value.eq.return_value.order.return_value.range.assert_called_once_with(
        24, 36
    )


@patch("agent.services.meme_repository.get_supabase_client")
def test_get_memes_by_emotion_reports_has_more_when_extra_row_present(mock_get_client):
    rows = [
        {"id": i, "emotion": "joy", "title": f"t{i}", "image_path": f"joy/{i}.png"}
        for i in range(4)
    ]
    mock_get_client.return_value = _mock_client(rows)

    memes, has_more = get_memes_by_emotion("joy", limit=3)

    assert [m["id"] for m in memes] == [0, 1, 2]
    assert has_more is True


@patch("agent.services.meme_repository.get_supabase_client")
def test_get_memes_by_emotion_returns_empty_when_no_rows(mock_get_client):
    mock_get_client.return_value = _mock_client([])

    assert get_memes_by_emotion("neutral") == ([], False)


@patch("agent.services.meme_repository.get_supabase_client")
def test_get_memes_by_emotion_propagates_supabase_errors(mock_get_client):
    mock_get_client.return_value = _mock_client_raising(Exception("network error"))

    with pytest.raises(Exception):
        get_memes_by_emotion("joy")


@patch("agent.services.meme_repository.get_supabase_client")
def test_get_memes_by_emotion_safe_returns_empty_on_error(mock_get_client):
    mock_get_client.return_value = _mock_client_raising(Exception("network error"))

    assert get_memes_by_emotion_safe("joy") == ([], False)


@patch("agent.services.meme_repository.get_supabase_client")
def test_get_memes_by_emotion_safe_passes_through_on_success(mock_get_client):
    mock_get_client.return_value = _mock_client(
        [{"id": 1, "emotion": "joy", "title": "t", "image_path": "joy/1.png"}]
    )

    assert get_memes_by_emotion_safe("joy") == (
        [{"id": 1, "imageUrl": "https://cdn.example/joy/1.png", "title": "t"}],
        False,
    )
