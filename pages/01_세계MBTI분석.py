import streamlit as st
import pandas as pd
import altair as alt

# 페이지 설정 (레이아웃을 넓게 설정)
st.set_page_config(layout="wide", page_title="국가별 MBTI 분석")

# 제목
st.title("🌏 국가별 MBTI 성향 분석 대시보드")
st.markdown("""
이 웹앱은 전 세계 국가별 MBTI 유형 비율 데이터를 시각화합니다. 
관심 있는 MBTI 유형을 선택하여 어느 나라에서 해당 유형의 비율이 높거나 낮은지 확인해보세요.
""")

# 데이터 로드 함수 (캐싱 적용하여 성능 최적화)
@st.cache_data
def load_data():
    # CSV 파일 읽기
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("데이터 파일(countriesMBTI_16types.csv)을 찾을 수 없습니다. 파일이 같은 디렉토리에 있는지 확인해주세요.")
    st.stop()

# 사이드바: MBTI 선택
mbti_list = df.columns[1:].tolist()  # 첫 번째 컬럼(Country)을 제외한 나머지 컬럼 리스트
selected_mbti = st.sidebar.selectbox("분석할 MBTI 유형을 선택하세요", mbti_list, index=0)

# 메인 화면 구성
st.header(f"📊 {selected_mbti} 유형 비율 분석")

# 선택된 MBTI 기준으로 데이터 정렬
sorted_df = df.sort_values(by=selected_mbti, ascending=False)

# 상위 10개 국가 데이터 추출
top_10 = sorted_df.head(10)
# 하위 10개 국가 데이터 추출
bottom_10 = sorted_df.tail(10).sort_values(by=selected_mbti, ascending=True) # 보기 좋게 작은 순서대로 정렬

# Altair 차트 생성 함수
def create_bar_chart(data, mbti_type, title, color_scheme):
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X(f'{mbti_type}:Q', title='비율'),
        y=alt.Y('Country:N', sort='-x', title='국가'),
        color=alt.Color(f'{mbti_type}:Q', scale=alt.Scale(scheme=color_scheme), legend=None),
        tooltip=['Country', alt.Tooltip(f'{mbti_type}:Q', format='.4f')]
    ).properties(
        title=title,
        height=400
    ).interactive()
    return chart

# 두 개의 컬럼으로 나누어 그래프 배치
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"⬆️ {selected_mbti} 비율이 가장 높은 상위 10개국")
    chart_top = create_bar_chart(top_10, selected_mbti, f"{selected_mbti} 비율 Top 10", "blues")
    st.altair_chart(chart_top, use_container_width=True)

    # 데이터 테이블 표시 (옵션)
    with st.expander("상위 10개국 데이터 보기"):
        st.dataframe(top_10[['Country', selected_mbti]])

with col2:
    st.subheader(f"⬇️ {selected_mbti} 비율이 가장 낮은 하위 10개국")
    # 하위 10개국은 그래프 가독성을 위해 y축 정렬을 조정 (값이 작은 순서대로 위에서 아래로 혹은 그 반대로)
    chart_bottom = alt.Chart(bottom_10).mark_bar().encode(
        x=alt.X(f'{selected_mbti}:Q', title='비율'),
        y=alt.Y('Country:N', sort='x', title='국가'), # 값이 작은 것부터 정렬
        color=alt.Color(f'{selected_mbti}:Q', scale=alt.Scale(scheme="reds"), legend=None),
        tooltip=['Country', alt.Tooltip(f'{selected_mbti}:Q', format='.4f')]
    ).properties(
        title=f"{selected_mbti} 비율 Bottom 10",
        height=400
    ).interactive()
    
    st.altair_chart(chart_bottom, use_container_width=True)

    # 데이터 테이블 표시 (옵션)
    with st.expander("하위 10개국 데이터 보기"):
        st.dataframe(bottom_10[['Country', selected_mbti]])

# 전체 데이터에 대한 인사이트 (선생님의 전문 분야와 연결)
st.divider()
st.markdown("### 💡 교육 및 진로 지도 인사이트")
st.info(f"""
**{selected_mbti}** 성향이 강한 국가들의 문화적 특징이나 교육 시스템을 분석해보면, 
우리나라 학생들 중 **{selected_mbti}** 유형을 가진 학생들에게 적합한 유학 국가나 
벤치마킹할 수 있는 진로 모델을 찾는 데 도움이 될 수 있습니다.
""")
