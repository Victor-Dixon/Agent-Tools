#!/usr/bin/env python3
"""
Generic Batch SSOT Verification Tool

Verifies SSOT files for any batch within the duplicate groups prioritization.
Checks if SSOT files exist and contain valid content (non-empty).

Usage: python tools/verify_batch_ssot.py <batch_number>
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

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
    if len(sys.argv) < 2:
        print("Usage: python tools/verify_batch_ssot.py <batch_number>")
        sys.exit(1)
    
    try:
        batch_number = int(sys.argv[1])
    except ValueError:
        print(f"❌ Error: Invalid batch number: {sys.argv[1]}")
        sys.exit(1)
    
    batches_file = Path("docs/technical_debt/DUPLICATE_GROUPS_PRIORITY_BATCHES.json")
    print(f"🔍 Batch {batch_number} SSOT Verification")
    print(f"   Batch: {batch_number}")

    if not batches_file.exists():
        print(f"❌ Error: Batches file not found at {batches_file}")
        sys.exit(1)

    try:
        with open(batches_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        batch = next((b for b in data['batches'] if b['batch_number'] == batch_number), None)

        if not batch:
            print(f"❌ Error: Batch {batch_number} not found in the prioritization file.")
            sys.exit(1)

        groups_to_verify = batch['groups']
        print(f"   Groups: {len(groups_to_verify)}")
        print(f"   Priority: {batch.get('priority', 'N/A')}\n")

        results = []
        for group in groups_to_verify:
            ssot_path_str = group['ssot']
            ssot_path = project_root / Path(ssot_path_str.replace('\\', '/'))
            
            verification_result = verify_ssot_file(ssot_path)
            results.append(verification_result)
            
            if not verification_result['valid']:
                print(f"   ❌ FAILED SSOT: {ssot_path_str} - {verification_result['error']}")

        passed_count = sum(1 for r in results if r['valid'])
        failed_count = len(results) - passed_count

        print("\n📊 Verification Results:")
        print(f"   Total groups: {len(groups_to_verify)}")
        print(f"   ✅ Passed: {passed_count}")
        print(f"   ❌ Failed: {failed_count}\n")

        if failed_count == 0:
            print("================================================================================")
            print(f"✅ BATCH {batch_number} SSOT VERIFICATION PASSED")
            print(f"   All {len(groups_to_verify)} groups have valid SSOT files")
            print(f"   Batch {batch_number} ready for consolidation assignment\n")
            return 0
        else:
            print("================================================================================")
            print(f"❌ BATCH {batch_number} SSOT VERIFICATION FAILED")
            print("   Some SSOT files are invalid. Review the errors above.\n")
            return 1

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())





