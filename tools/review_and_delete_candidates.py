#!/usr/bin/env python3
"""
Review and Delete Deletion Candidates
=====================================

Reviews the 64 deletion candidates from comprehensive analysis,
verifies no active dependencies, and deletes safe candidates.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-06
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def load_deletion_candidates() -> List[Dict[str, Any]]:
    """Load deletion candidates from analysis JSON."""
    analysis_file = project_root / "agent_workspaces" / "Agent-5" / "COMPREHENSIVE_TOOLS_ANALYSIS_2025-12-06.json"
    
    if not analysis_file.exists():
        print(f"❌ Analysis file not found: {analysis_file}")
        return []
    
    with open(analysis_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get("deletion_candidates", [])


def check_dependencies(tool_path: Path) -> List[str]:
    """Check if tool has active dependencies."""
    dependencies = []
    
    # Check if tool is imported anywhere
    tool_name = tool_path.stem
    tool_module = f"tools.{tool_path.parent.name}.{tool_name}" if tool_path.parent.name != "tools" else f"tools.{tool_name}"
    
    # Search for imports in Python files
    for py_file in project_root.rglob("*.py"):
        if py_file == tool_path:
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for various import patterns
            import_patterns = [
                f"from {tool_module}",
                f"import {tool_module}",
                f"from tools.{tool_name}",
                f"import {tool_name}",
                f"tools.{tool_name}",
            ]
            
            for pattern in import_patterns:
                if pattern in content:
                    dependencies.append(str(py_file.relative_to(project_root)))
                    break
        except Exception:
            pass
    
    return dependencies


def verify_and_delete(tool_info: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
    """Verify tool is safe to delete and delete if confirmed."""
    tool_path_str = tool_info["tool"]["path"]
    # Normalize path separators (handle Windows backslashes)
    tool_path_str = tool_path_str.replace("\\", "/")
    # Paths are relative to tools/ directory
    tool_path = project_root / "tools" / tool_path_str
    
    if not tool_path.exists():
        return {
            "tool": tool_path_str,
            "status": "not_found",
            "message": "File does not exist"
        }
    
    # Check dependencies
    dependencies = check_dependencies(tool_path)
    
    if dependencies:
        return {
            "tool": tool_path_str,
            "status": "has_dependencies",
            "dependencies": dependencies,
            "message": f"Found {len(dependencies)} active dependencies"
        }
    
    # Check if it's a library module (no main, but might be imported)
    has_main = tool_info["tool"].get("has_main", False)
    is_registered = tool_info["tool"].get("is_registered", False)
    
    if not has_main and not is_registered and not dependencies:
        if not dry_run:
            try:
                tool_path.unlink()
                return {
                    "tool": tool_path_str,
                    "status": "deleted",
                    "message": "Successfully deleted"
                }
            except Exception as e:
                return {
                    "tool": tool_path_str,
                    "status": "error",
                    "message": f"Error deleting: {e}"
                }
        else:
            return {
                "tool": tool_path_str,
                "status": "would_delete",
                "message": "Safe to delete (dry run)"
            }
    
    return {
        "tool": tool_path_str,
        "status": "skip",
        "message": "Skipped (has main or registered)"
    }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Review and delete deletion candidates")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run mode (default)")
    parser.add_argument("--execute", action="store_true", help="Actually delete files")
    parser.add_argument("--output", type=Path, help="Output report file")
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    print("🔍 Loading deletion candidates...")
    candidates = load_deletion_candidates()
    
    if not candidates:
        print("❌ No deletion candidates found")
        return 1
    
    print(f"📊 Found {len(candidates)} deletion candidates")
    print(f"🔧 Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print()
    
    results = {
        "deleted": [],
        "has_dependencies": [],
        "not_found": [],
        "skipped": [],
        "errors": []
    }
    
    for i, candidate in enumerate(candidates, 1):
        tool_name = candidate["tool"]["name"]
        print(f"[{i}/{len(candidates)}] Processing: {tool_name}...", end=" ")
        
        result = verify_and_delete(candidate, dry_run=dry_run)
        
        if result["status"] == "deleted" or result["status"] == "would_delete":
            results["deleted"].append(result)
            print(f"✅ {result['status']}")
        elif result["status"] == "has_dependencies":
            results["has_dependencies"].append(result)
            print(f"⚠️  {result['status']} ({len(result['dependencies'])} deps)")
        elif result["status"] == "not_found":
            results["not_found"].append(result)
            print(f"❌ {result['status']}")
        elif result["status"] == "skipped":
            results["skipped"].append(result)
            print(f"⏭️  {result['status']}")
        else:
            results["errors"].append(result)
            print(f"❌ {result['status']}: {result['message']}")
    
    # Generate report
    print()
    print("=" * 70)
    print("📊 DELETION REPORT")
    print("=" * 70)
    print(f"✅ Deleted/Would Delete: {len(results['deleted'])}")
    print(f"⚠️  Has Dependencies: {len(results['has_dependencies'])}")
    print(f"❌ Not Found: {len(results['not_found'])}")
    print(f"⏭️  Skipped: {len(results['skipped'])}")
    print(f"❌ Errors: {len(results['errors'])}")
    print()
    
    if results["has_dependencies"]:
        print("⚠️  TOOLS WITH DEPENDENCIES (NOT DELETED):")
        for item in results["has_dependencies"]:
            print(f"   - {item['tool']}")
            for dep in item["dependencies"][:3]:  # Show first 3
                print(f"     → {dep}")
            if len(item["dependencies"]) > 3:
                print(f"     ... and {len(item['dependencies']) - 3} more")
        print()
    
    # Save report
    if args.output:
        report_data = {
            "summary": {
                "total_candidates": len(candidates),
                "deleted": len(results["deleted"]),
                "has_dependencies": len(results["has_dependencies"]),
                "not_found": len(results["not_found"]),
                "skipped": len(results["skipped"]),
                "errors": len(results["errors"]),
                "dry_run": dry_run
            },
            "results": results
        }
        
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        print(f"📄 Report saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

