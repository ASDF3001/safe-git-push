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
4. Scan source for secret literals / secret files (warnings only; bundled into the final push confirmation if issues found)
5. `.gitignore` gap check (warn and offer to append missing patterns)
6. Repository selection — GitHub API lists existing repos; pick by number / `0` for new / `q` to quit. Visibility (Public / Private) by number
7. `git init` / `remote add` / `branch -M main`
8. `git add .` / `commit`
9. Dry-run preview (`git diff --stat`)
10. `Push to GitHub? [y/N]` — only `y` pushes (typing `q` in a menu does not affect this prompt)

Menus: pick by number, `q` cancels/exits. `q` does not respond in y/N prompts or free-text inputs.

## Requirements

- Python 3.7+ (on PATH as `python`)
- `colorama` (auto-installed on first run)
- `git` (on PATH)
- `gh` CLI (for auto repo creation)

## Making a GitHub token

> ⚠️ **Always create the token yourself on GitHub and keep it secret. Never share or commit it in plaintext.**

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Choose **Generate new token (classic)**
3. Enter a Note, set Expiration as you like (e.g. 90 days)
4. **Check BOTH scopes**:
   - ✅ `repo` (read/write repos — required to push)
   - ✅ `workflow` (**required** to push `.github/workflows/*.yml`; without it, push is rejected)
5. Generate token, copy `ghp_...`

The tool **prompts for the token on every run** (environment variables and saved values are not used). The entered token is saved only to **`~/.config/gitpush.toml` (outside the project)**, never to the project's `gitpush.toml` (so the pre-commit hook won't flag it). `gh` auto-creation also uses this entered token, so `gh auth login` is not required.

> 💡 Forgetting the `workflow` scope causes push to be rejected with
> `refusing to allow a Personal Access Token to create or update workflow ... without 'workflow' scope`.
> Add `workflow` to the token, or set `auto_ci = false`.

## Advanced features (automation)

All settings live in `gitpush.toml` (project + global `~/.config/gitpush.toml`). The interactive settings menu has been removed.
**Never put the token in the project's `gitpush.toml`; manage it via global config or per-run input.**

Place `gitpush.toml` in your project to change defaults:

```toml
default_visibility = "private"
default_branch = "main"
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

