# Safe Git Push

機密情報（`.env`、セッションログ、AIエージェントの設定など）を守りながら、安全に GitHub / GitLab へプッシュするためのインタラクティブ CLI ツールです。

AI エージェントを使って開発していると、セッションログや `.env` がうっかりパブリックリポジトリに push されてしまうリスクがあります。このツールは push 前に `.gitignore` の整備と `.env` のダミー化を自動で行います。

## フォルダ構成

- `linux/` — Linux / macOS 用スクリプトとインストーラー
- `windows/` — Windows 用スクリプトとインストーラー
- `gitpush.toml.example` — 設定ファイルの例
- `Dockerfile` — コンテナ実行用

使っている OS のフォルダを開いて、それぞれの README を参照してください。

## 主な機能

1. `.gitignore` の自動生成（`.env`, `__pycache__/`, `.roo/`, `.aider/`, `.qwen/` などを除外）
2. `.env` の自動スキャン → `.env.example` 生成（値をダミー化）
3. リポジトリの自動作成（public / private 選択式、`gh` / `glab` 使用）
4. GitHub / GitLab リモート URL の設定（`git init` / `remote add` / `branch -M main`）
5. プッシュ前の確認（`y` のみ `git push` を実行）

## 高度な自動化機能（v1.2.0）

`gitpush.toml` をプロジェクトに置くと有効になる機能:

- **pre-commit フック自動登録** — `.env` やトークンがコミットされるのをブロック
- **CI ワークフロー自動生成** — `.github/workflows/secret-scan.yml`（gitleaks でプッシュ時スキャン）
- **リモート警告** — 予期しないリモートへの push を警告
- **自己更新** — 起動時に GitHub 上の最新版と比較し更新を提案（stable / beta チャンネル可）
- **ソース内秘密リテラルスキャン** — `ghp_...` 等を検出して警告（`scan_secrets`）
- **機密ファイル警告** — `.pem` / `.key` 等を検出して警告（`warn_secret_files`）
- **.gitignore ギャップチェック** — 不足パターンを警告し追加を提案（`check_gitignore_gap`）
- **コミット履歴スキャン** — 過去のコミットもスキャン（重い・デフォルト off、`scan_history`）
- **dry-run プレビュー** — push 前に `git diff --stat` を表示（`dry_run`）
- **マルチリモート push** — 追加リモートへ一斉 push（`extra_remotes`）
- **コミットメッセージ指定** — デフォルト / 入力 / `--message`（`default_message`）
- **ブランチ自動命名** — パターン指定で自動命名（`branch_pattern`、デフォルト off）
- **ログ出力** — `gitpush.log` へ記録（`log_file`）
- **GitLab / Bitbucket 対応** — `provider = "gitlab"`（`glab` 使用）
- **トークンで push** — GitHub トークン（`GITHUB_TOKEN` 環境変数 / `gitpush.toml` の `token = "..."`）を使い、認証なしで push。push 後に remote URL からトークンを自動削除
- **非対話モード** — `--yes --public --repo NAME [--message ...]`
- **グローバル設定** — `~/.config/gitpush.toml` をプロジェクト設定にマージ
- **Docker / アンインストーラー** — `Dockerfile`、`uninstall.sh` / `uninstall.ps1`

詳細は各フォルダの README を参照してください。`gitpush.toml.example` が設定例です。

## 言語

起動時に日本語 / English を選択できます。

## ライセンス

自由に使ってください。
