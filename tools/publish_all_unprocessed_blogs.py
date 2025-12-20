#!/usr/bin/env python3
"""
Publish All Unprocessed Blog Posts
===================================

Publishes all blog posts from docs/blog/ that haven't been published yet.
Checks for recent blog posts and publishes them to dadudekc.com.

Author: Agent-1
Date: 2025-12-14
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.unified_blogging_automation import UnifiedBloggingAutomation


# Blog posts to publish with metadata
BLOG_POSTS = [
    {
        "file": "the_swarm_core_philosophy_2025-12-13.md",
        "title": "🎯 The Core Philosophy: Building Software Through Collaborative Agent Teams",
        "excerpt": "A fundamental shift from single-developer workflows to specialized agent teams. Learn how The Swarm creates more robust, maintainable, and innovative software through activity detection, unified messaging, and test-driven development.",
        "site_purpose": "swarm_system"
    },
    {
        "file": "4_agent_mode_optimization_2025-12-13.md",
        "title": "🚀 Optimizing Multi-Agent Systems: Introducing 4-Agent Mode",
        "excerpt": "Reducing compute costs by 50% while maintaining full system capabilities through intelligent agent mode switching. Learn how we implemented a configurable agent mode system that allows seamless scaling between 4 and 8 agents.",
        "site_purpose": "swarm_system"
    },
    {
        "file": "dream_os_operating_cycle_interview_2025-12-14.md",
        "title": "🚀 Dream.OS Operating Cycle: An Inside Look at WeAreSwarm.ai",
        "excerpt": "A candid interview about how the multi-agent system actually works, from setup to execution, and what's new with the rebranding. Learn about coordinate mapping, message queuing, blocker handling, and 24/7 operation.",
        "site_purpose": "swarm_system"
    },
    {
        "file": "what_comes_next_2025-12-14.md",
        "title": "🔮 What Comes Next: The Roadmap for WeAreSwarm.ai",
        "excerpt": "A look ahead at the features, improvements, and innovations coming to the multi-agent collaborative ecosystem. From enhanced workflows to visual dashboards to true swarm intelligence.",
        "site_purpose": "swarm_system"
    }
]


def main():
    """Publish all unprocessed blog posts."""
    
    print("🚀 Publishing All Unprocessed Blog Posts\n")
    
    # Initialize blogging automation
    automation = UnifiedBloggingAutomation()
    
    if not automation.clients:
        print("❌ No WordPress sites configured")
        print()
        print("To configure:")
        print("  1. Set up .deploy_credentials/blogging_api.json")
        print("  2. Or set WORDPRESS_USER and WORDPRESS_APP_PASSWORD environment variables")
        return 1
    
    print(f"✅ Found {len(automation.clients)} configured WordPress site(s)\n")
    
    blog_dir = project_root / "docs" / "blog"
    results = {}
    
    # Publish each blog post
    for blog_info in BLOG_POSTS:
        blog_file = blog_dir / blog_info["file"]
        
        if not blog_file.exists():
            print(f"⚠️  Skipping {blog_info['file']} - file not found")
            continue
        
        print(f"📝 Publishing: {blog_info['title']}")
        print(f"   File: {blog_info['file']}")
        
        # Read blog content
        with open(blog_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Publish to dadudekc.com (swarm system site)
        result = automation.publish_to_site(
            site_id="dadudekc.com",
            title=blog_info["title"],
            content=content,
            site_purpose=blog_info.get("site_purpose", "swarm_system"),
            excerpt=blog_info.get("excerpt"),
            status="publish"  # Publish immediately
        )
        
        results[blog_info["file"]] = result
        
        if result.get("success"):
            print(f"   ✅ Published successfully!")
            if result.get("link"):
                print(f"   🔗 Link: {result['link']}")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 Publishing Summary")
    print("=" * 60)
    
    successful = sum(1 for r in results.values() if r.get("success"))
    failed = len(results) - successful
    
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📝 Total: {len(results)}")
    
    if failed > 0:
        print("\n❌ Failed Posts:")
        for file, result in results.items():
            if not result.get("success"):
                print(f"   - {file}: {result.get('error', 'Unknown error')}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

