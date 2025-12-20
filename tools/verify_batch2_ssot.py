#!/usr/bin/env python3
"""
Batch 2 SSOT Verification
=========================

Verifies SSOT files for Batch 2 duplicate groups (15 groups, temp_repos/Thea/ directory).
After verification passes, Batch 2 consolidation will be assigned to Agent-7.

Author: Agent-8 (SSOT & System Integration Specialist)
V2 Compliant: <300 lines
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def verify_ssot_file(ssot_path: Path) -> Dict[str, Any]:
    """Verify SSOT file exists and contains valid content."""
    result = {
        "ssot_path": str(ssot_path),
        "exists": False,
        "size": 0,
        "valid": False,
        "error": None
    }
    
    if not ssot_path.exists():
        result["error"] = "File does not exist"
        return result
    
    result["exists"] = True
    
    try:
        file_size = ssot_path.stat().st_size
        result["size"] = file_size
        
        if file_size == 0:
            result["error"] = "File is empty (0 bytes)"
            return result
        
        # Check if file has content (read first 100 bytes to verify)
        with open(ssot_path, 'rb') as f:
            content = f.read(100)
            if len(content) == 0:
                result["error"] = "File appears empty"
                return result
        
        result["valid"] = True
        return result
        
    except Exception as e:
        result["error"] = str(e)
        return result


def verify_batch2_ssot() -> Dict[str, Any]:
    """Verify all SSOT files in Batch 2."""
    batches_file = project_root / "docs" / "technical_debt" / "DUPLICATE_GROUPS_PRIORITY_BATCHES.json"
    
    with open(batches_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    batch2 = [b for b in data['batches'] if b['batch_number'] == 2][0]
    groups = batch2['groups']
    
    verification_results = []
    passed = 0
    failed = 0
    
    for group in groups:
        ssot_path_str = group.get('ssot', '').replace('\\', '/')
        ssot_path = project_root / ssot_path_str
        
        verification = verify_ssot_file(ssot_path)
        verification['group'] = {
            'ssot': group.get('ssot'),
            'duplicates_count': len(group.get('duplicates', [])),
            'risk': group.get('risk'),
            'action': group.get('action')
        }
        
        verification_results.append(verification)
        
        if verification['valid']:
            passed += 1
        else:
            failed += 1
    
    return {
        "batch_number": 2,
        "total_groups": len(groups),
        "passed": passed,
        "failed": failed,
        "verification_results": verification_results,
        "all_valid": failed == 0
    }


def main():
    """Main execution."""
    print("🔍 Batch 2 SSOT Verification")
    print("   Batch: 2")
    print("   Groups: 15")
    print("   Directory: temp_repos/Thea/")
    print()
    
    results = verify_batch2_ssot()
    
    print(f"📊 Verification Results:")
    print(f"   Total groups: {results['total_groups']}")
    print(f"   ✅ Passed: {results['passed']}")
    print(f"   ❌ Failed: {results['failed']}")
    print()
    
    if results['failed'] > 0:
        print("❌ FAILED GROUPS:")
        print("=" * 80)
        for v in results['verification_results']:
            if not v['valid']:
                print(f"\nSSOT: {v['ssot_path']}")
                print(f"   Error: {v['error']}")
                print(f"   Exists: {v['exists']}")
                print(f"   Size: {v['size']} bytes")
    
    print()
    print("=" * 80)
    
    if results['all_valid']:
        print("✅ BATCH 2 SSOT VERIFICATION PASSED")
        print("   All 15 groups have valid SSOT files")
        print("   Batch 2 ready for consolidation assignment to Agent-7")
        return 0
    else:
        print("❌ BATCH 2 SSOT VERIFICATION FAILED")
        print(f"   {results['failed']} groups have invalid SSOT files")
        print("   Review failed groups before proceeding with consolidation")
        return 1


if __name__ == "__main__":
    sys.exit(main())





