#!/usr/bin/env python3
"""
GitHub Pusher Agent - Processes Deferred Push Queue
====================================================

Background agent that processes deferred GitHub operations from the queue.
Runs every 5 minutes, attempts pushes/PRs, removes completed entries.

V2 Compliance: Agent pattern, background service
Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-11-28
Priority: CRITICAL - Bottleneck Breaking
"""

import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.deferred_push_queue import get_deferred_push_queue, PushStatus
from src.core.synthetic_github import get_synthetic_github
from src.core.local_repo_layer import get_local_repo_manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GitHubPusherAgent:
    """Agent that processes deferred GitHub push queue."""
    
    def __init__(self):
        """Initialize pusher agent."""
        self.queue = get_deferred_push_queue()
        self.github = get_synthetic_github()
        self.repo_manager = get_local_repo_manager()
        
        logger.info("✅ GitHub Pusher Agent initialized")
    
    def process_queue(self, max_items: int = 10) -> Dict[str, int]:
        """
        Process deferred push queue.
        
        Args:
            max_items: Maximum items to process per cycle
        
        Returns:
            Statistics dictionary
        """
        stats = {
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "deferred": 0
        }
        
        # Get pending count
        pending_count = self.queue.get_pending_count()
        
        if pending_count == 0:
            logger.debug("📭 Queue is empty")
            return stats
        
        logger.info(f"📥 Processing queue: {pending_count} pending items")
        
        # Process up to max_items
        for _ in range(min(max_items, pending_count)):
            entry = self.queue.dequeue_push()
            if not entry:
                break
            
            entry_id = entry.get("id")
            repo = entry.get("repo")
            branch = entry.get("branch")
            reason = entry.get("reason", "unknown")
            
            logger.info(f"🔄 Processing: {repo}/{branch} (ID: {entry_id}, reason: {reason})")
            
            # Mark as retrying
            self.queue.mark_retrying(entry_id)
            
            # Process based on action
            metadata = entry.get("metadata", {})
            action = metadata.get("action", "push")
            
            if action == "create_pr":
                success = self._process_pr(entry)
            else:
                success = self._process_push(entry)
            
            stats["processed"] += 1
            
            if success:
                stats["succeeded"] += 1
                self.queue.mark_completed(entry_id)
                logger.info(f"✅ Completed: {repo}/{branch}")
            else:
                # Check if we should retry
                retry_count = entry.get("retry_count", 0)
                if retry_count < 5:
                    stats["deferred"] += 1
                    logger.info(f"⏳ Deferred: {repo}/{branch} (retry {retry_count + 1}/5)")
                else:
                    stats["failed"] += 1
                    self.queue.mark_failed(entry_id, "Max retries exceeded", max_retries=5)
                    logger.warning(f"❌ Failed permanently: {repo}/{branch}")
        
        return stats
    
    def _process_push(self, entry: Dict[str, Any]) -> bool:
        """Process a push entry."""
        repo = entry.get("repo")
        branch = entry.get("branch")
        
        try:
            # Use synthetic GitHub to push
            success, error = self.github.push_branch(repo, branch)
            
            if success:
                return True
            else:
                # If still rate-limited, defer again
                if "rate_limit" in str(error).lower() or "429" in str(error):
                    logger.warning(f"⚠️ Still rate-limited: {repo}/{branch}")
                    return False
                else:
                    logger.error(f"❌ Push failed: {error}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error processing push: {e}")
            return False
    
    def _process_pr(self, entry: Dict[str, Any]) -> bool:
        """Process a PR creation entry."""
        repo = entry.get("repo")
        branch = entry.get("branch")
        metadata = entry.get("metadata", {})
        
        try:
            # Use synthetic GitHub to create PR
            success, pr_url_or_error = self.github.create_pr(
                repo_name=repo,
                branch=branch,
                base_branch=metadata.get("base_branch", "main"),
                title=metadata.get("pr_title"),
                body=metadata.get("pr_body")
            )
            
            if success:
                logger.info(f"✅ PR created: {pr_url_or_error}")
                return True
            else:
                # If still rate-limited, defer again
                if "rate_limit" in str(pr_url_or_error).lower() or "429" in str(pr_url_or_error):
                    logger.warning(f"⚠️ Still rate-limited for PR: {repo}/{branch}")
                    return False
                else:
                    logger.error(f"❌ PR creation failed: {pr_url_or_error}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error processing PR: {e}")
            return False
    
    def run_continuous(self, interval_seconds: int = 300, max_iterations: Optional[int] = None):
        """
        Run agent continuously.
        
        Args:
            interval_seconds: Seconds between queue checks (default: 5 minutes)
            max_iterations: Maximum iterations (None = infinite)
        """
        logger.info(f"🚀 Starting continuous mode (interval: {interval_seconds}s)")
        
        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            try:
                # Process queue
                stats = self.process_queue(max_items=10)
                
                # Log stats
                if stats["processed"] > 0:
                    logger.info(
                        f"📊 Cycle complete: "
                        f"processed={stats['processed']}, "
                        f"succeeded={stats['succeeded']}, "
                        f"failed={stats['failed']}, "
                        f"deferred={stats['deferred']}"
                    )
                
                # Clean up old completed entries
                self.queue.clear_completed(older_than_hours=24)
                
                # Wait before next cycle
                if max_iterations is None or iteration < max_iterations - 1:
                    logger.debug(f"⏳ Waiting {interval_seconds}s before next cycle...")
                    time.sleep(interval_seconds)
                
                iteration += 1
                
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down (keyboard interrupt)")
                break
            except Exception as e:
                logger.error(f"❌ Error in continuous loop: {e}")
                time.sleep(interval_seconds)  # Wait before retry


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Pusher Agent - Process deferred queue")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process queue once and exit"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval between cycles in seconds (default: 300 = 5 minutes)"
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=10,
        help="Maximum items to process per cycle (default: 10)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum iterations (default: infinite)"
    )
    
    args = parser.parse_args()
    
    agent = GitHubPusherAgent()
    
    if args.once:
        # Process once
        stats = agent.process_queue(max_items=args.max_items)
        print(json.dumps(stats, indent=2))
    else:
        # Run continuously
        agent.run_continuous(
            interval_seconds=args.interval,
            max_iterations=args.max_iterations
        )


if __name__ == "__main__":
    main()

"""
GitHub Pusher Agent - Processes Deferred Push Queue
====================================================

Background agent that processes deferred GitHub operations from the queue.
Runs every 5 minutes, attempts pushes/PRs, removes completed entries.

V2 Compliance: Agent pattern, background service
Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-11-28
Priority: CRITICAL - Bottleneck Breaking
"""

import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.deferred_push_queue import get_deferred_push_queue, PushStatus
from src.core.synthetic_github import get_synthetic_github
from src.core.local_repo_layer import get_local_repo_manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GitHubPusherAgent:
    """Agent that processes deferred GitHub push queue."""
    
    def __init__(self):
        """Initialize pusher agent."""
        self.queue = get_deferred_push_queue()
        self.github = get_synthetic_github()
        self.repo_manager = get_local_repo_manager()
        
        logger.info("✅ GitHub Pusher Agent initialized")
    
    def process_queue(self, max_items: int = 10) -> Dict[str, int]:
        """
        Process deferred push queue.
        
        Args:
            max_items: Maximum items to process per cycle
        
        Returns:
            Statistics dictionary
        """
        stats = {
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "deferred": 0
        }
        
        # Get pending count
        pending_count = self.queue.get_pending_count()
        
        if pending_count == 0:
            logger.debug("📭 Queue is empty")
            return stats
        
        logger.info(f"📥 Processing queue: {pending_count} pending items")
        
        # Process up to max_items
        for _ in range(min(max_items, pending_count)):
            entry = self.queue.dequeue_push()
            if not entry:
                break
            
            entry_id = entry.get("id")
            repo = entry.get("repo")
            branch = entry.get("branch")
            reason = entry.get("reason", "unknown")
            
            logger.info(f"🔄 Processing: {repo}/{branch} (ID: {entry_id}, reason: {reason})")
            
            # Mark as retrying
            self.queue.mark_retrying(entry_id)
            
            # Process based on action
            metadata = entry.get("metadata", {})
            action = metadata.get("action", "push")
            
            if action == "create_pr":
                success = self._process_pr(entry)
            else:
                success = self._process_push(entry)
            
            stats["processed"] += 1
            
            if success:
                stats["succeeded"] += 1
                self.queue.mark_completed(entry_id)
                logger.info(f"✅ Completed: {repo}/{branch}")
            else:
                # Check if we should retry
                retry_count = entry.get("retry_count", 0)
                if retry_count < 5:
                    stats["deferred"] += 1
                    logger.info(f"⏳ Deferred: {repo}/{branch} (retry {retry_count + 1}/5)")
                else:
                    stats["failed"] += 1
                    self.queue.mark_failed(entry_id, "Max retries exceeded", max_retries=5)
                    logger.warning(f"❌ Failed permanently: {repo}/{branch}")
        
        return stats
    
    def _process_push(self, entry: Dict[str, Any]) -> bool:
        """Process a push entry."""
        repo = entry.get("repo")
        branch = entry.get("branch")
        
        try:
            # Use synthetic GitHub to push
            success, error = self.github.push_branch(repo, branch)
            
            if success:
                return True
            else:
                # If still rate-limited, defer again
                if "rate_limit" in str(error).lower() or "429" in str(error):
                    logger.warning(f"⚠️ Still rate-limited: {repo}/{branch}")
                    return False
                else:
                    logger.error(f"❌ Push failed: {error}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error processing push: {e}")
            return False
    
    def _process_pr(self, entry: Dict[str, Any]) -> bool:
        """Process a PR creation entry."""
        repo = entry.get("repo")
        branch = entry.get("branch")
        metadata = entry.get("metadata", {})
        
        try:
            # Use synthetic GitHub to create PR
            success, pr_url_or_error = self.github.create_pr(
                repo_name=repo,
                branch=branch,
                base_branch=metadata.get("base_branch", "main"),
                title=metadata.get("pr_title"),
                body=metadata.get("pr_body")
            )
            
            if success:
                logger.info(f"✅ PR created: {pr_url_or_error}")
                return True
            else:
                # If still rate-limited, defer again
                if "rate_limit" in str(pr_url_or_error).lower() or "429" in str(pr_url_or_error):
                    logger.warning(f"⚠️ Still rate-limited for PR: {repo}/{branch}")
                    return False
                else:
                    logger.error(f"❌ PR creation failed: {pr_url_or_error}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error processing PR: {e}")
            return False
    
    def run_continuous(self, interval_seconds: int = 300, max_iterations: Optional[int] = None):
        """
        Run agent continuously.
        
        Args:
            interval_seconds: Seconds between queue checks (default: 5 minutes)
            max_iterations: Maximum iterations (None = infinite)
        """
        logger.info(f"🚀 Starting continuous mode (interval: {interval_seconds}s)")
        
        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            try:
                # Process queue
                stats = self.process_queue(max_items=10)
                
                # Log stats
                if stats["processed"] > 0:
                    logger.info(
                        f"📊 Cycle complete: "
                        f"processed={stats['processed']}, "
                        f"succeeded={stats['succeeded']}, "
                        f"failed={stats['failed']}, "
                        f"deferred={stats['deferred']}"
                    )
                
                # Clean up old completed entries
                self.queue.clear_completed(older_than_hours=24)
                
                # Wait before next cycle
                if max_iterations is None or iteration < max_iterations - 1:
                    logger.debug(f"⏳ Waiting {interval_seconds}s before next cycle...")
                    time.sleep(interval_seconds)
                
                iteration += 1
                
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down (keyboard interrupt)")
                break
            except Exception as e:
                logger.error(f"❌ Error in continuous loop: {e}")
                time.sleep(interval_seconds)  # Wait before retry


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Pusher Agent - Process deferred queue")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process queue once and exit"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval between cycles in seconds (default: 300 = 5 minutes)"
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=10,
        help="Maximum items to process per cycle (default: 10)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum iterations (default: infinite)"
    )
    
    args = parser.parse_args()
    
    agent = GitHubPusherAgent()
    
    if args.once:
        # Process once
        stats = agent.process_queue(max_items=args.max_items)
        print(json.dumps(stats, indent=2))
    else:
        # Run continuously
        agent.run_continuous(
            interval_seconds=args.interval,
            max_iterations=args.max_iterations
        )


if __name__ == "__main__":
    main()

