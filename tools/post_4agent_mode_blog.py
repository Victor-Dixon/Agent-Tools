#!/usr/bin/env python3
"""
Post 4-Agent Mode Optimization Blog
====================================

Posts the 4-agent mode optimization blog to dadudekc.com.

Author: Agent-4 (Captain)
Date: 2025-12-13
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.unified_blogging_automation import UnifiedBloggingAutomation


def main():
    """Post the 4-agent mode optimization blog to dadudekc.com."""
    
    # Read the blog post content
    blog_content_path = project_root / "docs" / "blog" / "4_agent_mode_optimization_2025-12-13.md"
    
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
    
    # Blog post metadata
    title = "🚀 Optimizing Multi-Agent Systems: Introducing 4-Agent Mode"
    excerpt = "Reducing compute costs by 50% while maintaining full system capabilities through intelligent agent mode switching. Learn how we implemented a configurable agent mode system that allows seamless scaling between 4 and 8 agents."
    
    # Post to dadudekc.com
    site_id = "dadudekc.com"
    
    if site_id not in automation.clients:
        print(f"❌ Site '{site_id}' not found in configured sites")
        print(f"Available sites: {list(automation.clients.keys())}")
        return 1
    
    print("=" * 60)
    print("POSTING 4-AGENT MODE OPTIMIZATION BLOG")
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

