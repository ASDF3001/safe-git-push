# Safe Git Push (Windows)

機密情報を守りながら安全に GitHub へプッシュする CLI ツールの Windows 版です。

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

## 使い方

```powershell
gitpush
```

対話式に進みます（Linux 版と同じフロー）:

1. 言語選択（日本語 / English）
2. `.gitignore` の確認・生成
3. `.env` のスキャン → `.env.example` 生成
4. リポジトリ名と公開設定（Public / Private）の入力
5. `git init` / `remote add` / `branch -M main`
6. `git add .` / `commit` まで実行
7. `GitHub にプッシュしますか？ [y/N]` で `y` のみプッシュ

## 依存

- Python 3.7 以上（PATH に `python` が通っていること）
- `colorama`（初回起動時に自動インストール）
- `git`（PATH に通っていること）
- `gh` CLI（リポジトリ自動作成を使う場合）

## GitHub トークンの作り方

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Note 入力、Expiration は No expiration、scopes は `repo` にチェック
4. Generate token で `ghp_...` をコピー
5. `~/githubtoken.env` に `set GITHUB_TOKEN=ghp_...` と書く（またはシステム環境変数に設定）
6. `githubtoken.env` は `.gitignore` で除外済みなので push されません

`gh` での自動作成を使う場合は `gh auth login` も実行してください。
