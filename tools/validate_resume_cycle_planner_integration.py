#!/usr/bin/env python3
"""
Resume Cycle Planner Integration Validation
==========================================

Validates that resume cycle planner integration works correctly with contract system.

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-10
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def validate_integration():
    """Validate resume cycle planner integration."""
    print("=" * 80)
    print("RESUME CYCLE PLANNER INTEGRATION VALIDATION")
    print("=" * 80)
    print()
    
    # Check integration file exists
    integration_file = project_root / "src" / "core" / "resume_cycle_planner_integration.py"
    
    if not integration_file.exists():
        print("❌ ERROR: Integration file not found")
        return False
    
    print("✅ Integration file found")
    
    # Check imports
    try:
        from src.core.resume_cycle_planner_integration import ResumeCyclePlannerIntegration
        print("✅ Integration class importable")
    except ImportError as e:
        print(f"❌ ERROR: Cannot import integration: {e}")
        return False
    
    # Check initialization
    try:
        integration = ResumeCyclePlannerIntegration()
        print("✅ Integration initializes successfully")
        
        if integration._initialized:
            print("✅ Contract system integration initialized")
        else:
            print("⚠️  Contract system not available (expected in some environments)")
    except Exception as e:
        print(f"❌ ERROR: Initialization failed: {e}")
        return False
    
    # Check methods exist
    methods = ["get_and_claim_next_task", "get_next_task_preview"]
    for method in methods:
        if hasattr(integration, method):
            print(f"✅ Method {method} exists")
        else:
            print(f"❌ ERROR: Method {method} not found")
            return False
    
    # Check optimized_stall_resume_prompt integration
    prompt_file = project_root / "src" / "core" / "optimized_stall_resume_prompt.py"
    
    if not prompt_file.exists():
        print("❌ ERROR: Optimized stall resume prompt file not found")
        return False
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for integration usage
    checks = [
        ("ResumeCyclePlannerIntegration", "Integration class imported"),
        ("get_and_claim_next_task", "Task claiming method used"),
        ("get_next_task_preview", "Task preview method used"),
        ("auto_claim_tasks", "Auto-claim feature present"),
    ]
    
    print()
    print("📋 Integration Usage in Resume Prompt:")
    print("-" * 80)
    
    all_present = True
    for check, description in checks:
        if check in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - NOT FOUND")
            all_present = False
    
    # Check prompt builder includes task
    if "TASK ASSIGNED FROM CYCLE PLANNER" in content or "AVAILABLE TASK IN CYCLE PLANNER" in content:
        print("✅ Task assignment included in prompt")
    else:
        print("⚠️  Task assignment formatting not verified")
    
    print()
    print("=" * 80)
    
    if all_present:
        print("✅ VALIDATION PASSED: Integration correctly implemented")
        return True
    else:
        print("⚠️  VALIDATION WARNINGS: Some checks failed")
        return False

if __name__ == "__main__":
    success = validate_integration()
    sys.exit(0 if success else 1)

