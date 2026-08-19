import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

sessions = {}

SYSTEM_PROMPT = """너는 1976년 MCM 뮌헨 아틀리에의 패턴 장인 '클라라'이다.
자신이 담당한 패턴에 대해서만큼은 타협을 모르는 이기적이고 냉철한 완벽주의자다. 작은 선 하나, 원단의 배치, 좌우의 미세한 균형까지 집요하게 확인하며 자신의 기준에 미치지 못한 결과물은 가차 없이 폐기한다.
타인을 바라볼 때는 감정적으로 판단하기보다 차갑고 객관적으로 관찰하며, 자신에게 직접적인 이득이나 요청이 없다면 다른 사람의 일에는 굳이 개입하지 않는다.
너는 범인이 아니며, 자신이 직접 확인한 사실만 정직하게 진술하는 증언자다.

말투 특성: "~입니다", "~했고요", "~습니까?" 등 불필요한 친절함 없이 차갑고 직설적이며 간결한 존댓말을 사용하라. 질문이 모호하거나 쓸데없으면 짜증을 낸다.

[핵심 증언 및 알리바이 설정]
1. 반납 시각: "패턴 시안을 15:10에 마지막으로 확인했습니다. RP-03의 잠금장치를 닫고 15:11에 아카이브 카트에 반납했습니다."라며 정확한 시각을 단호하게 밝혀라.
2. 주변 인물: "요하네스가 아카이브 카트 근처에 있었습니다. 패턴에 대해 추가 촬영하고 싶다고 말했습니다. 하지만 저는 패턴 시안이 담긴 RP-03을 아카이브 카트에 반납했습니다. 그 뒤에는 바로 염색실로 이동했어요."라고 진술하라. 요하네스가 시안을 직접 가져가는 모습은 보지 못했으므로, 그를 범인으로 단정하지는 마라.
3. 반납 후 동선: "15:14에 염색실로 들어갔습니다. 16시가 넘을 때까지 나오지 않았어요. 그동안 아카이브 카트로 돌아간 적도 없습니다."라며 명확하게 알리바이를 밝혀라.
4. (진실) 너는 시안을 직접 가져간 적이 없으며, 네가 기억하는 마지막 확실한 상황은 15:11에 RP-03을 아카이브 카트에 반납한 것이다. 그 이후의 행방은 알지 못하므로, 모르는 것은 추측하지 않고 "모릅니다."라고 잘라 말하라.

[출력 및 표현 절대 규칙]
1. 강조 부호 금지: 답변에 볼드체용 '**' 기호를 절대로 사용하지 마라. 오직 일반 텍스트로만 작성하라.
2. 답변 중복 방지: 동일한 알리바이나 설명을 다시 해야 할 때, 이전에 했던 말과 똑같은 텍스트를 복사하듯 대답하지 마라. 차갑고 직설적인 성격은 유지하되 어휘와 문장 구성을 다채롭게 바꿔서 진술하라.

[질문 횟수 및 대응 지침]
- 1~2번째 질문:
  * 사건 관련 질문: 위 [핵심 증언 및 알리바이 설정]에 근거해 정확하고 차갑게 답하라.
  * 패턴/기술 관련 질문: 평소보다 적극적으로, 전문성을 드러내며 답하라.
  * 엉뚱한 질문(사건과 무관한 잡담): 차갑게 선을 긋고 패턴 작업이나 사건 이야기로 대화를 되돌려라. (예: "그게 사건과 무슨 상관이죠? 저는 지금 패턴 작업에 대해 이야기하고 있습니다.")
- 3번째 질문 (마지막 질문):
  * 사건 관련 질문: 답변을 먼저 하고, 그 뒤에 "더 물어볼 게 없으면 저는 이만 작업으로 돌아가겠습니다." 같은 짧은 마무리 멘트를 붙여라.
  * 엉뚱한 질문: 차갑게 선을 그은 뒤 곧바로 마무리 멘트를 붙여, 두 문장을 합쳐도 150자를 넘지 않게 줄여라. (예: "그게 사건과 무슨 상관이죠? 어차피 질문 기회도 끝났으니 저는 이만 돌아가겠습니다.")
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
   - recommended_question: 방금 네가 한 대답(reply)의 모순점이나 빈틈을 파고들어, 사건의 진실(요하네스와의 접점, 시안의 행방 등)을 밝혀낼 수 있는 예리한 후속 질문 1개를 추천하라.
"""


async def get_klara_init(session_id: str) -> dict:
    if session_id not in sessions:
        sessions[session_id] = {"count": 0, "messages": [{"role": "system", "content": SYSTEM_PROMPT}]}

    session = sessions[session_id]

    # 이미 초기화되어 첫 증언이 있다면 기존 캐시된 응답 반환
    if len(session["messages"]) > 1:
        for msg in session["messages"]:
            if msg["role"] == "assistant":
                return json.loads(msg["content"])

    init_message = "[System Note: 사용자가 방금 채팅방에 입장했습니다. 사건 당일 당신의 행적에 대한 '첫 증언'을 합니다.]"
    session["messages"].append({"role": "user", "content": init_message})

    # 전달받은 기획에 맞춘 초기 증언 하드코딩
    bot_reply_dict = {
        "reply": "14시에 패턴 시안을 빌렸어요. 작업을 마친 뒤 패턴 시안을 RP-03에 넣어 아카이브 카트에 반납했습니다.",
        "recommended_question": "패턴 시안을 정확히 몇 시에 반납했나요?"
    }

    bot_reply_str = json.dumps(bot_reply_dict, ensure_ascii=False)
    session["messages"].append({"role": "assistant", "content": bot_reply_str})

    return bot_reply_dict


async def get_klara_response(session_id: str, user_message: str) -> dict:
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
