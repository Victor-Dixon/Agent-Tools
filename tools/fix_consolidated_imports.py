#!/usr/bin/env python3
"""
Fix Consolidated Tool Imports - Agent-8
=======================================

Scans the codebase for imports of archived/consolidated tools and updates them
to use the new unified tools.

<!-- SSOT Domain: qa -->

Author: Agent-8 (Testing & Quality Assurance Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
"""

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Import mapping: old tool → new unified tool
IMPORT_MAP = {
    # Test coverage tools → unified_test_coverage.py
    "test_coverage_tracker": "unified_test_coverage",
    "test_coverage_prioritizer": "unified_test_coverage",
    "analyze_test_coverage_gaps_clean": "unified_test_coverage",
    
    # Test analysis tools → unified_test_analysis.py
    "test_all_discord_commands": "unified_test_analysis",
    
    # Monitoring tools → unified_monitor.py
    "monitor_github_pusher": "unified_monitor",
    "monitor_disk_and_ci": "unified_monitor",
    "monitor_digitaldreamscape_queue": "unified_monitor",
    "agent_progress_tracker": "unified_monitor",
    "automated_test_coverage_tracker": "unified_monitor",
    "infrastructure_automation_monitor": "unified_monitor",
    "infrastructure_health_dashboard": "unified_monitor",
    
    # Analysis tools → unified_analyzer.py
    "analyze_autoblogger_merge": "unified_analyzer",
    "analyze_development_journey": "unified_analyzer",
    "analyze_disk_usage": "unified_analyzer",
    "analyze_dreamvault_duplicates": "unified_analyzer",
    "analyze_duplicate_groups": "unified_analyzer",
    "analyze_init_files": "unified_analyzer",
    "analyze_local_duplicates": "unified_analyzer",
    "analyze_merged_repo_patterns": "unified_analyzer",
    "analyze_repo_duplicates": "unified_analyzer",
    "analyze_stress_test_metrics": "unified_analyzer",
    "analyze_test_coverage_gaps": "unified_analyzer",
    "analyze_unneeded_functionality": "unified_analyzer",
    "comprehensive_project_analyzer_BACKUP_PRE_REFACTOR": "unified_analyzer",
    "comprehensive_repo_analysis": "unified_analyzer",
    
    # Validation tools → unified_validator.py
    "validate_imports": "unified_validator",
    "validate_queue_behavior_under_load": "unified_validator",
    "arch_pattern_validator": "unified_validator",
    "coverage_validator": "unified_validator",
    "integrity_validator": "unified_validator",
    "passdown_validator": "unified_validator",
    "refactor_validator": "unified_validator",
}

# Path patterns to exclude
EXCLUDE_PATTERNS = [
    "__pycache__",
    ".git",
    "venv",
    "env",
    ".venv",
    "node_modules",
    "temp_repos",
    "deprecated",
    "tools/deprecated",
]


def find_python_files(root: Path) -> List[Path]:
    """Find all Python files to scan."""
    files = []
    for py_file in root.rglob("*.py"):
        if not any(pattern in str(py_file) for pattern in EXCLUDE_PATTERNS):
            files.append(py_file)
    return files


def find_imports(content: str) -> List[Tuple[int, str, str]]:
    """
    Find all import statements that need updating.
    Returns: [(line_number, old_import, new_import), ...]
    """
    updates = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Check for 'from tools.OLD import' or 'from tools import OLD'
        for old_tool, new_tool in IMPORT_MAP.items():
            # Pattern: from tools.old_tool import ...
            pattern1 = rf"from\s+tools\.{re.escape(old_tool)}\s+import"
            if re.search(pattern1, stripped):
                new_line = re.sub(
                    rf"from\s+tools\.{re.escape(old_tool)}\s+import",
                    f"from tools.{new_tool} import",
                    stripped
                )
                updates.append((i, stripped, new_line))
            
            # Pattern: from tools import old_tool
            pattern2 = rf"from\s+tools\s+import\s+{re.escape(old_tool)}\b"
            if re.search(pattern2, stripped):
                new_line = re.sub(
                    rf"from\s+tools\s+import\s+{re.escape(old_tool)}\b",
                    f"from tools import {new_tool}",
                    stripped
                )
                updates.append((i, stripped, new_line))
            
            # Pattern: import old_tool (standalone)
            pattern3 = rf"^import\s+{re.escape(old_tool)}\b"
            if re.search(pattern3, stripped):
                new_line = re.sub(
                    rf"^import\s+{re.escape(old_tool)}\b",
                    f"import {new_tool}",
                    stripped
                )
                updates.append((i, stripped, new_line))
    
    return updates


def fix_file(file_path: Path, dry_run: bool = True) -> Dict[str, any]:
    """Fix imports in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        updates = find_imports(content)
        
        if not updates:
            return {"file": str(file_path), "updated": False, "changes": []}
        
        if not dry_run:
            lines = content.split('\n')
            for line_num, old_line, new_line in updates:
                lines[line_num - 1] = new_line
            file_path.write_text('\n'.join(lines), encoding='utf-8')
        
        return {
            "file": str(file_path),
            "updated": not dry_run,
            "changes": [
                {"line": line_num, "old": old_line, "new": new_line}
                for line_num, old_line, new_line in updates
            ]
        }
    except Exception as e:
        return {
            "file": str(file_path),
            "error": str(e),
            "updated": False
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix consolidated tool imports"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Root directory to scan"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually fix files (default is dry-run)"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Fix a specific file"
    )
    
    args = parser.parse_args()
    
    print("🔍 FIXING CONSOLIDATED TOOL IMPORTS")
    print("=" * 80)
    print(f"Mode: {'DRY RUN' if not args.execute else 'EXECUTING'}")
    print(f"Root: {args.root}")
    print()
    
    if args.file:
        files = [args.file] if args.file.exists() else []
    else:
        files = find_python_files(args.root)
    
    print(f"📁 Scanning {len(files)} files...\n")
    
    results = []
    for file_path in files:
        result = fix_file(file_path, dry_run=not args.execute)
        if result.get("changes"):
            results.append(result)
    
    if not results:
        print("✅ No imports need fixing!")
        return 0
    
    print(f"📊 Found {len(results)} files with imports to fix:\n")
    
    total_changes = 0
    for result in results:
        print(f"📝 {result['file']}")
        for change in result['changes']:
            print(f"   Line {change['line']}:")
            print(f"     OLD: {change['old']}")
            print(f"     NEW: {change['new']}")
            total_changes += 1
        print()
    
    print(f"📊 Summary:")
    print(f"   Files: {len(results)}")
    print(f"   Changes: {total_changes}")
    
    if not args.execute:
        print(f"\n💡 Run with --execute to apply changes")
    else:
        print(f"\n✅ All imports fixed!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

