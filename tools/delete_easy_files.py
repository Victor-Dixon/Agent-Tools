#!/usr/bin/env python3
"""
Delete easy deletion candidates - safe deletions only.
"""
from pathlib import Path

# Try both deletion lists
DELETION_LIST = Path("DELETION_CANDIDATES_MORE.txt")
if not DELETION_LIST.exists():
    DELETION_LIST = Path("DELETION_CANDIDATES_EASY.txt")

if not DELETION_LIST.exists():
    print("❌ No deletion list found. Run find_easy_deletions.py or find_more_redundant_files.py first.")
    exit(1)

# Read deletion list
files_to_delete = []
with open(DELETION_LIST, 'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('=') and 'Reason:' not in line:
            if Path(line).exists():
                files_to_delete.append(Path(line))

if not files_to_delete:
    print("No files to delete.")
    exit(0)

print(f"🗑️  Deleting {len(files_to_delete)} files...\n")
deleted_count = 0
for f in files_to_delete:
    try:
        f.unlink()
        deleted_count += 1
        print(f"  ✅ Deleted: {f}")
    except Exception as e:
        print(f"  ❌ Failed to delete {f}: {e}")

print(f"\n✅ Deleted {deleted_count}/{len(files_to_delete)} files")
