import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="연도별 트렌드 분석 리포트", layout="wide")
st.title("📅 연도별 핵심 트렌드 분석 대시보드")

def load_data(file_name, skiprows=2):
    try:
        return pd.read_csv(file_name, skiprows=skiprows)
    except:
        return None

try:
    # 1. 시계열 데이터 전처리
    df_time = load_data("multiTimeline (1).csv")
    if df_time is not None:
        df_time.columns = ['날짜', '관심도']
        df_time['날짜'] = pd.to_datetime(df_time['날짜'])
        
        # [핵심] 연도(Year) 정보 추출
        df_time['연도'] = df_time['날짜'].dt.year
        
        # --- 발표 섹션 1: 연도별 평균 관심도 비교 ---
        st.header("1. 연도별 평균 검색 관심도")
        # 연도별로 그룹화하여 평균 계산
        df_yearly = df_time.groupby('연도')['관심도'].mean().reset_index()
        
        fig_yearly = px.bar(df_yearly, x='연도', y='관심도', 
                            title="연도별 평균 관심도 비교 (누적 데이터)",
                            text_auto='.1f', # 막대 위에 소수점 1자리까지 표시
                            color='관심도', color_continuous_scale='Reds')
        
        fig_yearly.update_layout(xaxis_tickmode='linear') # 모든 연도가 보이게 설정
        st.plotly_chart(fig_yearly, use_container_width=True)

        # --- 발표 섹션 2: 특정 연도 상세 분석 ---
        st.divider()
        st.header("2. 연도별 상세 추이 확인")
        
        # 사용자가 연도를 선택하면 해당 연도 그래프만 출력
        years = sorted(df_time['연도'].unique(), reverse=True)
        selected_year = st.select_slider("확인하고 싶은 연도를 선택하세요:", options=years)
        
        df_selected = df_time[df_time['연도'] == selected_year]
        
        col1, col2 = st.columns([3, 1])
        with col1:
            fig_detail = px.line(df_selected, x='날짜', y='관심도', 
                                 title=f"{selected_year}년 상세 관심도 변화",
                                 markers=True, text='관심도')
            fig_detail.update_traces(textposition="top center")
            st.plotly_chart(fig_detail, use_container_width=True)
            
        with col2:
            st.info(f"📊 {selected_year}년 요약")
            year_max = df_selected['관심도'].max()
            year_avg = df_selected['관심도'].mean()
            st.metric("최고 관심도", f"{year_max}점")
            st.metric("평균 관심도", f"{year_avg:.1f}점")

    # 3. 관련 주제/검색어 막대그래프 (기존 유지)
    st.divider()
    st.header("3. 관련 주제 영향력 (전체 기간)")
    df_ent = load_data("relatedEntities (2).csv")
    if df_ent is not None:
        if 'RISING' in df_ent.iloc[:, 0].values:
            rising_idx = df_ent[df_ent.iloc[:, 0] == 'RISING'].index[0]
            df_top_ent = df_ent.iloc[:rising_idx-1].copy()
        else:
            df_top_ent = df_ent.copy()
            
        df_top_ent.columns = ['주제', '점수']
        df_top_ent['점수'] = pd.to_numeric(df_top_ent['점수'].replace('<1', '0.5'), errors='coerce')
        df_top_ent = df_top_ent.dropna().sort_values(by='점수', ascending=False).head(10)

        fig_bar = px.bar(df_top_ent, x='점수', y='주제', orientation='h',
                         color='점수', color_continuous_scale='Blues',
                         text_auto=True)
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

except Exception as e:
    st.error(f"데이터 로드 및 분석 중 오류 발생: {e}")

