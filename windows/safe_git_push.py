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
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# スクリプトバージョン（self-update で使用）
SCRIPT_VERSION = "1.2.2"
# 自分自身を更新する際の raw URL（linux / windows で上書きされる）
SELF_UPDATE_RAW_URL = "https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/windows/safe_git_push.py"


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
        "title": "Safe Git Push へようこそ",
        "subtitle": "機密情報を守りながら GitHub へプッシュします",
        "lang_prompt": "言語を選択してください / Select language:",
        "lang_options": ["1. 日本語", "2. English"],
        "lang_selected": "日本語を選択しました",
        "gitignore_created": ".gitignore を作成しました",
        "gitignore_exists": ".gitignore は既に存在します",
        "env_found": ".env ファイルが見つかりました",
        "env_not_found": ".env ファイルが見つかりません（スキップ）",
        "env_example_created": ".env.example を生成しました",
        "repo_url_prompt": "GitHub リポジトリの URL を入力してください (例: https://github.com/user/repo.git)",
        "repo_url_empty": "URL は必須です",
        "repo_name_prompt": "作成するリポジトリ名を入力してください",
        "repo_name_empty": "リポジトリ名は必須です",
        "repo_visibility_prompt": "リポジトリの公開設定を選択してください",
        "repo_visibility_options": ["1. Public（世界に公開）", "2. Private（非公開）"],
        "repo_creating": "GitHub にリポジトリを作成しています...",
        "repo_created": "リポジトリを作成しました",
        "repo_create_failed": "リポジトリの自動作成に失敗しました（URLを手入力できます）",
        "repo_exists": "既存のリポジトリが見つかりました",
        "repo_exists_url": "既存リポジトリを使用: ",
        "repo_url_style": "リモートURLの形式を選択",
        "repo_url_style_options": ["1. HTTPS（推奨）", "2. SSH（git@...）"],
        "gh_missing": "gh が見つからないか未認証です。URLを直接入力してください",
        "auth_note": "自分のトークンで自動作成したい場合: gh auth login を実行してください",
        "branch_prompt": "ブランチ名を入力してください [main]",
        "git_init": "Git リポジトリを初期化しています...",
        "git_remote_add": "リモートを追加しています...",
        "git_branch_rename": "ブランチ名を変更しています...",
        "git_add": "ファイルをステージングしています...",
        "git_commit": "コミットを作成しています...",
        "push_confirm": "GitHub にプッシュしますか？ [y/N]:",
        "push_cancelled": "プッシュをキャンセルしました",
        "pushing": "プッシュしています...",
        "push_success": "プッシュが完了しました",
        "push_failed": "プッシュに失敗しました",
        "error_git_not_found": "git が見つかりません。インストールしてください。",
        "error_not_git_repo": "ここは Git リポジトリではありません。",
        "done": "完了",
        "press_enter": "Enter キーで終了...",
        "config_loaded": "設定ファイルを読み込みました",
        "config_not_found": "設定ファイルが見つかりません（デフォルトを使用）",
        "config_error": "設定ファイルの読み込みに失敗しました（デフォルトを使用）",
        "config_validated": "設定値の検証に通過しました",
        "config_global_loaded": "グローバル設定を適用しました (~/.config/gitpush.toml)",
        "config_unknown_key": "警告: 不明な設定キーを無視しました:",
        "config_bad_type": "警告: 設定の型が不正です:",
        "config_bad_value": "警告: 設定値が取り得ない値です:",
        "remote_warning": "警告: 予期しないリモート先が設定されています",
        "remote_expected": "予期されるリモート: ",
        "hook_installed": "pre-commit フックを登録しました（.env の混入を防ぎます）",
        "hook_exists": "pre-commit フックは既に存在します",
        "ci_created": ".github/workflows/secret-scan.yml を作成しました",
        "ci_exists": ".github/workflows/secret-scan.yml は既に存在します",
        "update_available": "新しいバージョンがあります。更新しますか？ [y/N]:",
        "update_no": "更新はありません",
        "update_failed": "更新の確認に失敗しました（スキップ）",
        "updating": "自己更新中...",
        "secret_in_code": "警告: ソースコード内に秘密のような文字列が見つかりました",
        "secret_in_code_detail": "以上のファイルに 'password'/'api_key'/'secret' 等のリテラルが含まれています",
        "secret_file_found": "警告: 機密ファイルらしきものが見つかりました",
        "secret_file_detail": "以下の機密ファイルを push しようとしています",
        "gitignore_gap": "既存の .gitignore に機密パターンが足りません。追記しますか？ [y/N]:",
        "gitignore_patched": ".gitignore を更新しました",
        "history_scan": "過去のコミット履歴をスキャン中...",
        "history_secret_found": "警告: 過去のコミットに秘密らしき文字列が見つかりました",
        "dry_run_title": "プッシュ予定の内容 (dry-run)",
        "commit_message_prompt": "コミットメッセージを入力してください [Initial commit]",
        "multi_remote_push": "追加のリモートにもプッシュしています...",
        "log_written": "ログを gitpush.log に書きました",
        "provider_gitlab": "GitLab リポジトリを作成しています...",
        "uninstall_done": "アンインストールが完了しました",
        "token_setup_title": "GitHub トークンの設定",
        "token_setup_detail": "Push に使う GitHub トークン (ghp_...) を入力してください。",
        "token_perm_recommend": "永久トークンをおすすめします（一度設定すれば保存されます）",
        "token_input_prompt": "トークンを貼り付けてください",
        "token_saved": "トークンを保存しました",
        "token_invalid": "警告: トークンの形式が不正です（ghp_ 等で始まるはず）",
        "token_from_env": "環境変数からトークンを読み込みました",
        "token_empty_skip": "トークンが無いので、URL を手動入力します",
        "repo_list_title": "既存のリポジトリ一覧（数字で選択 / 0 で新規作成 / q で終了）",
        "repo_list_empty": "既存リポジトリが見つかりません（0 で新規作成）",
        "repo_list_failed": "リポジトリ一覧の取得に失敗しました（新規作成または URL 手入力）",
        "menu_select_quit": "q で終了",
    },
    "en": {
        "title": "Welcome to Safe Git Push!",
        "subtitle": "Push to GitHub while protecting sensitive data",
        "lang_prompt": "Select language / 言語を選択してください:",
        "lang_options": ["1. 日本語", "2. English"],
        "lang_selected": "English selected",
        "gitignore_created": "Created .gitignore",
        "gitignore_exists": ".gitignore already exists",
        "env_found": "Found .env file",
        "env_not_found": "No .env file found (skipping)",
        "env_example_created": "Generated .env.example",
        "repo_url_prompt": "Enter GitHub repository URL (e.g., https://github.com/user/repo.git)",
        "repo_url_empty": "URL is required",
        "repo_name_prompt": "Enter the repository name to create",
        "repo_name_empty": "Repository name is required",
        "repo_visibility_prompt": "Select repository visibility",
        "repo_visibility_options": ["1. Public (open to the world)", "2. Private (hidden)"],
        "repo_creating": "Creating repository on GitHub...",
        "repo_created": "Repository created",
        "repo_create_failed": "Failed to auto-create repo (you can enter URL manually)",
        "repo_exists": "An existing repository was found",
        "repo_exists_url": "Using existing repository: ",
        "repo_url_style": "Select remote URL style",
        "repo_url_style_options": ["1. HTTPS (recommended)", "2. SSH (git@...)"],
        "gh_missing": "gh not found or not authenticated. Enter URL directly",
        "auth_note": "To auto-create with your token, run: gh auth login",
        "branch_prompt": "Enter branch name [main]",
        "git_init": "Initializing Git repository...",
        "git_remote_add": "Adding remote...",
        "git_branch_rename": "Renaming branch...",
        "git_add": "Staging files...",
        "git_commit": "Creating commit...",
        "push_confirm": "Push to GitHub? [y/N]:",
        "push_cancelled": "Push cancelled",
        "pushing": "Pushing...",
        "push_success": "Push completed successfully!",
        "push_failed": "Push failed",
        "error_git_not_found": "git not found. Please install git.",
        "error_not_git_repo": "Not a Git repository.",
        "done": "Done!",
        "press_enter": "Press Enter to exit...",
        "config_loaded": "Config file loaded",
        "config_not_found": "Config file not found (using defaults)",
        "config_error": "Failed to load config (using defaults)",
        "config_validated": "Config values validated",
        "config_global_loaded": "Global config applied (~/.config/gitpush.toml)",
        "config_unknown_key": "Warning: unknown config key ignored:",
        "config_bad_type": "Warning: config value has wrong type:",
        "config_bad_value": "Warning: config value is not allowed:",
        "remote_warning": "Warning: unexpected remote destination is configured",
        "remote_expected": "Expected remote: ",
        "hook_installed": "pre-commit hook installed (blocks .env commits)",
        "hook_exists": "pre-commit hook already exists",
        "ci_created": "Created .github/workflows/secret-scan.yml",
        "ci_exists": ".github/workflows/secret-scan.yml already exists",
        "update_available": "A new version is available. Update now? [y/N]:",
        "update_no": "No update available",
        "update_failed": "Failed to check for updates (skipped)",
        "updating": "Self-updating...",
        "secret_in_code": "Warning: secret-like strings found in source code",
        "secret_in_code_detail": "The above files contain literals like 'password'/'api_key'/'secret'",
        "secret_file_found": "Warning: secret-like files found",
        "secret_file_detail": "You are about to push these secret-like files",
        "gitignore_gap": "Existing .gitignore is missing secret patterns. Append them? [y/N]:",
        "gitignore_patched": ".gitignore updated",
        "history_scan": "Scanning past commit history...",
        "history_secret_found": "Warning: secret-like strings found in past commits",
        "dry_run_title": "Contents to be pushed (dry-run)",
        "commit_message_prompt": "Enter commit message [Initial commit]",
        "multi_remote_push": "Pushing to extra remotes...",
        "log_written": "Log written to gitpush.log",
        "provider_gitlab": "Creating GitLab repository...",
        "uninstall_done": "Uninstall completed",
        "token_setup_title": "GitHub token setup",
        "token_setup_detail": "Enter the GitHub token (ghp_...) used for pushing.",
        "token_perm_recommend": "A permanent token is recommended (saved once, reused).",
        "token_input_prompt": "Paste your token",
        "token_saved": "Token saved",
        "token_invalid": "Warning: token format looks wrong (should start with ghp_ etc.)",
        "token_from_env": "Loaded token from environment variable",
        "token_empty_skip": "No token given, will ask for URL manually",
        "repo_list_title": "Existing repositories (pick by number / 0 for new / q to quit):",
        "repo_list_empty": "No existing repos found (0 to create new)",
        "repo_list_failed": "Failed to list repos (create new or enter URL manually)",
        "menu_select_quit": "q to quit",
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
    print(f"{Neon.INFO}>> {msg}{Neon.RESET}")


def print_success(msg: str):
    print(f"{Neon.SUCCESS}[OK] {msg}{Neon.RESET}")


def print_warning(msg: str):
    print(f"{Neon.WARNING}[!] {msg}{Neon.RESET}")


def print_info(msg: str):
    print(f"{Neon.INFO}[i] {msg}{Neon.RESET}")


def print_error(msg: str):
    print(f"{Neon.ERROR}[X] {msg}{Neon.RESET}")


def prompt_input(prompt: str, default: str = "", range_hint: str = "") -> str:
    if range_hint:
        full_prompt = f"{Neon.PROMPT}{prompt} {Neon.INFO}[{range_hint}]{Neon.PROMPT}: {Neon.INPUT}"
    elif default:
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


def menu_select(options: List[str], default_idx: int = 0, title: str = "",
                t: Dict[str, str] = None, allow_quit: bool = True) -> Optional[int]:
    """番号選択メニュー。q で終了 (None を返す)。`q` は y/N プロンプトや
    自由入力には影響しない（干渉回避のため、このメニュー専用）。"""
    if not options:
        return None
    if title:
        print_divider(thin=True)
        print(f"{Neon.PROMPT}{title}{Neon.RESET}")
    for i, opt in enumerate(options, 1):
        marker = Neon.SUCCESS + "▶ " if (default_idx and i == default_idx) else Neon.INFO + "  "
        print(f"  {marker}{i}. {opt}{Neon.RESET}")
    if allow_quit:
        print(f"  {Neon.WARNING}  q. {t['menu_select_quit'] if t else 'quit'}{Neon.RESET}")
    while True:
        choice = prompt_input("Choice / 選択", "", range_hint=f"1-{len(options)}")
        if allow_quit and choice.lower() == "q":
            return None
        if not choice and default_idx:
            return default_idx
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        print_warning("Please enter 1-{0}{1}".format(
            len(options), " or q" if allow_quit else ""))


def run_command(cmd: List[str], cwd: Optional[Path] = None, capture: bool = False, env: Optional[Dict[str, str]] = None) -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)"""
    try:
        if capture:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, cwd=cwd, text=True, env=env)
            return result.returncode, "", ""
    except FileNotFoundError:
        return -1, "", "command not found"
    except Exception as e:
        return -1, "", str(e)


# ============================================================================
# Config (gitpush.toml)
# ============================================================================
def load_config(project_dir: Path, t: Dict[str, str]) -> Dict[str, object]:
    """gitpush.toml を読み込む。無い / 壊れてる場合はデフォルトを返す。"""
    cfg_path = project_dir / "gitpush.toml"
    defaults: Dict[str, object] = {
        "default_visibility": "public",   # public | private
        "token_env": "GITHUB_TOKEN",       # 読み込む環境変数名
        "default_branch": "main",
        "auto_hook": True,                  # pre-commit フックを自動登録
        "auto_ci": True,                   # secret-scan.yml を自動生成
        "self_update": True,               # 起動時に自己更新チェック
        "expected_remote": "",             # 警告用: 期待されるリモートURLの一部
        # --- 新機能 (v1.2.0) ---
        "scan_secrets": True,              # ソース内の秘密リテラルをスキャン
        "warn_secret_files": True,         # .pem/.key 等の機密ファイルを警告
        "scan_history": False,             # 過去のコミット履歴もスキャン (重い)
        "check_gitignore_gap": True,       # .gitignore の不足パターンを警告
        "dry_run": True,                   # push 前に差分プレビュー
        "default_message": "Initial commit",  # コミットメッセージ
        "branch_pattern": "",              # ブランチ自動命名 (例: feature/%Y%m%d) 空ならオフ
        "extra_remotes": [],               # 一斉 push する追加リモート名のリスト
        "update_channel": "stable",        # stable | beta
        "provider": "github",              # github | gitlab
        "log_file": "gitpush.log",         # ログ出力先 (空なら出力しない)
    }
    if not cfg_path.exists():
        print_info(t["config_not_found"])
        # プロジェクトに無くてもグローバル設定は適用
        global_cfg = _load_toml_file(Path.home() / ".config" / "gitpush.toml", t)
        if global_cfg:
            merged = dict(defaults)
            merged.update(global_cfg)
            print_success(t["config_global_loaded"])
            return merged
        return defaults
    try:
        data = _load_toml_file(cfg_path, t) or {}
        # プロジェクトの token は無視（平文保存を防ぐ。グローバル設定のみ有効）
        data.pop("token", None)
        # グローバル設定 (~/.config/gitpush.toml) をマージ（プロジェクト優先）
        global_cfg = _load_toml_file(Path.home() / ".config" / "gitpush.toml", t)
        merged = dict(defaults)
        if global_cfg:
            merged.update(global_cfg)
        merged.update(data)
        print_success(t["config_loaded"])
        return merged
    except Exception as e:
        print_warning(f"{t['config_error']}: {e}")
        return defaults


# 設定キーごとの期待型 / 取り得る値（バリデーション用）
CONFIG_SCHEMA: Dict[str, Dict[str, object]] = {
    "default_visibility": {"type": str, "choices": ["public", "private"]},
    "token_env": {"type": str},
    "default_branch": {"type": str},
    "auto_hook": {"type": bool},
    "auto_ci": {"type": bool},
    "self_update": {"type": bool},
    "expected_remote": {"type": str},
    "scan_secrets": {"type": bool},
    "warn_secret_files": {"type": bool},
    "scan_history": {"type": bool},
    "check_gitignore_gap": {"type": bool},
    "dry_run": {"type": bool},
    "default_message": {"type": str},
    "branch_pattern": {"type": str},
    "extra_remotes": {"type": list},
    "update_channel": {"type": str, "choices": ["stable", "beta"]},
    "provider": {"type": str, "choices": ["github", "gitlab"]},
    "log_file": {"type": str},
}


def get_token(cfg: Dict[str, object], t: Dict[str, str], interactive: bool = True) -> str:
    """GitHub トークンを取得する。毎回入力を促し、空エンターならグローバル保存値を使う。
    トークンは ~/.config/gitpush.toml のみに保存（プロジェクトには書かない）。"""
    if not interactive:
        print_warning(t["token_empty_skip"])
        return ""

    saved = cfg.get("token", "")
    print_divider()
    print(f"{Neon.TITLE}  {t['token_setup_title']}{Neon.RESET}")
    print_info(t["token_setup_detail"])
    print_info(t["token_perm_recommend"])
    while True:
        tok = prompt_input(t["token_input_prompt"], saved if saved else "")
        if not tok:
            if saved:
                return saved
            print_warning(t["token_empty_skip"])
            return ""
        # ざっくり検証: ghp_ / github_pat_ / その他40桁前後の英数字
        if not re.match(r"^(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|[A-Za-z0-9_-]{20,})$", tok):
            print_warning(t["token_invalid"])
            continue
        # 保存（グローバル設定 ~/.config/gitpush.toml のみ。プロジェクトには書かない）
        if tok != saved:
            _save_token_to_config(cfg, tok, t)
        return tok


def _save_token_to_config(cfg: Dict[str, object], tok: str, t: Dict[str, str]) -> None:
    """トークンをグローバル設定 (~/.config/gitpush.toml) のみに保存する。
    プロジェクトの gitpush.toml には書かない（pre-commit フックに検出されるため）。"""
    try:
        global_path = Path.home() / ".config" / "gitpush.toml"
        global_path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        if global_path.exists():
            lines = global_path.read_text(encoding="utf-8").splitlines()
        # 既存の token = 行を除去
        lines = [ln for ln in lines if not ln.strip().startswith("token")]
        lines.append(f'token = "{tok}"')
        global_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        cfg["token"] = tok
        print_success(t["token_saved"])
    except Exception:
        pass


def validate_config(cfg: Dict[str, object], t: Dict[str, str]) -> None:
    """設定値の妥当性をチェックし、不正があれば警告する。"""
    warned = False
    for key, val in cfg.items():
        schema = CONFIG_SCHEMA.get(key)
        if schema is None:
            print_warning(f"{t['config_unknown_key']} {key}")
            warned = True
            continue
        # 型チェック
        expected = schema["type"]
        if expected is bool and not isinstance(val, bool):
            # TOML 簡易パース等で文字列化された真偽値を救う
            if isinstance(val, str) and val.lower() in ("true", "false"):
                cfg[key] = (val.lower() == "true")
                continue
            print_warning(f"{t['config_bad_type']} {key} (expected bool, got {type(val).__name__})")
            warned = True
        elif expected is list and not isinstance(val, list):
            if isinstance(val, str) and val == "":
                cfg[key] = []
                continue
            print_warning(f"{t['config_bad_type']} {key} (expected list, got {type(val).__name__})")
            warned = True
        elif expected is str and not isinstance(val, str):
            print_warning(f"{t['config_bad_type']} {key} (expected string, got {type(val).__name__})")
            warned = True
        # choices チェック
        choices = schema.get("choices")
        if choices and isinstance(val, str) and val not in choices:
            print_warning(f"{t['config_bad_value']} {key}={val!r} (expected one of {choices})")
            warned = True
    if not warned:
        print_success(t["config_validated"])


def _load_toml_file(path: Path, t: Dict[str, str]) -> Dict[str, object]:
    """TOML ファイルを読み込む。無ければ空 dict を返す。"""
    if not path.exists():
        return {}
    try:
        try:
            import tomllib
            with open(path, "rb") as f:
                return tomllib.load(f)
        except ModuleNotFoundError:
            try:
                import toml  # type: ignore
                return toml.load(path)
            except ModuleNotFoundError:
                # 簡易パース（階層なしの key = "value" のみ対応）
                data: Dict[str, object] = {}
                for line in path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    data[k.strip()] = v.strip().strip('"').strip("'")
                return data
    except Exception:
        return {}


# ============================================================================
# Secret scanning (v1.2.0)
# ============================================================================
SECRET_LITERAL_RE = None  # lazy compile
SECRET_FILE_EXTS = {".pem", ".key", ".p12", ".pfx", ".keystore", ".jks", ".der", ".crt", ".cer", ".p7b", ".p7c"}
SECRET_FILE_NAMES = {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", "known_hosts", "credentials", ".netrc"}


def scan_secret_literals(project_dir: Path, t: Dict[str, str]) -> bool:
    """ソース内の秘密リテラルをスキャン。見つかったら警告し、y/N を返す（True=続行）。"""
    import re
    global SECRET_LITERAL_RE
    if SECRET_LITERAL_RE is None:
        SECRET_LITERAL_RE = re.compile(
            r"""(?i)\b(password|passwd|pwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|private[_-]?key)\s*[:=]\s*['"][^'"]{4,}['"]"""
        )
    hits = []
    for p in project_dir.rglob("*"):
        if not p.is_file():
            continue
        if any(part.startswith(".") for part in p.relative_to(project_dir).parts):
            # .git 等はスキップ
            if ".git" in p.relative_to(project_dir).parts:
                continue
        if p.suffix in {".py", ".js", ".ts", ".sh", ".json", ".yaml", ".yml", ".env", ".toml", ".txt", ".md", ".rb", ".go", ".java", ".php", ".c", ".cpp", ".cs"}:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if SECRET_LITERAL_RE.search(line):
                    hits.append(f"  {p.relative_to(project_dir)}:{i}")
                    break
    if not hits:
        return True
    print_warning(t["secret_in_code"])
    for h in hits[:10]:
        print_warning(h)
    if len(hits) > 10:
        print_warning(f"  ... and {len(hits) - 10} more")
    print_warning(t["secret_in_code_detail"])
    return False


def scan_secret_files(project_dir: Path, t: Dict[str, str]) -> bool:
    """機密ファイル（.pem, .key 等）をスキャン。見つかったら警告し y/N を返す。"""
    hits = []
    for p in project_dir.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(project_dir)
        if ".git" in rel.parts:
            continue
        if p.suffix.lower() in SECRET_FILE_EXTS or p.name.lower() in SECRET_FILE_NAMES:
            hits.append(f"  {rel}")
    if not hits:
        return True
    print_warning(t["secret_file_found"])
    for h in hits:
        print_warning(h)
    print_warning(t["secret_file_detail"])
    return False


def check_gitignore_gap(project_dir: Path, t: Dict[str, str], non_interactive: bool = False) -> None:
    """既存 .gitignore に機密パターンが足りなければ追記を提案。"""
    gitignore_path = project_dir / ".gitignore"
    if not gitignore_path.exists():
        return
    content = gitignore_path.read_text(encoding="utf-8")
    required = [".env", ".pem", ".key", "*.p12", "id_rsa", ".gitpush.toml", "gitpush.log"]
    missing = [pat for pat in required if pat not in content]
    if not missing:
        return
    print_warning(t["gitignore_gap"])
    if not non_interactive and not prompt_yes_no("Continue / 続行", default_no=True):
        return
    with open(gitignore_path, "a", encoding="utf-8") as f:
        f.write("\n# Added by Safe Git Push\n")
        for pat in missing:
            f.write(pat + "\n")
    print_success(t["gitignore_patched"])


def scan_history(project_dir: Path, t: Dict[str, str]) -> bool:
    """過去のコミット履歴をスキャン（重い）。秘密があれば警告。"""
    print_step(t["history_scan"])
    import re
    pat = re.compile(r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|password\s*[:=]\s*['\"][^'\"]{4,}['\"])", re.I)
    code, out, _ = run_command(
        ["git", "log", "-p", "--all", "-U0"], cwd=project_dir, capture=True
    )
    if code != 0 or not out:
        return True
    if pat.search(out):
        print_warning(t["history_secret_found"])
        return prompt_yes_no(t["history_secret_found"], default_no=True)
    return True


def write_log(project_dir: Path, cfg: Dict[str, object], lines: list) -> None:
    log_file = cfg.get("log_file", "")
    if not log_file:
        return
    try:
        with open(project_dir / log_file, "a", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        print_info(t["log_written"])
    except Exception:
        pass


# ============================================================================
# Auto-registration: pre-commit hook
# ============================================================================
PRE_COMMIT_HOOK = """#!/usr/bin/env bash
# Safe Git Push - pre-commit hook (auto-generated)
# .env やトークンらしき文字列がコミットされようとしていたらブロックする
set -euo pipefail

echo "[safe-git-push] checking for secrets..."

# 1. .env ファイルがステージされていないか（.env.example は許可）
#    ブロック: .env, .env.local, .env.prod など
#    許可:     .env.example
if git diff --cached --name-only | grep -E '(^|/)\.env(\.[a-zA-Z0-9]+)?$' | grep -v '\.env\.example$' ; then
    echo "ERROR: .env file is staged. Remove it (use .env.example instead)."
    exit 1
fi

# 2. トークンらしき文字列 (ghp_, github_pat_, etc.) が含まれていないか
if git diff --cached -U0 | grep -iE 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}' ; then
    echo "ERROR: possible token/secret found in commit. Aborting."
    exit 1
fi

echo "[safe-git-push] no secrets detected."
exit 0
"""


def install_pre_commit_hook(project_dir: Path, t: Dict[str, str]) -> None:
    hook_path = project_dir / ".git" / "hooks" / "pre-commit"
    if hook_path.exists():
        print_info(t["hook_exists"])
        return
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(PRE_COMMIT_HOOK, encoding="utf-8")
    try:
        hook_path.chmod(0o755)
    except Exception:
        pass
    print_success(t["hook_installed"])


# ============================================================================
# Auto-registration: GitHub Actions secret scan
# ============================================================================
SECRET_SCAN_WORKFLOW = """name: Secret Scan

on: [push, pull_request]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Scan for secrets
        uses: gitleaks/gitleaks-action@v2
        with:
          config-path: .github/gitleaks.toml
        continue-on-error: true
"""

GITLEAKS_CONFIG = """title = "gitpush default"

[[rules]]
id = "github-token"
description = "GitHub Personal Access Token"
regex = '''ghp_[A-Za-z0-9]{20,}'''
[[rules]]
id = "github-pat"
description = "GitHub Fine-grained PAT"
regex = '''github_pat_[A-Za-z0-9_]{20,}'''
[[rules]]
id = "aws-key"
description = "AWS Access Key"
regex = '''AKIA[0-9A-Z]{16}'''
"""


def create_ci_workflow(project_dir: Path, t: Dict[str, str]) -> None:
    wf_path = project_dir / ".github" / "workflows" / "secret-scan.yml"
    if wf_path.exists():
        print_info(t["ci_exists"])
        return
    wf_path.parent.mkdir(parents=True, exist_ok=True)
    wf_path.write_text(SECRET_SCAN_WORKFLOW, encoding="utf-8")
    # gitleaks 設定も置く
    (project_dir / ".github" / "gitleaks.toml").write_text(GITLEAKS_CONFIG, encoding="utf-8")
    print_success(t["ci_created"])


# ============================================================================
# Multi-remote warning
# ============================================================================
def check_unexpected_remote(project_dir: Path, expected: str, t: Dict[str, str]) -> None:
    if not expected:
        return
    code, out, _ = run_command(["git", "remote", "-v"], cwd=project_dir, capture=True)
    if code != 0:
        return
    for line in out.splitlines():
        if "origin" in line and "push" in line:
            url = line.split()[1]
            if expected not in url:
                print_warning(t["remote_warning"])
                print_warning(f"{t['remote_expected']}{expected}")
                print_warning(f"  actual: {url}")


# ============================================================================
# Self-update
# ============================================================================
def parse_version(v: str):
    """バージョン文字列を比較用タプルにする。
    '1.2.0' -> (1,2,0,1)  /  '1.2.1-beta' -> (1,2,1,0,'beta')
    pre-release サフィックス無しを上位(1)とし、ありを下位(0)とする。"""
    import re
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-([A-Za-z0-9.]+))?$", v.strip())
    if not m:
        # 解析不可な場合は辞書順比較のためそのまま返す
        return (0, 0, 0, 1, v)
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
    pre = m.group(4)
    if pre is None:
        return (major, minor, patch, 1)
    return (major, minor, patch, 0, pre)


def self_update(t: Dict[str, str], raw_url: str, channel: str = "stable") -> None:
    import urllib.request
    # チャンネルに応じてブランチを切り替え (main / beta)
    if channel == "beta":
        raw_url = raw_url.replace("/main/", "/beta/")
    try:
        with urllib.request.urlopen(raw_url, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="replace")
    except Exception:
        print_warning(t["update_failed"])
        return
    # バージョンを探す
    import re
    m = re.search(r'SCRIPT_VERSION\s*=\s*["\']([^"\']+)["\']', content)
    if not m:
        return
    remote_version = m.group(1)
    if parse_version(remote_version) <= parse_version(SCRIPT_VERSION):
        print_info(t["update_no"])
        return
    print_info(f"local={SCRIPT_VERSION} remote={remote_version}")
    if not prompt_yes_no(t["update_available"], default_no=True):
        return
    print_step(t["updating"])
    try:
        script_path = Path(__file__).resolve()
        # バックアップ
        backup = script_path.with_suffix(".py.bak")
        backup.write_text(script_path.read_text(encoding="utf-8"), encoding="utf-8")
        script_path.write_text(content, encoding="utf-8")
        print_success(f"Updated to {remote_version} (backup: {backup.name})")
    except Exception as e:
        print_warning(f"{t['update_failed']}: {e}")


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


def list_repos(token: str, t: Dict[str, str]) -> list:
    """GitHub API で既存リポジトリ一覧を取得（token が必要）。"""
    if not token:
        return []
    import urllib.request
    import json
    try:
        req = urllib.request.Request(
            "https://api.github.com/user/repos?per_page=100&sort=updated",
            headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return [r.get("name", "") for r in data if r.get("name")]
    except Exception:
        return []


def select_repo(token: str, t: Dict[str, str]) -> str:
    """既存リポジトリ一覧から数字で選択 / 0 で新規作成 / q で終了。"""
    repos = list_repos(token, t)
    if not repos:
        print_info(t["repo_list_empty"])
        return ""
    options = list(repos) + ["(new / 新規作成)"]
    idx = menu_select(options, default_idx=0,
                      title=t["repo_list_title"], t=t, allow_quit=True)
    if idx is None:
        sys.exit(0)
    if idx == len(repos) + 1:
        return ""
    return repos[idx - 1]


def create_github_repo(project_dir: Path, repo_name: str, private: bool, t: Dict[str, str], provider: str = "github", token: str = "") -> Optional[str]:
    """リポジトリを自動作成（github: gh / gitlab: glab）。成功時は remote URL、失敗時は None。"""
    visibility = "private" if private else "public"

    if provider == "gitlab":
        code, _, _ = run_command(["glab", "version"], capture=True)
        if code != 0:
            print_warning(t["gh_missing"])
            return None
        print_step(t["provider_gitlab"])
        code, _, err = run_command(
            ["glab", "repo", "create", repo_name, f"--{visibility}", "--remote=origin"],
            cwd=project_dir,
        )
        if code != 0:
            print_warning(t["repo_create_failed"])
            return None
        code, out, _ = run_command(["git", "remote", "get-url", "origin"], cwd=project_dir, capture=True)
        if code == 0 and out.strip():
            print_success(t["repo_created"])
            return out.strip()
        return None

    # github (default)
    code, _, _ = run_command(["gh", "--version"], capture=True)
    if code != 0:
        print_warning(t["gh_missing"])
        return None

    # 入力されたトークンを gh に渡す（環境変数を勝手に探させない）
    gh_env = dict(os.environ)
    if token:
        gh_env["GH_TOKEN"] = token
        gh_env["GITHUB_TOKEN"] = token

    # 同名リポジトリが既に存在するか確認
    view_code, view_out, _ = run_command(
        ["gh", "repo", "view", repo_name, "--json", "url"], cwd=project_dir, capture=True, env=gh_env
    )
    if view_code == 0 and "url" in view_out:
        print_warning(t["repo_exists"])
        if prompt_yes_no(t["push_confirm"], default_no=True):
            # 既存リポの URL を origin に設定
            import re as _re
            m = _re.search(r'"url"\s*:\s*"([^"]+)"', view_out)
            existing_url = m.group(1) if m else f"https://github.com/{repo_name}"
            run_command(["git", "remote", "add", "origin", existing_url], cwd=project_dir)
            print_success(t["repo_exists_url"] + existing_url)
            return _maybe_ssh(existing_url, project_dir, t)
        # 使わない場合は新規作成へ

    print_step(t["repo_creating"])
    vis_flag = "--private" if private else "--public"
    code, _, err = run_command(
        ["gh", "repo", "create", repo_name, vis_flag, "--source=.", "--remote=origin", "--push=false"],
        cwd=project_dir, env=gh_env,
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
        url = out.strip()
        print_success(t["repo_created"] + ": " + url)
        return _maybe_ssh(url, project_dir, t)

    print_warning(t["repo_create_failed"])
    return None


def _maybe_ssh(url: str, project_dir: Path, t: Dict[str, str]) -> str:
    """HTTPS / SSH の選択。SSH を選んだら remote URL を書き換える。"""
    idx = menu_select(t["repo_url_style_options"], default_idx=1,
                      title=t["repo_url_style"], t=t, allow_quit=True)
    if idx is None:
        sys.exit(0)
    if idx == 2:
        # https://github.com/user/repo.git -> git@github.com:user/repo.git
        import re
        m = re.match(r"https://github\.com/([^/]+)/(.+?)(?:\.git)?$", url)
        if m:
            ssh_url = f"git@{m.group(1)}:{m.group(2)}.git"
            run_command(["git", "remote", "set-url", "origin", ssh_url], cwd=project_dir)
            print_success(f"Remote set to SSH: {ssh_url}")
            return ssh_url
    return url


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


def git_add_commit(project_dir: Path, t: Dict[str, str], message: str = "Initial commit") -> bool:
    print_step(t["git_add"])
    code, _, err = run_command(["git", "add", "."], cwd=project_dir)
    if code != 0:
        print_error(f"Failed to stage files: {err}")
        return False

    print_step(t["git_commit"])
    code, _, err = run_command(["git", "commit", "-m", message], cwd=project_dir)
    if code != 0:
        if "nothing to commit" in err.lower():
            print_warning("Nothing to commit")
            return True
        print_error(f"Failed to commit: {err}")
        return False

    print_success("Initial commit created")
    return True


def git_push(project_dir: Path, branch_name: str, t: Dict[str, str], extra_remotes: Optional[list] = None, token: str = "") -> bool:
    print_step(t["pushing"])

    # token があれば remote URL に一時埋め込み（push 後にクリーン化）
    token_injected = False
    original_url = ""
    if token:
        code, out, _ = run_command(["git", "remote", "get-url", "origin"], cwd=project_dir, capture=True)
        if code == 0 and out.strip():
            original_url = out.strip()
            import re as _re
            m = _re.match(r"^(https://)([^/]+)(/.*)$", original_url)
            if m:
                injected = f"{m.group(1)}{token}@{m.group(2)}{m.group(3)}"
                run_command(["git", "remote", "set-url", "origin", injected], cwd=project_dir)
                token_injected = True

    code, _, err = run_command(["git", "push", "-u", "origin", branch_name], cwd=project_dir)

    # 必ずクリーン化
    if token_injected and original_url:
        run_command(["git", "remote", "set-url", "origin", original_url], cwd=project_dir)

    if code != 0:
        print_error(t["push_failed"])
        print_error(err)
        return False

    print_success(t["push_success"])

    # 追加リモートにも一斉 push
    for remote in (extra_remotes or []):
        print_step(t["multi_remote_push"] + f" {remote}")
        code, _, err = run_command(["git", "push", "-u", remote, branch_name], cwd=project_dir)
        if code != 0:
            print_warning(f"Push to {remote} failed: {err.strip().splitlines()[0] if err.strip() else ''}")
        else:
            print_success(f"Pushed to {remote}")
    return True


# ============================================================================
# Main Workflow
# ============================================================================
def select_language() -> str:
    print_divider()
    print(f"{Neon.TITLE}  Safe Git Push - Language Selection{Neon.RESET}")
    print_divider()
    idx = menu_select(["日本語", "English"], default_idx=1,
                      title="Select language / 言語を選択", t=TEXTS["ja"], allow_quit=True)
    if idx is None:
        sys.exit(0)
    return "ja" if idx == 1 else "en"


def main():
    # Non-interactive mode argv parsing
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--public", action="store_true")
    parser.add_argument("--private", action="store_true")
    parser.add_argument("--repo", type=str, default=None)
    parser.add_argument("--message", type=str, default=None)
    parser.add_argument("--lang", type=str, default=None)
    try:
        args, _ = parser.parse_known_args()
    except Exception:
        args = argparse.Namespace(yes=False, public=False, private=False,
                                   repo=None, message=None, lang=None)
    non_interactive = args.yes

    # Language selection (or from --lang)
    if args.lang in ("ja", "en"):
        lang = args.lang
    elif non_interactive:
        lang = "en"
    else:
        lang = select_language()
    t = TEXTS[lang]

    # Clear screen for clean start
    os.system("clear" if os.name == "posix" else "cls")

    print_title(t, lang)

    project_dir = Path.cwd()
    print(f"{Neon.INFO}Working directory: {project_dir}{Neon.RESET}")
    print_divider(thin=True)

    # 0. Self-update check (before anything else)
    cfg_pre = load_config(project_dir, t)
    if cfg_pre.get("self_update", True):
        self_update(t, SELF_UPDATE_RAW_URL, cfg_pre.get("update_channel", "stable"))

    # Reload config after potential update
    cfg = load_config(project_dir, t)
    validate_config(cfg, t)
    token = get_token(cfg, t, interactive=not non_interactive)
    default_visibility = cfg.get("default_visibility", "public")
    default_branch = cfg.get("default_branch", "main")
    auto_hook = cfg.get("auto_hook", True)
    auto_ci = cfg.get("auto_ci", True)
    expected_remote = cfg.get("expected_remote", "")
    default_message = cfg.get("default_message", "Initial commit")
    branch_pattern = cfg.get("branch_pattern", "")
    extra_remotes = cfg.get("extra_remotes", []) or []
    provider = cfg.get("provider", "github")
    update_channel = cfg.get("update_channel", "stable")
    scan_secrets = cfg.get("scan_secrets", True)
    warn_secret_files = cfg.get("warn_secret_files", True)
    scan_history_enabled = cfg.get("scan_history", False)
    check_gitignore_gap_enabled = cfg.get("check_gitignore_gap", True)
    dry_run_enabled = cfg.get("dry_run", True)
    log_lines = []

    # 1. Ensure .gitignore
    print_step("1. " + t["git_init"])
    ensure_gitignore(project_dir, t)

    # 2. Scan .env and create .env.example
    scan_env_and_create_example(project_dir, t)

    # 2b. Secret literal scan (source code)
    secret_issues = False
    if scan_secrets:
        if not scan_secret_literals(project_dir, t):
            secret_issues = True

    # 2c. Secret-file warning
    if warn_secret_files:
        if not scan_secret_files(project_dir, t):
            secret_issues = True

    # 2d. .gitignore gap check
    if check_gitignore_gap_enabled:
        check_gitignore_gap(project_dir, t, non_interactive=non_interactive)

    print_divider(thin=True)

    # 3. Repository creation
    if non_interactive and args.repo:
        repo_name = args.repo
    else:
        # 既存リポジトリ一覧から選択（token があれば）
        selected = select_repo(token, t)
        if selected:
            repo_name = selected
            print_info(f"{t['repo_exists_url']}{selected}")
        else:
            default_repo = project_dir.name
            while True:
                repo_name = prompt_input(t["repo_name_prompt"], default_repo)
                if repo_name:
                    break
                print_error(t["repo_name_empty"])

    # visibility
    if args.public:
        private = False
    elif args.private:
        private = True
    else:
        default_vis_idx = 2 if default_visibility == "private" else 1
        idx = menu_select(t["repo_visibility_options"], default_idx=default_vis_idx,
                          title=t["repo_visibility_prompt"], t=t, allow_quit=True)
        if idx is None:
            sys.exit(0)
        private = (idx == 2)

    # 3c. Try auto-create (gh repo create --source=. が git を必要とするため先に init)
    init_git_repo(project_dir, t)
    repo_url = create_github_repo(project_dir, repo_name, private, t, provider=provider, token=token)

    # 3d. Fallback: manual URL input
    if not repo_url:
        if non_interactive:
            repo_url = args.repo if args.repo and args.repo.startswith("http") else None
        while not repo_url:
            repo_url = prompt_input(t["repo_url_prompt"])
            if repo_url:
                break
            print_error(t["repo_url_empty"])

    # 4. Branch name (pattern from config or input)
    if branch_pattern:
        import datetime
        branch_name = branch_pattern.format(
            date=datetime.date.today().isoformat(),
            repo=repo_name,
            ts=datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        )
        print_info(f"{t['branch_prompt']} {branch_name}")
    elif non_interactive:
        branch_name = default_branch
    else:
        branch_name = prompt_input(t["branch_prompt"], default_branch)

    print_divider(thin=True)

    # 5. Git operations (git init は step 3c で済ませている)
    if auto_hook:
        install_pre_commit_hook(project_dir, t)

    if auto_ci:
        create_ci_workflow(project_dir, t)

    if not setup_git_remote(project_dir, repo_url, t):
        sys.exit(1)

    if not setup_git_branch(project_dir, branch_name, t):
        sys.exit(1)

    # commit message
    commit_message = args.message or default_message
    if not non_interactive and not args.message:
        commit_message = prompt_input(t["commit_message_prompt"], default_message)

    if not git_add_commit(project_dir, t, commit_message):
        sys.exit(1)

    # 6. Dry-run preview
    if dry_run_enabled:
        print_step(t["dry_run_title"])
        code, _, _ = run_command(["git", "rev-parse", "HEAD"], cwd=project_dir, capture=True)
        if code == 0:
            run_command(["git", "diff", "--stat", "HEAD"], cwd=project_dir)
        else:
            # まだコミットが無い（git init 直後）場合はステータスで代用
            run_command(["git", "status", "--short"], cwd=project_dir)

    # 6b. History scan (if enabled)
    if scan_history_enabled:
        if not scan_history(project_dir, t):
            sys.exit(1)

    # 7. Confirm push
    print_divider()
    if non_interactive:
        pass
    elif secret_issues:
        print_warning(t["secret_in_code_detail"])
        if not prompt_yes_no(t["push_confirm"], default_no=True):
            print_warning(t["push_cancelled"])
            print_divider()
            print(f"{Neon.SUCCESS}{t['done']}{Neon.RESET}")
            press_enter_to_exit(t)
            return
    elif not prompt_yes_no(t["push_confirm"], default_no=True):
        print_warning(t["push_cancelled"])
        print_divider()
        print(f"{Neon.SUCCESS}{t['done']}{Neon.RESET}")
        press_enter_to_exit(t)
        return

    # 7b. Multi-remote warning
    check_unexpected_remote(project_dir, expected_remote, t)

    # 8. Push (with multi-remote)
    if not git_push(project_dir, branch_name, t, extra_remotes, token=token):
        sys.exit(1)

    print_divider()
    print(f"{Neon.SUCCESS}{t['done']}{Neon.RESET}")
    print_divider()

    # 9. Logging
    log_lines.append(f"[{datetime.datetime.now().isoformat()}] pushed {repo_name} -> {branch_name} (provider={provider}, channel={update_channel})")
    write_log(project_dir, cfg, log_lines)

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