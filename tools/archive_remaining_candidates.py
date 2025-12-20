#!/usr/bin/env python3
"""
Archive Remaining Consolidation Candidates - Phase 2
====================================================

Archives remaining tools that can be replaced by unified tools.
Only processes tools that still exist.

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-02
Priority: HIGH - Tools Consolidation Phase 2
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import re

def check_imports(tool_path: Path, repo_root: Path) -> List[str]:
    """Check if tool is imported anywhere."""
    imports = []
    tool_name = tool_path.stem
    
    # Only check Python files
    for py_file in repo_root.rglob("*.py"):
        if py_file == tool_path:
            continue
        
        # Skip deprecated directory
        if "deprecated" in str(py_file):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for imports
            import_patterns = [
                f"from tools.{tool_name} import",
                f"from tools import {tool_name}",
                f"import {tool_name}",
                f"tools.{tool_name}",
            ]
            
            for pattern in import_patterns:
                if pattern in content:
                    # Basic check: not in string literal or comment
                    lines = content.split('\n')
                    for line in lines:
                        stripped = line.strip()
                        if pattern in line and not stripped.startswith('#') and not (stripped.startswith('"""') or stripped.startswith("'''")):
                            imports.append(str(py_file.relative_to(repo_root)))
                            break
                    if imports and str(py_file.relative_to(repo_root)) in imports:
                        break
        except Exception:
            pass
    
    return imports

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Archive remaining consolidation candidates")
    parser.add_argument("--execute", action="store_true", help="Actually archive files")
    parser.add_argument("--max-files", type=int, default=100, help="Maximum files to process")
    parser.add_argument("--category", choices=["monitoring", "validation", "analysis", "all"], default="all", help="Category to process")
    
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent
    candidates_path = repo_root / "agent_workspaces" / "Agent-8" / "CONSOLIDATION_CANDIDATES_PHASE2.json"
    
    if not candidates_path.exists():
        print(f"❌ Candidates file not found: {candidates_path}")
        return 1
    
    with open(candidates_path, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    
    archive_dir = repo_root / "tools" / "deprecated" / f"consolidated_2025-12-02"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all candidates that can be archived
    all_candidates = []
    categories_to_process = [args.category] if args.category != "all" else ["monitoring", "validation", "analysis", "review_needed"]
    
    for category in categories_to_process:
        for candidate in candidates.get(category, []):
            if candidate.get("can_archive", False):
                tool_path = Path(candidate["path"])
                if tool_path.exists():
                    all_candidates.append(candidate)
    
    print(f"🔍 Found {len(all_candidates)} tools safe to archive (that still exist)\n")
    print(f"📊 Mode: {'DRY RUN' if not args.execute else 'EXECUTE'}\n")
    
    results = {
        "archived": [],
        "skipped": [],
        "errors": [],
        "total": 0
    }
    
    count = 0
    for candidate in all_candidates:
        if count >= args.max_files:
            break
        
        tool_path = Path(candidate["path"])
        if not tool_path.exists():
            results["skipped"].append({
                "tool": candidate["name"],
                "reason": "File not found"
            })
            continue
        
        # Check imports
        imports = check_imports(tool_path, repo_root)
        if imports:
            results["skipped"].append({
                "tool": candidate["name"],
                "reason": f"Imported in {len(imports)} files",
                "imports": imports[:3]
            })
            continue
        
        # Archive tool
        archive_path = archive_dir / tool_path.name
        
        if args.execute:
            try:
                shutil.move(str(tool_path), str(archive_path))
                results["archived"].append(candidate["name"])
                count += 1
                print(f"✅ Archived: {candidate['name']} → {candidate.get('unified_replacement', 'unified tool')}")
            except Exception as e:
                results["errors"].append({
                    "tool": candidate["name"],
                    "error": str(e)
                })
        else:
            results["archived"].append(candidate["name"])
            count += 1
            print(f"🔍 Would archive: {candidate['name']} → {candidate.get('unified_replacement', 'unified tool')}")
    
    results["total"] = count
    
    print("\n" + "=" * 60)
    print("📊 ARCHIVE SUMMARY")
    print("=" * 60)
    print(f"✅ Archived/Safe to archive: {len(results['archived'])}")
    print(f"⏭️  Skipped: {len(results['skipped'])}")
    print(f"❌ Errors: {len(results['errors'])}")
    
    if results["skipped"]:
        print("\n⏭️  Skipped Tools:")
        for item in results["skipped"][:10]:
            print(f"   - {item['tool']}: {item['reason']}")
        if len(results["skipped"]) > 10:
            print(f"   ... and {len(results['skipped']) - 10} more")
    
    if not args.execute:
        print("\n💡 Run with --execute to actually archive files")
        print("💡 Use --max-files to limit batch size")
        print("💡 Use --category to process specific category")
    
    return 0

if __name__ == "__main__":
    exit(main())




