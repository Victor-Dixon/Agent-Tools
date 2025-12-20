#!/usr/bin/env python3
"""
System Validation Tools
=======================

Tools for smoke tests, validation, and system checks.

Author: Agent-7 - Repository Cloning Specialist
Created: 2025-10-13
"""

import logging
import subprocess
import sys
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec

logger = logging.getLogger(__name__)


class SmokeTestTool(IToolAdapter):
    """Run smoke tests."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="val.smoke",
            version="1.0.0",
            category="validation",
            summary="Run smoke tests for system validation",
            required_params=[],
            optional_params={"system": "all"}
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute smoke tests."""
        try:
            system = params.get("system", "all")

            if system == "all":
                test_files = [
                    "tests/test_msg_task_smoke.py",
                    "tests/test_oss_cli_smoke.py",
                    "tests/test_messaging_smoke.py",
                    "tests/test_error_handling_smoke.py",
                ]
            else:
                test_map = {
                    "msg_task": "tests/test_msg_task_smoke.py",
                    "oss": "tests/test_oss_cli_smoke.py",
                    "messaging": "tests/test_messaging_smoke.py",
                    "errors": "tests/test_error_handling_smoke.py",
                }
                test_files = [test_map.get(system, "")]

            results = []
            for test_file in test_files:
                if test_file:
                    result = subprocess.run(
                        [sys.executable, "-m", "pytest", test_file, "-v", "-m", "smoke"],
                        capture_output=True,
                        text=True,
                    )
                    results.append(
                        {
                            "file": test_file,
                            "passed": result.returncode == 0,
                            "output": result.stdout[-500:] if result.stdout else "",
                        }
                    )

            passing = sum(1 for r in results if r["passed"])
            total = len(results)

            return ToolResult(
                success=True,
                output={
                    "results": results,
                    "passed": passing,
                    "total": total,
                    "all_passed": passing == total,
                },
                exit_code=0
            )

        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class FeatureFlagTool(IToolAdapter):
    """Check or set feature flags."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="val.flags",
            version="1.0.0",
            category="validation",
            summary="Check or set feature flags",
            required_params=[],
            optional_params={"action": "check", "feature": None}
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute feature flag operations."""
        try:
            from src.features.flags import FF_MSG_TASK, FF_OSS_CLI, is_enabled

            action = params.get("action", "check")
            feature = params.get("feature")

            if action == "check":
                if feature:
                    return ToolResult(success=True, output={"feature": feature, "enabled": is_enabled(feature)}, exit_code=0)
                else:
                    return ToolResult(
                        success=True,
                        output={"flags": {"msg_task": FF_MSG_TASK, "oss_cli": FF_OSS_CLI}},
                        exit_code=0
                    )

            return ToolResult(success=False, output=None, exit_code=1, error_message="Only 'check' action supported via tool")

        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class RollbackTool(IToolAdapter):
    """Emergency rollback features."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="val.rollback",
            version="1.0.0",
            category="validation",
            summary="Emergency rollback features",
            required_params=[],
            optional_params={"feature": None}
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute rollback."""
        try:
            from src.features.flags import disable_feature

            feature = params.get("feature")
            if not feature:
                # Disable all
                for feat in ["msg_task", "oss_cli"]:
                    disable_feature(feat)
                return ToolResult(success=True, output={"message": "All features disabled"}, exit_code=0)
            else:
                disable_feature(feature)
                return ToolResult(success=True, output={"message": f"Feature disabled: {feature}"}, exit_code=0)

        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class ValidationReportTool(IToolAdapter):
    """Generate validation report for all systems."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="val.report",
            version="1.0.0",
            category="validation",
            summary="Generate validation report for all systems",
            required_params=[],
            optional_params={}
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute validation report."""
        try:
            from src.obs.metrics import snapshot

            metrics = snapshot()

            # Calculate success rates
            ingest_ok = metrics.get("msg_task.ingest.ok", 0)
            ingest_fail = metrics.get("msg_task.ingest.fail", 0)
            ingest_total = ingest_ok + ingest_fail

            report = {
                "timestamp": str(__import__("datetime").datetime.now()),
                "systems": {
                    "msg_task": {
                        "operational": True,
                        "success_rate": (
                            (ingest_ok / ingest_total * 100) if ingest_total > 0 else 100
                        ),
                        "slo_target": 99.0,
                    },
                    "oss": {
                        "operational": True,
                        "clones_ok": metrics.get("oss.clone.ok", 0),
                        "clones_fail": metrics.get("oss.clone.fail", 0),
                    },
                    "messaging": {
                        "operational": True,
                        "sent": metrics.get("messaging.sent", 0),
                        "failed": metrics.get("messaging.failed", 0),
                    },
                },
                "metrics": metrics,
            }

            return ToolResult(success=True, output={"report": report}, exit_code=0)

        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class IntegrityValidatorTool(IToolAdapter):
    """Validate agent task claims against evidence (git, files, status)."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="validation.integrity",
            version="1.0.0",
            category="validation",
            summary="Validate agent task claims against evidence",
            required_params=["agent", "task_id", "claimed_work", "files_claimed"],
            optional_params={"hours_ago": 24, "repo_path": "."}
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute integrity validation."""
        try:
            import sys
            from pathlib import Path

            # Add tools to path
            tools_path = Path(__file__).parent.parent.parent / "tools"
            sys.path.insert(0, str(tools_path))

            # Import integrity validator
            from integrity_validator import IntegrityValidator

            # Initialize validator
            repo_path = params.get("repo_path", ".")
            validator = IntegrityValidator(repo_path=repo_path)

            # Validate task completion
            result = validator.validate_task_completion(
                agent=params["agent"],
                task_id=params["task_id"],
                claimed_work=params["claimed_work"],
                files_claimed=params["files_claimed"],
                hours_ago=params.get("hours_ago", 24)
            )

            # Convert to dict
            from dataclasses import asdict
            result_dict = asdict(result)

            return ToolResult(
                success=result.validated,
                output={
                    "validation": result_dict,
                    "recommendation": result.recommendation,
                    "confidence": result.confidence,
                },
                exit_code=0 if result.validated else 1,
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                exit_code=1,
                error_message=str(e)
            )


class SSOTValidatorTool(IToolAdapter):
    """Validate SSOT (Single Source of Truth) - Check documentation-code alignment."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="validation.ssot",
            version="1.0.0",
            category="validation",
            summary="Validate SSOT - Check documentation-code alignment",
            required_params=["code", "docs"],
            optional_params={"verbose": False}
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute SSOT validation."""
        try:
            import sys
            from pathlib import Path

            # Add tools to path
            tools_path = Path(__file__).parent.parent.parent / "tools"
            sys.path.insert(0, str(tools_path))

            # Import SSOT validator
            from ssot_validator import validate_ssot

            # Get parameters
            code_file = params["code"]
            doc_files = params["docs"] if isinstance(params["docs"], list) else [params["docs"]]
            verbose = params.get("verbose", False)

            # Validate SSOT
            results = validate_ssot(code_file, doc_files)

            # Convert sets to lists for JSON serialization
            output = {
                "code_file": code_file,
                "doc_files": doc_files,
                "code_flags": list(results["code_flags"]),
                "doc_flags": list(results["doc_flags"]),
                "aligned": list(results["aligned"]),
                "undocumented": list(results["undocumented"]),
                "nonexistent": list(results["nonexistent"]),
                "alignment_percentage": (
                    len(results["aligned"]) / max(len(results["code_flags"]), len(results["doc_flags"])) * 100
                    if max(len(results["code_flags"]), len(results["doc_flags"])) > 0
                    else 100
                ),
                "ssot_violation": len(results["nonexistent"]) > 0,
                "status": "violation" if results["nonexistent"] else ("incomplete" if results["undocumented"] else "aligned")
            }

            return ToolResult(
                success=len(results["nonexistent"]) == 0,
                output=output,
                exit_code=1 if results["nonexistent"] else 0,
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                exit_code=1,
                error_message=str(e)
            )