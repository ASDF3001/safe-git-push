# Safe Git Push

機密情報（`.env`、セッションログ、AIエージェントの設定など）を守りながら、安全に GitHub へプッシュするためのインタラクティブ CLI ツールです。

AI エージェントを使って開発していると、セッションログや `.env` がうっかりパブリックリポジトリに push されてしまうリスクがあります。このツールは push 前に `.gitignore` の整備と `.env` のダミー化を自動で行います。

## フォルダ構成

- `linux/` — Linux / macOS 用スクリプトとインストーラー
- `windows/` — Windows 用スクリプトとインストーラー

使っている OS のフォルダを開いて、それぞれの README を参照してください。

## 主な機能

1. `.gitignore` の自動生成（`.env`, `__pycache__/`, `.roo/`, `.aider/`, `.qwen/` などを除外）
2. `.env` の自動スキャン → `.env.example` 生成（値をダミー化）
3. リポジトリの自動作成（public / private 選択式、`gh` 使用）
4. GitHub リモート URL の設定（`git init` / `remote add` / `branch -M main`）
5. プッシュ前の確認（`y` のみ `git push` を実行）

## 言語

起動時に日本語 / English を選択できます。

## ライセンス

自由に使ってください。
