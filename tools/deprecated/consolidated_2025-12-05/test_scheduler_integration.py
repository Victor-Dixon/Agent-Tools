#!/usr/bin/env python3
"""
⚠️ DEPRECATED: This tool has been archived.
Use unified_monitor.py instead (consolidated monitoring system).
Archived: 2025-12-08
Replacement: tools.unified_monitor.UnifiedMonitor
"""
"""
Test Scheduler-StatusMonitor Integration
========================================

Quick test to verify scheduler-status monitor integration is working.

Author: Agent-4 (Captain)
Date: 2025-12-04
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_integration():
    """Test scheduler-status monitor integration."""
    print("🧪 Testing Scheduler-StatusMonitor Integration\n")
    
    # Test 1: Import integration module (bypass __init__ circular import)
    try:
        import importlib.util
        integration_path = Path(project_root) / "src" / "orchestrators" / "overnight" / "scheduler_integration.py"
        spec = importlib.util.spec_from_file_location("scheduler_integration", integration_path)
        scheduler_integration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scheduler_integration)
        SchedulerStatusMonitorIntegration = scheduler_integration.SchedulerStatusMonitorIntegration
        print("✅ Integration module imported successfully (bypassed __init__)")
    except Exception as e:
        print(f"⚠️ Direct import failed: {e}")
        print("   Trying alternative import...")
        try:
            # Try direct file import
            import sys
            sys.path.insert(0, str(Path(project_root) / "src" / "orchestrators" / "overnight"))
            from scheduler_integration import SchedulerStatusMonitorIntegration
            print("✅ Integration module imported successfully (alternative method)")
        except Exception as e2:
            print(f"❌ Failed to import integration module: {e2}")
            return False
    
    # Test 2: Create integration instance
    try:
        integration = SchedulerStatusMonitorIntegration()
        print("✅ Integration instance created successfully")
    except Exception as e:
        print(f"❌ Failed to create integration instance: {e}")
        return False
    
    # Test 3: Test integration status
    try:
        status = integration.get_integration_status()
        print(f"✅ Integration status: {status}")
    except Exception as e:
        print(f"❌ Failed to get integration status: {e}")
        return False
    
    # Test 4: Test pending tasks query (without scheduler, should return empty)
    try:
        pending = integration.get_pending_tasks_for_agent("Agent-5")
        print(f"✅ Pending tasks query works (no scheduler): {len(pending)} tasks")
    except Exception as e:
        print(f"❌ Failed to query pending tasks: {e}")
        return False
    
    # Test 5: Test task formatting (without tasks, should return empty)
    try:
        formatted = integration.format_scheduled_tasks_for_prompt("Agent-5")
        print(f"✅ Task formatting works (empty result expected)")
    except Exception as e:
        print(f"❌ Failed to format tasks: {e}")
        return False
    
    print("\n✅ All integration tests passed!")
    print("\n📋 Next: Test with actual scheduler and status monitor instances")
    return True

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
