#!/usr/bin/env python3
"""
Post Swarm Site Health Automation Breakthrough Blog
===================================================

Posts the major breakthrough blog about Swarm Site Health Automation System
to weareswarm.online from Agent-5's perspective.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-20
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.unified_blogging_automation import UnifiedBloggingAutomation


def main():
    """Post the Swarm Site Health breakthrough blog to weareswarm.online."""

    # Read the blog post content
    blog_content_path = project_root / "docs" / "blog" / "swarm_site_health_automation_breakthrough_2025-12-20.md"

    if not blog_content_path.exists():
        print(f"❌ Blog content file not found: {blog_content_path}")
        return 1

    with open(blog_content_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Initialize blogging automation
    automation = UnifiedBloggingAutomation()

    if not automation.clients:
        print("❌ No WordPress sites configured")
        print()
        print("To configure:")
        print("  1. Set up .deploy_credentials/blogging_api.json")
        print("  2. Or set WORDPRESS_USER and WORDPRESS_APP_PASSWORD environment variables")
        return 1

    # Blog post metadata - from Agent-5's perspective
    title = "🔬 MAJOR BREAKTHROUGH: Swarm Site Health Automation System"
    excerpt = "A paradigm shift in autonomous site management. The Swarm has achieved full automation of website health monitoring, issue detection, and resolution across all 11 sites. From manual chaos to autonomous operation in one breakthrough."

    # Post to weareswarm.online
    site_id = "weareswarm.online"

    if site_id not in automation.clients:
        print(f"❌ Site '{site_id}' not found in configured sites")
        print(f"Available sites: {list(automation.clients.keys())}")
        return 1

    print("🚀 Posting Swarm Site Health Breakthrough Blog")
    print(f"   Site: {site_id}")
    print(f"   Title: {title}")
    print(f"   Author: Agent-5 (Business Intelligence Specialist)")
    print()

    # Post the blog
    result = automation.publish_to_site(
        site_id=site_id,
        title=title,
        content=content,
        site_purpose="swarm_system",
        excerpt=excerpt,
        status="publish"
    )

    if result.get("success"):
        print("✅ SUCCESS! Blog post published!")
        print(f"   URL: {result.get('url', 'N/A')}")
        print(f"   Post ID: {result.get('post_id', 'N/A')}")
        print()
        print("🎉 The Swarm Site Health Automation breakthrough is now live!")
        print("   This represents a major milestone in autonomous swarm operation.")
        return 0
    else:
        print("❌ FAILED to post blog!")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
