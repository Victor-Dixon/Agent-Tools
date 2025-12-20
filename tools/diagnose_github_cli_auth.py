#!/usr/bin/env python3
"""
Diagnose GitHub CLI Authentication Issues
=========================================

Identifies GitHub CLI authentication problems and provides solutions.

Author: Agent-3 (Infrastructure & DevOps Specialist)
Task: CP-004

<!-- SSOT Domain: infrastructure -->
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def check_gh_installed() -> Tuple[bool, Optional[str]]:
    """Check if GitHub CLI is installed."""
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip().split("\n")[0]
            return True, version
        return False, None
    except FileNotFoundError:
        return False, "GitHub CLI not found in PATH"
    except Exception as e:
        return False, str(e)


def check_gh_auth_status() -> Dict[str, any]:
    """Check GitHub CLI authentication status."""
    print("=" * 60)
    print("🔐 Checking GitHub CLI Authentication")
    print("=" * 60)

    results = {
        "installed": False,
        "authenticated": False,
        "accounts": [],
        "errors": []
    }

    # Check if installed
    installed, version_or_error = check_gh_installed()
    results["installed"] = installed

    if not installed:
        print(f"❌ GitHub CLI not installed: {version_or_error}")
        results["errors"].append(
            f"GitHub CLI not installed: {version_or_error}")
        return results

    print(f"✅ GitHub CLI installed: {version_or_error}")

    # Check auth status
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            output = result.stdout
            results["authenticated"] = True
            print("✅ GitHub CLI is authenticated")

            # Parse accounts
            if "Logged in to" in output:
                lines = output.split("\n")
                for line in lines:
                    if "Logged in to" in line or "github.com as" in line:
                        print(f"   {line.strip()}")
                        results["accounts"].append(line.strip())
        else:
            results["authenticated"] = False
            error_msg = result.stderr or result.stdout
            print(f"❌ Authentication check failed:")
            print(f"   {error_msg}")
            results["errors"].append(error_msg)

    except subprocess.TimeoutExpired:
        results["errors"].append("Authentication check timed out")
        print("❌ Authentication check timed out")
    except Exception as e:
        results["errors"].append(str(e))
        print(f"❌ Error checking authentication: {e}")

    return results


def check_environment_tokens() -> Dict[str, any]:
    """Check for GitHub tokens in environment."""
    print("\n" + "=" * 60)
    print("🔑 Checking Environment Variables")
    print("=" * 60)

    results = {
        "tokens_found": [],
        "token_sources": []
    }

    # Common token environment variables
    token_vars = [
        "GITHUB_TOKEN",
        "GH_TOKEN",
        "FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN",
        "GITHUB_PAT",
        "GITHUB_ACCESS_TOKEN"
    ]

    for var in token_vars:
        value = os.getenv(var)
        if value:
            # Show first/last chars for security
            masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            print(f"✅ {var}: {masked}")
            results["tokens_found"].append(var)
            results["token_sources"].append({
                "variable": var,
                "length": len(value),
                "masked": masked
            })
        else:
            print(f"⚠️  {var}: Not set")

    return results


def check_git_remote_auth() -> Dict[str, any]:
    """Check Git remote authentication."""
    print("\n" + "=" * 60)
    print("📡 Checking Git Remote Authentication")
    print("=" * 60)

    results = {
        "remotes": [],
        "auth_issues": []
    }

    try:
        # Get remotes
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            remotes = result.stdout.strip().split("\n")
            for remote in remotes:
                if remote:
                    print(f"   {remote}")
                    results["remotes"].append(remote)

                    # Check if remote uses HTTPS (needs auth)
                    if "https://" in remote and "github.com" in remote:
                        if "@" not in remote and "token" not in remote.lower():
                            results["auth_issues"].append(
                                f"Remote {remote} uses HTTPS without embedded token"
                            )
        else:
            print("⚠️  Could not list remotes")

    except Exception as e:
        print(f"❌ Error checking remotes: {e}")
        results["auth_issues"].append(str(e))

    return results


def test_github_api_access() -> Dict[str, any]:
    """Test GitHub API access."""
    print("\n" + "=" * 60)
    print("🌐 Testing GitHub API Access")
    print("=" * 60)

    results = {
        "api_accessible": False,
        "error": None
    }

    try:
        # Try to get authenticated user
        result = subprocess.run(
            ["gh", "api", "user"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("✅ GitHub API accessible")
            results["api_accessible"] = True
            # Parse user info
            import json
            try:
                user_data = json.loads(result.stdout)
                if "login" in user_data:
                    print(f"   Authenticated as: {user_data['login']}")
            except:
                pass
        else:
            error_msg = result.stderr or result.stdout
            print(f"❌ GitHub API access failed:")
            print(f"   {error_msg}")
            results["error"] = error_msg

    except subprocess.TimeoutExpired:
        results["error"] = "API test timed out"
        print("❌ API test timed out")
    except Exception as e:
        results["error"] = str(e)
        print(f"❌ Error testing API: {e}")

    return results


def generate_solutions(diagnostics: Dict) -> List[str]:
    """Generate solutions based on diagnostics."""
    solutions = []

    if not diagnostics["gh_auth"]["installed"]:
        solutions.append("""
🔧 SOLUTION 1: Install GitHub CLI
   Windows (PowerShell):
     winget install --id GitHub.cli
   
   Or download from: https://cli.github.com/
        """)

    if not diagnostics["gh_auth"]["authenticated"]:
        solutions.append("""
🔧 SOLUTION 2: Authenticate GitHub CLI
   Run: gh auth login
   
   Options:
   - GitHub.com (default)
   - HTTPS (recommended for automation)
   - Login with web browser or token
        """)

    if diagnostics["env_tokens"]["tokens_found"]:
        solutions.append("""
🔧 SOLUTION 3: Use Environment Token
   If you have GITHUB_TOKEN set, you can use it directly:
   
   export GITHUB_TOKEN=your_token_here
   gh auth status  # Should now work
        """)
    else:
        solutions.append("""
🔧 SOLUTION 4: Set GitHub Token
   Create a Personal Access Token (PAT):
   1. Go to: https://github.com/settings/tokens
   2. Generate new token (classic)
   3. Select scopes: repo, workflow, read:org
   4. Set environment variable:
      export GITHUB_TOKEN=your_token_here
        """)

    if diagnostics["git_remote"]["auth_issues"]:
        solutions.append("""
🔧 SOLUTION 5: Fix Git Remote Authentication
   Option A: Use SSH instead of HTTPS
     git remote set-url origin git@github.com:user/repo.git
   
   Option B: Embed token in HTTPS URL
     git remote set-url origin https://TOKEN@github.com/user/repo.git
   
   Option C: Use GitHub CLI credential helper
     gh auth setup-git
        """)

    return solutions


def main():
    """Main diagnostic function."""
    print("\n" + "=" * 60)
    print("🔍 GitHub CLI Authentication Diagnostic Tool")
    print("=" * 60)
    print("Task: CP-004 - Address GitHub CLI authentication blockers")
    print()

    diagnostics = {
        "gh_auth": check_gh_auth_status(),
        "env_tokens": check_environment_tokens(),
        "git_remote": check_git_remote_auth(),
        "api_test": test_github_api_access()
    }

    # Summary
    print("\n" + "=" * 60)
    print("📊 Diagnostic Summary")
    print("=" * 60)

    issues = []
    if not diagnostics["gh_auth"]["installed"]:
        issues.append("GitHub CLI not installed")
    if not diagnostics["gh_auth"]["authenticated"]:
        issues.append("GitHub CLI not authenticated")
    if not diagnostics["api_test"]["api_accessible"]:
        issues.append("GitHub API not accessible")
    if diagnostics["git_remote"]["auth_issues"]:
        issues.append("Git remote authentication issues")

    if issues:
        print("\n❌ Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ No authentication issues detected")

    # Generate solutions
    solutions = generate_solutions(diagnostics)

    if solutions:
        print("\n" + "=" * 60)
        print("💡 Recommended Solutions")
        print("=" * 60)
        for solution in solutions:
            print(solution)

    # Save diagnostic report
    report_file = Path(
        "agent_workspaces/Agent-3/github_cli_auth_diagnostic_2025-12-12.md")
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, 'w') as f:
        f.write("# GitHub CLI Authentication Diagnostic Report\n\n")
        f.write(f"**Date**: 2025-12-12\n")
        f.write(f"**Task**: CP-004\n\n")
        f.write("## Issues Found\n\n")
        for issue in issues:
            f.write(f"- {issue}\n")
        f.write("\n## Solutions\n\n")
        for solution in solutions:
            f.write(solution + "\n")

    print(f"\n✅ Diagnostic report saved: {report_file}")
    print()


if __name__ == "__main__":
    main()
