#!/usr/bin/env python3
"""
Batch 3 SSOT Verification Tool

Verifies SSOT files for all groups within Batch 3.
Checks if SSOT files exist and contain valid content (non-empty).
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def verify_ssot_file(file_path: Path) -> Dict[str, Any]:
    """Verify SSOT file exists and is not empty."""
    if not file_path.exists():
        return {"valid": False, "error": f"SSOT file not found: {file_path}"}
    if file_path.stat().st_size == 0:
        return {"valid": False, "error": f"SSOT file is empty (0 bytes): {file_path}"}
    return {"valid": True, "path": str(file_path)}


def main():
    batches_file = Path("docs/technical_debt/DUPLICATE_GROUPS_PRIORITY_BATCHES.json")
    print("🔍 Batch 3 SSOT Verification")
    print(f"   Batch: 3")

    if not batches_file.exists():
        print(f"❌ Error: Batches file not found at {batches_file}")
        sys.exit(1)

    try:
        with open(batches_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        batch3 = next((b for b in data['batches'] if b['batch_number'] == 3), None)

        if not batch3:
            print("❌ Error: Batch 3 not found in the prioritization file.")
            sys.exit(1)

        groups_to_verify = batch3['groups']
        print(f"   Groups: {len(groups_to_verify)}")
        print(f"   Directory: temp_repos/Thea/\n")

        results = []
        for group in groups_to_verify:
            ssot_path_str = group['ssot']
            # Adjust path for Windows if necessary, and make it absolute from project root
            ssot_path = project_root / Path(ssot_path_str.replace('\\', '/'))
            
            verification_result = verify_ssot_file(ssot_path)
            results.append(verification_result)
            
            if not verification_result['valid']:
                print(f"   ❌ FAILED SSOT: {ssot_path_str} - {verification_result['error']}")
            # else:
            #     print(f"   ✅ PASSED SSOT: {ssot_path_str}")

        passed_count = sum(1 for r in results if r['valid'])
        failed_count = len(results) - passed_count

        print("\n📊 Verification Results:")
        print(f"   Total groups: {len(groups_to_verify)}")
        print(f"   ✅ Passed: {passed_count}")
        print(f"   ❌ Failed: {failed_count}\n")

        if failed_count == 0:
            print("================================================================================")
            print("✅ BATCH 3 SSOT VERIFICATION PASSED")
            print("   All 15 groups have valid SSOT files")
            print("   Batch 3 ready for consolidation assignment\n")
            return 0
        else:
            print("================================================================================")
            print("❌ BATCH 3 SSOT VERIFICATION FAILED")
            print("   Some SSOT files are invalid. Review the errors above.\n")
            return 1

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())





