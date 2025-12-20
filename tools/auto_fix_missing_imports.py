#!/usr/bin/env python3
"""
Auto-Fix Missing Imports - Agent-8
===================================

Automatically fixes missing standard library imports based on usage patterns.
Focuses on easy wins: typing, logging, dataclass, enum, pathlib.

<!-- SSOT Domain: qa -->

Author: Agent-8 (Testing & Quality Assurance Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
"""

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Import fixes to apply
IMPORT_FIXES = {
    "typing": {
        "pattern": r"\b(Dict|List|Callable|Any|Optional|Union|Tuple|Set)\b",
        "import": "from typing import Dict, List, Callable, Any, Optional, Union, Tuple, Set",
        "check_usage": True
    },
    "logging": {
        "pattern": r"\blogging\.(info|debug|warning|error|critical|getLogger)\b",
        "import": "import logging",
        "check_usage": True
    },
    "dataclass": {
        "pattern": r"@dataclass|dataclass\(|field\(",
        "import": "from dataclasses import dataclass, field",
        "check_usage": True
    },
    "enum": {
        "pattern": r"class \w+\(Enum\)|Enum\.",
        "import": "from enum import Enum",
        "check_usage": True
    },
    "pathlib": {
        "pattern": r"Path\(",
        "import": "from pathlib import Path",
        "check_usage": True
    }
}

EXCLUDE_PATTERNS = [
    "__pycache__", ".git", "venv", "env", ".venv",
    "node_modules", "temp_repos", "deprecated", "tests"
]


def find_python_files(root: Path) -> List[Path]:
    """Find all Python files to scan."""
    files = []
    for py_file in root.rglob("*.py"):
        if not any(pattern in str(py_file) for pattern in EXCLUDE_PATTERNS):
            files.append(py_file)
    return files


def extract_existing_imports(content: str) -> Set[str]:
    """Extract existing import statements."""
    imports = set()
    lines = content.split('\n')
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            imports.add(stripped)
    
    return imports


def check_if_import_needed(content: str, fix_config: Dict) -> bool:
    """Check if import is needed based on usage pattern."""
    if not fix_config.get("check_usage", False):
        return True
    
    pattern = fix_config["pattern"]
    # Check if pattern is used (not in comments or strings)
    lines = content.split('\n')
    for line in lines:
        # Skip comments
        if line.strip().startswith('#'):
            continue
        # Skip docstrings
        if '"""' in line or "'''" in line:
            continue
        # Check for pattern
        if re.search(pattern, line):
            return True
    
    return False


def check_if_already_imported(existing_imports: Set[str], import_statement: str) -> bool:
    """Check if import already exists."""
    import_keywords = import_statement.split()[-1] if 'import' in import_statement else import_statement
    
    for existing in existing_imports:
        if import_statement in existing or import_keywords in existing:
            return True
        # Check for partial matches (e.g., "from typing import Dict" matches "from typing import Dict, List")
        if 'from typing import' in import_statement and 'from typing import' in existing:
            return True
        if 'import logging' in import_statement and 'import logging' in existing:
            return True
    
    return False


def fix_file_imports(file_path: Path, dry_run: bool = True) -> Dict:
    """Fix missing imports in a file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        existing_imports = extract_existing_imports(content)
        
        fixes_needed = []
        
        for fix_name, fix_config in IMPORT_FIXES.items():
            import_statement = fix_config["import"]
            
            # Check if already imported
            if check_if_already_imported(existing_imports, import_statement):
                continue
            
            # Check if import is needed
            if not check_if_import_needed(content, fix_config):
                continue
            
            fixes_needed.append({
                "fix": fix_name,
                "import": import_statement
            })
        
        if not fixes_needed:
            return {"file": str(file_path), "fixed": False, "changes": []}
        
        if not dry_run:
            # Find insertion point (after existing imports, before code)
            lines = content.split('\n')
            insert_idx = 0
            
            # Find last import statement
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    insert_idx = i + 1
                elif stripped and not stripped.startswith('#') and insert_idx > 0:
                    # Found non-import, non-comment line - stop
                    break
            
            # Insert new imports
            new_imports = [fix["import"] for fix in fixes_needed]
            lines[insert_idx:insert_idx] = new_imports + [""]  # Add blank line after imports
            
            file_path.write_text('\n'.join(lines), encoding='utf-8')
        
        return {
            "file": str(file_path),
            "fixed": not dry_run,
            "changes": fixes_needed
        }
    
    except Exception as e:
        return {
            "file": str(file_path),
            "error": str(e),
            "fixed": False
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Auto-Fix Missing Imports"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).parent.parent / "src",
        help="Root directory to scan"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually fix files (default is dry-run)"
    )
    parser.add_argument(
        "--category",
        choices=list(IMPORT_FIXES.keys()) + ["all"],
        default="all",
        help="Category to fix"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of files to process"
    )
    
    args = parser.parse_args()
    
    print("🔧 AUTO-FIX MISSING IMPORTS")
    print("=" * 80)
    print(f"Mode: {'DRY RUN' if not args.execute else 'EXECUTING'}")
    print(f"Root: {args.root}")
    print(f"Category: {args.category}\n")
    
    # Find files
    files = find_python_files(args.root)
    if args.limit:
        files = files[:args.limit]
    
    print(f"📁 Processing {len(files)} files...\n")
    
    # Process files
    results = []
    for file_path in files:
        result = fix_file_imports(file_path, dry_run=not args.execute)
        if result.get("changes"):
            results.append(result)
    
    if not results:
        print("✅ No imports need fixing!")
        return 0
    
    print(f"📊 Found {len(results)} files needing fixes:\n")
    
    total_fixes = 0
    for result in results[:20]:  # Show first 20
        print(f"📝 {result['file']}")
        for change in result['changes']:
            print(f"   + {change['import']}")
            total_fixes += 1
        print()
    
    if len(results) > 20:
        print(f"   ... and {len(results) - 20} more files\n")
    
    print(f"📊 Summary:")
    print(f"   Files: {len(results)}")
    print(f"   Fixes: {total_fixes}")
    
    if not args.execute:
        print(f"\n💡 Run with --execute to apply {total_fixes} fixes")
    else:
        print(f"\n✅ Fixed {total_fixes} missing imports!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

