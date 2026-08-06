from unittest.mock import MagicMock, patch

from agent.services.emotion_classifier import EMOTION_LABELS, classify_emotion


def _mock_message_response(text: str) -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text
    resp = MagicMock()
    resp.content = [block]
    return resp


@patch("agent.services.emotion_classifier._get_client")
def test_classify_emotion_returns_matching_label(mock_get_client):
    mock_get_client.return_value.messages.create.return_value = _mock_message_response("슬픔")

    assert classify_emotion("오늘 너무 슬퍼") == "슬픔"


@patch("agent.services.emotion_classifier._get_client")
def test_classify_emotion_falls_back_to_raw_text_when_no_label_matches(mock_get_client):
    mock_get_client.return_value.messages.create.return_value = _mock_message_response("모르겠음")

    assert classify_emotion("...") == "모르겠음"


def test_emotion_labels_are_unique():
    assert len(EMOTION_LABELS) == len(set(EMOTION_LABELS))
