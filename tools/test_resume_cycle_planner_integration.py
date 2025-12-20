#!/usr/bin/env python3
"""
Test Resume Cycle Planner Integration
=====================================
Validates that resume prompts automatically claim tasks from cycle planner.
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.resume_cycle_planner_integration import ResumeCyclePlannerIntegration
from src.core.optimized_stall_resume_prompt import generate_optimized_resume_prompt


def test_integration():
    """Test resume cycle planner integration."""
    print("🧪 Testing Resume Cycle Planner Integration...\n")
    
    results = {
        "timestamp": "2025-12-10T21:38:00Z",
        "tests": {},
        "summary": {}
    }
    
    # Test 1: Integration initialization
    print("Test 1: Integration Initialization")
    try:
        integration = ResumeCyclePlannerIntegration()
        results["tests"]["initialization"] = {
            "passed": integration._initialized,
            "status": "✅ PASS" if integration._initialized else "❌ FAIL"
        }
        print(f"  {results['tests']['initialization']['status']}")
    except Exception as e:
        results["tests"]["initialization"] = {
            "passed": False,
            "error": str(e),
            "status": f"❌ FAIL: {e}"
        }
        print(f"  {results['tests']['initialization']['status']}")
    
    # Test 2: Task preview (Agent-1)
    print("\nTest 2: Task Preview (Agent-1)")
    try:
        integration = ResumeCyclePlannerIntegration()
        if integration._initialized:
            task = integration.get_next_task_preview("Agent-1")
            results["tests"]["task_preview"] = {
                "passed": task is not None,
                "task_found": task is not None,
                "task_title": task.get("title") if task else None,
                "status": "✅ PASS" if task else "⚠️  NO TASK"
            }
            print(f"  {results['tests']['task_preview']['status']}")
            if task:
                print(f"  Task: {task.get('title', 'Unknown')}")
        else:
            results["tests"]["task_preview"] = {
                "passed": False,
                "error": "Integration not initialized",
                "status": "❌ SKIP"
            }
            print("  ❌ SKIP: Integration not initialized")
    except Exception as e:
        results["tests"]["task_preview"] = {
            "passed": False,
            "error": str(e),
            "status": f"❌ FAIL: {e}"
        }
        print(f"  {results['tests']['task_preview']['status']}")
    
    # Test 3: Resume prompt generation with auto-claim
    print("\nTest 3: Resume Prompt Generation (Auto-claim)")
    try:
        prompt = generate_optimized_resume_prompt(
            agent_id="Agent-1",
            fsm_state="active",
            stall_duration_minutes=5.0
        )
        has_task_section = "TASK ASSIGNED" in prompt or "AVAILABLE TASK" in prompt
        results["tests"]["prompt_generation"] = {
            "passed": len(prompt) > 0,
            "has_task_section": has_task_section,
            "prompt_length": len(prompt),
            "status": "✅ PASS" if len(prompt) > 0 else "❌ FAIL"
        }
        print(f"  {results['tests']['prompt_generation']['status']}")
        print(f"  Prompt length: {len(prompt)} chars")
        print(f"  Has task section: {has_task_section}")
    except Exception as e:
        results["tests"]["prompt_generation"] = {
            "passed": False,
            "error": str(e),
            "status": f"❌ FAIL: {e}"
        }
        print(f"  {results['tests']['prompt_generation']['status']}")
    
    # Calculate summary
    total_tests = len(results["tests"])
    passed_tests = sum(1 for t in results["tests"].values() if t.get("passed"))
    results["summary"] = {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": total_tests - passed_tests,
        "pass_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
    }
    
    print(f"\n{'='*50}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*50}")
    print(f"Total Tests: {results['summary']['total_tests']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Pass Rate: {results['summary']['pass_rate']}")
    
    return results


if __name__ == "__main__":
    results = test_integration()
    
    # Save results
    import json
    output_file = Path("agent_workspaces/Agent-4/validation_reports/resume_cycle_planner_validation_2025-12-10.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Validation report saved to: {output_file}")

