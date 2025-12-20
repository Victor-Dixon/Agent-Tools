#!/usr/bin/env python3
"""
Infrastructure Utility Tools - Agent Toolbelt V2
================================================

Utility and helper tools for infrastructure operations.

V2 Compliance: <400 lines
Author: Agent-2 (Architecture & Design) - Split from infrastructure_tools.py
Date: 2025-01-27
"""

import logging
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec

logger = logging.getLogger(__name__)


class ModuleExtractorPlannerTool(IToolAdapter):
    """Analyze file and suggest extraction opportunities."""

    def get_name(self) -> str:
        return "extract_planner"

    def get_description(self) -> str:
        return "Analyze file and suggest modular extraction plan"

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="extract_planner",
            version="1.0.0",
            category="infrastructure",
            summary="Analyze file and suggest modular extraction plan",
            required_params=["file"],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(
        self, params: dict[str, Any] = None, context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute extraction planning."""
        try:
            if params is None:
                params = {}
            filepath = params.get("file")
            if not filepath:
                return ToolResult(
                    success=False, output=None, error_message="No file specified", exit_code=1
                )

            with open(filepath) as f:
                content = f.read()
                lines = content.splitlines()

            # Count classes and functions
            classes = [l.strip() for l in lines if l.strip().startswith("class ")]
            functions = [l.strip() for l in lines if "def " in l and not l.strip().startswith("#")]
            imports = [l.strip() for l in lines if l.strip().startswith(("import ", "from "))]

            # Suggest extractions
            suggestions = []

            if len(classes) > 5:
                suggestions.append(
                    {
                        "type": "class_extraction",
                        "reason": f"{len(classes)} classes (>5 limit)",
                        "recommendation": "Extract classes into logical groups",
                    }
                )

            if len(functions) > 30:
                suggestions.append(
                    {
                        "type": "function_extraction",
                        "reason": f"{len(functions)} functions (high count)",
                        "recommendation": "Group related functions into modules",
                    }
                )

            if len(lines) > 400:
                suggestions.append(
                    {
                        "type": "file_size",
                        "reason": f"{len(lines)} lines (>400 V2 limit)",
                        "recommendation": f"Extract {len(lines) - 400}+ lines",
                    }
                )

            output = {
                "file": filepath,
                "metrics": {
                    "lines": len(lines),
                    "classes": len(classes),
                    "functions": len(functions),
                    "imports": len(imports),
                },
                "class_list": classes[:20],  # First 20
                "function_list": functions[:20],
                "suggestions": suggestions,
                "needs_extraction": len(suggestions) > 0,
            }
            return ToolResult(success=True, output=output)

        except Exception as e:
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class InfrastructureROICalculatorTool(IToolAdapter):
    """
    Calculate ROI for infrastructure refactoring tasks.
    
    SSOT: This is the infrastructure-specific ROI calculator.
    For workflow ROI, use workflow.roi (workflow_tools.py).
    For captain ROI, use captain.calculate_roi (captain_coordination_tools.py).
    """

    def get_name(self) -> str:
        return "infra_roi_calculator"

    def get_description(self) -> str:
        return "Calculate ROI for infrastructure refactoring tasks (points/complexity)"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="infra.roi_calc", version="1.0.0", category="infrastructure",
            summary="Calculate ROI for refactoring tasks",
            required_params=["points", "complexity"],
            optional_params={"v2_impact": 0, "autonomy_impact": 0},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return self.get_spec().validate_params(params)

    def execute(
        self, params: dict[str, Any] = None, context: dict[str, Any] | None = None
    ) -> ToolResult:
        try:
            params = params or {}
            reward = params.get("points", 0) + (params.get("v2_impact", 0) * 100) + (params.get("autonomy_impact", 0) * 200)
            roi = reward / max(params.get("complexity", 1), 1)
            return ToolResult(success=True, output={
                **params, "reward": reward, "roi": round(roi, 2),
                "rating": "EXCELLENT" if roi > 20 else "GOOD" if roi > 15 else "FAIR" if roi > 10 else "LOW"
            })
        except Exception as e:
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class BrowserPoolManagerTool(IToolAdapter):
    """Manage browser instance pool for performance optimization."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="browser.pool",
            version="1.0.0",
            category="infrastructure",
            summary="Manage browser instance pool for 20%+ performance improvement",
            required_params=[],
            optional_params={
                "pool_size": 3,
                "max_lifetime_minutes": 60,
                "max_usage_per_instance": 100,
                "headless": True,
                "action": "get",  # get, cleanup, status
            },
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])  # No required params

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute browser pool management."""
        try:
            import sys
            from pathlib import Path

            tools_path = Path(__file__).parent.parent.parent / "tools"
            sys.path.insert(0, str(tools_path))

            from browser_pool_manager import BrowserPoolManager

            pool_size = params.get("pool_size", 3)
            max_lifetime = params.get("max_lifetime_minutes", 60)
            max_usage = params.get("max_usage_per_instance", 100)
            headless = params.get("headless", True)
            action = params.get("action", "get")

            manager = BrowserPoolManager(
                pool_size=pool_size,
                max_lifetime_minutes=max_lifetime,
                max_usage_per_instance=max_usage,
                headless=headless,
            )

            if action == "get":
                browser = manager.get_browser()
                return ToolResult(
                    success=True,
                    output=f"Browser instance obtained from pool (size: {pool_size})",
                    exit_code=0,
                )
            elif action == "cleanup":
                manager.cleanup_expired()
                return ToolResult(
                    success=True,
                    output="Expired browser instances cleaned up",
                    exit_code=0,
                )
            elif action == "status":
                status = {
                    "pool_size": pool_size,
                    "active_instances": len(manager._pool),
                    "max_lifetime_minutes": max_lifetime,
                    "max_usage_per_instance": max_usage,
                }
                return ToolResult(success=True, output=status, exit_code=0)
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Unknown action: {action}",
                    exit_code=1,
                )
        except Exception as e:
            logger.error(f"Browser pool manager failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )


__all__ = [
    "ModuleExtractorPlannerTool",
    "InfrastructureROICalculatorTool",
    "BrowserPoolManagerTool",
]




