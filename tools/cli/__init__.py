"""
CLI Tools Package - Unified CLI Framework
==========================================

Provides the unified CLI dispatcher for all tools.

Usage:
    from tools.cli import main
    main()

Or via command line:
    python -m tools.cli [command] [args]
"""

from tools.cli.dispatchers.unified_dispatcher import main, UnifiedCLIDispatcher

__all__ = ["main", "UnifiedCLIDispatcher"]
