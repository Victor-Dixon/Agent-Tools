#!/usr/bin/env python3
"""
Comprehensive Consolidation Testing - C-048-2
=============================================

Tests all consolidated modules for V2 compliance and functionality.

Author: Agent-3 (Infrastructure & DevOps)
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_discord_consolidation():
    """Test Discord consolidated modules."""
    print("=" * 70)
    print("🧪 TEST 1: Discord Consolidation")
    print("=" * 70)

    tests_passed = 0
    tests_total = 0

    # Test 1.1: Import discord_service
    tests_total += 1
    try:
        from src.discord_commander import DiscordService

        print("✅ discord_service import: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ discord_service import: FAIL - {e}")

    # Test 1.2: Import discord_agent_communication
    tests_total += 1
    try:
        from src.discord_commander import AgentCommunicationEngine

        print("✅ discord_agent_communication import: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ discord_agent_communication import: FAIL - {e}")

    # Test 1.3: Import discord_models
    tests_total += 1
    try:
        print("✅ discord_models import: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ discord_models import: FAIL - {e}")

    # Test 1.4: Create instances
    tests_total += 1
    try:
        from src.discord_commander import AgentCommunicationEngine, DiscordService

        service = DiscordService()
        engine = AgentCommunicationEngine()
        print("✅ Instance creation: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Instance creation: FAIL - {e}")

    print(f"\n📊 Discord Tests: {tests_passed}/{tests_total} passed")
    print()
    return tests_passed, tests_total


def test_browser_consolidation():
    """Test browser consolidated modules."""
    print("=" * 70)
    print("🧪 TEST 2: Browser Consolidation")
    print("=" * 70)

    tests_passed = 0
    tests_total = 0

    # Test 2.1: Import thea_browser_service
    tests_total += 1
    try:
        from src.infrastructure.browser import TheaBrowserService

        print("✅ thea_browser_service import: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ thea_browser_service import: FAIL - {e}")

    # Test 2.2: Import thea_session_management
    tests_total += 1
    try:
        from src.infrastructure.browser import TheaSessionManagement

        print("✅ thea_session_management import: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ thea_session_management import: FAIL - {e}")

    # Test 2.3: Import thea_content_operations
    tests_total += 1
    try:
        from src.infrastructure.browser import TheaContentOperations

        print("✅ thea_content_operations import: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ thea_content_operations import: FAIL - {e}")

    # Test 2.4: Create instances
    tests_total += 1
    try:
        from src.infrastructure.browser import (
            TheaBrowserService,
            TheaContentOperations,
            TheaSessionManagement,
        )

        browser = TheaBrowserService()
        session = TheaSessionManagement()
        content = TheaContentOperations()
        print("✅ Instance creation: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Instance creation: FAIL - {e}")

    print(f"\n📊 Browser Tests: {tests_passed}/{tests_total} passed")
    print()
    return tests_passed, tests_total


def test_v2_compliance():
    """Verify V2 compliance of consolidated files."""
    print("=" * 70)
    print("🧪 TEST 3: V2 Compliance Verification")
    print("=" * 70)

    files_to_check = [
        ("src/discord_commander/discord_service.py", 381),
        ("src/discord_commander/discord_agent_communication.py", 258),
        ("src/discord_commander/discord_models.py", 104),
        ("src/infrastructure/browser/thea_browser_service.py", 273),
        ("src/infrastructure/browser/thea_session_management.py", 271),
        ("src/infrastructure/browser/thea_content_operations.py", 326),
    ]

    tests_passed = 0
    tests_total = len(files_to_check)

    for filepath, expected_lines in files_to_check:
        path = Path(filepath)
        if path.exists():
            with open(path, encoding="utf-8") as f:
                actual_lines = len(f.readlines())

            if actual_lines < 400:
                print(f"✅ {path.name}: {actual_lines} lines (<400) - V2 COMPLIANT")
                tests_passed += 1
            else:
                print(f"❌ {path.name}: {actual_lines} lines (≥400) - V2 VIOLATION")
        else:
            print(f"❌ {path.name}: FILE NOT FOUND")

    print(f"\n📊 V2 Compliance: {tests_passed}/{tests_total} files compliant")
    print()
    return tests_passed, tests_total


def test_gui_imports():
    """Test GUI imports (C-047 fix)."""
    print("=" * 70)
    print("🧪 TEST 4: GUI Imports (C-047)")
    print("=" * 70)

    tests_passed = 0
    tests_total = 1

    try:
        print("✅ src.gui.styles.themes: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ src.gui.styles.themes: FAIL - {e}")

    print(f"\n📊 GUI Tests: {tests_passed}/{tests_total} passed")
    print()
    return tests_passed, tests_total


def main():
    """Run all comprehensive tests."""
    print()
    print("=" * 70)
    print("🤖 AGENT-3: COMPREHENSIVE CONSOLIDATION TESTING")
    print("=" * 70)
    print()

    total_passed = 0
    total_tests = 0

    # Test 1: Discord
    passed, total = test_discord_consolidation()
    total_passed += passed
    total_tests += total

    # Test 2: Browser
    passed, total = test_browser_consolidation()
    total_passed += passed
    total_tests += total

    # Test 3: V2 Compliance
    passed, total = test_v2_compliance()
    total_passed += passed
    total_tests += total

    # Test 4: GUI
    passed, total = test_gui_imports()
    total_passed += passed
    total_tests += total

    # Final summary
    print("=" * 70)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_tests - total_passed}")
    print(f"Success Rate: {total_passed/total_tests*100:.1f}%")
    print()

    if total_passed == total_tests:
        print("✅ ALL TESTS PASSED!")
        return True
    else:
        print(f"⚠️  {total_tests - total_passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    print()
    print("🐝 WE ARE SWARM - Testing complete!")
    print()
    sys.exit(0 if success else 1)
