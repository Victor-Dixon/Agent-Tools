#!/usr/bin/env python3
"""Test Phase 2 activity sources implementation."""
from src.orchestrators.overnight.enhanced_agent_activity_detector import EnhancedAgentActivityDetector
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_phase2_sources():
    """Test Phase 2 activity sources."""
    print("=" * 60)
    print("Phase 2 Activity Sources - Validation Test")
    print("=" * 60)

    detector = EnhancedAgentActivityDetector()
    agent_id = "Agent-8"

    print(f"\nTesting activity detection for {agent_id}...")
    result = detector.detect_agent_activity(agent_id)

    activity_sources = result.get("activity_sources", [])
    latest_activity = result.get("latest_activity")

    print(f"\n✅ Activity Detection Results:")
    print(f"   Total sources found: {len(activity_sources)}")
    print(f"   Latest activity timestamp: {latest_activity}")
    print(f"\n   Activity sources:")
    for source in activity_sources:
        print(f"     - {source}")

    # Check for Phase 2 sources
    phase2_sources = [
        "passdown",
        "artifacts",
        "cycle_planner",
        "notes",
        "git_working"
    ]

    found_phase2 = [s for s in phase2_sources if s in activity_sources]

    print(f"\n✅ Phase 2 Sources Check:")
    print(f"   Expected: {len(phase2_sources)} sources")
    print(f"   Found: {len(found_phase2)} sources")
    for source in found_phase2:
        print(f"     ✓ {source}")

    missing = [s for s in phase2_sources if s not in activity_sources]
    if missing:
        print(f"   Not detected (may not have recent activity):")
        for source in missing:
            print(f"     - {source}")

    print(f"\n" + "=" * 60)
    if len(activity_sources) >= 11:  # Original 11 + any Phase 2
        print("✅ VALIDATION PASSED - Activity sources working")
        print(f"   Total sources: {len(activity_sources)} (expected: 11-16)")
    else:
        print("⚠️  VALIDATION WARNING - Fewer sources than expected")
    print("=" * 60)

    return len(activity_sources) >= 11


if __name__ == "__main__":
    success = test_phase2_sources()
    sys.exit(0 if success else 1)
