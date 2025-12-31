import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="구글 트렌드 분석 리포트", layout="wide")
st.title("📊 키워드 트렌드 및 영향력 분석")

try:
    # 1. 시계열 데이터 불러오기 및 전처리
    df_time = pd.read_csv("multiTimeline (1).csv", skiprows=2)
    df_time.columns = ['날짜', '관심도']
    df_time['날짜'] = pd.to_datetime(df_time['날짜'])
    
    # 2. 관련 주제 데이터 불러오기 및 전처리
    df_ent = pd.read_csv("relatedEntities (2).csv", skiprows=2)
    rising_idx = df_ent[df_ent.iloc[:, 0] == 'RISING'].index[0]
    df_top_ent = df_ent.iloc[:rising_idx-1].copy()
    df_top_ent.columns = ['주제', '점수']
    df_top_ent['점수'] = df_top_ent['점수'].replace('<1', '0.5').astype(float)
    df_top10 = df_top_ent.sort_values(by='점수', ascending=False).head(10)

    # --- 발표 섹션 1: 선 그래프 ---
    st.header("1. 시간별 관심도 변화 및 Peak 지점")
    peak_row = df_time.loc[df_time['관심도'].idxmax()]
    
    fig_line = px.line(df_time, x='날짜', y='관심도', title="검색 관심도 추이 (0-100)")
    fig_line.add_annotation(x=peak_row['날짜'], y=peak_row['관심도'],
                            text=f"최고점: {peak_row['날짜'].strftime('%Y-%m')}", 
                            showarrow=True, arrowhead=1, bgcolor="yellow")
    st.plotly_chart(fig_line, use_container_width=True)

    # --- 발표 섹션 2: 막대 그래프와 인사이트 ---
    st.divider()
    st.header("2. 한눈에 보는 데이터 비교")
    
    col1, col2 = st.columns([2, 1]) # 막대그래프를 조금 더 크게 배분

    with col1:
        fig_bar = px.bar(df_top10, x='점수', y='주제', orientation='h',
                         title="상위 10개 관련 주제 순위",
                         color='점수', color_continuous_scale='Blues')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.info("💡 실시간 분석 결과")
        st.write(f"**최고 관심 시점:** {peak_row['날짜'].strftime('%Y년 %m월')}")
        st.write(f"**평균 관심 지수:** {df_time['관심도'].mean():.1f}")
        
        status_msg = f"""
        * 1위 주제: **{df_top10.iloc[0]['주제']}**
        * 영향력 점수: **{df_top10.iloc[0]['점수']}**
        * 현재 시장 강도: **{(df_time['관심도'].iloc[-1]/peak_row['관심도']*100):.1f}%**
        """
        st.success(status_msg)

except Exception as e:
    st.error(f"데이터 로드 중 오류가 발생했습니다. 파일 이름을 확인해주세요: {e}")
