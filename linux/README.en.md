# Safe Git Push (Linux / macOS)

The Linux / macOS version of the CLI tool to push to GitHub / GitLab safely.

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

Uninstall:

```sh
curl -fsSL https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/linux/uninstall.sh | bash
```

## Usage

```sh
gitpush
```

Interactive flow:

1. Language selection (Japanese / English)
2. Check / create `.gitignore`
3. Scan `.env` and generate `.env.example`
4. Scan source for secret literals / secret files (warnings only; if issues found, they are bundled into the final push confirmation)
5. `.gitignore` gap check (warn and offer to append missing patterns)
6. Repository selection — GitHub API lists existing repos; pick by number / `0` for new / `q` to quit. Visibility (Public / Private) by number
7. `git init` / `remote add` / `branch -M main`
8. `git add .` / `commit`
9. Dry-run preview (`git diff --stat`)
10. `Push? [y/N]` — only `y` pushes (typing `q` in a menu does not affect this prompt)

Menus: pick by number, `q` cancels/exits. `q` does not respond in y/N prompts or free-text inputs.

## Non-interactive mode

For CI / automation, run in one shot:

```sh
gitpush --yes --public --repo my-repo --message "Initial commit"
#   --yes         answer y to everything
#   --public      / --private   visibility
#   --repo NAME   repository name
#   --message M   commit message
#   --lang ja|en  fix language
```

## Requirements

- Python 3.7+
- `colorama` (auto-installed on first run)
- `git` (required)
- `gh` CLI (for GitHub auto repo creation; URL entry works without it)
- `glab` CLI (for GitLab auto repo creation)

## Making a GitHub token

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Note, Expiration = No expiration, check `repo` scope
4. Generate token, copy `ghp_...`

The tool **prompts for the token on every run** (environment variables and saved values are not used). The entered token is saved to the project's `gitpush.toml` for reuse. `gh` auto-creation also uses this entered token, so `gh auth login` is not required.

## Advanced features (automation / v1.2.0)

All settings live in `gitpush.toml` (project + global `~/.config/gitpush.toml`). The interactive settings menu has been removed.

Place a `gitpush.toml` config file in your project to change defaults:

```toml
default_visibility = "private"   # initial repo visibility (public/private)
default_branch = "main"          # default branch name
auto_hook = true                 # auto-register pre-commit hook
auto_ci = true                   # auto-generate GitHub Actions secret-scan
self_update = true               # self-update check on launch
expected_remote = "ASDF3001"     # warn if remote URL lacks this string

# v1.2.0 new features
scan_secrets = true             # scan source for secret literals
warn_secret_files = true        # warn on .pem/.key etc.
scan_history = false            # also scan past commits (heavy / off by default)
check_gitignore_gap = true      # warn on missing .gitignore patterns
dry_run = true                  # preview git diff --stat before push
default_message = "Initial commit"  # default commit message
branch_pattern = ""             # auto branch naming (e.g. "feature/%Y%m%d") empty=off
extra_remotes = []              # extra remotes to push to in bulk
update_channel = "stable"       # stable | beta
provider = "github"             # github | gitlab
log_file = "gitpush.log"        # log output file (empty = no log)
```

Automatically performed:

1. **pre-commit hook** — blocks commits containing `.env` or tokens (`ghp_...`)
2. **CI workflow** — creates `.github/workflows/secret-scan.yml` (gitleaks scans secrets on push)
3. **Remote warning** — warns if pushing to a remote not matching `expected_remote`
4. **Self-update** — compares with the latest GitHub version on launch (`update_channel` picks stable/beta)
5. **Secret scanning** — scans source literals / secret files / history (toggle in config)
6. **Multi-remote push** — pushes to every remote listed in `extra_remotes`
7. **Logging** — appends run history to `log_file`

### Global config

Place `~/.config/gitpush.toml` to apply shared defaults across all projects.
If a project `gitpush.toml` exists, it takes precedence (merged).

### GitLab support

Set `provider = "gitlab"` and run `glab auth login`; auto repo creation uses `glab`.

### Docker

```sh
docker build -t safe-git-push .
docker run --rm -v "$PWD:/work" -w /work safe-git-push --yes --public --repo my-repo
```
