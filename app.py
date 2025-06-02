import html
import streamlit as st
import os
import difflib
import pandas as pd
import urllib.parse

# 이미지 URL 안전하게 인코딩 처리
image_url = urllib.parse.quote(level_images[level], safe=':/')



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


st.markdown("""
<style>
/* ==== 전체 앱 배경 이미지 완전 적용 ==== */
html, body, .stApp {
    background-image: url("https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjbPHC7GcS3kaAiuWjJo7kszHYYDMHdA-rx6eovZJUErqqusRv04ymGPBbzP1MnMptsyXYN50A6PjwEQJxDQJsX2qT2zeuRY7hGYPJEWLHjDDTbsDRdUpCIkLUKyMsW3qTrNiTYV-2rERyGTY0ZIkU-YLyDQqKYnud8hYYOtYsQmTkrtI39LVUymRLzFnSl/s320/5151.png");
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
    background-repeat: no-repeat !important;
}

/* 라디오(모드 선택) 체크/동그라미 아이콘 숨김 */
[data-baseweb="radio"] label > span:first-child {
    display: none !important;
}

/* 라디오 항목 스타일(박스형) */
[data-baseweb="radio"] label {
    display: block !important;
    width: 100%;
    border-radius: 12px !important;
    padding: 7px 22px !important;
    margin-bottom: 8px !important;
    font-size: 1.14em !important;
    font-weight: 700 !important;
    color: #22537d !important;
    background: #f4f8ff !important;
    border: 2.5px solid #f4f8ff !important;
    box-shadow: 0 1.5px 7px #b9d4fa;
    cursor: pointer;
    transition: background 0.16s, color 0.16s, border 0.16s;
}

/* 마우스 오버 효과 */
[data-baseweb="radio"] label:hover {
    background: #e3eeff !important;
    border: 2.5px solid #5795ef !important;
    color: #103c79 !important;
}

/* 선택된 항목: 배경+글씨 강조 */
[data-baseweb="radio"] input:checked + div label {
    background: #3977d5 !important;
    border: 2.5px solid #3977d5 !important;
    color: #fff !important;
    font-weight: 900 !important;
    box-shadow: 0 2px 10px #a9ccff;
}

/* 전체 라디오 컨테이너(테두리+배경) */
.stRadio {
    background: linear-gradient(92deg, #e5f0fb 80%, #d2e3f8 100%) !important;
    border-radius: 16px !important;
    box-shadow: 0 6px 30px rgba(30,70,120,0.10), 0 1.5px 12px #aacdee;
    padding: 20px 28px 18px 22px !important;
    border: 2.5px solid #86b8ea !important;
    margin-bottom: 18px;
}
.markdown-highlight {
    background: rgba(255,255,255,0.96);
    border-radius: 8px;
    padding: 10px 16px 9px 16px;
    color: #193e73;
    font-size: 1.13em;
    font-weight: 700;
    margin: 8px 0 13px 0;
    box-shadow: 0 3px 16px rgba(60,80,120,0.10);
    letter-spacing: 0.01em;
    line-height: 1.7em;
    transition: background 0.18s;
}
</style>
""", unsafe_allow_html=True)


#✅ 앱 제목
st.markdown("""
<div style="text-align:center; margin-top:10px;">
    <h1 style="font-family: 'Arial'; color: navy; margin: 0; font-size: 36px;">
        📓 성경 암송
    </h1>
</div>
""", unsafe_allow_html=True)




# ✅ 등급 계산용 포인트 설정
point = 11  # ← 원하는 값으로 조정 가능

# ✅ 점수에 따른 성장 단계 계산 함수
def get_growth_level(point):
    if point < 5:
        return "씨앗"
    elif point < 15:
        return "새싹"
    elif point < 30:
        return "묘목"
    else:
        return "차나무"

# ✅ 등급별 이미지 URL
level_images = {
    "씨앗": "https://blogger.googleusercontent.com/img/a/AVvXsEgP8v3BJ8b0C4f2uSs2oswJK-055x7OYA6Z6wBDOym25-txB4vuYYw6F_QK4YD3-J1oJUHSJqsemF0DJ5BMSAYToRjgHrVWQC3Q-vBihuuhK0H13vN9_hRM1OlOHOOLexk5aAdHb5jAwiGv2QhA_kqisQ8nUS2Sbl5srfO5jngHlLWjPVZyS7opr_CCMJgy",
    "새싹": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhuLQKm5YC34SRdHShiwVeUxONGHCBWhQn0iZFgz7Ay9ip8kZUbevwD3vbEH3fr0FOMQRJTn6aCD552fUf1XwdCvJ9zIZGVc2c37mqqUgFig9eLEOu6Bu6aYHRlZO0AXM5tpAoBPDuc8B9E0XgCZYkGiNG9X8GXeMK981zPhrkNoDG4I45WDacD2I9wJDOA/s320/ChatGPT%20Image%202025%EB%85%84%206%EC%9B%94%202%EC%9D%BC%20%EC%98%A4%EC%A0%84%2011_12_03.png",
    "묘목": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg0VAEUQS9ER9gBVJV1IOAdk3hWUkIFv-Gw-Ou-lOcR5Z5Q_GXHIRvwzR3QiSOfck20DqzYc_ykiwE3xz3QlrBBqvrTUiIdvHQxvHh4yhG6sZuzf6PgP2BnJFOSySXy8ThfSb3m_-a9BAtfo-lWMIUMcpYSU1ia94z_PRFpl_1-N1gWEqyLs68b8Xrc0Hq0/s320/ChatGPT%20Image%202025%EB%85%84%206%EC%9B%94%202%EC%9D%BC%20%EC%98%A4%EC%A0%84%2011_26_43.png",
    "차나무": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhofKc4Gsg0wkH6sn5gwqyeQlTfOGhU-MsJH18-rYMRm-yAdVzNEWipSUrJGlbtJYN5hkCS95Aw-nG21VfxoqSvWjyaYWbelJmOir250fFFSbMz0AVJ9APnFR5jVVSQY77Xi4QwQ0Wc8yCKnJgmYrWsX4fQrJLEaONcDuQWb7W6B-_U584TCUsEoLnpOWBu/s320/ChatGPT%20Image%202025%EB%85%84%206%EC%9B%94%202%EC%9D%BC%20%EC%98%A4%EC%A0%84%2011_32_31.png",
}

# ✅ 등급별 응원 메시지
level_messages = {
    "씨앗": "노력의 씨앗이 조용히 뿌려졌어요.",
    "새싹": "작은 습관이 새싹처럼 자라나고 있어요.",
    "묘목": "꾸준한 연습이 점점 단단해지고 있어요.",
    "차나무": "오랜 노력의 향기가 성과로 우러나고 있어요."
}

# ✅ 현재 등급 및 메시지/이미지
level = get_growth_level(point)
escaped_message = level_messages[level]
image_url = urllib.parse.quote(level_images[level], safe=':/')

# ✅ 색상 설정
text_color = "#2a9d8f"
border_color = "#6c9bcf"

# ✅ 등급 UI 출력
st.markdown(f"""
<div style="text-align:center; margin-bottom: 26px;">
    <img src="{image_url}" style="max-height: 140px; margin-bottom: 14px;" />
    <div style="font-size: 24px; font-weight: 900; color: #2c5282; margin-bottom: 6px;">
        현재 등급: {level}
    </div>
    <div style="
        background: rgba(255,255,255,0.95);
        padding: 14px 22px;
        border-radius: 14px;
        display: inline-block;
        box-shadow: 0 3px 12px rgba(80, 40, 40, 0.12);
        font-size: 17.5px;
        color: {text_color};
        font-weight: 600;
        border: 3px solid {border_color};
        margin-top: 8px;
    ">
        {escaped_message}
    </div>
</div>
""", unsafe_allow_html=True)







# ✅ 모드 선택 선언
mode = st.radio("**🎧 모드를 선택하세요**", ["본문 보기", "부분 듣기", "전체 듣기", "부분 암송 테스트", "전체 암송 테스트"], index=0)

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




# ✅ 듣기 처리 ---
if mode == "부분 듣기":
    # 1. 안내문구(하얀색) 별도 출력
    st.markdown(
        "<span style='color:#fff; font-size:1.00em; font-weight:800; display:block; margin-bottom:-100px;'>들을 절을 선택하세요.</span>",
        unsafe_allow_html=True
    )
    # 2. selectbox 라벨은 빈 문자열
    verse_num_label = st.selectbox("", [f"{i}절" for i in range(1, len(verse_texts)+1)])
    verse_num = int(verse_num_label.replace("절", ""))
    file_name = f"{verse_num:02d}_{verse_num}절.wav"
    path = os.path.join(audio_dir, file_name)
    st.markdown("---")
    if os.path.exists(path):
        st.audio(path, format='audio/wav')
        st.markdown(
            f"<div class='markdown-highlight'>{verse_texts[verse_num-1]}</div>",
            unsafe_allow_html=True
        )
    else:
        st.error("오디오 파일을 찾을 수 없습니다.")


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
    else:
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
