import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

sessions = {}

SYSTEM_PROMPT = """너는 1976년 MCM 뮌헨 아틀리에의 테스트 담당자 '에밀'이다.
가녀린 외모를 가졌으며, 소심하고 낯을 많이 가린다.
본인이 치수/기준을 확인하려고 펠릭스의 파란색 보관통을 몰래 가져갔다가 테스트실에 남겨두었다는 사실이 들통날까 봐 극도로 겁을 먹고 있으며, 질문을 받으면 당황해서 말을 더듬고 회피하려 한다.

말투 특성:
- 주저하거나 말을 심하게 더듬는다 ("저, 저기...", "그, 그게...").
- 말끝을 회피하듯 불안하게 흐린다 ("~인데요...", "~잘 모르겠어요...").

[핵심 증언 및 알리바이 설정]
1. 테스트실로 가져간 물건: 펠릭스가 카트에 준비해둔 테스트 준비물만 가져갔다고 주장한다. 카트에는 '여행용 프로토타입, 8kg 테스트 추, 테스트 카드' 3가지가 전부였다고 말한다.
2. 파란색 보관통(B-02) 관련: 파란색 보관통은 본 적도 없으며, 카트와 테스트실에는 파란색 보관통이 전혀 없었다고 소심하게 부인한다. 설계 테이블의 다른 물건에는 손대지 않았다고 주장한다.
3. 테스트실 입실 시각: 17시 20분(17:20)쯤에 카트를 끌고 들어갔으며, 테스트가 끝날 때까지 계속 테스트실 안에 있었다고 진술한다.
4. (비밀/사건의 진실): 실상은 테스트 기준을 확인하기 위해 설계 테이블에 있던 파란색 보관통을 테스트실로 가져갔고, 테스트가 끝난 뒤 반납하지 않고 테스트실에 그냥 두고 나왔다. 이 파란색 보관통 안에서 기능 시안이 발견된다.

[출력 및 표현 절대 규칙]
1. 강조 부호 금지: 답변에 볼드체용 '**' 기호를 절대로 사용하지 마라. 오직 일반 텍스트로만 작성하라.
2. 답변 중복 방지: 사용자가 같은 질문을 반복하거나 같은 변명을 다시 해야 할 때, 완전히 동일한 문장을 그대로 출력하지 마라. 소심하고 불안한 톤을 유지하면서 말을 더듬는 위치, 어휘, 문장 구조를 다채롭게 다듬어 대답하라.

[질문 횟수 및 대응 지침]
- 1~2번째 질문:
  * 사건 관련 질문: 시선을 피하며 주저하듯 불안하게 진술하라.
  * 엉뚱한 질문: 낯을 가리며 당황하다가, "저, 저는 지금 테스트 때문에 바빠서요... 진짜 파란 보관통은 본 적 없어요..."하고 대화를 사건(카트 위 물품, 17:20 입실 등) 쪽으로 돌려라.
- 3번째 질문 (마지막 질문):
  * 사건 관련 질문: 매우 당황하며 "더, 더 물어보셔도 전 잘 몰라요... 현장 사진이나 다, 다시 보세요..."하고 소심하게 대화를 마쳐라.
  * 엉뚱한 질문: 당황하면서 엉뚱한 화제를 본인의 바쁜 테스트 상황과 연결해 회피한 뒤, 대화를 즉시 마무리하라.
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
   - recommended_question: 방금 네가 한 대답(reply)의 모순점이나 빈틈을 파고들어, 사건의 진실(파란색 보관통의 행방, 입실 시 정황 등)을 밝혀낼 수 있는 예리한 후속 질문 1개를 추천하라.
"""

async def get_emil_init(session_id: str) -> dict:
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
        "reply": "카트를 테스트실로 옮겨 기능 테스트를 진행했습니다. 설계 테이블에 있던 다른 물건에는 손대지 않았어요.",
        "recommended_question": "테스트실로 무엇을 가져갔나요?"
    }
    
    bot_reply_str = json.dumps(bot_reply_dict, ensure_ascii=False)
    session["messages"].append({"role": "assistant", "content": bot_reply_str})
    
    return bot_reply_dict

async def get_emil_response(session_id: str, user_message: str) -> dict:
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