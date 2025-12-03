# Slasher TV AI - Clean Deployment Script
# Builds locally and deploys only necessary files (no source code on server)

param(
    [string]$Server = "root@dev.thinkelution.com",
    [string]$KeyPath = "$HOME\.ssh\slasher_deploy_key",
    [string]$RemotePath = "/var/www/slasher-tv-ai",
    [switch]$SkipBuild,
    [switch]$BackupFirst
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$TempDeploy = "$ProjectRoot\deploy_package"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SLASHER TV AI - CLEAN DEPLOYMENT" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Build Frontend
if (-not $SkipBuild) {
    Write-Host "[1/6] Building Frontend..." -ForegroundColor Yellow
    Set-Location "$ProjectRoot\frontend"
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Frontend build failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "Frontend built successfully!" -ForegroundColor Green
} else {
    Write-Host "[1/6] Skipping frontend build..." -ForegroundColor Gray
}

# Step 2: Create clean deployment package
Write-Host "`n[2/6] Creating deployment package..." -ForegroundColor Yellow
Set-Location $ProjectRoot

# Remove old package if exists
if (Test-Path $TempDeploy) {
    Remove-Item -Recurse -Force $TempDeploy
}
New-Item -ItemType Directory -Path $TempDeploy | Out-Null

# Copy only necessary files
Write-Host "  Copying backend source..." -ForegroundColor Gray
Copy-Item -Recurse "$ProjectRoot\src" "$TempDeploy\src"

Write-Host "  Copying frontend build..." -ForegroundColor Gray
New-Item -ItemType Directory -Path "$TempDeploy\frontend" | Out-Null
Copy-Item -Recurse "$ProjectRoot\frontend\dist" "$TempDeploy\frontend\dist"

Write-Host "  Copying config files..." -ForegroundColor Gray
Copy-Item "$ProjectRoot\requirements.txt" "$TempDeploy\"
Copy-Item "$ProjectRoot\run_api.py" "$TempDeploy\"
Copy-Item "$ProjectRoot\sample-feed.csv" "$TempDeploy\"

# Remove unnecessary files from package
Write-Host "  Cleaning up package..." -ForegroundColor Gray
Get-ChildItem -Path "$TempDeploy" -Recurse -Include "__pycache__", "*.pyc", ".pytest_cache" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Deployment package created!" -ForegroundColor Green

# Step 3: Backup existing deployment (optional)
if ($BackupFirst) {
    Write-Host "`n[3/6] Backing up existing deployment..." -ForegroundColor Yellow
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    ssh -i $KeyPath $Server "if [ -d $RemotePath ]; then mv $RemotePath ${RemotePath}_backup_$timestamp; fi"
    Write-Host "Backup created: ${RemotePath}_backup_$timestamp" -ForegroundColor Green
} else {
    Write-Host "`n[3/6] Skipping backup..." -ForegroundColor Gray
}

# Step 4: Clean existing deployment on server
Write-Host "`n[4/6] Cleaning server deployment..." -ForegroundColor Yellow
ssh -i $KeyPath $Server @"
    # Preserve .env and assets
    if [ -d $RemotePath ]; then
        cp $RemotePath/.env /tmp/slasher_env_backup 2>/dev/null || true
        cp -r $RemotePath/assets /tmp/slasher_assets_backup 2>/dev/null || true
        rm -rf $RemotePath/*
    else
        mkdir -p $RemotePath
    fi
"@
Write-Host "Server cleaned!" -ForegroundColor Green

# Step 5: Upload deployment package
Write-Host "`n[5/6] Uploading to server..." -ForegroundColor Yellow
scp -i $KeyPath -r "$TempDeploy\*" "${Server}:${RemotePath}/"
Write-Host "Files uploaded!" -ForegroundColor Green

# Step 6: Setup server and restore configs
Write-Host "`n[6/6] Setting up server..." -ForegroundColor Yellow
ssh -i $KeyPath $Server @"
    cd $RemotePath
    
    # Restore .env and assets
    if [ -f /tmp/slasher_env_backup ]; then
        mv /tmp/slasher_env_backup $RemotePath/.env
        echo '  .env restored'
    fi
    if [ -d /tmp/slasher_assets_backup ]; then
        mv /tmp/slasher_assets_backup $RemotePath/assets
        echo '  assets restored'
    fi
    
    # Create venv if not exists
    if [ ! -d venv ]; then
        python3 -m venv venv
        echo '  Virtual environment created'
    fi
    
    # Install dependencies
    source venv/bin/activate
    pip install -r requirements.txt -q
    echo '  Dependencies installed'
    
    # Restart service
    systemctl restart slasher-api
    echo '  Service restarted'
    
    # Verify
    sleep 2
    if systemctl is-active --quiet slasher-api; then
        echo '  Service is running!'
    else
        echo '  WARNING: Service may have issues'
        systemctl status slasher-api --no-pager -l
    fi
"@

# Cleanup local temp folder
Remove-Item -Recurse -Force $TempDeploy

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nURL: https://dev.thinkelution.com/slasher/" -ForegroundColor Cyan
Write-Host "`nFiles deployed (no source on server):" -ForegroundColor Gray
Write-Host "  - src/ (Python backend)" -ForegroundColor Gray
Write-Host "  - frontend/dist/ (Built React)" -ForegroundColor Gray
Write-Host "  - requirements.txt, run_api.py" -ForegroundColor Gray
Write-Host "`nNOT on server:" -ForegroundColor Gray
Write-Host "  - .git/ (no git history)" -ForegroundColor Gray
Write-Host "  - frontend/src/ (no React source)" -ForegroundColor Gray
Write-Host "  - node_modules/" -ForegroundColor Gray

