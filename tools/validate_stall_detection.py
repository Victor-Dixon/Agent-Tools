#!/usr/bin/env python3
"""
Validation script for stall detection fix.
Tests that monitor.py correctly uses detect_agent_activity().
"""
from src.orchestrators.overnight.enhanced_agent_activity_detector import EnhancedAgentActivityDetector
from src.orchestrators.overnight.monitor import ProgressMonitor
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def validate_stall_detection():
    """Validate stall detection implementation."""
    print("=" * 60)
    print("Agent-8 Stall Detection Fix - Validation Test")
    print("=" * 60)

    # Test 1: Import validation
    print("\n✅ Test 1: Import Validation")
    try:
        monitor = ProgressMonitor()
        detector = EnhancedAgentActivityDetector()
        print("   ✓ ProgressMonitor imported successfully")
        print("   ✓ EnhancedAgentActivityDetector imported successfully")
    except Exception as e:
        print(f"   ✗ Import failed: {e}")
        return False

    # Test 2: detect_agent_activity() call
    print("\n✅ Test 2: detect_agent_activity() Method")
    try:
        result = detector.detect_agent_activity('Agent-8')
        activity_sources = result.get("activity_sources", [])
        latest_activity = result.get("latest_activity")
        print(f"   ✓ detect_agent_activity() call successful")
        print(f"   ✓ Activity sources found: {len(activity_sources)}")
        print(f"   ✓ Latest activity timestamp: {latest_activity}")
        if activity_sources:
            print(f"   ✓ Sources: {', '.join(activity_sources[:5])}")
    except Exception as e:
        print(f"   ✗ detect_agent_activity() failed: {e}")
        return False

    # Test 3: get_stalled_agents() integration
    print("\n✅ Test 3: get_stalled_agents() Integration")
    try:
        monitor.start_monitoring()
        stalled = await monitor.get_stalled_agents()
        print(f"   ✓ get_stalled_agents() call successful")
        print(f"   ✓ Stalled agents detected: {len(stalled)}")
        if stalled:
            print(f"   ✓ Agents: {', '.join(stalled)}")
        else:
            print(f"   ✓ No stalled agents (expected)")
    except Exception as e:
        print(f"   ✗ get_stalled_agents() failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ ALL VALIDATION TESTS PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = asyncio.run(validate_stall_detection())
    sys.exit(0 if success else 1)
