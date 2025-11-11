# ✅ 수정된 streamlit 코드 (KeyError 방지 완전 버전)
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os

st.set_page_config(page_title="🎮 게임 장르별 이용자 분석", layout="wide")
st.title("🎮 게임 장르별 이용자 수 및 게임 수 상관관계 분석")

# --- 1️⃣ CSV 자동 로드 ---
csv_path = "steam_games_sample200.csv"

if not os.path.exists(csv_path):
    st.error(f"❌ '{csv_path}' 파일을 찾을 수 없습니다. 같은 폴더에 CSV 파일을 넣어주세요.")
    st.stop()

df = pd.read_csv(csv_path)

st.sidebar.success(f"✅ 데이터 불러오기 성공: {csv_path}")
st.subheader("📊 데이터 미리보기")
st.dataframe(df.head())

# --- 2️⃣ 컬럼 선택 ---
st.sidebar.header("⚙️ 분석 설정")
genre_col = st.sidebar.selectbox("장르(genre) 컬럼 선택", df.columns)
user_col = st.sidebar.selectbox("이용자 수 컬럼 선택", df.columns)

# --- 3️⃣ 데이터 전처리 ---
st.subheader("🧹 데이터 전처리")
df = df[[genre_col, user_col]].dropna()

# 숫자형으로 변환
df[user_col] = pd.to_numeric(df[user_col], errors='coerce')
df = df.dropna(subset=[user_col])

# 장르 문자열 정리
df[genre_col] = df[genre_col].astype(str).apply(lambda x: x.split(",")[0].strip())

st.write(f"전처리 후 데이터 개수: {len(df)}개")
st.dataframe(df.head())

# --- 4️⃣ 장르별 통계 ---
st.subheader("📈 장르별 통계 분석")
genre_stats = df.groupby(genre_col).agg(
    game_count=(genre_col, 'count'),
    avg_players=(user_col, 'mean')
).reset_index()

# 컬럼명 확인 후 자동 감지
genre_name_col = genre_stats.columns[0]  # 첫 번째 컬럼을 장르 컬럼으로 간주
st.write(f"✅ 감지된 장르 컬럼명: **{genre_name_col}**")

# --- 5️⃣ 상관관계 ---
if len(genre_stats) > 1:
    correlation = genre_stats["game_count"].corr(genre_stats["avg_players"])
else:
    correlation = 0.0
st.metric("📊 게임 수와 이용자 수 상관계수", f"{correlation:.3f}")

# --- 6️⃣ 시각화 ---
st.subheader("🎨 시각화 (상호작용형)")

tab1, tab2 = st.tabs(["장르별 요약 그래프", "상관관계 산점도"])

with tab1:
    st.write("장르별 게임 수 및 평균 이용자 수")
    fig_bar = px.bar(
        genre_stats,
        x=genre_stats[genre_name_col].astype(str),
        y="game_count",
        text="game_count",
        hover_data={"avg_players": True},
        color="avg_players",
        color_continuous_scale="viridis",
        title="장르별 게임 수 및 평균 이용자 수"
    )
    fig_bar.update_layout(xaxis_title="장르", yaxis_title="게임 수")
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.write("게임 수와 평균 이용자 수의 상관관계")
    fig_scatter = px.scatter(
        genre_stats,
        x="game_count",
        y="avg_players",
        size="avg_players",
        color=genre_name_col,
        hover_name=genre_name_col,
        hover_data={"game_count": True, "avg_players": True},
        title="장르별 게임 수 vs 이용자 수"
    )
    fig_scatter.update_layout(xaxis_title="게임 수", yaxis_title="평균 이용자 수")
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- 7️⃣ 결과 다운로드 ---
st.subheader("💾 분석 결과 다운로드")
csv_buffer = BytesIO()
genre_stats.to_csv(csv_buffer, index=False)
st.download_button(
    label="📥 결과 CSV 다운로드",
    data=csv_buffer.getvalue(),
    file_name="genre_analysis_result.csv",
    mime="text/csv"
)
