#!/usr/bin/env python3
"""
Legacy CLI entry point for toolbelt and unified dispatcher.

SSOT: This file is the single entry point for `python tools/cli.py` usage.
It routes flag-style invocations to the toolbelt registry and command-style
invocations to the unified CLI dispatcher.
"""

from __future__ import annotations

import sys

from tools.cli.dispatchers.unified_dispatcher import main as unified_main
from tools.toolbelt.__main__ import main as toolbelt_main
from tools.toolbelt_registry import ToolRegistry


def _should_use_toolbelt(argv: list[str]) -> bool:
    if len(argv) < 2:
        return False
    first_arg = argv[1]
    if not first_arg.startswith("-"):
        return False
    registry = ToolRegistry()
    return first_arg in registry.get_all_flags() or first_arg in {"--list", "--help", "-h"}


def main() -> int:
    if _should_use_toolbelt(sys.argv):
        toolbelt_main()
        return 0
    return unified_main()
"""Legacy CLI module shim for tooling expecting tools/cli.py."""

from __future__ import annotations

from tools.cli.main import main


if __name__ == "__main__":
    raise SystemExit(main())
