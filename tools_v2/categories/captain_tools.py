"""
Captain Operations Tools
=========================

Tool adapters for Captain-specific operations discovered in Session 2025-10-13.

REFACTORED: 2025-01-27 - Split into 3 modules for V2 compliance:
- captain_tools_core.py: StatusCheck, GitVerify, WorkVerify, IntegrityCheck
- captain_tools_advanced.py: PointsCalculator, MissionAssign, MarkovOptimizer
- captain_tools_monitoring.py: GasDelivery, LeaderboardUpdate, CycleReport

This file maintains backward compatibility by re-exporting all classes.

V2 Compliance: <400 lines (now a facade module)
Author: Agent-4 (Captain) - Refactored 2025-01-27
"""

# Core operations
from .captain_tools_core import (
    GitVerifyTool,
    IntegrityCheckTool,
    StatusCheckTool,
    WorkVerifyTool,
)

# Advanced operations
from .captain_tools_advanced import (
    MarkovOptimizerTool,
    MissionAssignTool,
    PointsCalculatorTool,
)

# Monitoring operations
from .captain_tools_monitoring import (
    CycleReportTool,
    GasDeliveryTool,
    LeaderboardUpdateTool,
)

# Re-export for backward compatibility
__all__ = [
    # Core
    "StatusCheckTool",
    "GitVerifyTool",
    "WorkVerifyTool",
    "IntegrityCheckTool",
    # Advanced
    "PointsCalculatorTool",
    "MissionAssignTool",
    "MarkovOptimizerTool",
    # Monitoring
    "GasDeliveryTool",
    "LeaderboardUpdateTool",
    "CycleReportTool",
]
