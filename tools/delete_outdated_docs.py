#!/usr/bin/env python3
"""
Delete Outdated Documentation Files
====================================

Deletes outdated documentation files based on OUTDATED_DOCS_DELETION_LIST.md

Author: Agent-6
Date: 2025-01-27
"""

import os
import re
from pathlib import Path
from typing import List

def extract_files_from_deletion_list(deletion_list_path: str) -> List[str]:
    """Extract file paths from deletion list markdown."""
    files = []
    with open(deletion_list_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Match file paths in backticks: `docs/organization/FILE.md`
        pattern = r'`([^`]+\.md)`'
        matches = re.findall(pattern, content)
        files.extend(matches)
    return files

def delete_files(file_paths: List[str], project_root: Path) -> dict:
    """Delete files and return statistics."""
    deleted = []
    not_found = []
    errors = []
    
    for file_path in file_paths:
        full_path = project_root / file_path
        try:
            if full_path.exists():
                full_path.unlink()
                deleted.append(file_path)
                print(f"✅ Deleted: {file_path}")
            else:
                not_found.append(file_path)
                print(f"⚠️  Not found: {file_path}")
        except Exception as e:
            errors.append((file_path, str(e)))
            print(f"❌ Error deleting {file_path}: {e}")
    
    return {
        'deleted': deleted,
        'not_found': not_found,
        'errors': errors
    }

def main():
    """Main execution."""
    project_root = Path(__file__).resolve().parent.parent
    deletion_list = project_root / 'docs' / 'OUTDATED_DOCS_DELETION_LIST.md'
    
    if not deletion_list.exists():
        print(f"❌ Deletion list not found: {deletion_list}")
        return
    
    print("📋 Extracting files from deletion list...")
    files_to_delete = extract_files_from_deletion_list(str(deletion_list))
    
    print(f"\n📊 Found {len(files_to_delete)} files to delete")
    print("\n🗑️  Starting deletion...\n")
    
    results = delete_files(files_to_delete, project_root)
    
    print(f"\n{'='*60}")
    print("📊 DELETION SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Deleted: {len(results['deleted'])} files")
    print(f"⚠️  Not found: {len(results['not_found'])} files")
    print(f"❌ Errors: {len(results['errors'])} files")
    
    if results['not_found']:
        print(f"\n⚠️  Files not found ({len(results['not_found'])}):")
        for f in results['not_found'][:10]:
            print(f"   - {f}")
        if len(results['not_found']) > 10:
            print(f"   ... and {len(results['not_found']) - 10} more")
    
    if results['errors']:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        for f, e in results['errors']:
            print(f"   - {f}: {e}")

if __name__ == '__main__':
    main()







