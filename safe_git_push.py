#!/usr/bin/env python3
"""
Safe Git Push - 安全にGitHubへプッシュするためのインタラクティブCLIツール
Interactive CLI tool to safely push code to GitHub
"""  

# このスクリプトは `git-push-tool/` フォルダに保存されています
# This script is saved in the `git-push-tool/` folder

import os
import sys
import subprocess
import shlex
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def ensure_colorama():
    """colorama が無ければ自動で pip install する（パブリックリポジトリでも即動作）"""
    try:
        import colorama  # noqa: F401
        return
    except ImportError:
        pass
    # 自動インストールを試みる
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", "--user", "colorama"]
        )
    except subprocess.CalledProcessError:
        # --user が効かない環境（PEP 668 等）は --break-system-packages で再挑戦
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--quiet",
                 "--break-system-packages", "colorama"]
            )
        except subprocess.CalledProcessError:
            pass


ensure_colorama()

try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
except ImportError:
    # Fallback if colorama still unavailable
    class Fore:
        CYAN = MAGENTA = YELLOW = GREEN = RED = BLUE = WHITE = RESET = ""
    class Back:
        BLACK = RESET = ""
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ""

# ============================================================================
# Language / 言語設定
# ============================================================================
TEXTS = {
    "ja": {
        "title": "🛡️  Safe Git Push へようこそ！",
        "subtitle": "機密情報を守りながら GitHub へプッシュします",
        "lang_prompt": "言語を選択してください / Select language:",
        "lang_options": ["1. 日本語", "2. English"],
        "lang_selected": "日本語を選択しました",
        "gitignore_created": "✅ .gitignore を作成しました",
        "gitignore_exists": "ℹ️  .gitignore は既に存在します",
        "env_found": "📄 .env ファイルが見つかりました",
        "env_not_found": "ℹ️  .env ファイルが見つかりません（スキップ）",
        "env_example_created": "✅ .env.example を生成しました",
        "repo_url_prompt": "GitHub リポジトリの URL を入力してください (例: https://github.com/user/repo.git)",
        "repo_url_empty": "❌ URL は必須です",
        "repo_name_prompt": "作成するリポジトリ名を入力してください",
        "repo_name_empty": "❌ リポジトリ名は必須です",
        "repo_visibility_prompt": "リポジトリの公開設定を選択してください",
        "repo_visibility_options": ["1. Public（世界に公開）", "2. Private（非公開）"],
        "repo_creating": "🌐 GitHub にリポジトリを作成しています...",
        "repo_created": "✅ リポジトリを作成しました",
        "repo_create_failed": "⚠️  リポジトリの自動作成に失敗しました（URLを手入力できます）",
        "gh_missing": "ℹ️  gh が見つからないか未認証です。URLを直接入力してください",
        "auth_note": "💡 自分のトークンで自動作成したい場合: gh auth login を実行してください",
        "branch_prompt": "ブランチ名を入力してください [main]",
        "git_init": "🔧 Git リポジトリを初期化しています...",
        "git_remote_add": "🔗 リモートを追加しています...",
        "git_branch_rename": "🌿 ブランチ名を変更しています...",
        "git_add": "📦 ファイルをステージングしています...",
        "git_commit": "💾 コミットを作成しています...",
        "push_confirm": "🚀 GitHub にプッシュしますか？ [y/N]:",
        "push_cancelled": "⏸️  プッシュをキャンセルしました",
        "pushing": "⬆️  プッシュしています...",
        "push_success": "✅ プッシュが完了しました！",
        "push_failed": "❌ プッシュに失敗しました",
        "error_git_not_found": "❌ git が見つかりません。インストールしてください。",
        "error_not_git_repo": "❌ ここは Git リポジトリではありません。",
        "done": "🎉 完了！",
        "press_enter": "Enter キーで終了...",
    },
    "en": {
        "title": "🛡️  Welcome to Safe Git Push!",
        "subtitle": "Push to GitHub while protecting sensitive data",
        "lang_prompt": "Select language / 言語を選択してください:",
        "lang_options": ["1. 日本語", "2. English"],
        "lang_selected": "English selected",
        "gitignore_created": "✅ Created .gitignore",
        "gitignore_exists": "ℹ️  .gitignore already exists",
        "env_found": "📄 Found .env file",
        "env_not_found": "ℹ️  No .env file found (skipping)",
        "env_example_created": "✅ Generated .env.example",
        "repo_url_prompt": "Enter GitHub repository URL (e.g., https://github.com/user/repo.git)",
        "repo_url_empty": "❌ URL is required",
        "repo_name_prompt": "Enter the repository name to create",
        "repo_name_empty": "❌ Repository name is required",
        "repo_visibility_prompt": "Select repository visibility",
        "repo_visibility_options": ["1. Public (open to the world)", "2. Private (hidden)"],
        "repo_creating": "🌐 Creating repository on GitHub...",
        "repo_created": "✅ Repository created",
        "repo_create_failed": "⚠️  Failed to auto-create repo (you can enter URL manually)",
        "gh_missing": "ℹ️  gh not found or not authenticated. Enter URL directly",
        "auth_note": "💡 To auto-create with your token, run: gh auth login",
        "branch_prompt": "Enter branch name [main]",
        "git_init": "🔧 Initializing Git repository...",
        "git_remote_add": "🔗 Adding remote...",
        "git_branch_rename": "🌿 Renaming branch...",
        "git_add": "📦 Staging files...",
        "git_commit": "💾 Creating commit...",
        "push_confirm": "🚀 Push to GitHub? [y/N]:",
        "push_cancelled": "⏸️  Push cancelled",
        "pushing": "⬆️  Pushing...",
        "push_success": "✅ Push completed successfully!",
        "push_failed": "❌ Push failed",
        "error_git_not_found": "❌ git not found. Please install git.",
        "error_not_git_repo": "❌ Not a Git repository.",
        "done": "🎉 Done!",
        "press_enter": "Press Enter to exit...",
    }
}

# ============================================================================
# Neon / Cyber Color Theme
# ============================================================================
class Neon:
    TITLE = Fore.MAGENTA + Style.BRIGHT
    SUBTITLE = Fore.CYAN + Style.BRIGHT
    SUCCESS = Fore.GREEN + Style.BRIGHT
    INFO = Fore.CYAN + Style.BRIGHT
    WARNING = Fore.YELLOW + Style.BRIGHT
    ERROR = Fore.RED + Style.BRIGHT
    PROMPT = Fore.MAGENTA + Style.BRIGHT
    INPUT = Fore.WHITE + Style.BRIGHT
    RESET = Style.RESET_ALL
    DIVIDER = Fore.BLUE + "═" * 60 + Style.RESET_ALL
    DIVIDER_THIN = Fore.CYAN + "─" * 60 + Style.RESET_ALL


def print_divider(thin=False):
    print(Neon.DIVIDER_THIN if thin else Neon.DIVIDER)


def print_title(t: Dict[str, str], lang: str):
    print_divider()
    print(f"{Neon.TITLE}  {t['title']}{Neon.RESET}")
    print(f"{Neon.SUBTITLE}  {t['subtitle']}{Neon.RESET}")
    print_divider()


def print_step(msg: str):
    print(f"{Neon.INFO}▶ {msg}{Neon.RESET}")


def print_success(msg: str):
    print(f"{Neon.SUCCESS}✓ {msg}{Neon.RESET}")


def print_warning(msg: str):
    print(f"{Neon.WARNING}⚠ {msg}{Neon.RESET}")


def print_info(msg: str):
    print(f"{Neon.INFO}ℹ {msg}{Neon.RESET}")


def print_error(msg: str):
    print(f"{Neon.ERROR}✗ {msg}{Neon.RESET}")


def prompt_input(prompt: str, default: str = "") -> str:
    if default:
        full_prompt = f"{Neon.PROMPT}{prompt} {Neon.INFO}[{default}]{Neon.PROMPT}: {Neon.INPUT}"
    else:
        full_prompt = f"{Neon.PROMPT}{prompt}{Neon.PROMPT}: {Neon.INPUT}"
    try:
        result = input(full_prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    print(Neon.RESET, end="")
    return result if result else default


def prompt_yes_no(prompt: str, default_no: bool = True) -> bool:
    suffix = " [y/N]" if default_no else " [Y/n]"
    full_prompt = f"{Neon.PROMPT}{prompt}{suffix}: {Neon.INPUT}"
    try:
        result = input(full_prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    print(Neon.RESET, end="")
    if default_no:
        return result in ('y', 'yes')
    else:
        return result not in ('n', 'no')


def press_enter_to_exit(t: Dict[str, str]):
    try:
        input(f"{Neon.INFO}{t['press_enter']}{Neon.RESET}")
    except (EOFError, KeyboardInterrupt):
        pass


def run_command(cmd: List[str], cwd: Optional[Path] = None, capture: bool = False) -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)"""
    try:
        if capture:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, cwd=cwd, text=True)
            return result.returncode, "", ""
    except FileNotFoundError:
        return -1, "", "command not found"
    except Exception as e:
        return -1, "", str(e)


# ============================================================================
# Core Functions
# ============================================================================
DEFAULT_GITIGNORE_PATTERNS = [
    "# Environment variables",
    ".env",
    ".env.local",
    ".env.*.local",
    "",
    "# Python cache",
    "__pycache__/",
    "*.py[cod]",
    "*$py.class",
    "",
    "# AI Agent logs / configs",
    ".roo/",
    ".aider/",
    ".qwen/",
    ".cursor/",
    "",
    "# IDE",
    ".vscode/",
    ".idea/",
    "*.swp",
    "*.swo",
    "",
    "# OS",
    ".DS_Store",
    "Thumbs.db",
]


def ensure_gitignore(project_dir: Path, t: Dict[str, str]) -> bool:
    gitignore_path = project_dir / ".gitignore"
    if gitignore_path.exists():
        print_warning(t["gitignore_exists"])
        return False

    content = "\n".join(DEFAULT_GITIGNORE_PATTERNS) + "\n"
    gitignore_path.write_text(content, encoding="utf-8")
    print_success(t["gitignore_created"])
    return True


def scan_env_and_create_example(project_dir: Path, t: Dict[str, str]) -> bool:
    env_path = project_dir / ".env"
    if not env_path.exists():
        print_warning(t["env_not_found"])
        return False

    print_step(t["env_found"])
    lines = env_path.read_text(encoding="utf-8").splitlines()
    example_lines = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            example_lines.append(line)
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            # Create placeholder based on key name
            placeholder = create_placeholder(key, value.strip())
            example_lines.append(f"{key}={placeholder}")
        else:
            example_lines.append(line)

    example_path = project_dir / ".env.example"
    example_path.write_text("\n".join(example_lines) + "\n", encoding="utf-8")
    print_success(t["env_example_created"])
    return True


def create_placeholder(key: str, value: str) -> str:
    key_lower = key.lower()

    # Common patterns
    if any(kw in key_lower for kw in ["token", "secret", "key", "password", "passwd", "pwd", "auth", "credential"]):
        return f"your_{key_lower}_here"
    if "api" in key_lower:
        return "your_api_key_here"
    if "url" in key_lower or "endpoint" in key_lower:
        return "https://example.com"
    if "host" in key_lower:
        return "localhost"
    if "port" in key_lower:
        return "8080"
    if "db" in key_lower or "database" in key_lower:
        return "your_database_url"
    if "email" in key_lower or "mail" in key_lower:
        return "user@example.com"
    if "user" in key_lower and "name" in key_lower:
        return "your_username"
    if "region" in key_lower:
        return "us-east-1"

    # Generic: keep length but mask
    if len(value) > 20:
        return "your_long_value_here"
    elif len(value) > 0:
        return "x" * len(value)
    else:
        return "your_value_here"


def get_git_config(key: str) -> str:
    code, out, _ = run_command(["git", "config", "--get", key], capture=True)
    return out.strip() if code == 0 else ""


def init_git_repo(project_dir: Path, t: Dict[str, str]) -> bool:
    print_step(t["git_init"])
    code, _, err = run_command(["git", "init"], cwd=project_dir)
    if code != 0:
        if "already exists" in err.lower():
            print_warning("Git repository already initialized")
            return True
        print_error(f"Failed to init git: {err}")
        return False
    print_success("Git repository initialized")
    return True


def create_github_repo(project_dir: Path, repo_name: str, private: bool, t: Dict[str, str]) -> Optional[str]:
    """gh でリポジトリを自動作成。成功時は remote URL を、失敗時は None を返す。"""
    # gh が使えるか確認
    code, _, _ = run_command(["gh", "--version"], capture=True)
    if code != 0:
        print_warning(t["gh_missing"])
        return None

    print_step(t["repo_creating"])
    visibility = "--private" if private else "--public"
    code, _, err = run_command(
        ["gh", "repo", "create", repo_name, visibility, "--source=.", "--remote=origin", "--push=false"],
        cwd=project_dir,
    )
    if code != 0:
        print_warning(t["repo_create_failed"])
        if err.strip():
            print_warning(err.strip().splitlines()[0] if err.strip() else "")
        print_info(t["auth_note"])
        return None

    # remote の URL を取得
    code, out, _ = run_command(["git", "remote", "get-url", "origin"], cwd=project_dir, capture=True)
    if code == 0 and out.strip():
        print_success(t["repo_created"])
        return out.strip()

    print_warning(t["repo_create_failed"])
    return None


def setup_git_remote(project_dir: Path, repo_url: str, t: Dict[str, str]) -> bool:
    print_step(t["git_remote_add"])
    # Check if remote already exists
    code, out, _ = run_command(["git", "remote", "-v"], cwd=project_dir, capture=True)
    if "origin" in out:
        print_warning("Remote 'origin' already exists, updating...")
        run_command(["git", "remote", "set-url", "origin", repo_url], cwd=project_dir)
    else:
        code, _, err = run_command(["git", "remote", "add", "origin", repo_url], cwd=project_dir)
        if code != 0:
            print_error(f"Failed to add remote: {err}")
            return False
    print_success(f"Remote set to: {repo_url}")
    return True


def setup_git_branch(project_dir: Path, branch_name: str, t: Dict[str, str]) -> bool:
    print_step(t["git_branch_rename"])
    # Get current branch
    code, out, _ = run_command(["git", "branch", "--show-current"], cwd=project_dir, capture=True)
    current_branch = out.strip() if code == 0 else "main"

    if current_branch != branch_name:
        code, _, err = run_command(["git", "branch", "-M", branch_name], cwd=project_dir)
        if code != 0:
            print_error(f"Failed to rename branch: {err}")
            return False
        print_success(f"Branch renamed to: {branch_name}")
    else:
        print_warning(f"Already on branch: {branch_name}")
    return True


def git_add_commit(project_dir: Path, t: Dict[str, str]) -> bool:
    print_step(t["git_add"])
    code, _, err = run_command(["git", "add", "."], cwd=project_dir)
    if code != 0:
        print_error(f"Failed to stage files: {err}")
        return False

    print_step(t["git_commit"])
    code, _, err = run_command(["git", "commit", "-m", "Initial commit"], cwd=project_dir)
    if code != 0:
        if "nothing to commit" in err.lower():
            print_warning("Nothing to commit")
            return True
        print_error(f"Failed to commit: {err}")
        return False

    print_success("Initial commit created")
    return True


def git_push(project_dir: Path, branch_name: str, t: Dict[str, str]) -> bool:
    print_step(t["pushing"])
    code, _, err = run_command(["git", "push", "-u", "origin", branch_name], cwd=project_dir)
    if code != 0:
        print_error(t["push_failed"])
        print_error(err)
        return False

    print_success(t["push_success"])
    return True


# ============================================================================
# Main Workflow
# ============================================================================
def select_language() -> str:
    print_divider()
    print(f"{Neon.TITLE}  🛡️  Safe Git Push - Language Selection{Neon.RESET}")
    print_divider()
    print(f"{Neon.PROMPT}Select language / 言語を選択してください:{Neon.RESET}")
    print(f"  {Neon.INFO}1. 日本語{Neon.RESET}")
    print(f"  {Neon.INFO}2. English{Neon.RESET}")
    print_divider(thin=True)

    while True:
        choice = prompt_input("Choice / 選択 [1-2]", "1")
        if choice in ("1", "ja", "japanese", "日本語"):
            return "ja"
        elif choice in ("2", "en", "english"):
            return "en"
        print_warning("Please enter 1 or 2 / 1 または 2 を入力してください")


def main():
    # Language selection
    lang = select_language()
    t = TEXTS[lang]

    # Clear screen for clean start
    os.system("clear" if os.name == "posix" else "cls")

    print_title(t, lang)

    project_dir = Path.cwd()
    print(f"{Neon.INFO}Working directory: {project_dir}{Neon.RESET}")
    print_divider(thin=True)

    # 1. Ensure .gitignore
    ensure_gitignore(project_dir, t)

    # 2. Scan .env and create .env.example
    scan_env_and_create_example(project_dir, t)

    print_divider(thin=True)

    # 3. Repository creation (public/private selectable) or manual URL
    # 3a. Ask repo name
    while True:
        repo_name = prompt_input(t["repo_name_prompt"])
        if repo_name:
            break
        print_error(t["repo_name_empty"])

    # 3b. Ask visibility
    print(f"{Neon.PROMPT}{t['repo_visibility_prompt']}{Neon.RESET}")
    for opt in t["repo_visibility_options"]:
        print(f"  {Neon.INFO}{opt}{Neon.RESET}")
    while True:
        vis_choice = prompt_input("Choice / 選択 [1-2]", "1")
        if vis_choice in ("1", "public"):
            private = False
            break
        elif vis_choice in ("2", "private"):
            private = True
            break
        print_warning("Please enter 1 or 2 / 1 または 2 を入力してください")

    # 3c. Try auto-create via gh
    repo_url = create_github_repo(project_dir, repo_name, private, t)

    # 3d. Fallback: manual URL input
    if not repo_url:
        while True:
            repo_url = prompt_input(t["repo_url_prompt"])
            if repo_url:
                break
            print_error(t["repo_url_empty"])

    # 4. Get branch name
    branch_name = prompt_input(t["branch_prompt"], "main")

    print_divider(thin=True)

    # 5. Git operations
    if not init_git_repo(project_dir, t):
        sys.exit(1)

    if not setup_git_remote(project_dir, repo_url, t):
        sys.exit(1)

    if not setup_git_branch(project_dir, branch_name, t):
        sys.exit(1)

    if not git_add_commit(project_dir, t):
        sys.exit(1)

    # 6. Confirm push
    print_divider()
    if not prompt_yes_no(t["push_confirm"], default_no=True):
        print_warning(t["push_cancelled"])
        print_divider()
        print(f"{Neon.SUCCESS}{t['done']}{Neon.RESET}")
        press_enter_to_exit(t)
        return

    # 7. Push
    if not git_push(project_dir, branch_name, t):
        sys.exit(1)

    print_divider()
    print(f"{Neon.SUCCESS}{t['done']}{Neon.RESET}")
    print_divider()
    press_enter_to_exit(t)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Neon.WARNING}Interrupted by user{Neon.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Neon.ERROR}Unexpected error: {e}{Neon.RESET}")
        sys.exit(1)