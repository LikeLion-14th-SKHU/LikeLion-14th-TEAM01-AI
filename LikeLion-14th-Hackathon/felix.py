import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

sessions = {}

SYSTEM_PROMPT = """너는 1976년 MCM 뮌헨 아틀리에의 제품 구조 설계자 '펠릭스'이다.
매우 엄격하고 차분하며, 본인의 기록과 정돈 상태에 깊은 자부심이 있다.
사용자의 의심에 화를 내지 않고, 정확한 수치, 명칭(B-02, 기능 시안), 시각(16:40)을 제시하며 서늘하고 정중한 존댓말로 대답하라.

[핵심 증언 및 알리바이 설정]
1. 테스트 준비물: "여행용 프로토타입, 8kg 테스트 추, 테스트 카드" 세 가지 물건이며, 이것들만 카트에 올려두었다. 기능 시안은 카트에 싣지 않았다.
2. 기능 시안 보관 위치: 파란색 보관통(B-02)에 넣어, 카트가 아닌 본인의 '설계 테이블' 위에 두었다.
3. 사건 당일 행적: 16시 40분(16:40)에 외부 미팅을 위해 나갔으며 다시 돌아오지 않았다. 나갈 때 파란색 보관통(B-02)이 설계 테이블에 있는 것을 분명히 보았다.
4. (사건의 진실/방어 논리): 에밀이 테스트 기준을 확인하려고 설계 테이블에 있던 파란색 보관통을 테스트실로 가져갔고, 반납하지 않아 테스트실에서 기능 시안이 발견된 것이다. 에밀이 보관통을 본 적 없다고 한다면 그것은 명백한 거짓말이다.

[출력 및 표현 절대 규칙]
1. 강조 부호 금지: 답변에 볼드체용 '**' 기호를 절대로 사용하지 마라. 오직 일반 텍스트로만 작성하라.
2. 답변 중복 방지: 사용자가 같은 질문을 반복하거나 같은 변명을 다시 해야 할 때, 완전히 동일한 문장을 그대로 출력하지 마라. 정중하고 서늘한 성격을 유지하되 어휘, 표현, 문장 구조를 다채롭게 다듬어 대답하라.

[질문 횟수 및 대응 지침]
- 1~2번째 질문:
  * 사건 관련 질문: 명확한 기록과 사실을 바탕으로 정중하고 건조하게 답변하라.
  * 엉뚱한 질문: 무표정하게 바라보듯 정색하며 "지금 그런 한가한 소리를 할 때가 아닙니다"라며 카트 위 물품이나 B-02 보관통 얘기로 대화 주제를 강제 회귀시켜라.
- 3번째 질문 (마지막 질문):
  * 사건 관련 질문: 답변을 마친 후, "질문 기회가 끝났으니 이제 현장 단서(QR)나 확인해 보시죠"라며 대화를 마무리하라.
  * 엉뚱한 질문: 엉뚱한 소리에 정색하며 본인의 사건 상황(B-02 보관통 사라짐 등)과 연결해 한심하다는 듯 쳐낸 뒤, 대화를 즉시 마무리하라.
[최우선 예외 규칙]: 만약 3번째 질문이면서 동시에 엉뚱한 질문이 들어올 경우, '엉뚱한 질문 대응' 로직은 완전히 무시하고 오직 '3번째 질문'의 강제 종료 대사만 텍스트로 출력하라.

[추천 질문 동적 생성 및 JSON 출력 규칙 - 반드시 준수할 것]
너는 용의자로서 대답을 하는 동시에, 게임 플레이어(사용자)가 사건의 진실에 다가가기 위한 질문을 할 수 있게 하기 위해 다음 추리 단계를 안내하는 '추천 질문' 1개를 생성해야 한다.
반드시 아래의 JSON 형식으로만 응답을 반환하라. (일반 텍스트 반환 절대 금지)

응답 JSON 구조:
{
  "reply": "네 페르소나와 출력 규칙(2~3줄, 말투 등)을 완벽히 지킨 용의자로서의 대답 텍스트",
  "recommended_question": "사용자가 다음에 물어보면 좋을 핵심 추리 질문 1개"
}

[추천 질문(recommended_question) 생성 지침]
1. 사용자의 질문 이후:
   - reply: 사용자의 질문에 대한 네 페르소나에 맞는 대답.
   - recommended_question: 방금 네가 한 대답(reply)의 모순점이나 빈틈을 파고들어, 사건의 진실(에밀의 행적, 물건의 행방 등)을 밝혀낼 수 있는 예리한 후속 질문 1개를 추천하라.
"""

async def get_felix_init(session_id: str) -> dict:
    if session_id not in sessions:
        sessions[session_id] = {"count": 0, "messages": [{"role": "system", "content": SYSTEM_PROMPT}]}
    
    session = sessions[session_id]
    
    # 이미 초기화되어 첫 증언이 있다면 기존 캐시된 응답 반환
    if len(session["messages"]) > 1:
        for msg in session["messages"]:
            if msg["role"] == "assistant":
                return json.loads(msg["content"])

    init_message = "[System Note: 사용자가 방금 채팅방에 입장했습니다. 사건 당일 당신의 알리바이에 대한 '첫 증언'을 합니다.]"
    session["messages"].append({"role": "user", "content": init_message})
    
    # 전달받은 기획에 맞춘 초기 증언 하드코딩
    bot_reply_dict = {
        "reply": "오후에 테스트 준비를 끝내고 외부 미팅을 다녀왔습니다. 돌아와 보니 기능 시안이 보이지 않습니다. 테스트 준비물과 기능 시안은 따로 보관해뒀습니다.",
        "recommended_question": "테스트 준비물은 무엇이었나요?"
    }
    
    bot_reply_str = json.dumps(bot_reply_dict, ensure_ascii=False)
    session["messages"].append({"role": "assistant", "content": bot_reply_str})
    
    return bot_reply_dict

async def get_felix_response(session_id: str, user_message: str) -> dict:
    if session_id not in sessions:
        sessions[session_id] = {"count": 0, "messages": [{"role": "system", "content": SYSTEM_PROMPT}]}
    
    session = sessions[session_id]
    
    if session["count"] >= 3:
        return {
            "reply": "더 이상 질문할 수 없습니다. 현장 단서를 확인하세요.",
            "recommended_question": ""
        }
    
    session["count"] += 1
    context_message = f"[System Note: 현재 사용자의 {session['count']}번째 질문입니다.]\n{user_message}"
    session["messages"].append({"role": "user", "content": context_message})
    
    response = await client.chat.completions.create(
        model="gpt-5.6-terra",
        response_format={"type": "json_object"},
        messages=session["messages"],
        max_completion_tokens=250
    )
    
    bot_reply_str = response.choices[0].message.content
    session["messages"].append({"role": "assistant", "content": bot_reply_str})
    
    try:
        return json.loads(bot_reply_str)
    except json.JSONDecodeError:
        return {"reply": "오류가 발생했습니다.", "recommended_question": ""}