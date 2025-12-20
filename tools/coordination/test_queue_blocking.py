#!/usr/bin/env python3
"""
Test Queue Blocking Operations
===============================

Tests that multi-message operations properly block other sends.
Verifies queue blocking fixes for message system improvements.

Usage:
    python tools/coordination/test_queue_blocking.py
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.services.messaging_infrastructure import ConsolidatedMessagingService
from src.core.keyboard_control_lock import is_locked, get_current_holder
from src.core.config.timeout_constants import TimeoutConstants


def test_broadcast_blocking():
    """Test that broadcast operation blocks properly."""
    print("🧪 Testing broadcast blocking...")
    print()
    
    service = ConsolidatedMessagingService()
    
    # Test message
    test_message = "🧪 TEST: Queue blocking verification"
    
    print(f"📤 Sending broadcast to all agents...")
    print(f"   Message: {test_message}")
    print(f"   Expected: All 8 messages delivered sequentially with keyboard lock")
    print()
    
    # Check lock status before
    locked_before = is_locked()
    holder_before = get_current_holder()
    print(f"🔒 Lock status before: locked={locked_before}, holder={holder_before}")
    print()
    
    # Send broadcast (should block)
    start_time = time.time()
    result = service.broadcast_message(test_message, priority="regular")
    elapsed = time.time() - start_time
    
    # Check lock status after
    locked_after = is_locked()
    holder_after = get_current_holder()
    print(f"🔓 Lock status after: locked={locked_after}, holder={holder_after}")
    print()
    
    # Results
    print("📊 RESULTS:")
    print("-" * 60)
    print(f"✅ Success: {result.get('success', False)}")
    print(f"⏱️  Time elapsed: {elapsed:.2f} seconds")
    print(f"📨 Message: {result.get('message', 'N/A')}")
    print()
    
    if result.get("results"):
        print("📋 Per-Agent Results:")
        for i, agent_result in enumerate(result["results"], 1):
            agent = agent_result.get("agent", "UNKNOWN")
            success = agent_result.get("success", False)
            delivered = agent_result.get("delivered", False)
            queue_id = agent_result.get("queue_id", "N/A")
            
            status = "✅" if delivered else ("⏳" if success else "❌")
            print(f"   {status} {agent}: queued={success}, delivered={delivered}, id={queue_id[:8]}...")
        print()
    
    # Verify blocking
    if locked_after:
        print("⚠️  WARNING: Lock still held after broadcast!")
        print(f"   Holder: {holder_after}")
        print()
    else:
        print("✅ Lock released after broadcast")
        print()
    
    print("-" * 60)
    print()
    
    return result.get("success", False) and not locked_after


def test_single_message_blocking():
    """Test that single message with wait_for_delivery blocks."""
    print("🧪 Testing single message blocking...")
    print()
    
    service = ConsolidatedMessagingService()
    
    # Test message
    test_message = "🧪 TEST: Single message blocking"
    test_agent = "Agent-6"  # Test to self
    
    print(f"📤 Sending message to {test_agent}...")
    print(f"   Message: {test_message}")
    print(f"   Mode: wait_for_delivery=True (blocking)")
    print()
    
    # Check lock status before
    locked_before = is_locked()
    print(f"🔒 Lock status before: locked={locked_before}")
    print()
    
    # Send message with blocking
    start_time = time.time()
    result = service.send_message(
        test_agent, 
        test_message, 
        priority="regular",
        wait_for_delivery=True,
        timeout=TimeoutConstants.HTTP_DEFAULT
    )
    elapsed = time.time() - start_time
    
    # Check lock status after
    locked_after = is_locked()
    print(f"🔓 Lock status after: locked={locked_after}")
    print()
    
    # Results
    print("📊 RESULTS:")
    print("-" * 60)
    print(f"✅ Success: {result.get('success', False)}")
    print(f"✅ Delivered: {result.get('delivered', False)}")
    print(f"⏱️  Time elapsed: {elapsed:.2f} seconds")
    print(f"📨 Queue ID: {result.get('queue_id', 'N/A')}")
    print()
    
    if locked_after:
        print("⚠️  WARNING: Lock still held after send!")
        print()
    else:
        print("✅ Lock released after send")
        print()
    
    print("-" * 60)
    print()
    
    return result.get("delivered", False) and not locked_after


def main():
    """Run all queue blocking tests."""
    print("=" * 70)
    print("🧪 QUEUE BLOCKING TESTS")
    print("=" * 70)
    print()
    print("Testing queue blocking fixes for message system improvements")
    print()
    
    tests = [
        ("Single Message Blocking", test_single_message_blocking),
        ("Broadcast Blocking", test_broadcast_blocking),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"📋 Test: {test_name}")
        print("-" * 70)
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append((test_name, False))
            print()
    
    # Summary
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print()
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print()
    
    if passed == total:
        print("🎉 All tests passed! Queue blocking is working correctly.")
        print()
        return 0
    else:
        print("⚠️  Some tests failed. Review output above.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())




