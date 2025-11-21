import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import re

# 페이지 설정
st.set_page_config(
    page_title="고3 성적 정밀 분석 & 추적 시스템",
    page_icon="🎓",
    layout="wide"
)

# 스타일 커스텀 (가독성 향상)
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f3f5;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border-bottom: 2px solid #4e8cff;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 고3 모의고사 성적 정밀 분석 & 추적 시스템")
st.markdown("### 🚀 Data-Driven Counseling & Management")

# 사이드바: 다중 파일 업로드
st.sidebar.header("📂 데이터 입력")
st.sidebar.info("💡 3월, 6월, 9월 등 여러 달의 파일을 한 번에 선택해서 업로드하세요.")
uploaded_files = st.sidebar.file_uploader(
    "성적 파일들(CSV)을 모두 업로드하세요", 
    type=['csv'], 
    accept_multiple_files=True
)

# --- 함수 정의 ---

def extract_exam_name(filename):
    """파일명에서 'N월' 추출"""
    match = re.search(r'(\d+)월', filename)
    if match:
        return f"{match.group(1)}월"
    return filename.split('.')[0]

def load_single_file(file):
    """단일 파일 전처리"""
    try:
        df = pd.read_csv(file, header=[1, 2], encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(file, header=[1, 2], encoding='utf-8')
    except Exception as e:
        return None

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
    
    current_cols = len(df.columns)
    if current_cols >= len(new_columns):
        df.columns = new_columns + [f"col_{i}" for i in range(current_cols - len(new_columns))]
    else:
        df.columns = new_columns[:current_cols]

    numeric_cols = ['국어_점수', '수학_점수', '영어_점수', '탐구1_점수', '탐구2_점수', '총점_국수탐', '전체_석차']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if '학번' in df.columns:
        df['학번'] = df['학번'].fillna(0).astype(int).astype(str)
        df['반'] = df['학번'].apply(lambda x: x[1:3] if len(x) == 5 else '기타')
    
    exam_name = extract_exam_name(file.name)
    df['시험명'] = exam_name
    
    month_match = re.search(r'(\d+)', exam_name)
    df['월_숫자'] = int(month_match.group(1)) if month_match else 99
    
    return df

@st.cache_data
def process_all_files(files):
    """모든 파일 통합"""
    all_dfs = []
    for file in files:
        df = load_single_file(file)
        if df is not None:
            all_dfs.append(df)
    
    if not all_dfs:
        return None
        
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df = final_df.sort_values(by=['월_숫자', '반', '학번'])
    return final_df

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- 메인 로직 ---

if uploaded_files:
    main_df = process_all_files(uploaded_files)

    if main_df is not None:
        # 시험 리스트 정렬 (3월 -> 4월 ...)
        exam_list = sorted(main_df['시험명'].unique(), key=lambda x: int(re.search(r'(\d+)', x).group(1)) if re.search(r'(\d+)', x) else 99)
        
        st.success(f"✅ 총 {len(uploaded_files)}개의 시험 데이터가 로드되었습니다: {', '.join(exam_list)}")

        # 탭 구성
        tabs = st.tabs([
            "📈 성적 추이(Trend)",
            "🚨 변동폭 분석(Who Changed?)", 
            "📊 최근 시험 분석", 
            "🏫 반별 비교", 
            "🔍 탐구 분석", 
            "👤 학생 조회"
        ])

        # --- [Tab 1] 성적 추이 ---
        with tabs[0]:
            st.header("📉 학생별 성적 히스토리")
            
            col_search, _ = st.columns([1, 2])
            with col_search:
                search_name = st.text_input("학생 이름 검색 (Enter)", placeholder="예: 정선재")
            
            if search_name:
                student_data = main_df[main_df['성명'].str.contains(search_name)].sort_values('월_숫자')
                
                if len(student_data) > 0:
                    info = student_data.iloc[-1]
                    st.subheader(f"🧑‍🎓 {info['성명']} ({info['반']}반) 성적 변화")
                    
                    # 그래프
                    fig_trend = go.Figure()
                    subjects = {'국어_점수': 'red', '수학_점수': 'blue', '영어_점수': 'green', '총점_국수탐': 'black'}
                    for subj, color in subjects.items():
                        fig_trend.add_trace(go.Scatter(
                            x=student_data['시험명'], y=student_data[subj],
                            mode='lines+markers', name=subj.split('_')[0],
                            line=dict(color=color, width=3 if subj=='총점_국수탐' else 1)
                        ))
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                    # 테이블 (스타일링 에러 방지 적용)
                    display = student_data[['시험명', '국어_점수', '수학_점수', '영어_점수', '탐구1_점수', '탐구2_점수', '총점_국수탐', '전체_석차']]
                    try:
                        st.dataframe(display.style.background_gradient(subset=['총점_국수탐'], cmap='Blues'))
                    except:
                        st.dataframe(display)
                else:
                    st.warning("검색 결과가 없습니다.")
            else:
                st.info("이름을 입력하면 개인별 성적 변화 그래프를 볼 수 있습니다.")

        # --- [Tab 2] 변동폭 분석 (요청하신 기능) ---
        with tabs[1]:
            st.header("🚨 Who Changed? (성적 변동 정밀 추적)")
            
            if len(exam_list) < 2:
                st.warning("⚠️ 비교 분석을 위해 최소 2개 이상의 파일이 필요합니다.")
            else:
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    base_exam = st.selectbox("기준 시험 (과거)", exam_list, index=len(exam_list)-2)
                with col_c2:
                    curr_exam = st.selectbox("비교 시험 (최근)", exam_list, index=len(exam_list)-1)
                
                if base_exam != curr_exam:
                    # 데이터 병합
                    df_base = main_df[main_df['시험명'] == base_exam][['학번', '성명', '반', '국어_점수', '수학_점수', '총점_국수탐']]
                    df_curr = main_df[main_df['시험명'] == curr_exam][['학번', '성명', '반', '국어_점수', '수학_점수', '총점_국수탐']]
                    
                    merged = pd.merge(df_curr, df_base, on=['학번', '성명', '반'], suffixes=('_최근', '_이전'))
                    
                    # 변동값 계산
                    merged['총점_변동'] = merged['총점_국수탐_최근'] - merged['총점_국수탐_이전']
                    merged['국어_변동'] = merged['국어_점수_최근'] - merged['국어_점수_이전']
                    merged['수학_변동'] = merged['수학_점수_최근'] - merged['수학_점수_이전']
                    
                    st.divider()
                    
                    # 1. 슬럼프 경보
                    st.subheader(f"📉 슬럼프 경보 (총점 -30점 이상 하락)")
                    slump = merged[merged['총점_변동'] <= -30].sort_values('총점_변동')
                    if not slump.empty:
                        st.error(f"총 {len(slump)}명의 학생이 관심이 필요합니다.")
                        st.dataframe(slump[['반', '성명', '총점_변동', '국어_변동', '수학_변동', '총점_국수탐_최근']])
                    else:
                        st.success("🎉 급격히 성적이 하락한 학생이 없습니다!")

                    st.divider()

                    # 2. 노력상 후보
                    st.subheader(f"🏆 노력상 후보 (성적 급상승 Top 5)")
                    rising = merged.sort_values('총점_변동', ascending=False).head(5)
                    st.table(rising[['반', '성명', '총점_변동', '총점_국수탐_이전', '총점_국수탐_최근']])

                    st.divider()

                    # 3. 과목 불균형 (수학Up 국어Down)
                    st.subheader("⚖️ 과목 불균형 (수학⬆️ 국어⬇️)")
                    st.markdown("수학 성적은 올랐는데(5점↑), 국어 성적은 떨어진(5점↓) 학생들입니다.")
                    
                    imbalance = merged[(merged['수학_변동'] >= 5) & (merged['국어_변동'] <= -5)]
                    
                    if not imbalance.empty:
                        fig_imb = px.scatter(
                            imbalance, x='국어_변동', y='수학_변동', 
                            text='성명', color='반',
                            title="국어 하락 vs 수학 상승 분포",
                            labels={'국어_변동': '국어 변동폭', '수학_변동': '수학 변동폭'}
                        )
                        fig_imb.add_hline(y=0, line_dash="dash", line_color="gray")
                        fig_imb.add_vline(x=0, line_dash="dash", line_color="gray")
                        st.plotly_chart(fig_imb, use_container_width=True)
                        st.dataframe(imbalance[['반', '성명', '국어_변동', '수학_변동']])
                    else:
                        st.info("해당 조건의 학생이 없습니다.")

        # --- [Tab 3] 최근 시험 분석 ---
        with tabs[2]:
            last_exam = exam_list[-1]
            st.header(f"📊 {last_exam} 상세 분석")
            
            latest_df = main_df[main_df['시험명'] == last_exam]
            col1, col2, col3 = st.columns(3)
            col1.metric("응시 인원", f"{len(latest_df)}명")
            col2.metric("평균 총점", f"{latest_df['총점_국수탐'].mean():.1f}점")
            col3.metric("수학 1등급 컷(4%)", f"{latest_df['수학_점수'].quantile(0.96):.0f}점")
            
            fig_sc = px.scatter(latest_df, x='국어_점수', y='수학_점수', color='탐구1_과목', size='총점_국수탐', hover_data=['성명'])
            st.plotly_chart(fig_sc, use_container_width=True)

        # --- [Tab 4] 반별 비교 ---
        with tabs[3]:
            st.header("🏫 반별 성적 비교")
            target_ex = st.selectbox("분석할 시험", exam_list, index=len(exam_list)-1, key='class_comp')
            t_df = main_df[main_df['시험명'] == target_ex]
            
            class_avg = t_df.groupby('반')[['국어_점수', '수학_점수', '영어_점수', '총점_국수탐']].mean().reset_index()
            fig_bar = px.bar(class_avg, x='반', y=['국어_점수', '수학_점수', '영어_점수'], barmode='group')
            st.plotly_chart(fig_bar, use_container_width=True)

        # --- [Tab 5] 탐구 분석 ---
        with tabs[4]:
            st.header("🔍 탐구 과목 분석")
            target_ex_tamgu = st.selectbox("분석할 시험", exam_list, index=len(exam_list)-1, key='tamgu_comp')
            t_df_tamgu = main_df[main_df['시험명'] == target_ex_tamgu]
            
            t1 = t_df_tamgu[['탐구1_과목', '총점_국수탐']].rename(columns={'탐구1_과목': '과목'})
            t2 = t_df_tamgu[['탐구2_과목', '총점_국수탐']].rename(columns={'탐구2_과목': '과목'})
            tamgu_long = pd.concat([t1, t2]).dropna()
            
            stats = tamgu_long.groupby('과목')['총점_국수탐'].agg(['mean', 'count']).sort_values('mean', ascending=False).reset_index()
            fig_t = px.bar(stats, x='과목', y='mean', color='mean', text='count', title="탐구 과목별 응시자 총점 평균")
            st.plotly_chart(fig_t, use_container_width=True)

        # --- [Tab 6] 학생 조회 ---
        with tabs[5]:
            st.header("📥 전체 데이터 다운로드")
            excel_data = convert_df_to_excel(main_df)
            st.download_button("전체 통합 데이터(Excel) 받기", excel_data, 'grade_analysis.xlsx')

    else:
        st.error("데이터 로드 실패. 파일 형식을 확인해주세요.")

else:
    st.info("👈 왼쪽 사이드바에 성적 파일들(CSV)을 업로드해주세요.")
