import urllib.parse
import streamlit as st
import os
import difflib
import pandas as pd

# --- 파일 경로 설정 ---
audio_dir = "audio"
full_audio_file = os.path.join(audio_dir, "full_audio.wav")

# --- 성경 본문 로드 및 엑셀 저장 ---
lines = []
with open("verses.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            parts = line.split(" ", 1)
            if len(parts) == 2:
                verse_num = parts[0].replace("절", "")
                verse_text = parts[1]
                lines.append({"절": int(verse_num), "본문": verse_text})

df = pd.DataFrame(lines)

with open("verses.txt", "r", encoding="utf-8") as f:
    verse_texts = [line.strip().split(" ", 1)[1] for line in f if line.strip() and len(line.strip().split(" ", 1)) > 1]

def compare_texts(correct, user):
    correct_clean = correct.replace(" ", "")
    user_clean = user.replace(" ", "")
    ratio = difflib.SequenceMatcher(None, correct_clean, user_clean).ratio()
    return ratio >= 0.95

# ✅ 스타일
st.markdown("""
<style>
html, body, .stApp {
    background-image: url("https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjbPHC7GcS3kaAiuWjJo7kszHYYDMHdA-rx6eovZJUErqqusRv04ymGPBbzP1MnMptsyXYN50A6PjwEQJxDQJsX2qT2zeuRY7hGYPJEWLHjDDTbsDRdUpCIkLUKyMsW3qTrNiTYV-2rERyGTY0ZIkU-YLyDQqKYnud8hYYOtYsQmTkrtI39LVUymRLzFnSl/s320/5151.png");
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
    background-repeat: no-repeat !important;
}
.stRadio {
    background: linear-gradient(92deg, #e5f0fb 80%, #d2e3f8 100%) !important;
    border-radius: 16px !important;
    box-shadow: 0 6px 30px rgba(30,70,120,0.10), 0 1.5px 12px #aacdee;
    padding: 20px 28px 18px 22px !important;
    border: 2.5px solid #86b8ea !important;
    margin-bottom: 18px;
    width: 100% !important;
    max-width: 640px !important;
    margin-left: auto;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)



# ✅ 사용자 닉네임 입력 (최초 1회만)
if "nickname" not in st.session_state:
    st.session_state.nickname = ""

st.session_state.nickname = st.text_input(
    "👤 사용자 닉네임을 입력하세요", 
    value=st.session_state.nickname,
    max_chars=20
)

if not st.session_state.nickname:
    st.warning("닉네임을 입력해야 앱을 사용할 수 있어요.")
    st.stop()

# ✅ 사용자 포인트 불러오기 (기본값 0)
if "user_points" not in st.session_state:
    st.session_state.user_points = {}

# 현재 사용자 포인트 불러오기
nickname = st.session_state.nickname
if nickname not in st.session_state.user_points:
    st.session_state.user_points[nickname] = 0




# ✅ 앱 제목
st.markdown("""
<div style="text-align:center; margin-top:10px;">
    <h1 style="font-family: 'Arial'; color: navy; margin: 0; font-size: 36px;">
        📓 성경 암송
    </h1>
</div>
""", unsafe_allow_html=True)

# ✅ 포인트 및 등급
point = st.session_state.user_points[nickname]


def get_growth_level(point):
    if point < 3:
        return "씨앗"
    elif point < 15:
        return "새싹"
    elif point < 30:
        return "묘목"
    else:
        return "차나무"

level_images = {
    "씨앗": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgP8v3BJ8b0C4f2uSs2oswJK-055x7OYA6Z6wBDOym25-txB4vuYYw6F_QK4YD3-J1oJUHSJqsemF0DJ5BMSAYToRjgHrVWQC3Q-vBihuuhK0H13vN9_hRM1OlOHOOLexk5aAdHb5jAwiGv2QhA_kqisQ8nUS2Sbl5srfO5jngHlLWjPVZyS7opr_CCMJgy",
    "새싹": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhuLQKm5YC34SRdHShiwVeUxONGHCBWhQn0iZFgz7Ay9ip8kZUbevwD3vbEH3fr0FOMQRJTn6aCD552fUf1XwdCvJ9zIZGVc2c37mqqUgFig9eLEOu6Bu6aYHRlZO0AXM5tpAoBPDuc8B9E0XgCZYkGiNG9X8GXeMK981zPhrkNoDG4I45WDacD2I9wJDOA/s320/ChatGPT%20Image.png",
    "묘목": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg0VAEUQS9ER9gBVJV1IOAdk3hWUkIFv-Gw-Ou-lOcR5Z5Q_GXHIRvwzR3QiSOfck20DqzYc_ykiwE3xz3QlrBBqvrTUiIdvHQxvHh4yhG6sZuzf6PgP2BnJFOSySXy8ThfSb3m_-a9BAtfo-lWMIUMcpYSU1ia94z_PRFpl_1-N1gWEqyLs68b8Xrc0Hq0/s320/ChatGPT%20Image.png",
    "차나무": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhofKc4Gsg0wkH6sn5gwqyeQlTfOGhU-MsJH18-rYMRm-yAdVzNEWipSUrJGlbtJYN5hkCS95Aw-nG21VfxoqSvWjyaYWbelJmOir250fFFSbMz0AVJ9APnFR5jVVSQY77Xi4QwQ0Wc8yCKnJgmYrWsX4fQrJLEaONcDuQWb7W6B-_U584TCUsEoLnpOWBu/s320/ChatGPT%20Image.png"
}

level_messages = {
    "씨앗": "노력의 씨앗이 조용히 뿌려졌어요.",
    "새싹": "작은 습관이 새싹처럼 자라나고 있어요.",
    "묘목": "꾸준한 연습이 점점 단단해지고 있어요.",
    "차나무": "오랜 노력의 향기가 성과로 우러나고 있어요."
}

level = get_growth_level(point)
image_url = urllib.parse.quote(level_images[level], safe=':/')
message = level_messages[level]

# ✅ 등급 박스 출력 (모드 박스와 동일 너비 + 아이콘 크게)
st.markdown(f"""
<div style="
    margin: 16px auto 18px auto;
    padding: 16px 20px;
    width: 100%;
    max-width: 640px;
    border-radius: 16px;
    background: linear-gradient(92deg, #f6faff 80%, #edf4fb 100%);
    border: 2.5px solid #86b8ea;
    box-shadow: 0 4px 16px rgba(30,70,120,0.12);
    display: flex;
    align-items: center;
    gap: 16px;
    font-family: '맑은 고딕', 'Noto Sans KR', sans-serif;
">
   <div style="flex-shrink: 0;">
        <img src=\"{level_images[level]}\" style=\"height: 135px;\" />
    </div>
    <div style="text-align: left;">
        <div style="font-size: 17px; font-weight: 900; color: #2c5282; margin-bottom: 4px;">
            현재 등급: {level}
        </div>
        <div style="font-size: 14.5px; font-weight: 700; color: #28a745; margin-bottom: 4px;">
            &lt; 포인트 {point} &gt;
        </div>
        <div style="font-size: 13.2px; font-weight: 500; color: #1a2a4f;">
            {message}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ✅ 모드 선택 라디오
mode = st.radio("🎧 모드를 선택하세요", ["본문 보기", "부분 듣기", "전체 듣기", "부분 암송 테스트", "전체 암송 테스트"], index=0)

# 이후 모드별 동작은 생략



# ✅ Expander 제목 전용 스타일 정의
st.markdown("""
<style>
/* ✅ Expander 타이틀 안의 span 태그에만 적용 */
details summary span.exp-title {
    font-size: 2.1em !important;      /* 글자 크기 */
    font-weight: 900 !important;      /* 글자 굵기 */
    color: #0c2d6e !important;        /* 글자 색상 */
}

/* ✅ 불필요한 화살표 제거 */
details summary::after {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ✅ 본문 보기 모드
if mode == "본문 보기":
    
    # ✅ 본문 보기 영역 (label에 span 클래스 적용!)
    with st.expander("📖 본문 보기", expanded=True):
        numbered_verses = [f"<b>{i+1}절</b> {text}" for i, text in enumerate(verse_texts)]

        st.markdown(
            """
            <div style="
                background: linear-gradient(92deg, #f6faff 80%, #edf4fb 100%);
                border: 2.5px solid #86b8ea;
                border-radius: 16px;
                padding: 28px 30px;
                box-shadow: 0 6px 22px rgba(30,70,120,0.12);
                font-size: 1.25em;
                font-weight: 400;
                line-height: 2.1em;
                color: #1a2a4f;
                letter-spacing: 0.01em;
                font-family: '맑은 고딕', 'Noto Sans KR', sans-serif;
            ">
            """ + "<br><br>".join(numbered_verses) + """
            </div>
            """,
            unsafe_allow_html=True
        )



# ✅ 부분 듣기 ---
elif mode == "부분 듣기":
    st.markdown(
        "<span style='color:#fff; font-size:1.00em; font-weight:800; display:block;'>들을 절을 선택하세요.</span>",
        unsafe_allow_html=True
    )

    # 절 선택 selectbox (고유 key 부여)
    verse_num_label = st.selectbox(
        label="", 
        options=[f"{i}절" for i in range(1, len(verse_texts) + 1)],
        key="verse_select_box"
    )
    verse_num = int(verse_num_label.replace("절", ""))
    file_name = f"{verse_num:02d}_{verse_num}절.wav"
    path = os.path.join(audio_dir, file_name)

    st.markdown("---")

    if os.path.exists(path):
        # 고유 키를 사용한 오디오 출력
        st.audio(path, format="audio/wav")

        # 고유한 스타일 블록
        st.markdown(
            f"""
            <div style='
                background: rgba(255,255,255,0.85);
                border-radius: 12px;
                padding: 16px 20px;
                margin-top: 12px;
                font-size: 1.2em;
                font-weight: 500;
                color: #1a2a4f;
                box-shadow: 0 2px 12px rgba(0,0,0,0.07);
            '>
                {verse_texts[verse_num - 1]}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("오디오 파일을 찾을 수 없습니다.")

# ✅ 전체 듣기 ---
elif mode == "전체 듣기":
    st.markdown(
        "<span style='color:#fff; font-size:1.13em; font-weight:900;'>🎵 전체 오디오 자동 재생</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='markdown-highlight'>전체 오디오를 자동으로 재생합니다.</div>",
        unsafe_allow_html=True
    )

    # ✅ 표준 속도 오디오
    st.markdown("<h5 style='color:white; margin-top:24px;'>🔊 표준 속도</h5>", unsafe_allow_html=True)
    if os.path.exists(full_audio_file):
        st.audio(full_audio_file, format="audio/wav")

        # ✅ 포인트 +2 (중복 방지)
        if "full_listened" not in st.session_state:
            st.session_state.user_points[nickname] += 2
            st.session_state.full_listened = True
    else:
        st.error("full_audio.wav 파일을 audio 폴더 안에 넣어주세요.")

    # ✅ 느리게 듣기 오디오
    slow_audio_file = os.path.join(audio_dir, "full_audio2.wav")
    st.markdown("<h5 style='color:white; margin-top:24px;'>🐢 조금 느리게</h5>", unsafe_allow_html=True)
    if os.path.exists(slow_audio_file):
        st.audio(slow_audio_file, format="audio/wav")
    else:
        st.error("full_audio2.wav 파일을 audio 폴더 안에 넣어주세요.")

        st.error("full_audio.wav 파일을 audio 폴더 안에 넣어주세요.")

    # ✅ 느리게 듣기 오디오
    slow_audio_file = os.path.join(audio_dir, "full_audio2.wav")
    st.markdown("<h5 style='color:white; margin-top:24px;'>🐢 조금 느리게</h5>", unsafe_allow_html=True)
    if os.path.exists(slow_audio_file):
        st.audio(slow_audio_file, format="audio/wav")
    else:
        st.error("full_audio2.wav 파일을 audio 폴더 안에 넣어주세요.")



elif mode == "부분 암송 테스트":
    st.subheader("🧠 부분 암송 테스트")

    # ✅ 정답 보기 CSS (항상 삽입되도록 수정)
    st.markdown("""
        <style>
        .readonly-box {
            display: block;
            background: rgba(255,255,255,0.95);
            color: #111;
            font-size: 1.15em;
            font-weight: 400;
            font-family: 'Segoe UI', sans-serif;
            border-radius: 7px;
            padding: 10px 14px;
            box-shadow: 0 2px 12px rgba(70,70,120,0.13);
            line-height: 1.9em;
            white-space: pre-wrap;
            width: 100%;
            margin-bottom: 12px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("📝 시작 절을 선택하세요.")
    start_label = st.selectbox(
        label="", 
        options=[f"{i}절" for i in range(1, len(verse_texts) - 4)],
        key="partial_select"
    )
    start_num = int(start_label.replace("절", ""))

    # 정답/결과 토글
    col1, col2 = st.columns(2)
    with col1:
        show_answer = st.toggle("전체 정답 보기", value=False, key="partial_show_answer")
    with col2:
        check_result = st.toggle("결과 보기", value=False, key="partial_show_result")

    # 반복 출력 (5절)
    for i in range(start_num, start_num + 5):
        verse_index = i - 1
        correct_text = verse_texts[verse_index]
        key = f"partial_{i}"
        typed_input = st.session_state.get(key, "").strip()

        # 절 번호 라벨
        st.markdown(
            f"""
            <span style="
                display: inline-block;
                background: rgba(255,255,255,0.94);
                color: #14428c;
                font-size: 1.15em;
                font-weight: 800;
                padding: 4px 13px 4px 10px;
                border-radius: 7px;
                margin-bottom: 6px;
                box-shadow: 0 2px 12px rgba(70,70,120,0.13);
            ">{i}절</span>
            """,
            unsafe_allow_html=True
        )

        # ✅ 절별 정답 보기 체크박스
        show_individual_answer = st.checkbox(f"{i}절 정답 보기", key=f"partial_show_ans_{i}")

        # ✅ 조건별 출력 분기 (정답 보기 or 직접 입력)
        if show_answer or show_individual_answer:
            # ✅ 정답 표시 div
            st.markdown(f"<div class='readonly-box'>{correct_text}</div>", unsafe_allow_html=True)
        else:
            # 입력창
            st.text_area(
                "",
                value=typed_input,
                key=key,
                placeholder="직접 입력해 보세요.",
                label_visibility="collapsed"
            )

        # 결과 보기 (정답 보기와 무관하게 항상 평가)
        if check_result:
            if typed_input == "":
                st.markdown(
                    f"<div style='color:#d63e22; font-weight:900; font-size:16px;'>❌ 오답</div>",
                    unsafe_allow_html=True
                )
            else:
                is_correct = compare_texts(correct_text, typed_input)
                st.markdown(
                    f"<div style='color:{'green' if is_correct else '#d63e22'}; font-weight:900; font-size:16px;'>"
                    f"{'✅ 정답' if is_correct else '❌ 오답'}</div>",
                    unsafe_allow_html=True
                )




elif mode == "전체 암송 테스트":
    st.subheader("🧠 전체 암송 테스트")
    
    # 전체 보기/결과 보기 토글
    col1, col2 = st.columns([1, 1])
    with col1:
        show_answer = st.toggle("전체 정답 보기", value=False)
    with col2:
        show_result = st.toggle("결과 보기", value=False)

    # 스타일 적용
    st.markdown("""
        <style>
        .verse-label {
            display: inline-block;
            background: rgba(255,255,255,0.94);
            color: #14428c;
            font-size: 1.15em;
            font-weight: 800;
            padding: 4px 13px 4px 10px;
            border-radius: 7px;
            margin-bottom: 6px;
            box-shadow: 0 2px 12px rgba(70,70,120,0.13);
        }

        textarea::placeholder {
            font-size: 0.95em !important;
            color: #888 !important;
            opacity: 0.75 !important;
        }

        .result-tag {
            font-weight: bold;
            margin-left: 6px;
            color: green;
            font-size: 15px;
        }

        .result-tag.wrong {
            color: red;
        }
        </style>
    """, unsafe_allow_html=True)

    user_inputs = []

    for i in range(len(verse_texts)):
        correct_text = verse_texts[i]
        key = f"full_{i}"

        # 세션 초기화
        if key not in st.session_state:
            st.session_state[key] = ""

        # 절 번호 출력
        st.markdown(f"""<span class="verse-label">{i+1}절</span>""", unsafe_allow_html=True)

        # 절별 정답 보기 토글
        show_individual_answer = st.checkbox(f"{i+1}절 정답 보기", key=f"show_ans_{i}")

        # 정답 표시 여부
        showing_answer = show_answer or show_individual_answer

        # 입력창 출력
        if showing_answer:
            # 정답 보기 상태 → 입력 비활성화용 더미 key 사용
            input_text = st.text_area(
                "",
                value=correct_text,
                key=f"view_only_{i}",  # 실제 세션 상태에 영향 없음
                placeholder="",
                label_visibility="collapsed"
            )
        else:
            # 사용자 입력창
            input_text = st.text_area(
                "",
                value=st.session_state[key],
                key=key,
                placeholder="직접 입력해보세요.",
                label_visibility="collapsed"
            )

        user_inputs.append(input_text)

        # ✅ 결과 평가: 입력 없으면 오답 / 정답 보기 중일 땐 표시만
        if show_result:
            user_input = st.session_state.get(key, "").strip()

            if not user_input:
                # 입력이 없으면 무조건 오답
                st.markdown(
                    f"<div class='result-tag wrong'>❌ 오답</div>",
                    unsafe_allow_html=True
                )
            elif not showing_answer:
                # 입력 있고 정답 보기 중이 아닐 때만 평가
                is_correct = compare_texts(correct_text, user_input)
                st.markdown(
                    f"<div class='result-tag {'wrong' if not is_correct else ''}'>"
                    f"{'✅ 정답' if is_correct else '❌ 오답'}</div>",
                    unsafe_allow_html=True
                )
            else:
                # 정답 보기 중일 땐 결과 생략 (이미 보여주고 있으므로)
                pass



# ✅ Expander 제목 전용 스타일 정의
st.markdown("""
<style>
/* ✅ Expander 타이틀 안의 span 태그에만 적용 */
details summary span.exp-title {
    font-size: 2.1em !important;      /* 글자 크기 */
    font-weight: 900 !important;      /* 글자 굵기 */
    color: #0c2d6e !important;        /* 글자 색상 */
}

/* ✅ 불필요한 화살표 제거 */
details summary::after {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ✅ 본문 보기 모드
if mode == "본문 보기":
    
    # ✅ 본문 보기 영역 (label에 span 클래스 적용!)
    with st.expander("📖 본문 보기", expanded=True):
        numbered_verses = [f"<b>{i+1}절</b> {text}" for i, text in enumerate(verse_texts)]

        st.markdown(
            """
            <div style="
                background: linear-gradient(92deg, #f6faff 80%, #edf4fb 100%);
                border: 2.5px solid #86b8ea;
                border-radius: 16px;
                padding: 28px 30px;
                box-shadow: 0 6px 22px rgba(30,70,120,0.12);
                font-size: 1.25em;
                font-weight: 400;
                line-height: 2.1em;
                color: #1a2a4f;
                letter-spacing: 0.01em;
                font-family: '맑은 고딕', 'Noto Sans KR', sans-serif;
            ">
            """ + "<br><br>".join(numbered_verses) + """
            </div>
            """,
            unsafe_allow_html=True
        )


elif mode == "부분 암송 테스트":
    st.subheader("🧠 부분 암송 테스트")

    # ✅ 정답 보기 CSS (항상 삽입되도록 수정)
    st.markdown("""
        <style>
        .readonly-box {
            display: block;
            background: rgba(255,255,255,0.95);
            color: #111;
            font-size: 1.15em;
            font-weight: 400;
            font-family: 'Segoe UI', sans-serif;
            border-radius: 7px;
            padding: 10px 14px;
            box-shadow: 0 2px 12px rgba(70,70,120,0.13);
            line-height: 1.9em;
            white-space: pre-wrap;
            width: 100%;
            margin-bottom: 12px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("📝 시작 절을 선택하세요.")
    start_label = st.selectbox(
        label="", 
        options=[f"{i}절" for i in range(1, len(verse_texts) - 4)],
        key="partial_select"
    )
    start_num = int(start_label.replace("절", ""))

    # 정답/결과 토글
    col1, col2 = st.columns(2)
    with col1:
        show_answer = st.toggle("전체 정답 보기", value=False, key="partial_show_answer")
    with col2:
        check_result = st.toggle("결과 보기", value=False, key="partial_show_result")

    # 반복 출력 (5절)
    for i in range(start_num, start_num + 5):
        verse_index = i - 1
        correct_text = verse_texts[verse_index]
        key = f"partial_{i}"
        typed_input = st.session_state.get(key, "").strip()

        # 절 번호 라벨
        st.markdown(
            f"""
            <span style="
                display: inline-block;
                background: rgba(255,255,255,0.94);
                color: #14428c;
                font-size: 1.15em;
                font-weight: 800;
                padding: 4px 13px 4px 10px;
                border-radius: 7px;
                margin-bottom: 6px;
                box-shadow: 0 2px 12px rgba(70,70,120,0.13);
            ">{i}절</span>
            """,
            unsafe_allow_html=True
        )

        # ✅ 절별 정답 보기 체크박스
        show_individual_answer = st.checkbox(f"{i}절 정답 보기", key=f"partial_show_ans_{i}")

        # ✅ 조건별 출력 분기 (정답 보기 or 직접 입력)
        if show_answer or show_individual_answer:
            # ✅ 정답 표시 div
            st.markdown(f"<div class='readonly-box'>{correct_text}</div>", unsafe_allow_html=True)
        else:
            # 입력창
            st.text_area(
                "",
                value=typed_input,
                key=key,
                placeholder="직접 입력해 보세요.",
                label_visibility="collapsed"
            )

        # 결과 보기 (정답 보기와 무관하게 항상 평가)
        if check_result:
            if typed_input == "":
                st.markdown(
                    f"<div style='color:#d63e22; font-weight:900; font-size:16px;'>❌ 오답</div>",
                    unsafe_allow_html=True
                )
            else:
                is_correct = compare_texts(correct_text, typed_input)
                st.markdown(
                    f"<div style='color:{'green' if is_correct else '#d63e22'}; font-weight:900; font-size:16px;'>"
                    f"{'✅ 정답' if is_correct else '❌ 오답'}</div>",
                    unsafe_allow_html=True
                )




elif mode == "전체 암송 테스트":
    st.subheader("🧠 전체 암송 테스트")
    
    # 전체 보기/결과 보기 토글
    col1, col2 = st.columns([1, 1])
    with col1:
        show_answer = st.toggle("전체 정답 보기", value=False)
    with col2:
        show_result = st.toggle("결과 보기", value=False)

    # 스타일 적용
    st.markdown("""
        <style>
        .verse-label {
            display: inline-block;
            background: rgba(255,255,255,0.94);
            color: #14428c;
            font-size: 1.15em;
            font-weight: 800;
            padding: 4px 13px 4px 10px;
            border-radius: 7px;
            margin-bottom: 6px;
            box-shadow: 0 2px 12px rgba(70,70,120,0.13);
        }

        textarea::placeholder {
            font-size: 0.95em !important;
            color: #888 !important;
            opacity: 0.75 !important;
        }

        .result-tag {
            font-weight: bold;
            margin-left: 6px;
            color: green;
            font-size: 15px;
        }

        .result-tag.wrong {
            color: red;
        }
        </style>
    """, unsafe_allow_html=True)

    user_inputs = []

    for i in range(len(verse_texts)):
        correct_text = verse_texts[i]
        key = f"full_{i}"

        # 세션 초기화
        if key not in st.session_state:
            st.session_state[key] = ""

        # 절 번호 출력
        st.markdown(f"""<span class="verse-label">{i+1}절</span>""", unsafe_allow_html=True)

        # 절별 정답 보기 토글
        show_individual_answer = st.checkbox(f"{i+1}절 정답 보기", key=f"show_ans_{i}")

        # 정답 표시 여부
        showing_answer = show_answer or show_individual_answer

        # 입력창 출력
        if showing_answer:
            # 정답 보기 상태 → 입력 비활성화용 더미 key 사용
            input_text = st.text_area(
                "",
                value=correct_text,
                key=f"view_only_{i}",  # 실제 세션 상태에 영향 없음
                placeholder="",
                label_visibility="collapsed"
            )
        else:
            # 사용자 입력창
            input_text = st.text_area(
                "",
                value=st.session_state[key],
                key=key,
                placeholder="직접 입력해보세요.",
                label_visibility="collapsed"
            )

        user_inputs.append(input_text)

        # ✅ 결과 평가: 입력 없으면 오답 / 정답 보기 중일 땐 표시만
        if show_result:
            user_input = st.session_state.get(key, "").strip()

            if not user_input:
                # 입력이 없으면 무조건 오답
                st.markdown(
                    f"<div class='result-tag wrong'>❌ 오답</div>",
                    unsafe_allow_html=True
                )
            elif not showing_answer:
                # 입력 있고 정답 보기 중이 아닐 때만 평가
                is_correct = compare_texts(correct_text, user_input)
                st.markdown(
                    f"<div class='result-tag {'wrong' if not is_correct else ''}'>"
                    f"{'✅ 정답' if is_correct else '❌ 오답'}</div>",
                    unsafe_allow_html=True
                )
            else:
                # 정답 보기 중일 땐 결과 생략 (이미 보여주고 있으므로)
                pass
