"""
File Deletion Support Tool - V2 Compliant
==========================================

Infrastructure support for safe file deletion process.
Provides pre-deletion health checks, post-deletion verification,
and system health monitoring.

V2 Compliance: ≤400 lines, comprehensive error handling, type hints.

Author: Agent-3 (Infrastructure & DevOps Specialist)
License: MIT
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileDeletionSupport:
    """Infrastructure support for safe file deletion operations."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize file deletion support."""
        self.project_root = project_root or Path(__file__).parent.parent
        self.reports_dir = self.project_root / "agent_workspaces" / "Agent-3" / "deletion_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def pre_deletion_health_check(self) -> Dict[str, Any]:
        """
        Run comprehensive health check before file deletions.
        
        Returns:
            Dictionary with health check results
        """
        logger.info("Running pre-deletion health check...")
        
        health_status = {
            "timestamp": self._get_timestamp(),
            "status": "healthy",
            "checks": {},
            "warnings": [],
            "errors": [],
        }

        # Check critical directories
        critical_dirs = ["src", "tests", "tools", "agent_workspaces", ".github"]
        for dir_name in critical_dirs:
            dir_path = self.project_root / dir_name
            exists = dir_path.exists()
            health_status["checks"][f"directory_{dir_name}"] = {
                "exists": exists,
                "path": str(dir_path),
            }
            if not exists:
                health_status["errors"].append(f"Critical directory missing: {dir_name}")
                health_status["status"] = "unhealthy"

        # Check Python imports
        import_check = self._check_python_imports()
        health_status["checks"]["python_imports"] = import_check
        if not import_check["all_valid"]:
            health_status["warnings"].extend(import_check["errors"])

        # Check test suite
        test_check = self._check_test_suite()
        health_status["checks"]["test_suite"] = test_check

        # Check CI/CD workflows
        cicd_check = self._check_cicd_workflows()
        health_status["checks"]["cicd_workflows"] = cicd_check

        # Determine overall status
        if health_status["errors"]:
            health_status["status"] = "unhealthy"
        elif health_status["warnings"]:
            health_status["status"] = "warning"

        return health_status

    def post_deletion_verification(
        self, deleted_files: List[str], pre_deletion_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify system health after file deletions.
        
        Args:
            deleted_files: List of file paths that were deleted
            pre_deletion_state: Health check state from before deletion
            
        Returns:
            Dictionary with verification results
        """
        logger.info(f"Running post-deletion verification for {len(deleted_files)} files...")
        
        verification = {
            "timestamp": self._get_timestamp(),
            "deleted_files": deleted_files,
            "status": "healthy",
            "checks": {},
            "issues": [],
            "recommendations": [],
        }

        # Re-run health checks
        current_health = self.pre_deletion_health_check()
        verification["current_health"] = current_health

        # Compare with pre-deletion state
        verification["comparison"] = self._compare_health_states(
            pre_deletion_state, current_health
        )

        # Check for broken imports
        import_check = self._check_python_imports()
        verification["checks"]["imports_after_deletion"] = import_check
        if not import_check["all_valid"]:
            verification["issues"].extend(import_check["errors"])
            verification["status"] = "unhealthy"

        # Run test suite
        test_results = self._run_test_suite()
        verification["checks"]["test_results"] = test_results
        if test_results.get("failures", 0) > 0:
            verification["issues"].append(
                f"Test failures detected: {test_results['failures']}"
            )
            verification["status"] = "unhealthy"

        # Check for missing dependencies
        missing_deps = self._check_missing_dependencies(deleted_files)
        if missing_deps:
            verification["issues"].extend(missing_deps)
            verification["status"] = "unhealthy"

        # Generate recommendations
        if verification["issues"]:
            verification["recommendations"].append(
                "Review deleted files - some may need to be restored"
            )
            verification["recommendations"].append(
                "Check import errors and fix broken dependencies"
            )

        return verification

    def monitor_system_health(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """
        Monitor system health over time after deletions.
        
        Args:
            duration_minutes: How long to monitor
            
        Returns:
            Dictionary with monitoring results
        """
        logger.info(f"Monitoring system health for {duration_minutes} minutes...")
        
        monitoring = {
            "start_time": self._get_timestamp(),
            "duration_minutes": duration_minutes,
            "checks": [],
            "status": "healthy",
        }

        # Run periodic health checks
        import time
        check_interval = 60  # 1 minute intervals
        num_checks = max(1, (duration_minutes * 60) // check_interval)

        for i in range(num_checks):
            check_result = self.pre_deletion_health_check()
            check_result["check_number"] = i + 1
            monitoring["checks"].append(check_result)

            if check_result["status"] != "healthy":
                monitoring["status"] = "unhealthy"
                break

            if i < num_checks - 1:
                time.sleep(check_interval)

        monitoring["end_time"] = self._get_timestamp()
        return monitoring

    def _check_python_imports(self) -> Dict[str, Any]:
        """Check if critical Python imports work."""
        result = {
            "all_valid": True,
            "errors": [],
            "modules_checked": [],
        }

        critical_modules = [
            "src.core.messaging_core",
            "src.core.config_ssot",
            "src.workflows.engine",
        ]

        for module_name in critical_modules:
            try:
                __import__(module_name)
                result["modules_checked"].append(module_name)
            except ImportError as e:
                result["all_valid"] = False
                result["errors"].append(f"{module_name}: {str(e)}")

        return result

    def _check_test_suite(self) -> Dict[str, Any]:
        """Check if test suite is accessible."""
        tests_dir = self.project_root / "tests"
        return {
            "exists": tests_dir.exists(),
            "path": str(tests_dir),
            "accessible": tests_dir.exists() and tests_dir.is_dir(),
        }

    def _check_cicd_workflows(self) -> Dict[str, Any]:
        """Check CI/CD workflow files."""
        workflows_dir = self.project_root / ".github" / "workflows"
        workflows = []
        
        if workflows_dir.exists():
            workflows = [f.name for f in workflows_dir.glob("*.yml")]

        return {
            "exists": workflows_dir.exists(),
            "workflow_count": len(workflows),
            "workflows": workflows,
        }

    def _run_test_suite(self) -> Dict[str, Any]:
        """Run test suite and return results."""
        result = {
            "success": False,
            "tests_run": 0,
            "failures": 0,
            "errors": 0,
        }

        try:
            # Run pytest with minimal output
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "-q",
                "--tb=short",
                "--maxfail=5",  # Stop after 5 failures
            ]

            process = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_EXTENDED,  # 5 minute timeout
            )

            result["success"] = process.returncode == 0
            result["returncode"] = process.returncode
            result["stdout"] = process.stdout[:1000]  # Limit output
            result["stderr"] = process.stderr[:1000] if process.stderr else ""

            # Parse pytest output for counts (simplified)
            if "failed" in process.stdout:
                result["failures"] = 1  # Simplified - would parse actual count

        except subprocess.TimeoutExpired:
            result["errors"].append("Test suite timeout")
        except Exception as e:
            result["errors"].append(f"Test execution error: {str(e)}")

        return result

    def _check_missing_dependencies(self, deleted_files: List[str]) -> List[str]:
        """Check if deleted files break any dependencies."""
        issues = []

        # Check if any deleted files are imported elsewhere
        for file_path in deleted_files:
            # Simplified check - would do actual import analysis
            if "core" in file_path or "services" in file_path:
                issues.append(
                    f"Deleted file may be imported: {file_path}"
                )

        return issues

    def _compare_health_states(
        self, before: Dict[str, Any], after: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare health states before and after deletion."""
        comparison = {
            "status_changed": before.get("status") != after.get("status"),
            "new_errors": [],
            "new_warnings": [],
            "resolved_issues": [],
        }

        before_errors = set(before.get("errors", []))
        after_errors = set(after.get("errors", []))
        comparison["new_errors"] = list(after_errors - before_errors)
        comparison["resolved_issues"] = list(before_errors - after_errors)

        return comparison

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def save_report(self, report: Dict[str, Any], report_type: str) -> Path:
        """
        Save health check or verification report.
        
        Args:
            report: Report data
            report_type: Type of report (health_check, verification, monitoring)
            
        Returns:
            Path to saved report file
        """
        timestamp = report.get("timestamp", self._get_timestamp()).replace(":", "-")
        report_file = self.reports_dir / f"{report_type}_{timestamp}.json"
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Report saved: {report_file}")
        return report_file


def main():
    """CLI entry point."""
    import argparse
from src.core.config.timeout_constants import TimeoutConstants

    parser = argparse.ArgumentParser(description="File Deletion Support Tool")
    parser.add_argument(
        "--pre-deletion",
        action="store_true",
        help="Run pre-deletion health check",
    )
    parser.add_argument(
        "--post-deletion",
        nargs="+",
        metavar="FILE",
        help="Run post-deletion verification for deleted files",
    )
    parser.add_argument(
        "--monitor",
        type=int,
        metavar="MINUTES",
        help="Monitor system health for specified minutes",
    )
    parser.add_argument(
        "--pre-state-file",
        type=str,
        help="Path to pre-deletion state JSON file",
    )

    args = parser.parse_args()

    support = FileDeletionSupport()

    if args.pre_deletion:
        health = support.pre_deletion_health_check()
        report_file = support.save_report(health, "pre_deletion_health")
        print(f"✅ Pre-deletion health check complete: {report_file}")
        print(f"Status: {health['status'].upper()}")
        if health.get("errors"):
            print(f"Errors: {len(health['errors'])}")
        if health.get("warnings"):
            print(f"Warnings: {len(health['warnings'])}")

    elif args.post_deletion:
        pre_state = {}
        if args.pre_state_file:
            with open(args.pre_state_file) as f:
                pre_state = json.load(f)

        verification = support.post_deletion_verification(
            args.post_deletion, pre_state
        )
        report_file = support.save_report(verification, "post_deletion_verification")
        print(f"✅ Post-deletion verification complete: {report_file}")
        print(f"Status: {verification['status'].upper()}")
        if verification.get("issues"):
            print(f"Issues: {len(verification['issues'])}")

    elif args.monitor:
        monitoring = support.monitor_system_health(args.monitor)
        report_file = support.save_report(monitoring, "health_monitoring")
        print(f"✅ Health monitoring complete: {report_file}")
        print(f"Status: {monitoring['status'].upper()}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

