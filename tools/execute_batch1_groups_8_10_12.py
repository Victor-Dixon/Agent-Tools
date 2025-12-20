#!/usr/bin/env python3
"""
Execute Batch 1 Duplicate Consolidation - Groups 8, 10-12
==========================================================

Deletes duplicate files for Agent-1's assigned groups:
- Group 8: file_locking (core systems)
- Groups 10-12: Auto_Blogger test files

Author: Agent-1 (Integration & Core Systems)
Date: 2025-12-18
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

# Group assignments for Agent-1
GROUPS = {
    8: {
        "ssot": "src/core/file_locking/file_locking_orchestrator.py",
        "duplicates": [
            "src/core/file_locking/operations/lock_operations.py"
        ]
    },
    10: {
        "ssot": "temp_repos/Auto_Blogger/tests/auth.e2e.test.js",
        "duplicates": [
            "agent_workspaces/Agent-1/extracted_patterns/testing_patterns/auth.e2e.test.js"
        ]
    },
    11: {
        "ssot": "temp_repos/Auto_Blogger/tests/email.e2e.test.js",
        "duplicates": [
            "agent_workspaces/Agent-1/extracted_patterns/testing_patterns/email.e2e.test.js"
        ]
    },
    12: {
        "ssot": "temp_repos/Auto_Blogger/tests/jest.setup.js",
        "duplicates": [
            "agent_workspaces/Agent-1/extracted_patterns/testing_patterns/jest.setup.js"
        ]
    }
}

def verify_ssot(group_num, ssot_path):
    """Verify SSOT file exists and is valid."""
    ssot_file = project_root / ssot_path
    if not ssot_file.exists():
        print(f"❌ Group {group_num}: SSOT file not found: {ssot_path}")
        return False
    try:
        if ssot_file.stat().st_size == 0:
            print(f"❌ Group {group_num}: SSOT file is empty: {ssot_path}")
            return False
    except Exception as e:
        print(f"❌ Group {group_num}: SSOT file error: {ssot_path} - {e}")
        return False
    print(f"✅ Group {group_num}: SSOT verified: {ssot_path}")
    return True

def delete_duplicate(group_num, dup_path):
    """Delete a duplicate file."""
    dup_file = project_root / dup_path
    if not dup_file.exists():
        print(f"⚠️  Group {group_num}: Duplicate already missing: {dup_path}")
        return True  # Already deleted, consider success
    
    try:
        dup_file.unlink()
        print(f"✅ Group {group_num}: Deleted duplicate: {dup_path}")
        return True
    except Exception as e:
        print(f"❌ Group {group_num}: Failed to delete {dup_path}: {e}")
        return False

def main():
    """Main execution."""
    print("🔧 Batch 1 Duplicate Consolidation - Groups 8, 10-12")
    print("=" * 60)
    print()
    
    total_deleted = 0
    total_failed = 0
    
    for group_num, group_data in GROUPS.items():
        print(f"\n📦 Processing Group {group_num}")
        print("-" * 60)
        
        # Verify SSOT
        ssot_path = group_data["ssot"]
        if not verify_ssot(group_num, ssot_path):
            print(f"❌ Group {group_num}: Skipping - SSOT invalid")
            total_failed += len(group_data["duplicates"])
            continue
        
        # Delete duplicates
        for dup_path in group_data["duplicates"]:
            if delete_duplicate(group_num, dup_path):
                total_deleted += 1
            else:
                total_failed += 1
    
    print()
    print("=" * 60)
    print("📊 EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Total Groups Processed: {len(GROUPS)}")
    print(f"Files Deleted: {total_deleted}")
    print(f"Files Failed: {total_failed}")
    
    if total_failed == 0:
        print()
        print("✅ ALL DUPLICATES DELETED SUCCESSFULLY")
        return 0
    else:
        print()
        print(f"⚠️  {total_failed} files failed to delete")
        return 1

if __name__ == "__main__":
    sys.exit(main())

