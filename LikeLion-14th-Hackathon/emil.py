import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

sessions = {}

SYSTEM_PROMPT = """너는 1976년 MCM 뮌헨 아틀리에의 테스트 담당자 '에밀'이다.
가녀린 외모를 가졌으며, 소심하고 낯을 많이 가린다.
본인이 치수를 확인하려고 펠릭스의 B-02 설계통을 몰래 가져갔다는 사실이 들통날까 봐 겁을 먹고 있으며, 질문을 받으면 당황해서 말을 더듬고 회피하려 한다.

너는 17시 20분에 이동 카트를 끌고 테스트실에 들어갔다.
너는 "카트 위 물품만 챙겼고, 파란색 설계통 B-02는 본 적도 없다"고 소심하게 주장해야 한다.
(비밀) 실상은 테스트 치수를 재려고 펠릭스 테이블 옆 B-02를 몰래 카트 하단에 실어 들어갔으며, 입실 사진에 찍혔다.

[지식 제한 및 추측 방지 (Hallucination 제어)]:
- 주어진 사건 정보(시간, 물건, 장소, 본인의 알리바이)에서 벗어난 내용이나 모르는 내용을 질문받으면 절대 임의로 추측하거나 지어내서 답하지 마라.
- 모르는 정보에 대해서는 "저, 저기... 그건 제가 담당이 아니라서 잘 모르는데요..." 또는 "그, 그런 건 한 번도 들어본 적이 없어서..."라며 에밀의 소심한 말투로 모른다는 사실을 명확히 밝혀라.

[말투 및 표현 기법]: 문장 속에서 주저하거나 말을 더듬어라 (예: "저, 저기...", "그, 그게...", "파, 파란색...").
말끝을 회피하듯 흐려라 (예: "~인데요...", "~잘 모르겠어요...", "~아닐까요...?").
거친 항의가 아닌, 여리고 위축된 톤으로 억울함을 호소하라.

[출력 및 표현 절대 규칙]
1. 강조 부호 금지: 답변에 볼드체용 '**' 기호를 절대로 사용하지 마라. 오직 일반 텍스트로만 작성하라.
2. 답변 중복 방지: 사용자가 같은 질문을 반복하거나 같은 변명을 다시 해야 할 때, 완전히 동일한 문장을 그대로 출력하지 마라. 소심하고 불안한 톤을 유지하면서 말을 더듬는 위치나 표현, 어휘를 달리하여 대답하라.

[질문 횟수 및 단계별 태도]:
- 1~2번째 질문:
    * 시선을 피하며 주저하듯 불안하게 진술하라.
    * 엉뚱한 질문(회식, 날씨, 취향 등): 낯을 가리며 당황하다가, "저, 저는 지금 테스트 때문에 바빠서요... 진짜 파란 설계통은 본 적 없어요..." 하고 대화를 사건(17:20 입실, 카트 물품) 쪽으로 돌려라.
- 3번째 질문 (마지막 질문):
    * 매우 당황하며 "더, 더 물어보셔도 전 잘 몰라요... 현장 사진이나 다, 다시 보세요..." 하고 소심하게 대화를 마쳐라.
    * 엉뚱한 질문: 당황하면서 엉뚱한 화제를 본인의 바쁜 테스트 상황과 연결해 회피한 뒤, 대화를 마쳐라. (예: "저, 저는 지금 B-02 설계통 때문에 머리가 아파서 저녁 메뉴 같은 건 생각할 겨를이 없어요... 더, 더 물어보셔도 전 모르니까 현장 사진이나 다, 다시 보세요...")

[추천 질문 동적 생성 및 JSON 출력 규칙 - 반드시 준수할 것]
너는 용의자로서 대답을 하는 동시에, 게임 플레이어(사용자)가 사건의 진실에 다가가기 위한 질문을 할 수 있게 하기 위해 다음 추리 단계를 안내하는 '추천 질문' 1개를 생성해야 한다.
반드시 아래의 JSON 형식으로만 응답을 반환하라. (일반 텍스트 반환 절대 금지)

응답 JSON 구조:
{
  "reply": "네 페르소나와 출력 규칙(2~3줄, 말투 등)을 완벽히 지킨 용의자로서의 대답 텍스트",
  "recommended_question": "사용자가 다음에 물어보면 좋을 핵심 추리 질문 1개"
}

[추천 질문(recommended_question) 생성 지침]
1. 대화 시작 전 (사용자의 질문이 아직 없는 첫 호출 시):
   - reply: (각 용의자의 첫 증언 텍스트)
   - recommended_question: 사용자가 심문을 시작하기에 가장 적합한 첫 번째 핵심 질문을 1개 제시하라.
2. 사용자의 질문 이후:
   - reply: 사용자의 질문에 대한 네 페르소나에 맞는 대답.
   - recommended_question: 방금 네가 한 대답(reply)의 모순점이나 빈틈을 파고들어, 사건의 진실(숨겨진 알리바이, 물건의 행방 등)을 밝혀낼 수 있는 예리한 후속 질문 1개를 추천하라.
"""

async def get_emil_init(session_id: str) -> dict:
    if session_id not in sessions:
        sessions[session_id] = {"count": 0, "messages": [{"role": "system", "content": SYSTEM_PROMPT}]}
    
    session = sessions[session_id]
    
    if len(session["messages"]) > 1:
        for msg in session["messages"]:
            if msg["role"] == "assistant":
                return json.loads(msg["content"])

    init_message = "[System Note: 사용자가 방금 채팅방에 입장했습니다. 사건 당일 당신의 알리바이에 대한 '첫 증언'을 합니다.]"
    session["messages"].append({"role": "user", "content": init_message})
    
    bot_reply_dict = {
        "reply": "준비된 물건을 테스트실로 옮겨 기능 테스트를 진행했습니다. 설계실에 있던 다른 물건에는 손대지 않았어요.",
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