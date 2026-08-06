# challenge-Meme-Agent

사용자가 입력한 문장의 **감정을 AI로 분석**하고, 그 감정에 어울리는 **무한도전 짤(이미지)을 추천**해주는 웹 애플리케이션입니다.

예: "오늘 시험 망쳤어 진짜 속상해" 입력 → 감정 분류(`상처`/`슬픔` 등) → 관련 무한도전 짤 이미지 목록 반환

---

## 1. 서비스 구성 및 핵심 기능

모노레포 구조로 `backend`(API 서버)와 `frontend`(웹 UI) 두 서비스로 구성되어 있습니다.

### backend (FastAPI)

- **목적**: 문장을 입력받아 감정을 분류하고, 그에 맞는 짤 이미지를 검색해 반환하는 API 서버
- **핵심 기능**
  - `GET /api/memes?emotion_text=...` — 문장을 받아 감정 분석 → 짤 목록 첫 페이지를 JSON으로 응답 (`{emotion, classifiedEmotion, memes, hasMore}`)
  - `GET /api/memes/by-emotion?emotion=...&offset=...` — 감정 재분류 없이 다음 페이지를 조회(무한 스크롤 "더 불러오기")
  - `recommend_memes()` 함수가 감정 분류 → 짤 조회를 순서대로 실행 ([backend/src/agent/recommend.py](backend/src/agent/recommend.py))
    1. Anthropic Claude(`claude-haiku-4-5` — 저비용/저지연 모델, 단순 6지선다 분류라 Haiku로 충분)로 문장의 감정을 `기쁨/상처/슬픔/분노/불안/당황` 중 하나로 분류 ([services/emotion_classifier.py](backend/src/agent/services/emotion_classifier.py))
    2. Claude가 반환한 한글 라벨(`기쁨/상처/슬픔/분노/불안/당황`, 매핑 안 되면 `중립`)로 Supabase `public.memes` 테이블을 조회 — `emotion` 컬럼 값도 한글 라벨과 동일 (Storage 폴더명만 영문이며 `image_path`에 이미 포함되어 있어 별도 변환 불필요). `id` 순으로 정렬해 `offset`부터 페이지 단위(기본 12개)로 조회하고, `image_path`를 Supabase Storage 공개 URL로 변환 ([services/meme_repository.py](backend/src/agent/services/meme_repository.py)) — 개수 제한 없이 해당 감정의 모든 짤을 페이지네이션으로 끝까지 탐색 가능
  - `GET /`, `GET /health` — 배포 플랫폼(Render 등) 헬스체크용 엔드포인트
  - `ALLOWED_ORIGINS` 환경변수로 CORS 허용 도메인 설정 (미설정 시 로컬 개발 서버만 허용)
  - `logging` 모듈로 요청 처리 로그 및 에러를 기록 (내부 에러 상세는 로그에만 남기고 클라이언트에는 노출하지 않음)
  - Supabase 조회 실패/결과 없음은 500이 아닌 200 + 빈 배열로 처리 (Claude 분류 자체가 실패한 경우에만 500)

### frontend (React + Vite)

- **목적**: 사용자가 감정 문장을 입력하고 추천된 짤 이미지를 그리드로 확인하는 UI
- **핵심 기능**
  - 문장 입력 후 `/api/memes` 호출 → 분류된 감정과 추천 짤 목록(첫 페이지)을 카드 그리드로 표시
  - 그리드 하단에 도달하면 `IntersectionObserver`가 감지해 `/api/memes/by-emotion`으로 다음 페이지를 자동 로드하는 무한 스크롤 (재분류 없이 같은 감정으로 계속 이어서 조회, 더 가져올 데이터가 없으면 자동 중단)
  - Header / SearchForm / MemeGrid / MemeModal 컴포넌트로 분리 ([frontend/src/components/](frontend/src/components/)), [App.jsx](frontend/src/App.jsx)는 상태 관리와 API 호출만 담당
  - 이미지를 클릭하면 모달로 확대 보기
  - API 호출 실패, 검색 결과 없음, 이미지 로딩 실패(깨진 이미지)를 각각 구분해 처리
  - 개발 서버에서 `/api` 요청을 백엔드(`localhost:8000`)로 프록시 ([frontend/vite.config.js](frontend/vite.config.js))
  - `VITE_API_BASE_URL` 환경변수로 백엔드 주소를 주입 ([src/config.js](frontend/src/config.js)) — 비워두면 위 프록시를 그대로 사용(로컬 개발), 배포 시에는 실제 백엔드 URL로 설정

---

## 2. 기술 스택

| 구분 | 기술 |
|---|---|
| Backend | Python 3.11+, FastAPI, Anthropic SDK, supabase-py, Uvicorn, python-dotenv |
| Backend 패키지 관리 | Poetry |
| Frontend | React 19, Vite 6 |
| Frontend 스타일 | Tailwind CSS 4 (PostCSS + autoprefixer) |
| Lint | ESLint 9 |
| Backend 테스트 | pytest |
| 외부 API | Anthropic Messages API(감정 분류), Supabase(짤 이미지 데이터/Storage) |

---

## 3. 패키지 구성도

```
challenge-Meme-Agent/
├── backend/
│   ├── pyproject.toml        # Poetry 프로젝트/의존성 정의 (+ pytest 설정)
│   ├── poetry.lock
│   ├── .env.example          # 필요한 환경변수 템플릿
│   ├── src/
│   │   └── agent/
│   │       ├── app.py                    # FastAPI 앱, /api/memes, /api/memes/by-emotion 엔드포인트
│   │       ├── recommend.py              # 감정 분류 → 감정 키 정규화 → 짤 조회를 실행하는 함수
│   │       └── services/
│   │           ├── emotion_classifier.py # Anthropic Claude 감정 분류 클라이언트
│   │           ├── supabase_client.py    # Supabase 클라이언트 (lazy singleton)
│   │           └── meme_repository.py    # public.memes 테이블 조회 + Storage 공개 URL 변환
│   └── tests/
│       ├── test_app.py
│       ├── test_emotion_classifier.py
│       ├── test_meme_repository.py
│       └── test_recommend.py
│
└── frontend/
    ├── package.json          # npm 의존성 및 스크립트(dev/build/lint/preview)
    ├── vite.config.js        # dev 서버 및 /api 프록시 설정
    ├── postcss.config.js     # Tailwind CSS 4 PostCSS 플러그인 설정
    ├── .env.example           # 필요한 환경변수 템플릿
    ├── index.html
    └── src/
        ├── main.jsx           # React 엔트리포인트
        ├── App.jsx            # 상태 관리 및 API 호출, 하위 컴포넌트 조합
        ├── config.js          # API_BASE_URL 등 환경변수 기반 설정
        ├── index.css          # Tailwind 진입점
        ├── components/
        │   ├── Header.jsx
        │   ├── SearchForm.jsx
        │   ├── MemeGrid.jsx
        │   └── MemeModal.jsx
        └── assets/            # 로고 등 이미지 리소스
```

---

## 4. 로컬 실행 가이드

### 사전 준비물

- Python 3.11 이상, [Poetry](https://python-poetry.org/)
- Node.js (npm 포함)
- 이미 구성된 Supabase 프로젝트 — Storage 버킷 `memes`(public, 감정별 폴더: joy/sadness/anger/anxiety/embarrassment/hurt/neutral)와 테이블 `public.memes`(id, emotion, title, image_path, created_at)
- API 키
  - `ANTHROPIC_API_KEY`: Anthropic API 키
  - `SUPABASE_URL`, `SUPABASE_KEY`: Supabase 프로젝트 URL과 API 키 (Project Settings > API). RLS로 `public.memes`의 공개 SELECT가 막혀 있다면 anon key 대신 service_role key 필요 — 백엔드 전용이라 프론트엔드에 노출되지 않음
  - `ALLOWED_ORIGINS`: (선택) CORS 허용 도메인, 로컬 개발은 기본값(`localhost:5173`)으로 충분
  - `VITE_API_BASE_URL`: (선택, 프론트엔드) 로컬 개발은 비워두면 됨 — Vite 프록시 사용

### 1) 환경변수 설정

`backend/.env.example`을 복사해 `backend/.env`를 생성합니다 (`.gitignore`에 등록되어 있어 커밋되지 않습니다).

```env
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your-supabase-key
ALLOWED_ORIGINS=http://localhost:5173
```

### 2) 백엔드 실행

```bash
cd backend
poetry install
poetry run uvicorn agent.app:app --reload --app-dir src --port 8000
```

- 정상 실행 시 `http://localhost:8000/api/memes?emotion_text=오늘 너무 슬퍼` 로 확인 가능합니다.

### 3) 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

- 기본적으로 `http://localhost:5173` 에서 접속 가능하며, `/api` 요청은 Vite 프록시를 통해 백엔드(`localhost:8000`)로 전달됩니다.
- 백엔드와 프론트엔드를 **모두 실행한 상태**여야 정상 동작합니다.

### 4) 백엔드 테스트 실행

```bash
cd backend
poetry install --with dev
poetry run pytest
```

- 외부 API(Anthropic, Supabase)는 모두 mock 처리되어 있어 API 키 없이도 실행됩니다.

### 참고

- 백엔드 포트를 8000이 아닌 다른 포트로 바꾸는 경우 [frontend/vite.config.js](frontend/vite.config.js)의 proxy 대상 주소도 함께 변경해야 합니다.

---

## 5. 배포 시 주의사항

로컬 개발과 달리 프론트엔드/백엔드가 서로 다른 도메인에 배포되므로 아래 두 가지를 반드시 설정해야 합니다.

- **프론트엔드**: 배포 환경에 `VITE_API_BASE_URL=https://your-backend-domain.com` 설정 (Vite 프록시는 `npm run dev` 개발 서버 전용 기능이라 빌드된 프로덕션 번들에는 적용되지 않습니다)
- **백엔드**: 배포 환경에 `ALLOWED_ORIGINS=https://your-frontend-domain.com` 설정 (미설정 시 로컬 개발 서버만 허용되어 배포된 프론트엔드에서 요청이 CORS로 막힙니다)
- 백엔드 시작 커맨드는 로컬과 동일: `uvicorn agent.app:app --app-dir src --port $PORT` (`--reload`는 프로덕션에서 제외)
- 배포 플랫폼의 헬스체크 경로는 `/` 또는 `/health` 아무거나 사용 가능
