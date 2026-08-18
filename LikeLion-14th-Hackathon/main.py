from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 각 캐릭터의 응답 로직을 불러옵니다.
# sessions 딕셔너리도 함께 불러와서, 질문 횟수 확인(차단 판단)에만 사용합니다.
# (질문 횟수를 증가시키는 로직 자체는 각 캐릭터 파일 내부에만 있고, 여기서는 건드리지 않습니다.)
from felix import get_felix_response, sessions as felix_sessions
from emil import get_emil_response, sessions as emil_sessions
from johannes import get_johannes_response, sessions as johannes_sessions
from klara import get_klara_response, sessions as klara_sessions

app = FastAPI(title="MCM 1976 해커톤 AI 챗봇 서버")

# 캐릭터별 최대 허용 질문 횟수 (4번째 질문부터 차단)
MAX_QUESTIONS = 3

# 4번째 질문부터 고정으로 반환할 차단 메시지 (텍스트 완전 일치 필요)
BLOCKED_MESSAGE = "더 이상 질문할 수 없습니다. 현장 단서를 확인하세요."


def is_blocked(sessions_dict: dict, session_id: str) -> bool:
    """
    해당 캐릭터의 세션 저장소에서 현재까지 누적된 질문 횟수를 확인합니다.
    이미 MAX_QUESTIONS(3)번 질문한 상태라면, 이번 요청은 4번째 질문이므로 차단 대상입니다.
    ※ 여기서는 카운트를 증가시키지 않습니다. 증가는 각 캐릭터 파일의 get_xxx_response 내부에서만 일어납니다.
    """
    session = sessions_dict.get(session_id)
    if session is None:
        return False
    return session.get("count", 0) >= MAX_QUESTIONS

# CORS 설정: 프론트엔드 도메인에서 통신이 가능하도록 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시 프론트엔드 URL만 넣는 것을 권장합니다 (예: ["https://my-frontend.com"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 프론트엔드에서 보내올 JSON 데이터 형식 정의
class ChatRequest(BaseModel):
    session_id: str  # 사용자 구분을 위한 고유 ID (프론트엔드에서 생성하여 전송)
    message: str     # 사용자가 입력한 질문

@app.post("/chat/felix")
async def chat_felix(request: ChatRequest):
    if is_blocked(felix_sessions, request.session_id):
        return {"reply": BLOCKED_MESSAGE}
    reply = await get_felix_response(request.session_id, request.message)
    return {"reply": reply}

@app.post("/chat/emil")
async def chat_emil(request: ChatRequest):
    if is_blocked(emil_sessions, request.session_id):
        return {"reply": BLOCKED_MESSAGE}
    reply = await get_emil_response(request.session_id, request.message)
    return {"reply": reply}

@app.post("/chat/johannes")
async def chat_johannes(request: ChatRequest):
    if is_blocked(johannes_sessions, request.session_id):
        return {"reply": BLOCKED_MESSAGE}
    reply = await get_johannes_response(request.session_id, request.message)
    return {"reply": reply}

@app.post("/chat/klara")
async def chat_klara(request: ChatRequest):
    # 클라라는 get_klara_response가 {"reply": ..., "suggestions": [...]} 형태의
    # dict를 반환하므로, 차단 시에도 형태를 맞춰서 suggestions: [] 를 같이 내려준다.
    if is_blocked(klara_sessions, request.session_id):
        return {"reply": BLOCKED_MESSAGE, "suggestions": []}
    result = await get_klara_response(request.session_id, request.message)
    return result
