# Slasher TV AI - Server Cleanup Script
# Removes existing deployment from server

param(
    [string]$Server = "root@dev.thinkelution.com",
    [string]$KeyPath = "$HOME\.ssh\slasher_deploy_key",
    [string]$RemotePath = "/var/www/slasher-tv-ai",
    [switch]$KeepBackup,
    [switch]$Force
)

Write-Host "`n========================================" -ForegroundColor Red
Write-Host "  SERVER CLEANUP - SLASHER TV AI" -ForegroundColor Red
Write-Host "========================================`n" -ForegroundColor Red

if (-not $Force) {
    Write-Host "This will remove the following from the server:" -ForegroundColor Yellow
    Write-Host "  - $RemotePath (main deployment)" -ForegroundColor Gray
    Write-Host "  - $RemotePath-old (old backup if exists)" -ForegroundColor Gray
    Write-Host "  - slasher-api systemd service" -ForegroundColor Gray
    Write-Host ""
    $confirm = Read-Host "Are you sure? Type 'YES' to confirm"
    if ($confirm -ne "YES") {
        Write-Host "Cancelled." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host "`n[1/4] Stopping service..." -ForegroundColor Yellow
ssh -i $KeyPath $Server "systemctl stop slasher-api 2>/dev/null || true"
Write-Host "Service stopped." -ForegroundColor Green

Write-Host "`n[2/4] Backing up .env file..." -ForegroundColor Yellow
ssh -i $KeyPath $Server @"
    if [ -f $RemotePath/.env ]; then
        cp $RemotePath/.env ~/slasher_env_backup_$(date +%Y%m%d_%H%M%S)
        echo 'Backup saved to home directory'
    fi
"@

Write-Host "`n[3/4] Removing deployment files..." -ForegroundColor Yellow
ssh -i $KeyPath $Server @"
    rm -rf $RemotePath
    rm -rf ${RemotePath}-old
    rm -rf /var/www/slasher-tv-ai-old
    echo 'Deployment files removed'
"@
Write-Host "Files removed." -ForegroundColor Green

if (-not $KeepBackup) {
    Write-Host "`n[4/4] Listing remaining backups..." -ForegroundColor Yellow
    ssh -i $KeyPath $Server "ls -la ~/ | grep slasher"
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nThe server is now clean." -ForegroundColor Gray
Write-Host "Run .\deploy.ps1 to deploy fresh." -ForegroundColor Cyan

