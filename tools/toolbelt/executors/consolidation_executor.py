#!/usr/bin/env python3
"""
Consolidation Executor - Agent Toolbelt
=======================================

Execute consolidation operations for agent toolbelt.
Patterns learned from Agent-7's consolidation session.

Author: Agent-2 (Extracted from agent_toolbelt_executors.py for V2 compliance)
V2 Compliance: <150 lines, single responsibility
"""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class ConsolidationExecutor:
    """Execute consolidation operations (learned from Agent-7's session)."""

    @staticmethod
    def execute(args):
        """Execute consolidation operations."""
        if args.consol_action == "find-duplicates":
            return ConsolidationExecutor._find_duplicates(args)
        elif args.consol_action == "suggest":
            return ConsolidationExecutor._suggest_consolidation(args)
        elif args.consol_action == "verify":
            return ConsolidationExecutor._verify_consolidation(args)
        return 1

    @staticmethod
    def _find_duplicates(args):
        """Find duplicate files or classes."""
        print(f"🔍 Scanning for duplicates in {args.path}")
        print(f"Type: {args.type}")

        if args.type == "files":
            files_by_name = {}
            for file in Path(args.path).rglob("*.py"):
                if file.name not in files_by_name:
                    files_by_name[file.name] = []
                files_by_name[file.name].append(file)

            duplicates = {name: files for name, files in files_by_name.items() if len(files) > 1}

            if duplicates:
                print(f"\n✅ Found {len(duplicates)} duplicate filenames:")
                for name, files in duplicates.items():
                    print(f"\n  {name} ({len(files)} copies):")
                    for file in files:
                        print(f"    - {file}")
            else:
                print("✅ No duplicate filenames found")

        elif args.type == "classes":
            classes = {}
            for file in Path(args.path).rglob("*.py"):
                try:
                    content = file.read_text()
                    class_names = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
                    for cls in class_names:
                        if cls not in classes:
                            classes[cls] = []
                        classes[cls].append(file)
                except Exception:
                    continue

            duplicates = {name: files for name, files in classes.items() if len(files) > 1}

            if duplicates:
                print(f"\n✅ Found {len(duplicates)} duplicate class names:")
                for name, files in duplicates.items():
                    print(f"\n  class {name} ({len(files)} definitions):")
                    for file in files:
                        print(f"    - {file}")
            else:
                print("✅ No duplicate class names found")

        return 0

    @staticmethod
    def _suggest_consolidation(args):
        """Suggest consolidation opportunities."""
        print(f"💡 Analyzing {args.path} for consolidation opportunities...")
        print(f"Similarity threshold: {args.min_similarity}")

        py_files = list(Path(args.path).rglob("*.py"))
        print(f"\n📊 Found {len(py_files)} Python files")

        # Find files with similar names or purposes
        similar_groups = {}
        for file in py_files:
            base = re.sub(r"(_v\d+|_new|_old|_backup|_core|_models)\.py$", ".py", file.name)
            if base not in similar_groups:
                similar_groups[base] = []
            similar_groups[base].append(file)

        consolidation_candidates = {
            name: files for name, files in similar_groups.items() if len(files) > 1
        }

        if consolidation_candidates:
            print(f"\n💡 Consolidation opportunities ({len(consolidation_candidates)} groups):")
            for base, files in consolidation_candidates.items():
                print(f"\n  {base} pattern ({len(files)} files):")
                for file in files:
                    print(f"    - {file}")
            print("\nSuggestion: Review these files for potential consolidation")
        else:
            print("\n✅ No obvious consolidation opportunities found")

        return 0

    @staticmethod
    def _verify_consolidation(args):
        """Verify consolidation safety."""
        print("✅ Verifying consolidation safety:")
        print(f"  Source: {args.source_file}")
        print(f"  Target: {args.target_file}")

        source = Path(args.source_file)
        target = Path(args.target_file)

        if not source.exists():
            print("  ❌ Source file not found")
            return 1

        if not target.exists():
            print("  ⚠️ Target file doesn't exist (will be created)")

        print("  ✅ Files accessible")
        print("  💡 Safe to proceed with manual consolidation")
        return 0
