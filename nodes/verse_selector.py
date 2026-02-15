from groq import Groq
import os
import re
import requests

try:
    import streamlit as st
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

# ── 성경 책 이름 → Bolls.life API book ID 매핑 ──
# 개역개정, 개역한글, LLM이 생성할 수 있는 다양한 변형 포함
BOOK_ALIASES = {
    # 구약
    "창세기": 1,
    "출애굽기": 2,
    "레위기": 3,
    "민수기": 4,
    "신명기": 5,
    "여호수아": 6, "여호수아기": 6,
    "사사기": 7,
    "룻기": 8, "룻": 8,
    "사무엘상": 9, "사무엘기상": 9,
    "사무엘하": 10, "사무엘기하": 10,
    "열왕기상": 11,
    "열왕기하": 12,
    "역대상": 13, "역대지상": 13,
    "역대하": 14, "역대지하": 14,
    "에스라": 15, "에스라기": 15,
    "느헤미야": 16, "느헤미야기": 16,
    "에스더": 17, "에스더기": 17,
    "욥기": 18, "욥": 18,
    "시편": 19,
    "잠언": 20,
    "전도서": 21,
    "아가": 22, "아가서": 22,
    "이사야": 23, "이사야서": 23,
    "예레미야": 24, "예레미야서": 24,
    "애가": 25, "예레미야애가": 25, "예레미야 애가": 25,
    "에스겔": 26, "에스겔서": 26,
    "다니엘": 27, "다니엘서": 27,
    "호세아": 28, "호세아서": 28,
    "요엘": 29, "요엘서": 29,
    "아모스": 30, "아모스서": 30,
    "오바댜": 31, "오바댜서": 31,
    "요나": 32, "요나서": 32,
    "미가": 33, "미가서": 33,
    "나훔": 34, "나훔서": 34,
    "하박국": 35, "하박국서": 35,
    "스바냐": 36, "스바냐서": 36,
    "학개": 37, "학개서": 37,
    "스가랴": 38, "스가랴서": 38,
    "말라기": 39, "말라기서": 39,
    # 신약
    "마태복음": 40, "마태복음서": 40, "마태": 40,
    "마가복음": 41, "마가복음서": 41, "마가": 41,
    "누가복음": 42, "누가복음서": 42, "누가": 42,
    "요한복음": 43, "요한복음서": 43,
    "사도행전": 44,
    "로마서": 45, "로마": 45,
    "고린도전서": 46, "코린도전서": 46,
    "고린도후서": 47, "코린도후서": 47,
    "갈라디아서": 48, "갈라디아": 48,
    "에베소서": 49, "에베소": 49,
    "빌립보서": 50, "빌립보": 50,
    "골로새서": 51, "골로새": 51,
    "데살로니가전서": 52, "살전": 52,
    "데살로니가후서": 53, "살후": 53,
    "디모데전서": 54,
    "디모데후서": 55,
    "디도서": 56, "디도": 56,
    "빌레몬서": 57, "빌레몬": 57,
    "히브리서": 58, "히브리": 58,
    "야고보서": 59, "야고보": 59,
    "베드로전서": 60,
    "베드로후서": 61,
    "요한일서": 62, "요한1서": 62,
    "요한이서": 63, "요한2서": 63,
    "요한삼서": 64, "요한3서": 64,
    "유다서": 65, "유다": 65,
    "요한계시록": 66, "계시록": 66,
}

# book ID → 표준 개역개정 이름
BOOK_ID_TO_NAME = {
    1: "창세기", 2: "출애굽기", 3: "레위기", 4: "민수기", 5: "신명기",
    6: "여호수아", 7: "사사기", 8: "룻기", 9: "사무엘상", 10: "사무엘하",
    11: "열왕기상", 12: "열왕기하", 13: "역대상", 14: "역대하",
    15: "에스라", 16: "느헤미야", 17: "에스더", 18: "욥기",
    19: "시편", 20: "잠언", 21: "전도서", 22: "아가",
    23: "이사야", 24: "예레미야", 25: "예레미야애가", 26: "에스겔",
    27: "다니엘", 28: "호세아", 29: "요엘", 30: "아모스",
    31: "오바댜", 32: "요나", 33: "미가", 34: "나훔",
    35: "하박국", 36: "스바냐", 37: "학개", 38: "스가랴", 39: "말라기",
    40: "마태복음", 41: "마가복음", 42: "누가복음", 43: "요한복음",
    44: "사도행전", 45: "로마서", 46: "고린도전서", 47: "고린도후서",
    48: "갈라디아서", 49: "에베소서", 50: "빌립보서", 51: "골로새서",
    52: "데살로니가전서", 53: "데살로니가후서",
    54: "디모데전서", 55: "디모데후서", 56: "디도서", 57: "빌레몬서",
    58: "히브리서", 59: "야고보서", 60: "베드로전서", 61: "베드로후서",
    62: "요한일서", 63: "요한이서", 64: "요한삼서",
    65: "유다서", 66: "요한계시록",
}


def resolve_book_id(book_name):
    """책 이름을 API book ID로 변환. 정확히 매칭되지 않으면 부분 매칭 시도."""
    name = book_name.strip()
    if name in BOOK_ALIASES:
        return BOOK_ALIASES[name]
    # 부분 매칭: 입력이 키에 포함되거나, 키가 입력에 포함되는 경우
    for alias, bid in BOOK_ALIASES.items():
        if alias in name or name in alias:
            return bid
    return None


def fetch_verse_from_api(book_id, chapter, verse_num):
    """Bolls.life API에서 성경 구절 텍스트 가져오기"""
    url = f"https://bolls.life/get-verse/KRV/{book_id}/{chapter}/{verse_num}/"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            text = data.get("text", "").strip()
            if text:
                return text
    except Exception:
        pass
    return None


def parse_reference(llm_output):
    """LLM 출력에서 '책이름 장:절' 파싱"""
    # 패턴: 책이름 숫자:숫자
    match = re.search(r'([가-힣\s]+?)\s*(\d+)\s*:\s*(\d+)', llm_output)
    if match:
        book_name = match.group(1).strip()
        chapter = int(match.group(2))
        verse_num = int(match.group(3))
        return book_name, chapter, verse_num
    return None, None, None


def select_verse(state):
    emotion = state["emotion"]
    event = state.get("event", "")

    prompt = f"""사용자의 상황: {event}
사용자의 감정: {emotion}

위 상황과 감정에 가장 위로가 되는 성경 구절을 하나 추천해주세요.
구약과 신약 66권 전체에서 가장 적합한 구절을 골라주세요.

중요한 규칙:
- 반드시 책이름과 장:절 참조만 출력하세요.
- 구절 본문은 작성하지 마세요.
- 다른 설명도 포함하지 마세요.

형식:
책이름 장:절

예시:
시편 23:1
빌립보서 4:6
이사야 41:10"""

    # LLM에게 참조만 추천받기 (최대 3회 시도)
    for attempt in range(3):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7 if attempt == 0 else 0.5,
        )
        llm_output = (response.choices[0].message.content or "").strip()

        book_name, chapter, verse_num = parse_reference(llm_output)
        if not book_name:
            continue

        book_id = resolve_book_id(book_name)
        if not book_id:
            continue

        # API에서 실제 구절 텍스트 가져오기
        verse_text = fetch_verse_from_api(book_id, chapter, verse_num)
        if verse_text:
            std_name = BOOK_ID_TO_NAME.get(book_id, book_name)
            return {"verse": f"{verse_text} ({std_name} {chapter}:{verse_num})"}

    # 모든 시도 실패 시 폴백 (시편 23:1)
    fallback_text = fetch_verse_from_api(19, 23, 1)
    if fallback_text:
        return {"verse": f"{fallback_text} (시편 23:1)"}
    return {"verse": "여호와는 나의 목자시니 내가 부족함이 없으리로다 (시편 23:1)"}
