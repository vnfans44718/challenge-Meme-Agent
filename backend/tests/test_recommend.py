from unittest.mock import patch

from agent.recommend import DEFAULT_EMOTION_KEY, recommend_memes
from agent.services.emotion_classifier import EMOTION_LABELS


@patch("agent.recommend.get_memes_by_emotion_safe")
@patch("agent.recommend.classify_emotion")
def test_recommend_memes_classifies_then_recommends(mock_classify, mock_get_memes):
    mock_classify.return_value = "기쁨"
    mock_get_memes.return_value = ([{"id": 1, "imageUrl": "url", "title": "t"}], True)

    result = recommend_memes("오늘 기분 좋아!")

    mock_classify.assert_called_once_with("오늘 기분 좋아!")
    mock_get_memes.assert_called_once_with("기쁨")
    assert result == {
        "classified_emotion": "기쁨",
        "emotion_key": "기쁨",
        "memes": [{"id": 1, "imageUrl": "url", "title": "t"}],
        "has_more": True,
    }


@patch("agent.recommend.get_memes_by_emotion_safe")
@patch("agent.recommend.classify_emotion")
def test_recommend_memes_falls_back_to_default_when_unmapped(mock_classify, mock_get_memes):
    mock_classify.return_value = "알수없음"
    mock_get_memes.return_value = ([], False)

    result = recommend_memes("...")

    mock_get_memes.assert_called_once_with(DEFAULT_EMOTION_KEY)
    assert result["emotion_key"] == DEFAULT_EMOTION_KEY


def test_default_emotion_key_is_not_a_classifier_label():
    assert DEFAULT_EMOTION_KEY not in EMOTION_LABELS
