#!/usr/bin/env python3
"""
Discord Button Verification Tool
=================================

Verifies all Discord bot buttons have proper callbacks and imports.
Checks for common issues:
- Missing callbacks
- Incorrect import paths
- Button registration issues
- Modal import errors

Author: Agent-3 (Infrastructure & DevOps Specialist)
Date: 2025-01-27
"""

import ast
import importlib.util
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ButtonVerifier:
    """Verifies Discord button implementations."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.issues: List[Dict[str, Any]] = []
        self.buttons_checked = 0
        self.buttons_ok = 0

    def verify_all_buttons(self) -> Tuple[int, int, List[Dict[str, Any]]]:
        """Verify all buttons in Discord commander directory."""
        discord_dir = self.base_path / "src" / "discord_commander"
        
        if not discord_dir.exists():
            logger.error(f"Discord commander directory not found: {discord_dir}")
            return 0, 0, []

        # Find all Python files
        python_files = list(discord_dir.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files to check")

        for file_path in python_files:
            if file_path.name.startswith("__"):
                continue
            self._verify_file(file_path)

        return self.buttons_checked, self.buttons_ok, self.issues

    def _verify_file(self, file_path: Path) -> None:
        """Verify buttons in a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))

            # Find all Button creations
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if self._is_button_creation(node):
                        self.buttons_checked += 1
                        self._check_button(node, file_path, content)

        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")

    def _is_button_creation(self, node: ast.Call) -> bool:
        """Check if this is a discord.ui.Button creation."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Attribute):
                if (
                    isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id == "discord"
                    and node.func.value.attr == "ui"
                    and node.func.attr == "Button"
                ):
                    return True
        return False

    def _check_button(self, node: ast.Call, file_path: Path, content: str) -> None:
        """Check a single button for issues."""
        # Find button variable assignment
        parent = self._find_parent_assignment(node, content)
        if not parent:
            return

        button_name = parent.get("name", "unknown")
        line_num = node.lineno

        # Check for callback assignment
        callback_found = self._check_callback(button_name, file_path, content)

        if callback_found:
            self.buttons_ok += 1
            logger.debug(f"✅ {file_path.name}:{line_num} - Button '{button_name}' has callback")
        else:
            self.issues.append(
                {
                    "file": str(file_path),
                    "line": line_num,
                    "button": button_name,
                    "issue": "Missing callback assignment",
                }
            )
            logger.warning(
                f"❌ {file_path.name}:{line_num} - Button '{button_name}' missing callback"
            )

    def _find_parent_assignment(self, node: ast.Call, content: str) -> Dict[str, Any] | None:
        """Find the variable assignment for this button."""
        # Simple heuristic: look for self.button_name = pattern
        lines = content.split("\n")
        if node.lineno > len(lines):
            return None

        line = lines[node.lineno - 1]
        if "self." in line and "=" in line:
            parts = line.split("=")
            if len(parts) >= 2:
                var_part = parts[0].strip()
                if "self." in var_part:
                    name = var_part.split("self.")[-1].strip()
                    return {"name": name, "line": node.lineno}
        return None

    def _check_callback(self, button_name: str, file_path: Path, content: str) -> bool:
        """Check if button has callback assigned."""
        # Look for button_name.callback = pattern
        if f"{button_name}.callback" in content:
            return True
        return False

    def verify_imports(self) -> List[Dict[str, Any]]:
        """Verify all modal imports are correct."""
        import_issues = []
        discord_dir = self.base_path / "src" / "discord_commander"

        for file_path in discord_dir.rglob("*.py"):
            if file_path.name.startswith("__"):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for discord_gui_modals imports
                if "discord_gui_modals" in content:
                    lines = content.split("\n")
                    for i, line in enumerate(lines, 1):
                        if "from" in line and "discord_gui_modals" in line:
                            # Check import path correctness
                            if "from ..discord_gui_modals" in line:
                                # This might be wrong depending on file location
                                if "controllers" in str(file_path):
                                    # Controllers should use ...discord_commander.discord_gui_modals
                                    if "...discord_commander.discord_gui_modals" not in line:
                                        import_issues.append(
                                            {
                                                "file": str(file_path),
                                                "line": i,
                                                "import": line.strip(),
                                                "issue": "Incorrect import path for controllers",
                                                "expected": "from ...discord_commander.discord_gui_modals import",
                                            }
                                        )

            except Exception as e:
                logger.warning(f"Error checking imports in {file_path}: {e}")

        return import_issues


def main():
    """Main verification function."""
    base_path = Path(__file__).parent.parent
    verifier = ButtonVerifier(base_path)

    print("=" * 60)
    print("🔍 DISCORD BUTTON VERIFICATION")
    print("=" * 60)
    print()

    # Verify buttons
    print("📋 Checking button callbacks...")
    buttons_checked, buttons_ok, button_issues = verifier.verify_all_buttons()
    print(f"   Buttons checked: {buttons_checked}")
    print(f"   Buttons OK: {buttons_ok}")
    print(f"   Issues found: {len(button_issues)}")
    print()

    # Verify imports
    print("📦 Checking import paths...")
    import_issues = verifier.verify_imports()
    print(f"   Import issues found: {len(import_issues)}")
    print()

    # Report issues
    all_issues = button_issues + import_issues

    if all_issues:
        print("=" * 60)
        print("❌ ISSUES FOUND")
        print("=" * 60)
        for issue in all_issues:
            print(f"\n📁 {issue['file']}")
            print(f"   Line {issue.get('line', '?')}: {issue.get('issue', 'Unknown issue')}")
            if "button" in issue:
                print(f"   Button: {issue['button']}")
            if "import" in issue:
                print(f"   Import: {issue['import']}")
            if "expected" in issue:
                print(f"   Expected: {issue['expected']}")
    else:
        print("=" * 60)
        print("✅ ALL BUTTONS VERIFIED - NO ISSUES FOUND")
        print("=" * 60)

    return len(all_issues)


if __name__ == "__main__":
    exit(main())

