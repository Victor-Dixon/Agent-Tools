#!/usr/bin/env python3
"""
GitHub Pusher Service - Background Service Launcher
===================================================

Starts the GitHub Pusher Agent as a background service with continuous mode.

<!-- SSOT Domain: infrastructure -->

Author: Agent-3 (Infrastructure & DevOps Specialist)
Date: 2025-01-27
License: MIT
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.github_pusher_agent import GitHubPusherAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for GitHub Pusher Service."""
    parser = argparse.ArgumentParser(
        description="Start GitHub Pusher Agent as background service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start service (5 minute interval)
  python tools/start_github_pusher_service.py

  # Custom interval (2 minutes)
  python tools/start_github_pusher_service.py --interval 120

  # Run once and exit (test mode)
  python tools/start_github_pusher_service.py --once
        """
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval between cycles in seconds (default: 300 = 5 minutes)"
    )
    
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process queue once and exit (test mode)"
    )
    
    parser.add_argument(
        "--max-items",
        type=int,
        default=10,
        help="Maximum items to process per cycle (default: 10)"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("🚀 GITHUB PUSHER SERVICE - Starting")
    logger.info("=" * 70)
    
    try:
        agent = GitHubPusherAgent()
        
        if args.once:
            # Test mode: process once
            logger.info("🧪 Test mode: Processing queue once...")
            stats = agent.process_queue(max_items=args.max_items)
            logger.info(f"✅ Test complete: {stats}")
            print(f"\n📊 Results: {stats}")
        else:
            # Continuous mode
            logger.info(f"🔄 Starting continuous mode (interval: {args.interval}s)")
            logger.info("💡 Press Ctrl+C to stop")
            agent.run_continuous(interval_seconds=args.interval)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Service stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Service error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

