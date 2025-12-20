#!/usr/bin/env python3
"""
Memory Safety Tool Adapters - Toolbelt V2
=========================================

IToolAdapter wrappers for memory safety functions.

Author: Agent-5 (Business Intelligence & Team Beta Leader)
License: MIT
"""

import logging
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError
from .memory_safety_tools import (
    check_file_handles,
    detect_memory_leaks,
    scan_unbounded_structures,
    validate_imports,
    verify_files_exist,
)

logger = logging.getLogger(__name__)


class MemoryLeakDetectorTool(IToolAdapter):
    """Detect potential memory leaks in codebase."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="mem.leaks",
            version="1.0.0",
            category="memory_safety",
            summary="Detect potential memory leaks (unbounded structures, missing size checks)",
            required_params=[],
            optional_params={"target_path": "src"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        try:
            target = params.get("target_path", "src")
            result = detect_memory_leaks(target)

            return ToolResult(
                success="error" not in result,
                output=result,
                exit_code=0 if "error" not in result else 1,
            )
        except Exception as e:
            logger.error(f"Memory leak detection failed: {e}")
            raise ToolExecutionError(str(e), tool_name="mem.leaks")


class FileVerificationTool(IToolAdapter):
    """Verify files exist before task assignment."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="mem.verify",
            version="1.0.0",
            category="memory_safety",
            summary="Verify files exist (prevent phantom tasks)",
            required_params=["file_list"],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        if "file_list" not in params:
            return (False, ["Missing required parameter: file_list"])
        if not isinstance(params["file_list"], list):
            return (False, ["file_list must be a list of file paths"])
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        try:
            file_list = params["file_list"]
            result = verify_files_exist(file_list)

            all_exist = len(result["missing"]) == 0

            return ToolResult(success=all_exist, output=result, exit_code=0 if all_exist else 1)
        except Exception as e:
            logger.error(f"File verification failed: {e}")
            raise ToolExecutionError(str(e), tool_name="mem.verify")


class UnboundedScanTool(IToolAdapter):
    """Scan for unbounded data structures."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="mem.scan",
            version="1.0.0",
            category="memory_safety",
            summary="Scan for unbounded data structures that could grow indefinitely",
            required_params=[],
            optional_params={"target_path": "src"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        try:
            target = params.get("target_path", "src")
            result = scan_unbounded_structures(target)

            return ToolResult(
                success="error" not in result,
                output=result,
                exit_code=0 if "error" not in result else 1,
            )
        except Exception as e:
            logger.error(f"Unbounded structure scan failed: {e}")
            raise ToolExecutionError(str(e), tool_name="mem.scan")


class MemorySafetyImportValidatorTool(IToolAdapter):
    """
    Validate Python file imports for memory safety.
    
    SSOT: This is the memory safety-specific import validator.
    For refactoring import validation, use refactor.validate_imports (import_fix_tools.py).
    """

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="mem.imports",
            version="1.0.0",
            category="memory_safety",
            summary="Validate Python file imports work correctly",
            required_params=["file_path"],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        if "file_path" not in params:
            return (False, ["Missing required parameter: file_path"])
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        try:
            file_path = params["file_path"]
            result = validate_imports(file_path)

            return ToolResult(
                success=result.get("success", False),
                output=result,
                exit_code=0 if result.get("success") else 1,
            )
        except Exception as e:
            logger.error(f"Import validation failed: {e}")
            raise ToolExecutionError(str(e), tool_name="mem.imports")


class FileHandleCheckTool(IToolAdapter):
    """Check for unclosed file handles."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="mem.handles",
            version="1.0.0",
            category="memory_safety",
            summary="Check for unclosed file handles (resource leak detection)",
            required_params=[],
            optional_params={"target_path": "src"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        try:
            target = params.get("target_path", "src")
            result = check_file_handles(target)

            return ToolResult(
                success="error" not in result,
                output=result,
                exit_code=0 if "error" not in result else 1,
            )
        except Exception as e:
            logger.error(f"File handle check failed: {e}")
            raise ToolExecutionError(str(e), tool_name="mem.handles")


__all__ = [
    "MemoryLeakDetectorTool",
    "FileVerificationTool",
    "UnboundedScanTool",
    "MemorySafetyImportValidatorTool",  # Fixed: Use actual class name, not "ImportValidatorTool"
    "FileHandleCheckTool",
]
