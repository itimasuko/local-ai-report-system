import streamlit as st
import os
import json
import processor
import time

# --- 設定管理 ---
CONFIG_FILE = "config.json"
TRIGGER_FILE = "start.signal" 

DEFAULT_CONFIG = {
    "ollama_ip": "192.168.1.50",
    "ollama_port": "11434",
    "prompt_mode": "default", 
    "custom_prompt": processor.DEFAULT_PROMPT_TEMPLATE,
    "report_name_prefix": "統合日報"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(new_config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(new_config, f, ensure_ascii=False, indent=4)

# --- 画面構築 ---
st.set_page_config(page_title="AIシステム管理画面", layout="wide")
config = load_config()
status = processor.get_status() # ここで最新の状態をファイルから読み込んでいます

if "admin_uploader_key" not in st.session_state:
    st.session_state.admin_uploader_key = 0

with st.sidebar:
    st.header("🛠️ 管理者設定")
    
    # サーバー接続設定 (閉じておく)
    with st.expander("📡 サーバー接続設定", expanded=False):
        current_ip = config.get("ollama_ip", DEFAULT_CONFIG["ollama_ip"])
        current_port = config.get("ollama_port", DEFAULT_CONFIG["ollama_port"])
        input_ip = st.text_input("IPアドレス", value=current_ip)
        input_port = st.text_input("ポート番号", value=current_port)
        if st.button("接続設定を保存"):
            config["ollama_ip"] = input_ip
            config["ollama_port"] = input_port
            save_config(config)
            st.toast("接続設定を保存しました")
            time.sleep(0.5)
            st.rerun()

    # ★修正1: 初期状態を閉じる (expanded=False)
    with st.expander("🏷️ 出力ファイル名設定", expanded=False):
        current_prefix = config.get("report_name_prefix", "統合日報")
        new_prefix = st.text_input("ファイル名の先頭 (日本語可)", value=current_prefix)
        if st.button("ファイル名を保存"):
            config["report_name_prefix"] = new_prefix
            save_config(config)
            st.toast(f"ファイル名を保存しました")
            time.sleep(0.5)
            st.rerun()

    # プロンプト設定 (閉じておく)
    with st.expander("📝 プロンプト設定", expanded=False):
        current_mode = config.get("prompt_mode", "default")
        saved_custom = config.get("custom_prompt", processor.DEFAULT_PROMPT_TEMPLATE)
        options = ["デフォルト", "カスタマイズ"]
        idx = 0 if current_mode == "default" else 1
        selected_label = st.radio("モード選択", options, index=idx)
        selected_mode_key = "default" if selected_label == "デフォルト" else "custom"

        if selected_mode_key != current_mode:
            config["prompt_mode"] = selected_mode_key
            save_config(config)
            st.toast(f"モードを{selected_label}に変更しました")
            time.sleep(0.5)
            st.rerun()

        if selected_mode_key == "custom":
            input_prompt = st.text_area("カスタムプロンプト", value=saved_custom, height=300)
            if st.button("カスタム内容を保存"):
                config["custom_prompt"] = input_prompt
                save_config(config)
                st.toast("保存しました")
                time.sleep(0.5)
                st.rerun()

    st.divider()
    st.subheader("🤖 システム状態")
    
    # 状態表示
    if status["state"] == "running":
        st.warning("稼働中 (Busy)")
        st.spinner("処理中...")
    elif status["state"] == "error":
        st.error("エラー")
    else:
        st.success("待機中 (Ready)")
    
    st.caption(f"Log: {status.get('message', '')}")
    
    # ★修正2: ボタンを押したことが分かるようにToastを出し、明示的にリロード
    if st.button("🔄 最新情報を確認"):
        st.toast("最新の状態を取得しました")
        time.sleep(0.5) # メッセージを見せるための短いウェイト
        st.rerun()

st.title("🛡️ AI集計システム 管理ダッシュボード")
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 未処理ファイルの管理")
    # アップロード欄はよく使うので開けておく
    with st.expander("管理者アップロード", expanded=True):
        uploaded_files = st.file_uploader("ファイル追加", type=["pdf", "txt", "md", "docx", "xlsx"], accept_multiple_files=True, key=f"admin_up_{st.session_state.admin_uploader_key}")
        if uploaded_files:
            count = 0
            for f in uploaded_files:
                with open(os.path.join(processor.INPUT_DIR, f.name), "wb") as w:
                    w.write(f.getbuffer())
                count += 1
            st.success(f"{count}件 アップロード完了")
            st.session_state.admin_uploader_key += 1
            time.sleep(1.0)
            st.rerun()

    files = sorted([f for f in os.listdir(processor.INPUT_DIR) if not f.startswith(".")])
    if files:
        st.info(f"未処理: {len(files)}件")
        for f in files:
            c1, c2 = st.columns([3, 1])
            with c1: st.text(f"📄 {f}")
            with c2:
                if st.button("削除", key=f"del_{f}", type="secondary"):
                    os.remove(os.path.join(processor.INPUT_DIR, f))
                    st.toast(f"削除: {f}")
                    time.sleep(0.5)
                    st.rerun()
    else:
        st.caption("未処理ファイルはありません。")

    st.write("---")
    is_running = (status["state"] == "running")
    if st.button("🚀 AI集計を実行開始", type="primary", disabled=is_running):
        if not files:
            st.warning("ファイルがありません")
        else:
            with open(TRIGGER_FILE, "w") as f:
                f.write("start")
            st.toast("Workerへ開始指示を出しました")
            time.sleep(1)
            st.rerun()

with col2:
    st.subheader("2. レポート管理")
    search_query = st.text_input("🔍 レポート内をキーワード検索", placeholder="例: プロジェクトA, トラブル...")
    all_reports = sorted([f for f in os.listdir(processor.OUTPUT_DIR) if f.endswith(".md")], key=lambda x: os.path.getmtime(os.path.join(processor.OUTPUT_DIR, x)), reverse=True)
    
    display_reports = []
    if search_query:
        for r in all_reports:
            path = os.path.join(processor.OUTPUT_DIR, r)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if search_query in content:
                    display_reports.append(r)
            except:
                pass
        if display_reports:
            st.caption(f"検索結果: {len(display_reports)}件 ヒット")
        else:
            st.warning("該当なし")
    else:
        display_reports = all_reports

    if not display_reports and not search_query: st.write("レポートなし")
    
    for r in display_reports:
        path = os.path.join(processor.OUTPUT_DIR, r)
        with st.expander(f"📄 {r}", expanded=False):
            try:
                with open(path, "r", encoding="utf-8") as f: content = f.read()
                b1, b2 = st.columns([1,1])
                with b1: st.download_button("DL", content, file_name=r, key=f"dl_{r}")
                with b2: 
                    if st.button("削除", key=f"del_rp_{r}"):
                        os.remove(path)
                        st.rerun()
                st.divider()
                
                if search_query:
                    highlighted = content.replace(search_query, f":red[**{search_query}**]")
                    st.markdown(highlighted, unsafe_allow_html=True)
                else:
                    st.markdown(content, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"読込エラー: {e}")