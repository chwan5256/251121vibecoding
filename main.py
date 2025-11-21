import streamlit as st

# 1. 페이지 기본 설정 (탭 이름, 아이콘)
st.set_page_config(
    page_title="MBTI 문학 소믈리에",
    page_icon="📚",
    layout="centered"
)

# 2. CSS 스타일링 (타이틀 폰트 및 여백 조정)
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4A4A4A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-text {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .book-card {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #FF6B6B;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .quote-box {
        font-style: italic;
        color: #2C3E50;
        background-color: #E8F6F3;
        padding: 15px;
        border-radius: 10px;
        margin-top: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 (MBTI별 추천 도서 매핑)
mbti_books = {
    # 분석가형 (INTJ, INTP, ENTJ, ENTP)
    "INTJ": {"book": "1984", "author": "조지 오웰", "emoji": "👁️", "desc": "치밀한 전략가인 당신에게, 시스템과 통제에 대한 날카로운 통찰을 주는 책.", "quote": "자유란 2 더하기 2가 4라고 말할 수 있는 자유이다."},
    "INTP": {"book": "월든", "author": "헨리 데이비드 소로", "emoji": "🌿", "desc": "사색과 논리를 사랑하는 당신, 숲속에서의 고독과 철학적 사유를 즐겨보세요.", "quote": "내가 숲으로 들어간 것은 인생을 의도적으로 살아보기 위해서였다."},
    "ENTJ": {"book": "군주론", "author": "마키아벨리", "emoji": "👑", "desc": "대담한 통솔자인 당신에게, 리더십의 본질과 현실적인 권력을 다룬 고전.", "quote": "사랑받는 것보다 두려움의 대상이 되는 것이 훨씬 안전하다."},
    "ENTP": {"book": "돈키호테", "author": "세르반테스", "emoji": "⚔️", "desc": "뜨거운 논쟁과 모험을 즐기는 당신, 현실에 안주하지 않는 기사의 열정을 만나보세요.", "quote": "이룩할 수 없는 꿈을 꾸고, 이루어질 수 없는 사랑을 하고..."},

    # 외교관형 (INFJ, INFP, ENFJ, ENFP)
    "INFJ": {"book": "데미안", "author": "헤르만 헤세", "emoji": "🐣", "desc": "깊은 통찰력을 지닌 당신, 내면의 자아를 찾아가는 치열한 여정에 공감할 거예요.", "quote": "새는 알을 깨고 나오려 투쟁한다. 알은 세계이다."},
    "INFP": {"book": "어린 왕자", "author": "생텍쥐페리", "emoji": "🦊", "desc": "이상주의적이고 낭만적인 당신에게, 보이지 않는 것의 소중함을 일깨워주는 책.", "quote": "가장 중요한 것은 눈에 보이지 않아."},
    "ENFJ": {"book": "레 미제라블", "author": "빅토르 위고", "emoji": "🇫🇷", "desc": "정의롭고 이타적인 당신, 인간에 대한 뜨거운 사랑과 혁명의 서사를 추천합니다.", "quote": "사랑하는 것은 신의 얼굴을 보는 것이다."},
    "ENFP": {"book": "빨강 머리 앤", "author": "루시 모드 몽고메리", "emoji": "👒", "desc": "재기발랄한 활동가인 당신! 긍정과 상상력으로 세상을 물들이는 앤과 찰떡궁합.", "quote": "세상은 생각대로 되지 않는다고요? 하지만 생각대로 되지 않는다는 건 정말 멋져요!"},

    # 관리자형 (ISTJ, ISFJ, ESTJ, ESFJ)
    "ISTJ": {"book": "오만과 편견", "author": "제인 오스틴", "emoji": "📜", "desc": "사실과 원칙을 중시하는 당신, 섬세한 감정선과 이성적 판단 사이의 균형을 느껴보세요.", "quote": "편견은 내가 다른 사람을 사랑하지 못하게 하고, 오만은 다른 사람이 나를 사랑할 수 없게 만든다."},
    "ISFJ": {"book": "작은 아씨들", "author": "루이자 메이 올콧", "emoji": "🧶", "desc": "성실하고 따뜻한 수호자인 당신에게 가족애와 성장의 따스함을 선물합니다.", "quote": "우리의 짐은 우리가 짊어질 수 있도록 만들어졌다."},
    "ESTJ": {"book": "동물농장", "author": "조지 오웰", "emoji": "🐷", "desc": "엄격한 관리자인 당신, 조직과 사회의 규율이 어떻게 변질될 수 있는지 꿰뚫어보세요.", "quote": "모든 동물은 평등하다. 하지만 어떤 동물은 다른 동물보다 더욱 평등하다."},
    "ESFJ": {"book": "위대한 개츠비", "author": "F. 스콧 피츠제럴드", "emoji": "🥂", "desc": "사교적이고 헌신적인 당신, 화려함 속에 감춰진 인간의 고독과 사랑을 만나보세요.", "quote": "우리는 조류를 거스르는 배처럼 끊임없이 과거로 떠밀려 가면서도 앞으로 나아가는 것이다."},

    # 탐험가형 (ISTP, ISFP, ESTP, ESFP)
    "ISTP": {"book": "노인과 바다", "author": "어니스트 헤밍웨이", "emoji": "🦈", "desc": "만능 재주꾼인 당신, 군더더기 없는 문체와 묵묵한 사투가 주는 강렬함을 느껴보세요.", "quote": "인간은 파괴될 수는 있어도 패배할 수는 없다."},
    "ISFP": {"book": "달과 6펜스", "author": "서머싯 몸", "emoji": "🎨", "desc": "예술적 감각이 넘치는 당신, 현실(6펜스)을 버리고 꿈(달)을 쫓는 열망에 빠져보세요.", "quote": "나는 그림을 그려야 한다지 않소. 물에 빠지면 헤엄을 잘 치고 못 치고가 문제가 아니오."},
    "ESTP": {"book": "로빈슨 크루소", "author": "대니얼 디포", "emoji": "🏝️", "desc": "모험을 즐기는 사업가인 당신! 어떤 상황에서도 살아남는 현실적 해결 능력을 확인해보세요.", "quote": "두려움은 위험 그 자체보다도 1만 배는 더 무서운 것이다."},
    "ESFP": {"book": "톰 소여의 모험", "author": "마크 트웨인", "emoji": "🛶", "desc": "자유로운 영혼의 연예인인 당신에게, 규율에 얽매이지 않는 유쾌한 모험을 추천합니다.", "quote": "일을 놀이처럼 하면 인생은 끝없는 즐거움이 된다."}
}

# 4. 메인 화면 구성
st.markdown('<div class="main-header">📚 MBTI 문학 소믈리에</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">찬환쌤과 함께하는 나만의 고전 찾기! 당신의 성향을 선택해주세요.</div>', unsafe_allow_html=True)

# 5. 사용자 입력 (Selectbox)
col1, col2, col3 = st.columns([1, 2, 1]) # 중앙 정렬을 위한 컬럼 분할

with col2:
    selected_mbti = st.selectbox(
        "🔻 아래에서 본인의 MBTI를 선택하세요",
        options=sorted(mbti_books.keys()),
        index=None,
        placeholder="MBTI 선택..."
    )
    
    st.write("") # 여백 추가
    
    if selected_mbti:
        data = mbti_books[selected_mbti]
        
        # 버튼 클릭 없이 선택 즉시 결과 보여주기 (반응형 느낌)
        st.balloons() # 축하 효과 🎉
        
        st.markdown(f"""
        <div class="book-card">
            <h2 style='text-align: center; color: #333;'>{data['emoji']} {selected_mbti}를 위한 추천</h2>
            <hr>
            <h3 style='text-align: center; color: #2c3e50;'>📖 {data['book']}</h3>
            <p style='text-align: center; color: #7f8c8d; font-weight: bold;'>- {data['author']} -</p>
            <br>
            <p style='text-align: center; font-size: 1.1em;'>{data['desc']}</p>
            <div class="quote-box">
                "{data['quote']}"
            </div>
        </div>
        """, unsafe_allow_html=True)

# 6. 푸터 (Footer)
st.markdown("---")
st.caption("👨‍🏫 Created by 찬환쌤 | 지구과학 & 융합교육 | AI Education")
