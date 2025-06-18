import streamlit as st
import pandas as pd
import plotly.express as px
import koreanize_matplotlib  # 한글 깨짐 방지

st.set_page_config(page_title="🧑‍🦲 외국인 비율 대시보드", layout="wide")

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("202505_202505_연령별인구현황_월간.csv", encoding="cp949")
    df["지역"] = df["행정구역"].str.split("(").str[0].str.strip()
    
    # 숫자형 변환 (콤마 제거)
    for col in ["총인구수", "내국인수", "외국인수"]:
        df[col] = df[col].astype(str).str.replace(",", "", regex=False).astype(int)
    
    # 외국인 비율 계산
    df["외국인비율"] = df["외국인수"] / df["총인구수"]
    
    return df

# ---------- UI ----------
st.title("🌍 외국인 비율이 가장 높은 지역")

df = load_data()

# 외국인 비율 순으로 정렬
top_df = df[["지역", "총인구수", "외국인수", "외국인비율"]].copy()
top_df = top_df.drop_duplicates(subset="지역")  # 중복 제거
top_df = top_df.sort_values(by="외국인비율", ascending=False)
top_df["외국인비율(%)"] = (top_df["외국인비율"] * 100).round(2)

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
