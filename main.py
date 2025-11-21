import streamlit as st

# 1. 페이지 기본 설정 (탭 제목 및 아이콘)
st.set_page_config(
    page_title="MBTI 진로 나침반",
    page_icon="🧭",
    layout="centered"
)

# 2. CSS로 간단한 스타일링 (폰트 및 여백 조정)
st.markdown("""
    <style>
    .main {
        color: #333333;
    }
    .stSelectbox > div > div {
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    h1 {
        color: #4F8BF9;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. MBTI 데이터베이스 (성격 키워드 + 추천 진로 3가지)
mbti_data = {
    "ISTJ": {
        "desc": "신중하고 철저한 관리자형 | 사실에 근거하여 사고함 🧐",
        "jobs": ["📊 회계/재무 전문가", "⚖️ 판사 및 법률가", "💻 시스템 관리자"]
    },
    "ISFJ": {
        "desc": "용감한 수호자형 | 성실하고 온화하며 협조적임 🛡️",
        "jobs": ["🏥 간호사 및 의료인", "🏫 초중등 교사", "📚 사서 및 기록물 관리자"]
    },
    "INFJ": {
        "desc": "통찰력 있는 선지자형 | 사람에 대한 깊은 탐구심 🔮",
        "jobs": ["🧠 심리 상담가", "✍️ 작가 및 시나리오 작가", "🎨 아트 디렉터"]
    },
    "INTJ": {
        "desc": "용의주도한 전략가형 | 독창적이고 판단력이 냉철함 ♟️",
        "jobs": ["🔬 자연과학 연구원", "📈 투자 분석가(Quant)", "🤖 AI 개발자"]
    },
    "ISTP": {
        "desc": "만능 재주꾼형 | 도구 사용에 능숙하고 상황 적응력이 높음 🛠️",
        "jobs": ["✈️ 파일럿 및 항공 전문가", "🕵️ 범죄 수사관", "🏗️ 토목/기계 엔지니어"]
    },
    "ISFP": {
        "desc": "호기심 많은 예술가형 | 온화하고 겸손하며 삶의 여유를 즐김 🎨",
        "jobs": ["👗 패션 디자이너", "🌿 조경/화훼 전문가", "🩺 수의사"]
    },
    "INFP": {
        "desc": "열정적인 중재자형 | 이상적인 세상을 만들어가는 몽상가 🦋",
        "jobs": ["🎬 멀티미디어 아티스트", "🗣️ 전문 강사/코치", "🌍 국제기구 활동가"]
    },
    "INTP": {
        "desc": "논리적인 사색가형 | 지적 호기심이 넘치는 아이디어 뱅크 💡",
        "jobs": ["📐 소프트웨어 아키텍트", "🧪 물리학/천문학자", "📉 경제학자"]
    },
    "ESTP": {
        "desc": "모험을 즐기는 사업가형 | 직설적이고 행동 중심적임 🏎️",
        "jobs": ["🤝 창업가(CEO)", "🎤 스포츠 에이전트", "🚒 소방관/구조대원"]
    },
    "ESFP": {
        "desc": "자유로운 영혼의 연예인형 | 사교적이고 에너지가 넘침 🎉",
        "jobs": ["📺 방송 연예인/유튜버", "✈️ 승무원", "🎉 이벤트 기획자"]
    },
    "ENFP": {
        "desc": "재기발랄한 활동가형 | 열정적이고 창의적인 아이디어 뱅크 ✨",
        "jobs": ["📢 마케팅/홍보 전문가", "📰 저널리스트", "🎭 공연 예술가"]
    },
    "ENTP": {
        "desc": "뜨거운 논쟁을 즐기는 변론가형 | 풍부한 지식과 입담 🗣️",
        "jobs": ["⚖️ 변호사", "🚀 벤처 투자자", "💡 발명가/혁신가"]
    },
    "ESTJ": {
        "desc": "엄격한 관리자형 | 사무적, 실용적, 현실적임 👔",
        "jobs": ["🏢 경영 컨설턴트", "👮 경찰/군 장교", "💊 약사"]
    },
    "ESFJ": {
        "desc": "사교적인 외교관형 | 타인을 돕고 조화를 이룸 🤝",
        "jobs": ["🏨 호텔리어/관광 전문가", "🏥 의료 행정 전문가", "📢 홍보 담당자(PR)"]
    },
    "ENFJ": {
        "desc": "정의로운 사회운동가형 | 카리스마와 충만한 열정 🔥",
        "jobs": ["🗣️ 정치인/사회운동가", "🏫 교육 행정가", "👥 인사 담당자(HR)"]
    },
    "ENTJ": {
        "desc": "대담한 통솔자형 | 철저한 준비와 활동적인 리더십 🦁",
        "jobs": ["🏢 기업 임원(Executive)", "💼 경영 컨설턴트", "🏗️ 도시 계획가"]
    }
}

# 4. 메인 화면 구성
st.title("✨ 찬환쌤의 진로 나침반 🧭")
st.subheader("학생의 성향(MBTI)에 딱 맞는 미래를 찾아보세요!")
st.markdown("---")

# 5. 사용자 입력 (MBTI 선택)
# 컬럼을 나누어 중앙에 배치하는 느낌을 줌
col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f9d1-200d-1f3eb.png", width=100) # 선생님 이모지

with col2:
    st.markdown("#### 🏫 학생의 MBTI를 선택해주세요")
    selected_mbti = st.selectbox(
        "아래에서 유형을 골라주세요 👇",
        options=["선택해주세요"] + list(mbti_data.keys()),
        label_visibility="collapsed"
    )

# 6. 결과 출력
if selected_mbti != "선택해주세요":
    data = mbti_data[selected_mbti]
    
    st.markdown("---")
    st.markdown(f"### 🧐 분석 결과: **{selected_mbti}**")
    st.info(data["desc"])
    
    st.markdown("#### 🚀 찬환쌤이 추천하는 BEST 진로 3")
    
    # 3개의 카드를 병렬로 배치
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.success(f"**1순위**\n\n{data['jobs'][0]}")
    with c2:
        st.success(f"**2순위**\n\n{data['jobs'][1]}")
    with c3:
        st.success(f"**3순위**\n\n{data['jobs'][2]}")

    st.markdown("---")
    st.caption("🎓 이 결과는 참고용이며, 학생의 흥미와 적성을 고려한 추가 상담이 필요합니다.")

else:
    # 선택 전 대기 화면
    st.markdown("---")
    st.markdown("#### 👋 환영합니다!")
    st.write("왼쪽(또는 위)의 선택상자에서 학생의 MBTI 유형을 선택하면")
    st.write("성격 특성과 추천 진로가 마법처럼 나타납니다! ✨")
