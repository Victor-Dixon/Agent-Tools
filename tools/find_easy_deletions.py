#!/usr/bin/env python3
"""
Find easy deletions: redundant docs, orphaned code, unnecessary complexity.
Focus on safe, obvious deletions.
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

REPO_ROOT = Path(__file__).parent.parent

# Patterns for redundant files
REDUNDANT_PATTERNS = [
    # Duplicate validation/summary files
    r'.*_(FINAL|COMPLETE|SUMMARY|DELTA|CERTIFICATE|RECORD|VALIDATION).*\.(md|txt|json)$',
    # Old dated files (older than 7 days for validation/summary files)
    r'.*_\d{4}-\d{2}-\d{2}.*\.(md|txt)$',
    # Temporary/backup files
    r'.*_(OLD|BACKUP|TEMP|TMP|BAK)\.(py|md|txt|json)$',
    # Duplicate agent summaries
    r'AGENT\d+_(SESSION|DAILY|WORK|DELTA|VALIDATION).*\.md$',
]

# Directories to check
CHECK_DIRS = [
    'docs',
    'artifacts',
    'agent_workspaces',
]

# Directories to skip
SKIP_DIRS = {
    'archive/tools/deprecated',  # Already archived
    'node_modules',
    '.git',
    '__pycache__',
    '.pytest_cache',
}

# Files to keep (important ones)
KEEP_FILES = {
    'docs/AGENT_OPERATING_CYCLE_WORKFLOW.md',
    'docs/README.md',
    'docs/DOCUMENTATION_INDEX.md',
}

def is_redundant_file(filepath: Path) -> tuple[bool, str]:
    """Check if file is redundant."""
    rel_path = filepath.relative_to(REPO_ROOT)
    
    # Skip important files
    if str(rel_path) in KEEP_FILES:
        return False, ""
    
    # Skip archived deprecated code
    if 'archive/tools/deprecated' in str(rel_path):
        return False, ""
    
    filename = filepath.name
    
    # Check patterns
    for pattern in REDUNDANT_PATTERNS:
        if re.match(pattern, filename, re.IGNORECASE):
            # Check if it's old (older than 7 days for validation/summary files)
            if '_FINAL' in filename.upper() or '_COMPLETE' in filename.upper() or '_VALIDATION' in filename.upper():
                try:
                    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                    if mtime < datetime.now() - timedelta(days=7):
                        return True, f"Old validation/summary file ({pattern})"
                except:
                    pass
            return True, f"Matches redundant pattern ({pattern})"
    
    # Check for duplicate agent summaries (keep only most recent)
    agent_match = re.match(r'AGENT(\d+)_(SESSION|DAILY|WORK|DELTA|VALIDATION).*\.md$', filename, re.IGNORECASE)
    if agent_match:
        return True, "Duplicate agent summary file"
    
    return False, ""

def find_duplicate_groups(files: list[Path]) -> dict[str, list[Path]]:
    """Group files by base name to find duplicates."""
    groups = defaultdict(list)
    for f in files:
        # Extract base name (without date suffixes)
        base = re.sub(r'_\d{4}-\d{2}-\d{2}.*', '', f.stem)
        base = re.sub(r'_(FINAL|COMPLETE|SUMMARY|DELTA|VALIDATION).*', '', base, flags=re.IGNORECASE)
        groups[base].append(f)
    
    # Return only groups with duplicates
    return {k: v for k, v in groups.items() if len(v) > 1}

def main():
    """Find easy deletions."""
    deletions = []
    duplicates = defaultdict(list)
    
    print("🔍 Scanning for easy deletions...\n")
    
    for check_dir in CHECK_DIRS:
        dir_path = REPO_ROOT / check_dir
        if not dir_path.exists():
            continue
        
        for filepath in dir_path.rglob('*'):
            # Skip directories and files in skip dirs
            if filepath.is_dir():
                continue
            
            rel_path = filepath.relative_to(REPO_ROOT)
            if any(skip in str(rel_path) for skip in SKIP_DIRS):
                continue
            
            # Check if redundant
            is_redundant, reason = is_redundant_file(filepath)
            if is_redundant:
                deletions.append((filepath, reason))
    
    # Find duplicate groups
    all_files = [f for f, _ in deletions]
    dup_groups = find_duplicate_groups(all_files)
    
    # For duplicates, keep most recent, delete others
    for base, files in dup_groups.items():
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        # Keep most recent, mark others for deletion
        for f in files[1:]:
            deletions.append((f, f"Duplicate of {files[0].name}"))
    
    # Sort by path
    deletions.sort(key=lambda x: str(x[0]))
    
    print(f"📋 Found {len(deletions)} easy deletions:\n")
    
    for filepath, reason in deletions[:50]:  # Show first 50
        rel_path = filepath.relative_to(REPO_ROOT)
        print(f"  ❌ {rel_path}")
        print(f"     Reason: {reason}\n")
    
    if len(deletions) > 50:
        print(f"  ... and {len(deletions) - 50} more\n")
    
    # Write deletion list
    deletion_list = REPO_ROOT / 'DELETION_CANDIDATES_EASY.txt'
    with open(deletion_list, 'w') as f:
        f.write(f"Easy Deletions - {len(deletions)} files\n")
        f.write("=" * 80 + "\n\n")
        for filepath, reason in deletions:
            rel_path = filepath.relative_to(REPO_ROOT)
            f.write(f"{rel_path}\n")
            f.write(f"  Reason: {reason}\n\n")
    
    print(f"✅ Deletion list written to: {deletion_list}")
    print(f"\n💡 To delete these files, run:")
    print(f"   python tools/delete_easy_files.py")

if __name__ == '__main__':
    main()








