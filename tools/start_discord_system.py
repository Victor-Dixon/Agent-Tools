#!/usr/bin/env python3
"""
Start Complete Discord System
==============================

Starts both Discord bot and message queue processor.
Ensures .env file is loaded properly.

<!-- SSOT Domain: infrastructure -->

Author: Agent-3 (Infrastructure & DevOps)
Date: 2025-01-27
Priority: CRITICAL
"""

import logging
import os
import subprocess
import sys
import time
import atexit
from pathlib import Path

# Load .env file FIRST
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import psutil (optional but recommended)
try:
    import psutil
    from src.core.config.timeout_constants import TimeoutConstants
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("⚠️  psutil not installed - single-instance check will be limited")
    logger.warning("   Install with: pip install psutil (recommended)")

# Lock file for single instance
LOCK_FILE = Path("logs/discord_system.lock")


def cleanup_lock():
    """Remove lock file on exit."""
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        pass


def check_existing_instance():
    """Check if Discord system is already running."""
    if not LOCK_FILE.exists():
        return None
    
    try:
        # Read PID from lock file
        pid = int(LOCK_FILE.read_text().strip())
        
        # Check if process is still running
        if PSUTIL_AVAILABLE:
            if psutil.pid_exists(pid):
                try:
                    process = psutil.Process(pid)
                    # Check if it's actually our script
                    cmdline = ' '.join(process.cmdline())
                    if 'start_discord_system.py' in cmdline or \
                       'run_unified_discord_bot_with_restart.py' in cmdline:
                        return pid
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process doesn't exist or we can't access it
                    pass
        else:
            # Fallback: Try to signal process (Windows)
            if sys.platform == 'win32':
                try:
                    # On Windows, try to check if process exists
                    # This is a simple check - if it fails, process doesn't exist
                    os.kill(pid, 0)  # Signal 0 doesn't kill, just checks existence
                    # If we get here, process exists - assume it's our script
                    return pid
                except (OSError, ProcessLookupError):
                    # Process doesn't exist
                    pass
            else:
                # On Unix, try similar approach
                try:
                    os.kill(pid, 0)
                    return pid
                except (OSError, ProcessLookupError):
                    pass
        
        # Stale lock file - process is dead
        logger.warning(f"⚠️  Found stale lock file (PID {pid} not running)")
        LOCK_FILE.unlink()
        return None
        
    except (ValueError, FileNotFoundError):
        # Invalid lock file or doesn't exist
        try:
            LOCK_FILE.unlink()
        except Exception:
            pass
        return None


def create_lock():
    """Create lock file with current PID."""
    try:
        # Ensure logs directory exists
        LOCK_FILE.parent.mkdir(exist_ok=True)
        
        # Write current PID
        LOCK_FILE.write_text(str(os.getpid()))
        
        # Register cleanup on exit
        atexit.register(cleanup_lock)
        
        logger.info(f"✅ Lock file created (PID: {os.getpid()})")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create lock file: {e}")
        return False


def check_running_discord_processes():
    """Check for running Discord bot processes."""
    if not PSUTIL_AVAILABLE:
        # Without psutil, we can't easily check for other processes
        logger.warning("⚠️  psutil not available - cannot check for running processes")
        logger.warning("   Install with: pip install psutil (recommended)")
        return []
    
    try:
        current_pid = os.getpid()
        discord_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['pid'] == current_pid:
                    continue
                    
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'run_unified_discord_bot_with_restart.py' in cmdline or \
                   'unified_discord_bot.py' in cmdline:
                    discord_processes.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return discord_processes
    except Exception as e:
        logger.warning(f"⚠️  Could not check for running processes: {e}")
        return []


def check_token():
    """Check if Discord token is set."""
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("❌ DISCORD_BOT_TOKEN not set!")
        logger.error("   Set it in .env file or environment variable")
        return False
    if len(token) < 50:
        logger.warning(f"⚠️  Token appears invalid (length: {len(token)})")
        return False
    logger.info("✅ Discord bot token found")
    return True


def start_discord_bot():
    """Start Discord bot in background with auto-restart."""
    logger.info("🚀 Starting Discord bot (with auto-restart)...")
    try:
        # Create log directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Redirect output to log files so we can see errors
        stdout_file = log_dir / "discord_bot.log"
        stderr_file = log_dir / "discord_bot_errors.log"

        with open(stdout_file, "w", encoding="utf-8") as stdout, \
                open(stderr_file, "w", encoding="utf-8") as stderr:
            process = subprocess.Popen(
                [sys.executable, "tools/run_unified_discord_bot_with_restart.py"],
                stdout=stdout,
                stderr=stderr,
                text=True,
                cwd=str(Path(__file__).parent.parent)
            )

        # Give it a moment to start
        time.sleep(2)

        # Check if process is still alive
        if process.poll() is not None:
            logger.error(
                f"❌ Discord bot exited immediately (exit code: {process.returncode})")
            logger.error(f"   Check logs: {stdout_file} and {stderr_file}")
            # Read error output
            try:
                with open(stderr_file, "r", encoding="utf-8") as f:
                    error_output = f.read(1000)
                    if error_output:
                        logger.error(f"   Error output: {error_output[:500]}")
            except:
                pass
            return None

        logger.info(f"✅ Discord bot started (PID: {process.pid})")
        logger.info(f"   Logs: {stdout_file}")
        return process
    except Exception as e:
        logger.error(f"❌ Failed to start Discord bot: {e}", exc_info=True)
        return None


def start_queue_processor():
    """Start queue processor in background."""
    logger.info("📬 Starting message queue processor...")
    try:
        # Create log directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Redirect output to log files
        stdout_file = log_dir / "queue_processor.log"
        stderr_file = log_dir / "queue_processor_errors.log"

        with open(stdout_file, "w", encoding="utf-8") as stdout, \
                open(stderr_file, "w", encoding="utf-8") as stderr:
            process = subprocess.Popen(
                [sys.executable, "tools/start_message_queue_processor.py"],
                stdout=stdout,
                stderr=stderr,
                text=True,
                cwd=str(Path(__file__).parent.parent)
            )

        # Give it a moment to start
        time.sleep(1)

        # Check if process is still alive
        if process.poll() is not None:
            logger.error(
                f"❌ Queue processor exited immediately (exit code: {process.returncode})")
            logger.error(f"   Check logs: {stdout_file} and {stderr_file}")
            # Read error output
            try:
                with open(stderr_file, "r", encoding="utf-8") as f:
                    error_output = f.read(1000)
                    if error_output:
                        logger.error(f"   Error output: {error_output[:500]}")
            except:
                pass
            return None

        logger.info(f"✅ Queue processor started (PID: {process.pid})")
        logger.info(f"   Logs: {stdout_file}")
        return process
    except Exception as e:
        logger.error(f"❌ Failed to start queue processor: {e}", exc_info=True)
        return None


def main():
    """Start complete Discord system."""
    print("\n" + "="*70)
    print("🚀 STARTING COMPLETE DISCORD SYSTEM")
    print("="*70 + "\n")

    # Check for existing instance
    existing_pid = check_existing_instance()
    if existing_pid:
        logger.error(f"❌ Discord system is already running (PID: {existing_pid})")
        logger.error("   Only one instance can run at a time.")
        logger.error("   To stop the existing instance:")
        logger.error(f"   - Press Ctrl+C in the terminal running it, or")
        logger.error(f"   - Kill the process: taskkill /F /PID {existing_pid}")
        return 1
    
    # Check for running Discord bot processes
    running_processes = check_running_discord_processes()
    if running_processes:
        logger.warning(f"⚠️  Found {len(running_processes)} running Discord bot process(es): {running_processes}")
        logger.warning("   These may conflict with the new instance.")
        response = input("   Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            logger.info("   Aborted by user")
            return 1
    
    # Create lock file
    if not create_lock():
        logger.error("❌ Failed to create lock file - cannot ensure single instance")
        return 1

    # Check token
    if not check_token():
        cleanup_lock()
        print("\n💡 To fix:")
        print("   1. Create .env file in project root")
        print("   2. Add: DISCORD_BOT_TOKEN=your_token_here")
        print("   3. Run this script again\n")
        return 1

    # Start Discord bot
    bot_process = start_discord_bot()
    if not bot_process:
        cleanup_lock()
        return 1

    # Wait a bit for bot to initialize
    time.sleep(3)

    # Start queue processor
    queue_process = start_queue_processor()
    if not queue_process:
        logger.warning(
            "⚠️  Queue processor failed to start - messages won't be delivered")

    print("\n" + "="*70)
    print("✅ DISCORD SYSTEM STARTED")
    print("="*70)
    print(f"Discord Bot PID: {bot_process.pid if bot_process else 'FAILED'}")
    print(
        f"Queue Processor PID: {queue_process.pid if queue_process else 'FAILED'}")
    print("\n💡 To stop:")
    print("   Press Ctrl+C or kill the processes")
    print("="*70 + "\n")

    # Crash tracking to prevent infinite restart loops
    bot_crash_count = 0
    queue_crash_count = 0
    max_crashes = 5  # Maximum consecutive crashes before stopping
    crash_cooldown = 10  # Seconds to wait before restarting after crash
    last_bot_crash_time = 0
    last_queue_crash_time = 0
    bot_stable_time = 30  # Seconds bot must run successfully to reset crash count
    queue_stable_time = 30
    bot_start_time = time.time()
    queue_start_time = time.time()

    # Keep script running
    try:
        while True:
            time.sleep(1)
            
            # Check if bot process is still alive or needs restart
            if bot_process is None:
                # Process is None (failed restart or never started) - try to start
                current_time = time.time()
                if current_time - last_bot_crash_time >= crash_cooldown:
                    logger.warning(
                        "⚠️  Discord bot process is None - attempting to start...")
                    bot_process = start_discord_bot()
                    if bot_process:
                        bot_start_time = time.time()
                        bot_crash_count = 0  # Reset on successful start
                    else:
                        logger.error(
                            "   Failed to start - will retry after cooldown")
                        last_bot_crash_time = current_time
                        bot_crash_count += 1
            elif bot_process.poll() is not None:
                # Process died - check crash count and cooldown
                exit_code = bot_process.returncode
                current_time = time.time()
                
                # Check if bot ran long enough to be considered stable
                if current_time - bot_start_time >= bot_stable_time:
                    bot_crash_count = 0  # Reset crash count on stable run
                
                bot_crash_count += 1
                logger.error(
                    f"❌ Discord bot process died (exit code: {exit_code})")
                logger.error(
                    f"   Crash count: {bot_crash_count}/{max_crashes}")
                logger.error(
                    "   Check logs/discord_bot_errors.log for details")
                
                if bot_crash_count >= max_crashes:
                    logger.error(
                        f"❌ Bot crashed {max_crashes} times in a row!")
                    logger.error(
                        "   Stopping auto-restart to prevent infinite loop.")
                    logger.error(
                        "   Please investigate the issue before restarting manually.")
                    bot_process = None  # Stop trying to restart
                elif current_time - last_bot_crash_time >= crash_cooldown:
                    # Cooldown passed - attempt restart
                    logger.info(
                        f"   Attempting to restart Discord bot (cooldown passed)...")
                    bot_process = start_discord_bot()
                    if bot_process:
                        bot_start_time = time.time()
                        last_bot_crash_time = 0  # Reset crash time on success
                    else:
                        last_bot_crash_time = current_time
                else:
                    # Still in cooldown - wait
                    remaining = crash_cooldown - (current_time - last_bot_crash_time)
                    logger.info(
                        f"   Waiting {int(remaining)}s before restart (cooldown)...")
                    last_bot_crash_time = current_time
            else:
                # Bot is running - check if it's been stable long enough
                if bot_crash_count > 0:
                    current_time = time.time()
                    if current_time - bot_start_time >= bot_stable_time:
                        logger.info(
                            f"✅ Bot has been stable for {bot_stable_time}s - resetting crash count")
                        bot_crash_count = 0

            # Check if queue process is still alive or needs restart
            if queue_process is None:
                # Process is None (failed restart or never started) - try to start
                current_time = time.time()
                if current_time - last_queue_crash_time >= crash_cooldown:
                    logger.warning(
                        "⚠️  Queue processor process is None - attempting to start...")
                    queue_process = start_queue_processor()
                    if queue_process:
                        queue_start_time = time.time()
                        queue_crash_count = 0  # Reset on successful start
                    else:
                        logger.error(
                            "   Failed to start - will retry after cooldown")
                        last_queue_crash_time = current_time
                        queue_crash_count += 1
            elif queue_process.poll() is not None:
                # Process died - check crash count and cooldown
                exit_code = queue_process.returncode
                current_time = time.time()
                
                # Check if queue ran long enough to be considered stable
                if current_time - queue_start_time >= queue_stable_time:
                    queue_crash_count = 0  # Reset crash count on stable run
                
                queue_crash_count += 1
                logger.error(
                    f"❌ Queue processor process died (exit code: {exit_code})")
                logger.error(
                    f"   Crash count: {queue_crash_count}/{max_crashes}")
                logger.error(
                    "   Check logs/queue_processor_errors.log for details")
                
                if queue_crash_count >= max_crashes:
                    logger.error(
                        f"❌ Queue processor crashed {max_crashes} times in a row!")
                    logger.error(
                        "   Stopping auto-restart to prevent infinite loop.")
                    logger.error(
                        "   Please investigate the issue before restarting manually.")
                    queue_process = None  # Stop trying to restart
                elif current_time - last_queue_crash_time >= crash_cooldown:
                    # Cooldown passed - attempt restart
                    logger.info(
                        f"   Attempting to restart queue processor (cooldown passed)...")
                    queue_process = start_queue_processor()
                    if queue_process:
                        queue_start_time = time.time()
                        last_queue_crash_time = 0  # Reset crash time on success
                    else:
                        last_queue_crash_time = current_time
                else:
                    # Still in cooldown - wait
                    remaining = crash_cooldown - (current_time - last_queue_crash_time)
                    logger.info(
                        f"   Waiting {int(remaining)}s before restart (cooldown)...")
                    last_queue_crash_time = current_time
            else:
                # Queue is running - check if it's been stable long enough
                if queue_crash_count > 0:
                    current_time = time.time()
                    if current_time - queue_start_time >= queue_stable_time:
                        logger.info(
                            f"✅ Queue processor has been stable for {queue_stable_time}s - resetting crash count")
                        queue_crash_count = 0
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down...")
        cleanup_lock()
        if bot_process and bot_process.poll() is None:
            logger.info("   Stopping Discord bot...")
            try:
                bot_process.terminate()
                bot_process.wait(timeout=TimeoutConstants.HTTP_QUICK)
            except subprocess.TimeoutExpired:
                logger.warning(
                    "   Discord bot didn't terminate in time - forcing kill...")
                bot_process.kill()
                bot_process.wait()
            except Exception as e:
                logger.error(f"   Error stopping Discord bot: {e}")

        if queue_process and queue_process.poll() is None:
            logger.info("   Stopping queue processor...")
            try:
                queue_process.terminate()
                queue_process.wait(timeout=TimeoutConstants.HTTP_QUICK)
            except subprocess.TimeoutExpired:
                logger.warning(
                    "   Queue processor didn't terminate in time - forcing kill...")
                queue_process.kill()
                queue_process.wait()
            except Exception as e:
                logger.error(f"   Error stopping queue processor: {e}")

        logger.info("✅ Shutdown complete")
        cleanup_lock()

    return 0


if __name__ == "__main__":
    sys.exit(main())
