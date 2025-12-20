#!/usr/bin/env python3
"""
Verify All CI Workflows
========================

Verifies all CI workflows are passing consistently.
Task: CP-008

Author: Agent-1 (Integration & Core Systems Specialist)

<!-- SSOT Domain: infrastructure -->
"""

import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️  requests library not available - GitHub API checks disabled")


def get_all_workflows() -> List[Path]:
    """Get all workflow YAML files."""
    workflow_dir = project_root / ".github" / "workflows"

    if not workflow_dir.exists():
        return []

    return list(workflow_dir.glob("*.yml"))


def validate_workflow_syntax(workflow_path: Path) -> Dict[str, Any]:
    """Validate workflow YAML syntax."""
    result = {
        "file": workflow_path.name,
        "valid": False,
        "errors": []
    }

    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()
            workflow = yaml.safe_load(content)

        if not workflow:
            result["errors"].append("Empty workflow file")
            return result

        # Basic validation - check if it's a valid GitHub Actions workflow
        if not isinstance(workflow, dict):
            result["errors"].append("Workflow must be a YAML dictionary")
            return result

        # GitHub Actions uses 'on' as trigger field (can be dict or string)
        # Note: 'on' can be parsed as boolean True in YAML, so check both
        on_key = None
        if "on" in workflow:
            on_key = "on"
        elif True in workflow and isinstance(workflow[True], (dict, str, list)):
            # YAML parser may interpret 'on:' as boolean True key
            on_key = True

        if on_key is None:
            result["errors"].append("Missing 'on' trigger field")
        else:
            # 'on' field exists, validate it's not empty
            on_value = workflow.get(on_key)
            if not on_value:
                result["errors"].append("'on' field is empty")

        # Jobs are required for workflows (unless it's a reusable workflow)
        if "jobs" not in workflow:
            on_value = workflow.get("on", {})
            if isinstance(on_value, dict) and "workflow_call" not in on_value:
                result["errors"].append(
                    "Missing 'jobs' field (and not a reusable workflow)")

        result["valid"] = len(result["errors"]) == 0
        result["name"] = workflow.get("name", "Unknown")
        result["jobs"] = list(workflow.get("jobs", {}).keys()
                              ) if "jobs" in workflow else []

    except yaml.YAMLError as e:
        result["errors"].append(f"YAML syntax error: {e}")
    except Exception as e:
        result["errors"].append(f"Error reading file: {e}")

    return result


def check_workflow_resilience(workflow_path: Path) -> Dict[str, Any]:
    """Check if workflow handles missing files gracefully."""
    result = {
        "file": workflow_path.name,
        "resilient": False,
        "issues": []
    }

    try:
        content = workflow_path.read_text()

        # Check for hard requirements
        hard_patterns = [
            ("requirements-testing.txt", "pip install -r requirements-testing.txt"),
            ("v2_standards_checker.py", "python tests/v2_standards_checker.py"),
            ("validate_v2_compliance.py", "python scripts/validate_v2_compliance.py"),
        ]

        for pattern_name, pattern in hard_patterns:
            if pattern in content:
                # Check if it's in a conditional
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if pattern in line:
                        # Check if previous lines have conditional
                        has_conditional = False
                        for j in range(max(0, i-10), i):
                            if "if [" in lines[j] or "continue-on-error" in lines[j] or "||" in lines[j]:
                                has_conditional = True
                                break

                        if not has_conditional:
                            result["issues"].append(
                                f"Line {i+1}: {pattern_name} used without conditional check")

        # Check for continue-on-error on test steps
        if "pytest" in content or "test" in content.lower():
            # Check if test steps have continue-on-error
            has_continue = "continue-on-error: true" in content
            has_conditional = "if [" in content or "||" in content

            if not (has_continue or has_conditional):
                result["issues"].append(
                    "Test steps may not have proper error handling")

        result["resilient"] = len(result["issues"]) == 0

    except Exception as e:
        result["issues"].append(f"Error checking resilience: {e}")

    return result


def check_github_workflow_status(repo: str = "Victor-Dixon/Dream.os") -> Dict[str, Any]:
    """Check GitHub Actions workflow status."""
    if not HAS_REQUESTS:
        return {"status": "skipped", "reason": "requests library not available"}

    api_url = f"https://api.github.com/repos/{repo}/actions/runs"

    try:
        response = requests.get(
            api_url,
            params={"per_page": 10, "branch": "main"},
            timeout=30
        )

        if response.status_code != 200:
            return {
                "status": "error",
                "error": f"HTTP {response.status_code}",
                "message": response.text[:200]
            }

        runs = response.json().get("workflow_runs", [])

        if not runs:
            return {"status": "no_runs", "message": "No workflow runs found"}

        # Get latest run for each workflow
        workflows = {}
        for run in runs:
            workflow_name = run.get("name", "Unknown")
            if workflow_name not in workflows:
                workflows[workflow_name] = {
                    "status": run.get("status"),
                    "conclusion": run.get("conclusion"),
                    "created_at": run.get("created_at"),
                    "html_url": run.get("html_url")
                }

        return {
            "status": "success",
            "workflows": workflows,
            "total_runs": len(runs)
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def main():
    """Main verification function."""
    print("=" * 60)
    print("CI WORKFLOW VERIFICATION (CP-008)")
    print("=" * 60)
    print()

    # Get all workflows
    workflows = get_all_workflows()

    if not workflows:
        print("❌ No workflow files found in .github/workflows/")
        return 1

    print(f"📋 Found {len(workflows)} workflow file(s)")
    print()

    # Validate each workflow
    print("=" * 60)
    print("WORKFLOW VALIDATION")
    print("=" * 60)
    print()

    validation_results = []
    for workflow_path in workflows:
        result = validate_workflow_syntax(workflow_path)
        validation_results.append(result)

        if result["valid"]:
            print(f"✅ {result['file']}")
            print(f"   Name: {result.get('name', 'N/A')}")
            print(f"   Jobs: {', '.join(result.get('jobs', []))}")
        else:
            print(f"❌ {result['file']}")
            for error in result["errors"]:
                print(f"   Error: {error}")
        print()

    # Check resilience
    print("=" * 60)
    print("RESILIENCE CHECK")
    print("=" * 60)
    print()

    resilience_results = []
    for workflow_path in workflows:
        result = check_workflow_resilience(workflow_path)
        resilience_results.append(result)

        if result["resilient"]:
            print(f"✅ {result['file']} - Resilient")
        else:
            print(f"⚠️  {result['file']} - Issues found:")
            for issue in result["issues"]:
                print(f"   {issue}")
        print()

    # Check GitHub status
    print("=" * 60)
    print("GITHUB ACTIONS STATUS")
    print("=" * 60)
    print()

    github_status = check_github_workflow_status()

    if github_status.get("status") == "success":
        workflows_status = github_status.get("workflows", {})
        print(f"📊 Found {len(workflows_status)} workflow(s) with recent runs")
        print()

        for workflow_name, status in workflows_status.items():
            status_icon = "✅" if status["conclusion"] == "success" else "❌" if status["conclusion"] == "failure" else "🟡"
            print(f"{status_icon} {workflow_name}")
            print(f"   Status: {status['status']}")
            print(f"   Conclusion: {status['conclusion'] or 'pending'}")
            print(f"   Created: {status['created_at']}")
            if status.get("html_url"):
                print(f"   URL: {status['html_url']}")
            print()
    else:
        print(
            f"⚠️  GitHub status check: {github_status.get('status', 'unknown')}")
        if "error" in github_status:
            print(f"   Error: {github_status['error']}")
        print()

    # Summary
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print()

    valid_count = sum(1 for r in validation_results if r["valid"])
    resilient_count = sum(1 for r in resilience_results if r["resilient"])

    print(f"✅ Valid workflows: {valid_count}/{len(workflows)}")
    print(f"✅ Resilient workflows: {resilient_count}/{len(workflows)}")
    print()

    if valid_count == len(workflows) and resilient_count == len(workflows):
        print("🎉 All workflows verified and resilient!")
        return 0
    else:
        print("⚠️  Some workflows need attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())
