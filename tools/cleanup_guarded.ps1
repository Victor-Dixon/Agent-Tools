param(
  [ValidateSet("conservative","moderate","aggressive")]
  [string]$Mode = "conservative",
  [switch]$DryRun,
  [string]$BackupRoot = "backups\cleanup"
)

function Stamp { (Get-Date -Format "yyyyMMddTHHmmssZ") }
$stamp = Stamp
$backupDir = Join-Path $BackupRoot $stamp
$manifest = @()

function Ensure-Dir($p) { if (-not (Test-Path $p)) { New-Item -ItemType Directory -Force -Path $p | Out-Null } }

function Move-Safe($path) {
  if (Test-Path $path) {
    $absSrc = Resolve-Path $path
    $relPath = Resolve-Path -Relative $path
    if ($relPath.StartsWith('.\')) { $relPath = $relPath.Substring(2) }
    $dst = Join-Path $backupDir $relPath
    Ensure-Dir (Split-Path $dst -Parent)
    if ($DryRun) { Write-Host "[DRY] MOVE $absSrc -> $dst"; }
    else { Move-Item -Force $absSrc $dst }
    $manifest += [pscustomobject]@{ action="move"; src="$absSrc"; dst="$dst" }
  }
}

function Remove-Safe($path) {
  if (Test-Path $path) {
    $rel = Resolve-Path $path
    if ($DryRun) { Write-Host "[DRY] DELETE $rel"; }
    else { Remove-Item -Force -Recurse $rel }
    $manifest += [pscustomobject]@{ action="delete"; src="$rel" }
  }
}

Ensure-Dir $backupDir

# 1) Debug/Temp files (delete)
foreach ($f in @("debug_imports.py","fix_manager_results.py")) { Remove-Safe $f }

# 2) Old agent inbox messages (move to backup)
Get-ChildItem -Recurse -Directory -Filter "inbox" -Path "agent_workspaces","agents" -ErrorAction SilentlyContinue |
  ForEach-Object { Get-ChildItem $_.FullName -Force -ErrorAction SilentlyContinue | ForEach-Object { Move-Safe $_.FullName } }

# 3) Old system logs (delete)
foreach ($f in @("logs/messaging_20250903.log","logs/messaging_coordination_20250903.log")) { Remove-Safe $f }

# 4) Runtime reports (moderate+)
if ($Mode -in @("moderate","aggressive")) {
  Get-ChildItem "runtime/reports" -Filter "cleanup_*" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -Skip 3 | ForEach-Object { Move-Safe $_.FullName }
}

# 5) Archive dir (aggressive: move to devlogs/archive)
if ($Mode -eq "aggressive") {
  if (Test-Path "archive") {
    Ensure-Dir "devlogs/archive"
    Get-ChildItem "archive" -Force -ErrorAction SilentlyContinue | ForEach-Object { Move-Safe $_.FullName }
    if (-not $DryRun) { Remove-Item -Force -Recurse "archive" }
  }
}

# 6) Devlogs (aggressive: archive >14d)
if ($Mode -eq "aggressive") {
  Ensure-Dir "devlogs/archive/old_logs_$stamp"
  Get-ChildItem "devlogs" -Recurse -Include *.md -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-14) } |
    ForEach-Object { Move-Safe $_.FullName }
}

# Save manifest
Ensure-Dir $backupDir
$manifestPath = Join-Path $backupDir "manifest.json"
$manifest | ConvertTo-Json -Depth 5 | Out-File -FilePath $manifestPath -Encoding utf8
Write-Host "✅ Cleanup ($Mode) complete. Backup: $backupDir"
Write-Host "📄 Manifest: $manifestPath"
if ($DryRun) { Write-Host "ℹ️ DRY-RUN only — no changes were made." }
