# Clear GH_TOKEN and run gh auth login
$env:GH_TOKEN = $null
Remove-Item Env:\GH_TOKEN -ErrorAction SilentlyContinue
Write-Host "Cleared GH_TOKEN. Starting authentication..." -ForegroundColor Cyan
gh auth login

