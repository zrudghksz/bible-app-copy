import urllib.parse
import streamlit as st
import os
import difflib
import pandas as pd
import datetime
import json
import os
import string  # ← 이 줄도 함께 추가 필요!
import requests

HF_URL = "https://huggingface.co/datasets/zrudghksz/user-points/resolve/main/user_points.json"
USER_POINT_FILE = "user_points.json"

# 로컬에 없으면 Hugging Face에서 받아옴
if not os.path.exists(USER_POINT_FILE):
    try:
        response = requests.get(HF_URL)
        if response.status_code == 200:
            with open(USER_POINT_FILE, "w", encoding="utf-8") as f:
                f.write(response.text)
    except Exception as e:
        import streamlit as st
        st.error("❌ Hugging Face에서 포인트 파일을 불러오지 못했습니다.")
        st.stop()




# ✅ 텍스트 정리 함수: 공백 및 구두점 제거
def clean_text(text):
    return text.translate(str.maketrans("", "", string.punctuation)).replace(" ", "")


# JSON 파일 경로 지정
USER_POINT_FILE = "user_points.json"

# 파일이 존재하면 불러오고, 문제가 생기면 빈 dict로 초기화
try:
    if os.path.exists(USER_POINT_FILE):
        with open(USER_POINT_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            user_points = json.loads(content) if content else {}
    else:
        user_points = {}
except Exception as e:
    st.warning("⚠️ 포인트 파일을 불러오지 못했습니다. 빈 상태로 시작합니다.")
    user_points = {}


# Streamlit 세션 상태에 로드
if "user_points" not in st.session_state:
    st.session_state.user_points = user_points


# # ✅ 🔥 전체 초기화 코드
# st.session_state.user_points = {}
# with open(USER_POINT_FILE, "w", encoding="utf-8") as f:
#     json.dump({}, f, ensure_ascii=False, indent=2)



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
    correct_clean = clean_text(correct)
    user_clean = clean_text(user)
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



# ✅ 닉네임을 query_params에서 읽기
params = st.query_params
nickname = params.get("nickname", "")

# 입력창에 기본값으로 표시
nickname = st.text_input("👤 사용자 닉네임을 입력하세요", value=nickname, max_chars=20)

# 입력값이 있으면 query_params에 다시 저장
st.query_params["nickname"] = nickname

# 닉네임 없으면 앱 중단
if not nickname:
    st.warning("닉네임을 입력해야 앱을 사용할 수 있어요.")
    st.stop()

# ✅ 세션에 닉네임 저장
st.session_state.nickname = nickname

# ✅ 포인트 dict 초기화
if "user_points" not in st.session_state:
    st.session_state.user_points = {}

# ✅ 현재 닉네임 포인트 로딩
if nickname not in st.session_state.user_points:
    if nickname in user_points:
        st.session_state.user_points[nickname] = user_points[nickname]
    else:
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
    if point < 5:
        return "씨앗"
    elif point < 15:
        return "새싹"
    elif point < 30:
        return "묘목"
    elif point < 40:
        return "차나무"
    else:
        return "튼튼한 차나무"

level_images = {
    "씨앗": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgP8v3BJ8b0C4f2uSs2oswJK-055x7OYA6Z6wBDOym25-txB4vuYYw6F_QK4YD3-J1oJUHSJqsemF0DJ5BMSAYToRjgHrVWQC3Q-vBihuuhK0H13vN9_hRM1OlOHOOLexk5aAdHb5jAwiGv2QhA_kqisQ8nUS2Sbl5srfO5jngHlLWjPVZyS7opr_CCMJgy",
    "새싹": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhuLQKm5YC34SRdHShiwVeUxONGHCBWhQn0iZFgz7Ay9ip8kZUbevwD3vbEH3fr0FOMQRJTn6aCD552fUf1XwdCvJ9zIZGVc2c37mqqUgFig9eLEOu6Bu6aYHRlZO0AXM5tpAoBPDuc8B9E0XgCZYkGiNG9X8GXeMK981zPhrkNoDG4I45WDacD2I9wJDOA/s320/ChatGPT%20Image.png",
    "묘목": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg0VAEUQS9ER9gBVJV1IOAdk3hWUkIFv-Gw-Ou-lOcR5Z5Q_GXHIRvwzR3QiSOfck20DqzYc_ykiwE3xz3QlrBBqvrTUiIdvHQxvHh4yhG6sZuzf6PgP2BnJFOSySXy8ThfSb3m_-a9BAtfo-lWMIUMcpYSU1ia94z_PRFpl_1-N1gWEqyLs68b8Xrc0Hq0/s320/ChatGPT%20Image.png",
    "차나무": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhofKc4Gsg0wkH6sn5gwqyeQlTfOGhU-MsJH18-rYMRm-yAdVzNEWipSUrJGlbtJYN5hkCS95Aw-nG21VfxoqSvWjyaYWbelJmOir250fFFSbMz0AVJ9APnFR5jVVSQY77Xi4QwQ0Wc8yCKnJgmYrWsX4fQrJLEaONcDuQWb7W6B-_U584TCUsEoLnpOWBu/s320/ChatGPT%20Image.png",
    "튼튼한 차나무": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi0iQEcT8lADAKDNrL_maKHpcHb3_fg4PN4tOcHPGozYD4vQsNd5ODXaqVV5luv18CoKwnWT91FOa2ezy44F9t1xodRlK3CVo5E1gd4ILAqsJBiOfHACypJ8xJw4W4cqxDbqTT5wD8KY3qyRESRgjFczrMKo9CGM8QKNmjAxylgk1Ai5W0bKmSko0mx1REG/s320/ChatGPT%20Image%202025%EB%85%84%206%EC%9B%94%203%EC%9D%BC%20%EC%98%A4%EC%A0%84%2011_52_40.png"
}

level_messages = {
    "씨앗": "🎉 첫 씨앗이 뿌리를 내렸어요!<br>이 시작이 나중엔 큰 열매가 될 거예요.",
    "새싹": "🎉 싹이 텄네요! 작지만 힘찬 생명이 자라나고 있어요.<br>멈추지 말고 계속 물을 주세요 🌱",
    "묘목": "🎉 와, 가지가 자라기 시작했어요!<br>당신의 꾸준함이 참 멋집니다 👏",
    "차나무": "🎉 이제 꽃도 피우고 있네요!<br>이 길을 잘 걸어오셨어요 🍃",
    "튼튼한 차나무": "🎉 깊은 뿌리와 푸른 잎, 든든한 나무가 되었어요.<br>당신의 걸음은 큰 울림을 줍니다 🌳"
}

# ✅ 축하 문구
level_congrats = {
    "새싹": "🎉 새로운 도전을 시작하신 용기가 좋아요! 처음 한 발 내딛었어요.<br>포기하지 말고 천천히 가도 괜찮아요.",
    "묘목": "🎉 짝짝짝! 멋져요! 여기까지 온 게 쉬운 일이 아니에요.<br>계속 이어가 볼까요?",
    "차나무": "🎉 짝짝짝! 대단해요! 흔들릴 때도 있었겠지만 여기까지 왔어요.<br>당신의 노력을 응원해요.",
    "튼튼한 차나무": "🎉 최고예요! 꾸준함의 정점을 찍었어요. 당신은 진짜입니다! 🙌"
}

# ✅ 등급 계산
level = get_growth_level(point)
image_url = urllib.parse.quote(level_images[level], safe=':/')
message = level_messages[level]

# ✅ 이전 등급 없으면 기본값 "씨앗" 지정
if "previous_level" not in st.session_state:
    st.session_state.previous_level = "씨앗"

# ✅ 등급 상승 시 축하 메시지 출력
if st.session_state.previous_level != level:
    st.markdown(f"""
    <div style="
        padding: 28px;
        text-align: center;
        font-size: 1.25em;
        font-weight: 700;
        background: linear-gradient(135deg, #fff8dc, #f0f8ff);
        border: 3px solid #86b8ea;
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
        color: #1a2a4f;
        margin-bottom: 24px;
        animation: fadeIn 1s ease-in-out;
    ">
        🌟 <strong>레벨 업!</strong><br>
        {level_congrats.get(level, "🎉 축하합니다! 새로운 단계에 도달했어요.")}
    </div>
    """, unsafe_allow_html=True)

    st.session_state.previous_level = level  # 등급 상태 업데이트

# ✅ 등급 박스 출력
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
        <img src="{image_url}" style="height: 145px;" />
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
    numbered_verses = [f"<b>{i+1}절</b> {text}" for i, text in enumerate(verse_texts)]

    st.markdown(
        """
        <div style="
            background: linear-gradient(92deg, #f6faff 80%, #edf4fb 100%);
            border: 2.5px solid #86b8ea;
            border-radius: 16px;
            padding: 22px 22px;
            box-shadow: 0 6px 22px rgba(30,70,120,0.12);
            font-size: 1.35em;                   /* ✅ 적당히 큰 글씨 */
            font-weight: 400;
            line-height: 2em;
            color: #1a2a4f;
            letter-spacing: 0.01em;
            font-family: '맑은 고딕', 'Noto Sans KR', sans-serif;
            max-width: 640px;                    /* ✅ 모드 박스와 동일 너비 */
            margin: 24px auto;                   /* ✅ 가운데 정렬 유지 */
            text-align: left;                    /* ✅ 본문 정렬은 왼쪽 */
        ">
        """ + "<br><br>".join(numbered_verses) + """
        </div>
        """,
        unsafe_allow_html=True
    )






# ✅ 부분 듣기 ---
elif mode == "부분 듣기":
    import time
    import base64

    today = str(datetime.date.today())

    # ✅ UI 스타일
    st.markdown("""
    <style>
    div[data-baseweb="select"] { max-width: 120px !important; }
    .play-button {
        background: linear-gradient(90deg, #ff7e5f, #feb47b);
        border: none;
        color: white;
        padding: 12px 24px;
        text-align: center;
        font-size: 1.1em;
        font-weight: 800;
        border-radius: 12px;
        margin-top: 12px;
        margin-bottom: 18px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .play-button:hover {
        background: linear-gradient(90deg, #feb47b, #ff7e5f);
        cursor: pointer;
        transform: scale(1.03);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='color:#fff; font-size:1.13em; font-weight:900;'>🎧 부분 오디오 반복 듣기</div>", unsafe_allow_html=True)
    st.markdown("<div class='markdown-highlight'>들을 범위를 선택하고 ▶️ 버튼을 누르면 자동 재생됩니다.</div>", unsafe_allow_html=True)

    # ✅ 절 선택
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.markdown("<div style='color:white; font-weight:800;'>시작 절</div>", unsafe_allow_html=True)
        start_label = st.selectbox("", [f"{i:02d}" for i in range(1, 26)], key="start", label_visibility="collapsed")
        start_num = int(start_label)

    with col2:
        st.markdown("<div style='text-align:center; font-weight:900; color:white; margin-top:12px;'>부터</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div style='color:white; font-weight:800;'>종료 절</div>", unsafe_allow_html=True)
        end_options = [f"{i:02d}" for i in range(start_num, min(start_num + 5, len(verse_texts)+1))]
        end_label = st.selectbox("", end_options, key="end", label_visibility="collapsed")
        end_num = int(end_label)

    st.markdown("---")

    # ✅ 재생 버튼
    if st.button("▶️ 재생", key="seq_play"):
        verse_box = st.empty()
        audio_box = st.empty()

        for i in range(start_num, end_num + 1):
            verse_text = verse_texts[i - 1]
            file_path = os.path.join(audio_dir, f"{i:02d}_{i}절.wav")

            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()

                verse_box.markdown(f"""
                <div style='
                    background: rgba(255,255,255,0.85);
                    border-radius: 12px;
                    padding: 16px 20px;
                    margin-top: 12px;
                    font-size: 1.2em;
                    font-weight: 500;
                    color: #1a2a4f;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
                '><b>{i}절</b> {verse_text}</div>
                """, unsafe_allow_html=True)

                audio_box.markdown(f"""
                <audio autoplay controls>
                    <source src="data:audio/wav;base64,{b64}" type="audio/wav">
                    브라우저가 오디오를 지원하지 않습니다.
                </audio>
                """, unsafe_allow_html=True)

                time.sleep(7)  # 각 절마다 재생 시간 확보
            else:
                st.error(f"{i}절 오디오 파일이 없습니다.")
                break

        # ✅ 포인트 1회 지급
        partial_key = f"{nickname}_partial_listened_{today}"
        if partial_key not in st.session_state:
            st.session_state.user_points[nickname] += 1
            st.session_state[partial_key] = True
            with open(USER_POINT_FILE, "w", encoding="utf-8") as f:
                json.dump(st.session_state.user_points, f, ensure_ascii=False, indent=2)












# ✅ 전체 듣기 ---
elif mode == "전체 듣기":
    today = str(datetime.date.today())

    # 상단 안내 문구
    st.markdown(
        "<span style='color:#fff; font-size:1.13em; font-weight:900;'>🎵 전체 오디오 자동 재생</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='markdown-highlight'>전체 오디오를 자동으로 재생합니다.</div>",
        unsafe_allow_html=True
    )

    # 🎧 표준 속도
    st.markdown("<h5 style='color:white; margin-top:24px;'>🔊 표준 속도</h5>", unsafe_allow_html=True)

    if os.path.exists(full_audio_file):
        # ✅ 오디오 자동 출력
        st.audio(full_audio_file, format="audio/wav")

        # ✅ 포인트 자동 지급 (1일 1점)
        full_key = f"{nickname}_full_listened_{today}"
        if full_key not in st.session_state:
            st.session_state.user_points[nickname] += 1   # 기존 3 → ✅ 1로 수정
            st.session_state[full_key] = True

            # ✅ 포인트 저장
            with open(USER_POINT_FILE, "w", encoding="utf-8") as f:
                json.dump(st.session_state.user_points, f, ensure_ascii=False, indent=2)
    else:
        st.error("full_audio.wav 파일을 audio 폴더 안에 넣어주세요.")

    # 🐢 느린 속도
    st.markdown("<h5 style='color:white; margin-top:24px;'>🐢 조금 느리게</h5>", unsafe_allow_html=True)
    slow_audio_file = os.path.join(audio_dir, "full_audio2.wav")
    if os.path.exists(slow_audio_file):
        # ❗ 느린 속도는 포인트 미지급 (재생만)
        st.audio(slow_audio_file, format="audio/wav")
    else:
        st.error("full_audio2.wav 파일을 audio 폴더 안에 넣어주세요.")








# ✅ 부분 암송 테스트 ---
elif mode == "부분 암송 테스트":
    st.subheader("🧠 부분 암송 테스트")

    # ✅ CSS 정의 (전체 라벨용 / 절별 라벨용 구분)
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

        .markdown-highlight {
            font-size: 1.15em;
            font-weight: 900;
            text-shadow: 0px 0px 6px rgba(0, 0, 0, 0.6);
            margin-bottom: 6px;
        }

        .markdown-highlight.all-label {
            color: #90caf9;
        }

        .markdown-highlight.verse-label {
            color: #ffffff;
        }

        .verse-label-box {
            display: inline-block;
            background: rgba(255,255,255,0.94);
            color: #000000;
            font-size: 1.15em;
            font-weight: 800;
            padding: 4px 13px 4px 10px;
            border-radius: 7px;
            margin-bottom: 6px;
            box-shadow: 0 2px 12px rgba(70,70,120,0.13);
        }
        </style>
    """, unsafe_allow_html=True)

    # ✅ 강조된 시작절 안내 문구
    st.markdown('<div class="markdown-highlight all-label">📄 시작 절을 선택하세요.</div>', unsafe_allow_html=True)

    start_label = st.selectbox(
        label="", 
        options=[f"{i}절" for i in range(1, len(verse_texts) - 4)],
        key="partial_select"
    )
    start_num = int(start_label.replace("절", ""))

    # ✅ 전체 정답/결과 보기 토글 강조
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="markdown-highlight all-label">전체 정답 보기</div>', unsafe_allow_html=True)
        show_answer_all = st.toggle("", value=False, key="partial_show_answer")
    with col2:
        st.markdown('<div class="markdown-highlight all-label">전체 결과 보기</div>', unsafe_allow_html=True)
        show_result_all = st.toggle("", value=False, key="partial_show_result")

    # ✅ 틀린 부분 빨간색 표시 함수
    def highlight_diff(correct, user):
        correct_clean = clean_text(correct)
        user_clean = clean_text(user)
        diff = difflib.ndiff(correct_clean, user_clean)
        result = ""
        for d in diff:
            if d.startswith("  "):
                result += d[-1]
            elif d.startswith("- "):
                result += f"<span style='color:red'>{d[-1]}</span>"
        return result

    # ✅ 절 반복 (5절)
    for i in range(start_num, start_num + 5):
        verse_index = i - 1
        correct_text = verse_texts[verse_index]
        key = f"partial_{i}"
        typed_input = st.session_state.get(key, "").strip()

        # ✅ 절 번호 라벨 (검정색 적용)
        st.markdown(f"<span class='verse-label-box'>{i}절</span>", unsafe_allow_html=True)

        # ✅ 절별 정답/결과 보기 토글 강조
        col_ans, col_result = st.columns([1, 1])
        with col_ans:
            st.markdown(f'<div class="markdown-highlight verse-label">{i}절 정답 보기</div>', unsafe_allow_html=True)
            show_ans_i = st.checkbox("", key=f"partial_show_ans_{i}")
        with col_result:
            st.markdown(f'<div class="markdown-highlight verse-label">{i}절 결과 보기</div>', unsafe_allow_html=True)
            show_result_i = st.checkbox("", key=f"partial_show_result_{i}")

        # ✅ 표시 우선순위
        if show_result_all or show_result_i:
            if typed_input == "":
                st.markdown("<div class='readonly-box'><span style='color:#d63e22;'>❗ 미입력</span></div>", unsafe_allow_html=True)
            else:
                is_correct = compare_texts(correct_text, typed_input)
                if is_correct:
                    st.markdown("<div class='readonly-box'>✅ 정답</div>", unsafe_allow_html=True)
                else:
                    highlighted = highlight_diff(correct_text, typed_input)
                    st.markdown(f"<div class='readonly-box'>{highlighted}</div>", unsafe_allow_html=True)

                # ✅ 포인트 지급
                today = str(datetime.date.today())
                partial_test_key = f"{nickname}_partial_tested_{i}_{today}"
                test_keys_today = [
                    k for k in st.session_state
                    if k.startswith(f"{nickname}_partial_tested_") and today in k
                ]

                if partial_test_key not in st.session_state and len(test_keys_today) < 3 and is_correct:
                    st.session_state.user_points[nickname] += 1
                    st.session_state[partial_test_key] = True
                    with open(USER_POINT_FILE, "w", encoding="utf-8") as f:
                        json.dump(st.session_state.user_points, f, ensure_ascii=False, indent=2)
                    st.success(f"📚 {i}절 암송 성공! +1점 지급되었습니다. (오늘 총 {len(test_keys_today)+1}/3)")

        elif show_answer_all or show_ans_i:
            st.markdown(f"<div class='readonly-box'>{correct_text}</div>", unsafe_allow_html=True)

        else:
            st.text_area(
                "",
                value=typed_input,
                key=key,
                placeholder="직접 입력해 보세요.",
                label_visibility="collapsed"
            )







# ✅ 전체 암송 테스트 ---
elif mode == "전체 암송 테스트":
    st.subheader("🧠 전체 암송 테스트")

    # ✅ 스타일 통일 적용 (부분 암송 테스트와 동일)
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

        .markdown-highlight {
            font-size: 1.15em;
            font-weight: 900;
            text-shadow: 0px 0px 6px rgba(0,0,0,0.6);
            margin-bottom: 6px;
        }

        .markdown-highlight.all-label {
            color: #90caf9;
        }

        .markdown-highlight.verse-label {
            color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)

    # ✅ 전체 정답/결과 보기 라벨
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="markdown-highlight all-label">전체 정답 보기</div>', unsafe_allow_html=True)
        show_answer_all = st.toggle("", value=False, key="full_show_answer")
    with col2:
        st.markdown('<div class="markdown-highlight all-label">전체 결과 보기</div>', unsafe_allow_html=True)
        show_result_all = st.toggle("", value=False, key="full_show_result")

    # ✅ 틀린 부분 하이라이트 함수
    def highlight_diff(correct, user):
        correct_clean = clean_text(correct)
        user_clean = clean_text(user)
        diff = difflib.ndiff(correct_clean, user_clean)
        result = ""
        for d in diff:
            if d.startswith("  "):
                result += d[-1]
            elif d.startswith("- "):
                result += f"<span style='color:red'>{d[-1]}</span>"
            elif d.startswith("+ "):
                continue
        return result

    user_inputs = []

    for i in range(len(verse_texts)):
        correct_text = verse_texts[i]
        key = f"full_{i}"
        if key not in st.session_state:
            st.session_state[key] = ""

        # ✅ 절 번호 표시
        st.markdown(f"""
            <span style="
                display: inline-block;
                background: rgba(255,255,255,0.94);
                color: #000000;
                font-size: 1.15em;
                font-weight: 800;
                padding: 4px 13px 4px 10px;
                border-radius: 7px;
                margin-bottom: 6px;
                box-shadow: 0 2px 12px rgba(70,70,120,0.13);
            ">{i+1}절</span>
        """, unsafe_allow_html=True)

        # ✅ 절별 정답/결과 보기 라벨 강조
        col_ans, col_result = st.columns([1, 1])
        with col_ans:
            st.markdown(f'<div class="markdown-highlight verse-label">{i+1}절 정답 보기</div>', unsafe_allow_html=True)
            show_ans_i = st.checkbox("", key=f"show_ans_{i}")
        with col_result:
            st.markdown(f'<div class="markdown-highlight verse-label">{i+1}절 결과 보기</div>', unsafe_allow_html=True)
            show_result_i = st.checkbox("", key=f"show_result_{i}")

        typed_input = st.session_state.get(key, "").strip()

        if show_result_all or show_result_i:
            if typed_input == "":
                st.markdown("<div class='readonly-box'><span style='color:#d63e22;'>❗ 미입력</span></div>", unsafe_allow_html=True)
            else:
                is_correct = compare_texts(correct_text, typed_input)
                if is_correct:
                    st.markdown("<div class='readonly-box'>✅ 정답</div>", unsafe_allow_html=True)
                else:
                    highlighted = highlight_diff(correct_text, typed_input)
                    st.markdown(f"<div class='readonly-box'>{highlighted}</div>", unsafe_allow_html=True)

                today = str(datetime.date.today())
                full_test_key = f"{nickname}_full_tested_{i}_{today}"
                full_keys_today = [k for k in st.session_state if k.startswith(f"{nickname}_full_tested_") and today in k]

                if full_test_key not in st.session_state and len(full_keys_today) < 29 and is_correct:
                    st.session_state.user_points[nickname] += 1
                    st.session_state[full_test_key] = True

                    with open(USER_POINT_FILE, "w", encoding="utf-8") as f:
                        json.dump(st.session_state.user_points, f, ensure_ascii=False, indent=2)

                    st.success(f"📚 {i+1}절 암송 성공! +1점 지급되었습니다. (오늘 총 {len(full_keys_today)+1}/29)")

        elif show_answer_all or show_ans_i:
            st.markdown(f"<div class='readonly-box'>{correct_text}</div>", unsafe_allow_html=True)

        else:
            input_text = st.text_area(
                "",
                value=st.session_state[key],
                key=key,
                placeholder="직접 입력해보세요.",
                label_visibility="collapsed"
            )

        user_inputs.append(typed_input)





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
