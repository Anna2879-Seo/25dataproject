import streamlit as st
import pandas as pd
import plotly.express as px
import koreanize_matplotlib

st.set_page_config(page_title="🧑‍🦲 외국인 비율 대시보드", layout="wide")

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("202505_202505_연령별인구현황_월간.csv", encoding="cp949")
    df["지역"] = df["행정구역"].str.split("(").str[0].str.strip()

    # 🔍 외국인/내국인/총 인구 관련 컬럼 자동 탐색
    foreign_col = next((col for col in df.columns if "외국인" in col and "계" in col), None)
    native_col = next((col for col in df.columns if "내국인" in col and "계" in col), None)
    total_col = next((col for col in df.columns if "총인구" in col or "총 계" in col or "계" == col.strip()), None)

    if not all([foreign_col, native_col, total_col]):
        st.error("❌ '외국인', '내국인', '총인구' 관련 컬럼을 찾을 수 없습니다. 파일 컬럼명을 확인해주세요.")
        st.write("컬럼 목록:", df.columns.tolist())
        st.stop()

    # 콤마 제거 후 정수형 변환
    for col in [foreign_col, native_col, total_col]:
        df[col] = df[col].astype(str).str.replace(",", "", regex=False).astype(int)

    # 외국인 비율 계산
    df["외국인비율"] = df[foreign_col] / df[total_col]

    return df, foreign_col, total_col

# ---------- UI ----------
st.title("🌍 외국인 비율이 가장 높은 지역")

df, foreign_col, total_col = load_data()

# 데이터 정리
top_df = df[["지역", total_col, foreign_col, "외국인비율"]].drop_duplicates(subset="지역").copy()
top_df["외국인비율(%)"] = (top_df["외국인비율"] * 100).round(2)
top_df = top_df.sort_values(by="외국인비율", ascending=False)

# ---------- 결과 출력 ----------
st.subheader("🏆 외국인 비율 TOP 지역")
st.dataframe(top_df.head(10), use_container_width=True)

# ---------- 시각화 ----------
fig = px.bar(
    top_df.head(10),
    x="지역",
    y="외국인비율(%)",
    title="외국인 비율이 높은 TOP 10 지역",
    labels={"외국인비율(%)": "외국인 비율 (%)"},
    color="지역"
)
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.caption("📊 데이터 출처: 행정안전부 주민등록 인구 통계")
