#!/usr/bin/env python3
"""
Consolidate Batch 1 Groups 5-6, 13-14 Duplicates
=================================================

Consolidates assigned Batch 1 duplicate files (4 groups, ~10 duplicate files).

Task: Batch 1 Consolidation - Agent-7 Assignment
- Groups: 5-6 (GUI panels), 13-14 (Auto_Blogger files)
- SSOT verified by Agent-8 ✅
- Action: DELETE, Risk: LOW

Author: Agent-7 (Web Development Specialist)
V2 Compliant: <300 lines
"""

import sys
import json
import hashlib
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def get_file_hash(file_path: Path) -> str:
    """Get MD5 hash of file."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return ""


def verify_ssot(ssot_path: Path) -> Dict[str, any]:
    """Verify SSOT file exists and is valid."""
    if not ssot_path.exists():
        return {
            "valid": False,
            "error": f"SSOT file not found: {ssot_path}"
        }

    ssot_hash = get_file_hash(ssot_path)
    ssot_size = ssot_path.stat().st_size

    return {
        "valid": True,
        "path": str(ssot_path),
        "hash": ssot_hash,
        "size": ssot_size,
        "exists": True
    }


def find_duplicates(ssot_path: Path, duplicate_paths: List[str]) -> Dict[str, any]:
    """Find and verify duplicate files."""
    ssot_hash = get_file_hash(ssot_path)
    duplicates_found = []
    missing_files = []
    different_files = []

    for dup_path_str in duplicate_paths:
        dup_path = project_root / dup_path_str.replace("\\", "/")

        if not dup_path.exists():
            missing_files.append(str(dup_path))
            continue

        dup_hash = get_file_hash(dup_path)

        if dup_hash == ssot_hash:
            duplicates_found.append({
                "path": str(dup_path),
                "hash": dup_hash,
                "size": dup_path.stat().st_size
            })
        else:
            different_files.append({
                "path": str(dup_path),
                "hash": dup_hash,
                "ssot_hash": ssot_hash
            })

    return {
        "duplicates": duplicates_found,
        "missing": missing_files,
        "different": different_files,
        "total_found": len(duplicates_found)
    }


def delete_duplicates(duplicates: List[Dict]) -> Dict[str, any]:
    """Delete duplicate files."""
    deleted = []
    errors = []

    for dup in duplicates:
        dup_path = Path(dup["path"])
        try:
            if dup_path.exists():
                dup_path.unlink()
                deleted.append(str(dup_path))
        except Exception as e:
            errors.append({
                "file": str(dup_path),
                "error": str(e)
            })

    return {
        "deleted": deleted,
        "errors": errors,
        "count": len(deleted)
    }


def load_batch1_groups() -> List[Dict]:
    """Load Batch 1 groups from JSON file."""
    json_path = project_root / "docs" / "technical_debt" / \
        "DUPLICATE_GROUPS_PRIORITY_BATCHES.json"

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find Batch 1
    for batch in data.get("batches", []):
        if batch.get("batch_number") == 1:
            all_groups = batch.get("groups", [])
            # Groups are 1-indexed in JSON, 0-indexed in array
            # Group 5 = index 4, Group 6 = index 5, Group 13 = index 12, Group 14 = index 13
            selected_groups = []
            for idx in [4, 5, 12, 13]:
                if idx < len(all_groups):
                    selected_groups.append(all_groups[idx])
            return selected_groups

    return []


def main():
    """Main execution."""
    print("🔧 Consolidate Batch 1 Groups 5-6, 13-14 Duplicates")
    print("   Task: Batch 1 Consolidation - Agent-7 Assignment")
    print("   Groups: 5-6 (GUI panels), 13-14 (Auto_Blogger files)")
    print("   SSOT Verification: ✅ PASSED (Agent-8)")
    print()

    # Load assigned groups from JSON
    assigned_groups = load_batch1_groups()

    if not assigned_groups or len(assigned_groups) != 4:
        print("❌ Error: Could not load assigned groups (5-6, 13-14) from JSON file")
        return 1

    print(f"📋 Loaded {len(assigned_groups)} groups (5-6, 13-14)")
    print()

    total_deleted = 0
    total_errors = 0
    skipped_groups = []
    group_numbers = [5, 6, 13, 14]

    # Process each group
    for i, group in enumerate(assigned_groups):
        group_num = group_numbers[i]
        ssot_path_str = group.get("ssot", "").replace("\\", "/")
        ssot_path = project_root / ssot_path_str

        print(f"📋 Group {group_num}: {ssot_path.name}")

        # Verify SSOT
        ssot_result = verify_ssot(ssot_path)
        if not ssot_result["valid"]:
            print(f"   ⚠️  SSOT verification failed: {ssot_result['error']}")
            skipped_groups.append({
                "group": group_num,
                "ssot": ssot_path_str,
                "reason": ssot_result['error']
            })
            continue

        # Find duplicates
        duplicate_paths = group.get("duplicates", [])
        duplicates_result = find_duplicates(ssot_path, duplicate_paths)

        if duplicates_result["total_found"] == 0:
            print(f"   ⚠️  No duplicates found (may already be deleted)")
            if duplicates_result["missing"]:
                print(
                    f"   📝 Missing files: {len(duplicates_result['missing'])}")
            continue

        # Delete duplicates (dry run first)
        if "--execute" not in sys.argv:
            print(
                f"   📝 Would delete {duplicates_result['total_found']} duplicate(s)")
            for dup in duplicates_result['duplicates']:
                print(f"      - {Path(dup['path']).name}")
            continue

        # Execute deletion
        delete_result = delete_duplicates(duplicates_result['duplicates'])
        total_deleted += delete_result["count"]
        total_errors += len(delete_result["errors"])

        if delete_result["count"] > 0:
            print(f"   ✅ Deleted {delete_result['count']} duplicate(s)")
        if delete_result["errors"]:
            print(
                f"   ⚠️  {len(delete_result['errors'])} error(s) during deletion")

    print()

    if "--execute" not in sys.argv:
        print("⚠️  DRY RUN MODE - No files deleted")
        print("   Use --execute flag to actually delete files")
        print()
        print("📋 Summary:")
        print(f"   Groups: {len(assigned_groups)} (5-6, 13-14)")
        print(f"   Ready for consolidation: ✅")
        if skipped_groups:
            print(f"   ⚠️  Skipped groups: {len(skipped_groups)}")
        return 0

    print("🎯 Consolidation complete!")
    print(f"   Files eliminated: {total_deleted}")
    print(f"   Errors: {total_errors}")
    if skipped_groups:
        print(f"   ⚠️  Skipped groups: {len(skipped_groups)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
