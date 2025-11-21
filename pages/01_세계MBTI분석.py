import streamlit as st
import pandas as pd
import altair as alt

# 1. 페이지 기본 설정 (와이드 모드)
st.set_page_config(
    page_title="World MBTI Analysis",
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
st.title("🌐 국가별 MBTI 성향 분석")
st.markdown("특정 **MBTI 유형**을 선택하면, 해당 성향 비율이 가장 **높은 나라**와 **낮은 나라**를 보여줍니다.")

try:
    df = load_data()
except FileNotFoundError:
    st.error("데이터 파일(countriesMBTI_16types.csv)을 찾을 수 없습니다. 같은 폴더에 위치시켜 주세요.")
    st.stop()

# 3. 사이드바: MBTI 선택
# 첫 번째 컬럼(Country)을 제외한 나머지 컬럼을 MBTI 리스트로 확보
mbti_options = df.columns[1:].tolist()
selected_mbti = st.selectbox("분석할 MBTI 유형을 선택하세요:", mbti_options, index=0)

# 4. 데이터 필터링 및 정렬
# 선택된 MBTI 기준으로 내림차순 정렬
df_sorted = df.sort_values(by=selected_mbti, ascending=False)

# 상위 10개국
top_10 = df_sorted.head(10)

# 하위 10개국 (오름차순으로 정렬하여 가장 적은 나라부터 보이게 함)
bottom_10 = df_sorted.tail(10).sort_values(by=selected_mbti, ascending=True)

# 5. Altair 차트 생성 함수
def create_bar_chart(data, x_col, y_col, color_scheme, title, sort_order):
    """
    Altair를 이용해 인터랙티브 막대 그래프를 그리는 함수
    """
    chart = alt.Chart(data).mark_bar().encode(
        # x축: 비율 (백분율 포맷팅 적용 가능하지만, 여기선 원본 값 사용)
        x=alt.X(x_col, title=f'{selected_mbti} 비율'),
        # y축: 국가명 (값이 큰 순서 혹은 작은 순서대로 정렬)
        y=alt.Y(y_col, sort=sort_order, title='국가'),
        # 색상: 비율에 따라 진하기 다르게 표현
        color=alt.Color(x_col, scale=alt.Scale(scheme=color_scheme), legend=None),
        # 툴팁: 마우스 오버 시 상세 정보 표시
        tooltip=[
            alt.Tooltip(y_col, title='국가'),
            alt.Tooltip(x_col, title='비율', format='.4f')
        ]
    ).properties(
        title=title,
        height=400  # 그래프 높이 설정
    ).interactive() # 줌 및 팬(Pan) 기능 활성화
    
    return chart

# 6. 화면 출력 (위아래 배치)

# [상단] 비율이 가장 높은 10개국
st.subheader(f"📈 {selected_mbti} 비율이 가장 높은 나라 Top 10")
chart_top = create_bar_chart(
    top_10, 
    selected_mbti, 
    'Country', 
    'blues',  # 파란색 계열
    f"Top 10 Countries for {selected_mbti}", 
    '-x'      # x축 값이 큰 순서대로 정렬 (내림차순)
)
st.altair_chart(chart_top, use_container_width=True)

st.markdown("---") # 구분선

# [하단] 비율이 가장 적은 10개국
st.subheader(f"📉 {selected_mbti} 비율이 가장 낮은 나라 Top 10")
chart_bottom = create_bar_chart(
    bottom_10, 
    selected_mbti, 
    'Country', 
    'reds',   # 빨간색 계열
    f"Bottom 10 Countries for {selected_mbti}", 
    'x'       # x축 값이 작은 순서대로 정렬 (오름차순)
)
st.altair_chart(chart_bottom, use_container_width=True)

# 7. (선택사항) 데이터 원본 보기
with st.expander("📊 전체 데이터 원본 보기"):
    st.dataframe(df)
```

### 코드 실행 및 배포 포인트

1.  **파일 구성:** 위 코드를 `app.py`로 저장하고, 이전에 업로드하신 `countriesMBTI_16types.csv` 파일이 반드시 **같은 폴더**에 있어야 합니다.
2.  **배포 시 `requirements.txt`:** Streamlit Cloud에 배포할 때는 다음 내용이 담긴 `requirements.txt` 파일도 함께 업로드해야 합니다.
    ```text
    streamlit
    pandas
    altair
