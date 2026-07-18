#!/usr/bin/env bash
# Safe Git Push - Uninstaller (Linux / macOS)
# 使い方 / Usage:
#   bash <(curl -fsSL https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/linux/uninstall.sh)
#   または / Or:  bash uninstall.sh

set -euo pipefail

echo -e "\033[36mSafe Git Push をアンインストールします / Uninstalling Safe Git Push...\033[0m"

# 1. シェルプロファイルから gitpush 関数/エイリアスを削除
for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
    if [ -f "$rc" ]; then
        if grep -q "safe_git_push.py" "$rc" 2>/dev/null; then
            # gitpush 関数定義行とその直後の python パス行を削除
            grep -v "safe_git_push.py" "$rc" > "${rc}.tmp" && mv "${rc}.tmp" "$rc"
            echo -e "\033[32m[ok] Cleaned $rc\033[0m"
        fi
    fi
done

# 2. インストールフォルダを削除
TOOL_DIR="$HOME/git-push-tool"
if [ -d "$TOOL_DIR" ]; then
    rm -rf "$TOOL_DIR"
    echo -e "\033[32m[ok] Removed $TOOL_DIR\033[0m"
fi

echo -e "\033[33m[note] gitpush を手動で別フォルダに置いた場合は、そちらも手動で削除してください / If you placed it manually elsewhere, delete it yourself.\033[0m"
echo -e "\033[32m完了 / Done.\033[0m"
