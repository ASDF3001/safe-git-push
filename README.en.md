# Safe Git Push

An interactive CLI tool to push code to GitHub safely, while protecting sensitive data (`.env` files, session logs, AI agent configs).

When developing with AI agents, there is a risk of accidentally pushing session logs or `.env` files to a public repository. This tool automatically maintains `.gitignore` and masks `.env` values before pushing.

## Directory layout

- `linux/` — scripts and installer for Linux / macOS
- `windows/` — scripts and installer for Windows

Open the folder for your OS and follow its README.

## Features

1. Auto-generate `.gitignore` (excludes `.env`, `__pycache__/`, `.roo/`, `.aider/`, `.qwen/`, etc.)
2. Scan `.env` and generate `.env.example` with masked values
3. Auto-create repository (public / private, via `gh`)
4. Set up GitHub remote (`git init` / `remote add` / `branch -M main`)
5. Confirm before push (only `y` runs `git push`)

## About Updating

A `gitpush update` command may be implemented in the future to easily update the tool.
If your version of `gitpush` supports the `gitpush update` command, you can simply run it to update.

**If you do not have the `gitpush update` command:**
Currently, `gitpush` has a self-update feature that checks for the latest version on launch (when `self_update = true` in `gitpush.toml`). 
When an update is available, you will be prompted to update. Simply typing `y` will update the tool automatically.

If you want to update manually, you can run `git pull` on this repository again or re-run the installer (`install.sh` or `install.ps1`) to overwrite the existing scripts.

## Language

Choose Japanese / English at startup.

## License
[MIT LICENSE](./LICENSE)
Free to use.
