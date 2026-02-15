from dotenv import load_dotenv
from groq import Groq
import os
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_text(state):
    text = state.get("emotion", "")

    prompt = f"""
    다음 텍스트에서
    1. 사건(Event) - 핵심 키워드만 간결하게
    2. 감정(Emotion) - 핵심 감정 키워드만 간결하게

    을 분리해서 JSON 형식으로 출력하세요.
    여러 개인 경우 반드시 쉼표(,)로 구분하세요. 세미콜론(;)은 사용하지 마세요.
    반드시 JSON만 출력하고 다른 텍스트는 포함하지 마세요.

    텍스트:
    "{text}"

    출력 예시:
    {{
      "event": "중요한 시험, 취업 준비",
      "emotion": "불안, 걱정"
    }}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    content = response.choices[0].message.content.strip()

    # 마크다운 코드블록 제거
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]
        content = content.strip()

    try:
        result = json.loads(content)
        event = result.get("event", "알 수 없음")
        emotion = result.get("emotion", "알 수 없음")
    except:
        event = "분석 실패"
        emotion = "알 수 없음"

    return {"event": event, "emotion": emotion}
