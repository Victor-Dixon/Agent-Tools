#!/usr/bin/env python3
"""Check Batches 2-8 status for consolidation readiness."""
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
batches_file = project_root / "docs" / "technical_debt" / "DUPLICATE_GROUPS_PRIORITY_BATCHES.json"

with open(batches_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

batches_2_8 = [b for b in data['batches'] if b['batch_number'] >= 2]

print("Batches 2-8 Summary:")
print(f"  Total batches: {len(batches_2_8)}")
print(f"  Total groups: {sum(b['size'] for b in batches_2_8)}")
print(f"  Priority: {batches_2_8[0]['priority'] if batches_2_8 else 'N/A'}")
print(f"\nBatch 2 Preview:")
if batches_2_8:
    batch2 = batches_2_8[0]
    print(f"  Size: {batch2['size']} groups")
    print(f"  First SSOT: {batch2['groups'][0]['ssot']}")
    print(f"  First group duplicates: {len(batch2['groups'][0].get('duplicates', []))}")





