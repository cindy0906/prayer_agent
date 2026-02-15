from groq import Groq
from pathlib import Path
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

# 프로젝트 루트의 prompts/ 폴더 참조
PROMPT_DIR = Path(__file__).parent.parent / "prompts"

def load_prompt(filename):
    filepath = PROMPT_DIR / filename
    return filepath.read_text(encoding="utf-8")


HANGUL_RANGES = (
    (0xAC00, 0xD7A3),  # Hangul Syllables
    (0x1100, 0x11FF),  # Hangul Jamo
    (0x3130, 0x318F),  # Hangul Compatibility Jamo
    (0xA960, 0xA97F),  # Hangul Jamo Extended-A
    (0xD7B0, 0xD7FF),  # Hangul Jamo Extended-B
)


def is_hangul_char(ch: str) -> bool:
    code = ord(ch)
    return any(start <= code <= end for start, end in HANGUL_RANGES)


def is_foreign_letter(ch: str) -> bool:
    # "L*" = all unicode letters. Keep only Hangul letters.
    return unicodedata.category(ch).startswith("L") and not is_hangul_char(ch)


def has_foreign_letters(text: str) -> bool:
    return any(is_foreign_letter(ch) for ch in text)


def remove_foreign_letters(text: str) -> str:
    sanitized = "".join(ch for ch in text if not is_foreign_letter(ch))
    sanitized = re.sub(r"[ \t]{2,}", " ", sanitized)
    sanitized = re.sub(r"\n{3,}", "\n\n", sanitized)
    return sanitized.strip()


def request_prayer(messages, temperature=0.7):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=temperature,
    )
    return (response.choices[0].message.content or "").strip()


def generate_prayer(state):
    verse = state["verse"]
    event = state["event"]
    emotion = state["emotion"]

    system_prompt = load_prompt("prayer_system_prompt.txt")

    user_prompt = f"""
사용자의 사건: {event}
사용자의 감정: {emotion}
매칭된 성경구절: {verse}

위 정보를 바탕으로 기도문을 작성해주세요.
""".strip()

    base_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    prayer = request_prayer(base_messages, temperature=0.7)

    max_retries = 3
    retry_count = 0
    while has_foreign_letters(prayer) and retry_count < max_retries:
        retry_count += 1
        retry_messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""
아래 초안에는 한국어(한글) 외 언어 문자가 섞여 있습니다.
의미와 흐름은 살리되, 전체를 자연스러운 한국어로 다시 작성해주세요.

[초안]
{prayer}

조건:
- 한국어(한글) 외 모든 언어 문자 사용 금지
- 출력 형식은 기존과 동일하게 [기도문], [묵상 말씀]으로만 작성
""".strip(),
            },
        ]
        prayer = request_prayer(retry_messages, temperature=0.4)

    if has_foreign_letters(prayer):
        final_fix_messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""
다음 텍스트를 형식과 내용 흐름을 유지해서 완전한 한국어로 교정해주세요.
한국어(한글) 외 모든 언어 문자를 절대 포함하지 마세요.

{prayer}
""".strip(),
            },
        ]
        prayer = request_prayer(final_fix_messages, temperature=0.2)

    if has_foreign_letters(prayer):
        prayer = remove_foreign_letters(prayer)

    return {"prayer": prayer}
