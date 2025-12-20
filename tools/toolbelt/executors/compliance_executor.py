#!/usr/bin/env python3
"""
Compliance Executor - Agent Toolbelt
====================================

Execute compliance checking operations for agent toolbelt.
Tools from Agent-7's refactor session.

Author: Agent-2 (Extracted from agent_toolbelt_executors.py for V2 compliance)
V2 Compliance: <250 lines, single responsibility
"""

import importlib
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class ComplianceExecutor:
    """Execute compliance checking operations (tools from Agent-7's refactor session)."""

    @staticmethod
    def execute(args):
        """Execute compliance checking operations."""
        if args.comp_action == "count-classes":
            return ComplianceExecutor._count_classes(args)
        elif args.comp_action == "count-functions":
            return ComplianceExecutor._count_functions(args)
        elif args.comp_action == "check-file":
            return ComplianceExecutor._check_file(args)
        elif args.comp_action == "scan-violations":
            return ComplianceExecutor._scan_violations(args)
        elif args.comp_action == "test-imports":
            return ComplianceExecutor._test_imports(args)
        return 1

    @staticmethod
    def _count_classes(args):
        """Count classes in file."""
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {args.file}")
            return 1

        content = file_path.read_text()
        classes = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)

        print(f"\n📊 Class Count: {args.file}")
        print(f"  Total classes: {len(classes)}")
        print("  Limit: ≤5")

        if len(classes) > 5:
            print(f"  Status: ❌ VIOLATION ({len(classes)} > 5)")
            print("\n  Classes found:")
            for i, cls in enumerate(classes, 1):
                print(f"    {i}. {cls}")
            if args.warn:
                return 1
        else:
            print(f"  Status: ✅ COMPLIANT ({len(classes)} ≤ 5)")

        return 0

    @staticmethod
    def _count_functions(args):
        """Count functions in file."""
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {args.file}")
            return 1

        content = file_path.read_text()
        functions = re.findall(r"^(?:async\s+)?def\s+(\w+)", content, re.MULTILINE)

        print(f"\n📊 Function Count: {args.file}")
        print(f"  Total functions: {len(functions)}")
        print("  Limit: ≤10")

        if len(functions) > 10:
            print(f"  Status: ❌ VIOLATION ({len(functions)} > 10)")
            if args.warn:
                return 1
        else:
            print(f"  Status: ✅ COMPLIANT ({len(functions)} ≤ 10)")

        return 0

    @staticmethod
    def _check_file(args):
        """Check file for V2 compliance."""
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {args.file}")
            return 1

        content = file_path.read_text()
        lines = content.count("\n") + 1
        classes = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
        functions = re.findall(r"^(?:async\s+)?def\s+(\w+)", content, re.MULTILINE)

        print(f"\n📊 V2 Compliance Check: {args.file}")
        print(f"\n  Lines: {lines} (limit: ≤400)")
        print(f"  Classes: {len(classes)} (limit: ≤5)")
        print(f"  Functions: {len(functions)} (limit: ≤10)")

        violations = []
        if lines > 400:
            violations.append(f"Lines: {lines} > 400")
        if len(classes) > 5:
            violations.append(f"Classes: {len(classes)} > 5")
        if len(functions) > 10:
            violations.append(f"Functions: {len(functions)} > 10")

        if violations:
            print("\n  Status: ❌ VIOLATIONS")
            for v in violations:
                print(f"    - {v}")

            if args.suggest_fixes:
                print("\n💡 Suggested Fixes:")
                if len(classes) > 5:
                    num_modules = (len(classes) + 4) // 5
                    print(f"  - Split {len(classes)} classes into {num_modules} modules")
                    print(f"    Classes to split: {', '.join(classes)}")
                if lines > 400:
                    print(f"  - Extract modules to reduce from {lines} to ≤400 lines")
                if len(functions) > 10:
                    print(
                        f"  - Group {len(functions)} functions into classes or extract to modules"
                    )

            return 1
        else:
            print("\n  Status: ✅ V2 COMPLIANT")
            return 0

    @staticmethod
    def _scan_violations(args):
        """Scan directory for V2 violations."""
        print(f"🔍 Scanning {args.path} for V2 violations...")

        py_files = list(Path(args.path).rglob("*.py"))
        violations = []

        for file in py_files:
            try:
                content = file.read_text()
                lines = content.count("\n") + 1
                classes = len(re.findall(r"^class\s+", content, re.MULTILINE))
                functions = len(re.findall(r"^(?:async\s+)?def\s+", content, re.MULTILINE))

                file_violations = []
                if lines > 400:
                    file_violations.append(f"lines:{lines}")
                if classes > 5:
                    file_violations.append(f"classes:{classes}")
                if functions > 10:
                    file_violations.append(f"functions:{functions}")

                if file_violations:
                    violations.append(
                        {
                            "file": str(file.relative_to(Path.cwd())),
                            "violations": file_violations,
                            "lines": lines,
                            "classes": classes,
                            "functions": functions,
                        }
                    )
            except Exception:
                continue

        if args.format == "json":
            print(json.dumps(violations, indent=2))
        else:
            if violations:
                print(f"\n📊 V2 Violations Found: {len(violations)}")
                for v in violations[:20]:
                    print(f"\n  {v['file']}")
                    print(
                        f"    Lines: {v['lines']} | Classes: {v['classes']} | Functions: {v['functions']}"
                    )
                    print(f"    Violations: {', '.join(v['violations'])}")

                if len(violations) > 20:
                    print(f"\n  ... and {len(violations) - 20} more violations")
            else:
                print("\n✅ No V2 violations found!")

        return 0

    @staticmethod
    def _test_imports(args):
        """Test imports for a module."""
        print(f"🧪 Testing imports for {args.path}")

        # Convert path to module name
        path_obj = Path(args.path)
        if path_obj.is_file():
            module_path = str(path_obj.with_suffix("")).replace("/", ".").replace("\\", ".")
        else:
            module_path = str(path_obj).replace("/", ".").replace("\\", ".")

        # Ensure it starts with src if needed
        if not module_path.startswith("src") and Path("src") / path_obj.name:
            module_path = f"src.{module_path}" if "." in module_path else module_path

        try:
            print(f"  Importing: {module_path}")
            mod = importlib.import_module(module_path)
            print("  ✅ Import successful")

            # Check exports
            if hasattr(mod, "__all__"):
                print(f"  📦 Exports: {len(mod.__all__)} items")
                if args.verify_backcompat:
                    print(f"  Items: {', '.join(mod.__all__)}")

            return 0
        except Exception as e:
            print(f"  ❌ Import failed: {e}")
            return 1
