"""
Business Intelligence Tools
===========================

Tool adapters for business intelligence, metrics, and ROI analysis operations.

V2 Compliance: <400 lines
Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-01-27
"""

import logging
import subprocess
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class QuickMetricsTool(IToolAdapter):
    """Quick file metrics analysis tool."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="bi.metrics",
            version="1.0.0",
            category="business_intelligence",
            summary="Quick analysis of Python file metrics (lines, classes, functions, V2 compliance)",
            required_params=["files"],
            optional_params={"pattern": None, "json": False, "summary": False, "violations_only": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute quick metrics analysis."""
        try:
            cmd = ["python", "tools/quick_metrics.py"]
            
            # Handle files parameter (can be string or list)
            files = params["files"]
            if isinstance(files, list):
                cmd.extend(files)
            elif isinstance(files, str):
                cmd.append(files)
            
            # Add optional flags
            if params.get("pattern"):
                cmd.extend(["--pattern", params["pattern"]])
            if params.get("json"):
                cmd.append("--json")
            if params.get("summary"):
                cmd.append("--summary")
            if params.get("violations_only"):
                cmd.append("--violations-only")

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error running quick metrics: {e}")
            raise ToolExecutionError(str(e), tool_name="bi.metrics")


class RepoROICalculatorTool(IToolAdapter):
    """Calculate ROI for GitHub repositories."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="bi.roi.repo",
            version="1.0.0",
            category="business_intelligence",
            summary="Calculate ROI for GitHub repositories (keep vs archive decision)",
            required_params=["repo_path"],
            optional_params={"output_format": "text", "detailed": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute repository ROI calculation."""
        try:
            cmd = ["python", "tools/github_repo_roi_calculator.py", params["repo_path"]]
            
            if params.get("detailed"):
                cmd.append("--detailed")
            if params.get("output_format") == "json":
                cmd.append("--json")

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error calculating repo ROI: {e}")
            raise ToolExecutionError(str(e), tool_name="bi.roi.repo")


class TaskROICalculatorTool(IToolAdapter):
    """Calculate ROI for tasks using Captain's ROI calculator."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="bi.roi.task",
            version="1.0.0",
            category="business_intelligence",
            summary="Calculate task ROI (points, complexity, V2 impact, autonomy impact)",
            required_params=["points", "complexity"],
            optional_params={"v2_impact": 0, "autonomy_impact": 0},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        is_valid, missing = spec.validate_params(params)
        
        # Additional validation
        if is_valid:
            if params["points"] < 0:
                return (False, ["points must be >= 0"])
            if params["complexity"] < 1:
                return (False, ["complexity must be >= 1"])
            if params.get("v2_impact", 0) < 0:
                return (False, ["v2_impact must be >= 0"])
            if params.get("autonomy_impact", 0) < 0:
                return (False, ["autonomy_impact must be >= 0"])
        
        return (is_valid, missing)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute task ROI calculation."""
        try:
            cmd = [
                "python",
                "tools/captain_roi_quick_calc.py",
                "--points", str(params["points"]),
                "--complexity", str(params["complexity"]),
            ]
            
            if params.get("v2_impact", 0) > 0:
                cmd.extend(["--v2", str(params["v2_impact"])])
            if params.get("autonomy_impact", 0) > 0:
                cmd.extend(["--autonomy", str(params["autonomy_impact"])])

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error calculating task ROI: {e}")
            raise ToolExecutionError(str(e), tool_name="bi.roi.task")


class MarkovROIOptimizerTool(IToolAdapter):
    """Optimize task ROI using Markov chain and ROI analysis."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="bi.roi.optimize",
            version="1.0.0",
            category="business_intelligence",
            summary="Optimize task assignment using Markov chain and ROI analysis for all agents",
            required_params=[],
            optional_params={"output_format": "text", "max_tasks": 10},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])  # No required params

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute Markov ROI optimization."""
        try:
            cmd = ["python", "tools/markov_8agent_roi_optimizer.py"]
            
            if params.get("output_format") == "json":
                cmd.append("--json")
            if params.get("max_tasks"):
                cmd.extend(["--max-tasks", str(params["max_tasks"])])

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error optimizing ROI: {e}")
            raise ToolExecutionError(str(e), tool_name="bi.roi.optimize")

