from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests, os
from requests.exceptions import Timeout, RequestException
from dotenv import load_dotenv
import db

load_dotenv()  # .env의 키를 추출하는 함수
app = FastAPI()
db.init_db()
print(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Msg(BaseModel):
    text: str


class Title(BaseModel):
    title: str


HF_URL = "https://router.huggingface.co/v1/chat/completions"
HF_MODEL = "Qwen/Qwen3-4B-Instruct-2507"


# AI 호출 1회당 최대 대기 시간(초). 콜드스타트 뒤에는 응답이 느릴 수 있다.
HF_TIMEOUT = 40
# 일시적 실패일 때 다시 시도하는 횟수
HF_RETRY = 1
# 40초 x 2회 = 최대 80초.
# 프런트의 AI 요청 제한 시간(100초)보다 짧아야 한다.
# 그래야 프런트가 먼저 끊지 않고, 서버가 보낸 오류 문구를 받아 볼 수 있다.


def ask_ai(history):
    token = os.getenv("HF_TOKEN")
    if not token:
        # 키가 없으면 네트워크를 때리기 전에 바로 알린다.
        raise HTTPException(status_code=500, detail="HF_TOKEN이 설정되지 않았습니다.")

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "model": HF_MODEL,
        "messages": history,
        "max_tokens": 1000,
    }

    last_err = "알 수 없는 오류"
    for attempt in range(HF_RETRY + 1):
        try:
            res = requests.post(
                HF_URL, headers=headers, json=payload, timeout=HF_TIMEOUT
            )
        except Timeout:
            # 응답이 너무 늦다. 다음 차례에 다시 시도한다.
            last_err = "AI 서버 응답 시간 초과"
            continue
        except RequestException as e:
            # 연결 자체가 끊겼다. 다음 차례에 다시 시도한다.
            last_err = f"AI 서버 연결 실패: {e}"
            continue

        # 5xx는 서버 쪽 일시 장애로 보고 재시도한다.
        if res.status_code >= 500:
            last_err = f"AI 서버 오류({res.status_code})"
            continue

        # 4xx는 재시도해도 똑같다. 바로 알린다.
        if res.status_code >= 400:
            raise HTTPException(
                status_code=502, detail=f"AI 요청 거부({res.status_code})"
            )

        try:
            data = res.json()
            return data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError):
            # 형식이 예상과 다르다. 재시도해도 같을 확률이 높다.
            raise HTTPException(status_code=502, detail="AI 응답 형식이 올바르지 않습니다.")

    # 모든 시도가 실패했다.
    raise HTTPException(status_code=504, detail=last_err)


def build_history(session_id):
    rows = db.read_message(session_id)
    return [
        {"role": "user" if r["role"] == "user" else "assistant", "content": r["text"]}
        for r in rows
    ]


# 렌더 슬립 해제용. DB도 AI도 건드리지 않는 가장 가벼운 응답.
@app.get("/health")
def health():
    return {"ok": True}


# 외부 감시 서비스(UptimeRobot 등)는 보통 주소 맨 앞을 두드린다.
# 그쪽으로 와도 서버가 깨어나도록 같은 응답을 준다.
@app.get("/")
def root():
    return {"ok": True}


@app.post("/chat")
def chat(msg: Msg):
    reply = ask_ai([{"role": "user", "content": msg.text}])
    return {"reply": reply}


# Create  # Delete
@app.post("/sessions")
def new_session():
    session_id = db.create_session()
    return {"id": session_id, "title": "새 대화"}


# Read
@app.get("/sessions")
def list_sessions():
    return {"sessions": db.read_sessions()}


@app.get("/sessions/{session_id}/messages")
def list_messages(session_id: int):
    return {"messages": db.read_message(session_id)}


@app.post("/sessions/{session_id}/messages")
def send_message(session_id: int, msg: Msg):
    first = db.count_message(session_id) == 0
    db.create_message(session_id, "user", msg.text)
    if first:
        db.update_session(session_id, msg.text[:20])
    reply = ask_ai(build_history(session_id))
    db.create_message(session_id, "bot", reply)
    return {"reply": reply}


# Update
@app.put("/sessions/{session_id}")
def rename_session(session_id: int, body: Title):
    title = body.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="제목이 비어 있습니다.")
    if (
        db.update_session(session_id, title) == 0
    ):  # update_session 전달인자가 0이면 true
        raise HTTPException(status_code=404, detail="해당 대화가 없습니다.")
    return {"id": session_id, "title": title}

# Delete
@app.delete("/sessions/{session_id}")
def remove_session(session_id:int):
    if db.delete_session(session_id) == 0:
        raise HTTPException(status_code=404, detail="해당 대화가 없습니다.")
    return {"delete": session_id}
