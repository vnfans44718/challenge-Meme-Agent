import os
import json
import requests
from openai import OpenAI
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict
from dotenv import load_dotenv

# ─── 환경변수 로드 ────────────────────────────────────
load_dotenv()

# ─── OpenAI 클라이언트 초기화 ──────────────────────────────
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ─── Google Custom Search API 키 및 엔진 ID 설정 ─────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX_ID = os.getenv("GOOGLE_CX_ID")

# ─── 상태 스키마 정의 ────────────────────────────
class EmotionState(TypedDict):
    emotion_text: str
    classified_emotion: str
    memes: list

# ─── 감정 분류 노드 ────────────────────────
def classify_emotion_fn(state: EmotionState) -> EmotionState:
    text = state.get("emotion_text", "")
    labels = ['기쁨', '상처', '슬픔', '분노', '불안', '당황']
    prompt = (
        "당신은 감정 분석 전문가입니다.\n"
        "아래 레이블 중 하나로 문장의 감정을 분류하고, 라벨만 정확히 출력하세요.\n"
        f"레이블: {labels}\n"
        f"문장: “{text}”"
    )
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    raw = resp.choices[0].message.content.strip()
    # 응답에서 유효한 라벨 추출
    for label in labels:
        if label in raw:
            state["classified_emotion"] = label
            break
    else:
        state["classified_emotion"] = raw
    print("🟢 감정 분석 결과 (정제):", state["classified_emotion"])
    return state

# ─── Google API 밈 이미지 검색 노드 ───────────────────────────
def recommend_memes_fn(state: EmotionState) -> EmotionState:
    label = state.get("classified_emotion", "")
    query = f"무한도전 {label} 밈"
    search_url = "https://www.googleapis.com/customsearch/v1"

    try:
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CX_ID,
            "q": query,
            "searchType": "image",
            "num": 10
        }
        print("🔍 Google API 요청 파라미터:", params)
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
        print("🟡 Google API 응답:", json.dumps(data, indent=2, ensure_ascii=False))

        state["memes"] = [
            {
                "id": item["link"],
                "imageUrl": item["image"]["link"],
                "title": item.get("title", "무한도전 밈")
            }
            for item in data.get("items", [])
            if item.get("mime", "").startswith("image/")
               and item.get("link", "").endswith((".jpg", ".jpeg", ".png", ".gif"))
               and not any(domain in item.get("displayLink", "") for domain in ["tiktok.com", "instagram.com"])
        ]
        print("🟢 최종 밈 결과:", state["memes"])

    except Exception as e:
        state["memes"] = []
        print("🔴 Google API 요청 실패:", e)

    return state

# ─── StateGraph 정의 및 컴파일 ─────────────────────────────
workflow = StateGraph(state_schema=EmotionState)
workflow.add_node("classify", classify_emotion_fn)
workflow.add_node("recommend", recommend_memes_fn)

workflow.set_entry_point("classify")
workflow.add_edge("classify", "recommend")
workflow.set_finish_point("recommend")

graph = workflow.compile(checkpointer=MemorySaver())

# 외부에서 import 할 때 graph 객체로 사용됩니다: from src.langgraph_agent.graph import graph