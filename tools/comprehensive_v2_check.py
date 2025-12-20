#!/usr/bin/env python3
"""
Comprehensive V2 Compliance Checker
====================================

Runs comprehensive V2 compliance check across entire codebase.
Provides detailed violation counts and statistics.

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <300 lines
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.v2_compliance_checker import V2ComplianceChecker, MAX_FILE_LINES


def comprehensive_check() -> dict:
    """Run comprehensive V2 compliance check."""
    checker = V2ComplianceChecker()
    
    # Check all Python files in src/
    src_dir = project_root / "src"
    if not src_dir.exists():
        return {"error": "src/ directory not found"}
    
    python_files = list(src_dir.rglob("*.py"))
    total_files = len(python_files)
    
    print(f"🔍 Checking {total_files} Python files in src/...")
    
    for py_file in python_files:
        if py_file.is_file():
            checker.check_file(py_file)
    
    # Categorize violations
    file_size_violations = [v for v in checker.violations if v.get("type") == "file_size"]
    function_violations = [v for v in checker.violations if v.get("type") == "function_size"]
    class_violations = [v for v in checker.violations if v.get("type") == "class_size"]
    ssot_violations = [v for v in checker.violations if v.get("type") == "ssot_tag"]
    syntax_errors = [v for v in checker.violations if v.get("type") == "syntax_error"]
    
    # Calculate statistics
    total_violations = len(checker.violations)
    compliant_count = len(checker.compliant_files)
    violation_count = total_files - compliant_count
    
    # Group file violations by directory
    violations_by_dir = {}
    for v in file_size_violations:
        file_path = Path(v["file"])
        dir_path = str(file_path.parent.relative_to(project_root))
        if dir_path not in violations_by_dir:
            violations_by_dir[dir_path] = []
        violations_by_dir[dir_path].append(v)
    
    results = {
        "total_files": total_files,
        "compliant_files": compliant_count,
        "files_with_violations": violation_count,
        "total_violations": total_violations,
        "file_size_violations": len(file_size_violations),
        "function_violations": len(function_violations),
        "class_violations": len(class_violations),
        "ssot_violations": len(ssot_violations),
        "syntax_errors": len(syntax_errors),
        "violations_by_type": {
            "file_size": file_size_violations,
            "function_size": function_violations,
            "class_size": class_violations,
            "ssot_tag": ssot_violations,
            "syntax_error": syntax_errors
        },
        "violations_by_directory": violations_by_dir,
        "top_violations": sorted(
            file_size_violations,
            key=lambda x: x.get("current", 0),
            reverse=True
        )[:20]
    }
    
    return results


def print_report(results: dict):
    """Print comprehensive compliance report."""
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    print("\n" + "="*70)
    print("📊 COMPREHENSIVE V2 COMPLIANCE REPORT")
    print("="*70)
    
    print(f"\n📁 FILES:")
    print(f"  Total Files: {results['total_files']}")
    print(f"  Compliant Files: {results['compliant_files']}")
    print(f"  Files with Violations: {results['files_with_violations']}")
    print(f"  Compliance Rate: {(results['compliant_files'] / results['total_files'] * 100):.1f}%")
    
    print(f"\n🚨 VIOLATIONS:")
    print(f"  Total Violations: {results['total_violations']}")
    print(f"  File Size Violations: {results['file_size_violations']}")
    print(f"  Function Size Violations: {results['function_violations']}")
    print(f"  Class Size Violations: {results['class_violations']}")
    print(f"  SSOT Tag Violations: {results['ssot_violations']}")
    print(f"  Syntax Errors: {results['syntax_errors']}")
    
    if results['top_violations']:
        print(f"\n📋 TOP 20 FILE SIZE VIOLATIONS:")
        for i, v in enumerate(results['top_violations'], 1):
            file_path = Path(v["file"]).relative_to(project_root)
            current = v.get("current", 0)
            over_limit = current - MAX_FILE_LINES
            print(f"  {i:2d}. {file_path}")
            print(f"      {current} lines (exceeds limit by {over_limit} lines)")
    
    if results['violations_by_directory']:
        print(f"\n📂 VIOLATIONS BY DIRECTORY:")
        for dir_path, violations in sorted(
            results['violations_by_directory'].items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]:
            print(f"  {dir_path}: {len(violations)} violations")
    
    print("\n" + "="*70 + "\n")


def main():
    """CLI entry point."""
    results = comprehensive_check()
    print_report(results)
    
    # Exit with error code if violations found
    if results.get("total_violations", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

