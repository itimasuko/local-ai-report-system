import time
import os
import json
import processor

CONFIG_FILE = "config.json"
TRIGGER_FILE = "start.signal" 

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {}

def main():
    print("=== Worker Started: Waiting for jobs... ===")
    processor.set_status("idle", "システム起動: 待機中")

    while True:
        if os.path.exists(TRIGGER_FILE):
            print(f"[{processor.datetime.datetime.now()}] Job detected!")
            processor.set_status("running", "AIが集計を行っています...")
            
            try:
                config = load_config()
                ip = config.get("ollama_ip", "192.168.1.50")
                port = config.get("ollama_port", "11434")
                ollama_url = f"http://{ip}:{port}"
                
                # ★追加: レポート名の設定を取得（デフォルトは「統合日報」）
                filename_prefix = config.get("report_name_prefix", "統合日報")
                
                mode = config.get("prompt_mode", "default")
                custom_text = config.get("custom_prompt", "")
                
                target_prompt = None
                if mode == "custom" and custom_text.strip():
                    target_prompt = custom_text
                else:
                    target_prompt = processor.DEFAULT_PROMPT_TEMPLATE

                os.remove(TRIGGER_FILE)

                # リトライ処理
                max_retries = 3
                wait_seconds = 5
                result_msg = ""

                for attempt in range(max_retries):
                    try:
                        if attempt > 0: print(f"Retry {attempt+1}...")
                        
                        # ★変更: filename_prefix を渡す
                        result_msg = processor.run_report_generation(
                            ollama_url, 
                            prompt_template=target_prompt,
                            filename_prefix=filename_prefix
                        )
                        
                        if "AI接続エラー" not in result_msg:
                            break
                        else:
                            if attempt < max_retries - 1:
                                processor.set_status("running", f"AI接続リトライ中 ({attempt+1}/{max_retries})...")
                                time.sleep(wait_seconds)
                    except Exception as e:
                        if attempt < max_retries - 1:
                            processor.set_status("running", f"通信リトライ中 ({attempt+1}/{max_retries})...")
                            time.sleep(wait_seconds)
                        else:
                            result_msg = f"システムエラー: {e}"

                print(f"Job Finished: {result_msg}")
                if "成功" in result_msg:
                    processor.set_status("idle", f"完了: {result_msg}")
                else:
                    processor.set_status("idle", f"エラー: {result_msg}")
            
            except Exception as e:
                processor.set_status("error", f"致命的エラー: {e}")
            
        time.sleep(2)

if __name__ == "__main__":
    main()