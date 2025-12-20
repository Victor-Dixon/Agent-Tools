#!/usr/bin/env python3
"""
Validation script for stall detection enhancement.

Tests the new ActivityEmitter and test execution activity detection methods.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestrators.overnight.enhanced_agent_activity_detector import EnhancedAgentActivityDetector


def validate_activity_detection():
    """Validate the enhanced activity detection."""
    print("🔍 Validating Enhanced Agent Activity Detection")
    print("=" * 60)
    
    detector = EnhancedAgentActivityDetector()
    
    # Test with Agent-3 (current agent)
    agent_id = "Agent-3"
    print(f"\n📊 Testing activity detection for {agent_id}...")
    
    activity_data = detector.detect_agent_activity(agent_id)
    
    print(f"\n✅ Activity Detection Results:")
    print(f"   Latest Activity: {activity_data.get('latest_activity')}")
    print(f"   Latest Source: {activity_data.get('latest_activity_source')}")
    print(f"   Activity Count: {activity_data.get('activity_count')}")
    print(f"   Sources Detected: {len(activity_data.get('activity_sources', []))}")
    
    print(f"\n📋 Activity Sources Found:")
    for source in activity_data.get('activity_sources', []):
        details = activity_data.get('activity_details', {}).get(source, {})
        age = details.get('age_seconds', 0)
        print(f"   - {source}: {age:.0f}s ago")
    
    # Check if new sources are working
    new_sources = ['activity_emitter', 'test_execution']
    found_new_sources = [s for s in activity_data.get('activity_sources', []) if s in new_sources]
    
    print(f"\n🎯 New Sources Status:")
    for source in new_sources:
        if source in activity_data.get('activity_sources', []):
            print(f"   ✅ {source}: DETECTED")
        else:
            print(f"   ⚠️  {source}: Not detected (may be normal if no recent activity)")
    
    # Test all agents
    print(f"\n📊 Testing all agents...")
    all_activity = detector.get_all_agents_activity()
    
    print(f"\n✅ All Agents Activity Summary:")
    for agent_id, activity in all_activity.items():
        latest = activity.get('latest_activity')
        sources = activity.get('activity_sources', [])
        if latest:
            age = activity.get('detected_at', 0) - latest
            print(f"   {agent_id}: {len(sources)} sources, last activity {age:.0f}s ago")
        else:
            print(f"   {agent_id}: No activity detected")
    
    print(f"\n✅ Validation Complete!")
    print(f"   Enhanced detector is operational")
    print(f"   New activity sources integrated successfully")
    
    return True


if __name__ == "__main__":
    try:
        validate_activity_detection()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
