import streamlit as st
from datetime import datetime

st.title("第7回 Streamlit 状態管理演習 - 解答例")
st.caption("st.session_state を使って今日の気分を記録しましょう。")

st.markdown("---")
st.subheader("演習: 今日の気分記録アプリ")
st.write("**課題**: ボタンで気分を選択し、`st.session_state` で履歴を保持するアプリを作成する。")

# session_stateでリストを初期化
if 'mood_history' not in st.session_state:
    st.session_state.mood_history = []

st.write("今の気分を選んでください：")

# 気分ボタンを横に並べて表示
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("😊 嬉しい"):
        st.session_state.mood_history.append("😊 嬉しい")

with col2:
    if st.button("😢 悲しい"):
        st.session_state.mood_history.append("😢 悲しい")

with col3:
    if st.button("😴 眠い"):
        st.session_state.mood_history.append("😴 眠い")

with col4:
    if st.button("🍕 お腹すいた"):
        st.session_state.mood_history.append("🍕 お腹すいた")

# 気分履歴を表示
if st.session_state.mood_history:
    st.markdown("---")
    st.subheader("気分の履歴")
    for i, mood in enumerate(reversed(st.session_state.mood_history)):
        st.write(f"{len(st.session_state.mood_history) - i}. {mood}")
    
    # 発展: 各気分の回数をカウント
    st.markdown("---")
    st.subheader("気分の統計")
    mood_count = {}
    for mood in st.session_state.mood_history:
        mood_count[mood] = mood_count.get(mood, 0) + 1
    
    for mood, count in mood_count.items():
        st.write(f"{mood}: {count}回")
    
    # リセットボタン
    if st.button("履歴をリセット"):
        st.session_state.mood_history = []
        st.rerun()

else:
    st.info("気分ボタンを押して記録を始めましょう！")

st.markdown("---")
st.success("✅ session_stateを使って状態を保持する気分記録アプリの解答例です。") 