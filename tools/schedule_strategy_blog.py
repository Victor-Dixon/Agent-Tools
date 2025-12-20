#!/usr/bin/env python3
"""
Schedule Strategy Blog Posts
============================

Automated scheduling for strategy blog posts. Can be run via cron or task scheduler.

Usage:
    python tools/schedule_strategy_blog.py --site tradingrobotplug.com --frequency daily
    python tools/schedule_strategy_blog.py --site tradingrobotplug.com --frequency weekly
"""

from strategy_blog_automation import generate_strategy_analysis, create_blog_post, generate_blog_post_content
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "tools"))


def should_generate_post(frequency: str, last_post_date: str = None) -> bool:
    """Check if we should generate a new post based on frequency."""
    if frequency == "daily":
        if not last_post_date:
            return True
        last_date = datetime.strptime(last_post_date, "%Y-%m-%d")
        return (datetime.now() - last_date).days >= 1

    elif frequency == "weekly":
        if not last_post_date:
            return True
        last_date = datetime.strptime(last_post_date, "%Y-%m-%d")
        return (datetime.now() - last_date).days >= 7

    elif frequency == "manual":
        return False

    return True


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Schedule Strategy Blog Posts")
    parser.add_argument("--site", default="freerideinvestor", help="Site name")
    parser.add_argument("--frequency", default="weekly", choices=["daily", "weekly", "manual"],
                        help="Post frequency")
    parser.add_argument("--force", action="store_true",
                        help="Force post generation")

    args = parser.parse_args()

    # Generate analysis
    analysis = generate_strategy_analysis()

    if args.force or should_generate_post(args.frequency):
        print(f"📝 Generating blog post for {args.site}...")
        print(f"   Strategy: {analysis['strategy_name']}")
        print(f"   Date: {analysis['analysis_date']}")

        success = create_blog_post(args.site, analysis)

        if success:
            print("✅ Blog post created successfully!")
            # Save last post date (you can implement file-based tracking)
        else:
            print("❌ Failed to create blog post")
            sys.exit(1)
    else:
        print("⏭️  Skipping post generation (frequency not met)")


if __name__ == "__main__":
    main()

