#!/usr/bin/env python3
"""
Fix Real Import Errors - Agent-2
================================

Fixes real import errors identified in BROKEN_IMPORTS.md and test files.
Focuses on actual errors, not false positives from relative imports.

<!-- SSOT Domain: qa -->

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Files that need src. prefix added
TEST_FILES_NEEDING_SRC_PREFIX = [
    "tests/test_chatgpt_integration.py",
    "tests/test_overnight_runner.py",
    "tests/test_toolbelt.py",
    "tests/test_vision.py",
    "tests/test_workflows.py",
]

# Import patterns to fix in test files
TEST_IMPORT_FIXES = [
    (r"^from services\.", "from src.services."),
    (r"^from orchestrators\.", "from src.orchestrators."),
    (r"^from core\.", "from src.core."),
    (r"^from vision\.", "from src.vision."),
    (r"^from workflows\.", "from src.workflows."),
    (r"^import services\.", "import src.services."),
    (r"^import orchestrators\.", "import src.orchestrators."),
    (r"^import core\.", "import src.core."),
]

# Files needing type imports (from BROKEN_IMPORTS.md)
FILES_NEEDING_TYPING = {
    # Performance files
    "src/core/performance/coordination_performance_monitor.py": ["Dict"],
    "src/core/performance/performance_cli.py": ["Dict"],
    "src/core/performance/performance_collector.py": [],  # Already has typing
    "src/core/performance/performance_dashboard.py": [],  # Redirect file
    "src/core/performance/performance_decorators.py": [],  # Already has typing
    "src/core/performance/performance_monitoring_system.py": [],  # Already has typing
    "src/core/performance/unified_dashboard/engine.py": ["Dict"],  # Partially fixed
    "src/core/performance/unified_dashboard/metric_manager.py": [],
    "src/core/performance/unified_dashboard/widget_manager.py": [],
    "src/core/performance/metrics/types.py": ["Dict"],
}

# Files needing logging import
FILES_NEEDING_LOGGING = [
    "src/core/documentation_indexing_service.py",
    "src/core/documentation_search_service.py",
    "src/core/search_history_service.py",
    "src/gaming/handlers/gaming_alert_handlers.py",
    "src/gaming/utils/gaming_alert_utils.py",
    "src/gaming/utils/gaming_handlers.py",
    "src/gaming/utils/gaming_monitors.py",
]

# Files needing dataclass import
FILES_NEEDING_DATACLASS = [
    "src/core/utils/agent_matching.py",
    "src/core/utils/coordination_utils.py",
    "src/core/utils/message_queue_utils.py",
    "src/core/utils/simple_utils.py",
]

# Files needing Enum import
FILES_NEEDING_ENUM = [
    "src/gaming/models/gaming_alert_models.py",
    "src/gaming/models/gaming_models.py",
]

# Files needing Path import
FILES_NEEDING_PATH = [
    "src/tools/duplicate_detection/find_duplicates.py",
    "src/tools/duplicate_detection/file_hash.py",
]

# Files needing Union import
FILES_NEEDING_UNION = [
    "src/gaming/dreamos/resumer_v2/atomic_file_manager.py",
]


def fix_test_imports(file_path: Path, dry_run: bool = True) -> bool:
    """Fix missing src. prefix in test files."""
    if str(file_path) not in TEST_FILES_NEEDING_SRC_PREFIX:
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        modified = False
        
        for i, line in enumerate(lines):
            original = line
            for pattern, replacement in TEST_IMPORT_FIXES:
                if re.match(pattern, line.strip()):
                    lines[i] = re.sub(pattern, replacement, line)
                    if lines[i] != original:
                        modified = True
                        if not dry_run:
                            print(f"  Line {i+1}: {original.strip()} → {lines[i].strip()}")
        
        if modified and not dry_run:
            file_path.write_text('\n'.join(lines), encoding='utf-8')
        
        return modified
    except Exception as e:
        print(f"⚠️  Error fixing {file_path}: {e}")
        return False


def add_typing_import(file_path: Path, needed_types: List[str], dry_run: bool = True) -> bool:
    """Add missing typing imports to a file."""
    if not needed_types:
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Check if typing is already imported
        if 'from typing import' in content or 'import typing' in content:
            # Check if all needed types are already imported
            all_present = all(t in content for t in needed_types)
            if all_present:
                return False
        
        lines = content.split('\n')
        
        # Find insertion point (after other imports, before code)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_idx = i + 1
            elif line.strip() and not line.strip().startswith('#'):
                break
        
        # Build import statement
        existing_typing = []
        for line in lines:
            if 'from typing import' in line:
                # Extract existing imports
                match = re.search(r'from typing import (.+)', line)
                if match:
                    existing_typing = [t.strip() for t in match.group(1).split(',')]
        
        # Combine needed and existing
        all_types = sorted(set(existing_typing + needed_types))
        import_line = f"from typing import {', '.join(all_types)}"
        
        # Remove old typing import if exists
        lines = [l for l in lines if 'from typing import' not in l and 'import typing' not in l]
        
        # Insert new import
        if insert_idx < len(lines):
            lines.insert(insert_idx, import_line)
        else:
            lines.append(import_line)
        
        if not dry_run:
            file_path.write_text('\n'.join(lines), encoding='utf-8')
            print(f"  Added: {import_line}")
        
        return True
    except Exception as e:
        print(f"⚠️  Error adding typing to {file_path}: {e}")
        return False


def add_simple_import(file_path: Path, import_stmt: str, dry_run: bool = True) -> bool:
    """Add a simple import statement (logging, dataclass, etc.)."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Check if already imported
        if import_stmt.split()[1] in content:
            return False
        
        lines = content.split('\n')
        
        # Find insertion point
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_idx = i + 1
            elif line.strip() and not line.strip().startswith('#'):
                break
        
        lines.insert(insert_idx, import_stmt)
        
        if not dry_run:
            file_path.write_text('\n'.join(lines), encoding='utf-8')
            print(f"  Added: {import_stmt}")
        
        return True
    except Exception as e:
        print(f"⚠️  Error adding import to {file_path}: {e}")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix Real Import Errors"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually fix files (default is dry-run)"
    )
    parser.add_argument(
        "--category",
        choices=["all", "tests", "typing", "logging", "dataclass", "enum", "path", "union"],
        default="all",
        help="Category to fix"
    )
    
    args = parser.parse_args()
    
    print("🔧 FIXING REAL IMPORT ERRORS")
    print("=" * 80)
    print(f"Mode: {'DRY RUN' if not args.execute else 'EXECUTING'}")
    print(f"Category: {args.category}\n")
    
    root = Path(__file__).parent.parent
    fixed_count = 0
    
    # Fix test imports
    if args.category in ["all", "tests"]:
        print("📝 Fixing test file imports (src. prefix)...")
        for test_file in TEST_FILES_NEEDING_SRC_PREFIX:
            file_path = root / test_file
            if file_path.exists():
                if fix_test_imports(file_path, dry_run=not args.execute):
                    fixed_count += 1
                    print(f"  ✅ {test_file}")
            else:
                print(f"  ⚠️  {test_file} not found")
        print()
    
    # Fix typing imports
    if args.category in ["all", "typing"]:
        print("📝 Fixing typing imports...")
        for file_path_str, needed_types in FILES_NEEDING_TYPING.items():
            if needed_types:
                file_path = root / file_path_str
                if file_path.exists():
                    if add_typing_import(file_path, needed_types, dry_run=not args.execute):
                        fixed_count += 1
                        print(f"  ✅ {file_path_str}")
                else:
                    print(f"  ⚠️  {file_path_str} not found")
        print()
    
    # Fix logging imports
    if args.category in ["all", "logging"]:
        print("📝 Fixing logging imports...")
        for file_path_str in FILES_NEEDING_LOGGING:
            file_path = root / file_path_str
            if file_path.exists():
                if add_simple_import(file_path, "import logging", dry_run=not args.execute):
                    fixed_count += 1
                    print(f"  ✅ {file_path_str}")
            else:
                print(f"  ⚠️  {file_path_str} not found")
        print()
    
    # Fix dataclass imports
    if args.category in ["all", "dataclass"]:
        print("📝 Fixing dataclass imports...")
        for file_path_str in FILES_NEEDING_DATACLASS:
            file_path = root / file_path_str
            if file_path.exists():
                if add_simple_import(file_path, "from dataclasses import dataclass, field", dry_run=not args.execute):
                    fixed_count += 1
                    print(f"  ✅ {file_path_str}")
            else:
                print(f"  ⚠️  {file_path_str} not found")
        print()
    
    # Fix Enum imports
    if args.category in ["all", "enum"]:
        print("📝 Fixing Enum imports...")
        for file_path_str in FILES_NEEDING_ENUM:
            file_path = root / file_path_str
            if file_path.exists():
                if add_simple_import(file_path, "from enum import Enum", dry_run=not args.execute):
                    fixed_count += 1
                    print(f"  ✅ {file_path_str}")
            else:
                print(f"  ⚠️  {file_path_str} not found")
        print()
    
    # Fix Path imports
    if args.category in ["all", "path"]:
        print("📝 Fixing Path imports...")
        for file_path_str in FILES_NEEDING_PATH:
            file_path = root / file_path_str
            if file_path.exists():
                if add_simple_import(file_path, "from pathlib import Path", dry_run=not args.execute):
                    fixed_count += 1
                    print(f"  ✅ {file_path_str}")
            else:
                print(f"  ⚠️  {file_path_str} not found")
        print()
    
    # Fix Union imports
    if args.category in ["all", "union"]:
        print("📝 Fixing Union imports...")
        for file_path_str in FILES_NEEDING_UNION:
            file_path = root / file_path_str
            if file_path.exists():
                if add_typing_import(file_path, ["Union"], dry_run=not args.execute):
                    fixed_count += 1
                    print(f"  ✅ {file_path_str}")
            else:
                print(f"  ⚠️  {file_path_str} not found")
        print()
    
    print(f"📊 Summary: {fixed_count} files {'would be' if not args.execute else ''} fixed")
    
    if not args.execute:
        print(f"\n💡 Run with --execute to apply fixes")
    else:
        print(f"\n✅ All fixes applied!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

