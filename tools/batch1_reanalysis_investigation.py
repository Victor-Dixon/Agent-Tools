#!/usr/bin/env python3
"""
Batch 1 Re-Analysis Investigation Tool

Investigates root cause of incorrect duplicate grouping for Batch 1.
SSOT file (tools/activate_wordpress_theme.py) is empty (0 bytes), 
but was grouped with 69 "duplicate" files that are clearly unrelated.

This tool:
1. Analyzes the SSOT file and listed duplicates
2. Checks file sizes and content hashes
3. Identifies why files were incorrectly grouped
4. Documents root cause findings
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import hashlib

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def get_file_hash(file_path: Path) -> str:
    """Get SHA256 hash of file content."""
    if not file_path.exists():
        return "FILE_NOT_FOUND"
    if file_path.stat().st_size == 0:
        return "EMPTY_FILE"
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    except Exception as e:
        return f"ERROR: {e}"


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    if not file_path.exists():
        return -1
    return file_path.stat().st_size


def analyze_batch1_group() -> Dict[str, Any]:
    """Analyze Batch 1 group to identify root cause of incorrect grouping."""
    batches_file = Path("docs/technical_debt/DUPLICATE_GROUPS_PRIORITY_BATCHES.json")
    
    if not batches_file.exists():
        return {"error": "Batches file not found"}
    
    with open(batches_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    batch1 = next((b for b in data['batches'] if b['batch_number'] == 1), None)
    if not batch1:
        return {"error": "Batch 1 not found"}
    
    # Get the first group (the one with empty SSOT)
    group = batch1['groups'][0]
    ssot_path = project_root / Path(group['ssot'].replace('\\', '/'))
    duplicates = [project_root / Path(d.replace('\\', '/')) for d in group['duplicates']]
    
    # Analyze SSOT file
    ssot_size = get_file_size(ssot_path)
    ssot_hash = get_file_hash(ssot_path)
    
    # Analyze duplicate files
    duplicate_analysis = []
    empty_files = []
    same_hash_files = {}
    
    for dup_path in duplicates:
        size = get_file_size(dup_path)
        hash_val = get_file_hash(dup_path)
        
        analysis = {
            "path": str(dup_path.relative_to(project_root)),
            "exists": dup_path.exists(),
            "size": size,
            "hash": hash_val
        }
        duplicate_analysis.append(analysis)
        
        # Track empty files
        if size == 0:
            empty_files.append(str(dup_path.relative_to(project_root)))
        
        # Track files with same hash
        if hash_val not in same_hash_files:
            same_hash_files[hash_val] = []
        same_hash_files[hash_val].append(str(dup_path.relative_to(project_root)))
    
    # Root cause analysis
    root_cause = []
    
    if ssot_size == 0:
        root_cause.append("SSOT file is empty (0 bytes)")
    
    if empty_files:
        root_cause.append(f"Found {len(empty_files)} empty duplicate files - likely matched by empty file hash")
    
    # Check if any duplicates have same hash as SSOT
    if ssot_hash == "EMPTY_FILE":
        matching_empty = [f for f in duplicate_analysis if f['hash'] == "EMPTY_FILE"]
        if matching_empty:
            root_cause.append(f"SSOT empty file matched {len(matching_empty)} other empty files")
    
    # Check for other hash matches
    hash_groups = {h: files for h, files in same_hash_files.items() if len(files) > 1 and h != "EMPTY_FILE"}
    if hash_groups:
        root_cause.append(f"Found {len(hash_groups)} hash groups with multiple files - possible actual duplicates")
    
    return {
        "ssot": {
            "path": str(ssot_path.relative_to(project_root)),
            "exists": ssot_path.exists(),
            "size": ssot_size,
            "hash": ssot_hash
        },
        "duplicates_count": len(duplicates),
        "duplicate_analysis": duplicate_analysis,
        "empty_files": empty_files,
        "hash_groups": hash_groups,
        "root_cause": root_cause,
        "recommendation": "Technical debt analysis likely matched files by content hash. Empty files (0 bytes) all have same hash, causing incorrect grouping. Need to filter out empty files from duplicate detection or use more sophisticated matching (e.g., file name similarity, directory structure)."
    }


def main():
    print("🔍 Batch 1 Re-Analysis Investigation")
    print("   Investigating root cause of incorrect duplicate grouping\n")
    
    analysis = analyze_batch1_group()
    
    if "error" in analysis:
        print(f"❌ Error: {analysis['error']}")
        return 1
    
    print("📊 SSOT File Analysis:")
    print(f"   Path: {analysis['ssot']['path']}")
    print(f"   Exists: {analysis['ssot']['exists']}")
    print(f"   Size: {analysis['ssot']['size']} bytes")
    print(f"   Hash: {analysis['ssot']['hash']}\n")
    
    print(f"📋 Duplicate Files Analysis:")
    print(f"   Total duplicates: {analysis['duplicates_count']}")
    print(f"   Empty files: {len(analysis['empty_files'])}")
    print(f"   Hash groups (potential real duplicates): {len(analysis['hash_groups'])}\n")
    
    if analysis['empty_files']:
        print(f"⚠️  Empty Files Found ({len(analysis['empty_files'])}):")
        for empty_file in analysis['empty_files'][:10]:  # Show first 10
            print(f"   - {empty_file}")
        if len(analysis['empty_files']) > 10:
            print(f"   ... and {len(analysis['empty_files']) - 10} more\n")
    
    if analysis['hash_groups']:
        print(f"🔍 Hash Groups (Potential Real Duplicates):")
        for hash_val, files in list(analysis['hash_groups'].items())[:5]:  # Show first 5
            print(f"   Hash: {hash_val}")
            for file in files[:3]:  # Show first 3 files per group
                print(f"     - {file}")
            if len(files) > 3:
                print(f"     ... and {len(files) - 3} more")
        if len(analysis['hash_groups']) > 5:
            print(f"   ... and {len(analysis['hash_groups']) - 5} more hash groups\n")
    
    print("🎯 Root Cause Analysis:")
    for cause in analysis['root_cause']:
        print(f"   - {cause}")
    print()
    
    print("💡 Recommendation:")
    print(f"   {analysis['recommendation']}\n")
    
    # Save detailed report
    report_path = Path("docs/technical_debt/BATCH1_REANALYSIS_INVESTIGATION_REPORT.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"✅ Investigation complete")
    print(f"   Detailed report: {report_path}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())





