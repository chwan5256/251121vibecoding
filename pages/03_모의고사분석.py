import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# 페이지 설정
st.set_page_config(
    page_title="고3 성적 정밀 분석 시스템",
    page_icon="🎓",
    layout="wide"
)

# 스타일 설정 (가독성 향상)
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 고3 모의고사 성적 정밀 분석 시스템")
st.markdown("### 🚀 Data-Driven 학급 경영 & 진학 상담 도구")

# 사이드바: 파일 업로드
st.sidebar.header("📂 데이터 입력")
uploaded_file = st.sidebar.file_uploader("성적 리스트(CSV)를 업로드하세요", type=['csv'])

# --- 함수 정의 ---

@st.cache_data
def load_data(file):
    """데이터 로드 및 전처리"""
    try:
        df = pd.read_csv(file, header=[1, 2], encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(file, header=[1, 2], encoding='utf-8')
    except Exception as e:
        st.error(f"파일 로드 실패: {e}")
        return None

    # 컬럼 매핑
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
    
    if len(df.columns) >= len(new_columns):
        df.columns = new_columns + [f"col_{i}" for i in range(len(df.columns) - len(new_columns))]
    else:
        df.columns = new_columns[:len(df.columns)]

    # 숫자 변환 및 반 정보 추출
    numeric_cols = ['국어_점수', '수학_점수', '영어_점수', '탐구1_점수', '탐구2_점수', '총점_국수탐', '전체_석차']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if '학번' in df.columns:
        df['학번'] = df['학번'].fillna(0).astype(int).astype(str)
        df['반'] = df['학번'].apply(lambda x: x[1:3] if len(x) == 5 else '기타')
        # 반 정렬을 위해 숫자 변환이 가능한 경우 변환
        try:
            df['반_sort'] = df['반'].astype(int)
        except:
            df['반_sort'] = 999 
        df = df.sort_values(['반_sort', '학번']).drop(columns=['반_sort'])

    return df

def convert_df_to_excel(df, sheet_name='Sheet1'):
    """엑셀 다운로드를 위한 바이너리 변환"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

# --- 메인 로직 ---

if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is not None:
        # 탭 구성
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 종합 대시보드", 
            "🏫 반별 비교", 
            "🔍 탐구 선택 분석", 
            "👤 학생 조회 (Q2)", 
            "📥 데이터 다운로드 (Q3)"
        ])

        # [Tab 1] 종합 대시보드
        with tab1:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("응시 인원", f"{len(df)}명")
            col2.metric("국수탐 전체 평균", f"{df['총점_국수탐'].mean():.1f}점")
            col3.metric("수학 1등급 추정(상위4%)", f"{df['수학_점수'].quantile(0.96):.0f}점")
            col4.metric("최고점(국수탐)", f"{df['총점_국수탐'].max():.0f}점")
            
            st.divider()
            
            # 산점도
            fig_scatter = px.scatter(
                df, x='국어_점수', y='수학_점수', color='탐구1_과목',
                size='총점_국수탐', hover_data=['성명', '반'],
                title="국어 vs 수학 점수 상관관계 (점 크기: 총점, 색상: 탐구1)",
                labels={'국어_점수': '국어', '수학_점수': '수학'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        # [Tab 2] 반별 비교
        with tab2:
            st.subheader("반별 성적 현황")
            
            # 반별 평균 계산
            class_summary = df.groupby('반')[['국어_점수', '수학_점수', '영어_점수', '총점_국수탐']].mean().reset_index()
            
            fig_bar = px.bar(
                class_summary, x='반', y=['국어_점수', '수학_점수', '영어_점수'],
                barmode='group', title="반별 주요 과목 평균",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            st.info("💡 팁: 특정 반의 막대를 더블 클릭하면 그 반만 하이라이트 됩니다.")

        # [Tab 3] 탐구 선택 분석 (NEW FEATURE)
        with tab3:
            st.subheader("🔬 탐구 과목 선택과 총점의 관계")
            st.markdown("어떤 탐구 과목을 선택한 학생 집단의 국/수/탐 총점이 높은지 분석합니다.")

            # 데이터 변환 (Wide -> Long): 탐구1, 탐구2를 합쳐서 분석
            t1 = df[['탐구1_과목', '총점_국수탐']].rename(columns={'탐구1_과목': '탐구과목'})
            t2 = df[['탐구2_과목', '총점_국수탐']].rename(columns={'탐구2_과목': '탐구과목'})
            tamgu_long = pd.concat([t1, t2]).dropna()
            
            # 과목별 총점 평균 및 학생 수 계산
            tamgu_stats = tamgu_long.groupby('탐구과목')['총점_국수탐'].agg(['mean', 'count', 'std']).reset_index()
            tamgu_stats = tamgu_stats.sort_values('mean', ascending=False) # 성적 높은 순 정렬

            # 1. 탐구 과목별 '총점 평균' 비교 (Bar Chart)
            fig_tamgu_score = px.bar(
                tamgu_stats, x='탐구과목', y='mean',
                color='mean', color_continuous_scale='Bluered',
                text_auto='.0f',
                title="탐구 과목 선택자별 '국수탐 총점' 평균 (높은 순)",
                hover_data=['count'],
                labels={'mean': '국수탐 총점 평균', 'count': '응시자 수'}
            )
            st.plotly_chart(fig_tamgu_score, use_container_width=True)
            
            # 2. 탐구 과목별 '총점 분포' (Box Plot) - 더욱 상세한 분석
            fig_tamgu_dist = px.box(
                tamgu_long, x='탐구과목', y='총점_국수탐',
                color='탐구과목',
                title="탐구 과목 선택자별 총점 분포 (Box Plot)",
                points=False # 점이 너무 많으면 복잡하므로 박스만 표시
            )
            fig_tamgu_dist.update_layout(xaxis={'categoryorder':'mean descending'}) # 평균 높은 순 정렬
            st.plotly_chart(fig_tamgu_dist, use_container_width=True)
            
            st.caption("""
            **해석 가이드**: 
            - 상단 막대 그래프: 해당 탐구 과목을 선택한 학생들의 **전체적인 학업 역량(총점)**을 보여줍니다. 
            - 예를 들어, '물리학1' 선택자의 총점 평균이 높다면, 상위권 학생들이 주로 물리를 선택함을 의미할 수 있습니다.
            """)

        # [Tab 4] 학생 조회 (Q2 구현)
        with tab4:
            st.subheader("🔍 학생 개별 성적 조회")
            
            col_search, col_empty = st.columns([1, 2])
            with col_search:
                search_name = st.text_input("학생 이름을 입력하세요 (일부만 입력해도 검색됨)")
            
            if search_name:
                # 이름 검색 로직
                result = df[df['성명'].str.contains(search_name)]
                
                if len(result) == 0:
                    st.warning("검색된 학생이 없습니다.")
                else:
                    st.success(f"{len(result)}명의 학생이 검색되었습니다.")
                    
                    # 카드 형태로 개별 성적 보여주기
                    for index, row in result.iterrows():
                        with st.container():
                            st.markdown(f"### 🧑‍🎓 {row['반']}반 {row['성명']} ({row['학번']})")
                            
                            # 주요 성적 메트릭
                            m1, m2, m3, m4, m5 = st.columns(5)
                            m1.metric("국어", f"{row['국어_점수']}점", f"({row['국어_선택']})")
                            m2.metric("수학", f"{row['수학_점수']}점", f"({row['수학_선택']})")
                            m3.metric("영어", f"{row['영어_점수']}점")
                            m4.metric("국수탐 총점", f"{row['총점_국수탐']}점")
                            m5.metric("전교 석차", f"{row['전체_석차']:.0f}등")
                            
                            # 탐구 과목 테이블
                            st.markdown("**[탐구 과목 성적]**")
                            tamgu_df = pd.DataFrame({
                                '과목': [row['탐구1_과목'], row['탐구2_과목']],
                                '점수': [row['탐구1_점수'], row['탐구2_점수']]
                            })
                            st.table(tamgu_df)
                            st.divider()

        # [Tab 5] 다운로드 (Q3 구현)
        with tab5:
            st.subheader("💾 분석 결과 다운로드")
            st.markdown("현재 분석된 데이터와 통계 자료를 엑셀 파일로 다운로드할 수 있습니다.")
            
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                # 전체 성적 데이터 다운로드
                excel_data = convert_df_to_excel(df)
                st.download_button(
                    label="📥 전체 성적 데이터 (Excel)",
                    data=excel_data,
                    file_name='processed_grades.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )
            
            with col_d2:
                # 반별 요약 데이터 다운로드
                class_summary = df.groupby('반')[['국어_점수', '수학_점수', '영어_점수', '총점_국수탐']].mean().reset_index()
                excel_summary = convert_df_to_excel(class_summary)
                st.download_button(
                    label="📥 반별 평균 통계 (Excel)",
                    data=excel_summary,
                    file_name='class_summary.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )

else:
    st.info("👈 왼쪽 사이드바에서 CSV 파일을 먼저 업로드해주세요.")
