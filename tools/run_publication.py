"""
Publication System CLI - Phase 3
=================================

Processes PUBLISH_QUEUE entries and coordinates all publishers.

Usage:
    python tools/run_publication.py --process-queue
    python tools/run_publication.py --add-entry --type readme --file path/to/readme.md --targets github,website
    python tools/run_publication.py --stats

Author: Agent-7 (Web Development Specialist)
V2 Compliant: <300 lines
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from systems.output_flywheel.publication import (
    PublishQueueManager,
    GitHubPublisher,
    WebsitePublisher,
    SocialDraftGenerator
)
import yaml


def load_config(config_path: Path = None) -> dict:
    """Load configuration from config.yaml."""
    if config_path is None:
        config_path = project_root / "systems" / "output_flywheel" / "config.yaml"
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"⚠️ Failed to load config: {e}")
        return {}


def process_queue_entry(entry, config: dict) -> dict:
    """Process a single queue entry."""
    result = {
        "entry_id": entry.id,
        "artifact_type": entry.artifact_type,
        "status": "failed",
        "results": {}
    }
    
    try:
        # Update status to processing
        queue_manager = PublishQueueManager()
        queue_manager.update_status(entry.id, "processing")
        
        # Process each target
        for target in entry.targets:
            if target == "github":
                github_config = config.get("publication", {}).get("github", {})
                publisher = GitHubPublisher(
                    branch=github_config.get("branch", "main"),
                    auto_commit=github_config.get("auto_commit", False),
                    auto_push=github_config.get("auto_push", False)
                )
                publish_result = publisher.publish_artifact(
                    artifact_type=entry.artifact_type,
                    artifact_path=entry.source_file,
                    commit_message=github_config.get("commit_message_template", "").format(
                        artifact_type=entry.artifact_type,
                        session_id=entry.metadata.get("session_id", "unknown")
                    )
                )
                result["results"]["github"] = publish_result
            
            elif target == "website":
                website_config = config.get("publication", {}).get("website", {})
                publisher = WebsitePublisher(
                    output_path=website_config.get("output_path", "website/content"),
                    markdown_to_html=website_config.get("markdown_to_html", True)
                )
                publish_result = publisher.publish_artifact(
                    artifact_type=entry.artifact_type,
                    artifact_path=entry.source_file,
                    metadata=entry.metadata
                )
                result["results"]["website"] = publish_result
            
            elif target == "social":
                social_config = config.get("publication", {}).get("social", {})
                generator = SocialDraftGenerator(
                    draft_mode=social_config.get("draft_mode", True)
                )
                platforms = social_config.get("platforms", ["twitter"])
                
                for platform in platforms:
                    draft_result = generator.generate_draft(
                        artifact_type=entry.artifact_type,
                        artifact_path=entry.source_file,
                        platform=platform,
                        metadata=entry.metadata
                    )
                    result["results"][f"social_{platform}"] = draft_result
        
        # Update status based on results
        all_success = all(
            r.get("success", False) for r in result["results"].values()
        )
        
        if all_success:
            queue_manager.update_status(entry.id, "published")
            result["status"] = "published"
        else:
            queue_manager.update_status(entry.id, "failed", {
                "error": "One or more targets failed"
            })
            result["status"] = "failed"
        
    except Exception as e:
        queue_manager = PublishQueueManager()
        queue_manager.update_status(entry.id, "failed", {"error": str(e)})
        result["status"] = "failed"
        result["error"] = str(e)
    
    return result


def process_queue(config: dict) -> None:
    """Process all pending queue entries."""
    queue_manager = PublishQueueManager()
    pending_entries = queue_manager.get_pending_entries()
    
    if not pending_entries:
        print("✅ No pending entries in queue")
        return
    
    print(f"📋 Processing {len(pending_entries)} pending entries...")
    
    for entry in pending_entries:
        print(f"\n🔄 Processing: {entry.artifact_type} ({entry.id[:8]}...)")
        result = process_queue_entry(entry, config)
        
        if result["status"] == "published":
            print(f"✅ Published successfully")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    # Show final stats
    stats = queue_manager.get_queue_stats()
    print(f"\n📊 Queue Stats:")
    print(f"   Total: {stats['total']}")
    print(f"   Pending: {stats['pending']}")
    print(f"   Published: {stats['published']}")
    print(f"   Failed: {stats['failed']}")


def add_entry(artifact_type: str, source_file: str, targets: list, metadata: dict = None) -> None:
    """Add entry to publication queue."""
    queue_manager = PublishQueueManager()
    entry_id = queue_manager.add_entry(
        artifact_type=artifact_type,
        source_file=source_file,
        targets=targets,
        metadata=metadata
    )
    print(f"✅ Entry added to queue: {entry_id}")


def show_stats() -> None:
    """Show queue statistics."""
    queue_manager = PublishQueueManager()
    stats = queue_manager.get_queue_stats()
    
    print("📊 Publication Queue Statistics:")
    print(f"   Total entries: {stats['total']}")
    print(f"   Pending: {stats['pending']}")
    print(f"   Processing: {stats['processing']}")
    print(f"   Published: {stats['published']}")
    print(f"   Failed: {stats['failed']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Publication System CLI - Process PUBLISH_QUEUE entries"
    )
    
    parser.add_argument(
        "--process-queue",
        action="store_true",
        help="Process all pending queue entries"
    )
    
    parser.add_argument(
        "--add-entry",
        action="store_true",
        help="Add entry to queue"
    )
    
    parser.add_argument(
        "--type",
        type=str,
        help="Artifact type (readme, blog_post, social_post, trade_journal)"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="Source file path"
    )
    
    parser.add_argument(
        "--targets",
        type=str,
        help="Comma-separated targets (github,website,social)"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show queue statistics"
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_config()
    
    # Execute command
    if args.process_queue:
        process_queue(config)
    elif args.add_entry:
        if not args.type or not args.file or not args.targets:
            print("❌ Error: --type, --file, and --targets required for --add-entry")
            sys.exit(1)
        
        targets = [t.strip() for t in args.targets.split(",")]
        add_entry(args.type, args.file, targets)
    elif args.stats:
        show_stats()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()




