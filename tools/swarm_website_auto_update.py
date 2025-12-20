#!/usr/bin/env python3
"""
Swarm Website Auto-Update Tool
==============================

Continuously monitors agent status files and automatically updates the website.

Usage:
    python tools/swarm_website_auto_update.py [--interval 10] [--once]

Options:
    --interval SECONDS    Check interval in seconds (default: 10)
    --once               Run once and exit (for cron/scripts)

V2 Compliance | Author: Agent-7 | Date: 2025-12-14
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.services.swarm_website.auto_updater import SwarmWebsiteAutoUpdater

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Automatically update website with agent status changes'
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=10.0,
        help='Check interval in seconds (default: 10)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (for cron/scripts)'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("SWARM WEBSITE AUTO-UPDATER")
    logger.info("=" * 60)
    logger.info(f"Check interval: {args.interval}s")
    logger.info(f"Run mode: {'Once' if args.once else 'Continuous'}")
    logger.info("")
    
    updater = SwarmWebsiteAutoUpdater()
    
    if not updater.updater.enabled:
        logger.error("❌ Website updater not configured!")
        logger.error("   Set environment variables:")
        logger.error("   - SWARM_WEBSITE_URL")
        logger.error("   - SWARM_WEBSITE_USERNAME")
        logger.error("   - SWARM_WEBSITE_PASSWORD")
        return 1
    
    # Test connection
    test_result = updater.updater.test_connection()
    logger.info(f"🔗 {test_result}")
    
    if args.once:
        # Run once
        logger.info("🔍 Checking all agents...")
        updated_count = updater.check_all_agents()
        logger.info(f"✅ Updated {updated_count} agent(s)")
        return 0
    else:
        # Continuous monitoring
        try:
            updater.monitor_agent_status_files(interval=args.interval)
        except KeyboardInterrupt:
            logger.info("\n⏹️ Stopped by user")
            return 0
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())


