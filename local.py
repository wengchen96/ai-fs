import streamlit as st
import pandas as pd
from collections import defaultdict

# ===== 🔑 你每天只改這裡 =====
CUSTOM_PASSWORD = "733558"   # ← 每天改這個就好

# ===== 基本設定 =====
st.set_page_config(
    page_title="AI名次預測系統",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 隱藏UI
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("🎯 AI智能名次預測系統")

# ===== 🔒 密碼驗證 =====
st.markdown("### 🔒 請輸入今日密碼")
password = st.text_input("密碼", type="password")

if password != CUSTOM_PASSWORD:
    st.warning("❌ 密碼錯誤（請至LINE取得）")
    st.stop()

st.success("✅ 驗證成功")

# ===== 📲 導流 =====
st.markdown("👉 [加入telegram取得每日密碼](https://t.me/big5138)")

# ===== 輸入 =====
raw_text = st.text_area("📊 貼上歷史資料（每行10個號碼）", height=200)
pred_rank = st.slider("🎯 預測名次", 1, 10, 1)

# ===== 分析 =====
if st.button("開始分析"):

    if not raw_text.strip():
        st.warning("請輸入資料")
        st.stop()

    DATA = []
    for row in raw_text.strip().split("\n"):
        row = row.replace(",", " ").split()
        if len(row) != 10:
            st.error("每列必須10個號碼")
            st.stop()
        DATA.append([0 if int(x)==10 else int(x) for x in row])

    N = len(DATA)

    total_counts = defaultdict(int)
    last_seen = {i: -1 for i in range(10)}

    for i, row in enumerate(DATA):
        for num in row:
            total_counts[num] += 1
            last_seen[num] = i

    sorted_nums = sorted(total_counts.items(), key=lambda x: -x[1])
    half = len(sorted_nums)//2
    hot_nums = [x[0] for x in sorted_nums[:half]]

    POSITION_WEIGHTS = {
        0:1.5, 1:1.3, 2:1.1, 3:1.0, 4:1.0,
        5:1.0, 6:1.0, 7:1.1, 8:1.3, 9:1.5
    }

    pred_idx = pred_rank - 1
    rank_scores = defaultdict(float)

    for i, row in enumerate(DATA):
        num = row[pred_idx]

        recency = (i+1)/N
        recency_weight = 1 + recency

        hot_weight = 1.1 if num in hot_nums else 0.9

        rank_scores[num] += POSITION_WEIGHTS[pred_idx] * recency_weight * hot_weight

    for num in range(10):
        gap = N - last_seen[num] if last_seen[num] != -1 else N
        rebound = 1 + (gap / N) * 0.3
        rank_scores[num] *= rebound

    total_score = sum(rank_scores.values())
    result = {
        num: round(rank_scores.get(num,0)/total_score*100, 2)
        for num in range(10)
    }

    sorted_result = sorted(result.items(), key=lambda x:-x[1])

    df = pd.DataFrame(sorted_result, columns=["號碼(0=10)", "機率(%)"])

    st.subheader("📊 預測結果")

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(df)

    with col2:
        best_num = sorted_result[0][0]
        st.metric("🔥 最推薦號碼", f"{best_num} (0=10)")
