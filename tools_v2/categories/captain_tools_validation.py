#!/usr/bin/env python3
"""
Captain Validation Tools - Agent Toolbelt V2
============================================

Validation and detection tools for captain operations.

V2 Compliance: <400 lines
Author: Agent-2 (Architecture & Design) - Split from captain_tools_advanced.py
Date: 2025-01-27
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class FileExistenceValidator(IToolAdapter):
    """Validate file existence before task assignment (prevents phantom tasks)."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.validate_file_exists",
            version="1.0.0",
            category="captain",
            summary="Verify file exists before assigning as task (prevents phantom tasks)",
            required_params=["file_path"],
            optional_params={"check_size": True},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute file existence validation."""
        try:
            file_path = params["file_path"]
            check_size = params.get("check_size", True)

            file = Path(file_path)
            exists = file.exists()

            validation = {
                "file_path": file_path,
                "exists": exists,
                "is_phantom": not exists,
                "verdict": "VALID" if exists else "PHANTOM_TASK",
            }

            if exists and check_size:
                validation["size"] = file.stat().st_size
                validation["lines"] = len(
                    file.read_text(encoding="utf-8", errors="ignore").splitlines()
                )

            return ToolResult(success=True, output=validation, exit_code=0 if exists else 1)
        except Exception as e:
            logger.error(f"Error validating file existence: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.validate_file_exists")


class ProjectScanRunner(IToolAdapter):
    """Run fresh project scan to update violation data."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.run_project_scan",
            version="1.0.0",
            category="captain",
            summary="Run fresh project scan to update violations and eliminate phantom files",
            required_params=[],
            optional_params={"generate_reports": True},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute project scan."""
        try:
            # Run project scanner
            result = subprocess.run(
                ["python", "tools/run_project_scan.py"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            scan_output = {
                "scan_completed": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            # Check if project_analysis.json was updated
            analysis_file = Path("project_analysis.json")
            if analysis_file.exists():
                scan_output["analysis_updated"] = True
                scan_output["analysis_file"] = str(analysis_file)

                # Count violations
                with open(analysis_file) as f:
                    data = json.load(f)
                    scan_output["total_files"] = len(data)

            return ToolResult(
                success=result.returncode == 0, output=scan_output, exit_code=result.returncode
            )
        except Exception as e:
            logger.error(f"Error running project scan: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.run_project_scan")


class PhantomTaskDetector(IToolAdapter):
    """Detect phantom tasks (files in task pool that don't exist)."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.detect_phantoms",
            version="1.0.0",
            category="captain",
            summary="Detect phantom tasks in project_analysis.json",
            required_params=[],
            optional_params={"analysis_file": "project_analysis.json"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute phantom detection."""
        try:
            analysis_file = Path(params.get("analysis_file", "project_analysis.json"))

            if not analysis_file.exists():
                return ToolResult(
                    success=False,
                    output={"error": "project_analysis.json not found"},
                    exit_code=1,
                    error_message="Analysis file does not exist",
                )

            with open(analysis_file) as f:
                data = json.load(f)

            phantom_tasks = []
            valid_tasks = []

            for file_path in data.keys():
                file = Path(file_path)
                if file.exists():
                    valid_tasks.append(file_path)
                else:
                    phantom_tasks.append(file_path)

            return ToolResult(
                success=True,
                output={
                    "total_files_in_analysis": len(data),
                    "valid_files": len(valid_tasks),
                    "phantom_files": len(phantom_tasks),
                    "phantom_list": phantom_tasks[:10],  # First 10 only
                    "phantom_percentage": (
                        round((len(phantom_tasks) / len(data)) * 100, 2) if data else 0
                    ),
                    "recommendation": (
                        "Run fresh project scan" if phantom_tasks else "Task pool is clean"
                    ),
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error detecting phantoms: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.detect_phantoms")


__all__ = [
    "FileExistenceValidator",
    "ProjectScanRunner",
    "PhantomTaskDetector",
]




