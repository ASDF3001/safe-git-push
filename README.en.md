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

You can easily update the tool to the latest version by running the `gitpush update` command.
If a new version is detected upon launch, a warning will be displayed. When you see this, run the command to update.

If you want to update manually or if the command fails, you can run `git pull` on this repository again or re-run the installer (`install.sh` or `install.ps1`) to overwrite the existing scripts.

## Language

Choose Japanese / English at startup.

## License
[MIT LICENSE](./LICENSE)
Free to use.
