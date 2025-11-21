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
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
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
    """파일명에서 'N월' 또는 파일명 자체를 추출하여 시험 구분자로 사용"""
    match = re.search(r'(\d+)월', filename)
    if match:
        return f"{match.group(1)}월"
    return filename.split('.')[0] # 'N월'이 없으면 파일명 사용

def load_single_file(file):
    """단일 파일 전처리 함수"""
    try:
        df = pd.read_csv(file, header=[1, 2], encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(file, header=[1, 2], encoding='utf-8')
    except Exception as e:
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
    
    # 컬럼 수 맞추기
    current_cols = len(df.columns)
    if current_cols >= len(new_columns):
        df.columns = new_columns + [f"col_{i}" for i in range(current_cols - len(new_columns))]
    else:
        df.columns = new_columns[:current_cols]

    # 숫자 변환
    numeric_cols = ['국어_점수', '수학_점수', '영어_점수', '탐구1_점수', '탐구2_점수', '총점_국수탐', '전체_석차']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 학번, 반 추출
    if '학번' in df.columns:
        df['학번'] = df['학번'].fillna(0).astype(int).astype(str)
        df['반'] = df['학번'].apply(lambda x: x[1:3] if len(x) == 5 else '기타')
    
    # 시험명 추가 (파일명 기반)
    exam_name = extract_exam_name(file.name)
    df['시험명'] = exam_name
    
    # 시험 순서 정렬을 위한 월 숫자 추출
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
    # 월별로 정렬 (3월 -> 6월 -> 9월)
    final_df = final_df.sort_values(by=['월_숫자', '반', '학번'])
    return final_df

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- 메인 로직 ---

if uploaded_files:
    # 1. 데이터 통합 로드
    main_df = process_all_files(uploaded_files)

    if main_df is not None:
        # 업로드된 시험 목록 확인
        exam_list = sorted(main_df['시험명'].unique(), key=lambda x: int(re.search(r'(\d+)', x).group(1)) if re.search(r'(\d+)', x) else 99)
        last_exam = exam_list[-1] # 가장 최근 시험
        
        st.success(f"✅ 총 {len(uploaded_files)}개의 파일이 통합되었습니다: {', '.join(exam_list)}")

        # 탭 구성
        tabs = st.tabs([
            "📈 성적 변화 추이(Trend)",
            "📊 최근 시험 분석", 
            "🏫 반별 비교", 
            "🔍 탐구 분석", 
            "👤 학생 개별 조회"
        ])

        # --- [Tab 1] 성적 변화 추이 (핵심 기능) ---
        with tabs[0]:
            st.header("📉 학생별/학급별 성적 변화 추적")
            
            # 모드 선택: 학생별 vs 반별
            trend_mode = st.radio("분석 모드 선택", ["학생 개인별 추이", "반별 평균 추이"], horizontal=True)

            if trend_mode == "학생 개인별 추이":
                col_search, _ = st.columns([1, 2])
                with col_search:
                    search_name = st.text_input("학생 이름 검색", placeholder="예: 정선재")
                
                if search_name:
                    student_data = main_df[main_df['성명'].str.contains(search_name)].sort_values('월_숫자')
                    
                    if len(student_data) > 0:
                        # 학생 정보 표시 (가장 최근 데이터 기준)
                        recent_info = student_data.iloc[-1]
                        st.subheader(f"🧑‍🎓 {recent_info['성명']} ({recent_info['반']}반) 학생의 성적 변화")
                        
                        # 라인 차트 그리기
                        fig_trend = go.Figure()
                        
                        # 주요 과목 추가
                        subjects = {'국어_점수': 'red', '수학_점수': 'blue', '영어_점수': 'green', '총점_국수탐': 'black'}
                        for subj, color in subjects.items():
                            fig_trend.add_trace(go.Scatter(
                                x=student_data['시험명'], 
                                y=student_data[subj],
                                mode='lines+markers',
                                name=subj.split('_')[0],
                                line=dict(color=color, width=3 if subj=='총점_국수탐' else 1)
                            ))
                        
                        fig_trend.update_layout(
                            title="시험별 주요 과목 원점수 변화",
                            xaxis_title="시험",
                            yaxis_title="점수",
                            hovermode="x unified"
                        )
                        st.plotly_chart(fig_trend, use_container_width=True)
                        
                        # 데이터 테이블
                        st.write("📋 상세 점수표")
                        display_cols = ['시험명', '국어_점수', '수학_점수', '영어_점수', '탐구1_점수', '탐구2_점수', '총점_국수탐', '전체_석차']
                        st.dataframe(student_data[display_cols].style.background_gradient(subset=['총점_국수탐'], cmap='Blues'))
                        
                    else:
                        st.warning("검색 결과가 없습니다.")
                else:
                    st.info("이름을 입력하면 해당 학생의 월별 성적 그래프가 나타납니다.")

            else: # 반별 평균 추이
                class_trend = main_df.groupby(['시험명', '월_숫자', '반'])['총점_국수탐'].mean().reset_index()
                class_trend = class_trend.sort_values('월_숫자')
                
                fig_class_trend = px.line(
                    class_trend, 
                    x='시험명', 
                    y='총점_국수탐', 
                    color='반',
                    markers=True,
                    title="반별 국수탐 총점 평균 변화 추이"
                )
                st.plotly_chart(fig_class_trend, use_container_width=True)

        # --- [Tab 2] 최근 시험 분석 ---
        with tabs[1]:
            st.header(f"📊 {last_exam} 상세 분석 (최신)")
            
            # 가장 최근 시험 데이터만 필터링
            latest_df = main_df[main_df['시험명'] == last_exam]
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("응시 인원", f"{len(latest_df)}명")
            col2.metric("전체 평균(국수탐)", f"{latest_df['총점_국수탐'].mean():.1f}점")
            col3.metric("수학 1등급 컷(4%)", f"{latest_df['수학_점수'].quantile(0.96):.0f}점")
            col4.metric("영어 1등급 비율", f"{(latest_df[latest_df['영어_점수'] >= 90].shape[0] / len(latest_df) * 100):.1f}%")

            # 상관관계 산점도
            fig_scatter = px.scatter(
                latest_df, x='국어_점수', y='수학_점수', color='탐구1_과목',
                size='총점_국수탐', hover_data=['성명', '반'],
                title=f"{last_exam} 국어 vs 수학 점수 분포"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        # --- [Tab 3] 반별 비교 ---
        with tabs[2]:
            st.header("🏫 반별 성적 비교")
            # 전체 데이터 or 최근 데이터 선택 가능하게
            compare_target = st.selectbox("비교 대상 시험", exam_list, index=len(exam_list)-1)
            target_df = main_df[main_df['시험명'] == compare_target]
            
            class_avg = target_df.groupby('반')[['국어_점수', '수학_점수', '영어_점수', '총점_국수탐']].mean().reset_index()
            
            fig_bar = px.bar(
                class_avg, x='반', y=['국어_점수', '수학_점수', '영어_점수'],
                barmode='group', title=f"{compare_target} 반별 평균 비교"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # --- [Tab 4] 탐구 분석 ---
        with tabs[3]:
            st.header("🔍 탐구 과목 선택 및 유불리")
            target_exam_tamgu = st.selectbox("분석할 시험 선택", exam_list, index=len(exam_list)-1, key='tamgu_exam')
            tamgu_df_target = main_df[main_df['시험명'] == target_exam_tamgu]
            
            # 탐구 데이터 전처리 (Long format)
            t1 = tamgu_df_target[['탐구1_과목', '총점_국수탐']].rename(columns={'탐구1_과목': '탐구과목'})
            t2 = tamgu_df_target[['탐구2_과목', '총점_국수탐']].rename(columns={'탐구2_과목': '탐구과목'})
            tamgu_long = pd.concat([t1, t2]).dropna()
            
            tamgu_stats = tamgu_long.groupby('탐구과목')['총점_국수탐'].agg(['mean', 'count']).sort_values('mean', ascending=False).reset_index()

            fig_tamgu = px.bar(
                tamgu_stats, x='탐구과목', y='mean', color='mean',
                text='count',
                title=f"{target_exam_tamgu} 탐구 과목별 응시자 총점 평균 (막대 위 숫자: 응시자 수)",
                labels={'mean': '국수탐 총점 평균', 'count': '응시자 수'}
            )
            st.plotly_chart(fig_tamgu, use_container_width=True)

        # --- [Tab 5] 학생 조회 및 다운로드 ---
        with tabs[4]:
            st.header("👤 학생 통합 조회 및 데이터 다운로드")
            
            # 엑셀 다운로드
            st.markdown("### 📥 전체 데이터 다운로드")
            excel_data = convert_df_to_excel(main_df)
            st.download_button(
                label="전체 통합 데이터 엑셀 다운로드",
                data=excel_data,
                file_name='total_grade_analysis.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    else:
        st.error("데이터 처리에 실패했습니다. 파일 형식을 확인해주세요.")

else:
    st.info("👈 사이드바에서 분석할 CSV 파일들을 업로드해주세요. (여러 개 선택 가능)")
