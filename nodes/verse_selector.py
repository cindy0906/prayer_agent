from groq import Groq
import os
import re
import unicodedata

try:
    import streamlit as st
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

HANGUL_RANGES = (
    (0xAC00, 0xD7A3),  # Hangul Syllables
    (0x1100, 0x11FF),  # Hangul Jamo
    (0x3130, 0x318F),  # Hangul Compatibility Jamo
    (0xA960, 0xA97F),  # Hangul Jamo Extended-A
    (0xD7B0, 0xD7FF),  # Hangul Jamo Extended-B
)


def is_hangul_char(ch):
    code = ord(ch)
    return any(start <= code <= end for start, end in HANGUL_RANGES)


def has_foreign_letters(text):
    for ch in text:
        if unicodedata.category(ch).startswith("L") and not is_hangul_char(ch):
            return True
    return False


def remove_foreign_letters(text):
    cleaned = "".join(
        ch for ch in text
        if not (unicodedata.category(ch).startswith("L") and not is_hangul_char(ch))
    )
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    return cleaned.strip()


def request_verse(messages, temperature=0.7):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=temperature,
    )
    return (response.choices[0].message.content or "").strip()


def extract_verse_line(text):
    """여러 줄 중 (책이름 장:절) 패턴이 있는 첫 줄만 추출"""
    for line in text.split("\n"):
        line = line.strip()
        if line and re.search(r'\(.*\d+:\d+\)', line):
            return line.strip('"\'""''')
    return text.strip('"\'""''')


BASE_PROMPT = """중요한 규칙:
- 반드시 한국어 개역개정 번역본으로 작성하세요.
- 한국어(한글) 외 모든 언어(영어, 일본어, 중국어 등)를 절대 포함하지 마세요.
- 책 이름도 한국어로 작성하세요 (예: 시편, 이사야, 마태복음, 빌립보서).
- 구절 본문과 출처만 출력하세요. 다른 설명은 절대 포함하지 마세요.

형식:
구절 본문 (책이름 장:절)

예시:
여호와는 나의 목자시니 내게 부족함이 없으리로다 (시편 23:1)"""


def select_verse(state):
    emotion = state["emotion"]
    event = state.get("event", "")

    prompt = f"""사용자의 상황: {event}
사용자의 감정: {emotion}

위 상황과 감정에 가장 위로가 되는 성경 구절을 하나 선택해주세요.
구약과 신약 66권 전체에서 가장 적합한 구절을 골라주세요.

{BASE_PROMPT}"""

    verse = request_verse([{"role": "user", "content": prompt}])
    verse = extract_verse_line(verse)

    # 외국어 감지 시 재시도 (최대 2회)
    retries = 0
    while has_foreign_letters(verse) and retries < 2:
        retries += 1
        retry_prompt = f"""아래 성경구절에 한국어가 아닌 문자가 포함되어 있습니다.
동일한 구절을 순수 한국어(한글)로만 다시 작성해주세요.

{verse}

{BASE_PROMPT}"""
        verse = request_verse(
            [{"role": "user", "content": retry_prompt}],
            temperature=0.3,
        )
        verse = extract_verse_line(verse)

    # 최종 폴백: 외국어 문자 강제 제거
    if has_foreign_letters(verse):
        verse = remove_foreign_letters(verse)

    return {"verse": verse}
