import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

_client = None

EMOTION_LABELS = ["기쁨", "상처", "슬픔", "분노", "불안", "당황"]

DEFAULT_MODEL = "claude-haiku-4-5"


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


def classify_emotion(text: str, *, model: str = DEFAULT_MODEL) -> str:
    """문장의 감정을 EMOTION_LABELS 중 하나로 분류한다. 매칭되는 라벨이 없으면 모델의 원본 응답을 반환한다."""
    prompt = (
        "당신은 감정 분석 전문가입니다.\n"
        "아래 레이블 중 하나로 문장의 감정을 분류하고, 라벨만 정확히 출력하세요.\n"
        f"레이블: {EMOTION_LABELS}\n"
        f"문장: “{text}”"
    )

    resp = _get_client().messages.create(
        model=model,
        max_tokens=20,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = next((block.text for block in resp.content if block.type == "text"), "").strip()

    for label in EMOTION_LABELS:
        if label in raw:
            return label
    return raw
