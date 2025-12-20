#!/usr/bin/env python3
"""
Stage 1 Duplicate Resolution - Phase 2: Import Migration Tool
Purpose: Migrate imports from deprecated locations to SSOT locations
Agent: Agent-5
Date: 2025-12-17
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict

# Repository root
REPO_ROOT = Path(__file__).parent.parent
SRC_DIR = REPO_ROOT / "src"

# Import migration mappings
IMPORT_MAPPINGS = {
    # Utilities
    "from src.core.utilities.cleanup_utilities import": "from src.core.shared_utilities.cleanup_manager import",
    "from src.core.utilities.config_utilities import": "from src.core.shared_utilities.configuration_manager_util import",
    "from src.core.utilities.error_utilities import": "from src.core.shared_utilities.error_handler import",
    "from src.core.utilities.init_utilities import": "from src.core.shared_utilities.initialization_manager import",
    "from src.core.utilities.result_utilities import": "from src.core.shared_utilities.result_manager import",
    "from src.core.utilities.status_utilities import": "from src.core.shared_utilities.status_manager import",

    # Config classes
    "from src.core.config_browser import BrowserConfig": "from src.core.config.config_dataclasses import BrowserConfig",
    "from src.infrastructure.browser.browser_models import BrowserConfig": "from src.core.config.config_dataclasses import BrowserConfig",
    "from src.core.config_thresholds import ThresholdConfig": "from src.core.config.config_dataclasses import ThresholdConfig",

    # Model enums
    "from src.services.contract_system.models import TaskStatus": "from src.core.coordination.swarm.coordination_models import TaskStatus",
    "from src.core.managers.execution.execution_operations import Priority": "from src.core.coordination.swarm.coordination_models import Priority",
    "from src.core.intelligent_context.unified_intelligent_context.models import CoordinationStrategy": "from src.core.coordination.swarm.coordination_models import CoordinationStrategy",

    # Interfaces
    "from src.core.messaging_core import IMessageDelivery": "from src.core.messaging_protocol_models import IMessageDelivery",
    "from src.core.onboarding_service import IOnboardingService": "from src.core.messaging_protocol_models import IOnboardingService",
}

# Additional patterns for imports with specific items
IMPORT_PATTERN_MAPPINGS = [
    # Utilities with specific imports
    (r"from src\.core\.utilities\.cleanup_utilities import (.+)",
     r"from src.core.shared_utilities.cleanup_manager import \1"),
    (r"from src\.core\.utilities\.config_utilities import (.+)",
     r"from src.core.shared_utilities.configuration_manager_util import \1"),
    (r"from src\.core\.utilities\.error_utilities import (.+)",
     r"from src.core.shared_utilities.error_handler import \1"),
    (r"from src\.core\.utilities\.init_utilities import (.+)",
     r"from src.core.shared_utilities.initialization_manager import \1"),
    (r"from src\.core\.utilities\.result_utilities import (.+)",
     r"from src.core.shared_utilities.result_manager import \1"),
    (r"from src\.core\.utilities\.status_utilities import (.+)",
     r"from src.core.shared_utilities.status_manager import \1"),

    # Config classes with specific imports
    (r"from src\.core\.config_browser import (.+BrowserConfig.+)",
     r"from src.core.config.config_dataclasses import \1"),
    (r"from src\.infrastructure\.browser\.browser_models import (.+BrowserConfig.+)",
     r"from src.core.config.config_dataclasses import \1"),
    (r"from src\.core\.config_thresholds import (.+ThresholdConfig.+)",
     r"from src.core.config.config_dataclasses import \1"),
]


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in directory, excluding utilities/ itself."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip deprecated utilities directory and __pycache__
        if "utilities" in root.split(os.sep) and "shared_utilities" not in root:
            continue
        if "__pycache__" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)
    return python_files


def find_deprecated_imports(file_path: Path) -> List[Tuple[int, str, str]]:
    """Find deprecated imports in a file and return (line_num, old_line, new_line)."""
    matches = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            # Check exact matches first
            for old_import, new_import in IMPORT_MAPPINGS.items():
                if old_import in line:
                    new_line = line.replace(old_import, new_import)
                    matches.append((line_num, line.strip(), new_line.strip()))
                    break

            # Check pattern matches
            for pattern, replacement in IMPORT_PATTERN_MAPPINGS:
                match = re.search(pattern, line)
                if match:
                    new_line = re.sub(pattern, replacement, line)
                    if new_line != line:
                        matches.append(
                            (line_num, line.strip(), new_line.strip()))
                        break
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return matches


def migrate_imports(file_path: Path, matches: List[Tuple[int, str, str]]) -> bool:
    """Migrate imports in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create a dict for easier lookup
        replacements = {line_num - 1: (old, new)
                        for line_num, old, new in matches}

        # Apply replacements
        modified = False
        for i, line in enumerate(lines):
            if i in replacements:
                old_line, new_line = replacements[i]
                if old_line in line:
                    lines[i] = line.replace(old_line, new_line)
                    modified = True

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        return False
    except Exception as e:
        print(f"Error migrating {file_path}: {e}")
        return False


def main():
    """Main migration function."""
    print("🔍 Stage 1 Phase 2: Import Migration Tool")
    print("=" * 60)

    python_files = find_python_files(SRC_DIR)
    print(f"\n📁 Found {len(python_files)} Python files to check")

    all_matches: Dict[Path, List[Tuple[int, str, str]]] = {}

    # Find all deprecated imports
    print("\n🔍 Scanning for deprecated imports...")
    for file_path in python_files:
        matches = find_deprecated_imports(file_path)
        if matches:
            all_matches[file_path] = matches

    if not all_matches:
        print("\n✅ No deprecated imports found! Migration may already be complete.")
        return

    print(f"\n📊 Found deprecated imports in {len(all_matches)} files:")
    for file_path, matches in all_matches.items():
        rel_path = file_path.relative_to(REPO_ROOT)
        print(f"\n  {rel_path} ({len(matches)} imports):")
        for line_num, old_line, new_line in matches[:3]:  # Show first 3
            print(f"    Line {line_num}: {old_line[:60]}...")
        if len(matches) > 3:
            print(f"    ... and {len(matches) - 3} more")

    # Ask for confirmation (in automated mode, proceed)
    print("\n🔄 Migrating imports...")
    migrated_count = 0
    for file_path, matches in all_matches.items():
        if migrate_imports(file_path, matches):
            migrated_count += 1
            rel_path = file_path.relative_to(REPO_ROOT)
            print(f"  ✅ Migrated {len(matches)} imports in {rel_path}")

    print(f"\n✅ Migration complete!")
    print(f"   - Files scanned: {len(python_files)}")
    print(f"   - Files with deprecated imports: {len(all_matches)}")
    print(f"   - Files migrated: {migrated_count}")

    # Generate report
    report_path = REPO_ROOT / "docs" / "STAGE1_PHASE2_IMPORT_MIGRATION_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Stage 1 Phase 2: Import Migration Report\n")
        f.write(f"**Date**: 2025-12-17\n")
        f.write(f"**Agent**: Agent-5\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- Files scanned: {len(python_files)}\n")
        f.write(f"- Files with deprecated imports: {len(all_matches)}\n")
        f.write(f"- Files migrated: {migrated_count}\n\n")
        f.write(f"## Migration Details\n\n")
        for file_path, matches in all_matches.items():
            rel_path = file_path.relative_to(REPO_ROOT)
            f.write(f"### {rel_path}\n\n")
            f.write(f"**Imports migrated**: {len(matches)}\n\n")
            for line_num, old_line, new_line in matches:
                f.write(f"- Line {line_num}:\n")
                f.write(f"  - Old: `{old_line}`\n")
                f.write(f"  - New: `{new_line}`\n\n")

    print(f"\n📄 Report generated: {report_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

