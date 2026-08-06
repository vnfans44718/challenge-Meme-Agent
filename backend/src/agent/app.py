import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agent.recommend import recommend_memes
from agent.services.meme_repository import VALID_EMOTION_KEYS, get_memes_by_emotion_safe

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/memes")
def get_memes(emotion_text: str = Query(..., description="추천용 문장")):
    try:
        result = recommend_memes(emotion_text)
        logger.info(
            "추천 완료: emotion_text=%r, emotion=%r, memes=%d개",
            emotion_text, result["emotion_key"], len(result["memes"]),
        )
        return {
            "emotion": result["emotion_key"],
            "classifiedEmotion": result["classified_emotion"],
            "memes": result["memes"],
            "hasMore": result["has_more"],
        }
    except Exception:
        logger.exception("짤 추천 처리 중 오류 발생: emotion_text=%r", emotion_text)
        raise HTTPException(status_code=500, detail="짤 추천 처리 중 오류가 발생했습니다.")


@app.get("/api/memes/by-emotion")
def get_memes_by_emotion_endpoint(
    emotion: str = Query(..., description="감정 라벨 (기쁨/상처/슬픔/분노/불안/당황/중립)"),
    offset: int = Query(0, ge=0, description="페이지네이션 시작 위치"),
):
    if emotion not in VALID_EMOTION_KEYS:
        raise HTTPException(status_code=400, detail="유효하지 않은 감정 값입니다.")
    memes, has_more = get_memes_by_emotion_safe(emotion, offset=offset)
    logger.info("짤 페이지 조회 완료: emotion=%r, offset=%d, memes=%d개", emotion, offset, len(memes))
    return {"emotion": emotion, "memes": memes, "hasMore": has_more}
