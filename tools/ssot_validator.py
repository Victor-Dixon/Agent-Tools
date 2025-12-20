#!/usr/bin/env python3
"""
SSOT Validator - Documentation-Code Alignment Checker
====================================================

Checks if documented features actually exist in code.
Prevents documentation-reality mismatches like the --get-next-task issue.

Author: Agent-8 (Quality Assurance) - Thread Experience Tool
Created: 2025-10-14
"""

import argparse
import re
import sys
from pathlib import Path


def extract_code_flags(file_path: Path) -> set[str]:
    """Extract CLI flags from Python argparse code."""
    flags = set()
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Find argparse add_argument calls
        flag_pattern = r'add_argument\(["\'](-{1,2}[\w-]+)["\']'
        matches = re.findall(flag_pattern, content)
        flags.update(matches)
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return flags


def extract_documented_flags(file_path: Path) -> set[str]:
    """Extract CLI flags mentioned in documentation."""
    flags = set()
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Find --flag mentions in markdown
        flag_pattern = r'(`|")(-{1,2}[\w-]+)(`|")'
        matches = re.findall(flag_pattern, content)
        flags.update([m[1] for m in matches])
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return flags


def validate_ssot(code_file: str, doc_files: list[str]) -> dict:
    """Validate SSOT between code and documentation."""
    results = {
        "code_flags": set(),
        "doc_flags": set(),
        "undocumented": set(),
        "nonexistent": set(),
        "aligned": set(),
    }
    
    # Extract from code
    code_path = Path(code_file)
    if code_path.exists():
        results["code_flags"] = extract_code_flags(code_path)
    
    # Extract from docs
    for doc_file in doc_files:
        doc_path = Path(doc_file)
        if doc_path.exists():
            results["doc_flags"].update(extract_documented_flags(doc_path))
    
    # Calculate alignment
    results["aligned"] = results["code_flags"] & results["doc_flags"]
    results["undocumented"] = results["code_flags"] - results["doc_flags"]
    results["nonexistent"] = results["doc_flags"] - results["code_flags"]
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SSOT Validator - Check documentation-code alignment"
    )
    parser.add_argument("--code", required=True, help="Python code file to check")
    parser.add_argument("--docs", nargs="+", required=True, help="Documentation files to check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    results = validate_ssot(args.code, args.docs)
    
    # Print report
    print("\n" + "="*80)
    print("🔍 SSOT VALIDATION REPORT")
    print("="*80)
    print(f"Code File: {args.code}")
    print(f"Doc Files: {len(args.docs)} files")
    print("="*80)
    
    print(f"\n✅ ALIGNED FLAGS ({len(results['aligned'])}):")
    for flag in sorted(results['aligned']):
        print(f"  {flag}")
    
    if results['nonexistent']:
        print(f"\n🚨 DOCUMENTED BUT NOT IMPLEMENTED ({len(results['nonexistent'])}):")
        for flag in sorted(results['nonexistent']):
            print(f"  {flag} - SSOT VIOLATION!")
    
    if results['undocumented']:
        print(f"\n⚠️  IMPLEMENTED BUT NOT DOCUMENTED ({len(results['undocumented'])}):")
        for flag in sorted(results['undocumented']):
            print(f"  {flag}")
    
    # Summary
    total_doc = len(results['doc_flags'])
    total_code = len(results['code_flags'])
    alignment_pct = (len(results['aligned']) / max(total_doc, total_code) * 100) if max(total_doc, total_code) > 0 else 0
    
    print("\n" + "="*80)
    print(f"SSOT COMPLIANCE: {alignment_pct:.1f}%")
    print(f"Code Flags: {total_code} | Doc Flags: {total_doc} | Aligned: {len(results['aligned'])}")
    
    if results['nonexistent']:
        print(f"\n🚨 SSOT VIOLATION DETECTED: {len(results['nonexistent'])} documented features don't exist!")
        print("="*80 + "\n")
        return 1
    elif results['undocumented']:
        print(f"\n⚠️  Documentation incomplete: {len(results['undocumented'])} features undocumented")
        print("="*80 + "\n")
        return 0
    else:
        print("\n✅ PERFECT SSOT ALIGNMENT!")
        print("="*80 + "\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())

