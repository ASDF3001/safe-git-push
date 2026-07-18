# Safe Git Push (Windows)

機密情報を守りながら安全に GitHub / GitLab へプッシュする CLI ツールの Windows 版です。

## インストール

### A. 実行ファイル (exe) を使う

`windows/gitpush.exe` をダウンロードして、任意のフォルダに置くだけで使えます。
Python のインストールは不要です。

```powershell
# 例: ダウンロードして実行
Invoke-WebRequest -Uri https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/windows/gitpush.exe -OutFile gitpush.exe
.\gitpush.exe
```

注意: この exe は Linux 環境 (wine + PyInstaller) でビルドしています。
Windows での動作確認は行っていないため、不具合があれば Issue で報告してください。

### B. PowerShell でワンライナー（Python 版）

```powershell
irm https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/windows/install.ps1 | iex
```

実行後、新しい PowerShell ウィンドウを開くか以下を実行:

```powershell
. $PROFILE
```

### C. 手動（Python 版）

```powershell
git clone https://github.com/ASDF3001/safe-git-push.git
New-Item -ItemType Directory -Force -Path ~/git-push-tool
Copy-Item safe-git-push/windows/safe_git_push.py ~/git-push-tool/
# PowerShell プロファイル ($PROFILE) に以下を追加:
function gitpush { python "$HOME/git-push-tool/safe_git_push.py" }
```

アンインストール:

```powershell
irm https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/windows/uninstall.ps1 | iex
```

## 使い方

```powershell
gitpush
```

対話式に進みます（Linux 版と同じフロー）:

1. 言語選択（日本語 / English）
2. `.gitignore` の確認・生成
3. `.env` のスキャン → `.env.example` 生成
4. ソース内の秘密リテラル / 機密ファイルのスキャン（警告 + y/N）
5. `.gitignore` ギャップチェック（不足パターンを警告し追加を提案）
6. リポジトリ名と公開設定（Public / Private）の入力
7. `git init` / `remote add` / `branch -M main`
8. `git add .` / `commit` まで実行
9. dry-run プレビュー（`git diff --stat`）
10. `GitHub にプッシュしますか？ [y/N]` で `y` のみプッシュ

## 非対話モード

```powershell
gitpush --yes --public --repo my-repo --message "Initial commit"
```

## 依存

- Python 3.7 以上（PATH に `python` が通っていること）
- `colorama`（初回起動時に自動インストール）
- `git`（PATH に通っていること）
- `gh` CLI（GitHub 自動作成を使う場合）
- `glab` CLI（GitLab 自動作成を使う場合）

## GitHub トークンの作り方

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Note 入力、Expiration は No expiration、scopes は `repo` にチェック
4. Generate token で `ghp_...` をコピー
5. `~/githubtoken.env` に `set GITHUB_TOKEN=ghp_...` と書く（またはシステム環境変数に設定）
6. `githubtoken.env` は `.gitignore` で除外済みなので push されません

`gh` での自動作成を使う場合は `gh auth login` も実行してください。

## 高度な機能（自動化 / v1.2.0）

プロジェクトに `gitpush.toml` を置くとデフォルト動作を変えられます:

```toml
default_visibility = "private"
default_branch = "main"
token_env = "GITHUB_TOKEN"
auto_hook = true
auto_ci = true
self_update = true
expected_remote = "ASDF3001"

# v1.2.0 新機能
scan_secrets = true
warn_secret_files = true
scan_history = false
check_gitignore_gap = true
dry_run = true
default_message = "Initial commit"
branch_pattern = ""
extra_remotes = []
update_channel = "stable"
provider = "github"
log_file = "gitpush.log"
```

自動で行われること:

1. **pre-commit フック登録** — `.env` やトークン (`ghp_...`) がコミットされるのをブロック
2. **CI ワークフロー生成** — `.github/workflows/secret-scan.yml`（gitleaks）
3. **リモート警告** — 予期しないリモートへの push を警告
4. **自己更新** — 起動時に最新版と比較し更新を提案（`update_channel` で stable/beta）
5. **秘密スキャン** — ソース内リテラル / 機密ファイル / 過去履歴
6. **マルチリモート push** — `extra_remotes` に列挙したリモートへ一斉 push
7. **ログ出力** — `log_file` に実行履歴を追記

### グローバル設定

`~/.config/gitpush.toml` を置くと全プロジェクト共通のデフォルトが適用されます（プロジェクト設定優先）。

### GitLab 対応

`provider = "gitlab"` を設定し `glab auth login` を済ませると `glab` で自動作成します。

exe の場合も `gitpush.toml` は同じように機能します（exe と同じフォルダ、またはカレントディレクトリに置く）。

