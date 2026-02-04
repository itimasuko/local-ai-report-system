# 🛡️ Local AI Report System

ローカル環境（Docker + Ollama）で動作する、セキュアな日報集計・報告書生成システムです。
機密情報を外部クラウドに送信することなく、社内ネットワーク内だけでAIによる要約・分析・アーカイブ化が完結します。

## ✨ 特徴

- **🔒 完全ローカル動作**: データは外部API（OpenAI等）に送信されず、社外秘情報の取り扱いに最適です。
- **📄 マルチフォーマット対応**: PDF, Word(.docx), Excel(.xlsx), Text(.txt/.md) をそのまま投函可能。
- **🔗 トレーサビリティ**: 生成されたレポートには、参照元の原本ファイルへのリンクが自動埋め込みされます（ワンクリックでダウンロード/参照可能）。
- **🐳 Docker対応**: コマンド一発で環境構築が完了。Windows/Mac/Linux 問わず動作します。
- **📝 カスタムプロンプト**: 管理画面からAIへの指示（集計の観点など）を自由に調整可能です。

## 🚀 クイックスタート

### 前提条件
- **Docker Desktop** (または Docker Engine) がインストールされていること
- **Ollama** が動作する環境（ローカルPC、またはLAN内の別サーバー）があること
  - 推奨モデル: `qwen2.5:7b-instruct-q4_k_m` など

### 1. インストール

リポジトリをクローンします。

```bash
git clone [https://github.com/YOUR_USERNAME/local-ai-report-system.git](https://github.com/YOUR_USERNAME/local-ai-report-system.git)
cd local-ai-report-system/web-app

```

### 2. 設定ファイルの準備

配布用の `config.sample.json` をコピーして、実設定ファイル `config.json` を作成します。

**Windows:**
ファイルエクスプローラーでコピー＆リネームするか、コマンドで実行:

```cmd
copy config.sample.json config.json

```

**Mac/Linux:**

```bash
cp config.sample.json config.json

```

### 3. 接続設定

`config.json` をテキストエディタで開き、OllamaサーバーのIPアドレスを設定します。

```json
{
    "ollama_ip": "192.168.1.XX",
    "ollama_port": "11434",
    "report_name_prefix": "統合日報"
}

```

> **Note:** `ollama_ip` には、Ollamaが動いているPCのIPアドレス（例: `192.168.1.50`）を入力してください。Windows機1台で完結させる場合は `"host.docker.internal"` と設定してください。

### 4. 起動

**Windowsの方:**
フォルダ内の `start_app.bat` をダブルクリックしてください。

**Mac/Linuxの方:**
以下のコマンドを実行してください。

```bash
docker-compose up -d --build

```

### 5. アクセス

ブラウザで以下のURLにアクセスします。

* **🛡️ 管理者ダッシュボード**: [http://localhost:8501](https://www.google.com/search?q=http://localhost:8501)
* ファイル管理、AI実行、設定変更、過去レポートの検索ができます。


* **📮 ユーザー投函ポスト**: [http://localhost:8502](https://www.google.com/search?q=http://localhost:8502)
* メンバーが日報をアップロードするためのシンプルな画面です。



---

## 📂 ディレクトリ構成

* `input_data/`: 解析待ちのファイルが一時的に置かれる場所
* `output_reports/`: AIが生成したMarkdownレポートの保存先
* `static/processed_data/`: 処理済みファイルのバックアップ（日時フォルダ別に自動整理され、Webからアクセス可能）
* `config.json`: システム設定（Gitにはアップロードされません）

## 🛠️ 技術スタック

* **Frontend**: Streamlit
* **LLM Engine**: LangChain + Ollama
* **Infrastructure**: Docker / Docker Compose
* **Language**: Python 3.11

## ⚠️ Ollamaサーバー側の設定について

Ollamaを別サーバー（またはDockerホスト）で動かす場合、外部からのアクセスを許可するために環境変数の設定が必要です。

**Linux (systemd):**
`sudo systemctl edit ollama.service` で以下を追加:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0"

```

**Windows:**
システム環境変数 `OLLAMA_HOST` に `0.0.0.0` を追加して再起動してください。

```
