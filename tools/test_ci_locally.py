#!/usr/bin/env python3
"""
Test CI Workflow Locally
========================

Simulates CI workflow steps locally to identify issues before pushing.

Author: Agent-2 (Architecture & Design Specialist)
"""

import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent


def run_command(cmd: list, description: str) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    print(f"\n{'='*70}")
    print(f"STEP: {description}")
    print('='*70)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"✅ SUCCESS")
            if result.stdout:
                print(result.stdout[:500])  # First 500 chars
            return True, result.stdout
        else:
            print(f"❌ FAILED (exit code: {result.returncode})")
            if result.stderr:
                print("STDERR:")
                print(result.stderr[:1000])  # First 1000 chars
            if result.stdout:
                print("STDOUT:")
                print(result.stdout[:500])
            return False, result.stderr or result.stdout
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT (exceeded 5 minutes)")
        return False, "Command timed out"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, str(e)


def main():
    """Run CI workflow steps locally."""
    print("="*70)
    print("CI WORKFLOW LOCAL TEST")
    print("="*70)
    print("\nSimulating GitHub Actions CI workflow steps...")
    
    results = []
    
    # Step 1: Install dependencies
    success, output = run_command(
        ["pip", "install", "-r", "requirements.txt"],
        "Install requirements.txt"
    )
    results.append(("Install requirements.txt", success))
    
    if not success:
        print("\n⚠️  requirements.txt installation failed - CI will fail here")
        return 1
    
    # Step 2: Install dev requirements
    success, output = run_command(
        ["pip", "install", "-r", "requirements-dev.txt"],
        "Install requirements-dev.txt"
    )
    results.append(("Install requirements-dev.txt", success))
    
    # Step 3: V2 compliance check
    if Path("scripts/validate_v2_compliance.py").exists():
        success, output = run_command(
            ["python", "scripts/validate_v2_compliance.py", "--rules", "config/v2_rules.yaml"],
            "V2 Compliance Check"
        )
        results.append(("V2 Compliance", success))
    else:
        print("\n⚠️  scripts/validate_v2_compliance.py not found")
        results.append(("V2 Compliance", False))
    
    # Step 4: Lint checks
    success, output = run_command(
        ["ruff", "check", "."],
        "Ruff Lint Check"
    )
    results.append(("Ruff Lint", success))
    
    success, output = run_command(
        ["black", "--check", "."],
        "Black Format Check"
    )
    results.append(("Black Format", success))
    
    success, output = run_command(
        ["isort", "--check-only", "."],
        "isort Import Check"
    )
    results.append(("isort Import", success))
    
    # Step 5: Run tests
    success, output = run_command(
        ["pytest", "-q", "--maxfail=5", "--disable-warnings",
         "--cov=scripts", "--cov=src",
         "--cov-report=xml", "--cov-report=term",
         "--cov-fail-under=50"],
        "Run Tests with Coverage"
    )
    results.append(("Tests", success))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for step, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {step}")
    
    print(f"\n{passed}/{total} steps passed")
    
    if passed == total:
        print("\n✅ All CI steps passed locally!")
        return 0
    else:
        print(f"\n❌ {total - passed} step(s) failed - CI will fail")
        print("\nFix the failing steps before pushing to GitHub")
        return 1


if __name__ == "__main__":
    sys.exit(main())


