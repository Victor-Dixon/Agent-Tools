#!/usr/bin/env python3
"""
Functionality Tests
===================

Agent-specific functionality verification tests.

Author: Agent-1 (Integration & Core Systems Specialist)
V2 Compliant: <300 lines
"""

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


class FunctionalityTests:
    """Run agent-specific functionality tests."""

    def __init__(self):
        """Initialize test runner."""
        self.project_root = Path(__file__).parent.parent

    def run_agent_tests(self, agent_id: str) -> Dict[str, Any]:
        """Run agent-specific verification tests."""
        tests_run = []
        tests_passed = []
        tests_failed = []

        # Basic agent workspace check
        workspace_path = self.project_root / "agent_workspaces" / agent_id
        if workspace_path.exists():
            tests_run.append("workspace_exists")
            tests_passed.append("workspace_exists")
        else:
            tests_run.append("workspace_exists")
            tests_failed.append({
                "test": "workspace_exists",
                "error": f"Workspace not found: {workspace_path}",
            })

        # Check for key agent files
        key_files = [
            "__init__.py",
            "status.json",
        ]

        for key_file in key_files:
            test_name = f"has_{key_file}"
            tests_run.append(test_name)
            file_path = workspace_path / key_file
            if file_path.exists():
                tests_passed.append(test_name)
            else:
                tests_failed.append({
                    "test": test_name,
                    "error": f"File not found: {file_path}",
                })

        # Determine functionality status
        if len(tests_failed) == 0:
            functionality_status = "FULLY_FUNCTIONAL"
        elif len(tests_failed) <= 1:
            functionality_status = "MINOR_ISSUES"
        else:
            functionality_status = "SIGNIFICANT_ISSUES"

        if len(tests_run) == 0:
            functionality_status = "NO_TESTS"

        return {
            "agent_id": agent_id,
            "functionality_status": functionality_status,
            "tests_run": tests_run,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
        }

