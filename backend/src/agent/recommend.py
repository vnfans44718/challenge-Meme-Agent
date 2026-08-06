from agent.services.emotion_classifier import EMOTION_LABELS, classify_emotion
from agent.services.meme_repository import get_memes_by_emotion_safe

DEFAULT_EMOTION_KEY = "중립"


def recommend_memes(emotion_text: str) -> dict:
    """문장을 감정으로 분류하고, 그 감정에 맞는 짤을 Supabase에서 조회한다."""
    classified_emotion = classify_emotion(emotion_text)
    emotion_key = classified_emotion if classified_emotion in EMOTION_LABELS else DEFAULT_EMOTION_KEY
    memes, has_more = get_memes_by_emotion_safe(emotion_key)
    return {
        "classified_emotion": classified_emotion,
        "emotion_key": emotion_key,
        "memes": memes,
        "has_more": has_more,
    }
