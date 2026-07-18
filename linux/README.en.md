# Safe Git Push (Linux / macOS)

The Linux / macOS version of the CLI tool to push to GitHub safely.

## Install

One-liner (recommended):

```sh
curl -fsSL https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/linux/install.sh | bash
```

Then activate:

```sh
source ~/.zshrc    # for zsh (use ~/.bashrc for bash)
# or open a new terminal
```

Manual:

```sh
git clone https://github.com/ASDF3001/safe-git-push.git
mkdir -p ~/git-push-tool
cp safe-git-push/linux/safe_git_push.py ~/git-push-tool/
echo "alias gitpush='python3 \$HOME/git-push-tool/safe_git_push.py'" >> ~/.zshrc
source ~/.zshrc
```

## Usage

```sh
gitpush
```

Interactive flow:

1. Language selection (Japanese / English)
2. Check / create `.gitignore`
3. Scan `.env` and generate `.env.example`
4. Enter repository name and visibility (Public / Private)
5. `git init` / `remote add` / `branch -M main`
6. `git add .` / `commit`
7. `Push to GitHub? [y/N]` — only `y` pushes

## Requirements

- Python 3.7+
- `colorama` (auto-installed on first run)
- `git` (required)
- `gh` CLI (for auto repo creation; URL entry works without it)

## Making a GitHub token

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Note, Expiration = No expiration, check `repo` scope
4. Generate token, copy `ghp_...`
5. Save to `~/githubtoken.env` as `export GITHUB_TOKEN=ghp_...`
6. `githubtoken.env` is gitignored, so it will not be pushed

For `gh` auto-creation, also run `gh auth login`.

## Advanced features (automation)

Place a `gitpush.toml` config file in your project to change defaults:

```toml
default_visibility = "private"   # initial repo visibility (public/private)
default_branch = "main"          # default branch name
token_env = "GITHUB_TOKEN"       # env var name to read
auto_hook = true                 # auto-register pre-commit hook
auto_ci = true                   # auto-generate GitHub Actions secret-scan
self_update = true               # self-update check on launch
expected_remote = "ASDF3001"     # warn if remote URL lacks this string
```

Automatically performed:

1. **pre-commit hook** — blocks commits containing `.env` or tokens (`ghp_...`)
2. **CI workflow** — creates `.github/workflows/secret-scan.yml` (gitleaks scans secrets on push)
3. **Remote warning** — warns if pushing to a remote not matching `expected_remote`
4. **Self-update** — compares with the latest GitHub version on launch and offers to update

