#!/usr/bin/env python3
"""
Test Suite Validation Tool
==========================

Runs test suite and captures results for file deletion infrastructure support.

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_test_suite(timeout=None):
    from src.core.config.timeout_constants import TimeoutConstants
    if timeout is None:
        timeout = TimeoutConstants.HTTP_EXTENDED
    """Run test suite and capture results."""
    print("=" * 60)
    print("🧪 Running Test Suite Validation")
    print("=" * 60)
    print()
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "status": "running",
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "tests_skipped": 0,
        "errors": [],
        "failures": [],
        "duration_seconds": 0,
    }
    
    try:
        print("📋 Starting pytest...")
        print()
        
        # Run pytest with JSON report
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-q",
            "--tb=line",
            "--maxfail=10",
            "--json-report",
            "--json-report-file=test_results.json",
            "--timeout=TimeoutConstants.HTTP_EXTENDED",
        ]
        
        start_time = datetime.now()
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        result["duration_seconds"] = duration
        
        # Parse output
        output_lines = process.stdout.split('\n')
        
        # Try to parse JSON report if it exists
        json_report_path = Path("test_results.json")
        if json_report_path.exists():
            try:
                with open(json_report_path) as f:
                    json_report = json.load(f)
                    result["tests_run"] = json_report.get("summary", {}).get("total", 0)
                    result["tests_passed"] = json_report.get("summary", {}).get("passed", 0)
                    result["tests_failed"] = json_report.get("summary", {}).get("failed", 0)
                    result["tests_skipped"] = json_report.get("summary", {}).get("skipped", 0)
                    
                    # Extract failures
                    for test in json_report.get("tests", []):
                        if test.get("outcome") == "failed":
                            result["failures"].append({
                                "nodeid": test.get("nodeid", ""),
                                "message": test.get("call", {}).get("longrepr", "")[:500]
                            })
            except Exception as e:
                result["errors"].append(f"Could not parse JSON report: {e}")
        
        # Parse stdout for summary
        for line in output_lines:
            if "passed" in line.lower() and "failed" in line.lower():
                # Try to extract numbers
                import re
from src.core.config.timeout_constants import TimeoutConstants
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 2:
                    result["tests_passed"] = int(numbers[0]) if numbers else 0
                    result["tests_failed"] = int(numbers[1]) if len(numbers) > 1 else 0
        
        result["status"] = "success" if process.returncode == 0 else "failed"
        result["returncode"] = process.returncode
        
        # Limit output size
        result["stdout"] = process.stdout[:2000]
        result["stderr"] = process.stderr[:1000] if process.stderr else ""
        
        print("=" * 60)
        print("📊 Test Suite Results")
        print("=" * 60)
        print(f"Status: {result['status'].upper()}")
        print(f"Tests Run: {result['tests_run']}")
        print(f"Tests Passed: {result['tests_passed']}")
        print(f"Tests Failed: {result['tests_failed']}")
        print(f"Tests Skipped: {result['tests_skipped']}")
        print(f"Duration: {duration:.1f} seconds")
        print()
        
        if result["failures"]:
            print(f"⚠️  {len(result['failures'])} test(s) failed")
            for i, failure in enumerate(result["failures"][:5], 1):
                print(f"   {i}. {failure.get('nodeid', 'Unknown')}")
        print()
        
        return result
        
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["errors"].append(f"Test suite timeout after {timeout} seconds")
        print(f"❌ Test suite timeout after {timeout} seconds")
        return result
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
        print(f"❌ Error running test suite: {e}")
        return result

def main():
    """Main function."""
    print("=" * 60)
    print("🚀 Test Suite Validation")
    print("=" * 60)
    print()
    
    result = run_test_suite()
    
    # Save report
    report_dir = Path("agent_workspaces/Agent-7")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / "TEST_SUITE_VALIDATION_REPORT.json"
    with open(report_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"✅ Report saved: {report_file}")
    print()
    
    # Determine overall status
    if result["status"] == "success" and result["tests_failed"] == 0:
        print("✅ Test suite validation: PASSED")
        return 0
    elif result["status"] == "success" and result["tests_failed"] > 0:
        print(f"⚠️  Test suite validation: {result['tests_failed']} test(s) failed")
        return 1
    else:
        print(f"❌ Test suite validation: {result['status']}")
        return 1

if __name__ == "__main__":
    sys.exit(main())




