#!/usr/bin/env python3
"""
Duplicate File Detector

Detects duplicate files in repository.
Following Agent-2's findings: 6,397 duplicate files found in DreamVault.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-11-26
"""

import os
import sys
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple


def calculate_file_hash(file_path: str) -> str:
    """Calculate MD5 hash of file."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (IOError, OSError):
        return None


def detect_duplicate_files(root_path: str) -> Dict[str, List[str]]:
    """
    Detect duplicate files by content hash.
    
    Args:
        root_path: Root directory to scan
        
    Returns:
        Dictionary mapping hash to list of file paths
    """
    root = Path(root_path)
    hash_to_files = defaultdict(list)
    
    for root_dir, dirs, files in os.walk(root):
        # Skip .git and venv directories
        if '.git' in root_dir or 'venv' in root_dir or '.venv' in root_dir:
            continue
        
        for file in files:
            file_path = os.path.join(root_dir, file)
            rel_path = os.path.relpath(file_path, root)
            
            file_hash = calculate_file_hash(file_path)
            if file_hash:
                hash_to_files[file_hash].append(rel_path)
    
    # Filter to only duplicates (more than one file with same hash)
    duplicates = {h: paths for h, paths in hash_to_files.items() 
                  if len(paths) > 1}
    
    return duplicates


def detect_duplicate_names(root_path: str) -> Dict[str, List[str]]:
    """
    Detect files with duplicate names (different locations).
    
    Args:
        root_path: Root directory to scan
        
    Returns:
        Dictionary mapping filename to list of paths
    """
    root = Path(root_path)
    name_to_paths = defaultdict(list)
    
    for root_dir, dirs, files in os.walk(root):
        # Skip .git and venv directories
        if '.git' in root_dir or 'venv' in root_dir or '.venv' in root_dir:
            continue
        
        for file in files:
            file_path = os.path.join(root_dir, file)
            rel_path = os.path.relpath(file_path, root)
            name_to_paths[file].append(rel_path)
    
    # Filter to only duplicates
    duplicates = {name: paths for name, paths in name_to_paths.items() 
                  if len(paths) > 1}
    
    return duplicates


def print_report(content_dups: Dict[str, List[str]], 
                 name_dups: Dict[str, List[str]]):
    """Print detection report."""
    total_content = sum(len(paths) - 1 for paths in content_dups.values())
    total_name = sum(len(paths) - 1 for paths in name_dups.values())
    
    print("=" * 60)
    print("DUPLICATE FILE DETECTION REPORT")
    print("=" * 60)
    print(f"\nContent duplicates (same hash): {len(content_dups)} groups")
    print(f"  Total duplicate files: {total_content}")
    print(f"\nName duplicates (same filename): {len(name_dups)} groups")
    print(f"  Total duplicate names: {total_name}")
    
    if content_dups:
        print("\n" + "=" * 60)
        print("CONTENT DUPLICATES (First 10 groups):")
        print("=" * 60)
        for i, (hash_val, paths) in enumerate(list(content_dups.items())[:10]):
            print(f"\nGroup {i+1} ({len(paths)} files):")
            for path in paths:
                print(f"  - {path}")
    
    if name_dups:
        print("\n" + "=" * 60)
        print("NAME DUPLICATES (First 10 groups):")
        print("=" * 60)
        for i, (name, paths) in enumerate(list(name_dups.items())[:10]):
            print(f"\nGroup {i+1} - '{name}' ({len(paths)} locations):")
            for path in paths:
                print(f"  - {path}")
    
    if total_content > 0 or total_name > 0:
        print("\n⚠️  WARNING: Duplicate files detected!")
        print("   Action: Review and resolve duplicates properly.")
    else:
        print("\n✅ No duplicate files detected.")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = os.getcwd()
    
    print(f"Scanning: {root_path}")
    print("Detecting duplicate files...")
    
    content_dups = detect_duplicate_files(root_path)
    name_dups = detect_duplicate_names(root_path)
    
    print_report(content_dups, name_dups)
    
    total_issues = len(content_dups) + len(name_dups)
    return 0 if total_issues == 0 else 1


if __name__ == '__main__':
    sys.exit(main())



