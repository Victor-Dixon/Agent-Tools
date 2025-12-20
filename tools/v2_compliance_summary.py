#!/usr/bin/env python3
"""
V2 Compliance Summary Tool
==========================

Quick summary tool for V2 compliance status.
Shows key metrics, active refactoring, and next priorities.

Usage:
    python tools/v2_compliance_summary.py

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <300 lines
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def get_summary() -> dict:
    """Get V2 compliance summary."""
    try:
        from tools.comprehensive_v2_check import comprehensive_check
        results = comprehensive_check()
        
        if "error" in results:
            return {"error": results["error"]}
        
        # Calculate summary
        file_violations = results["file_size_violations"]
        total_files = results["total_files"]
        compliant_files = results["compliant_files"]
        compliance_rate = (compliant_files / total_files * 100) if total_files > 0 else 0
        
        # Categorize violations
        critical = [v for v in results["top_violations"] if v.get("current", 0) > 1000]
        major = [v for v in results["top_violations"] if 500 < v.get("current", 0) <= 1000]
        moderate = [v for v in results["top_violations"] if 400 < v.get("current", 0) <= 500]
        minor = [v for v in results["top_violations"] if 300 < v.get("current", 0) <= 400]
        
        return {
            "total_files": total_files,
            "compliant_files": compliant_files,
            "file_violations": file_violations,
            "compliance_rate": round(compliance_rate, 1),
            "violations_by_tier": {
                "critical": len(critical),
                "major": len(major),
                "moderate": len(moderate),
                "minor": len(minor)
            },
            "other_violations": {
                "function": results["function_violations"],
                "class": results["class_violations"],
                "ssot": results["ssot_violations"]
            }
        }
    except Exception as e:
        return {"error": str(e)}


def print_summary(summary: dict):
    """Print formatted summary."""
    if "error" in summary:
        print(f"❌ Error: {summary['error']}")
        return
    
    print("\n" + "="*60)
    print("📊 V2 COMPLIANCE SUMMARY")
    print("="*60)
    
    print(f"\n📁 FILES:")
    print(f"  Total: {summary['total_files']}")
    print(f"  Compliant: {summary['compliant_files']}")
    print(f"  Violations: {summary['file_violations']}")
    print(f"  Compliance Rate: {summary['compliance_rate']}%")
    
    print(f"\n🚨 FILE SIZE VIOLATIONS BY TIER:")
    tiers = summary['violations_by_tier']
    print(f"  Critical (>1000 lines): {tiers['critical']}")
    print(f"  Major (500-1000 lines): {tiers['major']}")
    print(f"  Moderate (400-500 lines): {tiers['moderate']}")
    print(f"  Minor (300-400 lines): {tiers['minor']}")
    
    print(f"\n📋 OTHER VIOLATIONS:")
    other = summary['other_violations']
    print(f"  Function Size: {other['function']}")
    print(f"  Class Size: {other['class']}")
    print(f"  SSOT Tags: {other['ssot']}")
    
    print("\n" + "="*60 + "\n")


def main():
    """CLI entry point."""
    summary = get_summary()
    print_summary(summary)
    
    if "error" in summary:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

