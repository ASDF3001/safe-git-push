# Safe Git Push (`safe-git-push`)

機密情報（`.env`、セッションログ、AIエージェントの設定など）を守りながら、
**安全に GitHub へプッシュ・公開**するためのインタラクティブ CLI ツールです。

> AI エージェントを使って開発していると、セッションログや `.env` が
> うっかりパブリックリポジトリに push されてしまうリスクがあります。
> このツールは push 前に `.gitignore` の整備と `.env` のダミー化を自動で行います。

---

## 主な機能

1. **`.gitignore` の自動生成**
   - 存在しない場合、機密ファイルを除外する `.gitignore` を作成
   - デフォルト除外: `.env`, `__pycache__/`, `.roo/`, `.aider/`, `.qwen/`, `.cursor/` など
2. **`.env` の自動スキャン → `.env.example` 生成**
   - `.env` のキーを読み取り、値をダミーにした `.env.example` を作成
   - 例: `TOKEN=xyz123` → `TOKEN=your_token_here`
3. **リポジトリの自動作成（public / private 選択式）**
   - `gh` が認証されていれば、リポジトリ名と公開設定を選ぶだけで `gh repo create` を実行
   - `gh` が無い / 未認証の場合は、既存のリポジトリ URL を手入力することも可能
4. **GitHub リモート URL の対話入力**
   - `git init` → `git remote add origin <URL>` → `git branch -M main` を自動実行
5. **プッシュ前の確認**
   - `git add .` → `git commit -m "Initial commit"` まで実行
   - `GitHub にプッシュしますか？ [y/N]` で `y` のときのみ `git push -u origin main`

---

## 使い方

### ワンライナーでインストール（推奨）

以下のコマンド一発で、`safe_git_push.py` のダウンロードと `gitpush` エイリアスの登録が完了します:

```sh
curl -fsSL https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/install.sh | bash
```

実行後、以下のどれかで有効化してください:

```sh
source ~/.zshrc    # 現在のターミナルですぐ使う（zsh の場合）
# または新しいターミナルを開く
```

これで `gitpush` と打つだけで起動します。

```sh
gitpush
```

### 手動インストール

1. このリポジトリをクローン（または `safe_git_push.py` をダウンロード）:

```sh
git clone https://github.com/ASDF3001/safe-git-push.git ~/git-push-tool
```

2. `~/.zshrc`（または `~/.bashrc`）にエイリアスを追加:

```sh
echo "alias gitpush='python3 \$HOME/git-push-tool/safe_git_push.py'" >> ~/.zshrc
source ~/.zshrc
```

### 直接実行(linuxの場合)

```sh
python3 ~/git-push-tool/safe_git_push.py
```

---

## 言語

起動時に `1. 日本語` / `2. English` を選択できます。
すべてのメッセージとプロンプトが選択した言語で表示されます。

---

## CUI デザイン

ネオン / サイバー風のカラーテーマ（マゼンタ・シアン）で、
見やすくてかっこいい出力になっています。

---

## GitHub トークンの作り方

このツールは **あなた自身の GitHub アカウント** でリポジトリを作成・push します。
そのために、あなた専用の Personal Access Token（以下 PAT）を作ってください。
**トークンは他人に教えないでください。**

### 手順

1. GitHub にログインし、右上のアイコン → **Settings** を開く
2. 左メニュー一番下の **Developer settings** をクリック
3. **Personal access tokens** → **Tokens (classic)** をクリック
4. **Generate new token** → **Generate new token (classic)** をクリック
5. 設定項目:
   - **Note**: わかりやすい名前（例: `safe-git-push`）
   - **Expiration**: **No expiration**（永久に使う場合＝おすすめだが自己責任で）
   - **Select scopes**: **`repo`** の左のボックスにチェックを入れる（すべての `repo` 配下にチェックが入ります）
6. 一番下の **Generate token** をクリック
7. 表示された `ghp_xxxxxxxxxxxx` を **すぐコピー** する（あとから見れません）

### トークンを保存する

ホームディレクトリに `githubtoken.env` を作り、以下のように書きます:

```sh
export GITHUB_TOKEN=ghp_ここにコピーしたトークン
```

```sh
# 例: コマンドで作成する場合
echo 'export GITHUB_TOKEN=ghp_xxxxxxxxxxxx' > ~/githubtoken.env
```

> `githubtoken.env` は **絶対に Git に入れないでください**。
> このツールが生成する `.gitignore` には `.env` が含まれているので、
> `githubtoken.env` という名前にしておけば誤って push されることはありません。

### `gh` を認証する（リポジトリ自動作成を使う場合）

リポジトリを「public / private 選択式で自動作成」したい場合は、`gh` にもトークンを覚えさせます:

```sh
gh auth login
```

聞かれたら:
- `GitHub.com` を選択
- `HTTPS` を選択
- `Paste an authentication token` を選択
- さっき作ったトークン `ghp_...` を貼り付け

認証できると、`gitpush` 実行時にリポジトリ名と公開設定を選ぶだけで自動作成されます。

---

## 依存関係

- Python 3.7 以上
- `colorama`（自動インストールされます）
- `gh` CLI（リポジトリ自動作成を使う場合。無くても URL 手入力で動きます）

初回起動時に `colorama` が無い場合、スクリプトが自動で
`pip install --user colorama`（失敗時は `--break-system-packages`）を試みます。
そのため、このリポジトリを `git clone` した後も追加手順なしで動作します。

---

## ファイル構成

```
git-push-tool/
├── safe_git_push.py   # メインスクリプト
└── README.md          # このファイル
```

---

## 注意

- このツールは「初回の安全な push」を補助するものです。
  push 前には必ず `git status` / `git diff` で内容を確認してください。
- `.env.example` のダミー化は単純なルールベースです。
  機密値がそのまま残っていないか、生成後に目視で確認することをおすすめします。
- トークン（PAT）は誰にも見せず、漏洩時は GitHub の設定から即座に Revoke してください。
