#!/usr/bin/env python3
"""
Batch 6 Duplicate Consolidation
================================
Executes duplicate deletion for Batch 6 (8 groups, LOW risk, DELETE action).
All SSOT files verified. Deletes duplicate files, keeps SSOT.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-18
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_batch6_data() -> Dict[str, Any]:
    """Load Batch 6 data from priority batches file."""
    batches_file = PROJECT_ROOT / \
        'docs/technical_debt/DUPLICATE_GROUPS_PRIORITY_BATCHES.json'

    if not batches_file.exists():
        print(f"❌ File not found: {batches_file}")
        sys.exit(1)

    with open(batches_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find Batch 6
    batch6 = None
    for batch in data.get('batches', []):
        if batch.get('batch_number') == 6:
            batch6 = batch
            break

    if not batch6:
        print("❌ Batch 6 not found")
        sys.exit(1)

    return batch6


def verify_ssot_file(ssot_path: Path) -> bool:
    """Verify SSOT file exists and is non-empty."""
    if not ssot_path.exists():
        print(f"  ⚠️  SSOT file does not exist: {ssot_path}")
        return False

    try:
        file_size = ssot_path.stat().st_size
        if file_size == 0:
            print(f"  ⚠️  SSOT file is empty: {ssot_path}")
            return False
    except Exception as e:
        print(f"  ⚠️  Error checking SSOT file: {ssot_path} - {e}")
        return False

    return True


def verify_duplicate_file(dup_path: Path) -> bool:
    """Verify duplicate file exists before deletion."""
    if not dup_path.exists():
        print(
            f"  ⚠️  Duplicate file does not exist (already deleted?): {dup_path}")
        return False
    return True


def delete_duplicate_file(dup_path: Path) -> bool:
    """Safely delete a duplicate file."""
    try:
        dup_path.unlink()
        print(f"  ✅ Deleted: {dup_path}")
        return True
    except Exception as e:
        print(f"  ❌ Error deleting {dup_path}: {e}")
        return False


def consolidate_batch6() -> Dict[str, Any]:
    """Execute Batch 6 duplicate consolidation."""
    print("🔍 Batch 6 Duplicate Consolidation")
    print("=" * 60)
    print()

    batch6 = load_batch6_data()
    groups = batch6.get('groups', [])

    print(f"📊 Batch 6 Overview:")
    print(f"   Groups: {len(groups)}")
    print(f"   Priority: {batch6.get('priority', 'UNKNOWN')}")
    print(f"   Risk: LOW (all groups)")
    print()

    # Execution results
    results = {
        'total_groups': len(groups),
        'groups_processed': 0,
        'groups_successful': 0,
        'groups_failed': 0,
        'files_deleted': 0,
        'files_failed': 0,
        'deletions': []
    }

    # Process each group
    for i, group in enumerate(groups, 1):
        ssot_str = group.get('ssot', '')
        duplicates = group.get('duplicates', [])
        risk = group.get('risk', 'UNKNOWN')
        action = group.get('action', 'UNKNOWN')

        print(f"📁 Group {i}/{len(groups)}: {Path(ssot_str).name}")
        print(f"   SSOT: {ssot_str}")
        print(f"   Duplicates: {len(duplicates)}")
        print(f"   Risk: {risk}, Action: {action}")

        # Convert paths to Path objects
        ssot_path = PROJECT_ROOT / ssot_str.replace('\\', '/')

        # Verify SSOT file
        if not verify_ssot_file(ssot_path):
            print(f"  ❌ Skipping group - SSOT file invalid")
            results['groups_failed'] += 1
            results['groups_processed'] += 1
            print()
            continue

        # Process duplicates
        group_success = True
        for dup_str in duplicates:
            dup_path = PROJECT_ROOT / dup_str.replace('\\', '/')

            # Verify duplicate exists
            if not verify_duplicate_file(dup_path):
                continue  # Already deleted or doesn't exist, skip

            # Delete duplicate
            if delete_duplicate_file(dup_path):
                results['files_deleted'] += 1
                results['deletions'].append({
                    'ssot': ssot_str,
                    'deleted': str(dup_path),
                    'status': 'success'
                })
            else:
                results['files_failed'] += 1
                group_success = False
                results['deletions'].append({
                    'ssot': ssot_str,
                    'deleted': str(dup_path),
                    'status': 'failed'
                })

        if group_success:
            results['groups_successful'] += 1
        else:
            results['groups_failed'] += 1

        results['groups_processed'] += 1
        print()

    return results


def main():
    """Main entry point."""
    print("🚀 Starting Batch 6 Consolidation...")
    print()

    results = consolidate_batch6()

    # Summary
    print("=" * 60)
    print("📊 CONSOLIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Groups: {results['total_groups']}")
    print(f"Groups Processed: {results['groups_processed']}")
    print(f"Groups Successful: {results['groups_successful']}")
    print(f"Groups Failed: {results['groups_failed']}")
    print(f"Files Deleted: {results['files_deleted']}")
    print(f"Files Failed: {results['files_failed']}")
    print()

    if results['files_failed'] > 0:
        print("⚠️  Some deletions failed. Review errors above.")
        sys.exit(1)
    else:
        print("✅ All deletions completed successfully!")

    # Save results
    results_file = PROJECT_ROOT / 'docs/technical_debt/BATCH6_CONSOLIDATION_RESULTS.json'
    results_file.parent.mkdir(parents=True, exist_ok=True)

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"📄 Results saved to: {results_file}")


if __name__ == '__main__':
    main()

