#!/usr/bin/env bash
# Safe Git Push - インストーラー / Installer
# 使い方 / Usage:
#   curl -fsSL https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/install.sh | bash
#
# やること / What it does:
#   1. ~/git-push-tool/safe_git_push.py をダウンロード
#   2. ~/.zshrc (または ~/.bashrc) に `gitpush` エイリアスを追加
#   3. 完了メッセージを表示

set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/ASDF3001/safe-git-push/main"
INSTALL_DIR="$HOME/git-push-tool"
SCRIPT_PATH="$INSTALL_DIR/safe_git_push.py"
ALIAS_LINE="alias gitpush='python3 \$HOME/git-push-tool/safe_git_push.py'"

# カラー（対話的でない場合は無効）
if [ -t 1 ]; then
  C_MAGE='\033[95m'; C_CYAN='\033[94m'; C_GREEN='\033[92m'; C_YEL='\033[93m'; C_RED='\033[91m'; C_RST='\033[0m'
else
  C_MAGE=''; C_CYAN=''; C_GREEN=''; C_YEL=''; C_RED=''; C_RST=''
fi

echo -e "${C_MAGE}🛡️  Safe Git Push - Installer${C_RST}"
echo -e "${C_CYAN}────────────────────────────────────────${C_RST}"

# 1. ディレクトリ作成
mkdir -p "$INSTALL_DIR"

# 2. スクリプトダウンロード
echo -e "${C_CYAN}📥 safe_git_push.py を取得中...${C_RST}"
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$REPO_RAW/safe_git_push.py" -o "$SCRIPT_PATH"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$SCRIPT_PATH" "$REPO_RAW/safe_git_push.py"
else
  echo -e "${C_RED}❌ curl も wget も見つかりません。どちらかをインストールしてください。${C_RST}"
  exit 1
fi
chmod +x "$SCRIPT_PATH"
echo -e "${C_GREEN}✅ $SCRIPT_PATH に保存しました${C_RST}"

# 3. エイリアス追加（zshrc 優先、なければ bashrc）
if [ -n "${ZSH_VERSION:-}" ] || [ -f "$HOME/.zshrc" ]; then
  RC_FILE="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
  RC_FILE="$HOME/.bashrc"
else
  RC_FILE="$HOME/.profile"
fi

if grep -q "git-push-tool/safe_git_push.py" "$RC_FILE" 2>/dev/null; then
  echo -e "${C_YEL}ℹ️  エイリアスは既に $RC_FILE に登録済みです（スキップ）${C_RST}"
else
  {
    echo ""
    echo "# Safe Git Push - 機密を守りながら安全にプッシュ"
    echo "# 詳細: https://github.com/ASDF3001/safe-git-push"
    echo "$ALIAS_LINE"
  } >> "$RC_FILE"
  echo -e "${C_GREEN}✅ エイリアスを $RC_FILE に追加しました${C_RST}"
fi

echo -e "${C_CYAN}────────────────────────────────────────${C_RST}"
echo -e "${C_GREEN}🎉 インストール完了！${C_RST}"
echo -e "${C_YEL}以下のどれかで有効化してください:${C_RST}"
echo -e "  ${C_CYAN}source $RC_FILE${C_RST}   (現在のターミナルですぐ使う)"
echo -e "  または新しいターミナルを開く"
echo -e "${C_YEL}使い方:${C_RST} ${C_CYAN}gitpush${C_RST}"
