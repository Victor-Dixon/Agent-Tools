"""CLI package for toolbelt entry points."""

from tools.cli.dispatchers.unified_dispatcher import main

__all__ = ["main"]
"""
CLI Tools Package - Unified CLI Framework

Provides the unified CLI dispatcher for all tools.

Usage:
    from tools.cli import main
    main()

Or via command line:
    python -m tools.cli [command] [args]
"""

from tools.cli.dispatchers.unified_dispatcher import UnifiedCLIDispatcher
from tools.cli.main import main

__all__ = ["main", "UnifiedCLIDispatcher"]
