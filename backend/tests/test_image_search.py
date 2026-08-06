from unittest.mock import MagicMock, patch

from agent.services.image_search import search_meme_images


def _mock_search_response(documents: list[dict]) -> MagicMock:
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"documents": documents}
    return resp


@patch("agent.services.image_search.requests.get")
def test_search_meme_images_filters_and_dedupes(mock_get):
    mock_get.return_value = _mock_search_response([
        {"image_url": "https://a.com/1.jpg"},
        {"image_url": "https://a.com/1.jpg"},
        {"image_url": "https://www.tiktok.com/2.jpg"},
        {"image_url": "https://a.com/3.mp4"},
        {"image_url": "https://a.com/4.png"},
        {"image_url": "https://a.com/5.jpg?type=w966"},
        {"image_url": ""},
    ])

    results = search_meme_images("무한도전", ["슬퍼하는", "우울한"], "슬픔")

    assert [r["id"] for r in results] == [
        "https://a.com/1.jpg",
        "https://a.com/4.png",
        "https://a.com/5.jpg?type=w966",
    ]
    assert all(r["title"] == "무한도전 슬픔 짤" for r in results)


@patch("agent.services.image_search.requests.get")
def test_search_meme_images_issues_single_request_with_representative_phrase(mock_get):
    mock_get.return_value = _mock_search_response([])

    search_meme_images("무한도전", ["슬퍼하는", "우울한"], "슬픔")

    assert mock_get.call_count == 1
    assert mock_get.call_args.kwargs["params"]["query"] == "무한도전 슬퍼하는"
