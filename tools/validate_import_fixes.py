#!/usr/bin/env python3
"""
Validate Import Fixes - Agent-8
=================================

Validates import fixes against the master dependency map.
Helps coordinate systematic import error fixing.

<!-- SSOT Domain: qa -->

Author: Agent-8 (Testing & Quality Assurance Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
"""

import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Import categories from master dependency map
IMPORT_CATEGORIES = {
    "type_imports": {
        "pattern": r"(Dict|List|Callable|Any|Optional|Union|Tuple|Set)\b",
        "fix": "from typing import Dict, List, Callable, Any, Optional, Union, Tuple, Set",
        "error_pattern": r"name '(Dict|List|Callable|Any|Optional|Union|Tuple|Set)' is not defined"
    },
    "logging_imports": {
        "pattern": r"\blogging\b",
        "fix": "import logging",
        "error_pattern": r"name 'logging' is not defined"
    },
    "dataclass_imports": {
        "pattern": r"@dataclass|dataclass\(|field\(",
        "fix": "from dataclasses import dataclass, field",
        "error_pattern": r"name '(dataclass|field)' is not defined"
    },
    "enum_imports": {
        "pattern": r"class \w+\(Enum\)|Enum\.",
        "fix": "from enum import Enum",
        "error_pattern": r"name 'Enum' is not defined"
    },
    "path_imports": {
        "pattern": r"Path\(",
        "fix": "from pathlib import Path",
        "error_pattern": r"name 'Path' is not defined"
    }
}

EXCLUDE_PATTERNS = [
    "__pycache__", ".git", "venv", "env", ".venv",
    "node_modules", "temp_repos", "deprecated"
]


def find_python_files(root: Path) -> List[Path]:
    """Find all Python files to scan."""
    files = []
    for py_file in root.rglob("*.py"):
        if not any(pattern in str(py_file) for pattern in EXCLUDE_PATTERNS):
            files.append(py_file)
    return files


def extract_imports(file_path: Path) -> List[str]:
    """Extract all import statements from a file."""
    imports = []
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content, filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = [alias.name for alias in node.names]
                imports.append(f"from {module} import {', '.join(names)}")
    except SyntaxError:
        # File has syntax errors, skip
        pass
    except Exception:
        pass
    
    return imports


def check_missing_imports(file_path: Path) -> Dict[str, List[str]]:
    """Check for missing imports based on usage patterns."""
    try:
        content = file_path.read_text(encoding='utf-8')
        imports = extract_imports(file_path)
        import_text = '\n'.join(imports)
        
        missing = {}
        
        for category, config in IMPORT_CATEGORIES.items():
            # Check if pattern is used in file
            if re.search(config["pattern"], content):
                # Check if fix is already imported
                fix_base = config["fix"].split()[-1]  # Get the main import name
                if fix_base not in import_text and config["fix"] not in import_text:
                    # Check if it's actually used (not just in comments/strings)
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        # Skip comments and strings
                        if line.strip().startswith('#') or '"""' in line or "'''" in line:
                            continue
                        if re.search(config["pattern"], line):
                            if category not in missing:
                                missing[category] = []
                            missing[category].append({
                                "line": i,
                                "pattern": line.strip()[:80],
                                "fix": config["fix"]
                            })
                            break  # Only report once per category
        
        return missing
    
    except Exception as e:
        return {"error": str(e)}


def validate_fix(file_path: Path, category: str, fix: str) -> Tuple[bool, str]:
    """Validate that a fix has been applied correctly."""
    try:
        content = file_path.read_text(encoding='utf-8')
        imports = extract_imports(file_path)
        import_text = '\n'.join(imports)
        
        # Check if fix is present
        fix_keywords = fix.split()[-1] if 'import' in fix else fix
        if fix in import_text or fix_keywords in import_text:
            return True, "Fix applied correctly"
        else:
            return False, f"Fix not found: {fix}"
    
    except Exception as e:
        return False, f"Error validating: {str(e)}"


def scan_category(category: str, files: List[Path]) -> Dict:
    """Scan files for a specific import category."""
    config = IMPORT_CATEGORIES.get(category)
    if not config:
        return {"error": f"Unknown category: {category}"}
    
    results = {
        "category": category,
        "fix": config["fix"],
        "files_needing_fix": [],
        "files_fixed": []
    }
    
    for file_path in files:
        missing = check_missing_imports(file_path)
        if category in missing:
            results["files_needing_fix"].append({
                "file": str(file_path),
                "issues": missing[category]
            })
        else:
            # Check if fix is already applied
            is_valid, message = validate_fix(file_path, category, config["fix"])
            if is_valid:
                results["files_fixed"].append(str(file_path))
    
    return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate Import Fixes - QA Tool"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Root directory to scan"
    )
    parser.add_argument(
        "--category",
        choices=list(IMPORT_CATEGORIES.keys()) + ["all"],
        default="all",
        help="Category to validate"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Validate a specific file"
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Save report to JSON file"
    )
    
    args = parser.parse_args()
    
    print("🔍 VALIDATE IMPORT FIXES")
    print("=" * 80)
    print(f"Root: {args.root}")
    print(f"Category: {args.category}\n")
    
    # Find files
    if args.file:
        files = [args.file] if args.file.exists() else []
    else:
        files = find_python_files(args.root)
    
    print(f"📁 Scanning {len(files)} files...\n")
    
    # Scan categories
    if args.category == "all":
        categories = list(IMPORT_CATEGORIES.keys())
    else:
        categories = [args.category]
    
    all_results = {}
    for category in categories:
        print(f"🔍 Scanning Category: {category}")
        results = scan_category(category, files)
        all_results[category] = results
        
        print(f"   Files needing fix: {len(results.get('files_needing_fix', []))}")
        print(f"   Files already fixed: {len(results.get('files_fixed', []))}")
        
        if results.get('files_needing_fix'):
            print(f"\n   📝 Files needing {category} fix:")
            for file_info in results['files_needing_fix'][:5]:  # Show first 5
                print(f"      - {file_info['file']}")
                for issue in file_info['issues'][:1]:  # Show first issue
                    print(f"        Line {issue['line']}: {issue['pattern']}")
            if len(results['files_needing_fix']) > 5:
                print(f"      ... and {len(results['files_needing_fix']) - 5} more")
        print()
    
    # Summary
    total_needing_fix = sum(
        len(r.get('files_needing_fix', []))
        for r in all_results.values()
    )
    total_fixed = sum(
        len(r.get('files_fixed', []))
        for r in all_results.values()
    )
    
    print(f"📊 Summary:")
    print(f"   Total files needing fixes: {total_needing_fix}")
    print(f"   Total files already fixed: {total_fixed}")
    
    # Save report
    if args.report:
        report = {
            "scan_date": "2025-12-03",
            "total_files_scanned": len(files),
            "categories": all_results,
            "summary": {
                "total_needing_fix": total_needing_fix,
                "total_fixed": total_fixed
            }
        }
        args.report.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(f"\n📄 Report saved to: {args.report}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

