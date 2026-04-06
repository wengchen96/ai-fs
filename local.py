import streamlit as st
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="進階名次預測工具", layout="wide")
st.title("🎯 冷熱號＋近期權重名次預測")

st.markdown("""
輸入歷史資料，每行10個號碼（空格或逗號分隔）
※ 系統自動將 10 轉為 0（0=10）
""")

# ===== 輸入 =====
raw_text = st.text_area("貼上歷史資料", height=200)

# ===== 設定 =====
pred_rank = st.slider("預測名次", 1, 10, 1)
recent_weight = st.slider("近期權重強度", 1.0, 3.0, 2.0)
cold_bonus = st.slider("冷號反彈強度", 1.0, 2.0, 1.3)

# ===== 分析 =====
if st.button("開始分析"):

    if not raw_text.strip():
        st.warning("請輸入資料")
        st.stop()

    # ===== 解析 =====
    DATA = []
    for row in raw_text.strip().split("\n"):
        row = row.replace(",", " ").split()
        if len(row) != 10:
            st.error("每列必須10個號碼")
            st.stop()
        DATA.append([0 if int(x)==10 else int(x) for x in row])

    N = len(DATA)
    st.success(f"載入 {N} 期")

    # ===== 整體出現次數 =====
    total_counts = defaultdict(int)
    last_seen = {i: -1 for i in range(10)}

    for i, row in enumerate(DATA):
        for num in row:
            total_counts[num] += 1
            last_seen[num] = i  # 記錄最後出現位置

    # ===== 冷熱分群 =====
    sorted_nums = sorted(total_counts.items(), key=lambda x: -x[1])
    half = len(sorted_nums)//2
    hot_nums = [x[0] for x in sorted_nums[:half]]
    cold_nums = [x[0] for x in sorted_nums[half:]]

    # ===== 名次預測 =====
    POSITION_WEIGHTS = {
        0:1.5, 1:1.3, 2:1.1, 3:1.0, 4:1.0,
        5:1.0, 6:1.0, 7:1.1, 8:1.3, 9:1.5
    }

    pred_idx = pred_rank - 1
    rank_scores = defaultdict(float)

    for i, row in enumerate(DATA):
        num = row[pred_idx]

        # ===== 近期權重（越新越高）=====
        recency = (i+1) / N
        recency_weight = 1 + (recency * (recent_weight - 1))

        # ===== 冷熱權重 =====
        if num in hot_nums:
            hot_weight = 1.1
        else:
            hot_weight = 0.9

        rank_scores[num] += POSITION_WEIGHTS[pred_idx] * recency_weight * hot_weight

    # ===== 冷號反彈 =====
    for num in range(10):
        gap = N - last_seen[num] if last_seen[num] != -1 else N
        rebound = 1 + (gap / N) * (cold_bonus - 1)
        rank_scores[num] *= rebound

    # ===== 百分比 =====
    total_score = sum(rank_scores.values())
    rank_percent = {
        num: round(rank_scores.get(num,0)/total_score*100, 2)
        for num in range(10)
    }

    # ===== 排序 =====
    sorted_result = sorted(rank_percent.items(), key=lambda x:-x[1])

    df = pd.DataFrame(sorted_result, columns=["號碼(0=10)", "機率(%)"])

    st.subheader(f"📊 第 {pred_rank} 名預測")
    st.dataframe(df)

    # ===== 推薦號碼 =====
    best_num = sorted_result[0][0]
    st.success(f"🔥 最推薦號碼：{best_num} （0=10）")

st.set_page_config(
    page_title="AI名次預測",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 隱藏多餘UI
hide_menu = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

import datetime

today = datetime.datetime.now().strftime("%Y%m%d")
password = st.text_input("輸入今日密碼", type="password")

if password != today:
    st.warning(f"今日密碼錯誤")
    st.stop()
