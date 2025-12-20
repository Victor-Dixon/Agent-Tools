#!/usr/bin/env python3
"""
Generate 22 File List for Agent-8 Review
=========================================

Identifies files needing implementation, runs functionality existence check,
and extracts the 22 duplicate files (3 with functionality_exists, 19 possible duplicates).

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-02
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any

from check_functionality_existence import FunctionalityExistenceChecker


def find_files_needing_implementation(src_root: Path = Path("src")) -> List[Path]:
    """Find files that need implementation by scanning for TODO/FIXME/stubs."""
    files_needing_implementation = []
    
    print("🔍 Scanning for files needing implementation...")
    print("   (Looking for TODO, FIXME, stub functions, incomplete implementations)\n")
    
    for py_file in src_root.rglob("*.py"):
        # Skip cache and test files
        if "__pycache__" in str(py_file) or "test" in str(py_file).lower():
            continue
        
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            
            # Check for implementation markers
            has_todo = bool(re.search(r'TODO[:\s]+', content, re.IGNORECASE))
            has_fixme = bool(re.search(r'FIXME[:\s]+', content, re.IGNORECASE))
            has_stub = bool(re.search(r'def\s+\w+.*:\s*pass\s*$', content, re.MULTILINE))
            
            # Check for incomplete implementations (low implementation ratio)
            functions = len(re.findall(r'def\s+\w+', content))
            implemented = len(re.findall(r'def\s+\w+.*:\s*(?!pass)', content))
            low_implementation = functions > 0 and (implemented / functions) < 0.7
            
            if has_todo or has_fixme or has_stub or low_implementation:
                files_needing_implementation.append(py_file)
                
        except Exception as e:
            continue
    
    print(f"✅ Found {len(files_needing_implementation)} files needing implementation\n")
    return files_needing_implementation


def extract_22_duplicate_files(results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the 22 duplicate files from functionality existence check results."""
    
    functionality_exists = []
    possible_duplicates = []
    
    for file_result in results["files"]:
        if file_result.get("functionality_exists"):
            functionality_exists.append(file_result)
        elif file_result.get("similar_files") and file_result.get("recommendation", "").startswith("POSSIBLE_DUPLICATE"):
            possible_duplicates.append(file_result)
    
    print("\n" + "=" * 60)
    print("📋 22 DUPLICATE FILES EXTRACTED")
    print("=" * 60)
    print(f"\n✅ Functionality Exists (3 files):")
    for i, f in enumerate(functionality_exists[:3], 1):
        print(f"  {i}. {f['relative_path']}")
        if f.get("similar_files"):
            print(f"     Similar to: {f['similar_files'][0]['file']}")
    
    print(f"\n⚠️  Possible Duplicates (19 files):")
    for i, f in enumerate(possible_duplicates[:19], 1):
        print(f"  {i}. {f['relative_path']}")
        if f.get("similar_files"):
            print(f"     Similar to: {f['similar_files'][0]['file']} (score: {f['similar_files'][0].get('similarity_score', 'N/A')})")
    
    return {
        "summary": {
            "total_duplicate_files": len(functionality_exists) + len(possible_duplicates),
            "functionality_exists": len(functionality_exists),
            "possible_duplicates": len(possible_duplicates),
        },
        "functionality_exists_files": functionality_exists[:3],
        "possible_duplicate_files": possible_duplicates[:19],
        "all_22_files": functionality_exists[:3] + possible_duplicates[:19],
    }


def main():
    """Main execution."""
    print("=" * 60)
    print("🔍 GENERATING 22-FILE LIST FOR AGENT-8 REVIEW")
    print("=" * 60)
    print()
    
    # Step 1: Find files needing implementation
    files_needing_implementation = find_files_needing_implementation()
    
    if len(files_needing_implementation) == 0:
        print("❌ No files found needing implementation. Cannot generate list.")
        return
    
    # Step 2: Run functionality existence check
    print("\n" + "=" * 60)
    print("🔍 RUNNING FUNCTIONALITY EXISTENCE CHECK")
    print("=" * 60)
    print()
    
    checker = FunctionalityExistenceChecker()
    results = checker.analyze_files(files_needing_implementation)
    
    # Step 3: Extract 22 duplicate files
    duplicate_files = extract_22_duplicate_files(results)
    
    # Step 4: Save results
    output_file = Path("agent_workspaces/Agent-5/22_duplicate_files_list.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(duplicate_files, f, indent=2)
    
    print(f"\n✅ 22-file list saved to: {output_file}")
    
    # Step 5: Create simple file list for Agent-8
    simple_list_file = Path("agent_workspaces/Agent-8/22_FILES_FOR_REVIEW.md")
    simple_list_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(simple_list_file, "w", encoding="utf-8") as f:
        f.write("# 📋 22 Files for Agent-8 Review\n\n")
        f.write("**Generated**: 2025-12-02  \n")
        f.write("**Purpose**: Review duplicate files for Agent-1's 64 files implementation plan  \n\n")
        f.write("---\n\n")
        
        f.write("## ✅ 3 Files - Functionality Exists\n\n")
        for i, file_info in enumerate(duplicate_files["functionality_exists_files"], 1):
            f.write(f"{i}. **{file_info['relative_path']}**\n")
            if file_info.get("similar_files"):
                similar = file_info["similar_files"][0]
                f.write(f"   - Similar to: `{similar['file']}`\n")
            f.write("\n")
        
        f.write("---\n\n")
        f.write("## ⚠️ 19 Files - Possible Duplicates\n\n")
        for i, file_info in enumerate(duplicate_files["possible_duplicate_files"], 1):
            f.write(f"{i}. **{file_info['relative_path']}**\n")
            if file_info.get("similar_files"):
                similar = file_info["similar_files"][0]
                f.write(f"   - Similar to: `{similar['file']}` (similarity: {similar.get('similarity_score', 'N/A')})\n")
            f.write("\n")
        
        f.write("---\n\n")
        f.write("🐝 **WE. ARE. SWARM. ⚡🔥**\n")
    
    print(f"✅ Simple file list saved to: {simple_list_file}")
    
    print("\n" + "=" * 60)
    print("✅ GENERATION COMPLETE")
    print("=" * 60)
    print("\n📁 Files created:")
    print(f"  1. {output_file}")
    print(f"  2. {simple_list_file}")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()




