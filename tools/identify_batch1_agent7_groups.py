#!/usr/bin/env python3
"""
Identify Batch 1 groups assigned to Agent-7
"""
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
batches_file = project_root / "docs" / "technical_debt" / "DUPLICATE_GROUPS_PRIORITY_BATCHES.json"

with open(batches_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

batch1 = [b for b in data['batches'] if b['batch_number'] == 1][0]

print(f"Batch 1 has {len(batch1['groups'])} groups")
print("\nGroup assignments (based on completion status):")
print("Agent-1: Groups 1-4 (4/4 COMPLETE)")
print("Agent-2: Groups 5-8 (4/4 COMPLETE)")
print("Agent-7: Groups 9-12 (0/4 PENDING)")
print("Agent-8: Groups 13-15 (0/3 PENDING)")

print("\nAgent-7 assigned groups (9-12):")
for i in range(8, 12):  # Groups 9-12 (0-indexed: 8-11)
    group = batch1['groups'][i]
    print(f"\nGroup {i+1}:")
    print(f"  SSOT: {group['ssot']}")
    print(f"  Duplicates: {len(group['duplicates'])} files")
    for dup in group['duplicates']:
        print(f"    - {dup}")


