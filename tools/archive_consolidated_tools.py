#!/usr/bin/env python3
"""
Archive Consolidated Tools - Agent-8
=====================================

Identifies and archives tools that have been consolidated into unified tools.
"""

import shutil
from pathlib import Path
from datetime import datetime

# Tool mappings: consolidated tool → unified tool
CONSOLIDATION_MAP = {
    # Monitoring tools → unified_monitor.py
    "monitor_github_pusher.py": "unified_monitor.py",
    "monitor_disk_and_ci.py": "unified_monitor.py",
    "monitor_digitaldreamscape_queue.py": "unified_monitor.py",
    "agent_progress_tracker.py": "unified_monitor.py",
    "automated_test_coverage_tracker.py": "unified_monitor.py",
    "infrastructure_automation_monitor.py": "unified_monitor.py",
    "infrastructure_health_dashboard.py": "unified_monitor.py",
    
    # Analysis tools → unified_analyzer.py
    "analyze_autoblogger_merge.py": "unified_analyzer.py",
    "analyze_development_journey.py": "unified_analyzer.py",
    "analyze_disk_usage.py": "unified_analyzer.py",
    "analyze_dreamvault_duplicates.py": "unified_analyzer.py",
    "analyze_duplicate_groups.py": "unified_analyzer.py",
    "analyze_init_files.py": "unified_analyzer.py",
    "analyze_local_duplicates.py": "unified_analyzer.py",
    "analyze_merged_repo_patterns.py": "unified_analyzer.py",
    "analyze_repo_duplicates.py": "unified_analyzer.py",
    "analyze_stress_test_metrics.py": "unified_analyzer.py",
    "analyze_test_coverage_gaps.py": "unified_analyzer.py",
    "analyze_unneeded_functionality.py": "unified_analyzer.py",
    "comprehensive_project_analyzer_BACKUP_PRE_REFACTOR.py": "unified_analyzer.py",
    "comprehensive_repo_analysis.py": "unified_analyzer.py",
    
    # Validation tools → unified_validator.py
    "validate_imports.py": "unified_validator.py",
    "validate_queue_behavior_under_load.py": "unified_validator.py",
    "arch_pattern_validator.py": "unified_validator.py",
    "coverage_validator.py": "unified_validator.py",
    "integrity_validator.py": "unified_validator.py",
    "passdown_validator.py": "unified_validator.py",
    "refactor_validator.py": "unified_validator.py",
    
    # Test coverage tools → unified_test_coverage.py
    "test_coverage_tracker.py": "unified_test_coverage.py",
    "test_coverage_prioritizer.py": "unified_test_coverage.py",
    "analyze_test_coverage_gaps_clean.py": "unified_test_coverage.py",
    
    # Test analysis tools → unified_test_analysis.py
    "test_all_discord_commands.py": "unified_test_analysis.py",
}

def archive_tools(dry_run=True):
    """Archive consolidated tools."""
    tools_dir = Path(__file__).parent
    archive_dir = tools_dir / "deprecated" / "consolidated_2025-11-30"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    archived = []
    not_found = []
    
    for tool_name, unified_tool in CONSOLIDATION_MAP.items():
        tool_path = tools_dir / tool_name
        
        if not tool_path.exists():
            not_found.append(tool_name)
            continue
            
        # Skip if already archived
        if (archive_dir / tool_name).exists():
            continue
            
        if not dry_run:
            shutil.move(str(tool_path), str(archive_dir / tool_name))
            archived.append(tool_name)
            print(f"✅ Archived: {tool_name} → {unified_tool}")
        else:
            archived.append(tool_name)
            print(f"📦 Would archive: {tool_name} → {unified_tool}")
    
    print(f"\n📊 Summary:")
    print(f"   Archived: {len(archived)}")
    print(f"   Not found: {len(not_found)}")
    
    if not_found:
        print(f"\n⚠️  Not found (may already be archived):")
        for tool in not_found:
            print(f"   - {tool}")
    
    return archived, not_found

if __name__ == "__main__":
    import sys
    dry_run = "--execute" not in sys.argv
    
    if dry_run:
        print("🔍 DRY RUN MODE - Use --execute to actually archive\n")
    else:
        print("🚀 EXECUTING ARCHIVE\n")
    
    archived, not_found = archive_tools(dry_run=dry_run)
    
    if dry_run:
        print(f"\n💡 Run with --execute to archive {len(archived)} tools")



