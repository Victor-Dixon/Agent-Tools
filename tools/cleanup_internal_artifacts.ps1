<#!
Repo Cleanup Script (draft) - internal artifact pruning for public migration
Prereqs: approvals from Agent-5 (PII/compliance), Agent-6 (comms/locks), Agent-8 (SSOT keepers)
This script is non-destructive to working tree; it only removes tracked internal artifacts from git index.
#>

Continue = 'Stop'

Write-Host "[1/6] Appending .gitignore entries" -ForegroundColor Cyan
 = @(
    'devlogs/',
    'agent_workspaces/',
    'swarm_brain/',
    'docs/organization/',
    'artifacts/',
    'runtime/',
    'data/'
)
 = Join-Path -Path (Get-Location) -ChildPath '.gitignore'
 | ForEach-Object { Add-Content -Path  -Value  }

Write-Host "[2/6] Snapshotting pre-tracked internal files" -ForegroundColor Cyan
git ls-tree -r --name-only HEAD devlogs agent_workspaces swarm_brain docs/organization artifacts runtime data > cleanup_pretracked.txt

Write-Host "[3/6] Pruning index (keeping files locally)" -ForegroundColor Cyan
git rm -r --cached devlogs agent_workspaces swarm_brain docs/organization artifacts runtime data

Write-Host "[4/6] Snapshotting post-tracked files" -ForegroundColor Cyan
git ls-tree -r --name-only HEAD > cleanup_posttracked.txt

git status --short

Write-Host "[5/6] Clean-clone verification" -ForegroundColor Cyan
 = "..\_clean_clone"
if (Test-Path ) { Remove-Item -Recurse -Force  }
git clone . 
Push-Location 
python -m pytest tests/unit/infrastructure/test_unified_browser_service.py -q --disable-warnings --maxfail=1
Pop-Location

Write-Host "[6/6] Done. Review cleanup_pretracked.txt and cleanup_posttracked.txt" -ForegroundColor Green
