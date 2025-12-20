#!/usr/bin/env python3
"""
Stress Test Messaging Queue - CLI Command
==========================================

Command-line tool to stress test the message queue system with:
- 9-agent simulation
- Mock delivery with configurable latency/success rate
- Chaos mode (random crashes, latency spikes)
- Comparison mode (real vs mock delivery)

Usage:
    python -m tools.stress_test_messaging_queue [options]

<!-- SSOT Domain: infrastructure -->

Author: Agent-3 (Infrastructure & DevOps Specialist)
Date: 2025-01-27
License: MIT
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.mock_unified_messaging_core import (
    MockUnifiedMessagingCore,
    MockDeliveryConfig,
)
from src.core.stress_test_runner import StressTestRunner, MessageType
from src.core.message_queue import MessageQueue, QueueConfig

# Optional import - MessageQueueProcessor may not exist
try:
    from src.core.message_queue_processor import MessageQueueProcessor
    HAS_MESSAGE_QUEUE_PROCESSOR = True
except ImportError:
    HAS_MESSAGE_QUEUE_PROCESSOR = False
    MessageQueueProcessor = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_mock_delivery_callback(mock_core: MockUnifiedMessagingCore):
    """Create delivery callback using mock core."""
    def delivery_callback(sender: str, recipient: str, content: str, **kwargs) -> bool:
        return mock_core.send_message(
            content=content,
            sender=sender,
            recipient=recipient,
        )
    return delivery_callback


def create_real_delivery_callback(processor=None):
    """Create delivery callback using real message queue processor."""
    if not HAS_MESSAGE_QUEUE_PROCESSOR or processor is None:
        # Fallback: Use direct queue
        queue = MessageQueue()
        def delivery_callback(sender: str, recipient: str, content: str, **kwargs) -> bool:
            try:
                queue_id = queue.enqueue(
                    message={
                        "content": content,
                        "sender": sender,
                        "recipient": recipient,
                        **kwargs
                    },
                    priority="normal",
                    metadata=kwargs.get("metadata", {})
                )
                return queue_id is not None
            except Exception as e:
                logger.error(f"Error enqueueing message: {e}")
                return False
        return delivery_callback
    
    def delivery_callback(sender: str, recipient: str, content: str, **kwargs) -> bool:
        # Enqueue message to real queue
        try:
            queue_id = processor.queue.enqueue(
                message={
                    "content": content,
                    "sender": sender,
                    "recipient": recipient,
                    **kwargs
                },
                priority="normal",
                metadata=kwargs.get("metadata", {})
            )
            return queue_id is not None
        except Exception as e:
            logger.error(f"Error enqueueing message: {e}")
            return False
    return delivery_callback


def run_stress_test(
    duration: int,
    messages_per_second: float,
    use_mock: bool = True,
    chaos_mode: bool = False,
    success_rate: float = 0.95,
    min_latency_ms: int = 1,
    max_latency_ms: int = 10,
    output_file: Optional[str] = None,
    batch_size: int = 100,
    interval: float = 0.01,
    use_in_memory_queue: bool = True,
) -> None:
    """Run stress test.
    
    Args:
        duration: Test duration in seconds
        messages_per_second: Target message rate
        use_mock: Use mock delivery (True) or real queue (False)
        chaos_mode: Enable chaos mode
        success_rate: Mock success rate (0.0-1.0)
        min_latency_ms: Minimum latency in milliseconds
        max_latency_ms: Maximum latency in milliseconds
        output_file: Optional output file for results JSON
        batch_size: Batch size for queue processing (default: 100, optimized)
        interval: Interval between batches in seconds (default: 0.01, optimized)
        use_in_memory_queue: Use in-memory queue for performance (default: True)
    """
    logger.info("=" * 70)
    logger.info("🚀 STRESS TEST MESSAGING QUEUE")
    logger.info("=" * 70)
    logger.info(f"Duration: {duration}s")
    logger.info(f"Message Rate: {messages_per_second} msg/s")
    logger.info(f"Mode: {'MOCK' if use_mock else 'REAL'}")
    logger.info(f"Chaos Mode: {'ENABLED' if chaos_mode else 'DISABLED'}")
    if not use_mock:
        logger.info(f"Batch Size: {batch_size}")
        logger.info(f"Interval: {interval}s")
        logger.info(f"In-Memory Queue: {'ENABLED' if use_in_memory_queue else 'DISABLED'}")
    logger.info("=" * 70)
    
    # Setup delivery callback
    if use_mock:
        # Create mock messaging core
        config = MockDeliveryConfig(
            min_latency_ms=min_latency_ms,
            max_latency_ms=max_latency_ms,
            success_rate=success_rate,
            chaos_mode=chaos_mode,
        )
        mock_core = MockUnifiedMessagingCore(config)
        delivery_callback = create_mock_delivery_callback(mock_core)
        logger.info("✅ Mock messaging core initialized")
    else:
        # Use real message queue
        if HAS_MESSAGE_QUEUE_PROCESSOR:
            # Use in-memory queue for performance if requested
            if use_in_memory_queue:
                from src.core.in_memory_message_queue import InMemoryMessageQueue
                queue = InMemoryMessageQueue(max_size=50000)
                logger.info("✅ In-memory queue initialized (high performance)")
            else:
                queue = MessageQueue()
                logger.info("✅ File-based queue initialized")
            
            processor = MessageQueueProcessor(queue=queue)
            delivery_callback = create_real_delivery_callback(processor)
            logger.info("✅ Real message queue processor initialized")
            
            # Start processing queue in background with optimized batch size
            import threading
            def process_queue():
                processor.process_queue(max_messages=None, batch_size=batch_size, interval=interval)
            queue_thread = threading.Thread(target=process_queue, daemon=True)
            queue_thread.start()
        else:
            # Fallback: Direct queue without processor
            delivery_callback = create_real_delivery_callback()
            logger.info("✅ Real message queue initialized (direct mode)")
    
    # Create stress test runner
    runner = StressTestRunner(
        delivery_callback=delivery_callback,
        duration_seconds=duration,
        messages_per_second=messages_per_second,
        message_types=list(MessageType),
    )
    
    # Run test
    logger.info("🔄 Starting stress test...")
    start_time = time.time()
    runner.start()
    elapsed_time = time.time() - start_time
    
    # Collect results
    stats = runner.get_stats()
    
    if use_mock:
        mock_stats = mock_core.get_stats()
        stats["mock_delivery_stats"] = mock_stats
    
    logger.info("=" * 70)
    logger.info("📊 STRESS TEST RESULTS")
    logger.info("=" * 70)
    logger.info(f"Duration: {stats['test_duration_seconds']:.2f}s")
    logger.info(f"Total Messages: {stats['total_messages_sent']}")
    logger.info(f"Successful: {stats['total_successful']}")
    logger.info(f"Failed: {stats['total_failed']}")
    logger.info(f"Success Rate: {stats['overall_success_rate']:.2f}%")
    logger.info(f"Messages/Second: {stats['messages_per_second']:.2f}")
    
    if use_mock and "mock_delivery_stats" in stats:
        mock_stats = stats["mock_delivery_stats"]
        logger.info(f"Average Latency: {mock_stats['average_latency_ms']:.2f}ms")
        if mock_stats['chaos_events_count'] > 0:
            logger.info(f"Chaos Events: {mock_stats['chaos_events_count']}")
    
    logger.info("=" * 70)
    
    # Per-agent statistics
    logger.info("\n📈 Per-Agent Statistics:")
    logger.info("-" * 70)
    for agent_stat in stats["agent_stats"]:
        logger.info(
            f"{agent_stat['agent_id']}: "
            f"{agent_stat['message_count']} msgs, "
            f"{agent_stat['success_rate']:.1f}% success, "
            f"{agent_stat['average_latency_ms']:.2f}ms avg latency"
        )
    
    # Save results to file if requested
    if output_file:
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"\n💾 Results saved to: {output_path}")
    
    return stats


def run_comparison_mode(
    duration: int,
    messages_per_second: float,
    output_file: Optional[str] = None,
) -> None:
    """Run comparison mode (real vs mock delivery).
    
    Args:
        duration: Test duration in seconds
        messages_per_second: Target message rate
        output_file: Optional output file for results JSON
    """
    logger.info("=" * 70)
    logger.info("🔬 COMPARISON MODE: REAL vs MOCK")
    logger.info("=" * 70)
    
    # Run mock test
    logger.info("\n📦 Running MOCK delivery test...")
    mock_results = run_stress_test(
        duration=duration // 2,  # Half duration for each
        messages_per_second=messages_per_second,
        use_mock=True,
        chaos_mode=False,
        output_file=None,  # Don't save individual results
    )
    
    time.sleep(2)  # Brief pause between tests
    
    # Run real test
    logger.info("\n🔧 Running REAL delivery test...")
    real_results = run_stress_test(
        duration=duration // 2,  # Half duration for each
        messages_per_second=messages_per_second,
        use_mock=False,
        chaos_mode=False,
        output_file=None,  # Don't save individual results
    )
    
    # Compare results
    logger.info("\n" + "=" * 70)
    logger.info("📊 COMPARISON RESULTS")
    logger.info("=" * 70)
    
    comparison = {
        "mock": {
            "messages": mock_results["total_messages_sent"],
            "success_rate": mock_results["overall_success_rate"],
            "messages_per_second": mock_results["messages_per_second"],
            "avg_latency_ms": (
                mock_results.get("mock_delivery_stats", {}).get("average_latency_ms", 0.0)
            ),
        },
        "real": {
            "messages": real_results["total_messages_sent"],
            "success_rate": real_results["overall_success_rate"],
            "messages_per_second": real_results["messages_per_second"],
            "avg_latency_ms": 0.0,  # Real queue doesn't track latency
        },
    }
    
    logger.info(f"Mock - Messages: {comparison['mock']['messages']}, "
                f"Success: {comparison['mock']['success_rate']:.1f}%, "
                f"Rate: {comparison['mock']['messages_per_second']:.1f} msg/s, "
                f"Latency: {comparison['mock']['avg_latency_ms']:.2f}ms")
    
    logger.info(f"Real - Messages: {comparison['real']['messages']}, "
                f"Success: {comparison['real']['success_rate']:.1f}%, "
                f"Rate: {comparison['real']['messages_per_second']:.1f} msg/s")
    
    # Save comparison results
    if output_file:
        output_path = Path(output_file)
        comparison["full_results"] = {
            "mock": mock_results,
            "real": real_results,
        }
        with open(output_path, 'w') as f:
            json.dump(comparison, f, indent=2)
        logger.info(f"\n💾 Comparison results saved to: {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Stress test the message queue system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run mock stress test for 60 seconds
  python -m tools.stress_test_messaging_queue --duration 60

  # Run with chaos mode
  python -m tools.stress_test_messaging_queue --duration 60 --chaos

  # Run comparison mode (real vs mock)
  python -m tools.stress_test_messaging_queue --duration 60 --compare

  # Custom message rate and success rate
  python -m tools.stress_test_messaging_queue --duration 60 --rate 20 --success-rate 0.90

  # Save results to file
  python -m tools.stress_test_messaging_queue --duration 60 --output results.json
        """
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
        "--real",
        action="store_true",
        help="Use real message queue (default: use mock)"
    )
    
    parser.add_argument(
        "--chaos",
        action="store_true",
        help="Enable chaos mode (random crashes, latency spikes)"
    )
    
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Run comparison mode (real vs mock)"
    )
    
    parser.add_argument(
        "--success-rate",
        type=float,
        default=0.95,
        help="Mock success rate (0.0-1.0, default: 0.95)"
    )
    
    parser.add_argument(
        "--min-latency",
        type=int,
        default=1,
        help="Minimum latency in milliseconds (default: 1)"
    )
    
    parser.add_argument(
        "--max-latency",
        type=int,
        default=10,
        help="Maximum latency in milliseconds (default: 10)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for results JSON"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--batch-size", "-b",
        type=int,
        default=100,
        help="Batch size for queue processing (default: 100, optimized for throughput)"
    )
    
    parser.add_argument(
        "--interval",
        type=float,
        default=0.01,
        help="Interval between batches in seconds (default: 0.01, optimized for throughput)"
    )
    
    parser.add_argument(
        "--no-in-memory",
        action="store_true",
        help="Disable in-memory queue (use file-based queue)"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate arguments
    if args.duration <= 0:
        logger.error("Duration must be positive")
        sys.exit(1)
    
    if args.rate <= 0:
        logger.error("Message rate must be positive")
        sys.exit(1)
    
    if not 0.0 <= args.success_rate <= 1.0:
        logger.error("Success rate must be between 0.0 and 1.0")
        sys.exit(1)
    
    # Run appropriate test mode
    try:
        if args.compare:
            run_comparison_mode(
                duration=args.duration,
                messages_per_second=args.rate,
                output_file=args.output,
            )
        else:
            run_stress_test(
                duration=args.duration,
                messages_per_second=args.rate,
                use_mock=not args.real,
                chaos_mode=args.chaos,
                success_rate=args.success_rate,
                min_latency_ms=args.min_latency,
                max_latency_ms=args.max_latency,
                output_file=args.output,
                batch_size=args.batch_size,
                interval=args.interval,
                use_in_memory_queue=not args.no_in_memory,
            )
    except KeyboardInterrupt:
        logger.info("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running stress test: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

