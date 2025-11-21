import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 기본 설정
st.set_page_config(
    page_title="고3 성적 분석 대시보드",
    page_icon="📊",
    layout="wide"
)

# 타이틀 및 설명
st.title("📊 고3 모의고사 성적 분석 대시보드")
st.markdown("""
**선생님, 환영합니다!** 성적 집계표(CSV)를 업로드하시면 반별 비교, 과목별 유불리, 학생별 세부 성적을 시각화해 드립니다.
""")

# 사이드바: 파일 업로드
st.sidebar.header("📂 데이터 업로드")
uploaded_file = st.sidebar.file_uploader("성적 리스트 CSV 파일을 업로드하세요.", type=['csv'])

# 데이터 전처리 함수
@st.cache_data
def load_data(file):
    try:
        # 1. 헤더가 2단(Row 1, 2)으로 되어 있는 구조 처리
        df = pd.read_csv(file, header=[1, 2], encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(file, header=[1, 2], encoding='utf-8')
    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

    # 2. 컬럼명 단순화 (MultiIndex -> Single Index)
    # 선생님 데이터 구조에 맞춰 핵심 컬럼만 매핑합니다.
    # 순서가 바뀔 수 있으므로 인덱스가 아닌 로직으로 접근하거나, 
    # 업로드된 파일이 정확히 같은 포맷이라고 가정하고 인덱스로 매핑합니다.
    
    # 새 컬럼명 리스트 (데이터 구조에 맞춰 순서대로 나열)
    new_columns = [
        '석차', '학번', '성명',
        '국어_선택', '국어_점수',
        '수학_선택', '수학_점수',
        '영어_점수',
        '탐구1_과목', '탐구1_점수',
        '탐구2_과목', '탐구2_점수',
        '한국사_과목', '한국사_점수',
        '탐구_소계', '총점_450', '총점_국수탐', '전체_석차',
        '국수영_합계', '국수영_석차'
    ]
    
    # 컬럼 개수가 맞는지 확인 후 할당 (다르면 앞부분만 매핑)
    if len(df.columns) >= len(new_columns):
        df.columns = new_columns + [f"col_{i}" for i in range(len(df.columns) - len(new_columns))]
    else:
        df.columns = new_columns[:len(df.columns)]

    # 3. 데이터 정제
    # 결측치 및 숫자가 아닌 데이터 처리
    numeric_cols = ['국어_점수', '수학_점수', '영어_점수', '탐구1_점수', '탐구2_점수', '총점_국수탐']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 4. '반' 정보 추출 (학번 30919 -> 9반)
    # 학번이 float일 수 있으므로 처리
    if '학번' in df.columns:
        df['학번'] = df['학번'].fillna(0).astype(int).astype(str)
        df['반'] = df['학번'].apply(lambda x: x[1:3] if len(x) == 5 else '기타')
        df['반'] = df['반'].astype(int, errors='ignore') # 정렬을 위해 숫자 변환 시도

    return df

# 메인 로직
if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is not None:
        # 탭 구성
        tab1, tab2, tab3, tab4 = st.tabs(["📈 종합 현황", "🏫 반별 비교", "📚 과목별 분석", "📋 데이터 보기"])

        # --- Tab 1: 종합 현황 ---
        with tab1:
            st.header("학교 전체 성적 요약")
            
            # KPI 카드
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("전체 응시 인원", f"{len(df)}명")
            col2.metric("국수탐 총점 평균", f"{df['총점_국수탐'].mean():.1f}점")
            col3.metric("수학 평균", f"{df['수학_점수'].mean():.1f}점")
            col4.metric("영어 평균", f"{df['영어_점수'].mean():.1f}점")

            st.divider()

            # 산점도: 수학 점수 vs 총점 (상관관계)
            st.subheader("수학 점수와 총점의 상관관계")
            fig_scatter = px.scatter(
                df, 
                x='수학_점수', 
                y='총점_국수탐', 
                color='반', 
                hover_data=['성명', '국어_선택', '수학_선택'],
                title="수학 점수가 높을수록 총점이 높은가?",
                labels={'수학_점수': '수학 점수', '총점_국수탐': '국+수+탐 총점'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        # --- Tab 2: 반별 비교 ---
        with tab2:
            st.header("반별 학력 수준 비교")
            
            # 반별 평균 데이터 계산
            class_avg = df.groupby('반')[['국어_점수', '수학_점수', '영어_점수', '총점_국수탐']].mean().reset_index()
            # 반이 숫자인 경우 정렬
            try:
                class_avg['반'] = class_avg['반'].astype(int)
                class_avg = class_avg.sort_values('반')
                class_avg['반'] = class_avg['반'].astype(str) + "반" # 그래프 표시용
            except:
                pass

            # 반별 평균 막대 그래프 (Multi-bar)
            fig_class = px.bar(
                class_avg, 
                x='반', 
                y=['국어_점수', '수학_점수', '영어_점수'], 
                barmode='group',
                title="반별 주요 과목 평균 점수 비교",
                text_auto='.1f'
            )
            st.plotly_chart(fig_class, use_container_width=True)

            # 반별 박스플롯 (분포 확인)
            st.subheader("반별 총점 분포 (Box Plot)")
            st.caption("박스 안의 선은 중앙값을 의미하며, 점들은 학생 개개인의 점수 분포를 보여줍니다.")
            # 반 순서 정렬을 위해
            df_sorted = df.sort_values('반')
            df_sorted['반_str'] = df_sorted['반'].astype(str) + "반"
            
            fig_box = px.box(
                df_sorted, 
                x='반_str', 
                y='총점_국수탐', 
                color='반_str',
                points="all", # 모든 점 찍기
                hover_data=['성명'],
                title="반별 총점 분포 및 학생 위치"
            )
            st.plotly_chart(fig_box, use_container_width=True)

        # --- Tab 3: 과목별 분석 ---
        with tab3:
            st.header("선택 과목별 유불리 분석")

            col_a, col_b = st.columns(2)
            
            with col_a:
                st.subheader("수학 선택과목별 점수 분포")
                # 미적분/확통/기하
                fig_math = px.box(
                    df, 
                    x='수학_선택', 
                    y='수학_점수', 
                    color='수학_선택',
                    points='all',
                    hover_data=['성명', '반'],
                    title="미적분 vs 확통 vs 기하"
                )
                st.plotly_chart(fig_math, use_container_width=True)

            with col_b:
                st.subheader("국어 선택과목별 점수 분포")
                # 화작/언매
                fig_kor = px.box(
                    df, 
                    x='국어_선택', 
                    y='국어_점수', 
                    color='국어_선택',
                    points='all',
                    hover_data=['성명', '반'],
                    title="화법과작문 vs 언어와매체"
                )
                st.plotly_chart(fig_kor, use_container_width=True)
            
            # 탐구 과목 선택 비율 (Pie Chart or Bar)
            st.divider()
            st.subheader("탐구 과목 선택 비율 (Top 10)")
            
            # 탐구 1, 2 합치기
            s1 = df['탐구1_과목'].value_counts()
            s2 = df['탐구2_과목'].value_counts()
            tamgu_counts = s1.add(s2, fill_value=0).sort_values(ascending=False).head(10)
            
            fig_tamgu = px.bar(
                x=tamgu_counts.index, 
                y=tamgu_counts.values,
                labels={'x': '과목명', 'y': '학생 수'},
                color=tamgu_counts.values,
                title="가장 많이 선택한 탐구 과목 Top 10"
            )
            st.plotly_chart(fig_tamgu, use_container_width=True)

        # --- Tab 4: 데이터 보기 ---
        with tab4:
            st.header("업로드된 원본 데이터 (전처리 완료)")
            st.dataframe(df)

    else:
        st.warning("데이터를 불러오지 못했습니다. CSV 파일 형식을 확인해주세요.")

else:
    st.info("👈 왼쪽 사이드바에서 CSV 파일을 업로드해주세요.")
