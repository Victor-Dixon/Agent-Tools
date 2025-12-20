#!/usr/bin/env python3
"""
⚠️ DEPRECATED: This tool has been archived.
Use unified_validator.py instead (consolidated validation system).
Archived: 2025-12-08
Replacement: tools.unified_validator.UnifiedValidator
"""
"""
Archive Communication Validation Tools
======================================

Archives tools that have been consolidated into tools/communication/ core tools.

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-03
Task: Phase 2 Tools Consolidation - Communication Validation Migration
"""

import shutil
from pathlib import Path

ARCHIVE_DIR = Path("tools/deprecated/consolidated_2025-12-03")
TOOLS_TO_ARCHIVE = [
    "discord_message_validator.py",
    "check_agent_status_staleness.py",
    "agent_status_quick_check.py",
    "check_status_monitor_and_agent_statuses.py",
    "check_integration_issues.py",
    "integration_health_checker.py",
    "check_queue_status.py",
    "session_transition_validator.py",
    "validate_session_transition.py",
]

def main():
    """Archive consolidated tools."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    archived = []
    not_found = []
    
    for tool in TOOLS_TO_ARCHIVE:
        src = Path(f"tools/{tool}")
        if src.exists():
            dst = ARCHIVE_DIR / tool
            shutil.move(str(src), str(dst))
            archived.append(tool)
            print(f"✅ Archived: {tool}")
        else:
            not_found.append(tool)
            print(f"⚠️  Not found: {tool}")
    
    print(f"\n📊 Summary:")
    print(f"  Archived: {len(archived)}/{len(TOOLS_TO_ARCHIVE)}")
    if not_found:
        print(f"  Not found: {len(not_found)}")
        for tool in not_found:
            print(f"    - {tool}")

if __name__ == "__main__":
    main()


