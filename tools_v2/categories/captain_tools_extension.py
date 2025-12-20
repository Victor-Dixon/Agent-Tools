"""
Captain Operations Tools - Extension (Backward Compatibility)
=============================================================

⚠️ DEPRECATED: This file has been split for V2 compliance (986 lines → 3 files).
All tools are now in:
- captain_tools_core.py (5 tools)
- captain_tools_messaging.py (2 tools)
- captain_tools_utilities.py (5 tools)

This file maintains backward compatibility by re-exporting all tools.

V2 Compliance: <400 lines (backward compatibility layer)
Author: Agent-2 (Architecture & Design) - 2025-01-27
Split from original 986-line file for V2 compliance
"""

# Re-export all tools from split files for backward compatibility
from .captain_tools_core import (
    StatusCheckTool,
    GitVerifyTool,
    WorkVerifyTool,
    IntegrityCheckTool,
)
from .captain_tools_messaging import (
    SelfMessageTool,
    MessageAllAgentsTool,
)
from .captain_tools_utilities import (
    FindIdleAgentsTool,
    GasCheckTool,
    UpdateLogTool,
    ToolbeltHelpTool,
)
from .captain_tools_architecture import ArchitecturalCheckerTool


# All tool classes are now imported from split files above


# Export all tools (re-exported from split files for backward compatibility)
__all__ = [
    "StatusCheckTool",
    "GitVerifyTool",
    "WorkVerifyTool",
    "IntegrityCheckTool",
    "SelfMessageTool",
    "MessageAllAgentsTool",
    "FindIdleAgentsTool",
    "GasCheckTool",
    "UpdateLogTool",
    "ArchitecturalCheckerTool",
    "ToolbeltHelpTool",
]
