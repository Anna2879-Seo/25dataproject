import streamlit as st
import pandas as pd
import plotly.express as px
import koreanize_matplotlib

st.set_page_config(page_title="🗺️ 지역별 인구 구조 대시보드", layout="wide")

@st.cache_data
def load_data() -> tuple[pd.DataFrame, list, list]:
    df = pd.read_csv("202505_202505_연령별인구현황_월간.csv", encoding="cp949")
    df["지역"] = df["행정구역"].str.split("(").str[0].str.strip()
    age_cols = [col for col in df.columns if "_계_" in col and col.endswith("세")]
    age_labels = [col.split("_")[-1] for col in age_cols]
    for col in age_cols:
        df[col] = df[col].astype(str).str.replace(",", "", regex=False).astype(int)
    return df, age_cols, age_labels

# ---------- UI ----------
st.title("🏆 연령별 인구 비율이 가장 높은 지역 찾기")
df, age_cols, age_labels = load_data()

# 지역별 전체 인구 합계 계산
df["전체인구"] = df[age_cols].sum(axis=1)

# 연령별 비율 계산
for col in age_cols:
    df[f"{col}_비율"] = df[col] / df["전체인구"]

# 비율 컬럼 리스트 생성
rate_cols = [f"{col}_비율" for col in age_cols]

# 각 연령별로 비율이 가장 높은 지역 찾기
result = []
for age, col in zip(age_labels, rate_cols):
    max_row = df.loc[df[col].idxmax()]
    result.append({
        "연령": age,
        "최고 비율 지역": max_row["지역"],
        "비율 (%)": round(max_row[col] * 100, 2)
    })

result_df = pd.DataFrame(result)

# ---------- 결과 출력 ----------
st.subheader("👑 연령별 인구 비율이 가장 높은 지역")
st.dataframe(result_df, use_container_width=True)

# ---------- 시각화 ----------
fig = px.bar(
    result_df,
    x="연령",
    y="비율 (%)",
    color="최고 비율 지역",
    title="연령별 최고 인구 비율 지역",
    labels={"비율 (%)": "인구 비율 (%)"}
)
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.caption("📊 데이터 출처: 행정안전부 주민등록 인구 통계")
