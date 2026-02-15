import streamlit as st
import streamlit.components.v1 as components
from graph import app
import json

st.set_page_config(page_title="AI 기도문 생성기", page_icon="🙏", layout="centered")

# 커스텀 CSS (피그마 디자인 반영)
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

html, body, [class*="st-"] {
    font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
}
.stApp {
    background-color: #F9F8F5;
}
/* 헤더 숨기기 & 상단 여백 완전 제거 */
header[data-testid="stHeader"] { display: none; }
.stMainBlockContainer, .stMain, .block-container,
section[data-testid="stMain"] > div {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
div[data-testid="stMainBlockContainer"] > div {
    padding-top: 0 !important;
}

/* ── 입력 페이지 ── */
.app-title {
    text-align: center; font-size: 26px; font-weight: 700;
    color: #111; padding-top: 12px; margin-bottom: 0;
}
.hero-circle {
    width: 140px; height: 140px; border-radius: 50%;
    background: #fff; border: 1px solid #f0f0f0;
    display: flex; align-items: center; justify-content: center;
    margin: 20px auto; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.hero-circle span { font-size: 64px; }
.intro-text {
    text-align: center; color: #111; font-size: 16px;
    line-height: 1.7; margin-bottom: 24px;
}
.prompt-text {
    text-align: center; color: #7CB342; font-size: 18px;
    font-weight: 600; margin-bottom: 12px;
}
.info-hint {
    display: flex; align-items: center; gap: 6px;
    font-size: 13px; color: #999; margin-top: 8px;
}
.info-hint .badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 18px; height: 18px; border-radius: 50%;
    background: #e5e5e5; color: #999; font-size: 11px; font-weight: 600;
}

/* ── 결과 페이지 ── */
.result-header {
    display: flex; align-items: center; justify-content: center;
    position: relative;
    padding: 14px 0; border-bottom: 1px solid #f0f0f0;
    margin-bottom: 16px;
}
.result-header .back-arrow {
    position: absolute; left: 0;
    font-size: 20px; color: #555; cursor: pointer;
    background: none; border: none; padding: 2px 4px;
    display: flex; align-items: center; text-decoration: none;
}
.result-header .back-arrow:hover { color: #111; }
.result-header .title {
    font-size: 18px; font-weight: 600; color: #111;
}
.section-label {
    font-size: 13px; font-weight: 500; color: #888; margin-bottom: 10px;
}
.tags-wrap {
    display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;
}
.tag {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 7px 14px; border-radius: 20px; font-size: 14px; font-weight: 500;
}
.tag-event { background: #E8F5E9; border: 1px solid #C8E6C9; color: #2E7D32; }
.tag-emotion { background: #FFF3E0; border: 1px solid #FFE0B2; color: #E65100; }
.tag-emotion2 { background: #E3F2FD; border: 1px solid #BBDEFB; color: #1565C0; }

/* 성경 구절 카드 */
.verse-card {
    background: #F1F8E9; border-radius: 16px; padding: 24px 24px 20px;
    position: relative; overflow: hidden; margin-bottom: 16px;
}
.verse-card .quote-mark {
    position: absolute; top: 8px; right: 16px;
    font-size: 72px; font-family: serif; color: #C5E1A5;
    line-height: 1; opacity: 0.7;
}
.verse-card .verse-label { font-size: 13px; font-weight: 500; color: #7CB342; margin-bottom: 12px; }
.verse-card .verse-text { font-size: 16px; line-height: 1.8; color: #333; position: relative; font-style: italic; }
.verse-card .verse-ref { font-size: 14px; color: #558B2F; margin-top: 12px; font-weight: 500; }

/* 기도문 카드 */
.prayer-card {
    background: #fff; border-radius: 16px; padding: 28px 24px; margin: 16px 0;
    border: 1px solid #f0f0f0; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.prayer-card .prayer-text { font-size: 16px; line-height: 1.8; color: #333; white-space: pre-line; }

/* 하단 복사 버튼 — 실제 스타일은 components.html 내에서 처리 */

/* 하단 문구 */
.footer-hint { text-align: center; font-size: 13px; color: #ccc; padding: 8px 0 16px; }

/* CTA 버튼 스타일 */
div.stButton {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}
div.stButton > button,
div.stButton > button[kind="secondary"],
div.stButton > button[data-testid="stBaseButton-secondary"] {
    width: 100% !important;
    padding: 16px 80px !important;
    white-space: nowrap !important;
    border-radius: 50px !important;
    background-color: #FDE68A !important;
    color: #111 !important;
    font-size: 17px !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: none !important;
    transition: background-color 0.2s !important;
}
div.stButton > button:hover, div.stButton > button:focus {
    background-color: #fcd34d !important; color: #111 !important; border: none !important;
}
div.stButton > button:active { background-color: #f6c622 !important; }
div.stButton > button:disabled { opacity: 0.5 !important; background-color: #FDE68A !important; }
div.stButton > button p { font-size: 17px !important; font-weight: 600 !important; color: #111 !important; }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "result" not in st.session_state:
    st.session_state.result = None
if "back" in st.query_params or "cancel" in st.query_params:
    st.session_state.result = None
    st.query_params.clear()
    st.rerun()


def parse_verse(verse_str):
    import re
    match = re.match(r'^(.+)\s*\(([^)]+)\)\s*$', verse_str or "")
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return verse_str, ""

def render_copy_button(prayer_text):
    safe_text = json.dumps(prayer_text or "")
    components.html(
        f"""
        <style>
        .share-actions {{
            display: flex;
            justify-content: center;
            padding: 24px 0;
        }}
        .share-btn {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            color: #888;
            font-size: 13px;
            font-weight: 500;
            background: none;
            border: none;
            cursor: pointer;
        }}
        .share-btn:hover {{ color: #333; }}
        .share-btn svg {{ width: 24px; height: 24px; }}
        .share-hint {{
            text-align: center;
            font-size: 12px;
            color: #9aa0a6;
            margin-top: -8px;
            min-height: 16px;
        }}
        </style>
        <div class="share-actions">
            <button class="share-btn" id="copy-btn" type="button">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                텍스트 복사
            </button>
        </div>
        <div class="share-hint" id="share-hint"></div>
        <script>
        const prayerText = {safe_text};
        const hint = document.getElementById('share-hint');

        async function copyText() {{
            try {{
                await navigator.clipboard.writeText(prayerText);
                hint.textContent = '복사되었습니다.';
            }} catch (err) {{
                const textarea = document.createElement('textarea');
                textarea.value = prayerText;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                try {{
                    document.execCommand('copy');
                    hint.textContent = '복사되었습니다.';
                }} catch (err2) {{
                    hint.textContent = '복사에 실패했습니다.';
                }}
                document.body.removeChild(textarea);
            }}
            setTimeout(() => (hint.textContent = ''), 2000);
        }}

        document.getElementById('copy-btn').addEventListener('click', copyText);
        </script>
        """,
        height=100,
    )

# ── 결과 화면 ──
if st.session_state.result:
    result = st.session_state.result

    # 헤더: ← + 타이틀 (같은 줄, 배경 없음)
    st.markdown("""
    <div class="result-header">
        <a class="back-arrow" href="?back=1">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 19l-7-7 7-7"/></svg>
        </a>
        <div class="title">당신을 위한 기도</div>
    </div>
    """, unsafe_allow_html=True)

    # 분석된 상황 & 감정 태그 (두 줄 분리)
    event = result.get("event", "")
    emotion = result.get("emotion", "")
    emotions = [e.strip() for e in emotion.replace(";", ",").replace(", ", ",").split(",") if e.strip()]

    # 상황
    st.markdown('<div class="section-label">상황</div>', unsafe_allow_html=True)
    if event:
        events = [e.strip() for e in event.replace(";", ",").replace(", ", ",").split(",") if e.strip()]
        event_tags = ''.join([
            f'<span class="tag tag-event">{ev}</span>' for ev in events
        ])
        st.markdown(f'<div class="tags-wrap">{event_tags}</div>', unsafe_allow_html=True)

    # 감정
    st.markdown('<div class="section-label" style="margin-top:4px;">감정</div>', unsafe_allow_html=True)
    if emotions:
        emotion_styles = ["tag-emotion", "tag-emotion2"]
        emotion_tags = ''.join([
            f'<span class="tag {emotion_styles[min(i, 1)]}">{em}</span>'
            for i, em in enumerate(emotions)
        ])
        st.markdown(f'<div class="tags-wrap">{emotion_tags}</div>', unsafe_allow_html=True)

    # 성경 구절 카드
    verse = result.get("verse", "")
    verse_text, verse_ref = parse_verse(verse)
    st.markdown(f"""
    <div class="verse-card">
        <span class="quote-mark">&ldquo;</span>
        <div class="verse-label">오늘의 말씀</div>
        <div class="verse-text">"{verse_text}"</div>
        {"<div class='verse-ref'>" + verse_ref + "</div>" if verse_ref else ""}
    </div>
    """, unsafe_allow_html=True)

    # 기도문 카드 — 문단 간격 없이 줄바꿈만
    prayer = result.get("prayer", "")
    # 연속 빈 줄을 단일 줄바꿈으로 변환
    import re as _re
    prayer_display = _re.sub(r'\n{2,}', '\n', prayer.strip())
    st.markdown(f"""
    <div class="prayer-card">
        <div class="prayer-text">{prayer_display}</div>
    </div>
    """, unsafe_allow_html=True)

    # 텍스트 복사 버튼
    render_copy_button(prayer)

    # 새로운 기도문 만들기 버튼
    _, col_btn2, _ = st.columns([0.5, 4, 0.5])
    with col_btn2:
        if st.button("새로운 기도문 만들기", use_container_width=True):
            st.session_state.result = None
            st.rerun()

    st.markdown('<div class="footer-hint">마음이 힘들 때 언제든 다시 찾아주세요.</div>', unsafe_allow_html=True)

# ── 입력 화면 ──
else:
    st.markdown('<div class="app-title">AI 기도문 생성기</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-circle"><span>🙏</span></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="intro-text">
        답답한 마음과 막막한 기도<br>
        AI와 함께 기도습관을 만들어보세요
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="prompt-text">무엇을 위해 기도할까요?</div>', unsafe_allow_html=True)

    emotion_input = st.text_area(
        "입력",
        max_chars=1000,
        height=180,
        placeholder="오늘 하루 있었던 일이나, 하나님께\n드리고 싶은 솔직한 마음을 적어주세요...",
        label_visibility="collapsed",
    )

    st.markdown("""
    <div class="info-hint">
        <span class="badge">i</span>
        작성하신 내용은 기도를 생성하는 데만 사용됩니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    _, col_btn, _ = st.columns([0.5, 4, 0.5])
    with col_btn:
        submitted = st.button("기도문 만들어주세요", disabled=not emotion_input, use_container_width=True)
    if submitted:
        # 커스텀 로딩 모달 표시
        st.markdown("""
        <style>
        .loading-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.45); z-index: 99999;
            display: flex; align-items: center; justify-content: center;
        }
        .loading-modal {
            background: #fff; border-radius: 24px; padding: 40px 36px 32px;
            text-align: center; width: 280px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        }
        .loading-emoji { font-size: 48px; margin-bottom: 20px; }
        .loading-messages { position: relative; height: 28px; margin-bottom: 24px; }
        .loading-msg {
            position: absolute; width: 100%; text-align: center;
            font-size: 15px; font-weight: 500; color: #333;
            opacity: 0;
        }
        .loading-msg:nth-child(1) { animation: msgFade 4s infinite; }
        .loading-msg:nth-child(2) { animation: msgFade 4s infinite 2s; }
        @keyframes msgFade {
            0% { opacity: 0; }
            5% { opacity: 1; }
            45% { opacity: 1; }
            50% { opacity: 0; }
            100% { opacity: 0; }
        }
        .loading-dots { display: flex; justify-content: center; gap: 6px; margin-bottom: 28px; }
        .loading-dots span {
            width: 8px; height: 8px; border-radius: 50%; background: #C5E1A5;
            animation: dotPulse 1.2s infinite;
        }
        .loading-dots span:nth-child(2) { animation-delay: 0.2s; }
        .loading-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes dotPulse {
            0%, 100% { opacity: 0.3; transform: scale(0.8); }
            50% { opacity: 1; transform: scale(1.2); }
        }
        .cancel-link {
            display: inline-block; padding: 8px 28px;
            border: none; background: none;
            font-size: 13px; color: #999; text-decoration: none;
            transition: all 0.2s;
        }
        .cancel-link:hover { color: #666; }
        </style>
        <div class="loading-overlay">
            <div class="loading-modal">
                <div class="loading-emoji">🙏</div>
                <div class="loading-messages">
                    <div class="loading-msg">마음을 분석중입니다..</div>
                    <div class="loading-msg">열심히 기도문을 만들고 있습니다..</div>
                </div>
                <div class="loading-dots"><span></span><span></span><span></span></div>
                <a class="cancel-link" href="?cancel=1">그만하기</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        result = app.invoke({"emotion": emotion_input})
        st.session_state.result = result
        st.rerun()
