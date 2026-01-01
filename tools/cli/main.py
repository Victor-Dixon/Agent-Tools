"""CLI entry point for the toolbelt registry and unified dispatcher."""

from __future__ import annotations

import sys

from tools.cli.dispatchers.unified_dispatcher import main as unified_main
from tools.toolbelt.__main__ import main as toolbelt_main
from tools.toolbelt_registry import ToolRegistry

def main() -> int:
    """Route between toolbelt flags and unified dispatcher commands."""
    if _should_use_toolbelt(sys.argv):
        try:
            toolbelt_main()
        except SystemExit as exc:
            if _should_propagate_system_exit(sys.argv):
                raise
            return exc.code or 0
        return 0
    return unified_main()


def _should_use_toolbelt(argv: list[str]) -> bool:
    if len(argv) < 2:
        return False
    first_arg = argv[1]
    if not first_arg.startswith("-"):
        return False
    registry = ToolRegistry()
    return first_arg in registry.get_all_flags() or first_arg in {"--list", "--help", "-h"}


def _should_propagate_system_exit(argv: list[str]) -> bool:
    if len(argv) < 2:
        return False
    return argv[1] in {"--help", "-h"}


__all__ = ["main"]
