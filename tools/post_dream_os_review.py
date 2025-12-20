#!/usr/bin/env python3
"""
Post Dream.os Review Blog
==========================

Posts the Dream.os review blog to dadudekc.com (Code Reviews category).

Author: Agent-1 (Integration & Core Systems Specialist)
"""

from tools.unified_blogging_automation import UnifiedBloggingAutomation
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Post the Dream.os review blog to dadudekc.com."""

    # Read the blog post content (use styled version)
    blog_content_path = project_root / "docs" / "blog" / "dream_os_review_styled.md"

    # Fallback to unstyled version if styled doesn't exist
    if not blog_content_path.exists():
        blog_content_path = project_root / "docs" / "blog" / "dream_os_review.md"

    if not blog_content_path.exists():
        print(f"❌ Blog content file not found: {blog_content_path}")
        return 1

    with open(blog_content_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Initialize blogging automation
    automation = UnifiedBloggingAutomation()

    if not automation.clients:
        print("❌ No WordPress sites configured")
        print("   Configure sites in .deploy_credentials/blogging_api.json")
        return 1

    # Blog post metadata
    title = "A Professional Review of My Vibe-Coded Project: Dream.os"
    excerpt = "An honest review of Dream.os, examining the architecture, code quality, development process, and what makes this multi-agent system special."

    # Post to dadudekc.com (Code Reviews category)
    site_id = "dadudekc.com"

    if site_id not in automation.clients:
        print(f"❌ Site '{site_id}' not found in configuration")
        print(f"   Available sites: {', '.join(automation.clients.keys())}")
        return 1

    print("=" * 60)
    print("POSTING DREAM.OS REVIEW BLOG")
    print("=" * 60)
    print(f"Title: {title}")
    print(f"Site: {site_id}")
    print(f"Content length: {len(content)} characters")
    print()

    # Publish to dadudekc.com
    print(f"🚀 Publishing to {site_id}...")
    print()

    result = automation.publish_to_site(
        site_id=site_id,
        title=title,
        content=content,
        site_purpose="personal",  # Will use Code Reviews category from config
        excerpt=excerpt,
        status="publish"  # Publish immediately
    )

    if result.get("success"):
        post_id = result.get("post_id")
        post_url = result.get("post_url", "N/A")
        print(f"✅ Published successfully!")
        print(f"   Post ID: {post_id}")
        print(f"   URL: {post_url}")
        print()
        print("=" * 60)
        print("✅ Blog post published successfully!")
        print("=" * 60)
        return 0
    else:
        error = result.get("error", "Unknown error")
        print(f"❌ Failed to publish: {error}")
        print()
        print("=" * 60)
        print("❌ Publication failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
