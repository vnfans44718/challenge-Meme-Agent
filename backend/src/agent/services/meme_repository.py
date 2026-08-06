import logging
import random

from agent.services.emotion_classifier import EMOTION_LABELS
from agent.services.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

BUCKET_NAME = "memes"
MAX_RESULTS = 3

VALID_EMOTION_KEYS = frozenset({*EMOTION_LABELS, "중립"})


def get_memes_by_emotion(emotion: str, limit: int = MAX_RESULTS) -> list[dict]:
    """public.memes에서 emotion이 일치하는 행을 모두 조회해 무작위로 최대 `limit`개 선택한다.

    DB 쿼리에 LIMIT을 걸면 "다른 짤 보기"가 매번 같은 결과만 반환하게 되므로,
    해당 감정의 전체 행을 가져온 뒤 파이썬에서 섞어서 자른다.
    """
    effective_limit = min(limit, MAX_RESULTS)
    response = (
        get_supabase_client()
        .table("memes")
        .select("*")
        .eq("emotion", emotion)
        .execute()
    )
    rows = list(response.data or [])
    random.shuffle(rows)
    return [_to_meme_dict(row) for row in rows[:effective_limit]]


def get_memes_by_emotion_safe(emotion: str, limit: int = MAX_RESULTS) -> list[dict]:
    """get_memes_by_emotion의 예외-안전 래퍼. Supabase 장애 시 빈 리스트를 반환한다."""
    try:
        return get_memes_by_emotion(emotion, limit)
    except Exception:
        logger.exception("Supabase 짤 조회 실패: emotion=%r", emotion)
        return []


def _to_meme_dict(row: dict) -> dict:
    public_url = get_supabase_client().storage.from_(BUCKET_NAME).get_public_url(row["image_path"])
    return {
        "id": row["id"],
        "imageUrl": public_url,
        "title": row.get("title") or "",
    }
