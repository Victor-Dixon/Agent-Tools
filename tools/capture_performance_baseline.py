#!/usr/bin/env python3
"""
Capture Performance Baseline
============================

Captures current performance baseline for message queue system.
Run this before making changes to establish baseline metrics.

Usage:
    python tools/capture_performance_baseline.py

Author: Agent-6
Date: 2025-12-13
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.message_queue_performance_metrics import MessageQueuePerformanceMetrics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Capture and save performance baseline."""
    print("📊 Capturing Performance Baseline")
    print("=" * 50)
    
    metrics = MessageQueuePerformanceMetrics()
    
    # Load existing metrics
    baseline = metrics.calculate_baseline()
    
    if baseline.total_messages == 0:
        print("⚠️  No metrics available yet.")
        print("   Process some messages first to establish baseline.")
        return 1
    
    # Save baseline
    metrics.save_baseline(baseline)
    
    # Display baseline
    print(f"\n✅ Baseline captured:")
    print(f"   Timestamp: {baseline.timestamp}")
    print(f"   Total Messages: {baseline.total_messages}")
    print(f"   Success Rate: {baseline.success_rate:.2%}")
    print(f"   Avg Delivery Time: {baseline.avg_delivery_time_seconds:.3f}s")
    print(f"   Median Delivery Time: {baseline.median_delivery_time_seconds:.3f}s")
    print(f"   P95 Delivery Time: {baseline.p95_delivery_time_seconds:.3f}s")
    print(f"   P99 Delivery Time: {baseline.p99_delivery_time_seconds:.3f}s")
    print(f"   Throughput: {baseline.messages_per_second:.2f} msg/s")
    print(f"   PyAutoGUI Success Rate: {baseline.pyautogui_success_rate:.2%}")
    print(f"   Inbox Success Rate: {baseline.inbox_success_rate:.2%}")
    print(f"   Avg Retry Count: {baseline.avg_retry_count:.2f}")
    print(f"\n   Delivery Method Distribution:")
    for method, count in baseline.delivery_method_distribution.items():
        print(f"     {method}: {count}")
    
    print(f"\n📁 Baseline saved to: {metrics.baseline_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())





