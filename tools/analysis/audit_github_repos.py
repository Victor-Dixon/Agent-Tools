#!/usr/bin/env python3
"""
GitHub Portfolio Audit Tool
============================

Comprehensive audit of all GitHub repositories:
- Clone functionality
- CI/CD workflows
- Testing infrastructure  
- Professional setup

Author: Agent-7 - Repository Cloning Specialist
Created: 2025-10-13
"""

import subprocess
import json
from pathlib import Path
from typing import Optional

# Add to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.github_scanner import GitHubScanner
from src.core.config.timeout_constants import TimeoutConstants


def audit_repository(repo_name: str, clone_url: str, audit_dir: Path) -> dict:
    """
    Audit a single repository.
    
    Returns audit results dict.
    """
    results = {
        "name": repo_name,
        "clone_url": clone_url,
        "clone_success": False,
        "has_readme": False,
        "has_license": False,
        "has_gitignore": False,
        "has_requirements": False,
        "has_package_json": False,
        "has_tests": False,
        "test_count": 0,
        "has_ci_cd": False,
        "workflow_count": 0,
        "has_setup_py": False,
        "issues": [],
        "recommendations": [],
    }
    
    repo_path = audit_dir / repo_name
    
    # Skip if already cloned
    if repo_path.exists():
        print(f"  ⏭️ Already cloned: {repo_name}")
    else:
        # Try to clone
        print(f"  📥 Cloning {repo_name}...")
        try:
            result = subprocess.run(
                ["git", "clone", clone_url, str(repo_path)],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_EXTENDED
            )
            if result.returncode == 0:
                results["clone_success"] = True
                print(f"  ✅ Clone successful")
            else:
                results["issues"].append(f"Clone failed: {result.stderr[:100]}")
                print(f"  ❌ Clone failed")
                return results
        except Exception as e:
            results["issues"].append(f"Clone error: {str(e)}")
            print(f"  ❌ Clone error: {e}")
            return results
    
    results["clone_success"] = True
    
    # Check files
    results["has_readme"] = (repo_path / "README.md").exists()
    results["has_license"] = (repo_path / "LICENSE").exists() or (repo_path / "LICENSE.txt").exists()
    results["has_gitignore"] = (repo_path / ".gitignore").exists()
    results["has_requirements"] = (repo_path / "requirements.txt").exists()
    results["has_package_json"] = (repo_path / "package.json").exists()
    results["has_setup_py"] = (repo_path / "setup.py").exists()
    
    # Check tests
    tests_dir = repo_path / "tests"
    if tests_dir.exists():
        results["has_tests"] = True
        test_files = list(tests_dir.rglob("test_*.py"))
        results["test_count"] = len(test_files)
    
    # Check CI/CD
    workflows_dir = repo_path / ".github" / "workflows"
    if workflows_dir.exists():
        results["has_ci_cd"] = True
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        results["workflow_count"] = len(workflow_files)
    
    # Generate recommendations
    if not results["has_readme"]:
        results["recommendations"].append("Add README.md with description, installation, usage")
    if not results["has_license"]:
        results["recommendations"].append("Add LICENSE file (MIT recommended)")
    if not results["has_gitignore"]:
        results["recommendations"].append("Add .gitignore for Python/Node")
    if not results["has_requirements"] and not results["has_package_json"]:
        results["recommendations"].append("Add requirements.txt or package.json")
    if not results["has_tests"]:
        results["recommendations"].append("Add tests directory with test coverage")
        results["issues"].append("No tests found")
    if not results["has_ci_cd"]:
        results["recommendations"].append("Add GitHub Actions workflow for CI/CD")
        results["issues"].append("No CI/CD configured")
    
    return results


def main():
    """Run comprehensive GitHub audit."""
    print("=" * 70)
    print("🔍 GITHUB PORTFOLIO COMPREHENSIVE AUDIT")
    print("=" * 70)
    print()
    
    # Get all repos
    print("📋 Fetching repositories...")
    scanner = GitHubScanner()
    repos = scanner.list_user_repositories()
    
    print(f"✅ Found {len(repos)} repositories")
    print()
    
    # Audit directory
    audit_dir = Path("D:/GitHub_Audit_Test")
    audit_dir.mkdir(exist_ok=True)
    
    # Audit top priority repos first
    priority_repos = [
        "projectscanner",
        "Agent_Cellphone",
        "AutoDream.Os",
        "UltimateOptionsTradingRobot",
        "machinelearningmodelmaker",
        "trade_analyzer",
        "network-scanner",
        "dreambank",
    ]
    
    audit_results = []
    
    print("🎯 Auditing Priority Repositories:")
    print("=" * 70)
    
    for repo in repos:
        if repo.name in priority_repos:
            print(f"\n📦 {repo.name}")
            result = audit_repository(repo.name, repo.clone_url, audit_dir)
            audit_results.append(result)
    
    # Summary
    print()
    print("=" * 70)
    print("📊 AUDIT SUMMARY")
    print("=" * 70)
    
    total_audited = len(audit_results)
    clone_success = sum(1 for r in audit_results if r["clone_success"])
    has_ci_cd = sum(1 for r in audit_results if r["has_ci_cd"])
    has_tests = sum(1 for r in audit_results if r["has_tests"])
    has_license = sum(1 for r in audit_results if r["has_license"])
    
    print(f"\n✅ Repositories Audited: {total_audited}")
    print(f"✅ Clone Success: {clone_success}/{total_audited}")
    print(f"✅ Have CI/CD: {has_ci_cd}/{total_audited}")
    print(f"✅ Have Tests: {has_tests}/{total_audited}")
    print(f"✅ Have License: {has_license}/{total_audited}")
    
    # Issues
    total_issues = sum(len(r["issues"]) for r in audit_results)
    total_recommendations = sum(len(r["recommendations"]) for r in audit_results)
    
    print(f"\n⚠️ Total Issues Found: {total_issues}")
    print(f"💡 Total Recommendations: {total_recommendations}")
    
    # Save results
    output_file = Path("GITHUB_AUDIT_RESULTS.json")
    with open(output_file, "w") as f:
        json.dump({
            "audit_date": "2025-10-13",
            "total_repos": len(repos),
            "audited_repos": total_audited,
            "results": audit_results,
            "summary": {
                "clone_success_rate": f"{(clone_success/total_audited*100):.1f}%",
                "ci_cd_rate": f"{(has_ci_cd/total_audited*100):.1f}%",
                "testing_rate": f"{(has_tests/total_audited*100):.1f}%",
                "license_rate": f"{(has_license/total_audited*100):.1f}%",
                "total_issues": total_issues,
                "total_recommendations": total_recommendations,
            }
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Print top issues
    print("\n🚨 TOP ISSUES:")
    for result in audit_results:
        if result["issues"]:
            print(f"\n{result['name']}:")
            for issue in result["issues"]:
                print(f"  ❌ {issue}")
    
    print("\n✅ Audit complete!")


if __name__ == "__main__":
    main()

