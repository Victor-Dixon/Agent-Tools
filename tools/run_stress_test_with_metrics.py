#!/usr/bin/env python3
"""
Run Stress Test with Metrics Collection
========================================

Enhanced stress test runner that integrates with metrics collection system.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-11-29
License: MIT
"""

import argparse
import logging
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.stress_test_metrics_integration import StressTestMetricsIntegration
from src.core.stress_test_runner import StressTestRunner, MessageType
from src.core.mock_unified_messaging_core import (
    MockUnifiedMessagingCore,
    MockDeliveryConfig,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_metrics_enabled_callback(mock_core, integration):
    """Create delivery callback that records metrics."""
    def delivery_callback(sender: str, recipient: str, content: str, **kwargs):
        message_type = kwargs.get("message_type", "direct")
        start_time = time.time()
        
        # Send message
        success = mock_core.send_message(
            content=content,
            sender=sender,
            recipient=recipient,
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Record metrics
        if success:
            integration.record_queue_event(
                "message_delivered",
                queue_id=f"msg_{int(time.time() * 1000)}",
                agent_id=recipient,
                message_type=message_type,
                latency_ms=latency_ms,
                delivery_mode="mock",
            )
        else:
            integration.record_queue_event(
                "message_failed",
                queue_id=f"msg_{int(time.time() * 1000)}",
                agent_id=recipient,
                message_type=message_type,
                reason="delivery_failed",
            )
        
        return success
    
    return delivery_callback


def run_stress_test_with_metrics(
    duration: int = 60,
    messages_per_second: float = 10.0,
    success_rate: float = 0.95,
    output_dir: str = "stress_test_results",
):
    """Run stress test with integrated metrics collection."""
    logger.info("=" * 70)
    logger.info("🚀 STRESS TEST WITH METRICS COLLECTION")
    logger.info("=" * 70)
    
    # Initialize metrics integration
    integration = StressTestMetricsIntegration()
    
    # Create mock delivery core
    mock_config = MockDeliveryConfig(
        success_rate=success_rate,
        min_latency_ms=1,
        max_latency_ms=50,
    )
    mock_core = MockUnifiedMessagingCore(config=mock_config)
    
    # Create metrics-enabled callback
    delivery_callback = create_metrics_enabled_callback(mock_core, integration)
    
    # Initialize metrics collection
    collector = integration.integrate_with_stress_test_runner({
        "test_name": "metrics_integrated_test",
        "duration_seconds": duration,
        "message_rate": messages_per_second,
    })
    
    # Create and run stress test
    runner = StressTestRunner(
        delivery_callback=delivery_callback,
        duration_seconds=duration,
        messages_per_second=messages_per_second,
    )
    
    logger.info(f"Starting stress test: {duration}s, {messages_per_second} msg/s")
    runner.start()
    
    # Get runner stats
    runner_stats = runner.get_stats()
    logger.info(f"\n📊 Runner Statistics:")
    logger.info(f"   Total Messages: {runner_stats['total_messages_sent']}")
    logger.info(f"   Success Rate: {runner_stats['overall_success_rate']:.2f}%")
    logger.info(f"   Messages/sec: {runner_stats['messages_per_second']:.2f}")
    
    # Generate metrics dashboard
    logger.info("\n📈 Generating metrics dashboard...")
    dashboard = integration.finalize_stress_test(output_dir)
    
    logger.info("✅ Stress test complete with metrics collection!")
    logger.info(f"   Dashboard saved to: {output_dir}")
    
    return dashboard


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run stress test with integrated metrics collection"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=60,
        help="Test duration in seconds (default: 60)"
    )
    parser.add_argument(
        "--rate", "-r",
        type=float,
        default=10.0,
        help="Messages per second (default: 10.0)"
    )
    parser.add_argument(
        "--success-rate",
        type=float,
        default=0.95,
        help="Mock success rate (0.0-1.0, default: 0.95)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="stress_test_results",
        help="Output directory for results (default: stress_test_results)"
    )
    
    args = parser.parse_args()
    
    try:
        dashboard = run_stress_test_with_metrics(
            duration=args.duration,
            messages_per_second=args.rate,
            success_rate=args.success_rate,
            output_dir=args.output_dir,
        )
        logger.info("\n✅ Stress test with metrics complete!")
        return 0
    except Exception as e:
        logger.error(f"Error running stress test: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

