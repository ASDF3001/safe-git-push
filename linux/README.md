# Safe Git Push (Linux / macOS)

機密情報を守りながら安全に GitHub / GitLab へプッシュする CLI ツールの Linux / macOS 版です。

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

アンインストール:

```sh
curl -fsSL https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/linux/uninstall.sh | bash
```

## 使い方

```sh
gitpush
```

対話式に進みます:

1. 言語選択（日本語 / English）
2. `.gitignore` の確認・生成
3. `.env` のスキャン → `.env.example` 生成
4. ソース内の秘密リテラル / 機密ファイルのスキャン（警告 + y/N）
5. `.gitignore` ギャップチェック（不足パターンを警告し追加を提案）
6. リポジトリ名と公開設定（Public / Private）の入力
7. `git init` / `remote add` / `branch -M main`
8. `git add .` / `commit` まで実行
9. dry-run プレビュー（`git diff --stat`）
10. `プッシュしますか？ [y/N]` で `y` のみプッシュ

## 非対話モード

CI や自動化向けに引数で一発実行できます:

```sh
gitpush --yes --public --repo my-repo --message "Initial commit"
#   --yes       すべて y で進める
#   --public    / --private  公開設定
#   --repo NAME リポジトリ名
#   --message M コミットメッセージ
#   --lang ja|en  言語固定
```

## 依存

- Python 3.7 以上
- `colorama`（初回起動時に自動インストール）
- `git`（必須）
- `gh` CLI（GitHub 自動作成を使う場合。無くても URL 手入力で動きます）
- `glab` CLI（GitLab 自動作成を使う場合）

## GitHub トークンの作り方

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Note 入力、Expiration は No expiration（永久）、scopes は `repo` にチェック
4. Generate token で `ghp_...` をコピー
5. `~/githubtoken.env` に `export GITHUB_TOKEN=ghp_...` と書く
6. `githubtoken.env` は `.gitignore` で除外済みなので push されません

`gh` での自動作成を使う場合は `gh auth login` も実行してください。

## 高度な機能（自動化 / v1.2.0）

設定ファイル `gitpush.toml` をプロジェクトに置くと、デフォルト動作を変えられます:

```toml
default_visibility = "private"   # リポジトリの初期公開設定 (public/private)
default_branch = "main"          # デフォルトブランチ名
token_env = "GITHUB_TOKEN"       # 読み込む環境変数名
auto_hook = true                 # pre-commit フックを自動登録
auto_ci = true                   # GitHub Actions の secret-scan を自動生成
self_update = true               # 起動時に自分自身を自動更新
expected_remote = "ASDF3001"     # この文字列がリモートURLに無ければ警告

# v1.2.0 新機能
scan_secrets = true             # ソース内の秘密リテラルをスキャン
warn_secret_files = true        # .pem/.key 等の機密ファイルを警告
scan_history = false            # 過去のコミット履歴もスキャン (重い/デフォルトoff)
check_gitignore_gap = true      # .gitignore の不足パターンを警告
dry_run = true                  # push 前に git diff --stat をプレビュー
default_message = "Initial commit"  # デフォルトのコミットメッセージ
branch_pattern = ""             # ブランチ自動命名 (例: "feature/%Y%m%d") 空=off
extra_remotes = []              # 一斉 push する追加リモート名
update_channel = "stable"       # stable | beta
provider = "github"             # github | gitlab
log_file = "gitpush.log"        # ログ出力先 (空=出力しない)
```

自動で行われること:

1. **pre-commit フック登録** — `.env` やトークン (`ghp_...`) がコミットされようとしたらブロック
2. **CI ワークフロー生成** — `.github/workflows/secret-scan.yml` を作成（gitleaks でプッシュ時に秘密をスキャン）
3. **リモート警告** — `expected_remote` と異なるリモートへ push しようとすると警告
4. **自己更新** — 起動時に GitHub 上の最新版と比較し、新しければ更新を提案（`update_channel` で stable/beta 選択）
5. **秘密スキャン** — ソース内リテラル / 機密ファイル / 過去履歴（設定で切替）をスキャン
6. **マルチリモート push** — `extra_remotes` に列挙したリモートへ一斉 push
7. **ログ出力** — `log_file` に実行履歴を追記

### グローバル設定

`~/.config/gitpush.toml` を置くと、すべてのプロジェクトに共通のデフォルトが適用されます。
プロジェクトの `gitpush.toml` がある場合はそちらが優先されます（マージ）。

### GitLab 対応

`provider = "gitlab"` を設定し、`glab auth login` を済ませておくと、リポジトリ自動作成に `glab` を使います。

### Docker

```sh
docker build -t safe-git-push .
docker run --rm -v "$PWD:/work" -w /work safe-git-push --yes --public --repo my-repo
```
