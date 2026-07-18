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
