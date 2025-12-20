#!/usr/bin/env python3
"""
Check File Implementation Status
================================

Checks if files are "not yet implemented" vs "truly unused".
Looks for:
- TODO/FIXME comments
- Documentation references
- Implementation plans
- Related files that might need this

<!-- SSOT Domain: infrastructure -->

Author: Agent-4 (Captain)
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

def check_todo_comments(file_path: Path) -> List[str]:
    """Check for TODO/FIXME comments in file."""
    todos = []
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for TODO/FIXME/HACK/NOTE comments
            if re.search(r'\b(TODO|FIXME|HACK|NOTE|XXX|IMPLEMENT|PLANNED)\b', line, re.IGNORECASE):
                todos.append(f"Line {i}: {line.strip()[:80]}")
    except Exception as e:
        pass
    return todos

def check_doc_references(file_path: Path, project_root: Path) -> List[str]:
    """Check if file is mentioned in documentation."""
    references = []
    file_name = file_path.name
    file_stem = file_path.stem
    rel_path = file_path.relative_to(project_root)
    
    # Search in docs directory
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        for doc_file in docs_dir.rglob("*.md"):
            try:
                content = doc_file.read_text(encoding='utf-8', errors='ignore')
                if file_name in content or file_stem in content or str(rel_path) in content:
                    references.append(f"docs/{doc_file.relative_to(project_root)}")
            except:
                pass
    
    return references

def check_related_files(file_path: Path, project_root: Path) -> List[str]:
    """Check for related files that might indicate this is part of a feature."""
    related = []
    file_stem = file_path.stem
    file_dir = file_path.parent
    
    # Check for related files in same directory
    for related_file in file_dir.glob(f"{file_stem}*"):
        if related_file != file_path:
            related.append(str(related_file.relative_to(project_root)))
    
    # Check for test files
    test_file = project_root / "tests" / f"test_{file_stem}.py"
    if test_file.exists():
        related.append(f"tests/test_{file_stem}.py")
    
    return related

def check_implementation_indicators(file_path: Path) -> Dict[str, any]:
    """Check all implementation indicators."""
    project_root = Path(__file__).parent.parent
    
    results = {
        "file": str(file_path.relative_to(project_root)),
        "todos": check_todo_comments(file_path),
        "doc_references": check_doc_references(file_path, project_root),
        "related_files": check_related_files(file_path, project_root),
        "status": "UNKNOWN"
    }
    
    # Determine status
    if results["todos"]:
        results["status"] = "NOT_YET_IMPLEMENTED"
    elif results["doc_references"]:
        results["status"] = "DOCUMENTED_FEATURE"
    elif results["related_files"]:
        results["status"] = "PART_OF_FEATURE"
    else:
        results["status"] = "POSSIBLY_UNUSED"
    
    return results

def analyze_file_list(file_list: List[str], project_root: Optional[Path] = None) -> Dict[str, Dict]:
    """Analyze a list of files for implementation status."""
    if project_root is None:
        project_root = Path(__file__).parent.parent
    
    results = {}
    
    for file_path_str in file_list:
        file_path = project_root / file_path_str
        if file_path.exists():
            results[file_path_str] = check_implementation_indicators(file_path)
        else:
            results[file_path_str] = {
                "file": file_path_str,
                "status": "FILE_NOT_FOUND",
                "todos": [],
                "doc_references": [],
                "related_files": []
            }
    
    return results

def main():
    """CLI interface."""
    import argparse
    parser = argparse.ArgumentParser(description="Check file implementation status")
    parser.add_argument("files", nargs="+", help="Files to check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    results = analyze_file_list(args.files)
    
    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        for file_path, data in results.items():
            print(f"\n{'='*60}")
            print(f"File: {file_path}")
            print(f"Status: {data['status']}")
            
            if data.get("todos"):
                print(f"\nTODO/FIXME Comments ({len(data['todos'])}):")
                for todo in data["todos"][:5]:  # Show first 5
                    print(f"  • {todo}")
            
            if data.get("doc_references"):
                print(f"\nDocumentation References ({len(data['doc_references'])}):")
                for ref in data["doc_references"][:5]:
                    print(f"  • {ref}")
            
            if data.get("related_files"):
                print(f"\nRelated Files ({len(data['related_files'])}):")
                for ref in data["related_files"][:5]:
                    print(f"  • {ref}")

if __name__ == "__main__":
    main()

