# Safe Git Push - Uninstaller (Windows / PowerShell)
# 使い方 / Usage:
#   irm https://raw.githubusercontent.com/ASDF3001/safe-git-push/main/windows/uninstall.ps1 | iex
#   または / Or:  powershell -ExecutionPolicy Bypass -File uninstall.ps1

$ErrorActionPreference = "SilentlyContinue"

Write-Host "Safe Git Push をアンインストールします / Uninstalling Safe Git Push..." -ForegroundColor Cyan

# 1. PowerShell プロファイルから gitpush 関数を削除
$profilePath = $PROFILE
if (Test-Path $profilePath) {
    $lines = Get-Content $profilePath
    $filtered = $lines | Where-Object { $_ -notmatch 'function gitpush' -and $_ -notmatch 'safe_git_push\.py' }
    if ($filtered.Count -ne $lines.Count) {
        Set-Content -Path $profilePath -Value $filtered
        Write-Host "[ok] Removed gitpush function from $profilePath" -ForegroundColor Green
    }
}

# 2. インストールフォルダを削除
$toolDir = Join-Path $HOME "git-push-tool"
if (Test-Path $toolDir) {
    Remove-Item -Recurse -Force $toolDir
    Write-Host "[ok] Removed $toolDir" -ForegroundColor Green
}

# 3. exe をカレントディレクトリに置いた場合の案内
Write-Host "[note] gitpush.exe を手動で別フォルダに置いた場合は、そちらも手動で削除してください / If you placed gitpush.exe manually, delete it yourself." -ForegroundColor Yellow

Write-Host "完了 / Done." -ForegroundColor Green
