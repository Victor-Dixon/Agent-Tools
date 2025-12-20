#!/usr/bin/env python3
"""
Import Fix Tools
===============

Tools for fixing broken imports after refactoring.
Based on Agent-1 refactoring mission learnings.

Author: Agent-1 - Testing & Quality Assurance Specialist  
Created: 2025-10-14
"""

import ast
import logging
import subprocess
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class ImportValidatorTool(IToolAdapter):
    """Validate imports in a file or directory."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="refactor.validate_imports",
            version="1.0.0",
            category="refactoring",
            summary="Validate all imports can be resolved",
            required_params=["path"],
            optional_params={"fix": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute import validation."""
        try:
            path = Path(params["path"])
            broken_imports = []

            if path.is_file():
                files_to_check = [path]
            else:
                files_to_check = list(path.rglob("*.py"))

            for file in files_to_check:
                try:
                    content = file.read_text(encoding="utf-8")
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                # Try importing
                                try:
                                    __import__(alias.name)
                                except ImportError as e:
                                    broken_imports.append(
                                        {
                                            "file": str(file),
                                            "import": alias.name,
                                            "error": str(e),
                                            "line": node.lineno,
                                        }
                                    )
                        elif isinstance(node, ast.ImportFrom):
                            module = node.module or ""
                            try:
                                __import__(module)
                            except ImportError as e:
                                broken_imports.append(
                                    {
                                        "file": str(file),
                                        "import": module,
                                        "error": str(e),
                                        "line": node.lineno,
                                    }
                                )

                except SyntaxError as e:
                    broken_imports.append(
                        {"file": str(file), "import": "N/A", "error": f"Syntax error: {e}"}
                    )

            return ToolResult(
                success=len(broken_imports) == 0,
                output={
                    "files_checked": len(files_to_check),
                    "broken_imports": broken_imports,
                    "total_issues": len(broken_imports),
                    "status": "all_valid" if len(broken_imports) == 0 else "issues_found",
                },
                exit_code=0 if len(broken_imports) == 0 else 1,
            )

        except Exception as e:
            logger.error(f"Error validating imports: {e}")
            raise ToolExecutionError(str(e), tool_name="refactor.validate_imports")


class ModuleExtractorTool(IToolAdapter):
    """Extract functions/classes to new module file."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="refactor.extract_module",
            version="1.0.0",
            category="refactoring",
            summary="Extract specific functions/classes to new module",
            required_params=["source_file", "target_module", "items"],
            optional_params={"preserve_imports": True},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute module extraction."""
        try:
            source_file = Path(params["source_file"])
            target_module = Path(params["target_module"])
            items_to_extract = params["items"]  # List of function/class names

            content = source_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            extracted_code = []
            imports_needed = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name in items_to_extract:
                    extracted_code.append(ast.unparse(node))
                elif isinstance(node, ast.FunctionDef) and node.name in items_to_extract:
                    extracted_code.append(ast.unparse(node))

            # Generate new module content
            module_content = f'''#!/usr/bin/env python3
"""
{target_module.stem.replace('_', ' ').title()}
Extracted from {source_file.name} for V2 compliance.

Author: Agent-1 - Testing & Quality Assurance Specialist
"""

{chr(10).join(extracted_code)}
'''

            return ToolResult(
                success=True,
                output={
                    "source_file": str(source_file),
                    "target_module": str(target_module),
                    "items_extracted": len(extracted_code),
                    "module_content": module_content,
                    "preview": module_content[:500] + "...",
                },
                exit_code=0,
            )

        except Exception as e:
            logger.error(f"Error extracting module: {e}")
            raise ToolExecutionError(str(e), tool_name="refactor.extract_module")


class QuickLineCountTool(IToolAdapter):
    """Quick line count for V2 compliance checking."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="refactor.quick_line_count",
            version="1.0.0",
            category="refactoring",
            summary="Quick line count for files",
            required_params=["path"],
            optional_params={"threshold": 400, "show_violations_only": True},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute quick line count."""
        try:
            path = Path(params["path"])
            threshold = params.get("threshold", 400)
            show_violations_only = params.get("show_violations_only", True)

            results = []

            if path.is_file():
                files = [path]
            else:
                files = list(path.rglob("*.py"))

            for file in files:
                line_count = len(file.read_text(encoding="utf-8").splitlines())

                if show_violations_only:
                    if line_count > threshold:
                        results.append(
                            {
                                "file": str(file),
                                "lines": line_count,
                                "status": "VIOLATION",
                                "excess": line_count - threshold,
                            }
                        )
                else:
                    results.append(
                        {
                            "file": str(file),
                            "lines": line_count,
                            "status": "OK" if line_count <= threshold else "VIOLATION",
                            "excess": max(0, line_count - threshold),
                        }
                    )

            violations = [r for r in results if r["status"] == "VIOLATION"]

            return ToolResult(
                success=True,
                output={
                    "total_files": len(files),
                    "violations": len(violations),
                    "threshold": threshold,
                    "results": results,
                    "compliance_rate": (
                        (len(files) - len(violations)) / len(files) * 100
                    )
                    if len(files) > 0
                    else 100,
                },
                exit_code=0,
            )

        except Exception as e:
            logger.error(f"Error in quick line count: {e}")
            raise ToolExecutionError(str(e), tool_name="refactor.quick_line_count")


class PublicAPIImportValidatorTool(IToolAdapter):
    """Validate public API imports from modules (checks __all__ exports)."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="integration.validate_public_api",
            version="1.0.0",
            category="integration",
            summary="Validate public API imports from modules (checks __all__ exports)",
            required_params=[],
            optional_params={"module": None, "directory": None},
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        # Either module or directory must be provided
        if not params.get("module") and not params.get("directory"):
            return False, ["Either 'module' or 'directory' must be provided"]
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute public API import validation."""
        try:
            import sys
            from pathlib import Path

            # Add tools to path
            tools_path = Path(__file__).parent.parent.parent / "tools"
            sys.path.insert(0, str(tools_path))

            # Import validate_imports functions
            from validate_imports import validate_module_imports, validate_directory

            results = {
                "modules_tested": [],
                "modules_passed": [],
                "modules_failed": [],
                "total": 0,
                "passed": 0,
                "failed": 0,
            }

            all_success = True

            # Validate individual modules
            if params.get("module"):
                modules = params["module"] if isinstance(params["module"], list) else [params["module"]]
                for module_path in modules:
                    success, errors = validate_module_imports(module_path)
                    results["modules_tested"].append(module_path)
                    results["total"] += 1
                    if success:
                        results["modules_passed"].append(module_path)
                        results["passed"] += 1
                    else:
                        results["modules_failed"].append({"module": module_path, "errors": errors})
                        results["failed"] += 1
                        all_success = False

            # Validate directory
            if params.get("directory"):
                success, total, failed = validate_directory(params["directory"])
                results["total"] += total
                results["passed"] += (total - failed)
                results["failed"] += failed
                if not success:
                    all_success = False

            return ToolResult(
                success=all_success,
                output=results,
                exit_code=0 if all_success else 1,
            )

        except Exception as e:
            logger.error(f"Error in public API validation: {e}")
            raise ToolExecutionError(str(e), tool_name="integration.validate_public_api")


class ImportChainValidatorTool(IToolAdapter):
    """Validate import chains and identify missing modules."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="integration.import_chain",
            version="1.0.0",
            category="integration",
            summary="Validate import chains and find missing modules",
            required_params=["file"],
            optional_params={"fix_suggestions": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute import chain validation."""
        try:
            import sys
            import importlib.util
            from pathlib import Path

            file_path = Path(params["file"])
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    output={"error": f"File not found: {file_path}"},
                    exit_code=1,
                )

            # Import the tool function
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
            from import_chain_validator import test_import, find_import_statements

            # Test import
            result = test_import(str(file_path))

            if result["success"]:
                return ToolResult(
                    success=True,
                    output={
                        "file": str(file_path),
                        "status": "all_imports_valid",
                        "missing_modules": [],
                    },
                    exit_code=0,
                )

            # Get imports
            imports = find_import_statements(file_path)

            output = {
                "file": str(file_path),
                "status": "import_errors_found",
                "error": result["error"],
                "missing_modules": result["missing_modules"],
                "imports_found": len(imports),
                "imports": imports[:10],  # First 10
            }

            if params.get("fix_suggestions") and result["missing_modules"]:
                suggestions = []
                for module in result["missing_modules"]:
                    suggestions.append(
                        {
                            "missing": module,
                            "suggestions": [
                                f"Check if module exists: find . -name '{module}.py'",
                                "Check __init__.py exports",
                                "Consider creating the module if needed",
                                "Update imports to use correct path",
                            ],
                        }
                    )
                output["fix_suggestions"] = suggestions

            return ToolResult(
                success=False,
                output=output,
                exit_code=1,
            )

        except Exception as e:
            logger.error(f"Error validating import chain: {e}")
            raise ToolExecutionError(str(e), tool_name="integration.import_chain")