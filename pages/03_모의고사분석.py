import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import re

# 페이지 설정
st.set_page_config(
    page_title="고3 성적 추이 분석 시스템",
    page_icon="📈",
    layout="wide"
)

# 스타일 커스텀
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    /* 탭 스타일 */
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

st.title("📈 고3 모의고사 성적 누적 분석 시스템")
st.markdown("### Data-Driven Growth Tracking & Counseling")

# 사이드바: 다중 파일 업로드
st.sidebar.header("📂 데이터 입력")
st.sidebar.info("💡 여러 달의 파일을 한 번에 선택해서 업로드하세요.\n(파일명에 '3월', '6월' 등이 포함되어야 합니다.)")
uploaded_files = st.sidebar.file_uploader(
    "성적 파일들(CSV)을 모두 업로드하세요", 
    type=['csv'], 
    accept_multiple_files=True
)

# --- 함수 정의 ---

def extract_exam_name(filename):
    """파일명에서 'N월' 또는 파일명 자체를 추출"""
    match = re.search(r'(\d+)월', filename)
    if match:
        return f"{match.group(1)}월"
    return filename.split('.')[0]

def load_single_file(file):
    """단일 파일 전처리 함수"""
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
    """모든 파일을 읽어서 하나로 합침"""
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
        exam_list = sorted(main_df['시험명'].unique(), key=lambda x: int(re.search(r'(\d+)', x).group(1)) if re.search(r'(\d+)', x) else 99)
        
        st.success(f"✅ 총 {len(uploaded_files)}개의 데이터 통합 완료: {', '.join(exam_list)}")

        # 탭 구성
        tabs = st.tabs([
            "📈 성적 추이(Trend)",
            "🚨 변동폭 분석(Who Changed?)",  # NEW FEATURE
            "📊 시험 상세 분석", 
            "🏫 반별 비교", 
            "🔍 탐구 분석", 
            "👤 학생 조회"
        ])

        # --- [Tab 1] 성적 변화 추이 ---
        with tabs[0]:
            st.header("📉 학생별/학급별 성적 변화 추적")
            trend_mode = st.radio("분석 모드", ["학생 개인별 추이", "반별 평균 추이"], horizontal=True)

            if trend_mode == "학생 개인별 추이":
                col_search, _ = st.columns([1, 2])
                with col_search:
                    search_name = st.text_input("학생 이름 검색", placeholder="예: 정선재")
                
                if search_name:
                    student_data = main_df[main_df['성명'].str.contains(search_name)].sort_values('월_숫자')
                    
                    if len(student_data) > 0:
                        recent_info = student_data.iloc[-1]
                        st.subheader(f"🧑‍🎓 {recent_info['성명']} ({recent_info['반']}반) 성적 히스토리")
                        
                        fig_trend = go.Figure()
                        subjects = {'국어_점수': 'red', '수학_점수': 'blue', '영어_점수': 'green', '총점_국수탐': 'black'}
                        for subj, color in subjects.items():
                            fig_trend.add_trace(go.Scatter(
                                x=student_data['시험명'], y=student_data[subj],
                                mode='lines+markers', name=subj.split('_')[0],
                                line=dict(color=color, width=3 if subj=='총점_국수탐' else 1)
                            ))
                        fig_trend.update_layout(hovermode="x unified")
                        st.plotly_chart(fig_trend, use_container_width=True)
                        
                        # 오류 방지를 위한 스타일 적용
                        display_cols = ['시험명', '국어_점수', '수학_점수', '영어_점수', '탐구1_점수', '탐구2_점수', '총점_국수탐', '전체_석차']
                        st_data = student_data[display_cols]
                        try:
                            st.dataframe(st_data.style.background_gradient(subset=['총점_국수탐'], cmap='Blues'))
                        except ImportError:
                            # matplotlib 없을 경우 스타일 없이 출력
                            st.dataframe(st_data)
                    else:
                        st.warning("검색 결과가 없습니다.")

            else: # 반별 평균 추이
                class_trend = main_df.groupby(['시험명', '월_숫자', '반'])['총점_국수탐'].mean().reset_index()
                class_trend = class_trend.sort_values('월_숫자')
                fig_class_trend = px.line(class_trend, x='시험명', y='총점_국수탐', color='반', markers=True)
                st.plotly_chart(fig_class_trend, use_container_width=True)

        # --- [Tab 2] 변동폭 분석 (Who Changed?) - NEW ---
        with tabs[1]:
            st.header("🚨 Who Changed? (성적 급변동 학생 추적)")
            
            if len(exam_list) < 2:
                st.warning("⚠️ 변동폭을 분석하려면 최소 2개 이상의 시험 데이터가 필요합니다.")
            else:
                # 비교할 두 시험 선택
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    exam_base = st.selectbox("기준 시험 (이전)", exam_list, index=len(exam_list)-2)
                with col_c2:
                    exam_curr = st.selectbox("비교 시험 (최근)", exam_list, index=len(exam_list)-1)
                
                if exam_base == exam_curr:
                    st.error("서로 다른 시험을 선택해주세요.")
                else:
                    # 데이터 준비 및 병합
                    df_base = main_df[main_df['시험명'] == exam_base][['학번', '성명', '반', '국어_점수', '수학_점수', '총점_국수탐']]
                    df_curr = main_df[main_df['시험명'] == exam_curr][['학번', '성명', '반', '국어_점수', '수학_점수', '총점_국수탐']]
                    
                    merged = pd.merge(df_curr, df_base, on=['학번', '성명', '반'], suffixes=('_최근', '_이전'))
                    
                    # 변동폭 계산
                    merged['총점_변동'] = merged['총점_국수탐_최근'] - merged['총점_국수탐_이전']
                    merged['국어_변동'] = merged['국어_점수_최근'] - merged['국어_점수_이전']
                    merged['수학_변동'] = merged['수학_점수_최근'] - merged['수학_점수_이전']

                    st.divider()

                    # 1. 슬럼프 경보 (총점 30점 이상 하락)
                    st.subheader("📉 슬럼프 경보 (총점 -30점 이상)")
                    slump_students = merged[merged['총점_변동'] <= -30].sort_values('총점_변동')
                    if not slump_students.empty:
                        st.dataframe(slump_students[['반', '성명', '총점_변동', '국어_변동', '수학_변동', '총점_국수탐_최근']])
                    else:
                        st.info("해당하는 학생이 없습니다. 다행이네요!")

                    st.divider()

                    # 2. 노력상 후보 (총점 상승 Top 5)
                    st.subheader("🏆 노력상 후보 (성적 급상승 Top 5)")
                    rising_students = merged.sort_values('총점_변동', ascending=False).head(5)
                    if not rising_students.empty:
                        # 보기 좋게 컬럼 정리
                        st.table(rising_students[['반', '성명', '총점_변동', '총점_국수탐_이전', '총점_국수탐_최근']])

                    st.divider()

                    # 3. 과목 편식 확인 (수학 상승 & 국어 하락)
                    st.subheader("⚖️ 과목 불균형 (수학⬆️ 국어⬇️)")
                    st.markdown("**조건:** 수학은 5점 이상 올랐는데, 국어는 5점 이상 떨어진 학생")
                    
                    imbalance_students = merged[(merged['수학_변동'] >= 5) & (merged['국어_변동'] <= -5)]
                    
                    if not imbalance_students.empty:
                        fig_imb = px.scatter(
                            imbalance_students, 
                            x='국어_변동', 
                            y='수학_변동', 
                            text='성명',
                            color='반',
                            title="국어 하락 vs 수학 상승 분포",
                            labels={'국어_변동': '국어 점수 변동', '수학_변동': '수학 점수 변동'}
                        )
                        fig_imb.add_hline(y=0, line_dash="dash", line_color="gray")
                        fig_imb.add_vline(x=0, line_dash="dash", line_color="gray")
                        st.plotly_chart(fig_imb, use_container_width=True)
                        st.dataframe(imbalance_students[['반', '성명', '수학_변동', '국어_변동', '총점_변동']])
                    else:
                        st.info("해당 조건의 학생이 없습니다.")

        # --- [Tab 3] 최근 시험 상세 분석 ---
        with tabs[2]:
            last_exam = exam_list[-1]
            st.header(f"📊 {last_exam} 상세 분석")
            latest_df = main_df[main_df['시험명'] == last_exam]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("응시 인원", f"{len(latest_df)}명")
            col2.metric("전체 평균(국수탐)", f"{latest_df['총점_국수탐'].mean():.1f}점")
            col3.metric("수학 1등급 컷(4%)", f"{latest_df['수학_점수'].quantile(0.96):.0f}점")

            fig_scatter = px.scatter(
                latest_df, x='국어_점수', y='수학_점수', color='탐구1_과목',
                size='총점_국수탐', hover_data=['성명', '반'],
                title=f"{last_exam} 국어 vs 수학 점수 분포"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        # --- [Tab 4] 반별 비교 ---
        with tabs[3]:
            st.header("🏫 반별 성적 비교")
            compare_target = st.selectbox("비교 대상 시험", exam_list, index=len(exam_list)-1)
            target_df = main_df[main_df['시험명'] == compare_target]
            
            class_avg = target_df.groupby('반')[['국어_점수', '수학_점수', '영어_점수', '총점_국수탐']].mean().reset_index()
            fig_bar = px.bar(class_avg, x='반', y=['국어_점수', '수학_점수', '영어_점수'], barmode='group', title=f"{compare_target} 반별 평균")
            st.plotly_chart(fig_bar, use_container_width=True)

        # --- [Tab 5] 탐구 분석 ---
        with tabs[4]:
            st.header("🔍 탐구 과목 선택 분석")
            target_exam_tamgu = st.selectbox("분석할 시험", exam_list, index=len(exam_list)-1, key='tamgu_select')
            tamgu_df_target = main_df[main_df['시험명'] == target_exam_tamgu]
            
            t1 = tamgu_df_target[['탐구1_과목', '총점_국수탐']].rename(columns={'탐구1_과목': '탐구과목'})
            t2 = tamgu_df_target[['탐구2_과목', '총점_국수탐']].rename(columns={'탐구2_과목': '탐구과목'})
            tamgu_long = pd.concat([t1, t2]).dropna()
            
            tamgu_stats = tamgu_long.groupby('탐구과목')['총점_국수탐'].agg(['mean', 'count']).sort_values('mean', ascending=False).reset_index()
            
            fig_tamgu = px.bar(tamgu_stats, x='탐구과목', y='mean', color='mean', text='count', title="탐구 과목별 총점 평균")
            st.plotly_chart(fig_tamgu, use_container_width=True)

        # --- [Tab 6] 학생 조회 ---
        with tabs[5]:
            st.header("👤 통합 데이터 다운로드")
            excel_data = convert_df_to_excel(main_df)
            st.download_button("전체 데이터 엑셀 다운로드", excel_data, 'total_grade_analysis.xlsx')

    else:
        st.error("데이터 처리에 실패했습니다.")

else:
    st.info("👈 사이드바에서 분석할 CSV 파일들을 업로드해주세요.")
