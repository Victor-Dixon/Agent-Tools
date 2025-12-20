#!/usr/bin/env python3
"""
Unified Integration Validator
==============================

Consolidates integration validation tools.
Combines functionality from check_integration_issues.py and integration_health_checker.py.

Features:
- Integration health checks
- Virtual environment file detection
- Duplicate file detection
- Integration connectivity validation

V2 Compliance: ≤300 lines, ≤200 lines/class, ≤30 lines/function
Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-03
Task: Phase 2 Tools Consolidation - Communication Validation
"""

import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VENV_PATTERNS = [
    'lib/python*/site-packages/',
    'venv/',
    'env/',
    '.venv/',
    'node_modules/',
    '__pycache__/',
    '.pytest_cache/',
]

EXCLUDE_PATTERNS = [
    'lib/python*/site-packages/',
    'venv/',
    'env/',
    '.venv/',
    'node_modules/',
    '__pycache__/',
    '.pytest_cache/',
    '.git/',
]


class IntegrationValidator:
    """Unified integration validation."""

    def __init__(self):
        """Initialize validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def get_file_hash(self, filepath: Path) -> Optional[str]:
        """Calculate MD5 hash of file content."""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None

    def find_venv_directories(self, root_dir: Path) -> List[str]:
        """Find virtual environment directories."""
        venv_dirs = []
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                rel_path = os.path.relpath(dir_path, root_dir)
                for pattern in VENV_PATTERNS:
                    if pattern.replace('*', '') in rel_path or 'site-packages' in rel_path:
                        venv_dirs.append(rel_path)
                        break
        return venv_dirs

    def find_duplicate_files(self, root_dir: Path) -> Dict[str, List[str]]:
        """Find duplicate files by content hash."""
        file_hashes = defaultdict(list)
        for root, dirs, files in os.walk(root_dir):
            rel_root = os.path.relpath(root, root_dir)
            skip = False
            for pattern in EXCLUDE_PATTERNS:
                if pattern.replace('*', '') in rel_root or 'site-packages' in rel_root:
                    skip = True
                    break
            if skip:
                continue

            for file_name in files:
                file_path = Path(root) / file_name
                file_hash = self.get_file_hash(file_path)
                if file_hash:
                    rel_path = os.path.relpath(file_path, root_dir)
                    file_hashes[file_hash].append(rel_path)

        duplicates = {h: paths for h, paths in file_hashes.items() if len(paths) > 1}
        return duplicates

    def check_tool_availability(self, tools_dir: Path) -> Dict[str, bool]:
        """Check if integration tools are available."""
        required_tools = [
            "detect_venv_files.py",
            "enhanced_duplicate_detector.py",
            "pattern_analyzer.py",
            "check_integration_issues.py",
        ]
        results = {}
        for tool in required_tools:
            tool_path = tools_dir / tool
            results[tool] = tool_path.exists()
        return results

    def validate_integration_health(self, root_dir: Path) -> Dict[str, Any]:
        """Validate overall integration health."""
        venv_dirs = self.find_venv_directories(root_dir)
        duplicates = self.find_duplicate_files(root_dir)
        tools_dir = root_dir / "tools"
        tool_availability = self.check_tool_availability(tools_dir)

        if venv_dirs:
            self.warnings.append(
                f"Found {len(venv_dirs)} virtual environment directories"
            )

        if duplicates:
            duplicate_count = sum(len(paths) - 1 for paths in duplicates.values())
            self.warnings.append(
                f"Found {len(duplicates)} duplicate file groups ({duplicate_count} duplicates)"
            )

        missing_tools = [tool for tool, available in tool_availability.items() if not available]
        if missing_tools:
            self.warnings.append(f"Missing tools: {', '.join(missing_tools)}")

        return {
            "valid": len(self.errors) == 0,
            "venv_directories": len(venv_dirs),
            "duplicate_groups": len(duplicates),
            "tool_availability": tool_availability,
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "valid": len(self.errors) == 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def print_report(self) -> None:
        """Print validation report using SSOT utility."""
        from src.core.utils.validation_utils import print_validation_report
        print_validation_report(
            errors=self.errors,
            warnings=self.warnings,
        )


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified integration validator"
    )
    parser.add_argument(
        "--root", type=Path, default=Path.cwd(),
        help="Root directory to validate"
    )
    parser.add_argument(
        "--venv", action="store_true", help="Check for venv directories"
    )
    parser.add_argument(
        "--duplicates", action="store_true", help="Check for duplicate files"
    )
    parser.add_argument(
        "--tools", action="store_true", help="Check tool availability"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    args = parser.parse_args()
    validator = IntegrationValidator()

    if args.venv or args.duplicates or args.tools or (not any([args.venv, args.duplicates, args.tools])):
        results = validator.validate_integration_health(args.root)
        if args.json:
            print(json.dumps(results, indent=2))
            return 0 if results["valid"] else 1
        else:
            validator.print_report()
            return 0 if results["valid"] else 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())


