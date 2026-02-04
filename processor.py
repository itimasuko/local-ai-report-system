import os
import datetime
import shutil
import pandas as pd
import json
import urllib.parse
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# --- デフォルト設定 ---
DEFAULT_MODEL_NAME = "qwen2.5:7b-instruct-q4_k_m"

DEFAULT_PROMPT_TEMPLATE = """
あなたは優秀なマネージャー補佐です。
以下の複数の報告書を読み、チーム全体の日報サマリーを作成してください。

【フォーマット】
# 統合日報 ({date})
## 1. 全体ハイライト
(重要な成果やニュース)

## 2. 部門・プロジェクト別状況
(詳細な進捗)

## 3. 課題・共有事項
(早急に対応すべきこと)

--- 報告書データ ---
{text}
"""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
PROCESSED_DIR = os.path.join(STATIC_DIR, "processed_data")

INPUT_DIR = os.path.join(BASE_DIR, "input_data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_reports")
STATUS_FILE = os.path.join(BASE_DIR, "status.json")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# --- ステータス管理機能 ---
def set_status(state, message=""):
    data = {
        "state": state,
        "message": message,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f)

def get_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                return json.load(f)
        except:
            return {"state": "idle", "message": ""}
    return {"state": "idle", "message": ""}

# --- メイン処理 ---
def run_report_generation(ollama_url, prompt_template=None, filename_prefix="統合日報"):
    print(f"[{datetime.datetime.now()}] 処理開始: 接続先 {ollama_url} / ファイル名: {filename_prefix}")
    
    if not prompt_template:
        prompt_template = DEFAULT_PROMPT_TEMPLATE

    all_text = ""
    files = [f for f in os.listdir(INPUT_DIR) if not f.startswith(".")]
    
    if not files:
        return "投函箱は空です。"

    files_processed = []
    
    # 1. ファイル読み込み
    for filename in files:
        file_path = os.path.join(INPUT_DIR, filename)
        try:
            content = ""
            ext = filename.lower()
            
            if ext.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                content = "\n".join([d.page_content for d in docs])
            elif ext.endswith(".txt") or ext.endswith(".md"):
                loader = TextLoader(file_path, encoding='utf-8')
                docs = loader.load()
                content = "\n".join([d.page_content for d in docs])
            elif ext.endswith(".docx"):
                loader = Docx2txtLoader(file_path)
                docs = loader.load()
                content = "\n".join([d.page_content for d in docs])
            elif ext.endswith(".xlsx"):
                df = pd.read_excel(file_path)
                content = df.to_markdown(index=False)

            if content:
                all_text += f"\n\n--- 報告書: {filename} ---\n{content}"
                files_processed.append(filename)
            else:
                print(f"スキップ: {filename}")
                
        except Exception as e:
            print(f"読込エラー {filename}: {e}")

    if not all_text:
        return "有効なテキストが見つかりませんでした。"

    # 2. AI推論
    try:
        llm = ChatOllama(
            base_url=ollama_url,
            model=DEFAULT_MODEL_NAME,
            temperature=0.2
        )

        final_prompt = prompt_template.replace("{date}", str(datetime.date.today())).replace("{text}", all_text[:12000])
        response = llm.invoke([HumanMessage(content=final_prompt)])
        report_content = response.content

        # 3. 日本語ファイル名 & バックアップ作成
        timestamp = datetime.datetime.now().strftime("%Y年%m月%d日_%H時%M分%S秒")
        report_base_name = f"{filename_prefix}_{timestamp}"
        out_filename = f"{report_base_name}.md"
        
        backup_dir_path = os.path.join(PROCESSED_DIR, report_base_name)
        os.makedirs(backup_dir_path, exist_ok=True)

        reference_links = "\n\n---\n### 📂 参照ファイル (原本バックアップ)\n"
        moved_count = 0
        
        for filename in files_processed:
            src = os.path.join(INPUT_DIR, filename)
            dst = os.path.join(backup_dir_path, filename)
            shutil.move(src, dst)
            moved_count += 1
            
            safe_filename = urllib.parse.quote(filename)
            safe_dirname = urllib.parse.quote(report_base_name)
            web_link_path = f"/app/static/processed_data/{safe_dirname}/{safe_filename}"
            
            # ★ここを変更: HTMLタグで download 属性を付ける
            # これによりクリックした瞬間にファイルとして保存されます
            reference_links += f'- <a href="{web_link_path}" download="{filename}" style="text-decoration:none;">📥 {filename}</a><br>\n'

        final_report_content = report_content + reference_links
        
        out_path = os.path.join(OUTPUT_DIR, out_filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(final_report_content)

        return f"成功: 「{out_filename}」を作成し、{moved_count}件のファイルをバックアップしました。"

    except Exception as e:
        return f"AI接続エラー: {e}"