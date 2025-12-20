#!/usr/bin/env python3
"""
Task Verification Tool
======================

Verifies if a task assignment is still valid by checking current file state.
Prevents wasted effort on already-completed work.

Usage:
    python tools/verify_task.py src/core/shared_utilities.py
    python tools/verify_task.py --file gaming_integration_core.py --search

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-10-13
License: MIT
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess


def get_file_metrics(file_path: Path) -> Dict[str, Any]:
    """Get comprehensive metrics for a Python file."""
    if not file_path.exists():
        return {"exists": False, "error": "File not found"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.splitlines()
        tree = ast.parse(content)
        
        # Count classes and functions
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        # Get last modified info from git
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%an|%ar|%s', '--', str(file_path)],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0 and result.stdout:
                author, date, message = result.stdout.strip().split('|', 2)
            else:
                author = date = message = "Unknown"
        except Exception:
            author = date = message = "Unknown"
        
        return {
            "exists": True,
            "path": str(file_path),
            "lines": len(lines),
            "classes": len(classes),
            "functions": len(functions),
            "last_modified_by": author,
            "last_modified": date,
            "last_commit": message,
            "v2_compliant": len(lines) <= 400
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}


def search_file(filename: str) -> list:
    """Search for files matching pattern in project."""
    try:
        result = subprocess.run(
            ['git', 'ls-files', f'**/*{filename}*'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return [line for line in result.stdout.strip().split('\n') if line]
        return []
    except Exception:
        return []


def verify_task(file_path: str, search: bool = False) -> Dict[str, Any]:
    """Verify if a task is still needed."""
    # Search for file if requested
    if search or not Path(file_path).exists():
        matches = search_file(Path(file_path).name)
        if not matches:
            return {
                "status": "not_found",
                "message": f"File '{file_path}' not found in project",
                "recommendation": "Task may be invalid or file was deleted"
            }
        if len(matches) > 1:
            return {
                "status": "multiple_found",
                "matches": matches,
                "message": f"Found {len(matches)} files matching pattern",
                "recommendation": "Specify full path or check all matches"
            }
        file_path = matches[0]
    
    # Get metrics
    metrics = get_file_metrics(Path(file_path))
    
    if not metrics.get("exists"):
        return {
            "status": "not_found",
            "message": f"File does not exist: {file_path}",
            "recommendation": "Task may already be completed or file moved/deleted"
        }
    
    # Analyze if work is needed
    if metrics.get("error"):
        return {
            "status": "error",
            "message": metrics["error"],
            "recommendation": "Check file syntax"
        }
    
    # Check if already refactored
    indicators = []
    if metrics["v2_compliant"]:
        indicators.append("✅ V2 compliant (≤400 lines)")
    else:
        indicators.append(f"⚠️ V2 violation ({metrics['lines']} lines)")
    
    if metrics["functions"] < 10 and metrics["classes"] < 5:
        indicators.append("✅ Reasonable complexity")
    else:
        indicators.append(f"⚠️ High complexity ({metrics['functions']} functions, {metrics['classes']} classes)")
    
    # Check commit message for refactoring keywords
    commit_msg = metrics.get("last_commit", "").lower()
    if any(word in commit_msg for word in ["refactor", "consolidate", "v2", "solid", "modular"]):
        indicators.append(f"⚠️ Recently refactored: '{metrics['last_commit']}'")
    
    return {
        "status": "analyzed",
        "file": file_path,
        "metrics": metrics,
        "indicators": indicators,
        "recommendation": "Review indicators before starting work"
    }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Verify if a task assignment is still valid",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Check specific file
    python tools/verify_task.py src/core/shared_utilities.py
    
    # Search for file and check
    python tools/verify_task.py --file gaming_integration_core.py --search
    
    # Check before starting assignment
    python tools/verify_task.py src/services/vector_integration.py

This tool helps prevent wasted effort on already-completed tasks!
        """
    )
    
    parser.add_argument('file', nargs='?', help='File path to verify')
    parser.add_argument('--file', '-f', dest='file_alt', help='File path (alternative)')
    parser.add_argument('--search', '-s', action='store_true', help='Search for file if not found')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    file_path = args.file or args.file_alt
    if not file_path:
        parser.print_help()
        sys.exit(1)
    
    result = verify_task(file_path, args.search)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        # Pretty print results
        print("\n" + "="*70)
        print("🔍 TASK VERIFICATION REPORT")
        print("="*70)
        
        if result["status"] == "not_found":
            print(f"\n❌ {result['message']}")
            print(f"\n💡 Recommendation: {result['recommendation']}")
        elif result["status"] == "multiple_found":
            print(f"\n⚠️  {result['message']}")
            print("\nMatches found:")
            for match in result["matches"]:
                print(f"  - {match}")
            print(f"\n💡 Recommendation: {result['recommendation']}")
        elif result["status"] == "analyzed":
            metrics = result["metrics"]
            print(f"\n📁 File: {result['file']}")
            print(f"\n📊 Current Metrics:")
            print(f"  Lines: {metrics['lines']}")
            print(f"  Classes: {metrics['classes']}")
            print(f"  Functions: {metrics['functions']}")
            print(f"  V2 Compliant: {'Yes' if metrics['v2_compliant'] else 'No'}")
            print(f"\n🔄 Last Modified:")
            print(f"  By: {metrics['last_modified_by']}")
            print(f"  When: {metrics['last_modified']}")
            print(f"  Commit: {metrics['last_commit']}")
            print(f"\n🎯 Analysis:")
            for indicator in result["indicators"]:
                print(f"  {indicator}")
            print(f"\n💡 Recommendation: {result['recommendation']}")
        
        print("\n" + "="*70 + "\n")
    
    # Exit code based on status
    if result["status"] == "not_found":
        sys.exit(2)  # File not found
    elif result["status"] == "error":
        sys.exit(1)  # Error
    else:
        sys.exit(0)  # Success


if __name__ == "__main__":
    main()

