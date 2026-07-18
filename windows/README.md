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
4. ソース内の秘密リテラル / 機密ファイルのスキャン（警告のみ。問題があれば最後のプッシュ確認でまとめて y/N）
5. `.gitignore` ギャップチェック（不足パターンを警告し追加を提案）
6. リポジトリ選択 — GitHub API で既存リポジトリ一覧を表示し、数字で選択 / `0` で新規作成 / `q` で終了。公開設定（Public / Private）は番号で選択
7. `git init` / `remote add` / `branch -M main`
8. `git add .` / `commit` まで実行
9. dry-run プレビュー（`git diff --stat`）
10. `GitHub にプッシュしますか？ [y/N]` で `y` のみプッシュ（メニューでの `q` 入力はこの確認には影響しません）

メニュー操作の共通ルール: 番号で選択、`q` でキャンセル終了。`q` は y/N プロンプトや自由入力には反応しません。

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

> ⚠️ **トークンは必ず GitHub で発行し、自分で管理してください。平文で共有・コミットしないでください。**

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **Generate new token (classic)** を選ぶ
3. Note を入力、Expiration はお好み（例: 90 days）
4. **Scopes（権限）に必ず以下の両方にチェックを入れる**:
   - ✅ `repo` （リポジトリの読み書き — プッシュに必要）
   - ✅ `workflow` （`.github/workflows/*.yml` を push するために**必須**。これが無いと push が拒否されます）
5. Generate token で `ghp_...` をコピー

ツールを起動すると **毎回トークン入力を求められます**（環境変数や保存値は使いません）。
入力したトークンは **`~/.config/gitpush.toml`（プロジェクト外）のみ** に保存され、プロジェクトの `gitpush.toml` には書き込まれません（pre-commit フックに検出されるのを防ぐため）。
`gh` でのリポジトリ自動作成もこの入力トークンを使うため、`gh auth login` は不要です。

> 💡 `workflow` スコープを忘れると、CI ワークフローファイルを含む push が
> `refusing to allow a Personal Access Token to create or update workflow ... without 'workflow' scope`
> で拒否されます。その場合はトークンに `workflow` を追加するか、`auto_ci = false` にしてください。

## 高度な機能（自動化 / v1.2.0）

設定はすべて `gitpush.toml`（プロジェクト + グローバル `~/.config/gitpush.toml`）で管理します。対話式の設定メニューは廃止しました。
**トークンはプロジェクトの `gitpush.toml` には書かず、常にグローバル設定か都度入力で管理してください。**

プロジェクトに `gitpush.toml` を置くとデフォルト動作を変えられます:

```toml
default_visibility = "private"
default_branch = "main"
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

