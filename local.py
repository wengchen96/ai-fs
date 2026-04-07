import streamlit as st
import pandas as pd
from collections import defaultdict
import random

# ===== 🔑 密碼 =====
CUSTOM_PASSWORD = "0407"

st.set_page_config(
    page_title="AI智能預測系統",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ===== 隱藏UI =====
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("🎯 AI智能預測系統")

# ===== 密碼 =====
st.markdown("### 🔒 請輸入密碼")
password = st.text_input("密碼", type="password")

if password != CUSTOM_PASSWORD:
    st.warning("❌ 密碼錯誤")
    st.stop()

st.success("✅ 驗證成功")

# ===== 輸入 =====
raw_text = st.text_area("📊 請貼入歷史資料（每列10個號碼）", height=200)

pred_rank = st.slider("🎯 選擇預測名次", 1, 10, 1)
pick_count = st.slider("🎯 預測碼數", 1, 10, 3)

# ===== 分析 =====
if st.button("開始分析"):

    if not raw_text.strip():
        st.warning("請輸入資料")
        st.stop()

    # ===== 資料解析 =====
    DATA = []
    for row in raw_text.strip().split("\n"):
        row = row.replace(",", " ").split()
        if len(row) != 10:
            st.error("每列必須10個號碼")
            st.stop()
        DATA.append([0 if int(x)==10 else int(x) for x in row])

    N = len(DATA)

    # ===== 🎯 固定隨機名次 =====
    rand_rank = random.randint(1, 10)
    idx = rand_rank - 1

    # ===== 🔥 用名次當seed（關鍵）=====
    random.seed(rand_rank)

    rank_counts = defaultdict(int)
    for row in DATA:
        rank_counts[row[idx]] += 1

    sorted_nums = sorted(rank_counts.items(), key=lambda x: -x[1])

    hot_nums = [num for num, _ in sorted_nums[:5]]
    cold_nums = [num for num, _ in sorted_nums[5:]]

    # ===== 🎯 限制最多8碼 =====
    pick_count = min(pick_count, 8)

    # ===== 比例 85 / 15 =====
    hot_n = max(1, int(pick_count * 0.85))
    cold_n = pick_count - hot_n

    hot_pick = random.sample(hot_nums, min(hot_n, len(hot_nums)))
    cold_pick = random.sample(cold_nums, min(cold_n, len(cold_nums)))

    final_nums = list(set(hot_pick + cold_pick))

    # 補齊（避免不足）
    while len(final_nums) < pick_count:
        candidate = random.choice(hot_nums)
        if candidate not in final_nums:
            final_nums.append(candidate)

    # ===== 排序（0當10）=====
    final_nums_sorted = sorted(final_nums, key=lambda x: 10 if x == 0 else x)
    final_str = ",".join(str(n) for n in final_nums_sorted)

    # ===== 顯示 =====
    st.subheader("🎯 預測結果")
    st.success(f"預測結果：第{rand_rank}名 {final_str}")

    # ===== 名次預測 =====
    POSITION_WEIGHTS = {
        0:1.5, 1:1.3, 2:1.1, 3:1.0, 4:1.0,
        5:1.0, 6:1.0, 7:1.1, 8:1.3, 9:1.5
    }

    pred_idx = pred_rank - 1
    rank_scores = defaultdict(float)

    for row in DATA:
        num = row[pred_idx]
        rank_scores[num] += POSITION_WEIGHTS[pred_idx]

    total_score = sum(rank_scores.values())

    rank_percent = {
        num: round(rank_scores.get(num,0)/total_score*100, 2)
        for num in range(10)
    }

    top6 = sorted(rank_percent.items(), key=lambda x:-x[1])[:6]
    df_pred = pd.DataFrame(top6, columns=["號碼(0=10)", "機率(%)"])

    st.subheader(f"📊 預測名次（第 {pred_rank} 名）")

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(df_pred)

    with col2:
        best_num = top6[0][0]
        st.metric("🔥 最推薦號碼", f"{best_num} (0=10)")

    # ===== 區段 =====
    front_counts = defaultdict(int)
    middle_counts = defaultdict(int)
    back_counts = defaultdict(int)

    for row in DATA:
        for i, num in enumerate(row):
            if i < 5:
                front_counts[num] += 1
            if 2 <= i <= 7:
                middle_counts[num] += 1
            if i >= 5:
                back_counts[num] += 1

    def calc_percent(count_dict):
        return {
            num: round(count_dict.get(num, 0) / N * 100, 2)
            for num in range(10)
        }

    front_percent = calc_percent(front_counts)
    middle_percent = calc_percent(middle_counts)
    back_percent = calc_percent(back_counts)

    st.subheader("📊 區段機率分析")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**前段 (1~5名)**")
        st.dataframe(pd.DataFrame(sorted(front_percent.items(), key=lambda x:-x[1]),
                                 columns=["號碼(0=10)", "%"]))

    with col2:
        st.markdown("**中段 (3~8名)**")
        st.dataframe(pd.DataFrame(sorted(middle_percent.items(), key=lambda x:-x[1]),
                                 columns=["號碼(0=10)", "%"]))

    with col3:
        st.markdown("**後段 (6~10名)**")
        st.dataframe(pd.DataFrame(sorted(back_percent.items(), key=lambda x:-x[1]),
                                 columns=["號碼(0=10)", "%"]))
