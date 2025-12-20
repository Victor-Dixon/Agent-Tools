#!/usr/bin/env python3
"""
Heal Stalled Agents - CLI Tool
===============================

Immediate healing tool for stalled agents. Can be run manually or
scheduled to prevent agent stalls from accumulating.

<!-- SSOT Domain: infrastructure -->

Usage:
    python tools/heal_stalled_agents.py [--start-daemon] [--check-now]

Author: Agent-3 (Infrastructure & DevOps Specialist)
Date: 2025-01-27
Priority: CRITICAL
"""

import argparse
import asyncio
import logging
import sys
import signal
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.agent_self_healing_system import (
    AgentSelfHealingSystem,
    SelfHealingConfig,
    heal_stalled_agents_now,
    get_self_healing_system,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    logger.info("\n🛑 Shutting down self-healing system...")
    system = get_self_healing_system()
    system.stop()
    sys.exit(0)


async def run_healing_check() -> None:
    """Run immediate healing check."""
    logger.info("=" * 70)
    logger.info("🏥 IMMEDIATE STALLED AGENT HEALING CHECK")
    logger.info("=" * 70)
    
    results = await heal_stalled_agents_now()
    
    logger.info("\n📊 Healing Results:")
    logger.info(f"Stalled agents found: {results['stalled_agents_found']}")
    logger.info(f"Agents healed: {len(results['agents_healed'])}")
    logger.info(f"Agents failed: {len(results['agents_failed'])}")
    
    if results['agents_healed']:
        logger.info(f"\n✅ Successfully healed: {', '.join(results['agents_healed'])}")
    
    if results['agents_failed']:
        logger.warning(f"\n⚠️ Failed to heal: {', '.join(results['agents_failed'])}")
    
    logger.info("=" * 70)
    
    # Show healing stats
    system = get_self_healing_system()
    stats = system.get_healing_stats()
    
    logger.info("\n📈 Healing Statistics:")
    logger.info(f"Total healing actions: {stats['total_actions']}")
    logger.info(f"Success rate: {stats['success_rate']:.1f}%")
    
    if stats['recent_actions']:
        logger.info("\nRecent actions:")
        for action in stats['recent_actions'][-5:]:
            status = "✅" if action['success'] else "❌"
            logger.info(
                f"  {status} {action['agent_id']}: {action['action']} "
                f"({action['timestamp']})"
            )


async def run_daemon(config: SelfHealingConfig) -> None:
    """Run self-healing system as daemon.
    
    Args:
        config: Self-healing configuration
    """
    logger.info("=" * 70)
    logger.info("🚀 STARTING AGENT SELF-HEALING DAEMON")
    logger.info("=" * 70)
    logger.info(f"Check interval: {config.check_interval_seconds}s")
    logger.info(f"Stall threshold: {config.stall_threshold_seconds}s")
    logger.info(f"Auto-reset: {config.auto_reset_enabled}")
    logger.info("=" * 70)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start system
    system = AgentSelfHealingSystem(config)
    system.start()
    
    logger.info("✅ Self-healing daemon running. Press Ctrl+C to stop.")
    
    # Keep running
    try:
        while system.running:
            await asyncio.sleep(1)
            
            # Show periodic stats every 5 minutes
            if len(system.healing_history) > 0 and len(system.healing_history) % 10 == 0:
                stats = system.get_healing_stats()
                logger.info(
                    f"📊 Healing stats: {stats['total_actions']} actions, "
                    f"{stats['success_rate']:.1f}% success rate"
                )
    except KeyboardInterrupt:
        signal_handler(None, None)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Heal stalled agents - Immediate check or daemon mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run immediate healing check
  python tools/heal_stalled_agents.py --check-now

  # Start daemon mode (continuous monitoring)
  python tools/heal_stalled_agents.py --start-daemon

  # Daemon with custom settings
  python tools/heal_stalled_agents.py --start-daemon --interval 60 --threshold 180

  # Check now with verbose logging
  python tools/heal_stalled_agents.py --check-now --verbose
        """
    )
    
    parser.add_argument(
        "--check-now",
        action="store_true",
        help="Run immediate healing check and exit"
    )
    
    parser.add_argument(
        "--start-daemon",
        action="store_true",
        help="Start self-healing daemon (continuous monitoring)"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Check interval in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--threshold",
        type=int,
        default=120,
        help="Stall threshold in seconds (default: 120)"
    )
    
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
        help="Max recovery attempts per agent (default: 3)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate arguments
    if not args.check_now and not args.start_daemon:
        parser.error("Must specify either --check-now or --start-daemon")
    
    if args.check_now and args.start_daemon:
        parser.error("Cannot specify both --check-now and --start-daemon")
    
    # Create config
    config = SelfHealingConfig(
        check_interval_seconds=args.interval,
        stall_threshold_seconds=args.threshold,
        recovery_attempts_max=args.max_attempts,
    )
    
    # Run appropriate mode
    try:
        if args.check_now:
            asyncio.run(run_healing_check())
        elif args.start_daemon:
            asyncio.run(run_daemon(config))
    except KeyboardInterrupt:
        logger.info("\n⚠️ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

