#!/usr/bin/env python3
"""
Archive Consolidation Candidates - Phase 2
===========================================

Safely archives tools that can be replaced by unified tools.
Checks for imports before archiving.

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
                    # Basic check: not in string literal
                    lines = content.split('\n')
                    for line in lines:
                        if pattern in line and not (line.strip().startswith('#') or ('"' in line[:line.find(pattern)] and '"' in line[line.find(pattern):])):
                            imports.append(str(py_file.relative_to(repo_root)))
                            break
                    if imports and str(py_file.relative_to(repo_root)) in imports:
                        break
        except Exception:
            pass
    
    return imports

def archive_candidates(dry_run: bool = True, max_files: int = 50) -> Dict:
    """Archive consolidation candidates."""
    repo_root = Path(__file__).parent.parent
    candidates_path = repo_root / "agent_workspaces" / "Agent-8" / "CONSOLIDATION_CANDIDATES_PHASE2.json"
    
    if not candidates_path.exists():
        print(f"❌ Candidates file not found: {candidates_path}")
        return {}
    
    with open(candidates_path, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    
    archive_dir = repo_root / "tools" / "deprecated" / f"consolidated_2025-12-02"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "archived": [],
        "skipped": [],
        "errors": [],
        "total": 0
    }
    
    # Process candidates that can be archived
    all_candidates = []
    for category in ["monitoring", "validation", "analysis"]:
        for candidate in candidates.get(category, []):
            if candidate.get("can_archive", False):
                all_candidates.append(candidate)
    
    print(f"🔍 Found {len(all_candidates)} tools safe to archive\n")
    print(f"📊 Mode: {'DRY RUN' if dry_run else 'EXECUTE'}\n")
    
    count = 0
    for candidate in all_candidates:
        if count >= max_files:
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
        
        if not dry_run:
            try:
                shutil.move(str(tool_path), str(archive_path))
                results["archived"].append(candidate["name"])
                count += 1
                print(f"✅ Archived: {candidate['name']} → {candidate['unified_replacement']}")
            except Exception as e:
                results["errors"].append({
                    "tool": candidate["name"],
                    "error": str(e)
                })
        else:
            results["archived"].append(candidate["name"])
            count += 1
            print(f"🔍 Would archive: {candidate['name']} → {candidate['unified_replacement']}")
    
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
    
    return results

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Archive consolidation candidates")
    parser.add_argument("--execute", action="store_true", help="Actually archive files")
    parser.add_argument("--max-files", type=int, default=50, help="Maximum files to process")
    
    args = parser.parse_args()
    
    results = archive_candidates(dry_run=not args.execute, max_files=args.max_files)
    
    if not args.execute:
        print("\n💡 Run with --execute to actually archive files")
        print("💡 Use --max-files to limit batch size")
    
    return 0

if __name__ == "__main__":
    exit(main())




