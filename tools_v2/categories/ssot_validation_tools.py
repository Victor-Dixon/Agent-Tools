"""
SSOT Validation Tools - Single Source of Truth Enforcement
==========================================================

Tools for validating and enforcing SSOT compliance across the codebase.
Detects violations, duplicates, and ensures single source of truth.

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-01-27
V2 Compliance: <400 lines
"""

import ast
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class SSOTViolationDetector(IToolAdapter):
    """Detect SSOT violations in codebase."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="ssot.detect_violations",
            version="1.0.0",
            category="ssot",
            summary="Detect Single Source of Truth violations in codebase",
            required_params=[],
            optional_params={
                "directory": "src",
                "patterns": None,  # JSON string of patterns to check
            },
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute SSOT violation detection."""
        try:
            directory = params.get("directory", "src")
            patterns_json = params.get("patterns")
            patterns = json.loads(patterns_json) if patterns_json else None

            violations = self._detect_violations(Path(directory), patterns)

            return ToolResult(
                success=True,
                output={
                    "violations": violations,
                    "count": len(violations),
                    "summary": self._generate_summary(violations),
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error detecting SSOT violations: {e}")
            raise ToolExecutionError(str(e), tool_name="ssot.detect_violations")

    def _detect_violations(self, directory: Path, patterns: Optional[List[str]]) -> List[Dict[str, Any]]:
        """Detect SSOT violations in directory."""
        violations = []

        # Default patterns to check
        default_patterns = [
            "duplicate_class",
            "duplicate_function",
            "multiple_repositories",
            "scattered_config",
            "duplicate_constants",
        ]

        check_patterns = patterns or default_patterns

        if "duplicate_class" in check_patterns:
            violations.extend(self._find_duplicate_classes(directory))

        if "duplicate_function" in check_patterns:
            violations.extend(self._find_duplicate_functions(directory))

        if "multiple_repositories" in check_patterns:
            violations.extend(self._find_multiple_repositories(directory))

        if "scattered_config" in check_patterns:
            violations.extend(self._find_scattered_config(directory))

        if "duplicate_constants" in check_patterns:
            violations.extend(self._find_duplicate_constants(directory))

        return violations

    def _find_duplicate_classes(self, directory: Path) -> List[Dict[str, Any]]:
        """Find duplicate class definitions."""
        class_names: Dict[str, List[str]] = {}
        violations = []

        for py_file in directory.rglob("*.py"):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"), str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        file_path = str(py_file.relative_to(directory))
                        if class_name not in class_names:
                            class_names[class_name] = []
                        class_names[class_name].append(file_path)
            except Exception:
                continue

        for class_name, files in class_names.items():
            if len(files) > 1:
                violations.append({
                    "type": "duplicate_class",
                    "name": class_name,
                    "files": files,
                    "severity": "high",
                })

        return violations

    def _find_duplicate_functions(self, directory: Path) -> List[Dict[str, Any]]:
        """Find duplicate function definitions."""
        function_signatures: Dict[str, List[str]] = {}
        violations = []

        for py_file in directory.rglob("*.py"):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"), str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_name = node.name
                        # Create signature
                        args = [arg.arg for arg in node.args.args]
                        signature = f"{func_name}({', '.join(args)})"
                        file_path = str(py_file.relative_to(directory))
                        if signature not in function_signatures:
                            function_signatures[signature] = []
                        function_signatures[signature].append(file_path)
            except Exception:
                continue

        for signature, files in function_signatures.items():
            if len(files) > 1:
                violations.append({
                    "type": "duplicate_function",
                    "signature": signature,
                    "files": files,
                    "severity": "medium",
                })

        return violations

    def _find_multiple_repositories(self, directory: Path) -> List[Dict[str, Any]]:
        """Find multiple repository implementations for same entity."""
        repositories: Dict[str, List[str]] = {}
        violations = []

        for py_file in directory.rglob("*repository*.py"):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"), str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if "Repository" in node.name:
                            entity = node.name.replace("Repository", "").lower()
                            file_path = str(py_file.relative_to(directory))
                            if entity not in repositories:
                                repositories[entity] = []
                            repositories[entity].append(file_path)
            except Exception:
                continue

        for entity, files in repositories.items():
            if len(files) > 1:
                violations.append({
                    "type": "multiple_repositories",
                    "entity": entity,
                    "files": files,
                    "severity": "high",
                })

        return violations

    def _find_scattered_config(self, directory: Path) -> List[Dict[str, Any]]:
        """Find scattered configuration definitions."""
        config_files = []
        violations = []

        # Look for config files
        for config_file in directory.rglob("*config*.py"):
            config_files.append(str(config_file.relative_to(directory)))

        for config_file in directory.rglob("*settings*.py"):
            config_files.append(str(config_file.relative_to(directory)))

        if len(config_files) > 3:  # More than 3 config files suggests scattering
            violations.append({
                "type": "scattered_config",
                "files": config_files,
                "severity": "medium",
                "message": f"Found {len(config_files)} config files - consider consolidation",
            })

        return violations

    def _find_duplicate_constants(self, directory: Path) -> List[Dict[str, Any]]:
        """Find duplicate constant definitions."""
        constants: Dict[str, List[str]] = {}
        violations = []

        for py_file in directory.rglob("*.py"):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"), str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                name = target.name
                                if name.isupper() and "_" in name:  # Likely a constant
                                    file_path = str(py_file.relative_to(directory))
                                    if name not in constants:
                                        constants[name] = []
                                    if file_path not in constants[name]:
                                        constants[name].append(file_path)
            except Exception:
                continue

        for const_name, files in constants.items():
            if len(files) > 1:
                violations.append({
                    "type": "duplicate_constants",
                    "name": const_name,
                    "files": files,
                    "severity": "low",
                })

        return violations

    def _generate_summary(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of violations."""
        by_type = {}
        by_severity = {"high": 0, "medium": 0, "low": 0}

        for violation in violations:
            vtype = violation["type"]
            severity = violation["severity"]
            if vtype not in by_type:
                by_type[vtype] = 0
            by_type[vtype] += 1
            by_severity[severity] += 1

        return {
            "total": len(violations),
            "by_type": by_type,
            "by_severity": by_severity,
        }


class SSOTPatternValidator(IToolAdapter):
    """Validate SSOT patterns in code."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="ssot.validate_patterns",
            version="1.0.0",
            category="ssot",
            summary="Validate SSOT patterns in codebase",
            required_params=["file_path"],
            optional_params={"pattern_type": "repository"},
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        """Validate parameters."""
        if not params.get("file_path"):
            return False, ["file_path is required"]
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute SSOT pattern validation."""
        try:
            file_path = Path(params["file_path"])
            pattern_type = params.get("pattern_type", "repository")

            if not file_path.exists():
                return ToolResult(
                    success=False,
                    output={"error": f"File not found: {file_path}"},
                    exit_code=1,
                )

            validation_result = self._validate_pattern(file_path, pattern_type)

            return ToolResult(
                success=validation_result["valid"],
                output=validation_result,
                exit_code=0 if validation_result["valid"] else 1,
            )
        except Exception as e:
            logger.error(f"Error validating SSOT pattern: {e}")
            raise ToolExecutionError(str(e), tool_name="ssot.validate_patterns")

    def _validate_pattern(self, file_path: Path, pattern_type: str) -> Dict[str, Any]:
        """Validate SSOT pattern in file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, str(file_path))

            if pattern_type == "repository":
                return self._validate_repository_pattern(tree, file_path)
            elif pattern_type == "service":
                return self._validate_service_pattern(tree, file_path)
            elif pattern_type == "config":
                return self._validate_config_pattern(tree, file_path)
            else:
                return {
                    "valid": False,
                    "error": f"Unknown pattern type: {pattern_type}",
                }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
            }

    def _validate_repository_pattern(self, tree: ast.AST, file_path: Path) -> Dict[str, Any]:
        """Validate repository pattern (data access only, no business logic)."""
        issues = []
        has_repository_class = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if "Repository" in node.name:
                    has_repository_class = True
                    # Check for business logic (should only have data access)
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Check for business logic patterns
                            if any(
                                keyword in item.name.lower()
                                for keyword in ["process", "calculate", "validate", "transform"]
                            ):
                                issues.append(f"Repository method '{item.name}' may contain business logic")

        if not has_repository_class:
            return {
                "valid": False,
                "error": "No Repository class found",
            }

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "pattern": "repository",
        }

    def _validate_service_pattern(self, tree: ast.AST, file_path: Path) -> Dict[str, Any]:
        """Validate service pattern (business logic, uses repositories)."""
        issues = []
        has_service_class = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if "Service" in node.name:
                    has_service_class = True
                    # Check for direct file I/O (should use repositories)
                    content = ast.unparse(node) if hasattr(ast, "unparse") else str(node)
                    if "open(" in content or "Path(" in content:
                        issues.append("Service contains direct file I/O - should use repositories")

        if not has_service_class:
            return {
                "valid": False,
                "error": "No Service class found",
            }

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "pattern": "service",
        }

    def _validate_config_pattern(self, tree: ast.AST, file_path: Path) -> Dict[str, Any]:
        """Validate config pattern (single source of truth)."""
        issues = []
        config_classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if "Config" in node.name or "Settings" in node.name:
                    config_classes.append(node.name)

        if len(config_classes) > 1:
            issues.append(f"Multiple config classes found: {config_classes}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "pattern": "config",
        }


__all__ = ["SSOTViolationDetector", "SSOTPatternValidator"]




