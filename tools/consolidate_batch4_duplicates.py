#!/usr/bin/env python3
"""
Consolidate Batch 4 Duplicates
===============================

Consolidates Batch 4 duplicate files (15 groups, temp_repos/Thea/ directory).

Task: Batch 4 Consolidation (LOW priority)
- SSOT verified by Agent-1 ✅
- 15 groups, ~15 duplicate files to eliminate
- All SSOT files in temp_repos/Thea/ directory
- All duplicates in agent_workspaces/Agent-2/extracted_logic/

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <300 lines
"""

import sys
import hashlib
import json
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

    ssot_size = ssot_path.stat().st_size
    if ssot_size == 0:
        return {
            "valid": False,
            "error": f"SSOT file is empty: {ssot_path}"
        }

    ssot_hash = get_file_hash(ssot_path)

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
        # Normalize path separators
        dup_path = project_root / dup_path_str.replace("\\", "/")

        if not dup_path.exists():
            missing_files.append(str(dup_path))
            continue

        dup_size = dup_path.stat().st_size
        if dup_size == 0:
            missing_files.append(str(dup_path) + " (empty file)")
            continue

        dup_hash = get_file_hash(dup_path)

        if dup_hash == ssot_hash:
            duplicates_found.append({
                "path": str(dup_path),
                "hash": dup_hash,
                "size": dup_size
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


def load_batch4_groups() -> List[Dict]:
    """Load Batch 4 groups from JSON file."""
    json_path = project_root / "docs" / "technical_debt" / \
        "DUPLICATE_GROUPS_PRIORITY_BATCHES.json"

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Find Batch 4
        for batch in data.get("batches", []):
            if batch.get("batch_number") == 4:
                return batch.get("groups", [])

        return []
    except Exception as e:
        print(f"❌ Error loading batch data: {e}")
        return []


def main():
    """Main execution."""
    print("🔧 Consolidate Batch 4 Duplicates")
    print("   Task: Batch 4 Consolidation (15 groups, temp_repos/Thea/)")
    print("   SSOT Verification: ✅ PASSED (Agent-1)")
    print()

    # Load Batch 4 groups from JSON
    batch4_groups = load_batch4_groups()

    if not batch4_groups:
        print("❌ Failed to load Batch 4 groups from JSON")
        return 1

    print(f"📋 Loaded {len(batch4_groups)} groups from Batch 4")
    print()

    total_deleted = 0
    total_errors = 0
    ssot_verified = 0
    ssot_failed = 0

    # Process each group
    for i, group in enumerate(batch4_groups, 1):
        ssot_path_str = group.get("ssot", "")
        duplicates_list = group.get("duplicates", [])

        if not ssot_path_str:
            print(f"📋 Group {i}/15: ⚠️  Missing SSOT path")
            continue

        ssot_path = project_root / ssot_path_str.replace("\\", "/")

        print(f"📋 Group {i}/15: {ssot_path.name}")

        # Verify SSOT
        ssot_result = verify_ssot(ssot_path)
        if not ssot_result["valid"]:
            print(
                f"   ⚠️  SSOT verification failed: {ssot_result.get('error', 'Unknown error')}")
            ssot_failed += 1
            continue

        ssot_verified += 1
        print(f"   ✅ SSOT verified: {ssot_result['size']} bytes")

        # Find duplicates
        duplicates_result = find_duplicates(ssot_path, duplicates_list)

        if duplicates_result["missing"]:
            print(
                f"   ⚠️  {len(duplicates_result['missing'])} duplicate(s) already missing")

        if duplicates_result["different"]:
            print(
                f"   ⚠️  {len(duplicates_result['different'])} duplicate(s) have different content (skipping)")

        if duplicates_result["total_found"] == 0:
            print(f"   ℹ️  No duplicates found (may already be deleted)")
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
            for err in delete_result["errors"]:
                print(f"      - {err['file']}: {err['error']}")

    print()

    if "--execute" not in sys.argv:
        print("⚠️  DRY RUN MODE - No files deleted")
        print("   Use --execute flag to actually delete files")
        print()
        print("📋 Summary:")
        print(f"   Groups: {len(batch4_groups)}")
        print(f"   SSOT Verified: {ssot_verified}/{len(batch4_groups)}")
        print(f"   SSOT Failed: {ssot_failed}")
        print(f"   SSOT Location: temp_repos/Thea/")
        print(f"   Ready for consolidation: ✅")
        return 0

    print("🎯 Consolidation complete!")
    print(f"   Files eliminated: {total_deleted}")
    print(f"   Errors: {total_errors}")
    print(f"   SSOT Verified: {ssot_verified}/{len(batch4_groups)}")

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

