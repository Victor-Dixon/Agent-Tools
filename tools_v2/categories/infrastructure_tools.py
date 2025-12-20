#!/usr/bin/env python3
"""
Infrastructure Tools - Agent Toolbelt V2 (Backward Compatibility)
==================================================================

⚠️ DEPRECATED: This file has been split for V2 compliance (748 lines → 3 files).
All tools are now in:
- infrastructure_workspace_tools.py (6 tools)
- infrastructure_audit_tools.py (5 tools)
- infrastructure_utility_tools.py (3 tools)

This file maintains backward compatibility by re-exporting all tools.

V2 Compliance: <400 lines (backward compatibility layer)
Author: Agent-2 (Architecture & Design) - 2025-01-27
Split from original 748-line file for V2 compliance
"""

# Re-export all tools from split files for backward compatibility
from .infrastructure_workspace_tools import (
    WorkspaceHealthMonitorTool,
    WorkspaceAutoCleanerTool,
    AgentStatusQuickCheckTool,
    AutoStatusUpdaterTool,
    SessionTransitionAutomatorTool,
    SwarmStatusBroadcasterTool,
)
from .infrastructure_audit_tools import (
    OrchestratorScanTool,
    FileLineCounterTool,
    ToolRuntimeAuditTool,
    BrokenToolsAuditTool,
    ProjectComponentsAuditTool,
)
from .infrastructure_utility_tools import (
    InfrastructureROICalculatorTool,
    ModuleExtractorPlannerTool,
    BrowserPoolManagerTool,
)


# All tool classes are now imported from split files above


# Export all tools (re-exported from split files for backward compatibility)
__all__ = [
    "OrchestratorScanTool",
    "FileLineCounterTool",
    "ModuleExtractorPlannerTool",
    "InfrastructureROICalculatorTool",
    "WorkspaceHealthMonitorTool",
    "WorkspaceAutoCleanerTool",
    "BrowserPoolManagerTool",
    "AgentStatusQuickCheckTool",
    "ToolRuntimeAuditTool",
    "BrokenToolsAuditTool",
    "AutoStatusUpdaterTool",
    "SessionTransitionAutomatorTool",
    "SwarmStatusBroadcasterTool",
    "ProjectComponentsAuditTool",
]
