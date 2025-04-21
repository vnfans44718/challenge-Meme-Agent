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
GOOGLE_CX_ID   = os.getenv("GOOGLE_CX_ID")

# ─── 상태 스키마 정의 ────────────────────────────
class EmotionState(TypedDict):
    emotion_text: str
    classified_emotion: str
    memes: list

# ─── 감정에 따른 한글 표현 매핑 (다중 표현) ─────────────────────
EMOTION_PHRASES = {
    '기쁨':  ['기뻐하는', '즐거운', '행복한'],
    '상처':  ['상처받은', '상처깊은', '마음아픈'],
    '슬픔':  ['슬퍼하는', '우울한', '슬픈', '마음아픈'],
    '분노':  ['화내는', '분노하는','화내는','빡친'],
    '불안':  ['불안해하는','불안한','불안','심란한'],
    '당황':  ['당황하는','당황한','당황스러운운'],
}

# ─── 감정 분류 노드 ────────────────────────────────────
def classify_emotion_fn(state: EmotionState) -> EmotionState:
    text   = state.get("emotion_text", "")
    labels = list(EMOTION_PHRASES.keys())
    prompt = (
        "당신은 감정 분석 전문가입니다.\n"
        "아래 레이블 중 하나로 문장의 감정을 분류하고, 라벨만 정확히 출력하세요.\n"
        f"레이블: {labels}\n"
        f"문장: “{text}”"
    )

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"user","content":prompt}],
        temperature=0.0
    )
    raw = resp.choices[0].message.content.strip()

    # 유효한 라벨만 추출
    for label in labels:
        if label in raw:
            state["classified_emotion"] = label
            break
    else:
        state["classified_emotion"] = raw

    return state

# ─── Google API 짤 이미지 검색 노드 (다중 표현 지원) ─────────────
def recommend_memes_fn(state: EmotionState) -> EmotionState:
    label   = state.get("classified_emotion", "")
    phrases = EMOTION_PHRASES.get(label, [label])
    url     = "https://www.googleapis.com/customsearch/v1"

    seen = set()
    results = []

    for phrase in phrases:
        query = f"무한도전 {phrase} 짤"
        params = {
            "key":        GOOGLE_API_KEY,
            "cx":         GOOGLE_CX_ID,
            "q":          query,
            "searchType": "image",
            "num":        10,
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        items = resp.json().get("items", [])

        for item in items:
            link = item.get("link")
            if not link or not item.get("mime","").startswith("image/"):
                continue
            if not link.lower().endswith((".jpg",".jpeg",".png",".gif")):
                continue
            if any(d in item.get("displayLink","") for d in ["tiktok.com","instagram.com"]):
                continue
            if link in seen:
                continue
            seen.add(link)
            results.append({
                "id": link,
                "imageUrl": link,
                "title": f"무한도전 {phrase} 짤"
            })
    state["memes"] = results
    return state

# ─── StateGraph 정의 및 컴파일 ─────────────────────────────
workflow = StateGraph(state_schema=EmotionState)
workflow.add_node("classify", classify_emotion_fn)
workflow.add_node("recommend", recommend_memes_fn)

workflow.set_entry_point("classify")
workflow.add_edge("classify", "recommend")
workflow.set_finish_point("recommend")

graph = workflow.compile()

# 외부에서 import 할 때 graph 객체로 사용: `from src.langgraph_agent.graph import graph