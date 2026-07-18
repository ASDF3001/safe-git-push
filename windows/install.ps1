# Safe Git Push - Windows インストーラー / Windows Installer
# 使い方 / Usage:
#   irm https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/windows/install.ps1 | iex
#
# やること / What it does:
#   1. ~/git-push-tool/safe_git_push.py をダウンロード
#   2. PowerShell プロファイル ($PROFILE) に関数 gitpush を追加
#   3. 完了メッセージを表示

$ErrorActionPreference = "Stop"

$REPO_RAW = "https://raw.githubusercontent.com/ASDF3001/safe-git-push/main"
$InstallDir = Join-Path $HOME "git-push-tool"
$ScriptPath = Join-Path $InstallDir "safe_git_push.py"
$FuncLine = 'function gitpush { python "$HOME/git-push-tool/safe_git_push.py" }'

Write-Host "Safe Git Push - Installer" -ForegroundColor Magenta
Write-Host ("-" * 40)

# 1. ディレクトリ作成
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

# 2. スクリプトダウンロード
Write-Host "safe_git_push.py を取得中..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "$REPO_RAW/windows/safe_git_push.py" -OutFile $ScriptPath -UseBasicParsing
}
catch {
    Write-Host "ダウンロードに失敗しました: $_" -ForegroundColor Red
    exit 1
}
Write-Host "$ScriptPath に保存しました" -ForegroundColor Green

# 3. プロファイルに関数追加
if (-not (Test-Path $PROFILE)) {
    New-Item -ItemType File -Force -Path $PROFILE | Out-Null
}
$profileContent = Get-Content $PROFILE -ErrorAction SilentlyContinue
if ($profileContent -match "git-push-tool/safe_git_push.py") {
    Write-Host "関数 gitpush は既に $PROFILE に登録済みです（スキップ）" -ForegroundColor Yellow
}
else {
    Add-Content -Path $PROFILE -Value ""
    Add-Content -Path $PROFILE -Value "# Safe Git Push - https://github.com/ASDF3001/safe-git-push"
    Add-Content -Path $PROFILE -Value $FuncLine
    Write-Host "関数 gitpush を $PROFILE に追加しました" -ForegroundColor Green
}

Write-Host ("-" * 40)
Write-Host "インストール完了" -ForegroundColor Green
Write-Host "新しい PowerShell ウィンドウを開くか、以下を実行:" -ForegroundColor Yellow
Write-Host "  . `$PROFILE" -ForegroundColor Cyan
Write-Host "使い方: gitpush" -ForegroundColor Cyan
