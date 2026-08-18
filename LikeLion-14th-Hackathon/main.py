from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# 각 캐릭터의 응답 로직을 불러옵니다.
from felix import get_felix_response, get_felix_init
from emil import get_emil_response, get_emil_init
from johannes import get_johannes_response, get_johannes_init
from klara import get_klara_response, get_klara_init

app = FastAPI(title="MCM 1976 해커톤 AI 챗봇 서버")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

# ———————— 펠릭스 엔드포인트 ————————
@app.get("/chat/felix/init")
async def init_felix(session_id: str):
    # 예: GET /chat/felix/init?session_id=test_user_01
    return await get_felix_init(session_id)

@app.post("/chat/felix")
async def chat_felix(request: ChatRequest):
    return await get_felix_response(request.session_id, request.message)

# ———————— 에밀 엔드포인트 ————————
@app.get("/chat/emil/init")
async def init_emil(session_id: str):
    return await get_emil_init(session_id)

@app.post("/chat/emil")
async def chat_emil(request: ChatRequest):
    return await get_emil_response(request.session_id, request.message)

# ———————— 요하네스 엔드포인트 ————————
@app.get("/chat/johannes/init")
async def init_johannes(session_id: str):
    return await get_johannes_init(session_id)

@app.post("/chat/johannes")
async def chat_johannes(request: ChatRequest):
    return await get_johannes_response(request.session_id, request.message)

# ———————— 클라라 엔드포인트 ————————
@app.get("/chat/klara/init")
async def init_klara(session_id: str):
    return await get_klara_init(session_id)

@app.post("/chat/klara")
async def chat_klara(request: ChatRequest):
    return await get_klara_response(request.session_id, request.message)
