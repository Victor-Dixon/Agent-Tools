#!/usr/bin/env python3
"""
Refactor Executor - Agent Toolbelt
==================================

Execute refactoring operations for agent toolbelt.
Patterns learned from Agent-7's refactoring session.

Author: Agent-2 (Extracted from agent_toolbelt_executors.py for V2 compliance)
V2 Compliance: <150 lines, single responsibility
"""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class RefactorExecutor:
    """Execute refactoring operations (patterns learned from Agent-7's session)."""

    @staticmethod
    def execute(args):
        """Execute refactoring operations."""
        if args.refactor_action == "split":
            return RefactorExecutor._split_file(args)
        elif args.refactor_action == "facade":
            return RefactorExecutor._apply_facade(args)
        elif args.refactor_action == "extract":
            return RefactorExecutor._extract_classes(args)
        return 1

    @staticmethod
    def _split_file(args):
        """Split file into modules."""
        print(f"🔧 Splitting {args.file}")
        print(f"Strategy: {args.strategy}")
        print(f"Max classes per file: {args.max_classes}")

        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {args.file}")
            return 1

        content = file_path.read_text()
        classes = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
        print("\n📊 Analysis:")
        print(f"  Total classes: {len(classes)}")
        print(f"  Classes: {', '.join(classes)}")
        print(f"  Lines: {content.count(chr(10)) + 1}")

        if len(classes) <= args.max_classes:
            print(f"\n✅ File already compliant ({len(classes)} ≤ {args.max_classes} classes)")
            return 0

        print(f"\n⚠️ Violation: {len(classes)} > {args.max_classes} classes")
        num_modules = (len(classes) + args.max_classes - 1) // args.max_classes
        print(f"\n💡 Suggested: Split into {num_modules} modules")

        # Group classes by similarity
        if args.strategy == "auto":
            groups = RefactorExecutor._auto_group_classes(classes)
            print("\n📦 Suggested module structure:")
            for group_name, group_classes in groups.items():
                print(f"  {group_name}.py ({len(group_classes)} classes):")
                for cls in group_classes:
                    print(f"    - {cls}")

        return 0

    @staticmethod
    def _auto_group_classes(classes):
        """Auto-group classes by naming patterns."""
        groups = {}
        for cls in classes:
            if "Manager" in cls:
                group_key = "managers"
            elif "Model" in cls or "Response" in cls or "Context" in cls:
                group_key = "models"
            elif "Handler" in cls or "Processor" in cls:
                group_key = "handlers"
            elif "Exception" in cls or "Error" in cls:
                group_key = "exceptions"
            else:
                group_key = "other"

            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(cls)
        return groups

    @staticmethod
    def _apply_facade(args):
        """Apply facade pattern to directory."""
        print(f"🏗️ Applying facade pattern to {args.directory}")

        dir_path = Path(args.directory)
        if not dir_path.exists():
            print(f"❌ Directory not found: {args.directory}")
            return 1

        modules = [f for f in dir_path.glob("*.py") if f.stem != "__init__"]
        print(f"\n📦 Found {len(modules)} modules")

        print("\n💡 Suggested facade pattern:")
        print("Main file re-exports from modules:")
        for mod in modules:
            print(f"  from .{mod.stem} import ...")

        return 0

    @staticmethod
    def _extract_classes(args):
        """Extract classes to new module."""
        print(f"📤 Extracting from {args.source_file}")
        print(f"Classes to extract: {', '.join(args.class_names)}")
        print(f"Target: {args.target or 'auto-generated'}")

        source = Path(args.source_file)
        if not source.exists():
            print("❌ Source file not found")
            return 1

        content = source.read_text()
        all_classes = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
        missing = set(args.class_names) - set(all_classes)

        if missing:
            print(f"❌ Classes not found: {', '.join(missing)}")
            return 1

        print("✅ All classes found in source")
        print("💡 Ready for extraction")
        return 0
