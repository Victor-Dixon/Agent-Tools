#!/usr/bin/env pwsh
# Cleanup Obsolete Documentation
# Removes old status files, coordination files, and cycle accomplishments

$obsoletePatterns = @(
    "*2025-01-27*.md",  # Old consolidation status files
    "CYCLE_ACCOMPLISHMENTS_*.md",  # Old cycle files
    "*BATCH*.md",  # Old batch files
    "*CONSOLIDATION_STATUS*.md",  # Old consolidation status
    "*SWARM_PROGRESS*.md",  # Old progress files
    "*SWARM_MOMENTUM*.md",  # Old momentum files
    "*SWARM_COORDINATION*.md",  # Old coordination files
    "*SWARM_METRICS*.md",  # Old metrics files
    "*DELETION_ANALYSIS*.md",  # Old deletion analysis
    "*REPO_COUNT*.md",  # Old repo count files
    "*ARCHIVED_VS_DELETED*.md",  # Old archive files
    "*PHASE1_ARCHIVING*.md",  # Old archiving files
    "*PR_MERGE*.md",  # Old PR merge files
    "*CONSOLIDATION_PROGRESS*.md",  # Old progress files
    "*CONSOLIDATION_FINAL*.md",  # Old final files
    "*TRADING_LEADS_BOT*.md",  # Old cleanup files
    "*CAPTAIN_DECISION*.md",  # Old decision files
    "*DELETION_DECISION*.md",  # Old decision files
    "*VERIFICATION_PLAN*.md",  # Old verification files
    "*JET_FUEL_MISSION*.md",  # Old mission files
    "*SWARM_ACTIVATION*.md",  # Old activation files
    "*COMPREHENSIVE_REPO*.md",  # Old repo analysis
    "*REPO_COUNT_COMPARISON*.md",  # Old comparison files
    "*MISSION_CLARIFICATION*.md",  # Old clarification files
    "*REVISED_MISSION*.md",  # Old mission files
    "*WORKFLOW_CLARIFICATION*.md",  # Old workflow files
    "*CLEAR_ASSIGNMENTS*.md",  # Old assignment files
    "*CAPTAIN_PATTERN*.md",  # Old pattern files
    "*SWARM_DISTRIBUTION*.md",  # Old distribution files
    "*MODEL_BEHAVIOR*.md",  # Old behavior files
    "*AUTONOMOUS_BEHAVIOR*.md",  # Old behavior files
    "*LOOP_BREAKING*.md"  # Old loop breaking files (keep protocol, remove status)
)

$directories = @(
    "agent_workspaces\Agent-4",
    "docs\cycles",
    "docs\organization"
)

$removedCount = 0
$keptFiles = @(
    "LOOP_BREAKING_PROTOCOL_2025-01-27.md",  # Keep protocol, not status
    "CAPTAINS_HANDBOOK.md",  # Keep handbook
    "CAPTAIN_LOG.md"  # Keep log
)

foreach ($dir in $directories) {
    if (Test-Path $dir) {
        Write-Host "Cleaning $dir..."
        foreach ($pattern in $obsoletePatterns) {
            $files = Get-ChildItem -Path $dir -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                if ($keptFiles -notcontains $file.Name) {
                    Write-Host "  Removing: $($file.FullName)"
                    Remove-Item $file.FullName -Force
                    $removedCount++
                }
            }
        }
    }
}

Write-Host "`nCleanup complete: $removedCount files removed"



