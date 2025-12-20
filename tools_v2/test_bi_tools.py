#!/usr/bin/env python3
"""
Test BI Tools via Toolbelt
===========================

Quick test script to verify BI tools work correctly via toolbelt.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-01-27
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools_v2.toolbelt_core import ToolbeltCore


def test_bi_metrics():
    """Test bi.metrics tool."""
    print("\n" + "="*70)
    print("Testing: bi.metrics")
    print("="*70)
    
    toolbelt = ToolbeltCore()
    result = toolbelt.run(
        "bi.metrics",
        {"files": ["tools/quick_metrics.py"]}
    )
    
    print(f"Success: {result.success}")
    if result.success:
        print("Output:")
        print(result.output[:500] if result.output else "No output")
    else:
        print(f"Error: {result.error_message}")
    
    return result.success


def test_bi_roi_task():
    """Test bi.roi.task tool."""
    print("\n" + "="*70)
    print("Testing: bi.roi.task")
    print("="*70)
    
    toolbelt = ToolbeltCore()
    result = toolbelt.run(
        "bi.roi.task",
        {
            "points": 1000,
            "complexity": 50,
            "v2_impact": 2,
            "autonomy_impact": 1
        }
    )
    
    print(f"Success: {result.success}")
    if result.success:
        print("Output:")
        print(result.output[:500] if result.output else "No output")
    else:
        print(f"Error: {result.error_message}")
    
    return result.success


def test_bi_roi_optimize():
    """Test bi.roi.optimize tool."""
    print("\n" + "="*70)
    print("Testing: bi.roi.optimize")
    print("="*70)
    
    toolbelt = ToolbeltCore()
    result = toolbelt.run(
        "bi.roi.optimize",
        {"max_tasks": 5}
    )
    
    print(f"Success: {result.success}")
    if result.success:
        print("Output:")
        print(result.output[:500] if result.output else "No output")
    else:
        print(f"Error: {result.error_message}")
    
    return result.success


def main():
    """Run all BI tool tests."""
    print("\n" + "="*70)
    print("BI TOOLS TEST SUITE")
    print("="*70)
    
    results = []
    
    # Test each tool
    results.append(("bi.metrics", test_bi_metrics()))
    results.append(("bi.roi.task", test_bi_roi_task()))
    results.append(("bi.roi.optimize", test_bi_roi_optimize()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for tool_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {tool_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

