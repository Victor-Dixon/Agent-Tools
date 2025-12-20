"""
Captain Operations Tools - Architecture Checks
===============================================

Architecture checking tools for captain operations.

V2 Compliance: <400 lines
Author: Agent-2 (Architecture & Design) - 2025-01-27
Split from captain_tools_utilities.py for V2 compliance
"""

import ast
import logging
import re
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class ArchitecturalCheckerTool(IToolAdapter):
    """Check for architectural issues (missing methods, circular imports)."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.architectural_check",
            version="1.0.0",
            category="captain",
            summary="Check for architectural issues (missing methods, circular imports)",
            required_params=["path"],
            optional_params={"check_circular": True, "check_missing": True},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        errors = []
        if "path" not in params:
            errors.append("path is required")
        return len(errors) == 0, errors

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Run architectural checks."""
        try:
            target_path = Path(params["path"])
            check_circular = params.get("check_circular", True)
            check_missing = params.get("check_missing", True)

            if not target_path.exists():
                return ToolResult(
                    success=False,
                    output={"error": f"Path not found: {target_path}"},
                    exit_code=1,
                )

            issues = []

            if target_path.is_file():
                files_to_check = [target_path]
            else:
                files_to_check = list(target_path.rglob("*.py"))

            # Check missing methods (simplified)
            if check_missing:
                for file_path in files_to_check:
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        tree = ast.parse(content)

                        # Find self.method() calls that may be undefined
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                                if isinstance(node.func.value, ast.Name) and node.func.value.id == "self":
                                    # Check if method exists in class
                                    found = False
                                    for item in tree.body:
                                        if isinstance(item, ast.ClassDef):
                                            for method in item.body:
                                                if isinstance(method, ast.FunctionDef):
                                                    if method.name == node.func.attr:
                                                        found = True
                                                        break
                                        if found:
                                            break

                                    if not found and not node.func.attr.startswith("_"):
                                        issues.append({
                                            "file": str(file_path),
                                            "line": node.lineno,
                                            "type": "missing_method",
                                            "method": node.func.attr,
                                        })
                    except Exception as e:
                        issues.append({
                            "file": str(file_path),
                            "type": "parse_error",
                            "error": str(e),
                        })

            # Check circular imports (simplified)
            if check_circular and target_path.is_dir():
                import_graph = {}
                for py_file in target_path.rglob("*.py"):
                    try:
                        content = py_file.read_text(encoding="utf-8")
                        imports = re.findall(r"from\s+([\w.]+)\s+import", content)
                        import_graph[str(py_file)] = [imp for imp in imports if imp.startswith("src.")]
                    except:
                        pass

                # Simple cycle detection
                for file1, imports1 in import_graph.items():
                    for imp in imports1:
                        imp_path = imp.replace(".", "/") + ".py"
                        for file2, imports2 in import_graph.items():
                            if imp_path in file2 and any(f1 in i for i in imports2 for f1 in [file1]):
                                issues.append({
                                    "type": "circular_import",
                                    "file1": file1,
                                    "file2": file2,
                                })

            missing_count = len([i for i in issues if i.get("type") == "missing_method"])
            circular_count = len([i for i in issues if i.get("type") == "circular_import"])

            return ToolResult(
                success=len(issues) == 0,
                output={
                    "files_checked": len(files_to_check),
                    "total_issues": len(issues),
                    "missing_methods": missing_count,
                    "circular_imports": circular_count,
                    "issues": issues[:20],  # Limit to first 20
                },
                exit_code=0 if len(issues) == 0 else 1,
                execution_time=0.0,
            )
        except Exception as e:
            logger.error(f"Error checking architecture: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.architectural_check")


# Export all tools
__all__ = [
    "ArchitecturalCheckerTool",
]




