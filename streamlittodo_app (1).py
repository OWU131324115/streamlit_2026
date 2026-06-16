import datetime  # 日付を入れるために
import streamlit as st

st.title("To do list+")
st.caption("タスクと収支を記入して整理しよう！")

st.markdown("---")

# ToDoリストの初期化
if "todo_list" not in st.session_state:
    st.session_state.todo_list = []
if "next_task_i" not in st.session_state:
    st.session_state.next_task_i = 1

# 収入・支出の初期化
if "balance_list" not in st.session_state:
    st.session_state.balance_list = []
if "next_balance_i" not in st.session_state:
    st.session_state.next_balance_i = 1


def _normalize_tasks() -> None:
    updated = False
    today = datetime.date.today()
    for item in st.session_state.todo_list:
        if "i" not in item:
            item["i"] = st.session_state.next_task_i
            st.session_state.next_task_i += 1
            updated = True
        if "date" not in item:
            item["date"] = today  # データに日付がない場合は今日の日付
            updated = True
    if updated:
        st.session_state.todo_list = list(st.session_state.todo_list)


def _move_task(task_i: int, direction: int) -> None:
    tasks = st.session_state.todo_list
    index = next((i for i, item in enumerate(tasks) if item["i"] == task_i), None)
    if index is None:
        return

    target_date = tasks[index]["date"]

    # 同じ日付のタスクの、全体リストにおけるインデックス一覧を取得
    same_date_indices = [
        i for i, item in enumerate(tasks) if item["date"] == target_date
    ]
    pos = same_date_indices.index(index)

    target_pos = pos + direction
    if target_pos < 0 or target_pos >= len(same_date_indices):
        return

    target_index = same_date_indices[target_pos]
    tasks[index], tasks[target_index] = tasks[target_index], tasks[index]


# ボタンを押した時に画面が描画される前に実行する
def _complete_all_today_tasks(target_date) -> None:
    """選択された日のタスクをすべて完了にし、画面のチェックボックスも同期します。"""
    for item in st.session_state.todo_list:
        if item["date"] == target_date:
            item["done"] = True
            # 画面上のチェックボックスの記憶(session_state)も同時にTrueに書き換える
            st.session_state[f"checkbox_{item['i']}"] = True


_normalize_tasks()


# 1. カレンダー機能

st.subheader("📅 日付を選択")
selected_date = st.date_input("タスクを追加する日付を選んでください", datetime.date.today())


tab1, tab2 = st.tabs(["📝 Todoリスト", "💴 収支管理"])




# 2. タスク追加機能
with tab1:
    st.subheader(f"▼ add a task")
new_task = st.text_input("タスクを入力してください", placeholder="例 : 30分ランニングする🏃")

if st.button("タスクを追加"):
    if new_task:
        st.session_state.todo_list.append(
            {
                "i": st.session_state.next_task_i,
                "task": new_task,
                "done": False,
                "date": selected_date,  # 選択した日付をデータに含める
            }
        )
    st.session_state.next_task_i += 1
    st.success(f"「{new_task}」を追加しました！")
    st.rerun()
    else:
        st.error("タスクを入力してください")
# 選択された日付のタスクだけをピックアップ
filtered_tasks = [
    item for item in st.session_state.todo_list if item["date"] == selected_date
]


# 3. ToDoリスト表示（選択された日付のみ）

st.subheader(f"📝 To Do List 【{selected_date.strftime('%Y.%m.%d')}】")

if not filtered_tasks:
    st.info("この日のタスクはありません")
else:
    # 完了・未完了
    total_tasks = len(filtered_tasks)
    completed_tasks = sum(1 for item in filtered_tasks if item["done"])

    st.write(
        f"**タスク数**: {total_tasks} 件 | **完了**: {completed_tasks} 件 | **残り**: {total_tasks - completed_tasks} 件"
    )

    # 各タスクの表示
    for i, item in enumerate(filtered_tasks):
        col1, col2, col3, col4 = st.columns([4, 1, 1, 1])

        with col1:
            # 完了状態の管理
            is_done = st.checkbox(
                item["task"], value=item["done"], key=f"checkbox_{item['i']}"
            )

            if is_done != item["done"]:
                item["done"] = is_done
                st.rerun()

        with col2:
            if st.button("↑", key=f"move_up_{item['i']}", disabled=i == 0):
                _move_task(item["i"], -1)
                st.rerun()

        with col3:
            if st.button(
                "↓",
                key=f"move_down_{item['i']}",
                disabled=i == len(filtered_tasks) - 1,
            ):
                _move_task(item["i"], 1)
                st.rerun()

        with col4:
            if st.button("🗑️ 削除", key=f"delete_{item['i']}"):
                st.session_state.todo_list = [
                    t for t in st.session_state.todo_list if t["i"] != item["i"]
                ]
                st.success("タスクを削除しました")
                st.rerun()


with tab2:
    st.subheader(f"▼ add icome and expenditure")
    
    # 入力項目の配置
    b_type = st.radio("種別", ["支出", "収入"], horizontal=True)
    amount = st.number_input("金額", min_value=0, step=100)
    memo = st.text_input("メモ", placeholder="例: ランチ代、給料など")
    
    if st.button("収支を追加"):
        if amount > 0:
            st.session_state.balance_list.append({
                "i": st.session_state.next_balance_i,
                "date": selected_date,
                "type": b_type,
                "amount": amount,
                "memo": memo
            })
            st.session_state.next_balance_i += 1
            st.success("記録しました！")
            st.rerun()


# 選択された日の収支をフィルタリング
    filtered_balance = [b for b in st.session_state.balance_list if b["date"] == selected_date]
    
    if not filtered_balance:
        st.info("この日の収支記録はありません")
    else:
        # 計算
        total_income = sum(b["amount"] for b in filtered_balance if b["type"] == "収入")
        total_expense = sum(b["amount"] for b in filtered_balance if b["type"] == "支出")
        net_balance = total_income - total_expense
        
        # 合計の表示
        st.metric(label="この日の収支残高", value=f"{net_balance:,} 円", delta=f"収入: {total_income:,}円 / 支出: {total_expense:,}円")
        
        # 一覧表示と削除ボタン
        for b in filtered_balance:
            col1, col2, col3 = st.columns([2, 4, 1])
            with col1:
                st.write(f"[{b['type']}] {b['amount']:,}円")
            with col2:
                st.write(b["memo"])
            with col3:
                if st.button("🗑️ 削除", key=f"del_b_{b['i']}"):
                    st.session_state.balance_list = [item for item in st.session_state.balance_list if item["i"] != b["i"]]
                    st.rerun()

# 一括操作（選択された日付のタスクのみに適用）
if filtered_tasks:
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.button(
            "この日のタスクを全て完了にする",
            on_click=_complete_all_today_tasks,
            args=(selected_date,),
        )

    with col2:
        if st.button("この日の完了済みタスクを削除"):
            st.session_state.todo_list = [
                item
                for item in st.session_state.todo_list
                if not (item["date"] == selected_date and item["done"])
            ]
            st.success("選択された日の完了済みタスクを削除しました")
            st.rerun()

st.markdown("---")


# 4. サイドバーの拡張

st.sidebar.header("📅 全体の予定一覧")
if st.session_state.todo_list:
    # 日付順、かつ未完了が上に来るよう表示
    sorted_all_tasks = sorted(
        st.session_state.todo_list, key=lambda x: (x["date"], x["done"])
    )
    for item in sorted_all_tasks:
        status = "✔" if item["done"] else "□"
        st.sidebar.write(
            f"{status} **{item['date'].strftime('%m/%d')}**: {item['task']}"
        )
else:
    st.sidebar.info("タスクがありません。")

st.sidebar.markdown("---")
st.sidebar.header("このアプリについて")
st.sidebar.success(
    """
    このアプリではTodoリスト作成と収支管理ができます。
    - 日付を選択してタスクを登録
    - サイドバーには、すべてのタスクが日付順に一覧表示されます
    - 収支管理では収入と支出を管理することが出来ます。
    """
)
