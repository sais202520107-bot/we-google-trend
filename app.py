import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="구글 트렌드 분석 대시보드", layout="wide")
st.title("📊 구글 트렌드 키워드 분석")

# 1. 시계열 데이터 분석 (multiTimeline)
st.header("1. 시간별 검색 관심도 추이")
try:
    # 상단 2줄(메타데이터) 제외하고 읽기
    df_time = pd.read_csv("multiTimeline (1).csv", skiprows=2)
    st.header(df_time.head())
    st.header(df_time.info())
    df_time.columns = ['월', '관심도']
    df_time['월'] = pd.to_datetime(df_time['월'])
    
    fig_time = px.line(df_time, x='월', y='관심도', title="연도별 검색량 변화")
    st.plotly_chart(fig_time, use_container_width=True)
except:
    st.warning("multiTimeline 파일을 확인해주세요.")

col1, col2 = st.columns(2)

# 2. 관련 주제 분석 (relatedEntities)
with col1:
    st.header("2. 관련 주제 (Entities)")
    try:
        df_entities = pd.read_csv("relatedEntities (2).csv", skiprows=2)
        # TOP 섹션 데이터만 추출 (RISING 전까지)
        top_entities = df_entities.iloc[:df_entities[df_entities.iloc[:,0] == 'RISING'].index[0]-1]
        top_entities.columns = ['주제', '점수']
        # <1 표시를 0.5로 변환하여 수치화
        top_entities['점수'] = top_entities['점수'].replace('<1', '0.5').astype(float)
        
        fig_entities = px.bar(top_entities.head(10), x='점수', y='주제', orientation='h', title="인기 관련 주제 TOP 10")
        st.plotly_chart(fig_entities)
    except:
        st.write("관련 주제 데이터를 불러올 수 없습니다.")

# 3. 관련 검색어 분석 (relatedQueries)
with col2:
    st.header("3. 관련 검색어 (Queries)")
    try:
        df_queries = pd.read_csv("relatedQueries (1).csv", skiprows=2)
        top_queries = df_queries.iloc[:df_queries[df_queries.iloc[:,0] == 'RISING'].index[0]-1]
        top_queries.columns = ['검색어', '점수']
        top_queries['점수'] = pd.to_numeric(top_queries['점수'])
        
        st.dataframe(top_queries, use_container_width=True)
    except:

        st.write("관련 검색어 데이터를 불러올 수 없습니다.")


