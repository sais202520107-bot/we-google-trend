import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="구글 트렌드 인터랙티브 리포트", layout="wide")
st.title("📊 키워드 분석 및 실시간 관심도 체크")

# --- 데이터 로드 함수 (오류 방지용) ---
def load_data(file_name, skiprows=2):
    try:
        return pd.read_csv(file_name, skiprows=skiprows)
    except:
        return None

try:
    # 1. 데이터 전처리
    df_time = load_data("multiTimeline (1).csv")
    if df_time is not None:
        df_time.columns = ['날짜', '관심도']
        df_time['날짜'] = pd.to_datetime(df_time['날짜'])
        
        # 2. 선 그래프 (클릭 및 호버 기능)
        st.header("1. 시계열 트렌드 (그래프에 마우스를 올리세요)")
        st.info("💡 그래프의 선 위에 마우스를 올리면 해당 시점의 정확한 관심도 수치가 나타납니다.")
        
        fig_line = px.line(df_time, x='날짜', y='관심도', 
                           title="날짜별 검색 관심도 추이",
                           markers=True, # 지점마다 점 표시
                           hover_data={'날짜': "|%Y년 %m월", '관심도': True})
        
        fig_line.update_traces(line_color='#1f77b4', line_width=2)
        fig_line.update_layout(hovermode="x unified") # 마우스 위치의 모든 데이터 통합 표시
        st.plotly_chart(fig_line, use_container_width=True)

    # 3. 막대 그래프 (강화된 로직)
    st.divider()
    st.header("2. 관련 주제별 영향력 비교 (막대그래프)")
    
    df_ent = load_data("relatedEntities (2).csv")
    if df_ent is not None:
        # RISING 키워드가 있으면 자르고, 없으면 전체 사용
        if 'RISING' in df_ent.iloc[:, 0].values:
            rising_idx = df_ent[df_ent.iloc[:, 0] == 'RISING'].index[0]
            df_top_ent = df_ent.iloc[:rising_idx-1].copy()
        else:
            df_top_ent = df_ent.copy()
            
        df_top_ent.columns = ['주제', '점수']
        df_top_ent['점수'] = pd.to_numeric(df_top_ent['점수'].replace('<1', '0.5'), errors='coerce')
        df_top_ent = df_top_ent.dropna().sort_values(by='점수', ascending=False).head(10)

        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 막대그래프 출력
            fig_bar = px.bar(df_top_ent, x='점수', y='주제', orientation='h',
                             color='점수', color_continuous_scale='Blues',
                             text_auto=True, title="인기 주제 TOP 10")
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            st.subheader("🎯 키워드별 상세 수치")
            # 사용자가 키워드를 선택하면 점수를 보여주는 기능
            selected_item = st.selectbox("상세 확인을 원하는 주제를 선택하세요:", df_top_ent['주제'].tolist())
            if selected_item:
                score = df_top_ent[df_top_ent['주제'] == selected_item]['점수'].values[0]
                st.metric(label=f"'{selected_item}'의 관심도 점수", value=f"{score}점")
                st.write(f"현재 분석된 데이터 중 **{selected_item}**은(는) 상위권에 위치해 있습니다.")

except Exception as e:
    st.error(f"데이터 로드 중 문제가 발생했습니다: {e}")
    st.info("CSV 파일 형식이 구글 트렌드 정규 형식인지 확인해주세요.")

