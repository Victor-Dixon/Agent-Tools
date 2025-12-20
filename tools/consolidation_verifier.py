#!/usr/bin/env python3
"""
Consolidation Verifier Tool

Verifies that consolidation work is complete by checking for duplicate class/enum definitions.
Uses grep patterns to confirm only SSOT has definitions.

Author: Agent-2 - Architecture & Design Specialist
Created: 2025-12-04
Purpose: Verify consolidation completeness before marking work complete
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class ConsolidationVerifier:
    """Verifies consolidation work is complete."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.src_dir = self.project_root / "src"

    def find_class_definitions(
        self, class_name: str, search_path: Path | None = None
    ) -> List[Tuple[Path, int]]:
        """Find all class definitions for a given class name."""
        search_path = search_path or self.src_dir
        results = []

        try:
            # Use grep to find class definitions
            cmd = [
                "grep",
                "-r",
                "-n",
                f"^class {class_name}",
                str(search_path),
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )

            for line in result.stdout.splitlines():
                if ":" in line:
                    file_path, line_num = line.split(":", 1)
                    file_path = Path(file_path)
                    line_num = int(line_num.split(":")[0])
                    results.append((file_path, line_num))

        except FileNotFoundError:
            # Fallback to Python-based search
            for py_file in search_path.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8")
                    for i, line in enumerate(content.splitlines(), 1):
                        if line.strip().startswith(f"class {class_name}"):
                            results.append((py_file, i))
                except Exception:
                    continue

        return results

    def verify_ssot_consolidation(
        self, class_name: str, ssot_path: Path
    ) -> Tuple[bool, List[Tuple[Path, int]]]:
        """Verify only SSOT has class definition."""
        definitions = self.find_class_definitions(class_name)

        # Filter out SSOT location
        ssot_abs = ssot_path.resolve()
        violations = [
            (path, line)
            for path, line in definitions
            if path.resolve() != ssot_abs
        ]

        is_complete = len(violations) == 0
        return is_complete, violations

    def verify_redirects(
        self, class_name: str, ssot_path: Path
    ) -> Tuple[bool, List[Path]]:
        """Verify files are using redirects/imports from SSOT."""
        ssot_module = self._path_to_module(ssot_path)
        redirect_patterns = [
            f"from {ssot_module} import {class_name}",
            f"from {ssot_module} import",
        ]

        # Find files that reference the class but don't import from SSOT
        violations = []
        for py_file in self.src_dir.rglob("*.py"):
            if py_file.resolve() == ssot_path.resolve():
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                if class_name in content:
                    # Skip if it defines the class (already checked)
                    if f"class {class_name}" in content:
                        continue

                    # Check if it imports from SSOT directly
                    has_direct_import = any(
                        pattern in content for pattern in redirect_patterns
                    )

                    # Check if it imports from a redirect module (e.g., .models)
                    # This is acceptable - the redirect module handles SSOT import
                    has_redirect_import = False
                    for line in content.splitlines():
                        if "import" in line and class_name in line:
                            # If importing from a local module, that's fine (redirect shim)
                            if "from ." in line or "from .." in line:
                                has_redirect_import = True
                                break

                    if not has_direct_import and not has_redirect_import:
                        # Using class but not importing - potential issue
                        violations.append(py_file)
            except Exception:
                continue

        return len(violations) == 0, violations

    def _path_to_module(self, file_path: Path) -> str:
        """Convert file path to Python module path."""
        rel_path = file_path.relative_to(self.project_root)
        parts = rel_path.parts[:-1] + (rel_path.stem,)
        return ".".join(parts)

    def verify(
        self, class_name: str, ssot_path: Path
    ) -> dict:
        """Complete verification of consolidation."""
        ssot_path = self.project_root / ssot_path

        # Check for duplicate definitions
        is_complete, violations = self.verify_ssot_consolidation(
            class_name, ssot_path
        )

        # Check redirects
        redirects_ok, redirect_violations = self.verify_redirects(
            class_name, ssot_path
        )

        return {
            "class_name": class_name,
            "ssot_path": str(ssot_path.relative_to(self.project_root)),
            "consolidation_complete": is_complete,
            "duplicate_definitions": [
                {"file": str(v[0].relative_to(self.project_root)), "line": v[1]}
                for v in violations
            ],
            "redirects_verified": redirects_ok,
            "redirect_violations": [
                str(v.relative_to(self.project_root)) for v in redirect_violations
            ],
            "status": "✅ COMPLETE" if is_complete and redirects_ok else "❌ INCOMPLETE",
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Verify consolidation work is complete"
    )
    parser.add_argument(
        "class_name", help="Name of class/enum to verify (e.g., IntegrationStatus)"
    )
    parser.add_argument(
        "ssot_path",
        type=Path,
        help="Path to SSOT file (e.g., src/architecture/system_integration.py)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    args = parser.parse_args()

    verifier = ConsolidationVerifier()
    result = verifier.verify(args.class_name, args.ssot_path)

    if args.json:
        import json

        print(json.dumps(result, indent=2))
    else:
        print(f"\n🔍 Verification Results for {result['class_name']}")
        print(f"SSOT: {result['ssot_path']}")
        print(f"Status: {result['status']}")
        print(f"\nDuplicate Definitions: {len(result['duplicate_definitions'])}")
        if result["duplicate_definitions"]:
            for dup in result["duplicate_definitions"]:
                print(f"  ❌ {dup['file']}:{dup['line']}")
        else:
            print("  ✅ None found")

        print(f"\nRedirects Verified: {'✅' if result['redirects_verified'] else '❌'}")
        if result["redirect_violations"]:
            for viol in result["redirect_violations"]:
                print(f"  ⚠️  {viol}")

    return 0 if result["consolidation_complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
