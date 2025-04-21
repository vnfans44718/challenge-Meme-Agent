from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent.graph import graph  # graph는 동기 방식으로 invoke됨
import json  # 결과 출력용

app = FastAPI()

# ─── CORS 설정 (프론트와 연동 시 필수) ───────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계에서는 전체 허용, 배포 시 도메인으로 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/memes")
def get_memes(emotion_text: str = Query(..., description="추천용 문장")):
    try:
        result = graph.invoke({"emotion_text": emotion_text})  # ✅ LangGraph 실행
        print("🟢 최종 결과:", json.dumps(result, ensure_ascii=False, indent=2))
        return {"memes": result["memes"]}
    except Exception as e:
        print("🔴 API 에러:", e)
        raise HTTPException(status_code=500, detail=str(e))
