# Safe Git Push (Linux / macOS)

機密情報を守りながら安全に GitHub へプッシュする CLI ツールの Linux / macOS 版です。

## インストール

ワンライナー（推奨）:

```sh
curl -fsSL https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/linux/install.sh | bash
```

実行後、以下で有効化:

```sh
source ~/.zshrc    # zsh の場合（bash なら ~/.bashrc）
# または新しいターミナルを開く
```

手動:

```sh
git clone https://github.com/ASDF3001/safe-git-push.git
mkdir -p ~/git-push-tool
cp safe-git-push/linux/safe_git_push.py ~/git-push-tool/
echo "alias gitpush='python3 \$HOME/git-push-tool/safe_git_push.py'" >> ~/.zshrc
source ~/.zshrc
```

## 使い方

```sh
gitpush
```

対話式に進みます:

1. 言語選択（日本語 / English）
2. `.gitignore` の確認・生成
3. `.env` のスキャン → `.env.example` 生成
4. リポジトリ名と公開設定（Public / Private）の入力
5. `git init` / `remote add` / `branch -M main`
6. `git add .` / `commit` まで実行
7. `GitHub にプッシュしますか？ [y/N]` で `y` のみプッシュ

## 依存

- Python 3.7 以上
- `colorama`（初回起動時に自動インストール）
- `git`（必須）
- `gh` CLI（リポジトリ自動作成を使う場合。無くても URL 手入力で動きます）

## GitHub トークンの作り方

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Note 入力、Expiration は No expiration（永久）、scopes は `repo` にチェック
4. Generate token で `ghp_...` をコピー
5. `~/githubtoken.env` に `export GITHUB_TOKEN=ghp_...` と書く
6. `githubtoken.env` は `.gitignore` で除外済みなので push されません

`gh` での自動作成を使う場合は `gh auth login` も実行してください。

## 高度な機能（自動化）

設定ファイル `gitpush.toml` をプロジェクトに置くと、デフォルト動作を変えられます:

```toml
default_visibility = "private"   # リポジトリの初期公開設定 (public/private)
default_branch = "main"          # デフォルトブランチ名
token_env = "GITHUB_TOKEN"       # 読み込む環境変数名
auto_hook = true                 # pre-commit フックを自動登録
auto_ci = true                   # GitHub Actions の secret-scan を自動生成
self_update = true               # 起動時に自分自身を自動更新
expected_remote = "ASDF3001"     # この文字列がリモートURLに無ければ警告
```

自動で行われること:

1. **pre-commit フック登録** — `.env` やトークン (`ghp_...`) がコミットされようとしたらブロック
2. **CI ワークフロー生成** — `.github/workflows/secret-scan.yml` を作成（gitleaks でプッシュ時に秘密をスキャン）
3. **リモート警告** — `expected_remote` と異なるリモートへ push しようとすると警告
4. **自己更新** — 起動時に GitHub 上の最新版と比較し、新しければ更新を提案

