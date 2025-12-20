"""
Config Tools - Agent Toolbelt Category
======================================

Tools for config validation, SSOT compliance, and configuration management.

Based on Agent-1's config SSOT integration work.

Author: Agent-1 (Integration & Core Systems Specialist)
"""

import subprocess
from pathlib import Path

from ..adapters.base_adapter import IToolAdapter, ToolResult


class ValidateConfigSSOTAdapter(IToolAdapter):
    """Validate that config follows SSOT principle."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="config.validate-ssot",
            version="1.0.0",
            category="config",
            summary="Validate config SSOT compliance",
            required_params=[],
            optional_params={},
        )

    def get_help(self) -> str:
        return """
Validate Config SSOT
===================
Validates that configuration follows Single Source of Truth principle.

Parameters:
  None
  
Returns: SSOT validation status
        """

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        try:
            # Check for config_ssot.py (should be THE SSOT)
            ssot_path = Path("src/core/config_ssot.py")
            ssot_exists = ssot_path.exists()

            # Check for unified_config.py (should be facade)
            facade_path = Path("src/core/unified_config.py")
            facade_exists = facade_path.exists()

            # Check if facade delegates to SSOT
            delegates_properly = False
            if facade_exists:
                with open(facade_path) as f:
                    content = f.read()
                    delegates_properly = "from .config_ssot import" in content

            # Find all config files
            config_files = list(Path("src").rglob("*config*.py"))

            validation = {
                "ssot_exists": ssot_exists,
                "facade_exists": facade_exists,
                "facade_delegates": delegates_properly,
                "total_config_files": len(config_files),
                "compliant": ssot_exists and (not facade_exists or delegates_properly),
                "issues": [],
            }

            if not ssot_exists:
                validation["issues"].append("config_ssot.py not found - no SSOT defined")

            if facade_exists and not delegates_properly:
                validation["issues"].append(
                    "unified_config.py exists but does not delegate to SSOT"
                )

            if len(config_files) > 5:
                validation["issues"].append(
                    f"{len(config_files)} config files found - possible fragmentation"
                )

            return ToolResult(success=True, output=validation, exit_code=0)
        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class ListConfigSourcesAdapter(IToolAdapter):
    """List all configuration sources in project."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="config.list-sources",
            version="1.0.0",
            category="config",
            summary="List all configuration sources",
            required_params=[],
            optional_params={"detail": False},
        )

    def get_help(self) -> str:
        return """
List Config Sources
==================
Lists all configuration files and sources.

Parameters:
  detail: Show detailed info (true/false, default: false)
  
Returns: List of configuration sources
        """

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        detail = params.get("detail", False)

        try:
            config_files = list(Path("src").rglob("*config*.py"))

            sources = []
            for config_file in config_files:
                source_info = {"path": str(config_file), "name": config_file.name}

                if detail:
                    # Get line count
                    with open(config_file) as f:
                        lines = len(f.readlines())
                    source_info["lines"] = lines

                    # Check if it claims to be SSOT
                    with open(config_file) as f:
                        content = f.read()
                        source_info["claims_ssot"] = (
                            "SINGLE SOURCE OF TRUTH" in content or "SSOT" in content
                        )

                sources.append(source_info)

            return ToolResult(
                success=True, output={"sources": sources, "count": len(sources)}, exit_code=0
            )
        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class CheckConfigImportsAdapter(IToolAdapter):
    """Check what imports config files."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="config.check-imports",
            version="1.0.0",
            category="config",
            summary="Check files importing configuration",
            required_params=["config_file"],
            optional_params={},
        )

    def get_help(self) -> str:
        return """
Check Config Imports
===================
Finds all files that import configuration.

Parameters:
  config_file: Config file to check (e.g., "config_ssot", "unified_config")
  
Returns: List of files importing the config
        """

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        if "config_file" not in params:
            return False, ["config_file"]
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        config_file = params["config_file"]

        try:
            # Search for imports
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "grep",
                    f"from.*{config_file} import|import.*{config_file}",
                    "--output-mode",
                    "files-with-matches",
                    "src",
                ],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            if result.returncode == 0:
                importing_files = result.stdout.strip().split("\n") if result.stdout else []
            else:
                importing_files = []

            return ToolResult(
                success=True,
                output={
                    "config_file": config_file,
                    "importing_files": importing_files,
                    "count": len(importing_files),
                },
                exit_code=0,
            )
        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


# Registration dictionary
CONFIG_TOOLS = {
    "config.validate-ssot": ValidateConfigSSOTAdapter,
    "config.list-sources": ListConfigSourcesAdapter,
    "config.check-imports": CheckConfigImportsAdapter,
}
