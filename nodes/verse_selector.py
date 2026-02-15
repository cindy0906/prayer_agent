from dotenv import load_dotenv
from groq import Groq
import os
import re

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def select_verse(state):
    emotion = state["emotion"]
    event = state.get("event", "")

    prompt = f"""
    사용자의 상황: {event}
    사용자의 감정: {emotion}

    위 상황과 감정에 가장 위로가 되는 성경 구절을 하나 선택해주세요.
    구약과 신약 66권 전체에서 가장 적합한 구절을 골라주세요.

    중요한 규칙:
    - 반드시 한국어 개역개정 번역본으로 작성하세요.
    - 영어를 절대 포함하지 마세요.
    - 책 이름도 한국어로 작성하세요 (예: 시편, 이사야, 마태복음, 빌립보서).
    - 구절 본문과 출처만 출력하세요. 다른 설명은 절대 포함하지 마세요.

    형식:
    구절 본문 (책이름 장:절)

    예시:
    여호와는 나의 목자시니 내게 부족함이 없으리로다 (시편 23:1)
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    verse = response.choices[0].message.content.strip()

    # 여러 줄이면 첫 번째 유효한 줄만 사용
    for line in verse.split("\n"):
        line = line.strip()
        if line and re.search(r'\(.*\d+:\d+\)', line):
            verse = line
            break

    # 앞뒤 따옴표 제거
    verse = verse.strip('"\'""''')

    return {"verse": verse}
