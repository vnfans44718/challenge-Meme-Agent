import os
from urllib.parse import urlparse

from dotenv import load_dotenv
import requests

load_dotenv()

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

SEARCH_URL = "https://dapi.kakao.com/v2/search/image"
EXCLUDED_DOMAINS = ("tiktok.com", "instagram.com")
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif")


def search_meme_images(theme: str, phrases: list[str], label: str, *, num: int = 10) -> list[dict]:
    """감정을 대표하는 표현 하나로 단일 Kakao(Daum) 이미지 검색 요청을 보낸다.

    Kakao 이미지 검색은 쿼리의 모든 단어를 AND로 매칭하므로, 여러 유사 표현을 한 쿼리에
    합치면(예: "화내는 분노하는 빡친") 세 단어를 동시에 포함하는 문서가 거의 없어 결과가
    0에 가까워진다. 그래서 감정당 대표 표현 하나(phrases[0])만 사용한다.
    """
    query = f"{theme} {phrases[0]}"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": query, "size": num}
    resp = requests.get(SEARCH_URL, headers=headers, params=params)
    resp.raise_for_status()
    documents = resp.json().get("documents", [])

    seen = set()
    results = []
    for doc in documents:
        link = doc.get("image_url")
        if not link:
            continue
        parsed = urlparse(link)
        if not parsed.path.lower().endswith(IMAGE_EXTENSIONS):
            continue
        if any(d in parsed.netloc for d in EXCLUDED_DOMAINS):
            continue
        if link in seen:
            continue
        seen.add(link)
        results.append({
            "id": link,
            "imageUrl": link,
            "title": f"{theme} {label} 짤",
        })
    return results
