# Fix GitHub CLI Authentication
# ==============================
# 
# This script clears the GH_TOKEN environment variable and helps you
# authenticate with GitHub CLI properly.
#
# Author: Agent-6 (Coordination & Communication Specialist)
# Date: 2025-12-05

Write-Host "Fixing GitHub CLI Authentication..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Clear GH_TOKEN environment variable
Write-Host "Step 1: Clearing GH_TOKEN environment variable..." -ForegroundColor Yellow
$env:GH_TOKEN = $null
Remove-Item Env:\GH_TOKEN -ErrorAction SilentlyContinue
Write-Host "GH_TOKEN cleared" -ForegroundColor Green
Write-Host ""

# Step 2: Check current auth status
Write-Host "Step 2: Checking current authentication status..." -ForegroundColor Yellow
gh auth status
Write-Host ""

# Step 3: Instructions for manual login
Write-Host "Step 3: Run the following command to authenticate:" -ForegroundColor Yellow
Write-Host "  gh auth login" -ForegroundColor White
Write-Host ""
Write-Host "When prompted:" -ForegroundColor Cyan
Write-Host "  1. Select 'GitHub.com'" -ForegroundColor White
Write-Host "  2. Choose 'HTTPS' or 'SSH' (HTTPS recommended)" -ForegroundColor White
Write-Host "  3. Authenticate Git credential helper: Yes" -ForegroundColor White
Write-Host "  4. Choose 'Login with a web browser'" -ForegroundColor White
Write-Host "  5. Copy the code and press Enter" -ForegroundColor White
Write-Host "  6. Authorize in your browser" -ForegroundColor White
Write-Host ""

# Step 4: Verify after login
Write-Host "Step 4: After logging in, verify with:" -ForegroundColor Yellow
Write-Host "  gh auth status" -ForegroundColor White
Write-Host ""

Write-Host "Setup complete! Run 'gh auth login' now." -ForegroundColor Green
