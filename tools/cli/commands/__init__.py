"""CLI Commands Registry Package."""

try:
    from tools.cli.commands.registry import COMMAND_REGISTRY
except ImportError:
    COMMAND_REGISTRY = {}

__all__ = ["COMMAND_REGISTRY"]
