#!/usr/bin/env python3
"""
Archive Merge Plans
===================

Archives the consolidation buffer merge plans to docs/archive/consolidation/
"""

import json
from pathlib import Path
from datetime import datetime

def main():
    # Read merge plans
    merge_plans_file = Path("dream/consolidation_buffer/merge_plans.json")
    if not merge_plans_file.exists():
        print("❌ merge_plans.json not found")
        return 1
    
    data = json.loads(merge_plans_file.read_text(encoding='utf-8'))
    
    # Extract successful merges
    successful = {k: v for k, v in data.items() if v['status'] == 'merged'}
    
    print(f"📊 Merge Plans Analysis:")
    print(f"   Total plans: {len(data)}")
    print(f"   Successful: {len(successful)}")
    print(f"   Failed: {len(data) - len(successful)}")
    
    # Create archive directory
    archive_dir = Path("docs/archive/consolidation")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Create summary
    summary = {
        "total_plans": len(data),
        "successful": len(successful),
        "failed": len(data) - len(successful),
        "successful_merges": successful,
        "archived_at": datetime.now().isoformat()
    }
    
    # Write summary
    summary_file = archive_dir / "merge_plans_summary.json"
    summary_file.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"✅ Summary saved to: {summary_file}")
    
    # Copy full file
    full_archive = archive_dir / "merge_plans_full_2025-11-30.json"
    full_archive.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"✅ Full archive saved to: {full_archive}")
    
    print(f"\n✅ Archive complete!")
    print(f"   Archive location: {archive_dir}")
    print(f"   Files created: 2 (summary + full archive)")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

