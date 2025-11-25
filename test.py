import streamlit as st
import pandas as pd
import plotly.express as px
import os
import ast

st.set_page_config(page_title="🎮 Steam 게임 분석", layout="wide")
st.title("🎮 Steam 게임 데이터 분석 대시보드")

# -----------------------------
# 1) CSV 로드
# -----------------------------
csv_path = "steam_games_sample200.csv"

if not os.path.exists(csv_path):
    st.error(f"❌ CSV 파일 '{csv_path}'이(가) 없습니다. 같은 폴더에 넣어주세요.")
    st.stop()

df = pd.read_csv(csv_path)
df = df.loc[:, ~df.columns.duplicated()]  # 중복 컬럼 제거

st.subheader("📌 데이터 미리보기")
st.dataframe(df.head())

# -----------------------------
# 2) 컬럼 자동 감지
# -----------------------------
string_cols = df.select_dtypes(include=['object']).columns.tolist()
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

# 장르/평균 이용자 수 컬럼 자동 선택
genre_col = string_cols[0] if string_cols else df.columns[0]
player_col = numeric_cols[0] if numeric_cols else df.columns[0]

# -----------------------------
# 3) X/Y축 선택 (사이드바)
# -----------------------------
st.sidebar.header("⚙️ X/Y축 시각화 옵션")

# X축 후보: 문자열 + 숫자
x_candidates = string_cols + numeric_cols
x_col = st.sidebar.selectbox("📌 X축 컬럼 선택", x_candidates)

# Y축 후보: 숫자형만
y_candidates = numeric_cols
y_col = st.sidebar.selectbox("📌 Y축 컬럼 선택 (숫자형만)", y_candidates)

# -----------------------------
# 4) 문자열 안전 처리
# -----------------------------
def extract_first(value):
    if pd.isna(value):
        return "Unknown"
    if isinstance(value, list):
        return str(value[0]).strip()
    if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list) and len(parsed) > 0:
                return str(parsed[0]).strip()
        except:
            pass
    if isinstance(value, str):
        return value.split(",")[0].strip()
    return str(value)

if x_col in string_cols:
    df[x_col] = df[x_col].apply(extract_first)

# -----------------------------
# 5) Y축 숫자형 전처리
# -----------------------------
df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
df[player_col] = pd.to_numeric(df[player_col], errors='coerce')
df = df.dropna(subset=[y_col, player_col])

st.write(f"전처리 완료 데이터 개수: {len(df)}")

# -----------------------------
# 6) X/Y축 기반 시각화
# -----------------------------
st.header("📊 선택 기반 시각화")

# X축 문자열 → 막대그래프
if x_col in string_cols:
    st.subheader("📌 범주형 X축 → 막대그래프")
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=f"{x_col} 별 {y_col}",
        text=y_col
    )
    st.plotly_chart(fig, use_container_width=True)
# X축 숫자 → 산점도
else:
    st.subheader("📌 숫자형 X·Y축 → 산점도")
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        trendline="ols",
        title=f"{x_col} vs {y_col}"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 7) 장르별 평균 이용자 수
# -----------------------------
st.header("📌 장르별 평균 이용자 수")
df["main_genre"] = df[genre_col].apply(extract_first)
genre_stats = df.groupby("main_genre")[player_col].mean().reset_index()
fig_genre = px.bar(
    genre_stats,
    x="main_genre",
    y=player_col,
    color=player_col,
    title="장르별 평균 이용자 수"
)
st.plotly_chart(fig_genre, use_container_width=True)

