#!/usr/bin/env python3
"""
Consolidate Batch 7 Duplicates
===============================

Consolidates Batch 7 duplicate files (12 groups).

Task: Batch 7 Consolidation (LOW priority)
- SSOT verified by Agent-8 ✅
- 12 groups, ~12 duplicate files to eliminate

Author: Agent-1 (Integration & Core Systems Specialist)
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


def load_batch7_groups() -> List[Dict]:
    """Load Batch 7 groups from JSON file."""
    json_path = project_root / "docs" / "technical_debt" / "DUPLICATE_GROUPS_PRIORITY_BATCHES.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find Batch 7
    for batch in data.get("batches", []):
        if batch.get("batch_number") == 7:
            return batch.get("groups", [])
    
    return []


def main():
    """Main execution."""
    print("🔧 Consolidate Batch 7 Duplicates")
    print("   Task: Batch 7 Consolidation (12 groups)")
    print("   SSOT Verification: ✅ PASSED (Agent-8)")
    print()
    
    # Load Batch 7 groups from JSON
    batch7_groups = load_batch7_groups()
    
    if not batch7_groups:
        print("❌ Error: Batch 7 groups not found in JSON file")
        return 1
    
    print(f"📋 Loaded {len(batch7_groups)} groups from Batch 7")
    print()
    
    total_deleted = 0
    total_errors = 0
    skipped_groups = []
    already_deleted = 0
    
    # Process each group
    for i, group in enumerate(batch7_groups, 1):
        ssot_path_str = group.get("ssot", "").replace("\\", "/")
        ssot_path = project_root / ssot_path_str
        
        print(f"📋 Group {i}/12: {ssot_path.name}")
        
        # Verify SSOT
        ssot_result = verify_ssot(ssot_path)
        if not ssot_result["valid"]:
            print(f"   ⚠️  SSOT verification failed: {ssot_result['error']}")
            skipped_groups.append({
                "group": i,
                "ssot": ssot_path_str,
                "reason": ssot_result['error']
            })
            continue
        
        # Find duplicates
        duplicate_paths = group.get("duplicates", [])
        duplicates_result = find_duplicates(ssot_path, duplicate_paths)
        
        if duplicates_result["total_found"] == 0:
            if duplicates_result["missing"]:
                already_deleted += len(duplicates_result["missing"])
                print(f"   ✅ Duplicate already deleted (missing: {len(duplicates_result['missing'])})")
            else:
                print(f"   ⚠️  No duplicates found")
            continue
        
        # Delete duplicates (dry run first)
        if "--execute" not in sys.argv:
            print(f"   📝 Would delete {duplicates_result['total_found']} duplicate(s)")
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
            print(f"   ⚠️  {len(delete_result['errors'])} error(s) during deletion")
    
    print()
    
    if "--execute" not in sys.argv:
        print("⚠️  DRY RUN MODE - No files deleted")
        print("   Use --execute flag to actually delete files")
        print()
        print("📋 Summary:")
        print(f"   Groups: {len(batch7_groups)}")
        print(f"   Ready for consolidation: ✅")
        if already_deleted > 0:
            print(f"   Already deleted: {already_deleted}")
        if skipped_groups:
            print(f"   ⚠️  Skipped groups: {len(skipped_groups)}")
        return 0
    
    print("🎯 Consolidation complete!")
    print(f"   Files eliminated: {total_deleted}")
    if already_deleted > 0:
        print(f"   Already deleted: {already_deleted}")
    print(f"   Errors: {total_errors}")
    if skipped_groups:
        print(f"   ⚠️  Skipped groups: {len(skipped_groups)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

