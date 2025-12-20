#!/usr/bin/env python3
"""
Find More Redundant Files
==========================

Expanded search for redundant docs, orphaned code, and unnecessary complexity.

Author: Agent-7 (Web Development Specialist)
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

REPO_ROOT = Path(__file__).parent.parent

# Expanded patterns for redundant files
REDUNDANT_PATTERNS = [
    # Validation/summary files
    r'.*_(FINAL|COMPLETE|SUMMARY|DELTA|CERTIFICATE|RECORD|VALIDATION).*\.(md|txt|json)$',
    # Dated files (older than 3 days for validation/summary)
    r'.*_\d{4}-\d{2}-\d{2}.*\.(md|txt)$',
    # Temporary/backup files
    r'.*_(OLD|BACKUP|TEMP|TMP|BAK)\.(py|md|txt|json)$',
    # Duplicate agent summaries
    r'AGENT\d+_(SESSION|DAILY|WORK|DELTA|VALIDATION).*\.md$',
    # Progress/status files
    r'.*_(PROGRESS|STATUS|UPDATE|REPORT).*\.md$',
    # Session summaries
    r'.*SESSION.*SUMMARY.*\.md$',
]

# Directories to check
CHECK_DIRS = [
    'docs',
    'agent_workspaces',
]

# Directories to skip
SKIP_DIRS = {
    'archive',
    'node_modules',
    '.git',
    '__pycache__',
    '.pytest_cache',
    'temp_repos',
}

# Files to keep (important ones)
KEEP_FILES = {
    'docs/AGENT_OPERATING_CYCLE_WORKFLOW.md',
    'docs/README.md',
    'docs/DOCUMENTATION_INDEX.md',
    'docs/blog/STANDARDIZED_BLOG_POST_TEMPLATE.md',
    'docs/blog/introducing_the_swarm.md',
}

def is_redundant_file(filepath: Path) -> tuple[bool, str]:
    """Check if file is redundant."""
    rel_path = filepath.relative_to(REPO_ROOT)
    
    # Skip important files
    if str(rel_path) in KEEP_FILES:
        return False, ""
    
    # Skip archived deprecated code
    if 'archive' in str(rel_path) or 'temp_repos' in str(rel_path):
        return False, ""
    
    filename = filepath.name
    
    # Check patterns
    for pattern in REDUNDANT_PATTERNS:
        if re.match(pattern, filename, re.IGNORECASE):
            # Check if it's old (older than 3 days for validation/summary files)
            if any(x in filename.upper() for x in ['_FINAL', '_COMPLETE', '_VALIDATION', '_SUMMARY', '_PROGRESS', '_STATUS']):
                try:
                    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                    if mtime < datetime.now() - timedelta(days=3):
                        return True, f"Old validation/summary file ({pattern})"
                except:
                    pass
            return True, f"Matches redundant pattern ({pattern})"
    
    return False, ""

def main():
    """Find easy deletions."""
    deletions = []
    
    print("🔍 Scanning for more redundant files...\n")
    
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
    
    # Sort by path
    deletions.sort(key=lambda x: str(x[0]))
    
    print(f"📋 Found {len(deletions)} more redundant files:\n")
    
    for filepath, reason in deletions[:50]:  # Show first 50
        rel_path = filepath.relative_to(REPO_ROOT)
        print(f"  ❌ {rel_path}")
        print(f"     Reason: {reason}\n")
    
    if len(deletions) > 50:
        print(f"  ... and {len(deletions) - 50} more\n")
    
    # Write deletion list
    deletion_list = REPO_ROOT / 'DELETION_CANDIDATES_MORE.txt'
    with open(deletion_list, 'w') as f:
        f.write(f"More Redundant Files - {len(deletions)} files\n")
        f.write("=" * 80 + "\n\n")
        for filepath, reason in deletions:
            rel_path = filepath.relative_to(REPO_ROOT)
            f.write(f"{rel_path}\n")
            f.write(f"  Reason: {reason}\n\n")
    
    print(f"✅ Deletion list written to: {deletion_list}")
    print(f"\n💡 To delete these files, run:")
    print(f"   python tools/delete_easy_files.py (update to use DELETION_CANDIDATES_MORE.txt)")

if __name__ == '__main__':
    main()


