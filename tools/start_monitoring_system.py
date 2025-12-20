#!/usr/bin/env python3
"""
Start Monitoring System - Activate Agent Status Monitor & Self-Healing
======================================================================

Starts the overnight orchestrator which includes:
- Agent status monitoring (every 60 seconds)
- Self-healing system (every 30 seconds)
- Recovery system
- Continuous autonomous operation

Usage:
    python tools/start_monitoring_system.py [--background]

Author: Agent-3 (Infrastructure & DevOps Specialist)
Date: 2025-01-27
V2 Compliant: Yes
<!-- SSOT Domain: infrastructure -->
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def start_monitoring():
    """Start the monitoring and self-healing system."""
    try:
        from src.orchestrators.overnight.orchestrator import OvernightOrchestrator
        
        logger.info("=" * 70)
        logger.info("🚀 STARTING AGENT MONITORING SYSTEM")
        logger.info("=" * 70)
        logger.info("This will start:")
        logger.info("  ✅ Agent Status Monitor (checks every 60 seconds)")
        logger.info("  ✅ Self-Healing System (checks every 30 seconds)")
        logger.info("  ✅ Recovery System")
        logger.info("  ✅ Continuous autonomous operation")
        logger.info("=" * 70)
        
        # Create orchestrator
        orchestrator = OvernightOrchestrator()
        
        # Start orchestrator (this starts monitoring and self-healing)
        await orchestrator.start()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down monitoring system...")
        if 'orchestrator' in locals():
            await orchestrator.stop()
        logger.info("✅ Shutdown complete")
    except Exception as e:
        logger.error(f"❌ Error starting monitoring system: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Start agent monitoring and self-healing system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start monitoring (foreground)
  python tools/start_monitoring_system.py

  # Start in background (Windows)
  start /B python tools/start_monitoring_system.py

  # Start in background (Linux/Mac)
  python tools/start_monitoring_system.py &
        """
    )
    
    parser.add_argument(
        "--background", "-b",
        action="store_true",
        help="Run in background (detached)"
    )
    
    args = parser.parse_args()
    
    if args.background:
        logger.info("Running in background mode...")
        # Note: True background requires OS-specific handling
        # For now, just run normally
        logger.warning("Background mode not fully implemented - running in foreground")
    
    # Run the monitoring system
    try:
        asyncio.run(start_monitoring())
    except KeyboardInterrupt:
        logger.info("\n⚠️ Interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()

