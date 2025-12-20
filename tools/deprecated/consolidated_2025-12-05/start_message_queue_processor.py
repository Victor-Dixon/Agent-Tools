#!/usr/bin/env python3
"""
⚠️ DEPRECATED: This tool has been archived.
Use unified_monitor.py instead (consolidated monitoring system).
Archived: 2025-12-08
Replacement: tools.unified_monitor.UnifiedMonitor
"""
"""
Start Message Queue Processor
==============================

Starts the message queue processor to deliver queued messages.
This must be running for messages to be delivered via PyAutoGUI.

Author: Agent-3 (Infrastructure & DevOps)
Date: 2025-01-27
Priority: CRITICAL
V2 Compliant: Yes
<!-- SSOT Domain: infrastructure -->
"""

import logging
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Configure logging with both console and file handlers
log_dir = Path(__file__).resolve().parent.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "queue_processor.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding='utf-8'),
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Start the message queue processor."""
    try:
        from src.core.message_queue_processor import MessageQueueProcessor
        
        logger.info("🚀 Starting Message Queue Processor...")
        logger.info("📬 This will process queued messages and deliver them via PyAutoGUI")
        logger.info("🛑 Press Ctrl+C to stop\n")
        
        # Create processor
        processor = MessageQueueProcessor()
        
        # Start processing (runs continuously)
        try:
            processor.process_queue(max_messages=None, batch_size=1, interval=5.0)
        except KeyboardInterrupt:
            logger.info("\n👋 Queue processor stopped by user")
            processor.running = False
        except Exception as e:
            logger.error(f"❌ Queue processor error: {e}", exc_info=True)
            return 1
        
        return 0
        
    except ImportError as e:
        logger.error(f"❌ Failed to import queue processor: {e}")
        logger.error("   Ensure all dependencies are installed")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

