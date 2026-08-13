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
- **リポジトリ選択** — 既存リポ一覧を GitHub API で取得し、数字で選択 / 0 で新規作成 / `q` で終了（トークンが必要）
- **設定は TOML のみ** — すべての設定は `gitpush.toml`（プロジェクト + グローバル `~/.config/gitpush.toml`）で管理。対話式設定メニューは廃止
- **メニュー操作** — 番号で選択、`q` でキャンセル終了（y/N プロンプトや自由入力には影響しません）
- **非対話モード** — `--yes --public --repo NAME [--message ...]`
- **グローバル設定** — `~/.config/gitpush.toml` をプロジェクト設定にマージ
- **Docker / アンインストーラー** — `Dockerfile`、`uninstall.sh` / `uninstall.ps1`

詳細は各フォルダの README を参照してください。`gitpush.toml.example` が設定例です。

## アップデートについて

現在、`gitpush` には将来的な機能として `gitpush update` コマンドが想定されています。
もしお手元の環境で `gitpush update` コマンドが利用できる場合は、そのコマンドを実行してアップデートしてください。

**`gitpush update` コマンドが無い場合のアップデート方法：**
現在、`gitpush` は起動時に最新版をチェックし、更新がある場合は自動的にアップデートを提案する機能（自己更新機能）が備わっています（`gitpush.toml` にて `self_update = true` の場合）。
そのため、基本的には起動時のプロンプトに従って `y` を入力するだけで最新版に更新されます。

もし手動で更新したい場合は、再度リポジトリを `git pull` するか、最新のインストーラー（`install.sh` または `install.ps1`）を再実行してスクリプトを上書きしてください。

## 言語

起動時に日本語 / English を選択できます。

## ライセンス
[MIT LICENSE](./LICENSE)
自由に使ってください。
