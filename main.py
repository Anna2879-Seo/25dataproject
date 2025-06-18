import streamlit as st
import pandas as pd
import plotly.express as px
import koreanize_matplotlib  # 한글 깨짐 방지

st.set_page_config(page_title="🗺️ 지역별 인구 구조 대시보드", layout="wide")

@st.cache_data
def load_data() -> tuple[pd.DataFrame, list]:
    """
    CSV를 읽고 필요한 컬럼만 정리해서 리턴
    """
    df = pd.read_csv("202505_202505_연령별인구현황_월간.csv", encoding="cp949")
    df["지역"] = df["행정구역"].str.split("(").str[0].str.strip()

    age_cols = [c for c in df.columns if c.endswith("세") and "_계_" in c]

    for col in age_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .astype(int)
        )

    return df, age_cols


# ---------- 🌐 UI ----------
st.title("🔍 지역별 인구 구조 대시보드")
df, age_cols = load_data()

regions = sorted(df["지역"].unique())
selected = st.sidebar.multiselect("✅ 분석할 지역(복수 선택 가능)", regions, default=["서울특별시"])

if not selected:
    st.info("왼쪽 사이드바에서 최소 1개 지역을 선택하세요!")
    st.stop()

chart_type = st.sidebar.selectbox("차트 유형", ("꺾은선 그래프", "막대 그래프 (Population Pyramid용)"))

# ---------- 📊 데이터 가공 ----------
subset = df[df["지역"].isin(selected)]
agg = subset.groupby("지역")[age_cols].sum().T

# 인덱스: '2024년_계_0세' → 숫자만 추출
ages = agg.index.str.extract(r"(\d+)").astype(int).squeeze()
ages_label = ages.astype(str) + "세"  # → '0세', '1세', ..., '100세'
agg.index = ages_label

# ---------- 🎨 그래프 ----------
if chart_type.startswith("꺾은선"):
    fig = px.line(
        agg,
        x=agg.index,
        y=agg.columns,
        labels={"x": "나이", "value": "인구 수", "variable": "지역"},
        title="연령별 인구 분포 (선 그래프)"
    )
else:
    if len(selected) == 1:
        pop = agg[selected[0]]
        pop_neg = pop.copy()
        pop_neg.iloc[:] *= -1  # 좌우대칭용

        pyr = pd.DataFrame({
            "남녀합계(왼쪽)": pop_neg,
            "남녀합계(오른쪽)": pop
        })

        fig = px.bar(
            pyr,
            x=pyr.columns,
            y=pyr.index,
            orientation="h",
            labels={"y": "나이", "value": "인구 수"},
            title=f"{selected[0]} 인구 피라미드"
        )
    else:
        fig = px.bar(
            agg,
            x=agg.index,
            y=agg.columns,
            barmode="group",
            labels={"x": "나이", "value": "인구 수", "variable": "지역"},
            title="연령별 인구 분포 (막대 그래프)"
        )

fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.caption("📊 데이터 출처: 행정안전부 주민등록 인구 통계")
