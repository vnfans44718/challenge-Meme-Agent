import logging

from agent.services.emotion_classifier import EMOTION_LABELS
from agent.services.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

BUCKET_NAME = "memes"
DEFAULT_PAGE_SIZE = 12

VALID_EMOTION_KEYS = frozenset({*EMOTION_LABELS, "중립"})


def get_memes_by_emotion(
    emotion: str, offset: int = 0, limit: int = DEFAULT_PAGE_SIZE
) -> tuple[list[dict], bool]:
    response = (
        get_supabase_client()
        .table("memes")
        .select("*")
        .eq("emotion", emotion)
        .order("id")
        .range(offset, offset + limit)
        .execute()
    )
    rows = list(response.data or [])
    has_more = len(rows) > limit
    return [_to_meme_dict(row) for row in rows[:limit]], has_more


def get_memes_by_emotion_safe(
    emotion: str, offset: int = 0, limit: int = DEFAULT_PAGE_SIZE
) -> tuple[list[dict], bool]:
    try:
        return get_memes_by_emotion(emotion, offset, limit)
    except Exception:
        logger.exception("Supabase 짤 조회 실패: emotion=%r", emotion)
        return [], False


def _to_meme_dict(row: dict) -> dict:
    public_url = get_supabase_client().storage.from_(BUCKET_NAME).get_public_url(row["image_path"])
    return {
        "id": row["id"],
        "imageUrl": public_url,
        "title": row.get("title") or "",
    }
