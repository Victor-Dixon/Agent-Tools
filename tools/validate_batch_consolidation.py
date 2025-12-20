#!/usr/bin/env python3
"""
Batch Consolidation Validation Tool
===================================

Validates batch consolidation readiness:
- SSOT file verification
- File system health checks
- Pre-deletion validation
- Infrastructure readiness

Author: Agent-7 (Web Development Specialist)
V2 Compliant: < 300 lines
"""

import sys
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple

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
    
    try:
        ssot_hash = get_file_hash(ssot_path)
        ssot_size = ssot_path.stat().st_size
        
        return {
            "valid": True,
            "path": str(ssot_path),
            "hash": ssot_hash,
            "size": ssot_size,
            "exists": True
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"SSOT file validation failed: {str(e)}"
        }


def check_duplicate_files(ssot_path: Path, duplicate_paths: List[str]) -> Dict[str, any]:
    """Check duplicate files before deletion."""
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
        "total_found": len(duplicates_found),
        "ready_for_deletion": len(duplicates_found) > 0 and len(different_files) == 0
    }


def validate_batch(batch_number: int) -> Dict[str, any]:
    """Validate a batch for consolidation readiness."""
    json_path = project_root / "docs" / "technical_debt" / \
        "DUPLICATE_GROUPS_PRIORITY_BATCHES.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find batch
    batch_data = None
    for batch in data.get("batches", []):
        if batch.get("batch_number") == batch_number:
            batch_data = batch
            break
    
    if not batch_data:
        return {
            "valid": False,
            "error": f"Batch {batch_number} not found"
        }
    
    groups = batch_data.get("groups", [])
    validation_results = {
        "batch_number": batch_number,
        "total_groups": len(groups),
        "groups_validated": 0,
        "groups_ready": 0,
        "groups_with_issues": 0,
        "ssot_issues": [],
        "duplicate_issues": [],
        "ready": False
    }
    
    for i, group in enumerate(groups, 1):
        ssot_path_str = group.get("ssot", "").replace("\\", "/")
        ssot_path = project_root / ssot_path_str
        
        # Verify SSOT
        ssot_result = verify_ssot(ssot_path)
        if not ssot_result["valid"]:
            validation_results["ssot_issues"].append({
                "group": i,
                "ssot": ssot_path_str,
                "error": ssot_result["error"]
            })
            validation_results["groups_with_issues"] += 1
            continue
        
        # Check duplicates
        duplicate_paths = group.get("duplicates", [])
        dup_result = check_duplicate_files(ssot_path, duplicate_paths)
        
        # Group is ready if: duplicates found and match SSOT, OR all duplicates already deleted
        if dup_result["ready_for_deletion"]:
            validation_results["groups_ready"] += 1
        elif len(dup_result["missing"]) == len(duplicate_paths) and len(dup_result["duplicates"]) == 0:
            # All duplicates already deleted - group is already consolidated
            validation_results["groups_ready"] += 1
        else:
            if dup_result["different"]:
                validation_results["duplicate_issues"].append({
                    "group": i,
                    "ssot": ssot_path_str,
                    "issue": "Duplicates have different content than SSOT",
                    "count": len(dup_result["different"])
                })
            validation_results["groups_with_issues"] += 1
        
        validation_results["groups_validated"] += 1
    
    # Batch is ready if all groups are ready
    validation_results["ready"] = (
        validation_results["groups_ready"] == validation_results["total_groups"] and
        len(validation_results["ssot_issues"]) == 0 and
        len(validation_results["duplicate_issues"]) == 0
    )
    
    return validation_results


def main():
    """Main execution."""
    if len(sys.argv) < 2:
        print("Usage: python validate_batch_consolidation.py <batch_number>")
        print("Example: python validate_batch_consolidation.py 6")
        return 1
    
    try:
        batch_number = int(sys.argv[1])
    except ValueError:
        print(f"Error: Invalid batch number: {sys.argv[1]}")
        return 1
    
    print(f"🔍 Validating Batch {batch_number} Consolidation Readiness")
    print()
    
    result = validate_batch(batch_number)
    
    if not result.get("valid", True) and "error" in result:
        print(f"❌ Error: {result['error']}")
        return 1
    
    print(f"📋 Batch {batch_number} Validation Results:")
    print(f"   Total Groups: {result['total_groups']}")
    print(f"   Groups Validated: {result['groups_validated']}")
    print(f"   Groups Ready: {result['groups_ready']}")
    print(f"   Groups with Issues: {result['groups_with_issues']}")
    print()
    
    if result["ssot_issues"]:
        print(f"⚠️  SSOT Issues ({len(result['ssot_issues'])}):")
        for issue in result["ssot_issues"]:
            print(f"   Group {issue['group']}: {issue['error']}")
        print()
    
    if result["duplicate_issues"]:
        print(f"⚠️  Duplicate Issues ({len(result['duplicate_issues'])}):")
        for issue in result["duplicate_issues"]:
            print(f"   Group {issue['group']}: {issue['issue']}")
        print()
    
    if result["ready"]:
        print("✅ Batch is READY for consolidation")
        print("   All SSOT files verified")
        print("   All duplicates validated")
        print("   Safe to proceed with deletion")
    else:
        print("⚠️  Batch has issues - review before consolidation")
        print(f"   SSOT issues: {len(result['ssot_issues'])}")
        print(f"   Duplicate issues: {len(result['duplicate_issues'])}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

