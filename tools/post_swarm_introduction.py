#!/usr/bin/env python3
"""
Post Swarm Introduction Blog
============================

Posts the Swarm introduction blog to dadudekc.com.

Author: Agent-1 (Integration & Core Systems Specialist)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.unified_blogging_automation import UnifiedBloggingAutomation


def main():
    """Post the Swarm introduction blog to dadudekc.com."""
    
    # Read the blog post content
    blog_content_path = project_root / "docs" / "blog" / "introducing_the_swarm.md"
    
    if not blog_content_path.exists():
        print(f"❌ Blog content file not found: {blog_content_path}")
        return 1
    
    with open(blog_content_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Initialize blogging automation
    automation = UnifiedBloggingAutomation()
    
    if not automation.clients:
        print("❌ No WordPress sites configured")
        return 1
    
    # Blog post metadata
    title = "Introducing The Swarm: A New Paradigm in Collaborative Development"
    excerpt = "Meet The Swarm: A revolutionary multi-agent system where specialized AI agents collaborate to build complex software. Learn how 8 specialized agents work together to transform software development."
    
    # Post to dadudekc.com
    site_id = "dadudekc.com"
    
    if site_id not in automation.clients:
        print(f"❌ Site '{site_id}' not found")
        return 1
    
    print("=" * 60)
    print("POSTING SWARM INTRODUCTION BLOG")
    print("=" * 60)
    print(f"Title: {title}")
    print(f"Site: {site_id}")
    print(f"Content length: {len(content)} characters")
    print()
    
    # Publish
    print(f"🚀 Publishing to {site_id}...")
    print()
    
    result = automation.publish_to_site(
        site_id=site_id,
        title=title,
        content=content,
        site_purpose="personal",
        excerpt=excerpt,
        status="publish"
    )
    
    if result.get("success"):
        post_id = result.get("post_id")
        post_url = result.get("link", "N/A")
        print(f"✅ Published successfully!")
        print(f"   Post ID: {post_id}")
        print(f"   URL: {post_url}")
        return 0
    else:
        error = result.get("error", "Unknown error")
        print(f"❌ Failed: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())





