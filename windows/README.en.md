# Safe Git Push (Windows)

The Windows version of the CLI tool to push to GitHub safely.

## Install

### A. Executable (exe)

Download `windows/gitpush.exe` and place it in any folder. No Python install needed.

```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/windows/gitpush.exe -OutFile gitpush.exe
.\gitpush.exe
```

Note: this exe was built on Linux (wine + PyInstaller). It has not been tested on a real Windows machine, so please report any issues via Issues.

### B. PowerShell one-liner (Python version)

```powershell
irm https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/windows/install.ps1 | iex
```

Then open a new PowerShell window, or run:

```powershell
. $PROFILE
```

### C. Manual (Python version)

```powershell
git clone https://github.com/ASDF3001/safe-git-push.git
New-Item -ItemType Directory -Force -Path ~/git-push-tool
Copy-Item safe-git-push/windows/safe_git_push.py ~/git-push-tool/
# Add to your PowerShell profile ($PROFILE):
function gitpush { python "$HOME/git-push-tool/safe_git_push.py" }
```

## Usage

```powershell
gitpush
```

Interactive flow (same as Linux version):

1. Language selection (Japanese / English)
2. Check / create `.gitignore`
3. Scan `.env` and generate `.env.example`
4. Enter repository name and visibility (Public / Private)
5. `git init` / `remote add` / `branch -M main`
6. `git add .` / `commit`
7. `Push to GitHub? [y/N]` — only `y` pushes

## Requirements

- Python 3.7+ (on PATH as `python`)
- `colorama` (auto-installed on first run)
- `git` (on PATH)
- `gh` CLI (for auto repo creation)

## Making a GitHub token

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Note, Expiration = No expiration, check `repo` scope
4. Generate token, copy `ghp_...`
5. Save to `~/githubtoken.env` as `set GITHUB_TOKEN=ghp_...` (or set as system env var)
6. `githubtoken.env` is gitignored, so it will not be pushed

For `gh` auto-creation, also run `gh auth login`.

## Advanced features (automation)

Place `gitpush.toml` in your project to change defaults:

```toml
default_visibility = "private"
default_branch = "main"
token_env = "GITHUB_TOKEN"
auto_hook = true
auto_ci = true
self_update = true
expected_remote = "ASDF3001"
```

Automatically performed:

1. **pre-commit hook** — blocks commits with `.env` or tokens
2. **CI workflow** — `.github/workflows/secret-scan.yml` (gitleaks)
3. **Remote warning** — warns on unexpected remote push
4. **Self-update** — compares with latest version on launch

The exe also reads `gitpush.toml` (placed next to the exe or in the current directory).

