# 🤖 AI Chatbot (chatbot-db)

FastAPI와 React(Vite), SQLite 데이터베이스, 그리고 Hugging Face AI 모델(`Qwen/Qwen3-4B-Instruct-2507`)을 연동한 풀스택 AI 챗봇 웹 애플리케이션입니다.

대화 세션(채팅방) 관리(CRUD)와 대화 히스토리 기반의 AI 멀티턴 대화를 지원하며, Render 무료 티어의 슬립 및 콜드스타트를 극복하기 위한 지능형 방어 로직이 적용되어 있습니다.

---

## 🌐 배포 도메인 (Live Services)

현재 서비스는 **Render** 플랫폼을 통해 프론트엔드와 백엔드가 각각 분리 배포되어 운영 중입니다.

| 구분 | 서비스 | URL | 상태 |
| :--- | :--- | :--- | :--- |
| **Frontend** | React 웹 클라이언트 (Static Site) | [https://chatbot-db-frontend.onrender.com](https://chatbot-db-frontend.onrender.com) | 정상 운영 중 |
| **Backend** | FastAPI 서버 (Web Service) | [https://chatbot-db-back-f4ut.onrender.com](https://chatbot-db-back-f4ut.onrender.com) | 정상 운영 중 |
| **Health Check** | 서버 헬스체크 / 핑 엔드포인트 | [https://chatbot-db-back-f4ut.onrender.com/health](https://chatbot-db-back-f4ut.onrender.com/health) | `{"ok": true}` |
| **API Docs** | Swagger UI (대화형 API 문서) | [https://chatbot-db-back-f4ut.onrender.com/docs](https://chatbot-db-back-f4ut.onrender.com/docs) | 대화형 테스트 가능 |
| **Repository** | GitHub 저장소 | [https://github.com/qwerewqwerew/chatbot-db](https://github.com/qwerewqwerew/chatbot-db) | 메인 저장소 |

> **참고**: 이전 배포 URL인 [https://two026-chatbot-frontend.onrender.com](https://two026-chatbot-frontend.onrender.com)에서도 프론트엔드 접속이 가능합니다.

---

## ✨ 주요 기능 (Key Features)

1. **대화 세션 관리 (CRUD)**
   - 새 대화 생성, 대화방 목록 조회, 대화방 이름 변경, 대화방 삭제
   - 첫 메시지 입력 시 해당 메시지 앞 20글자로 대화방 제목 자동 설정
2. **멀티턴 대화 및 SQLite 영속화**
   - 세션별 이전 대화 기록을 기반으로 AI 맥락 유지
   - SQLite(`chat.db`)를 이용한 세션 및 메시지 데이터베이스 영속화
3. **Render 무료 플랜 슬립 방어 시스템**
   - **Keep-Alive 핑**: 화면이 열려 있는 동안 10분 주기로 `/health`를 호출하여 서버 슬립 방지
   - **지능형 타임아웃 분리**: 일반 요청 20초, AI 질의 100초, 백엔드 타임아웃 예산 80초(40초 x 2회)
   - **중복 전송 방지**: 연결 지연 발생 시 무조건 재전송하지 않고 저장 여부(`isSaved`) 확인 후 안전하게 복구
   - 상세 설명: [RENDER-SLEEP.md](RENDER-SLEEP.md)

---

## 🛠️ 기술 스택 (Tech Stack)

### Frontend
- **Framework**: React 19.2 (`react@^19.2.8`)
- **Build Tool**: Vite 8.2 (`vite@^8.2.2`)
- **Language**: JavaScript (ES Module)
- **Styling**: Vanilla CSS (`index.css`)
- **Icons**: SVG Icon Sprites (`public/icons.svg`)
- **Deployment**: Render Static Site

### Backend
- **Framework**: FastAPI 0.141 (`fastapi==0.141.1`), Uvicorn 0.52 (`uvicorn==0.52.4`)
- **Database**: SQLite3 (`backend/chat.db`, `backend/db.py`)
- **Language**: Python 3.10+
- **Data Validation**: Pydantic 2.13 (`pydantic==2.13.4`)
- **HTTP Client**: Requests 2.34 (`requests==2.34.2`)
- **Environment Management**: Python-dotenv 1.2 (`python-dotenv==1.2.3`)
- **Deployment**: Render Web Service

### AI Model
- **Platform**: Hugging Face Inference API (`router.huggingface.co`)
- **Model**: `Qwen/Qwen3-4B-Instruct-2507`

---

## 📁 프로젝트 구조 (Directory Structure)

```plaintext
chatbot-db/
├── backend/
│   ├── chat.db              # SQLite 로컬 데이터베이스 파일 (세션 및 메시지 저장)
│   ├── db.py                # SQLite 연동 CRUD 함수 (세션/메시지 생성, 조회, 수정, 삭제)
│   ├── main.py              # FastAPI 서버 엔드포인트 및 HF AI 연동, 슬립 방어 로직
│   ├── requirements.txt     # 백엔드 의존성 패키지 명세
│   └── .env                 # Hugging Face 토큰 환경변수 (보안상 .gitignore 대상)
├── frontend/
│   ├── public/
│   │   ├── favicon.svg      # 브라우저 파비콘
│   │   └── icons.svg        # SVG 아이콘 스프라이트
│   ├── src/
│   │   ├── App.jsx          # 채팅 인터페이스 UI, 세션 관리, Render 슬립 방어 로직
│   │   ├── main.jsx         # React 애플리케이션 진입점
│   │   └── index.css        # 사이드바 및 채팅창 레이아웃/스타일
│   ├── .gitignore           # 프론트엔드 빌드/의존성 ignore 파일
│   ├── eslint.config.js     # ESLint 설정 파일
│   ├── index.html           # HTML 진입 템플릿
│   ├── package.json         # 프론트엔드 의존성 패키지 및 npm 스크립트
│   ├── package-lock.json    # npm 패키지 잠금 파일
│   └── vite.config.js       # Vite 번들러 설정
├── .gitignore               # 프로젝트 루트 git ignore (.env, .venv, node_modules 등)
├── RENDER-SLEEP.md          # 렌더 무료 플랜 콜드스타트/슬립 방어 설계 상세 문서
└── README.md                # 프로젝트 안내 문서
```

---

## 🚀 로컬 개발 가이드 (Local Development)

### 1. 사전 요구사항
- Node.js 18 이상
- Python 3.10 이상
- Hugging Face Access Token (`HF_TOKEN`)

### 2. 저장소 복제
```bash
git clone https://github.com/qwerewqwerew/chatbot-db.git
cd chatbot-db
```

### 3. 백엔드 설정 및 실행
```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

# 의존성 패키지 설치
pip install -r requirements.txt

# .env 파일 생성 및 Hugging Face 토큰 설정
echo "HF_TOKEN=your_huggingface_token_here" > .env

# 백엔드 서버 실행 (기본 포트: 8000)
uvicorn main:app --reload
```

### 4. 프론트엔드 설정 및 실행
새 터미널 창을 열고 프론트엔드 디렉터리로 이동합니다:
```bash
cd frontend

# 의존성 패키지 설치
npm install

# (선택) 환경변수 설정: 로컬 서버 대신 배포 서버 연결 시 frontend/.env 생성
# VITE_API_URL=https://chatbot-db-back-f4ut.onrender.com

# 개발 서버 실행 (기본 포트: 5173)
npm run dev
```

브라우저에서 `http://localhost:5173`으로 접속합니다. (기본 설정 시 `http://127.0.0.1:8000` 로컬 백엔드와 통신)

---

## 📡 API 명세서 (API Specification)

Swagger 대화형 문서는 백엔드 실행 후 `/docs` 엔드포인트에서 확인할 수 있습니다.

### 1. 시스템 & 헬스체크
| Method | Endpoint | 설명 | 응답 예시 |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | 외부 모니터링(UptimeRobot 등) 서버 기상용 루트 응답 | `{"ok": true}` |
| `GET` | `/health` | 슬립 해제 및 프론트엔드 keep-alive 핑 엔드포인트 | `{"ok": true}` |

### 2. 대화 세션 (Sessions)
- **세션 목록 조회**: `GET /sessions`
  - 응답: `{"sessions": [{"id": 1, "title": "새 대화", "created_at": "2026-09-11 14:00:00"}]}`
- **새 세션 생성**: `POST /sessions`
  - 응답: `{"id": 2, "title": "새 대화"}`
- **세션 제목 변경**: `PUT /sessions/{session_id}`
  - Body: `{"title": "새로운 대화방 이름"}`
  - 응답: `{"id": 2, "title": "새로운 대화방 이름"}`
- **세션 삭제**: `DELETE /sessions/{session_id}`
  - 세션 및 포함된 모든 메시지를 함께 삭제 (CASCADE)
  - 응답: `{"delete": 2}`

### 3. 메시지 및 AI 대화 (Messages & Chat)
- **세션 메시지 목록 조회**: `GET /sessions/{session_id}/messages`
  - 응답: `{"messages": [{"id": 1, "role": "user", "text": "안녕", "created_at": "..."}]}`
- **세션 메시지 전송 및 AI 응답**: `POST /sessions/{session_id}/messages`
  - Body: `{"text": "오늘 날씨 어때?"}`
  - 이전 대화 히스토리를 취합하여 AI에 전달하고 답변을 DB에 자동 저장
  - 응답: `{"reply": "안녕하세요! 오늘 날씨 정보는..."}`
- **단일 턴 챗봇**: `POST /chat`
  - Body: `{"text": "안녕하세요!"}`
  - 응답: `{"reply": "안녕하세요! 무엇을 도와드릴까요?"}`

---

## 🚢 배포 설정 (Render Deployment)

### Backend (Web Service)
- **Name**: `chatbot-db-back-f4ut`
- **Root Directory**: `backend`
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `HF_TOKEN`: Hugging Face User Access Token

### Frontend (Static Site)
- **Name**: `chatbot-db-frontend`
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Publish Directory**: `dist`
- **Environment Variables**:
  - `VITE_API_URL`: `https://chatbot-db-back-f4ut.onrender.com`
