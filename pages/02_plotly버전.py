import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="World MBTI Analysis (Plotly)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    # CSV 파일이 같은 폴더에 있다고 가정
    file_path = 'countriesMBTI_16types.csv'
    df = pd.read_csv(file_path)
    return df

# 메인 타이틀
st.title("🌐 국가별 MBTI 성향 분석 (with Plotly)")
st.markdown("""
**Plotly**를 활용하여 특정 **MBTI 유형**의 국가별 비율을 시각화합니다.
마우스를 그래프 위에 올리면 상세 수치를 확인할 수 있으며, 그래프를 확대/축소할 수 있습니다.
""")

try:
    df = load_data()
except FileNotFoundError:
    st.error("데이터 파일(countriesMBTI_16types.csv)을 찾을 수 없습니다. 같은 폴더에 위치시켜 주세요.")
    st.stop()

# 3. 사이드바: MBTI 선택
mbti_options = df.columns[1:].tolist()
selected_mbti = st.sidebar.selectbox("분석할 MBTI 유형을 선택하세요:", mbti_options, index=0)

# 4. 데이터 필터링 및 정렬
# 전체 데이터를 해당 MBTI 기준으로 내림차순 정렬
df_sorted = df.sort_values(by=selected_mbti, ascending=False)

# 상위 10개국 (비율이 높은 순)
top_10 = df_sorted.head(10)
# Plotly 막대 그래프는 데이터프레임 순서대로 아래에서 위로 그리는 경우가 많으므로,
# 화면상 위에서부터 1위가 나오게 하려면 y축 설정을 뒤집거나 데이터를 역순으로 주어야 함.
# 여기서는 Plotly의 'yaxis={'categoryorder':'total ascending'}' 등을 활용하거나 데이터를 재정렬함.
top_10_reversed = top_10.sort_values(by=selected_mbti, ascending=True) # 그래프 그릴 때 위쪽이 큰 값이 되도록 조정용

# 하위 10개국 (비율이 낮은 순)
bottom_10 = df_sorted.tail(10)
# 하위 10개국 중 '가장 낮은' 나라가 가장 눈에 띄게(예: 맨 위나 맨 아래) 배치.
# 여기서는 비율이 '가장 낮은' 나라를 맨 위에 보여주기 위해 정렬.
bottom_10_sorted = bottom_10.sort_values(by=selected_mbti, ascending=False) 


# 5. 차트 그리기

# [상단] Top 10 그래프
st.subheader(f"⬆️ {selected_mbti} 비율이 가장 높은 나라 Top 10")

fig_top = px.bar(
    top_10_reversed, 
    x=selected_mbti, 
    y='Country', 
    orientation='h',
    text=selected_mbti, # 막대 끝에 수치 표시
    title=f"Top 10 Countries with Highest {selected_mbti} Ratio",
    color=selected_mbti, # 비율에 따라 색상 농도 조절
    color_continuous_scale='Blues'
)

# 그래프 레이아웃 다듬기 (수치 포맷 등)
fig_top.update_traces(texttemplate='%{text:.4f}', textposition='outside')
fig_top.update_layout(
    xaxis_title="Ratio", 
    yaxis_title="Country",
    height=500,
    margin=dict(l=0, r=0, t=40, b=0)
)

st.plotly_chart(fig_top, use_container_width=True)


st.markdown("---") # 구분선


# [하단] Bottom 10 그래프
st.subheader(f"⬇️ {selected_mbti} 비율이 가장 낮은 나라 Top 10")

fig_bottom = px.bar(
    bottom_10_sorted, 
    x=selected_mbti, 
    y='Country', 
    orientation='h',
    text=selected_mbti,
    title=f"Top 10 Countries with Lowest {selected_mbti} Ratio",
    color=selected_mbti,
    color_continuous_scale='Reds'
)

fig_bottom.update_traces(texttemplate='%{text:.4f}', textposition='outside')
fig_bottom.update_layout(
    xaxis_title="Ratio", 
    yaxis_title="Country",
    height=500,
    margin=dict(l=0, r=0, t=40, b=0)
)

st.plotly_chart(fig_bottom, use_container_width=True)

# 6. (선택사항) 데이터 원본 보기
with st.expander("📊 전체 데이터 원본 보기"):
    st.dataframe(df)
