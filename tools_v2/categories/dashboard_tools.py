"""
Dashboard Tools
===============

Tool adapters for dashboard generation and web UI tools.

V2 Compliance: <400 lines
Author: Agent-7 - Web Development Specialist
Date: 2025-01-27
"""

import logging
import subprocess
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class DashboardGenerateTool(IToolAdapter):
    """Generate compliance dashboards."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="dashboard.generate",
            version="1.0.0",
            category="dashboard",
            summary="Generate compliance dashboard with V2 metrics and charts",
            required_params=["directory"],
            optional_params={
                "pattern": "**/*.py",
                "include_history": True,
                "output_dir": "reports/dashboards",
            },
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute dashboard generation."""
        try:
            cmd = [
                "python",
                "tools/compliance_dashboard.py",
                "--directory",
                str(params["directory"]),
            ]

            if params.get("pattern"):
                cmd.extend(["--pattern", str(params["pattern"])])

            if params.get("include_history"):
                cmd.append("--history")

            if params.get("output_dir"):
                cmd.extend(["--output", str(params["output_dir"])])

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")
            raise ToolExecutionError(str(e), tool_name="dashboard.generate")


class DashboardDataAggregateTool(IToolAdapter):
    """Aggregate data for dashboard generation."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="dashboard.data",
            version="1.0.0",
            category="dashboard",
            summary="Aggregate data from quality tools for dashboard",
            required_params=[],
            optional_params={
                "v2_report": None,
                "complexity_reports": None,
                "suggestions": None,
            },
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])  # No required params

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute data aggregation."""
        try:
            # Import and use DashboardDataAggregator directly
            import sys
            from pathlib import Path

            tools_path = Path(__file__).parent.parent.parent / "tools"
            sys.path.insert(0, str(tools_path))

            from dashboard_data_aggregator import DashboardDataAggregator

            aggregator = DashboardDataAggregator()
            # This would typically be called by dashboard.generate
            # For now, return info about the aggregator
            return ToolResult(
                success=True,
                output="DashboardDataAggregator available for data aggregation",
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error aggregating dashboard data: {e}")
            raise ToolExecutionError(str(e), tool_name="dashboard.data")


class DashboardHTMLTool(IToolAdapter):
    """Generate HTML for dashboards."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="dashboard.html",
            version="1.0.0",
            category="dashboard",
            summary="Generate HTML content for compliance dashboards",
            required_params=["data"],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute HTML generation."""
        try:
            # Import and use DashboardHTMLGenerator directly
            import sys
            from pathlib import Path

            tools_path = Path(__file__).parent.parent.parent / "tools"
            sys.path.insert(0, str(tools_path))

            from dashboard_html_generator_refactored import DashboardHTMLGenerator

            generator = DashboardHTMLGenerator()
            html = generator.generate_html(params["data"])

            return ToolResult(
                success=True,
                output=html,
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error generating HTML: {e}")
            raise ToolExecutionError(str(e), tool_name="dashboard.html")


class DashboardChartsTool(IToolAdapter):
    """Generate JavaScript charts for dashboards."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="dashboard.charts",
            version="1.0.0",
            category="dashboard",
            summary="Generate JavaScript chart code for dashboards",
            required_params=["data"],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute chart generation."""
        try:
            # Import and use DashboardCharts directly
            import sys
            from pathlib import Path

            tools_path = Path(__file__).parent.parent.parent / "tools"
            sys.path.insert(0, str(tools_path))

            from dashboard_charts import DashboardCharts

            charts = DashboardCharts()
            chart_js = charts.generate_charts(params["data"])

            return ToolResult(
                success=True,
                output=chart_js,
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
            raise ToolExecutionError(str(e), tool_name="dashboard.charts")


class DashboardStylesTool(IToolAdapter):
    """Generate CSS styles for dashboards."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="dashboard.styles",
            version="1.0.0",
            category="dashboard",
            summary="Generate CSS styles for compliance dashboards",
            required_params=[],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])  # No required params

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute style generation."""
        try:
            # Import and use DashboardStyles directly
            import sys
            from pathlib import Path

            tools_path = Path(__file__).parent.parent.parent / "tools"
            sys.path.insert(0, str(tools_path))

            from dashboard_styles import DashboardStyles

            styles = DashboardStyles()
            css = styles.get_css()

            return ToolResult(
                success=True,
                output=css,
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error generating styles: {e}")
            raise ToolExecutionError(str(e), tool_name="dashboard.styles")


class DiscordStatusDashboardTool(IToolAdapter):
    """Generate Discord status dashboard."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="dashboard.discord",
            version="1.0.0",
            category="dashboard",
            summary="Generate Discord status dashboard",
            required_params=[],
            optional_params={"output_file": None},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])  # No required params

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute Discord dashboard generation."""
        try:
            cmd = ["python", "tools/discord_status_dashboard.py"]

            if params.get("output_file"):
                cmd.extend(["--output", str(params["output_file"])])

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error generating Discord dashboard: {e}")
            raise ToolExecutionError(str(e), tool_name="dashboard.discord")


__all__ = [
    "DashboardGenerateTool",
    "DashboardDataAggregateTool",
    "DashboardHTMLTool",
    "DashboardChartsTool",
    "DashboardStylesTool",
    "DiscordStatusDashboardTool",
]

