#!/usr/bin/env python3
"""
Check for Sensitive Files in Git - Security Audit Tool
======================================================

Checks if any sensitive files are tracked in git that shouldn't be.

<!-- SSOT Domain: infrastructure -->

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-01-27
Priority: CRITICAL - Security Audit
"""

import subprocess
import sys
from pathlib import Path
from typing import Any


def run_git_command(cmd: list[str]) -> str:
    """Run git command and return output."""
    try:
        result = subprocess.run(
            ["git"] + cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error running git command: {e}")
        return ""


def check_tracked_sensitive_files() -> dict[str, Any]:
    """Check for sensitive files tracked in git."""
    # Get all tracked files
    tracked_files = run_git_command(["ls-files"]).split("\n")
    
    # Patterns to check for
    sensitive_patterns = [
        ".env",
        "thea_cookies",
        "discord_token",
        "github_token",
        "api_key",
        "secret",
        "password",
        "credential",
        "_token",
        "_key",
        "_secret",
    ]
    
    found_files = []
    
    for file in tracked_files:
        if not file:
            continue
        
        file_lower = file.lower()
        for pattern in sensitive_patterns:
            if pattern in file_lower:
                found_files.append({
                    "file": file,
                    "pattern": pattern,
                    "risk": "HIGH" if pattern in [".env", "token", "secret", "password"] else "MEDIUM",
                })
                break
    
    return {
        "total_tracked": len(tracked_files),
        "sensitive_files": found_files,
        "count": len(found_files),
    }


def check_gitignore_coverage() -> dict[str, Any]:
    """Check if .gitignore properly covers sensitive patterns."""
    gitignore_path = Path(".gitignore")
    
    if not gitignore_path.exists():
        return {"error": ".gitignore not found"}
    
    gitignore_content = gitignore_path.read_text(encoding="utf-8")
    
    required_patterns = [
        ".env",
        "thea_cookies",
        "*_token",
        "*_key",
        "*_secret",
        "password",
        "credential",
    ]
    
    missing_patterns = []
    for pattern in required_patterns:
        if pattern not in gitignore_content:
            missing_patterns.append(pattern)
    
    return {
        "gitignore_exists": True,
        "missing_patterns": missing_patterns,
        "all_covered": len(missing_patterns) == 0,
    }


def print_security_report(results: dict[str, Any], gitignore_check: dict[str, Any]) -> None:
    """Print security audit report."""
    print("=" * 80)
    print("SECURITY AUDIT - SENSITIVE FILES CHECK")
    print("=" * 80)
    print()
    
    print(f"Total Tracked Files: {results['total_tracked']}")
    print(f"Sensitive Files Found: {results['count']}")
    print()
    
    if results['count'] > 0:
        print("⚠️  WARNING: Sensitive files found in git tracking!")
        print()
        for item in results['sensitive_files']:
            print(f"  [{item['risk']}] {item['file']}")
            print(f"      Pattern: {item['pattern']}")
        print()
        print("🔴 ACTION REQUIRED:")
        print("   1. Remove these files from git tracking:")
        print("      git rm --cached <file>")
        print("   2. Ensure they're in .gitignore")
        print("   3. Consider removing from git history if already pushed")
        print()
    else:
        print("✅ No sensitive files found in git tracking")
        print()
    
    print("Gitignore Coverage:")
    if gitignore_check.get("error"):
        print(f"  ❌ {gitignore_check['error']}")
    elif gitignore_check.get("all_covered"):
        print("  ✅ All required patterns covered in .gitignore")
    else:
        print("  ⚠️  Missing patterns in .gitignore:")
        for pattern in gitignore_check.get("missing_patterns", []):
            print(f"      - {pattern}")
    print()
    
    print("=" * 80)


def main():
    """Main execution."""
    print("Checking for sensitive files in git...")
    print()
    
    results = check_tracked_sensitive_files()
    gitignore_check = check_gitignore_coverage()
    
    print_security_report(results, gitignore_check)
    
    if results['count'] > 0:
        print("\n🔴 CRITICAL: Sensitive files detected in git!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())


