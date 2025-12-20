#!/usr/bin/env python3
"""
Infrastructure Audit Tools - Agent Toolbelt V2
==============================================

Audit and analysis tools for infrastructure operations.

V2 Compliance: <400 lines
Author: Agent-2 (Architecture & Design) - Split from infrastructure_tools.py
Date: 2025-01-27
"""

import logging
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec

logger = logging.getLogger(__name__)


class OrchestratorScanTool(IToolAdapter):
    """Scan all orchestrators for violations and performance issues."""

    def get_name(self) -> str:
        return "orchestrator_scan"

    def get_description(self) -> str:
        return "Scan all orchestrator files for V2 violations and performance bottlenecks"

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="orchestrator_scan",
            version="1.0.0",
            category="infrastructure",
            summary="Scan all orchestrator files for V2 violations and performance bottlenecks",
            required_params=[],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters (no required params for this tool)."""
        return (True, [])

    def execute(
        self, params: dict[str, Any] = None, context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute orchestrator scan."""
        try:
            violations = []
            all_orchestrators = []

            # Find all orchestrator files
            patterns = ["*orchestrat*.py"]
            for pattern in patterns:
                files = list(Path(".").rglob(pattern))
                for f in files:
                    if f.is_file():
                        try:
                            lines = len(open(f).readlines())
                            all_orchestrators.append((str(f), lines))

                            # Check for violations
                            if lines > 400:
                                violations.append(
                                    {
                                        "file": str(f),
                                        "lines": lines,
                                        "severity": "CRITICAL",
                                        "over_limit": lines - 400,
                                    }
                                )
                            elif lines > 300:
                                violations.append(
                                    {
                                        "file": str(f),
                                        "lines": lines,
                                        "severity": "HIGH",
                                        "over_limit": lines - 300,
                                    }
                                )
                            elif lines > 250:
                                violations.append(
                                    {
                                        "file": str(f),
                                        "lines": lines,
                                        "severity": "MEDIUM",
                                        "approaching_limit": 400 - lines,
                                    }
                                )
                        except:
                            pass

            # Sort by line count
            all_orchestrators.sort(key=lambda x: x[1], reverse=True)
            violations.sort(key=lambda x: x.get("lines", 0), reverse=True)

            output = {
                "total_orchestrators": len(all_orchestrators),
                "violations": violations,
                "violation_count": len(violations),
                "top_10_largest": [
                    {"file": f, "lines": lines} for f, lines in all_orchestrators[:10]
                ],
            }
            return ToolResult(success=True, output=output)

        except Exception as e:
            logger.error(f"Orchestrator scan failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class FileLineCounterTool(IToolAdapter):
    """Quick line count for files (V2 compliance checking)."""

    def get_name(self) -> str:
        return "file_lines"

    def get_description(self) -> str:
        return "Count lines in file(s) for V2 compliance verification"

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="file_lines",
            version="1.0.0",
            category="infrastructure",
            summary="Count lines in file(s) for V2 compliance verification",
            required_params=["files"],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(
        self, params: dict[str, Any] = None, context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute line count."""
        try:
            if params is None:
                params = {}
            files = params.get("files", [])
            if isinstance(files, str):
                files = [files]

            results = []
            for filepath in files:
                try:
                    lines = len(open(filepath).readlines())
                    compliant = lines <= 400
                    results.append(
                        {
                            "file": filepath,
                            "lines": lines,
                            "v2_compliant": compliant,
                            "buffer": 400 - lines if compliant else None,
                            "over_by": lines - 400 if not compliant else None,
                        }
                    )
                except Exception as e:
                    results.append({"file": filepath, "error": str(e)})

            output = {
                "results": results,
                "total_files": len(results),
                "compliant_count": sum(1 for r in results if r.get("v2_compliant")),
            }
            return ToolResult(success=True, output=output)

        except Exception as e:
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class ToolRuntimeAuditTool(IToolAdapter):
    """Enhanced audit tools by running them to identify runtime failures (IMPROVED - Agent-7)."""
    def get_name(self) -> str:
        return "tool_runtime_audit"
    def get_description(self) -> str:
        return "Test tools by running them to identify runtime failures with enhanced web tool support"
    def get_spec(self) -> ToolSpec:
        return ToolSpec(name="tool_runtime_audit", version="2.0.0", category="infrastructure",
            summary="Enhanced runtime audit of tools with web tool categorization", required_params=[],
            optional_params={"directory": "tools", "verbose": False, "categorize": True, "web_only": False})
    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])
    def execute(self, params: dict[str, Any] = None, context: dict[str, Any] | None = None) -> ToolResult:
        try:
            import sys
            import subprocess
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
            from comprehensive_tool_runtime_audit import RuntimeAuditor
            params = params or {}
            auditor = RuntimeAuditor()
            directory = Path(params.get("directory", "tools"))
            
            # Enhanced: Categorize web tools
            web_keywords = ['web', 'dashboard', 'browser', 'frontend', 'ui', 'html', 'css', 'js']
            web_tools = []
            
            auditor.audit_directory(directory)
            
            # Categorize tools if requested
            if params.get("categorize", True):
                all_tools = auditor.results['cli_working'] + auditor.results['cli_broken']
                for tool_path in all_tools:
                    tool_name = Path(tool_path).name.lower()
                    if any(keyword in tool_name for keyword in web_keywords):
                        web_tools.append(tool_path)
            
            output = {
                "working": len(auditor.results['cli_working']),
                "broken": len(auditor.results['cli_broken']),
                "total": len(auditor.results['cli_working']) + len(auditor.results['cli_broken']),
                "broken_tools": auditor.results['cli_broken'][:10],
                "web_tools_found": len(web_tools),
                "web_tools": web_tools[:10] if params.get("web_only", False) else web_tools[:5]
            }
            
            # Enhanced: Filter to web tools only if requested
            if params.get("web_only", False):
                output["working"] = len([t for t in auditor.results['cli_working'] if t in web_tools])
                output["broken"] = len([t for t in auditor.results['cli_broken'] if t in web_tools])
                output["total"] = len(web_tools)
            
            return ToolResult(success=True, output=output)
        except Exception as e:
            logger.error(f"Tool runtime audit failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class BrokenToolsAuditTool(IToolAdapter):
    """Systematic testing and quarantine of broken tools."""
    def get_name(self) -> str:
        return "broken_tools_audit"
    def get_description(self) -> str:
        return "Systematic testing and quarantine of broken tools"
    def get_spec(self) -> ToolSpec:
        return ToolSpec(name="broken_tools_audit", version="1.0.0", category="infrastructure",
            summary="Audit broken tools for quarantine", required_params=[],
            optional_params={"directory": "tools", "verbose": False, "create_manifest": False})
    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])
    def execute(self, params: dict[str, Any] = None, context: dict[str, Any] | None = None) -> ToolResult:
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
            from audit_broken_tools import ToolAuditor
            params = params or {}
            auditor = ToolAuditor(verbose=params.get("verbose", False))
            directory = Path(params.get("directory", "tools"))
            results = auditor.audit_directory(directory)
            output = {
                "working": len(results['working']),
                "broken": len(results['broken']),
                "syntax_errors": len(results['syntax_errors']),
                "import_errors": len(results['import_errors']),
                "broken_tools": results['broken'][:10]
            }
            return ToolResult(success=True, output=output)
        except Exception as e:
            logger.error(f"Broken tools audit failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class ProjectComponentsAuditTool(IToolAdapter):
    """Audit project components for import errors and broken modules."""
    def get_name(self) -> str:
        return "project_components_audit"
    def get_description(self) -> str:
        return "Audit project components for import errors and broken modules"
    def get_spec(self) -> ToolSpec:
        return ToolSpec(name="project_components_audit", version="1.0.0", category="infrastructure",
            summary="Audit project components", required_params=[],
            optional_params={"categories": None})
    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])
    def execute(self, params: dict[str, Any] = None, context: dict[str, Any] | None = None) -> ToolResult:
        try:
            import sys
            import importlib
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            components = {
                "Core Systems": ["src.core.messaging_core", "src.core.unified_config"],
                "Services": ["src.services.messaging_cli", "src.services.unified_messaging_service"],
                "Tools V2": ["tools_v2.core.tool_facade", "tools_v2.core.tool_spec"]
            }
            results = {}
            for category, modules in components.items():
                category_results = []
                for module in modules:
                    try:
                        importlib.import_module(module)
                        category_results.append({"module": module, "status": "WORKING"})
                    except Exception as e:
                        category_results.append({"module": module, "status": "BROKEN", "error": str(e)[:100]})
                results[category] = category_results
            return ToolResult(success=True, output={"components": results})
        except Exception as e:
            logger.error(f"Project components audit failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


__all__ = [
    "OrchestratorScanTool",
    "FileLineCounterTool",
    "ToolRuntimeAuditTool",
    "BrokenToolsAuditTool",
    "ProjectComponentsAuditTool",
]




