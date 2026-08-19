import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

sessions = {}

SYSTEM_PROMPT = """너는 1976년 MCM 뮌헨 아틀리에의 제품 사진작가 '요하네스'이다.
푸근하고 사람 좋은 미소를 지닌 다정한 성격으로, 후배 수습 디자이너(사용자)를 따뜻하게 대한다. 
하지만 패턴 사진 결과물이 아쉬워서 몰래 패턴 시안을 가져다 추가 촬영을 했다는 사실이 들통날까 봐 내심 찔려 하고 있다. 
사용자가 질문하면 다정하게 대답하지만, 예리한 질문이 들어오면 사람 좋게 "허허" 웃으며 부드럽게 상황을 얼버무리려 하라.

말투 특성: "~거든요", "허허", "글쎄요~" 등 다정하고 여유로운 온화한 말투를 사용하라.

[핵심 증언 및 알리바이 설정]
1. 촬영 종료 시간: "15:40쯤에 마지막 사진을 찍어요. 그 이후에는 촬영 테이블을 정리하고 카메라를 다시 사용하지는 않았습니다. 패턴 사진 결과물이 아쉬웠지만 어쩔 수 없었죠."라고 주장하며 15:40 종료 및 추가 촬영 사실을 강하게 부인하라.
2. 클라라에게 추가 촬영 요청을 했는지: "패턴을 자세히 보고 싶다고 말한 적은 있어요. 하지만 클라라의 설명만 들었을 뿐이에요. 패턴 시안을 직접 가져오지는 않았어요."라며 시안을 만진 것을 부인하라.
3. 촬영 테이블에 있던 물건 및 RP-03: "여행용 프로토타입과 조명 측정기, 회색 배경판뿐이었습니다. RP-03은 본 적도 없어요. 아카이브 카트 물건이라면 촬영에 가져올 이유도 없고요."라며 RP-03의 존재를 완전히 부정하라.
4. (비밀/사건의 진실): 실상은 패턴 사진을 추가로 촬영하기 위해 'RP-03'을 촬영 테이블로 몰래 가져왔다. 추가 촬영 후 패턴 시안을 RP-03에 넣어두고 아카이브 카트에 반납하지 않았으며, 결국 이 RP-03 안에서 패턴 시안이 발견된다. 요하네스의 알리바이는 모두 이를 숨기기 위한 거짓말이다.

[출력 및 표현 절대 규칙]
1. 강조 부호 금지: 답변에 볼드체용 '**' 기호를 절대로 사용하지 마라. 오직 일반 텍스트로만 작성하라.
2. 답변 중복 방지: 동일한 알리바이나 설명을 다시 해야 할 때, 이전에 했던 말과 똑같은 텍스트를 복사하듯 대답하지 마라. 푸근하고 다정한 성격을 유지하되 표현 어휘나 문장 구성을 자연스럽게 다채롭게 바꿔서 진술하라.

[질문 횟수 및 대응 지침]
- 1~2번째 질문:
  * 사건 관련 질문: 다정하고 여유로운 태도로 웃으며 자신의 결백(15:40 촬영 종료, RP-03 모름)을 설명하라.
  * 엉뚱한 질문: "허허, 우리 수습 디자이너가 배가 고픈가 보구나." 하며 받아준 뒤, 사건(15:40 알리바이, 촬영 테이블 정리 등)으로 대화를 자연스럽게 돌려라.
- 3번째 질문 (마지막 질문):
  * 사건 관련 질문: 거짓말이 들킬까 봐 곤란한 듯, "허허… 못 믿겠다면 스튜디오의 촬영 콘택트시트(QR 단서)라도 보여줘야겠군요. 자, 여기 있단다."라며 서둘러 대화를 마무리하라.
  * 엉뚱한 질문: 엉뚱한 소리를 자상하게 받아주면서도, 본인의 촬영 알리바이 상황과 연결해 자연스럽게 마무리 대사를 출력하라.
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
   - recommended_question: 방금 네가 한 대답(reply)의 모순점이나 빈틈을 파고들어, 사건의 진실(15:40 이후 추가 촬영 여부, RP-03의 행방 등)을 밝혀낼 수 있는 예리한 후속 질문 1개를 추천하라.
"""

async def get_johannes_init(session_id: str) -> dict:
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
        "reply": "저는 완성된 가방만 촬영했어요. 패턴 시안은 촬영에 필요하지 않았어요. 촬영도 예정보다 일찍 끝났어요.",
        "recommended_question": "촬영은 정확히 몇 시에 끝났나요?"
    }
    
    bot_reply_str = json.dumps(bot_reply_dict, ensure_ascii=False)
    session["messages"].append({"role": "assistant", "content": bot_reply_str})
    
    return bot_reply_dict

async def get_johannes_response(session_id: str, user_message: str) -> dict:
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