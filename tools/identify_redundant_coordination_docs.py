#!/usr/bin/env python3
"""Identify redundant coordination documentation files for deletion."""
from pathlib import Path

# Files to delete (redundant/duplicate)
redundant_files = [
    # Duplicate date-specific vs generic
    "tools/COORDINATION_SESSION_SUMMARY.md",  # Keep _2025-12-12 version
    "tools/COORDINATION_WORK_SUMMARY.md",  # Keep _2025-12-12 version
    "tools/COORDINATION_PROGRESS_REPORT.md",  # Keep _2025-12-12 version
    
    # Redundant summaries (keep most recent)
    "tools/COORDINATION_ACCOMPLISHMENTS_SUMMARY.md",
    "tools/COORDINATION_ACHIEVEMENTS_REPORT.md",
    "tools/COORDINATION_COMPREHENSIVE_REPORT.md",
    "tools/COORDINATION_COMPLETION_REPORT.md",
    "tools/COORDINATION_FINAL_SUMMARY.md",
    "tools/COORDINATION_MASTER_SUMMARY.md",
    "tools/COORDINATION_SESSION_REPORT.md",
    
    # Redundant indexes (keep COORDINATION_INDEX.md)
    "tools/COORDINATION_DOCUMENTATION_INDEX.md",
    
    # Redundant inventories (keep one)
    "tools/COORDINATION_DELIVERABLES_CATALOG.md",  # Keep INVENTORY
    "tools/COORDINATION_DELIVERABLES_INVENTORY.md",  # Actually, keep this one
    
    # Archive/old files
    "tools/COORDINATION_ARCHIVE.md",
    "tools/COORDINATION_REFERENCE_GUIDE.md",
    
    # Redundant status/update files (keep most recent)
    "tools/COORDINATION_STATUS_UPDATE.md",
    "tools/COORDINATION_CHECK_VALIDATION_REPORT.md",
]

files_to_delete = []
for file_path in redundant_files:
    path = Path(file_path)
    if path.exists():
        files_to_delete.append(path)

print(f"Found {len(files_to_delete)} redundant files to delete:\n")
for f in files_to_delete:
    size = f.stat().st_size
    print(f"  {f.name} ({size:,} bytes)")

print(f"\nTotal size to free: {sum(f.stat().st_size for f in files_to_delete):,} bytes")









