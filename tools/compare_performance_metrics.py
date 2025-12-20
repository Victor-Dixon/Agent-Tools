#!/usr/bin/env python3
"""
Compare Performance Metrics
============================

Compares current performance metrics to saved baseline.
Run this after making changes to see performance impact.

Usage:
    python tools/compare_performance_metrics.py

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


def format_delta(delta: float, delta_percent: float) -> str:
    """Format delta with sign and percentage."""
    sign = "+" if delta >= 0 else ""
    percent_sign = "+" if delta_percent >= 0 else ""
    return f"{sign}{delta:.3f} ({percent_sign}{delta_percent:.2f}%)"


def main():
    """Compare current metrics to baseline."""
    print("📊 Performance Metrics Comparison")
    print("=" * 50)
    
    metrics = MessageQueuePerformanceMetrics()
    
    # Get current metrics
    current_baseline = metrics.calculate_baseline()
    
    if current_baseline.total_messages == 0:
        print("⚠️  No current metrics available.")
        print("   Process some messages first.")
        return 1
    
    # Compare to baseline
    comparison = metrics.compare_to_baseline(current_baseline)
    
    if "error" in comparison:
        print(f"❌ {comparison['error']}")
        return 1
    
    # Display comparison
    print(f"\n📅 Baseline: {comparison['baseline_timestamp']}")
    print(f"📅 Current:  {comparison['current_timestamp']}")
    print()
    
    # Success rate
    sr = comparison['success_rate']
    print(f"✅ Success Rate:")
    print(f"   Baseline: {sr['baseline']:.2%}")
    print(f"   Current:  {sr['current']:.2%}")
    print(f"   Change:   {format_delta(sr['delta'], sr['delta_percent'])}")
    print()
    
    # Delivery time
    dt = comparison['avg_delivery_time']
    print(f"⏱️  Avg Delivery Time:")
    print(f"   Baseline: {dt['baseline']:.3f}s")
    print(f"   Current:  {dt['current']:.3f}s")
    print(f"   Change:   {format_delta(dt['delta'], dt['delta_percent'])}")
    print()
    
    # Throughput
    tp = comparison['throughput']
    print(f"🚀 Throughput:")
    print(f"   Baseline: {tp['baseline']:.2f} msg/s")
    print(f"   Current:  {tp['current']:.2f} msg/s")
    print(f"   Change:   {format_delta(tp['delta'], tp['delta_percent'])}")
    print()
    
    # Current metrics details
    print(f"📈 Current Metrics Summary:")
    print(f"   Total Messages: {current_baseline.total_messages}")
    print(f"   Successful: {current_baseline.successful_deliveries}")
    print(f"   Failed: {current_baseline.failed_deliveries}")
    print(f"   Median Time: {current_baseline.median_delivery_time_seconds:.3f}s")
    print(f"   P95 Time: {current_baseline.p95_delivery_time_seconds:.3f}s")
    print(f"   P99 Time: {current_baseline.p99_delivery_time_seconds:.3f}s")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())





