import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler # 정규화 도구

st.set_page_config(page_title="구글 트렌드 분석 대시보드", layout="wide")
st.title("📊 구글 트렌드 정밀 분석 (정규화 포함)")

# 1. 시계열 데이터 분석 (multiTimeline)
st.header("1. 시간별 검색 관심도 추이")
try:
    df_time = pd.read_csv("multiTimeline (1).csv", skiprows=2)
    # 컬럼명 강제 지정
    df_time.columns = ['월', '관심도']
    df_time['월'] = pd.to_datetime(df_time['월'])
    
    # [정규화 로직 추가]
    scaler = MinMaxScaler()
    df_time['정규화_관심도'] = scaler.fit_transform(df_time[['관심도']])
    
    # 시각화 선택 (원본 vs 정규화)
    view_mode = st.radio("데이터 선택:", ["원본 (0-100)", "정규화 (0-1)"])
    y_col = '관심도' if view_mode == "원본 (0-100)" else '정규화_관심도'
    
    fig_time = px.line(df_time, x='월', y=y_col, title=f"연도별 트렌드 변화 ({view_mode})")
    st.plotly_chart(fig_time, use_container_width=True)
except Exception as e:
    st.warning(f"시계열 파일 오류: {e}")

col1, col2 = st.columns(2)

# 2. 관련 주제 분석 (정규화 포함)
with col1:
    st.header("2. 관련 주제 (Entities)")
    try:
        df_entities = pd.read_csv("relatedEntities (2).csv", skiprows=2)
        top_entities = df_entities.iloc[:df_entities[df_entities.iloc[:,0] == 'RISING'].index[0]-1].copy()
        top_entities.columns = ['주제', '점수']
        top_entities['점수'] = top_entities['점수'].replace('<1', '0.5').astype(float)
        
        # [정규화] 점수를 0~1 사이로 변환
        top_entities['정규화_점수'] = scaler.fit_transform(top_entities[['점수']])
        
        fig_entities = px.bar(top_entities.head(10), x='정규화_점수', y='주제', orientation='h', title="주제별 정규화 관심도")
        st.plotly_chart(fig_entities)
    except:
        st.write("관련 주제 로딩 실패")

# 3. 관련 검색어 분석
with col2:
    st.header("3. 관련 검색어 (Queries)")
    try:
        df_queries = pd.read_csv("relatedQueries (1).csv", skiprows=2)
        top_queries = df_queries.iloc[:df_queries[df_queries.iloc[:,0] == 'RISING'].index[0]-1].copy()
        top_queries.columns = ['검색어', '점수']
        top_queries['점수'] = pd.to_numeric(top_queries['점수'])
        
        # 데이터프레임 출력
        st.dataframe(top_queries, use_container_width=True)
    except:
        st.write("관련 검색어 로딩 실패")
