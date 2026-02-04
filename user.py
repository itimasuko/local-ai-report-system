import streamlit as st
import os
import processor
import time

# --- 画面設定 ---
st.set_page_config(page_title="日報投函ポスト", layout="centered")
st.title("📮 日報・報告書 投函ポスト")

# --- セッション状態の初期化 (リセット用) ---
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# --- システム状態の表示 ---
status = processor.get_status()
if status["state"] == "running":
    st.info("ℹ️ 現在、AIが集計処理を実行中です。投函は可能です。")

st.write("本日の業務報告書はこちらにアップロードしてください。")

# ---------------------------------------------------------
# 投函口
# keyに変数を使うことで、処理後に値をインクリメントして強制リセットする
# ---------------------------------------------------------
uploaded_files = st.file_uploader(
    "ファイルをドラッグ＆ドロップ (PDF, TXT, DOCX, XLSX)", 
    type=["pdf", "txt", "md", "docx", "xlsx"], 
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}"  # ここが重要！
)

if uploaded_files:
    # 1. 保存処理
    count = 0
    for f in uploaded_files:
        save_path = os.path.join(processor.INPUT_DIR, f.name)
        with open(save_path, "wb") as w:
            w.write(f.getbuffer())
        count += 1
    
    # 2. 完了メッセージ
    st.success(f"✅ {count}件の提出を受け付けました！")
    time.sleep(1.5)

    # 3. アップロードボックスを新品にする (キーを更新)
    st.session_state.uploader_key += 1
    
    # 4. リロード (これでボックスが空になる)
    st.rerun()

# ---------------------------------------------------------
# 現在の提出状況
# ---------------------------------------------------------
st.divider()
st.subheader("📦 現在の提出状況")

files = sorted([f for f in os.listdir(processor.INPUT_DIR) if not f.startswith(".")])

if files:
    st.caption(f"未処理のファイル: {len(files)}件")
    for f in files:
        st.text(f"・ {f}")
else:
    st.caption("現在、未処理のファイルはありません。")

st.markdown("---")
st.caption("※ 間違えて投函した場合は、管理者に連絡してください。")