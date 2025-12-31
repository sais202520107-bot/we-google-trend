import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="구글 트렌드 발표 대시보드", layout="wide")

# 1. 데이터 로드 및 전처리
try:
    # 시계열 데이터
    df_time = pd.read_csv("multiTimeline (1).csv", skiprows=2)
    df_time.columns = ['날짜', '관심도']
    df_time['날짜'] = pd.to_datetime(df_time['날짜'])
    
    # 정규화
    scaler = MinMaxScaler()
    df_time['정규화지수'] = scaler.fit_transform(df_time[['관심도']])

    # --- [발표 섹션 1: 선 그래프와 Peak] ---
    st.title("📊 트렌드 분석 리포트")
    st.header("1. 시간별 관심도 변화 및 최고점")
    
    peak_row = df_time.loc[df_time['관심도'].idxmax()]
    
    fig_line = px.line(df_time, x='날짜', y='관심도', title="검색 관심도 추이")
    fig_line.add_annotation(x=peak_row['날짜'], y=peak_row['관심도'],
                            text="최고 관심 시점", showarrow=True, arrowhead=1)
    st.plotly_chart(fig_line, use_container_width=True)

    # --- [발표 섹션 2: 한눈에 보는 막대그래프 비교] ---
    st.divider()
    st.header("2. 데이터 한눈에 비교 (요약 분석)")
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📌 항목별 인기도 비교 (막대)")
        # 관련 주제 데이터를 가져와서 점수순으로 정렬
        df_ent = pd.read_csv("relatedEntities (2).csv", skiprows=2)
        rising_idx = df_ent[df_ent.iloc[:, 0] == 'RISING'].index[0]
        df_top_ent = df_ent.iloc[:rising_idx-1].copy()
        df_top_ent.columns = ['주제', '점수']
        df_top_ent['점수'] = df_top_ent['점수'].replace('<1', '0.5').astype(float)
        
        # 상위 10개 추출 및 시각화
        df_top10 = df_top_ent.sort_values(by='점수', ascending=False).head(10)
        
        fig_bar = px.bar(df_top10, x='점수', y='주제', orientation='h',
                         title="상위 10개 관련 주제 영향력",
                         color='점수', color_continuous_scale='Viridis')
        # 막대 위에 숫자 표시
        fig_bar.update_traces(texttemplate='%{x}', textposition='outside')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("📝 분석 인사이트")
        st.write(f"**최고점 날짜:** {peak_row['날짜'].strftime('%Y년 %m월')}")
        st.write(f"**평균 관심도:** {df_time['관심도'].mean():.1f}")
        st.success(f"""
        - 현재 가장 영향력 있는 주제는 **'{df_top10.iloc[0]['주제']}'**입니다.
        - 점수 **{df_top10.iloc[0]['점수']}**로 압도적인 1위를 차지하고 있습니다.
