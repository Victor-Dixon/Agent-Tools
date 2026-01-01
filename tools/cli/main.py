"""CLI entry point wrapper for the unified dispatcher."""

from __future__ import annotations

from tools.cli.dispatchers.unified_dispatcher import main as _main


def main() -> int:
    """Expose the unified dispatcher main for `from tools.cli import main`."""
    return _main()


__all__ = ["main"]
