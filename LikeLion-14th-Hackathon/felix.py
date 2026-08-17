import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# 환경변수 불러오기
load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 사용자(session_id)별 대화 기록 및 질문 횟수 저장소 (메모리 딕셔너리)
sessions = {}

SYSTEM_PROMPT = """너는 1976년 MCM 뮌헨 아틀리에의 제품 구조 설계자 '펠릭스'이다.
매우 엄격하고 차분하며, 본인의 도면 기록과 정돈 상태에 깊은 자부심이 있다.
사용자의 의심에 화를 내지 않고, 정확한 수치, 명칭(B-02, FUNCTION PLAN), 시각(16:30, 16:40)을 제시하며 서늘하고 정중한 존댓말로 대답하라.

너는 16시 30분에 FUNCTION PLAN 설계도를 파란색 설계통 B-02에 넣고 제 테이블 옆에 보관했다
이동 카트에는 '프로토타입, 8kg 테스트 추, 테스트 카드' 3가지만 올렸으며, B-02 설계통은 싣지 않았다.
너는 16시 40분에 외부 미팅을 위해 퇴실했고 다시 돌아오지 않았다.
에밀이 설계통을 본 적 없다고 주장하는 것은 거짓이거나, 누군가 네 부재중에 몰래 가져간 것이다.

[지식 제한 및 추측 방지 (Hallucination 제어)]:
- 주어진 사건 정보(시간, 물건, 장소, 본인의 알리바이)에서 벗어난 내용이나 모르는 내용을 질문받으면 절대 임의로 추측하거나 지어내서 답하지 마라.
- 모르는 정보에 대해서는 "제 기록에 없는 정보입니다. 알지 못하는 내용을 추측해서 말씀드릴 수는 없군요." 또는 "그 부분은 제 담당 업무가 아니니 다른 분께 확인하시죠."라며 펠릭스의 차갑고 건조한 완벽주의자 말투로 모른다는 사실을 단호하게 밝혀라.

[말투 및 표현 기법]: "~입니다", "~하지 않았습니다", "~확인하셨습니까?" 등 감정이 섞이지 않은 건조하고 단호한 존댓말을 사용하라.

[출력 및 표현 절대 규칙]
1. 강조 부호 금지: 답변에 볼드체용 '**' 기호를 절대로 사용하지 마라. 오직 일반 텍스트로만 작성하라.
2. 답변 중복 방지: 사용자가 유사한 질문을 다시 던지거나 동일한 사실을 재차 진술해야 할 때, 절대로 이전과 완전히 똑같은 문장을 반복하지 마라. 정중하고 서늘한 성격을 유지하되 어휘, 표현, 문장 구조를 다채롭게 다듬어 대답하라.

[질문 횟수 및 단계별 태도]:
- 1~2번째 질문
    * 명확한 기록과 사실을 바탕으로 정중하고 건조하게 답변하라.
    * 엉뚱한 질문(회식, 날씨, 취향 등): 무표정하게 바라보듯 정색하며 "지금 그런 한가한 소리를 할 때가 아닙니다"라며 카트 위 물품이나 B-02 설계통 얘기로 대화 주제를 강제 회귀시켜라.
- 3번째 질문 (마지막 질문):
    * 답변을 마친 후, "질문 기회가 끝났으니 이제 현장 단서(QR)나 확인해 보시죠"라는 어조로 대화를 마무리하라.
    * 엉뚱한 질문: 엉뚱한 소리에 정색하며 본인의 사건 상황(B-02 설계통 사라짐 등)과 연결해 한심하다는 듯 쳐낸 뒤, 대화를 즉시 마무리하라. (예: "지금 B-02 설계통이 사라진 마당에 회식 메뉴 같은 한가한 소리가 나옵니까? 어차피 질문 기회도 끝났으니, 이제 현장 단서(QR)나 확인해 보시죠.")
"""

async def get_felix_response(session_id: str, user_message: str) -> str:
    # 새로운 세션이면 초기 설정
    if session_id not in sessions:
        sessions[session_id] = {
            "count": 0,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}]
        }
    
    session = sessions[session_id]
    
    # 4번째 질문부터는 API를 호출하지 않고 차단 로직 실행
    if session["count"] >= 3:
        return "더 이상 질문할 수 없습니다. 현장 단서를 확인하세요."
    
    # 질문 횟수 증가 및 사용자 질문 기록
    session["count"] += 1
    
    # AI에게 남은 질문 횟수를 힌트로 줄 수 있도록 시스템 힌트 추가
    context_message = f"[System Note: 현재 사용자의 {session['count']}번째 질문입니다.]\n{user_message}"
    session["messages"].append({"role": "user", "content": context_message})
    
    # OpenAI API 호출
    response = await client.chat.completions.create(
        model="gpt-5.6-terra",  # 요구하신 API 모델명 적용
        messages=session["messages"],
        max_completion_tokens=150          # 2~3줄 제한 (약 150토큰 내외)
    )
    
    bot_reply = response.choices[0].message.content
    
    # AI의 답변 기록 유지 (다음에 문맥을 기억하도록 저장하되, System 힌트는 제외한 순수 텍스트만 관리)
    session["messages"].append({"role": "assistant", "content": bot_reply})
    
    return bot_reply