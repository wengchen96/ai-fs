import streamlit as st
import pandas as pd
from collections import defaultdict

# ===== 🔑 每日手動密碼 =====
CUSTOM_PASSWORD = "0407"

# ===== 頁面設定 =====
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

# ===== 密碼驗證 =====
st.markdown("### 🔒 請輸入密碼")
password = st.text_input("密碼", type="password")

if password != CUSTOM_PASSWORD:
    st.warning("❌ 密碼錯誤")
    st.stop()

st.success("✅ 驗證成功")

# ===== 輸入區 =====
raw_text = st.text_area("📊 請貼入歷史資料（每列10個號碼）", height=200)

pred_rank = st.slider("🎯 選擇預測名次", 1, 10, 1)

# ===== 分析 =====
if st.button("開始分析"):

    if not raw_text.strip():
        st.warning("請輸入資料")
        st.stop()

    # ===== 解析資料 =====
    DATA = []
    for row in raw_text.strip().split("\n"):
        row = row.replace(",", " ").split()
        if len(row) != 10:
            st.error("每列必須10個號碼")
            st.stop()
        DATA.append([0 if int(x)==10 else int(x) for x in row])

    N = len(DATA)

    # ===== 區段統計 =====
    front_counts = defaultdict(int)   # 1~5
    middle_counts = defaultdict(int)  # 3~8
    back_counts = defaultdict(int)    # 6~10

    for row in DATA:
        for i, num in enumerate(row):
            if i < 5:
                front_counts[num] += 1
            if 2 <= i <= 7:
                middle_counts[num] += 1
            if i >= 5:
                back_counts[num] += 1

    # ===== 轉百分比 =====
    def calc_percent(count_dict):
        return {
            num: round(count_dict.get(num, 0) / N * 100, 2)
            for num in range(10)
        }

    front_percent = calc_percent(front_counts)
    middle_percent = calc_percent(middle_counts)
    back_percent = calc_percent(back_counts)

    # ===== 顯示區段 =====
    st.subheader("📊 區段機率分析")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**前段 (1~5名)**")
        df_front = pd.DataFrame(sorted(front_percent.items(), key=lambda x:-x[1]),
                                columns=["號碼(0=10)", "%"])
        st.dataframe(df_front)

    with col2:
        st.markdown("**中段 (3~8名)**")
        df_middle = pd.DataFrame(sorted(middle_percent.items(), key=lambda x:-x[1]),
                                 columns=["號碼(0=10)", "%"])
        st.dataframe(df_middle)

    with col3:
        st.markdown("**後段 (6~10名)**")
        df_back = pd.DataFrame(sorted(back_percent.items(), key=lambda x:-x[1]),
                               columns=["號碼(0=10)", "%"])
        st.dataframe(df_back)

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

    # ===== 取前6名 =====
    top6 = sorted(rank_percent.items(), key=lambda x:-x[1])[:6]
    df_pred = pd.DataFrame(top6, columns=["號碼(0=10)", "機率(%)"])

    # ===== 顯示預測 =====
    st.subheader(f"🎯 第 {pred_rank} 名預測（前6名）")

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(df_pred)

    with col2:
        best_num = top6[0][0]
        st.metric("🔥 最推薦號碼", f"{best_num} (0=10)")
