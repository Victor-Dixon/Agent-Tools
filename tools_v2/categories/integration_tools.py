"""
Integration Tools - Agent Toolbelt Category
===========================================

Tools for integration specialist work: finding SSOT violations, duplicate
functionality, and integration opportunities.

Based on Agent-1's actual workflow from session.

Author: Agent-1 (Integration & Core Systems Specialist)
"""

import subprocess
from pathlib import Path

from ..adapters.base_adapter import IToolAdapter, ToolResult


class FindSSOTViolationsAdapter(IToolAdapter):
    """Find potential SSOT (Single Source of Truth) violations."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="integration.find-ssot-violations",
            version="1.0.0",
            category="integration",
            summary="Find potential SSOT violations in codebase",
            required_params=[],
            optional_params={"path": "src/"},
        )

    def get_help(self) -> str:
        return """
Find SSOT Violations
===================
Searches for files that might violate Single Source of Truth principle.

Parameters:
  path: Directory to search (default: src/)
  
Returns: List of potential SSOT violations
        """

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        path = params.get("path", "src/")

        try:
            # Look for duplicate config patterns
            result = subprocess.run(
                ["python", "-m", "grep", "-i", "class.*Config", "--files-with-matches", path],
                capture_output=True,
                text=True,
            )

            config_files = result.stdout.strip().split("\n") if result.stdout else []

            # Look for duplicate SSOT claims
            result2 = subprocess.run(
                [
                    "python",
                    "-m",
                    "grep",
                    "-i",
                    "SINGLE SOURCE OF TRUTH|SSOT",
                    "--files-with-matches",
                    path,
                ],
                capture_output=True,
                text=True,
            )

            ssot_files = result2.stdout.strip().split("\n") if result2.stdout else []

            violations = {
                "multiple_config_files": config_files,
                "multiple_ssot_claims": ssot_files,
                "potential_violations": len(config_files) > 1 or len(ssot_files) > 1,
            }

            return ToolResult(success=True, output=violations, exit_code=0)
        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class FindDuplicateFunctionalityAdapter(IToolAdapter):
    """Find duplicate functionality across services/modules."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="integration.find-duplicates",
            version="1.0.0",
            category="integration",
            summary="Find duplicate functionality across codebase",
            required_params=["pattern"],
            optional_params={"path": "src/"},
        )

    def get_help(self) -> str:
        return """
Find Duplicate Functionality
============================
Searches for similar class names or functionality across codebase.

Parameters:
  pattern: Pattern to search for (e.g., "Service", "Manager")
  path: Directory to search (default: src/)
  
Returns: List of files with matching patterns
        """

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        if "pattern" not in params:
            return False, ["pattern"]
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        pattern = params["pattern"]
        path = params.get("path", "src/")

        try:
            result = subprocess.run(
                ["python", "-m", "grep", "-i", f"class.*{pattern}", "--output-mode", "count", path],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            output = {"pattern": pattern, "search_path": path, "results": result.stdout}

            return ToolResult(success=True, output=output, exit_code=0)
        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class FindIntegrationOpportunitiesAdapter(IToolAdapter):
    """Analyze codebase for integration opportunities."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="integration.find-opportunities",
            version="1.0.0",
            category="integration",
            summary="Analyze codebase for integration opportunities",
            required_params=[],
            optional_params={"focus": "all"},
        )

    def get_help(self) -> str:
        return """
Find Integration Opportunities
==============================
Analyzes project structure to find integration opportunities.

Parameters:
  focus: Area to focus on (config, services, managers, all)
  
Returns: List of potential integration opportunities
        """

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        focus = params.get("focus", "all")

        try:
            opportunities = []

            # Check for multiple config files
            if focus in ["config", "all"]:
                config_check = subprocess.run(
                    ["python", "-m", "glob_file_search", "**/config*.py", "src"],
                    capture_output=True,
                    text=True,
                )
                if config_check.returncode == 0:
                    config_files = config_check.stdout.strip().split("\n")
                    if len(config_files) > 2:
                        opportunities.append(
                            {
                                "type": "config_consolidation",
                                "files": config_files,
                                "priority": "high",
                            }
                        )

            # Check for multiple service files
            if focus in ["services", "all"]:
                service_check = subprocess.run(
                    ["python", "-m", "glob_file_search", "**/*service*.py", "src/services"],
                    capture_output=True,
                    text=True,
                )
                if service_check.returncode == 0:
                    service_files = service_check.stdout.strip().split("\n")
                    if len(service_files) > 5:
                        opportunities.append(
                            {
                                "type": "service_consolidation",
                                "count": len(service_files),
                                "priority": "medium",
                            }
                        )

            return ToolResult(
                success=True,
                output={"opportunities": opportunities, "count": len(opportunities)},
                exit_code=0,
            )
        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class CheckImportDependenciesAdapter(IToolAdapter):
    """Check import dependencies for circular imports or heavy dependencies."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="integration.check-imports",
            version="1.0.0",
            category="integration",
            summary="Check import dependencies for issues",
            required_params=["file"],
            optional_params={},
        )

    def get_help(self) -> str:
        return """
Check Import Dependencies
========================
Analyzes import statements to find circular dependencies or heavy imports.

Parameters:
  file: File to analyze
  
Returns: Dependency analysis
        """

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        if "file" not in params:
            return False, ["file"]
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        file_path = params["file"]

        try:
            with open(file_path) as f:
                content = f.read()

            imports = []
            for line in content.split("\n"):
                if line.strip().startswith(("import ", "from ")):
                    imports.append(line.strip())

            analysis = {
                "file": file_path,
                "import_count": len(imports),
                "imports": imports,
                "has_relative_imports": any("from ." in imp for imp in imports),
                "has_heavy_imports": any(
                    any(pkg in imp for pkg in ["browser", "selenium", "playwright"])
                    for imp in imports
                ),
            }

            return ToolResult(success=True, output=analysis, exit_code=0)
        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class AuditImportsTool(IToolAdapter):
    """Audit all imports in a directory to identify broken components."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="integration.audit_imports",
            version="1.0.0",
            category="integration",
            summary="Audit all imports in a directory to identify broken components",
            required_params=[],
            optional_params={"base_path": "src", "output_file": None},
        )

    def get_help(self) -> str:
        return """
Audit Imports
=============
Systematically test all Python imports to identify broken components.

Parameters:
  base_path: Directory to audit (default: src/)
  output_file: Optional file to save results (default: None)
  
Returns: Dictionary with working, broken, and skipped imports
        """

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute import audit."""
        try:
            import sys
            from pathlib import Path

            # Add tools to path
            tools_path = Path(__file__).parent.parent.parent / "tools"
            sys.path.insert(0, str(tools_path))

            # Import audit_imports
            from audit_imports import audit_imports

            # Get parameters
            base_path = params.get("base_path", "src")
            output_file = params.get("output_file")

            # Run audit
            results = audit_imports(base_path)

            # Save to file if requested
            if output_file:
                output_path = Path(output_file)
                import json
                output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

            # Format output
            output = {
                "base_path": base_path,
                "total_files": results.get("total", 0),
                "working": len(results.get("working", [])),
                "broken": len(results.get("broken", [])),
                "skipped": len(results.get("skipped", [])),
                "broken_details": results.get("broken", [])[:20],  # Limit to first 20
                "output_file": str(output_file) if output_file else None,
            }

            return ToolResult(
                success=len(results.get("broken", [])) == 0,
                output=output,
                exit_code=0 if len(results.get("broken", [])) == 0 else 1,
            )

        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


# Registration dictionary
INTEGRATION_TOOLS = {
    "integration.find-ssot-violations": FindSSOTViolationsAdapter,
    "integration.find-duplicates": FindDuplicateFunctionalityAdapter,
    "integration.find-opportunities": FindIntegrationOpportunitiesAdapter,
    "integration.check-imports": CheckImportDependenciesAdapter,
    "integration.audit_imports": AuditImportsTool,
}
